"""
LLM Prompt and Extraction Helpers
"""
import json
import re
from .config import MAX_TRANSCRIPT_CHARS

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
    easy = max(1, n // 4)
    hard = max(1, n // 4)
    medium = n - easy - hard
    return _PROMPT_TEMPLATE.format(
        n=n,
        easy_n=easy,
        medium_n=medium,
        hard_n=hard,
        transcript=transcript[:MAX_TRANSCRIPT_CHARS],
    )


def _extract_json_array(raw: str) -> list[dict]:
    if not raw:
        return []
    strategies = [
        lambda s: s,
        lambda s: re.sub(r"```(?:json)?\s*|```", "", s, flags=re.IGNORECASE).strip(),
        lambda s: re.sub(r",\s*([}\]])", r"\1", re.sub(r"```(?:json)?\s*|```", "", s, flags=re.IGNORECASE).strip()),
    ]
    for transform in strategies:
        candidate = transform(raw)
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
    return []
