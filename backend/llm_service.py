"""
LLM Quiz Generation Service
============================
Generates multiple-choice question pools from YouTube video transcripts.

Supports two LLM providers, switchable via the LLM_PROVIDER env variable:

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PROVIDER 1: ollama  (default)  — Local, offline, no API key needed    │
  │    Set in .env:                                                         │
  │      LLM_PROVIDER=ollama                                                │
  │      OLLAMA_MODEL=qwen2.5:3b                                            │
  │      OLLAMA_URL=http://localhost:11434/api/generate                     │
  │                                                                         │
  │  Recommended hardware (optimised for RTX 3050 4 GB):                   │
  │    Model: qwen2.5:3b  (~2.0 GB VRAM, best quality)                     │
  │    Fallback: phi3:mini (~1.5 GB VRAM, fastest)                         │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  PROVIDER 2: groq   — Free cloud API, no GPU required                  │
  │    Sign up free at https://console.groq.com  (no credit card needed)   │
  │    Set in .env:                                                         │
  │      LLM_PROVIDER=groq                                                  │
  │      GROQ_API_KEY=your_groq_api_key_here                                │
  │      GROQ_MODEL=llama-3.1-8b-instant   (default, very fast)            │
  │                                                                         │
  │    Other free Groq models:                                              │
  │      llama-3.3-70b-versatile    — Best quality (higher latency)        │
  │      llama3-8b-8192             — Fast, good for structured JSON        │
  │      gemma2-9b-it               — Google Gemma 2, great accuracy        │
  │    Free tier limits: ~30 req/min, 6 000 req/day (plenty for this app)  │
  └─────────────────────────────────────────────────────────────────────────┘
"""

import asyncio
import itertools
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID

import httpx
from sqlmodel import Session, select
from youtube_transcript_api import YouTubeTranscriptApi

from models import Question, Quiz

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

# ── Provider selection ────────────────────────────────────────────────────────
# Set LLM_PROVIDER=ollama  for local inference (default)
# Set LLM_PROVIDER=groq    for free cloud API (no GPU required)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

# ── Ollama config (used when LLM_PROVIDER=ollama) ─────────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434/api/generate")

# RTX 3050 4 GB can comfortably hold qwen2.5:3b entirely on-GPU.
# num_gpu=-1 tells Ollama to auto-assign all layers to GPU.
# num_ctx=4096 keeps VRAM usage predictable; enough for ~8 000-char transcripts.
OLLAMA_OPTIONS: dict[str, Any] = {
    "temperature":   0.65,   # Slightly lower → more factual, fewer hallucinations
    "top_p":         0.90,
    "top_k":         40,
    "num_predict":   3072,   # Enough for ~20 well-formed questions in one pass
    "num_ctx":       4096,   # Context window (prompt + response)
    "num_gpu":       -1,     # -1 = use all available GPU layers automatically
    "num_thread":    6,      # i5-12500H has 12 threads; leave 6 for the OS
    "repeat_penalty": 1.15,  # Penalise repeated phrasing in question stems
}

# ── Groq config (used when LLM_PROVIDER=groq) ─────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── Transcript constants ───────────────────────────────────────────────────────
# With num_ctx=4096 and ~200 tokens/question overhead, max safe transcript is ~3 200 tokens.
# ~4 chars/token on average English text → 12 800 chars is a safe upper bound.
MAX_TRANSCRIPT_CHARS = 12_800

# ── Question pool constants ───────────────────────────────────────────────────
# These are the BASE defaults. The actual pool size is calculated dynamically
# in generate_quiz_pool_background based on questions_per_attempt so that the
# pool is always at least POOL_MULTIPLIER × questions_per_attempt.
# (More variety in the pool = more randomization across attempts.)
QUESTIONS_PER_BATCH  = 12   # Questions requested per LLM call
POOL_MULTIPLIER      = 4    # Pool target = questions_per_attempt × this factor
MAX_BATCHES          = 6    # Safety cap so we never spam the API


# ══════════════════════════════════════════════════════════════════════════════
# Startup validation
# ══════════════════════════════════════════════════════════════════════════════

