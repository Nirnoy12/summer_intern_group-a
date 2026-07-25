"""
Playlists Router
────────────────
Endpoints:
  POST   /api/ingest/playlist
  GET    /api/playlists
  DELETE /api/playlists/{playlist_id}
  GET    /api/playlists/{playlist_id}/videos
"""
import os
import re
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from core.deps import engine, get_current_user, get_session
from llm_service import enqueue_quiz, PRIORITY_FIRST
from models import (
    Playlist, Quiz, Question, QuizAttempt,
    User, UserProgress, Video,
)

router = APIRouter(tags=["Playlists"])

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YT_BASE = "https://www.googleapis.com/youtube/v3"


# ── Smart Quiz Scheduling Constants ───────────────────────────────────────────
# Minimum cumulative seconds of video content to trigger a chapter quiz.
# Chapters shorter than this are merged into the next one.
QUIZ_MIN_CHAPTER_SECONDS = int(os.getenv("QUIZ_MIN_CHAPTER_SECONDS", 600))    # 10 min

# Duration thresholds that determine quiz depth / question count.
QUIZ_LIGHT_THRESHOLD_SECONDS   = int(os.getenv("QUIZ_LIGHT_THRESHOLD",    3600))   # < 60 min  → light
QUIZ_STANDARD_THRESHOLD_SECONDS = int(os.getenv("QUIZ_STANDARD_THRESHOLD", 10800))  # < 180 min → standard

# Questions shown to the student per quiz attempt, by depth tier.
QUIZ_LIGHT_QUESTIONS    = int(os.getenv("QUIZ_LIGHT_QUESTIONS",    8))   # 10–59 min chapter
QUIZ_STANDARD_QUESTIONS = int(os.getenv("QUIZ_STANDARD_QUESTIONS", 15))  # 1–3 hr chapter
QUIZ_DEEP_QUESTIONS     = int(os.getenv("QUIZ_DEEP_QUESTIONS",     25))  # 3 hr+ chapter

