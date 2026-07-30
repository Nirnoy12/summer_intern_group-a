"""
YouTube API Fetch Helpers for Ingest
"""
import httpx
from models import Video


async def fetch_youtube_playlist_videos(playlist_id: str, playlist_db_id, client: httpx.AsyncClient, yt_base: str, api_key: str) -> list[Video]:
    videos_to_insert: list[Video] = []
    next_token = None
    order = 1

    while True:
        items_resp = await client.get(
            f"{yt_base}/playlistItems",
            params={
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": 50,
                "pageToken": next_token,
                "key": api_key,
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
                    playlist_id=playlist_db_id,
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

    return videos_to_insert
