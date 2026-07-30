"""
Delete Playlist Endpoint
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.deps import get_current_user, get_session
from models import Playlist, Video, Quiz, User, UserProgress, QuizAttempt

router = APIRouter()


@router.delete("/api/playlists/{playlist_id}")
def delete_playlist(
    playlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a playlist and all associated data (videos, progress, quizzes)."""
    playlist = session.exec(
        select(Playlist).where(
            Playlist.id == playlist_id, Playlist.user_id == current_user.id
        )
    ).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    videos = session.exec(select(Video).where(Video.playlist_id == playlist.id)).all()
    video_ids = [v.id for v in videos]

    if video_ids:
        for prog in session.exec(select(UserProgress).where(UserProgress.video_id.in_(video_ids))).all():
            session.delete(prog)
        session.flush()

    for v in videos:
        session.delete(v)
    session.flush()

    for q in session.exec(select(Quiz).where(Quiz.playlist_id == playlist.id)).all():
        for a in session.exec(select(QuizAttempt).where(QuizAttempt.quiz_id == q.id)).all():
            session.delete(a)
        session.flush()
        session.delete(q)
    session.flush()

    session.delete(playlist)
    session.commit()

    return {"message": "Playlist removed successfully"}
