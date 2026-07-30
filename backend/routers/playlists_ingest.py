"""
Playlists Ingestion Endpoint
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.deps import engine, get_current_user, get_session
from llm_service import enqueue_quiz, PRIORITY_FIRST
from models import Playlist, User, SharedQuiz
from .playlists_helpers import YOUTUBE_API_KEY, YT_BASE, PlaylistIngestRequest, fetch_video_durations, build_fixed_interval_quiz_schedule
from .playlists_yt_fetch import fetch_youtube_playlist_videos

router = APIRouter()


@router.post("/api/ingest/playlist")
async def ingest_playlist(
    request: PlaylistIngestRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API key not configured.")

    async with httpx.AsyncClient() as client:
        pl_resp = await client.get(
            f"{YT_BASE}/playlists",
            params={"part": "snippet", "id": request.playlist_id, "key": YOUTUBE_API_KEY},
        )
        pl_data = pl_resp.json()
        if not pl_data.get("items"):
            raise HTTPException(status_code=404, detail="YouTube playlist not found.")

        snippet = pl_data["items"][0]["snippet"]

        if session.exec(select(Playlist).where(Playlist.user_id == current_user.id, Playlist.yt_playlist_id == request.playlist_id)).first():
            raise HTTPException(status_code=400, detail="Playlist already imported.")

        playlist = Playlist(user_id=current_user.id, yt_playlist_id=request.playlist_id, title=snippet.get("title", "Unknown Title"), description=snippet.get("description", ""))
        session.add(playlist)
        session.flush()

        videos_to_insert = await fetch_youtube_playlist_videos(request.playlist_id, playlist.id, client, YT_BASE, YOUTUBE_API_KEY)
        yt_video_ids = [v.yt_video_id for v in videos_to_insert]
        duration_map = await fetch_video_durations(yt_video_ids, client)
        for v in videos_to_insert:
            v.duration_seconds = duration_map.get(v.yt_video_id, 0)

        session.add_all(videos_to_insert)
        session.commit()
        session.refresh(playlist)

        sorted_vids = sorted(videos_to_insert, key=lambda v: v.sequence_order)
        quiz_records = build_fixed_interval_quiz_schedule(sorted_vids, request.playlist_id, session)

        shared_quizzes_to_enqueue: list[tuple[SharedQuiz, list[str], int]] = []
        for shared_quiz, quiz, vids, qpa in quiz_records:
            if shared_quiz.id is None:
                session.add(shared_quiz)
                session.flush()
                shared_quizzes_to_enqueue.append((shared_quiz, vids, qpa))
            else:
                session.merge(shared_quiz)
                session.flush()

            quiz.playlist_id = playlist.id
            quiz.shared_quiz_id = shared_quiz.id
            quiz.status = shared_quiz.status
            session.add(quiz)
            session.flush()

        session.commit()

        if shared_quizzes_to_enqueue:
            first_sq, first_vids, first_qpa = shared_quizzes_to_enqueue[0]
            enqueue_quiz(first_sq.id, first_vids, first_qpa, engine, priority=PRIORITY_FIRST)

    return {
        "message": "Playlist ingested successfully",
        "playlist_title": playlist.title,
        "total_videos_added": len(videos_to_insert),
        "quizzes_scheduled": len(quiz_records),
        "quizzes_reused": len(quiz_records) - len(shared_quizzes_to_enqueue),
    }
