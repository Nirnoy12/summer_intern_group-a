"""
Progress Router
───────────────
Endpoints: POST /api/progress/update
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from core.deps import get_current_user, get_session
from models import Playlist, Quiz, QuizAttempt, User, UserProgress, Video, XpLog

router = APIRouter(prefix="/api/progress", tags=["Progress"])

SEEK_BUFFER_SECONDS = 15.0  # Tolerance for seek-ahead detection


class VideoProgressRequest(BaseModel):
    video_id: UUID
    current_time: float
    duration: float


@router.post("/update")
def update_video_progress(
    req: VideoProgressRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Save a learner's video watch position. Enforces:
    - Sequential video order (prior videos must be completed)
    - Sequential quiz order (prior quizzes must be passed)
    - No skipping ahead beyond SEEK_BUFFER_SECONDS
    Awards XP on first completion.
    """
    video = session.get(Video, req.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    playlist = session.get(Playlist, video.playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this playlist.")

    # Enforce: all prior videos completed
    prior_videos = session.exec(
        select(Video)
        .where(Video.playlist_id == video.playlist_id, Video.sequence_order < video.sequence_order)
        .order_by(Video.sequence_order)
    ).all()
    for prior in prior_videos:
        prog = session.exec(
            select(UserProgress).where(
                UserProgress.user_id == current_user.id,
                UserProgress.video_id == prior.id,
            )
        ).first()
        if not prog or not prog.is_completed:
            raise HTTPException(
                status_code=403,
                detail="Previous video not completed. Complete videos in order.",
            )

    # Enforce: all prior quizzes passed
    prior_quizzes = session.exec(
        select(Quiz)
        .where(Quiz.playlist_id == video.playlist_id, Quiz.sequence_order < video.sequence_order)
        .order_by(Quiz.sequence_order)
    ).all()
    for pq in prior_quizzes:
        passed = session.exec(
            select(QuizAttempt).where(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.quiz_id == pq.id,
                QuizAttempt.passed == True,
            )
        ).first()
        if not passed:
            raise HTTPException(
                status_code=403,
                detail="Previous quiz not passed. Complete quizzes in order.",
            )

    # Get or create progress record
    progress = session.exec(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.video_id == req.video_id,
        )
    ).first()
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            video_id=req.video_id,
            highest_watched_second=0,
            last_watched_second=0,
            is_completed=False,
        )

    # Reject seek-ahead cheating
    if req.current_time > progress.highest_watched_second + SEEK_BUFFER_SECONDS:
        return {
            "allowed": False,
            "seek_to": progress.highest_watched_second,
            "completed": progress.is_completed,
        }

    # Update positions
    progress.last_watched_second = req.current_time
    progress.last_updated = datetime.utcnow()
    if req.current_time > progress.highest_watched_second:
        progress.highest_watched_second = req.current_time

    # XP + completion
    xp_awarded = 0
    leveled_up = False
    if not progress.is_completed and progress.highest_watched_second >= req.duration - SEEK_BUFFER_SECONDS:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()

        xp_awarded = video.xp_reward
        current_user.total_xp += xp_awarded
        new_level = (current_user.total_xp // 500) + 1
        leveled_up = new_level > current_user.current_level
        current_user.current_level = new_level
        session.add(current_user)
        session.add(XpLog(user_id=current_user.id, xp_amount=xp_awarded, source_type="video_completion"))

    session.add(progress)
    session.commit()

    return {
        "allowed": True,
        "highest_watched_second": progress.highest_watched_second,
        "last_watched_second": progress.last_watched_second,
        "completed": progress.is_completed,
        "xp_awarded": xp_awarded,
        "total_xp": current_user.total_xp,
        "current_level": current_user.current_level,
        "leveled_up": leveled_up,
    }
