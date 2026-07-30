"""
Get Playlists Endpoint
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from core.deps import get_current_user, get_session
from models import Playlist, Video, User, UserProgress

router = APIRouter()


@router.get("/api/playlists")
def get_playlists(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all playlists for the current user, with progress stats."""
    playlists = session.exec(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(Playlist.created_at.desc())
    ).all()

    result = []
    for p in playlists:
        videos = session.exec(
            select(Video).where(Video.playlist_id == p.id).order_by(Video.sequence_order)
        ).all()

        p_dict = p.model_dump()
        p_dict["video_count"] = len(videos)

        first = videos[0] if videos else None
        if first:
            try:
                thumb = first.yt_metadata.get("thumbnails", {}).get("high", {}).get("url")
                p_dict["thumbnail_url"] = thumb or f"https://img.youtube.com/vi/{first.yt_video_id}/hqdefault.jpg"
            except Exception:
                p_dict["thumbnail_url"] = f"https://img.youtube.com/vi/{first.yt_video_id}/hqdefault.jpg"
        else:
            p_dict["thumbnail_url"] = None

        video_ids = [v.id for v in videos]
        completed = 0
        if video_ids:
            completed = len(
                session.exec(
                    select(UserProgress).where(
                        UserProgress.user_id == current_user.id,
                        UserProgress.video_id.in_(video_ids),
                        UserProgress.is_completed == True,
                    )
                ).all()
            )

        p_dict["completed_videos"] = completed
        p_dict["is_completed"] = len(videos) > 0 and completed == len(videos)
        p_dict["course_progress_percentage"] = (completed / len(videos) * 100) if videos else 0
        p_dict["status"] = (
            "Completed" if p_dict["is_completed"]
            else ("In Progress" if completed > 0 else "Not Started")
        )

        last_accessed = None
        if video_ids:
            latest = session.exec(
                select(UserProgress)
                .where(
                    UserProgress.user_id == current_user.id,
                    UserProgress.video_id.in_(video_ids),
                )
                .order_by(UserProgress.last_updated.desc())
            ).first()
            if latest:
                last_accessed = latest.last_updated
        p_dict["last_accessed_date"] = last_accessed

        result.append(p_dict)

    return result
