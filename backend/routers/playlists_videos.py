"""
Playlist Videos Endpoint
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.deps import get_current_user, get_session
from models import Playlist, Video, Quiz, User, UserProgress, QuizAttempt

router = APIRouter()


@router.get("/api/playlists/{playlist_id}/videos")
def get_playlist_videos(
    playlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return all videos + quizzes for a playlist, with progress and lock state."""
    playlist = session.exec(
        select(Playlist).where(
            Playlist.id == playlist_id, Playlist.user_id == current_user.id
        )
    ).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found.")

    videos = session.exec(
        select(Video).where(Video.playlist_id == playlist_id).order_by(Video.sequence_order)
    ).all()
    quizzes = session.exec(
        select(Quiz).where(Quiz.playlist_id == playlist_id).order_by(Quiz.sequence_order)
    ).all()

    progress_lookup = {
        p.video_id: p
        for p in session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id)).all()
    }
    passed_quizzes = {
        a.quiz_id
        for a in session.exec(
            select(QuizAttempt).where(
                QuizAttempt.user_id == current_user.id, QuizAttempt.passed == True
            )
        ).all()
    }

    items = [
        {**v.model_dump(), "type": "video"} for v in videos
    ] + [
        {**q.model_dump(), "type": "quiz"} for q in quizzes
    ]
    items.sort(key=lambda x: x["sequence_order"])

    prev_video_completed = True
    result = []
    for item in items:
        if item["type"] == "video":
            prog = progress_lookup.get(item["id"])
            item["is_completed"] = prog.is_completed if prog else False
            item["highest_watched_second"] = prog.highest_watched_second if prog else 0
            item["last_watched_second"] = prog.last_watched_second if prog else 0
            item["is_locked"] = not prev_video_completed
            prev_video_completed = item["is_completed"]
        else:
            item["is_completed"] = item["id"] in passed_quizzes
            item["is_locked"] = not prev_video_completed

        result.append(item)

    return result
