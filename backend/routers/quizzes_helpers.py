from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from core.deps import engine
from llm_service import enqueue_quiz, PRIORITY_URGENT
from models import Question, Quiz, SharedQuiz, QuizAttempt, User

DEFAULT_QUESTIONS_PER_ATTEMPT = 10
PASS_THRESHOLD_PCT = 70.0
ETA_SECONDS_PER_QUIZ = 120

class QuizSubmitRequest(BaseModel):
    attempt_id: UUID
    answers: dict[str, int]

def start_quiz_logic(quiz_id: UUID, current_user: User, session: Session):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    shared_quiz = session.get(SharedQuiz, quiz.shared_quiz_id) if quiz.shared_quiz_id else None
    effective_status = shared_quiz.status if shared_quiz else quiz.status

    if effective_status == "pending":
        if shared_quiz and shared_quiz.video_yt_ids:
            enqueue_quiz(shared_quiz.id, list(shared_quiz.video_yt_ids), shared_quiz.questions_per_attempt, engine, priority=PRIORITY_URGENT)
        elif quiz.video_yt_ids:
            enqueue_quiz(quiz.id, list(quiz.video_yt_ids), quiz.questions_per_attempt, engine, priority=PRIORITY_URGENT)

        ref_id = shared_quiz.yt_playlist_id if shared_quiz else None
        ref_seq = shared_quiz.sequence_order if shared_quiz else quiz.sequence_order
        pending_ahead = session.exec(select(SharedQuiz).where(SharedQuiz.yt_playlist_id == ref_id, SharedQuiz.status.in_(["pending", "generating"]), SharedQuiz.sequence_order < ref_seq)).all() if ref_id else []
        return {"status": "pending", "message": "Quiz generation hasn't started yet.", "queue_position": len(pending_ahead), "eta_seconds": max(30, len(pending_ahead) * ETA_SECONDS_PER_QUIZ)}

    if effective_status == "generating":
        ref_id = shared_quiz.yt_playlist_id if shared_quiz else None
        ref_seq = shared_quiz.sequence_order if shared_quiz else quiz.sequence_order
        pending_ahead = session.exec(select(SharedQuiz).where(SharedQuiz.yt_playlist_id == ref_id, SharedQuiz.status == "generating", SharedQuiz.sequence_order < ref_seq)).all() if ref_id else []
        return {"status": "generating", "message": "Quiz is being generated. Check back shortly.", "queue_position": len(pending_ahead), "eta_seconds": (len(pending_ahead) + 1) * ETA_SECONDS_PER_QUIZ}

    if effective_status.startswith("error_"):
        return {"status": effective_status, "message": "Quiz generation encountered an error."}

    source_id = shared_quiz.id if shared_quiz else quiz_id
    all_questions = session.exec(select(Question).where(Question.quiz_id == source_id)).all()
    q_count = (shared_quiz.questions_per_attempt if shared_quiz else quiz.questions_per_attempt) or DEFAULT_QUESTIONS_PER_ATTEMPT
    selected = all_questions[:q_count] if len(all_questions) >= q_count else all_questions
    q_ids = [str(q.id) for q in selected]
    q_data = [{"id": str(q.id), "question_text": q.question_text, "options": q.options.get("choices", [])} for q in selected]

    attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz_id, questions_asked={"question_ids": q_ids})
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    return {"status": "ready", "attempt_id": attempt.id, "questions": q_data, "questions_per_attempt": q_count, "pass_threshold_pct": PASS_THRESHOLD_PCT}