def _validate_config() -> None:
    """Log a clear warning if the active provider is misconfigured."""
    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            logger.warning(
                "[Config] LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                "Sign up free at https://console.groq.com and add GROQ_API_KEY to your .env"
            )
        else:
            logger.info(f"[Config] LLM Provider: Groq  |  Model: {GROQ_MODEL}")
    elif LLM_PROVIDER == "ollama":
        logger.info(f"[Config] LLM Provider: Ollama (local)  |  Model: {OLLAMA_MODEL}  |  URL: {OLLAMA_URL}")
    else:
        logger.warning(
            f"[Config] Unknown LLM_PROVIDER='{LLM_PROVIDER}'. "
            "Valid values: 'ollama', 'groq'. Defaulting to 'ollama'."
        )

_validate_config()


# ══════════════════════════════════════════════════════════════════════════════
# Priority Queue — Global Quiz Generation Scheduler
# ══════════════════════════════════════════════════════════════════════════════
#
# Architecture:
#   • A single asyncio.PriorityQueue holds pending QuizJobs.
#   • quiz_generation_worker() is a long-lived asyncio Task started in the
#     FastAPI lifespan. It processes jobs one at a time, lowest priority first.
#   • After each job finishes it calls _chain_to_next() which automatically
#     enqueues the next pending quiz in the same playlist at CHAIN priority.
#   • Callers use enqueue_quiz() — a safe, dedup-guarded public API.
#
# Priority tiers (lower number = processed first):
#   PRIORITY_URGENT   = 0   → user is sitting at a pending quiz right now
#   PRIORITY_FIRST    = 10  → first quiz of a newly ingested playlist,
#                             or next quiz after user passes current one
#   PRIORITY_CHAIN    = 20  → automatic cascade: N finishes → N+1 queued
#   PRIORITY_RECOVERY = 30  → quizzes re-enqueued after server restart
# ══════════════════════════════════════════════════════════════════════════════

PRIORITY_URGENT   = 0
PRIORITY_FIRST    = 10
PRIORITY_CHAIN    = 20
PRIORITY_RECOVERY = 30

# Monotonic counter for stable FIFO ordering within the same priority tier.
_job_counter = itertools.count()


@dataclass(order=True)
class QuizJob:
    """
    A single unit of work in the priority queue.
    Ordering: (priority, seq) — lowest priority wins, seq breaks ties FIFO.
    """
    priority: int
    seq:      int                    # monotonic tiebreaker, auto-assigned
    quiz_id:             UUID        = field(compare=False)
    video_yt_ids:        list[str]   = field(compare=False)
    questions_per_attempt: int       = field(compare=False)
    engine:              Any         = field(compare=False)


# Module-level singletons — one queue and one dedup-set for the whole process.
_quiz_queue:          asyncio.PriorityQueue = asyncio.PriorityQueue()
_queued_or_running:   set[UUID]             = set()   # prevents double-enqueue


def enqueue_quiz(
    quiz_id: UUID,
    video_yt_ids: list[str],
    questions_per_attempt: int,
    engine: Any,
    priority: int = PRIORITY_CHAIN,
) -> bool:
    """
    Add a quiz to the global generation queue.

    Thread/coroutine safe (asyncio.PriorityQueue is not thread-safe, but
    all callers are async endpoints running in the same event loop).

    Returns True if the job was enqueued, False if it was already queued/running.
    If the quiz is already in the queue but at a lower priority, the new
    higher-priority entry is added — the duplicate is harmlessly skipped later.
    """
    # Always allow URGENT to jump the queue even if already queued at lower priority
    if quiz_id in _queued_or_running and priority != PRIORITY_URGENT:
        logger.debug(f"[Queue] Quiz {quiz_id} already queued — skip (priority={priority})")
        return False

    job = QuizJob(
        priority=priority,
        seq=next(_job_counter),
        quiz_id=quiz_id,
        video_yt_ids=video_yt_ids,
        questions_per_attempt=questions_per_attempt,
        engine=engine,
    )
    _queued_or_running.add(quiz_id)
    _quiz_queue.put_nowait(job)
    logger.info(
        f"[Queue] Enqueued quiz {quiz_id} | priority={priority} "
        f"| qpa={questions_per_attempt} | qsize={_quiz_queue.qsize()}"
    )
    return True


