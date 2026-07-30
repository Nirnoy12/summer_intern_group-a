import asyncio
import logging
from uuid import UUID

from sqlmodel import Session, select
from models import Quiz, SharedQuiz
from .config import POOL_MULTIPLIER, MAX_BATCHES, QUESTIONS_PER_BATCH
from .transcript import get_transcripts
from .llm_caller import _build_prompt, _call_llm
from .questions import _save_questions

logger = logging.getLogger(__name__)

def _set_quiz_status(engine, shared_quiz_id: UUID, status: str) -> None:
    with Session(engine) as session:
        shared_quiz = session.get(SharedQuiz, shared_quiz_id)
        if shared_quiz:
            shared_quiz.status = status
            user_quizzes = session.exec(select(Quiz).where(Quiz.shared_quiz_id == shared_quiz_id)).all()
            for uq in user_quizzes:
                uq.status = status
            session.commit()

async def generate_quiz_pool_background(
    shared_quiz_id: UUID,
    video_yt_ids: list[str],
    engine,
    questions_per_attempt: int = 10,
) -> None:
    pool_target = questions_per_attempt * POOL_MULTIPLIER
    min_pool_ready = max(questions_per_attempt, pool_target // 2)
    num_batches = min(MAX_BATCHES, -(-pool_target // QUESTIONS_PER_BATCH))

    transcript = get_transcripts(video_yt_ids)
    real_content = [line for line in transcript.splitlines() if line.strip() and "[No transcript available]" not in line]
    if not real_content:
        _set_quiz_status(engine, shared_quiz_id, "error_no_transcript")
        return

    prompt = _build_prompt(transcript, QUESTIONS_PER_BATCH)
    all_raw: list[dict] = []

    for batch_idx in range(num_batches):
        batch = await _call_llm(prompt)
        if batch: all_raw.extend(batch)
        if batch_idx < num_batches - 1:
            await asyncio.sleep(2.0)

    if not all_raw:
        _set_quiz_status(engine, shared_quiz_id, "error_llm_failure")
        return

    with Session(engine) as session:
        saved = _save_questions(session, shared_quiz_id, all_raw)
        shared_quiz = session.get(SharedQuiz, shared_quiz_id)
        if shared_quiz:
            if saved >= min_pool_ready or saved >= questions_per_attempt:
                new_status = "ready"
            else:
                new_status = "error_llm_validation"
            shared_quiz.status = new_status
            user_quizzes = session.exec(select(Quiz).where(Quiz.shared_quiz_id == shared_quiz_id)).all()
            for uq in user_quizzes: uq.status = new_status
        session.commit()
