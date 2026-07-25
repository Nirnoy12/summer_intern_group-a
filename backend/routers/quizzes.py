"""
Quizzes Router
──────────────
Endpoints:
  GET  /api/quizzes/{quiz_id}/start
  POST /api/quizzes/{quiz_id}/submit
"""
import random
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from core.deps import engine, get_current_user, get_session
from llm_service import enqueue_quiz, PRIORITY_URGENT, PRIORITY_FIRST
from models import Question, Quiz, QuizAttempt, User

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

# Fallback questions per attempt when the quiz record has no value set.
# In practice, Quiz.questions_per_attempt is always set by the smart scheduler.
DEFAULT_QUESTIONS_PER_ATTEMPT = 15

PASS_THRESHOLD_PCT = 70.0    # Score % required to pass
ETA_SECONDS_PER_QUIZ = 120   # Estimated generation time per queued quiz


@router.get("/{quiz_id}/start")
def start_quiz(
    quiz_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Begin a quiz attempt. Returns questions sampled from the pool.

    Smart status handling:
      - 'ready'     → return questions immediately.
      - 'pending'   → the quiz hasn't started generating yet.
                      Upgrade its priority to URGENT so it jumps to the
                      front of the generation queue, then return ETA.
      - 'generating'→ already in progress; return ETA.
      - 'error_*'   → generation failed; return error detail.
    """
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.status == "pending":
        # User has reached this quiz before generation started.
        # Bump it to URGENT priority so the worker picks it up immediately.
        if quiz.video_yt_ids:
            enqueue_quiz(
                quiz_id,
                list(quiz.video_yt_ids),
                quiz.questions_per_attempt,
                engine,
                priority=PRIORITY_URGENT,
            )
        # Count how many quizzes are ahead of this one in the queue
        pending_ahead = session.exec(
            select(Quiz).where(
                Quiz.status.in_(["pending", "generating"]),
                Quiz.created_at < quiz.created_at,
            )
        ).all()
        return {
            "status": "pending",
            "message": (
                "Quiz generation hasn't started yet — your request has been "
                "prioritised and will begin immediately."
            ),
            "queue_position": len(pending_ahead),
            "eta_seconds": max(30, len(pending_ahead) * ETA_SECONDS_PER_QUIZ),
        }

    if quiz.status == "generating":
        pending_ahead = session.exec(
            select(Quiz).where(
                Quiz.status == "generating",
                Quiz.created_at < quiz.created_at,
            )
        ).all()
        return {
            "status": "generating",
            "message": "Quiz is being generated. Check back shortly.",
            "queue_position": len(pending_ahead),
            "eta_seconds": (len(pending_ahead) + 1) * ETA_SECONDS_PER_QUIZ,
        }

    if quiz.status.startswith("error_"):
        return {
            "status": quiz.status,
            "message": (
                "Quiz generation encountered an error. "
                "The administrator has been notified."
            ),
        }

    # ── status == "ready" ─────────────────────────────────────────────────────
    all_questions = session.exec(select(Question).where(Question.quiz_id == quiz_id)).all()

    # Use this quiz's own depth setting; fall back to the default if somehow unset.
    q_count = quiz.questions_per_attempt or DEFAULT_QUESTIONS_PER_ATTEMPT

    selected = (
        random.sample(all_questions, q_count)
        if len(all_questions) >= q_count
        else all_questions
    )

    q_ids = [str(q.id) for q in selected]
    q_data = [
        {
            "id": str(q.id),
            "question_text": q.question_text,
            "options": q.options.get("choices", []),
        }
        for q in selected
    ]

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        questions_asked={"question_ids": q_ids},
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)

    return {
        "status": "ready",
        "attempt_id": attempt.id,
        "questions": q_data,
        "questions_per_attempt": q_count,
        "pass_threshold_pct": PASS_THRESHOLD_PCT,
    }


class QuizSubmitRequest(BaseModel):
    attempt_id: UUID
    answers: dict[str, int]  # question_id -> selected option index


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: UUID,
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Score a quiz attempt. Pass threshold is 70%.

    On pass: enqueues the next quiz in the playlist at PRIORITY_FIRST so
    it jumps ahead of chained quizzes from other playlists — the user will
    need it soon.
    """
    attempt = session.get(QuizAttempt, req.attempt_id)
    if not attempt or attempt.user_id != current_user.id or attempt.quiz_id != quiz_id:
        raise HTTPException(status_code=400, detail="Invalid attempt")

    if attempt.passed:
        return {"message": "Quiz already passed", "passed": True}

    asked_ids = attempt.questions_asked.get("question_ids", [])
    correct = sum(
        1
        for qid in asked_ids
        if (q := session.get(Question, UUID(qid))) and req.answers.get(qid) == q.correct_option_index
    )
    total  = len(asked_ids)
    pct    = (correct / total * 100) if total else 0
    passed = pct >= PASS_THRESHOLD_PCT

    attempt.score  = int(pct)
    attempt.passed = passed
    session.add(attempt)
    session.commit()

    # ── Pass-trigger: boost the next quiz to PRIORITY_FIRST ──────────────────
    # The user just passed this quiz, meaning they will soon reach the next one.
    # Upgrade it from CHAIN priority to FIRST priority so it generates before
    # anything queued at lower priority (e.g. later quizzes from other playlists).
    if passed:
        current_quiz = session.get(Quiz, quiz_id)
        if current_quiz:
            next_quiz = session.exec(
                select(Quiz).where(
                    Quiz.playlist_id    == current_quiz.playlist_id,
                    Quiz.status         == "pending",
                    Quiz.sequence_order >  current_quiz.sequence_order,
                ).order_by(Quiz.sequence_order)
            ).first()

            if next_quiz and next_quiz.video_yt_ids:
                enqueue_quiz(
                    next_quiz.id,
                    list(next_quiz.video_yt_ids),
                    next_quiz.questions_per_attempt,
                    engine,
                    priority=PRIORITY_FIRST,
                )

    return {
        "score":         attempt.score,
        "passed":        passed,
        "correct_count": correct,
        "total":         total,
    }