async def _chain_to_next(finished_quiz_id: UUID, engine: Any) -> None:
    """
    After a quiz finishes (success or failure), automatically enqueue the
    next pending quiz in the same playlist (by sequence_order) at CHAIN priority.
    This creates a self-sustaining generation cascade without any external trigger.
    """
    from sqlmodel import Session as _Session
    with _Session(engine) as session:
        current = session.get(Quiz, finished_quiz_id)
        if not current:
            return

        next_quiz = session.exec(
            select(Quiz).where(
                Quiz.playlist_id     == current.playlist_id,
                Quiz.status          == "pending",
                Quiz.sequence_order  >  current.sequence_order,
            ).order_by(Quiz.sequence_order)
        ).first()

        if next_quiz and next_quiz.video_yt_ids:
            enqueue_quiz(
                next_quiz.id,
                list(next_quiz.video_yt_ids),
                next_quiz.questions_per_attempt,
                engine,
                priority=PRIORITY_CHAIN,
            )
        elif next_quiz:
            logger.warning(
                f"[Queue] Next quiz {next_quiz.id} has no video_yt_ids stored — "
                "cannot chain. Check playlist ingestion."
            )


async def quiz_generation_worker() -> None:
    """
    Long-running background worker.
    Started once in the FastAPI lifespan; runs until the server shuts down.

    Loop:
      1. Block until a job is available (lowest priority first).
      2. Skip duplicates (URGENT can add duplicates intentionally).
      3. Generate the quiz pool via the active LLM provider.
      4. Chain to the next pending quiz in the same playlist.
      5. Repeat.
    """
    logger.info("[Worker] Quiz generation worker started.")
    while True:
        job: QuizJob = await _quiz_queue.get()
        try:
            # Skip if this job was already processed (duplicate from URGENT boost)
            with Session(job.engine) as session:
                quiz = session.get(Quiz, job.quiz_id)
                if not quiz:
                    logger.warning(f"[Worker] Quiz {job.quiz_id} not found — skipping.")
                    continue
                if quiz.status not in ("pending", "generating"):
                    logger.info(
                        f"[Worker] Quiz {job.quiz_id} already has status='{quiz.status}' — skipping."
                    )
                    continue

            logger.info(
                f"[Worker] ▶ Starting quiz {job.quiz_id} "
                f"(priority={job.priority}, qsize_remaining={_quiz_queue.qsize()})"
            )
            await generate_quiz_pool_background(
                job.quiz_id,
                job.video_yt_ids,
                job.engine,
                job.questions_per_attempt,
            )
        except Exception as exc:
            logger.error(f"[Worker] Unhandled error for quiz {job.quiz_id}: {exc}", exc_info=True)
        finally:
            _queued_or_running.discard(job.quiz_id)
            _quiz_queue.task_done()
            # Always attempt to chain, even after failure
            await _chain_to_next(job.quiz_id, job.engine)


async def recover_pending_quizzes(engine: Any) -> None:
    """
    Called once at server startup (before the worker loop begins).

    Handles two recovery scenarios:
      1. Quizzes stuck in 'generating' (server crashed mid-generation) →
         reset to 'pending' so they are re-processed.
      2. All 'pending' quizzes → re-enqueue in playlist-creation-time + sequence
         order at RECOVERY priority, so the most "first" quizzes run first.

    Only the first pending quiz per playlist is enqueued directly —
    the rest will be chained automatically when their predecessor finishes.
    This avoids flooding the queue with dozens of jobs on startup.
    """
    from sqlmodel import Session as _Session
    with _Session(engine) as session:
        # 1. Reset stuck quizzes
        stuck = session.exec(
            select(Quiz).where(Quiz.status == "generating")
        ).all()
        if stuck:
            logger.info(f"[Recovery] Resetting {len(stuck)} stuck 'generating' quizzes → 'pending'")
            for q in stuck:
                q.status = "pending"
            session.commit()

        # 2. Find the first pending quiz for every playlist that has pending work
        #    (order by playlist creation time + sequence_order)
        pending_all = session.exec(
            select(Quiz)
            .where(Quiz.status == "pending", Quiz.video_yt_ids != None)  # noqa: E711
            .order_by(Quiz.created_at, Quiz.sequence_order)
        ).all()

        # Enqueue only the earliest pending quiz per playlist (the rest will chain)
        seen_playlists: set = set()
        enqueued = 0
        for quiz in pending_all:
            if quiz.playlist_id not in seen_playlists:
                seen_playlists.add(quiz.playlist_id)
                enqueue_quiz(
                    quiz.id,
                    list(quiz.video_yt_ids),
                    quiz.questions_per_attempt,
                    engine,
                    priority=PRIORITY_RECOVERY,
                )
                enqueued += 1

        if enqueued:
            logger.info(f"[Recovery] Re-enqueued {enqueued} quiz(zes) from {len(seen_playlists)} playlist(s).")
        else:
            logger.info("[Recovery] No pending quizzes found — clean startup.")


