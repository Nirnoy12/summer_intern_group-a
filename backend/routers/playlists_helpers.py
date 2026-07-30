"""
Playlists Router Helpers
"""
import os
import httpx
from pydantic import BaseModel
from sqlmodel import Session, select
from models import SharedQuiz, Quiz, Video
from .video_durations import fetch_video_durations as _fetch_durations

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YT_BASE = "https://www.googleapis.com/youtube/v3"

QUIZ_INTERVAL_VIDEOS = int(os.getenv("QUIZ_INTERVAL_VIDEOS", 5))
QUESTIONS_PER_QUIZ = int(os.getenv("QUESTIONS_PER_QUIZ", 10))


class PlaylistIngestRequest(BaseModel):
    playlist_id: str


async def fetch_video_durations(yt_video_ids: list[str], client: httpx.AsyncClient) -> dict[str, int]:
    return await _fetch_durations(yt_video_ids, client, YT_BASE, YOUTUBE_API_KEY)


def build_fixed_interval_quiz_schedule(
    videos: list[Video],
    yt_playlist_id: str,
    session: Session,
) -> list[tuple[SharedQuiz, Quiz, list[str], int]]:
    if not videos:
        return []

    results: list[tuple[SharedQuiz, Quiz, list[str], int]] = []

    for group_idx in range(0, len(videos), QUIZ_INTERVAL_VIDEOS):
        group = videos[group_idx : group_idx + QUIZ_INTERVAL_VIDEOS]
        if len(group) < QUIZ_INTERVAL_VIDEOS:
            break

        seq_order = group_idx // QUIZ_INTERVAL_VIDEOS + 1
        last_video = group[-1]

        first_seq = group[0].sequence_order
        last_seq = group[-1].sequence_order
        title = f"Quiz {seq_order} — Video {first_seq}" if first_seq == last_seq else f"Quiz {seq_order} — Videos {first_seq}–{last_seq}"

        chapter_vids = [v.yt_video_id for v in group]

        existing_shared = session.exec(
            select(SharedQuiz).where(
                SharedQuiz.yt_playlist_id == yt_playlist_id,
                SharedQuiz.sequence_order == seq_order,
            )
        ).first()

        shared_quiz = existing_shared or SharedQuiz(
            yt_playlist_id=yt_playlist_id,
            sequence_order=seq_order,
            title=title,
            status="pending",
            questions_per_attempt=QUESTIONS_PER_QUIZ,
            video_yt_ids=chapter_vids,
        )

        quiz = Quiz(
            sequence_order=last_video.sequence_order + 0.5,
            title=title,
            status=shared_quiz.status,
            questions_per_attempt=QUESTIONS_PER_QUIZ,
            video_yt_ids=chapter_vids,
        )

        results.append((shared_quiz, quiz, chapter_vids, QUESTIONS_PER_QUIZ))

    return results