# Minimum total playlist duration (seconds) before a Final Quiz is added.
QUIZ_FINAL_MIN_SECONDS = int(os.getenv("QUIZ_FINAL_MIN_SECONDS", 900))   # 15 min


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_iso8601_duration(duration_str: str) -> int:
    """
    Parse an ISO 8601 duration string (e.g. 'PT3H12M45S', 'PT7M30S', 'PT45S')
    returned by the YouTube contentDetails API into total seconds (int).
    Returns 0 for live streams or malformed strings.
    """
    if not duration_str or duration_str == "P0D":
        return 0
    pattern = re.compile(
        r"P(?:(?P<days>\d+)D)?"
        r"(?:T"
        r"(?:(?P<hours>\d+)H)?"
        r"(?:(?P<minutes>\d+)M)?"
        r"(?:(?P<seconds>\d+)S)?"
        r")?"
    )
    m = pattern.fullmatch(duration_str)
    if not m:
        return 0
    days    = int(m.group("days")    or 0)
    hours   = int(m.group("hours")   or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = int(m.group("seconds") or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


async def _fetch_video_durations(yt_video_ids: list[str], client: httpx.AsyncClient) -> dict[str, int]:
    """
    Fetch duration_seconds for a list of YouTube video IDs via the
    'videos?part=contentDetails' endpoint. Handles pagination in batches of 50.
    Returns a dict mapping yt_video_id → duration_seconds.
    """
    durations: dict[str, int] = {}
    # YouTube allows max 50 IDs per request
    for i in range(0, len(yt_video_ids), 50):
        batch = yt_video_ids[i : i + 50]
        resp = await client.get(
            f"{YT_BASE}/videos",
            params={
                "part": "contentDetails",
                "id": ",".join(batch),
                "key": YOUTUBE_API_KEY,
            },
        )
        for item in resp.json().get("items", []):
            vid_id = item["id"]
            iso_dur = item.get("contentDetails", {}).get("duration", "")
            durations[vid_id] = _parse_iso8601_duration(iso_dur)
    return durations


def _questions_for_chapter(chapter_seconds: int) -> int:
    """Return the questions_per_attempt value for a chapter of the given duration."""
    if chapter_seconds < QUIZ_LIGHT_THRESHOLD_SECONDS:
        return QUIZ_LIGHT_QUESTIONS
    if chapter_seconds < QUIZ_STANDARD_THRESHOLD_SECONDS:
        return QUIZ_STANDARD_QUESTIONS
    return QUIZ_DEEP_QUESTIONS


def _build_smart_quiz_schedule(
    videos: list[Video],
    playlist_id: UUID,
) -> list[tuple["Quiz", list[str], int]]:
    """
    Duration-aware quiz placement algorithm.

    Strategy:
      1. Walk videos in sequence order, accumulating duration_seconds.
      2. When cumulative duration ≥ QUIZ_MIN_CHAPTER_SECONDS, close the chapter
         and schedule a quiz after the last video in that chapter.
      3. Any trailing chunk < QUIZ_MIN_CHAPTER_SECONDS is merged backwards into
         the previous chapter (no quiz for a 3-minute clip).
      4. A final "Full Playlist" quiz is appended if the total duration
         ≥ QUIZ_FINAL_MIN_SECONDS.

    Returns:
      List of (Quiz ORM object, [yt_video_id, ...], questions_per_attempt) tuples.
    """
    if not videos:
        return []

    # ── Phase 1: group videos into chapters by cumulative duration ────────────
    chapters: list[list[Video]] = []
    current_chapter: list[Video] = []
    current_seconds = 0

    for video in videos:
        current_chapter.append(video)
        current_seconds += video.duration_seconds

        if current_seconds >= QUIZ_MIN_CHAPTER_SECONDS:
            chapters.append(current_chapter)
            current_chapter = []
            current_seconds = 0

    # ── Phase 2: handle the trailing leftover chunk ───────────────────────────
    if current_chapter:
        if chapters:
            # Merge trailing chunk into the last chapter (no tiny quiz)
            chapters[-1].extend(current_chapter)
        else:
            # Edge case: every video is < MIN threshold → one chapter for all
            chapters.append(current_chapter)

    # ── Phase 3: build Quiz objects ───────────────────────────────────────────
    quiz_records: list[tuple[Quiz, list[str], int]] = []
    total_playlist_seconds = sum(v.duration_seconds for v in videos)

    for idx, chapter in enumerate(chapters):
        chapter_seconds = sum(v.duration_seconds for v in chapter)
        q_per_attempt   = _questions_for_chapter(chapter_seconds)
        last_video      = chapter[-1]
        quiz_num        = idx + 1

        # Determine a human-readable chapter label
        first_seq = chapter[0].sequence_order
        last_seq  = chapter[-1].sequence_order
        if first_seq == last_seq:
            chapter_label = f"Quiz {quiz_num} — Video {first_seq}"
        else:
            chapter_label = f"Quiz {quiz_num} — Videos {first_seq}–{last_seq}"

        chapter_vids = [v.yt_video_id for v in chapter]

        quiz = Quiz(
            playlist_id=playlist_id,
            # Place quiz just after the last video in the chapter
            sequence_order=last_video.sequence_order + 0.5,
            title=chapter_label,
            # All start as pending; only Quiz 1 is enqueued immediately.
            # The queue worker's _chain_to_next() cascades the rest.
            status="pending",
            questions_per_attempt=q_per_attempt,
            video_yt_ids=chapter_vids,  # persisted for recovery & chaining
        )
        quiz_records.append((
            quiz,
            chapter_vids,
            q_per_attempt,
        ))

    # ── Phase 4: Final Playlist Quiz (comprehensive review) ───────────────────
    if total_playlist_seconds >= QUIZ_FINAL_MIN_SECONDS and len(videos) > 1:
        final_q_per_attempt = _questions_for_chapter(total_playlist_seconds)
        final_vids = [v.yt_video_id for v in videos]
        final_quiz = Quiz(
            playlist_id=playlist_id,
            sequence_order=videos[-1].sequence_order + 0.75,
            title="Final Playlist Quiz",
            status="pending",
            questions_per_attempt=final_q_per_attempt,
            video_yt_ids=final_vids,
        )
        quiz_records.append((
            final_quiz,
            final_vids,
            final_q_per_attempt,
        ))

    return quiz_records



# ── Routes ─────────────────────────────────────────────────────────────────────

class PlaylistIngestRequest(BaseModel):
    playlist_id: str


@router.post("/api/ingest/playlist")
async def ingest_playlist(
    request: PlaylistIngestRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Fetch a public YouTube playlist and import it as a course."""
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API key not configured.")

    async with httpx.AsyncClient() as client:
        # 1. Playlist metadata
        pl_resp = await client.get(
            f"{YT_BASE}/playlists",
            params={"part": "snippet", "id": request.playlist_id, "key": YOUTUBE_API_KEY},
        )
        pl_data = pl_resp.json()
        if not pl_data.get("items"):
            raise HTTPException(status_code=404, detail="YouTube playlist not found.")

        snippet = pl_data["items"][0]["snippet"]

        # 2. Duplicate check
        if session.exec(
            select(Playlist).where(
                Playlist.user_id == current_user.id,
                Playlist.yt_playlist_id == request.playlist_id,
            )
        ).first():
            raise HTTPException(status_code=400, detail="Playlist already imported.")

        # 3. Save playlist
        playlist = Playlist(
            user_id=current_user.id,
            yt_playlist_id=request.playlist_id,
            title=snippet.get("title", "Unknown Title"),
            description=snippet.get("description", ""),
        )
        session.add(playlist)
        session.flush()

        # 4. Fetch all video pages
        videos_to_insert: list[Video] = []
        next_token = None
        order = 1

        while True:
            items_resp = await client.get(
                f"{YT_BASE}/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": request.playlist_id,
                    "maxResults": 50,
                    "pageToken": next_token,
                    "key": YOUTUBE_API_KEY,
                },
            )
            items_data = items_resp.json()

            for item in items_data.get("items", []):
                vs = item["snippet"]
                title = vs.get("title", "")
                if title in ("Deleted video", "Private video"):
                    continue
                videos_to_insert.append(
                    Video(
                        playlist_id=playlist.id,
                        yt_video_id=vs["resourceId"]["videoId"],
                        title=title,
                        sequence_order=order,
                        xp_reward=50,
                        yt_metadata=vs,
                    )
                )
                order += 1

            next_token = items_data.get("nextPageToken")
            if not next_token:
                break

        # 5. Fetch video durations from YouTube contentDetails API
        yt_video_ids = [v.yt_video_id for v in videos_to_insert]
        duration_map = await _fetch_video_durations(yt_video_ids, client)
        for v in videos_to_insert:
            v.duration_seconds = duration_map.get(v.yt_video_id, 0)

        # 6. Save videos
        session.add_all(videos_to_insert)
        session.commit()
        session.refresh(playlist)

        # 7. Build smart quiz schedule + flush
        sorted_vids  = sorted(videos_to_insert, key=lambda v: v.sequence_order)
        quiz_records = _build_smart_quiz_schedule(sorted_vids, playlist.id)
        for quiz, _, _ in quiz_records:
            session.add(quiz)
            session.flush()   # get quiz.id assigned
        session.commit()

        # 8. Enqueue ONLY the first quiz at high priority.
        #    The queue worker's _chain_to_next() will cascade through the rest
        #    automatically once Quiz 1 finishes.
        if quiz_records:
            first_quiz, first_vids, first_qpa = quiz_records[0]
            enqueue_quiz(
                first_quiz.id,
                first_vids,
                first_qpa,
                engine,
                priority=PRIORITY_FIRST,
            )

    return {
        "message": "Playlist ingested successfully",
        "playlist_title": playlist.title,
        "total_videos_added": len(videos_to_insert),
        "quizzes_scheduled": len(quiz_records),
    }


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

        # Thumbnail
        first = videos[0] if videos else None
        if first:
            try:
                thumb = first.yt_metadata.get("thumbnails", {}).get("high", {}).get("url")
                p_dict["thumbnail_url"] = thumb or f"https://img.youtube.com/vi/{first.yt_video_id}/hqdefault.jpg"
            except Exception:
                p_dict["thumbnail_url"] = f"https://img.youtube.com/vi/{first.yt_video_id}/hqdefault.jpg"
        else:
            p_dict["thumbnail_url"] = None

        # Progress stats
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
        for qq in session.exec(select(Question).where(Question.quiz_id == q.id)).all():
            session.delete(qq)
        for a in session.exec(select(QuizAttempt).where(QuizAttempt.quiz_id == q.id)).all():
            session.delete(a)
        session.flush()
        session.delete(q)
    session.flush()

    session.delete(playlist)
    session.commit()
    return {"message": "Playlist removed successfully"}


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

    # Merge and sort by sequence_order
    items = [
        {**v.model_dump(), "type": "video"} for v in videos
    ] + [
        {**q.model_dump(), "type": "quiz"} for q in quizzes
    ]
    items.sort(key=lambda x: x["sequence_order"])

    prev_completed = True
    result = []
    for item in items:
        if item["type"] == "video":
            prog = progress_lookup.get(item["id"])
            item["is_completed"] = prog.is_completed if prog else False
            item["highest_watched_second"] = prog.highest_watched_second if prog else 0
            item["last_watched_second"] = prog.last_watched_second if prog else 0
        else:  # quiz
            item["is_completed"] = item["id"] in passed_quizzes

        item["is_locked"] = not prev_completed
        prev_completed = item["is_completed"]
        result.append(item)

    return result
