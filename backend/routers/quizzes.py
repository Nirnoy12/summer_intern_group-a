from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.deps import get_current_user, get_session
from models import Question, QuizAttempt, User
from .quizzes_helpers import start_quiz_logic, QuizSubmitRequest, PASS_THRESHOLD_PCT

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

@router.get("/{quiz_id}/start")
def start_quiz(
    quiz_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return start_quiz_logic(quiz_id, current_user, session)

@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: UUID,
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    attempt = session.get(QuizAttempt, req.attempt_id)
    if not attempt or attempt.user_id != current_user.id or attempt.quiz_id != quiz_id:
        raise HTTPException(status_code=400, detail="Invalid attempt")

    if attempt.passed:
        return {"message": "Quiz already passed", "passed": True}

    asked_ids = attempt.questions_asked.get("question_ids", [])
    correct = sum(
        1 for qid in asked_ids
        if (q := session.get(Question, UUID(qid))) and req.answers.get(qid) == q.correct_option_index
    )
    total  = len(asked_ids)
    pct    = (correct / total * 100) if total else 0
    passed = pct >= PASS_THRESHOLD_PCT

    attempt.score  = int(pct)
    attempt.passed = passed
    session.add(attempt)
    session.commit()

    return {
        "score":         attempt.score,
        "passed":        passed,
        "correct_count": correct,
        "total":         total,
    }