# ══════════════════════════════════════════════════════════════════════════════
# Transcript Fetching
# ══════════════════════════════════════════════════════════════════════════════

def get_transcripts(video_ids: list[str]) -> str:
    """
    Fetch and concatenate transcripts for a list of YouTube video IDs.
    Falls back gracefully when a transcript is unavailable (private/no captions).
    """
    parts: list[str] = []
    for vid in video_ids:
        try:
            entries = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join(e["text"] for e in entries)
            parts.append(f"=== Video: {vid} ===\n{text.strip()}\n")
            logger.info(f"[Transcript] Fetched {len(text)} chars for {vid}")
        except Exception as exc:
            logger.warning(f"[Transcript] Unavailable for {vid}: {exc}")
            parts.append(f"=== Video: {vid} ===\n[No transcript available]\n")
    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# JSON Extraction  (robust against common LLM output quirks)
# ══════════════════════════════════════════════════════════════════════════════

def _extract_json_array(raw: str) -> list[dict]:
    """
    Extract a JSON array from an LLM response, handling:
      1. Clean JSON array
      2. JSON wrapped in a dict key  ({"questions": [...]})
      3. Markdown code fences         (```json ... ```)
      4. Extra prose before/after     (regex-find the first [...])
      5. Trailing commas              (common LLM mistake)
    Returns an empty list if all strategies fail.
    """
    if not raw:
        return []

    strategies = [
        # Strategy 1 – direct parse
        lambda s: s,
        # Strategy 2 – strip markdown fences
        lambda s: re.sub(r"```(?:json)?\s*|```", "", s, flags=re.IGNORECASE).strip(),
        # Strategy 3 – fix trailing commas then try again
        lambda s: re.sub(r",\s*([}\]])", r"\1",
                         re.sub(r"```(?:json)?\s*|```", "", s, flags=re.IGNORECASE).strip()),
    ]

    for transform in strategies:
        candidate = transform(raw)

        # Try parsing as-is
        for attempt in [candidate, re.search(r"\[.*\]", candidate, re.DOTALL)]:
            text = attempt.group(0) if hasattr(attempt, "group") else attempt
            try:
                obj = json.loads(text)
                if isinstance(obj, list):
                    return obj
                if isinstance(obj, dict):
                    for val in obj.values():
                        if isinstance(val, list) and val:
                            return val
            except (json.JSONDecodeError, TypeError):
                continue

    logger.error(f"[JSON] All extraction strategies failed. Raw snippet: {raw[:300]!r}")
    return []


# ══════════════════════════════════════════════════════════════════════════════
# Prompt Template
# ══════════════════════════════════════════════════════════════════════════════

_PROMPT_TEMPLATE = """\
You are an expert educator creating a multiple-choice quiz for a learner who just watched educational videos.

## Your Task
Generate exactly {n} high-quality multiple-choice questions based ONLY on the video transcripts below.

## Output Format
Output ONLY a valid JSON array — no markdown, no explanation, no surrounding text.
Each element must have exactly these keys:
{{
  "question_text": "Clear, specific question?",
  "options": ["Choice A", "Choice B", "Choice C", "Choice D"],
  "correct_option_index": 0,
  "explanation": "One sentence why this is correct."
}}

## Question Quality Rules
- correct_option_index is 0-based (0 = first option, 3 = fourth option).
- All 4 options must be plausible — avoid obviously wrong choices.
- Questions must be directly answerable from the transcripts.
- Vary cognitive level across the batch:
    {easy_n} RECALL questions   (definitions, facts, terminology)
    {medium_n} CONCEPT questions (how/why, cause-effect, comparisons)
    {hard_n} APPLY questions    (apply knowledge to a new scenario)
- Do NOT repeat a question from a previous batch.
- Keep each question stem under 30 words.
- Keep each option under 20 words.

## Transcripts
{transcript}

## JSON Array (output only):
"""


