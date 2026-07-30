import logging
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from models import Quiz, SharedQuiz
from .queue import PRIORITY_CHAIN, PRIORITY_RECOVERY, _quiz_queue, _queued_or_running, QuizJob, enqueue_quiz
from .generator import generate_quiz_pool_background

logger = logging.getLogger(__name__)

async def _chain_to_next(finished_shared_quiz_id: UUID, engine: Any) -> None:
    with Session(engine) as session:
        current = session.get(SharedQuiz, finished_shared_quiz_id)
        if not current:
            return
        next_shared_quiz = session.exec(
            select(SharedQuiz).where(
                SharedQuiz.yt_playlist_id  == current.yt_playlist_id,
                SharedQuiz.status          == "pending",
                SharedQuiz.sequence_order  >  current.sequence_order,
            ).order_by(SharedQuiz.sequence_order)
        ).first()
        if next_shared_quiz and next_shared_quiz.video_yt_ids:
            enqueue_quiz(next_shared_quiz.id, list(next_shared_quiz.video_yt_ids), next_shared_quiz.questions_per_attempt, engine, priority=PRIORITY_CHAIN)

async def quiz_generation_worker() -> None:
    logger.info("[Worker] Quiz generation worker started.")
    while True:
        job: QuizJob = await _quiz_queue.get()
        try:
            with Session(job.engine) as session:
                shared_quiz = session.get(SharedQuiz, job.shared_quiz_id)
                if not shared_quiz or shared_quiz.status not in ("pending", "generating"):
                    continue
            await generate_quiz_pool_background(job.shared_quiz_id, job.video_yt_ids, job.engine, job.questions_per_attempt)
        except Exception as exc:
            logger.error(f"[Worker] Error for SharedQuiz {job.shared_quiz_id}: {exc}", exc_info=True)
        finally:
            _queued_or_running.discard(job.shared_quiz_id)
            _quiz_queue.task_done()
            await _chain_to_next(job.shared_quiz_id, job.engine)

async def recover_pending_quizzes(engine: Any) -> None:
    with Session(engine) as session:
        stuck = session.exec(select(Quiz).where(Quiz.status == "generating")).all()
        for q in stuck:
            q.status = "pending"
        session.commit()
        pending_all = session.exec(
            select(Quiz).where(Quiz.status == "pending", Quiz.video_yt_ids != None).order_by(Quiz.created_at, Quiz.sequence_order) # noqa: E711
        ).all()
        seen_playlists = set()
        for quiz in pending_all:
            if quiz.playlist_id not in seen_playlists:
                seen_playlists.add(quiz.playlist_id)
                enqueue_quiz(quiz.id, list(quiz.video_yt_ids), quiz.questions_per_attempt, engine, priority=PRIORITY_RECOVERY)
