import logging
from uuid import UUID
from sqlmodel import Session
from models import Question

logger = logging.getLogger(__name__)

_Q_TEXT_KEYS    = ("question_text", "question", "text", "q")
_OPTIONS_KEYS   = ("options", "choices", "answers")
_CORRECT_KEYS   = ("correct_option_index", "answer_index", "correct", "answer")
_EXPLAIN_KEYS   = ("explanation", "reason", "rationale", "justification")

def _extract_field(obj: dict, keys: tuple[str, ...]):
    for k in keys:
        if k in obj: return obj[k]
    return None

def _save_questions(session: Session, shared_quiz_id: UUID, raw_questions: list[dict]) -> int:
    saved = 0
    seen_texts: set[str] = set()

    for raw in raw_questions:
        if not isinstance(raw, dict): continue
        q_text   = _extract_field(raw, _Q_TEXT_KEYS)
        options  = _extract_field(raw, _OPTIONS_KEYS)
        c_idx    = _extract_field(raw, _CORRECT_KEYS)
        explain  = _extract_field(raw, _EXPLAIN_KEYS) or ""

        if not (q_text and options and isinstance(options, list) and c_idx is not None): continue
        if not (2 <= len(options) <= 6): continue

        canonical = str(q_text).strip().lower()
        if canonical in seen_texts: continue
        seen_texts.add(canonical)

        try:
            idx = int(c_idx)
            if not (0 <= idx < len(options)): idx = 0
            session.add(
                Question(
                    quiz_id=shared_quiz_id,
                    question_text=str(q_text).strip(),
                    options={"choices": [str(o).strip() for o in options]},
                    correct_option_index=idx,
                    explanation=str(explain).strip(),
                )
            )
            saved += 1
        except (ValueError, TypeError):
            continue

    return saved

async def generate_questions_with_groq(transcript_text: str, num_questions: int = 12) -> list[dict]:
    from .llm_caller import _build_prompt, _call_llm
    prompt = _build_prompt(transcript_text, num_questions)
    return await _call_llm(prompt)