def _build_prompt(transcript: str, n: int) -> str:
    easy   = max(1, n // 4)
    hard   = max(1, n // 4)
    medium = n - easy - hard
    return _PROMPT_TEMPLATE.format(
        n=n,
        easy_n=easy,
        medium_n=medium,
        hard_n=hard,
        transcript=transcript[:MAX_TRANSCRIPT_CHARS],
    )


# ══════════════════════════════════════════════════════════════════════════════
# Ollama Caller  (LLM_PROVIDER=ollama)
# ══════════════════════════════════════════════════════════════════════════════

async def _call_ollama(prompt: str) -> list[dict]:
    """
    Call the local Ollama API and return a list of question dicts.
    Returns [] on any error (timeout, connection refused, bad JSON).
    """
    payload = {
        "model":   OLLAMA_MODEL,
        "prompt":  prompt,
        "stream":  False,
        "format":  "json",          # Ollama grammar-samples valid JSON only
        "options": OLLAMA_OPTIONS,
    }
    try:
        async with httpx.AsyncClient(timeout=360.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            raw = resp.json().get("response", "")
            questions = _extract_json_array(raw)
            logger.info(f"[Ollama] Model={OLLAMA_MODEL} → extracted {len(questions)} Qs")
            return questions

    except httpx.TimeoutException:
        logger.error(
            f"[Ollama] Request timed out after 360 s. "
            f"If using {OLLAMA_MODEL}, try a lighter model (phi3:mini). "
            "Or switch to LLM_PROVIDER=groq for a faster cloud alternative."
        )
    except httpx.ConnectError:
        logger.error(
            f"[Ollama] Cannot connect to {OLLAMA_URL}. "
            "Ensure Ollama is running:  ollama serve  "
            "Or switch to LLM_PROVIDER=groq to skip the local setup entirely."
        )
    except Exception as exc:
        logger.error(f"[Ollama] Unexpected error: {exc}")

    return []


# ══════════════════════════════════════════════════════════════════════════════
# Groq Caller  (LLM_PROVIDER=groq)
# ══════════════════════════════════════════════════════════════════════════════

async def _call_groq(prompt: str) -> list[dict]:
    """
    Call the Groq cloud API (OpenAI-compatible) and return a list of question dicts.
    Groq provides a free tier — sign up at https://console.groq.com
    Returns [] on any error (auth failure, rate limit, bad JSON).
    """
    if not GROQ_API_KEY:
        logger.error(
            "[Groq] GROQ_API_KEY is not set. "
            "Get a free key at https://console.groq.com and add it to your .env"
        )
        return []

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert educator. You always respond with valid JSON only. "
                    "Never include markdown fences or any explanation outside the JSON array."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature":     0.65,
        "max_tokens":      3072,
        "top_p":           0.90,
        "response_format": {"type": "json_object"},   # Forces JSON output on supported models
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(GROQ_API_URL, headers=headers, json=payload)

            if resp.status_code == 401:
                logger.error("[Groq] Authentication failed — check your GROQ_API_KEY.")
                return []
            if resp.status_code == 429:
                logger.warning("[Groq] Rate limit hit. Waiting 10 s before retry...")
                await asyncio.sleep(10)
                # One automatic retry
                resp = await client.post(GROQ_API_URL, headers=headers, json=payload)

            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            questions = _extract_json_array(raw)
            logger.info(f"[Groq] Model={GROQ_MODEL} → extracted {len(questions)} Qs")
            return questions

    except httpx.TimeoutException:
        logger.error("[Groq] Request timed out after 120 s.")
    except httpx.ConnectError:
        logger.error("[Groq] Cannot connect to Groq API. Check your internet connection.")
    except (KeyError, IndexError) as exc:
        logger.error(f"[Groq] Unexpected response structure: {exc}")
    except Exception as exc:
        logger.error(f"[Groq] Unexpected error: {exc}")

    return []


# ══════════════════════════════════════════════════════════════════════════════
# Unified LLM Dispatcher
# ══════════════════════════════════════════════════════════════════════════════

async def _call_llm(prompt: str) -> list[dict]:
    """
    Route the prompt to the correct LLM backend based on LLM_PROVIDER.
    Supported values: 'ollama' (default), 'groq'.
    """
    if LLM_PROVIDER == "groq":
        return await _call_groq(prompt)
    else:
        # Fallback to Ollama for 'ollama' or any unknown value
        return await _call_ollama(prompt)


# ══════════════════════════════════════════════════════════════════════════════
# Question Validation & DB Save
# ══════════════════════════════════════════════════════════════════════════════

# Accept multiple field names that different models may use
_Q_TEXT_KEYS    = ("question_text", "question", "text", "q")
_OPTIONS_KEYS   = ("options", "choices", "answers")
_CORRECT_KEYS   = ("correct_option_index", "answer_index", "correct", "answer")
_EXPLAIN_KEYS   = ("explanation", "reason", "rationale", "justification")


def _extract_field(obj: dict, keys: tuple[str, ...]):
    for k in keys:
        if k in obj:
            return obj[k]
    return None


def _save_questions(session: Session, quiz_id: UUID, raw_questions: list[dict]) -> int:
    """
    Validate each question dict and save valid ones to the DB.
    Returns the count of successfully saved questions.
    """
    saved = 0
    seen_texts: set[str] = set()

    for raw in raw_questions:
        if not isinstance(raw, dict):
            continue

        q_text   = _extract_field(raw, _Q_TEXT_KEYS)
        options  = _extract_field(raw, _OPTIONS_KEYS)
        c_idx    = _extract_field(raw, _CORRECT_KEYS)
        explain  = _extract_field(raw, _EXPLAIN_KEYS) or ""

        # Basic type validation
        if not (q_text and options and isinstance(options, list) and c_idx is not None):
            logger.debug(f"[Validate] Skipped — missing fields: {list(raw.keys())}")
            continue

        if not (2 <= len(options) <= 6):
            logger.debug(f"[Validate] Skipped — bad option count ({len(options)}): {str(q_text)[:40]}")
            continue

        # Deduplicate (same question text from different batches)
        canonical = str(q_text).strip().lower()
        if canonical in seen_texts:
            logger.debug(f"[Validate] Skipped duplicate: {str(q_text)[:40]}")
            continue
        seen_texts.add(canonical)

        try:
            idx = int(c_idx)
            if not (0 <= idx < len(options)):
                logger.warning(f"[Validate] Clamping out-of-bounds index {idx} → 0")
                idx = 0

            session.add(
                Question(
                    quiz_id=quiz_id,
                    question_text=str(q_text).strip(),
                    options={"choices": [str(o).strip() for o in options]},
                    correct_option_index=idx,
                    explanation=str(explain).strip(),
                )
            )
            saved += 1
        except (ValueError, TypeError) as exc:
            logger.warning(f"[Validate] Failed to parse correct_option_index: {c_idx} — {exc}")

    return saved


# ══════════════════════════════════════════════════════════════════════════════
# Public Background Task Entry Point
# ══════════════════════════════════════════════════════════════════════════════

async def generate_quiz_pool_background(
    quiz_id: UUID,
    video_yt_ids: list[str],
    engine,
    questions_per_attempt: int = 15,
) -> None:
    """
    Background task: generate a pool of questions for one quiz.

    The pool size scales with the quiz depth so there's always plenty of
    variety for randomisation across multiple attempts:

      pool_target = questions_per_attempt × POOL_MULTIPLIER

      Example:
        Light  quiz (8 Qs / attempt)  → target pool of  32 Qs  (3 batches)
        Standard quiz (15 Qs/attempt) → target pool of  60 Qs  (5 batches)
        Deep   quiz (25 Qs/attempt)   → target pool of 100 Qs  (MAX_BATCHES batches)

    Flow:
      1. Fetch transcripts for the given video IDs
      2. Generate batches of questions via the active LLM provider
         (Ollama local OR Groq cloud, controlled by LLM_PROVIDER env var)
      3. Validate and deduplicate all questions
      4. Persist to DB; set quiz.status = "ready" or "error_*"
    """
    # ── Calculate dynamic pool target ─────────────────────────────────────────
    pool_target     = questions_per_attempt * POOL_MULTIPLIER
    min_pool_ready  = max(questions_per_attempt, pool_target // 2)  # at minimum need enough for 1 attempt
    num_batches     = min(MAX_BATCHES, -(-pool_target // QUESTIONS_PER_BATCH))  # ceiling division

    logger.info(
        f"[Quiz {quiz_id}] Starting — provider={LLM_PROVIDER}, "
        f"questions_per_attempt={questions_per_attempt}, "
        f"pool_target={pool_target} ({num_batches} batches × {QUESTIONS_PER_BATCH} Qs), "
        f"videos={video_yt_ids}"
    )

    # Step 1 – Transcripts
    transcript = get_transcripts(video_yt_ids)
    real_content = [
        line for line in transcript.splitlines()
        if line.strip() and "[No transcript available]" not in line
    ]
    if not real_content:
        logger.warning(f"[Quiz {quiz_id}] No usable transcripts — marking error_no_transcript")
        _set_quiz_status(engine, quiz_id, "error_no_transcript")
        return

    # Step 2 – Generate in sequential batches
    prompt = _build_prompt(transcript, QUESTIONS_PER_BATCH)
    all_raw: list[dict] = []

    for batch_idx in range(num_batches):
        logger.info(f"[Quiz {quiz_id}] Batch {batch_idx + 1}/{num_batches}")
        batch = await _call_llm(prompt)
        if batch:
            all_raw.extend(batch)
            logger.info(
                f"[Quiz {quiz_id}] Batch {batch_idx + 1}: +{len(batch)} Qs "
                f"(total raw: {len(all_raw)} / target: {pool_target})"
            )
        else:
            logger.warning(f"[Quiz {quiz_id}] Batch {batch_idx + 1} returned 0 questions")

        # Small pause between batches:
        # - Ollama: lets GPU memory settle
        # - Groq: avoids hitting the free-tier rate limit (30 req/min)
        if batch_idx < num_batches - 1:
            await asyncio.sleep(2.0 if LLM_PROVIDER == "groq" else 0.5)

    if not all_raw:
        logger.error(f"[Quiz {quiz_id}] LLM produced no questions across all batches")
        _set_quiz_status(engine, quiz_id, "error_llm_failure")
        return

    # Step 3 – Validate, deduplicate, save
    from sqlmodel import Session as _Session  # local import avoids circular

    with _Session(engine) as session:
        saved = _save_questions(session, quiz_id, all_raw)

        quiz = session.get(Quiz, quiz_id)
        if quiz:
            if saved >= min_pool_ready:
                quiz.status = "ready"
                logger.info(
                    f"[Quiz {quiz_id}] ✅ Ready — {saved} questions saved "
                    f"(target ≥{min_pool_ready}, attempt size={questions_per_attempt})"
                )
            elif saved >= questions_per_attempt:
                # Fewer than ideal but enough for at least one attempt
                quiz.status = "ready"
                logger.warning(
                    f"[Quiz {quiz_id}] ⚠ Only {saved} valid questions "
                    f"(enough for {saved // questions_per_attempt} attempt(s), "
                    f"target pool was {pool_target}). "
                    "Quiz marked ready but pool is thin."
                )
            else:
                quiz.status = "error_llm_validation"
                logger.error(
                    f"[Quiz {quiz_id}] ❌ Only {saved} valid questions saved — "
                    f"not enough for even one attempt of {questions_per_attempt} Qs. "
                    f"Raw output sample: {str(all_raw)[:400]}"
                )
        session.commit()


def _set_quiz_status(engine, quiz_id: UUID, status: str) -> None:
    """Helper: update quiz status in a new session."""
    from sqlmodel import Session as _Session

    with _Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if quiz:
            quiz.status = status
            session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# Public helper kept for backwards compatibility with existing test imports
# ══════════════════════════════════════════════════════════════════════════════

async def generate_questions_with_ollama(transcript_text: str, num_questions: int = 12) -> list[dict]:
    """
    Thin public wrapper used by tests to generate questions directly.
    Now routes through the unified _call_llm dispatcher, so it respects
    the LLM_PROVIDER env variable automatically.
    """
    prompt = _build_prompt(transcript_text, num_questions)
    return await _call_llm(prompt)
