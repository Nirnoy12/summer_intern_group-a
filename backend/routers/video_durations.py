"""
YouTube Video Duration Helper
"""
import re
import httpx


def parse_iso8601_duration(duration_str: str) -> int:
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
    days = int(m.group("days") or 0)
    hours = int(m.group("hours") or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = int(m.group("seconds") or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


async def fetch_video_durations(yt_video_ids: list[str], client: httpx.AsyncClient, yt_base: str, api_key: str) -> dict[str, int]:
    durations: dict[str, int] = {}
    for i in range(0, len(yt_video_ids), 50):
        batch = yt_video_ids[i : i + 50]
        resp = await client.get(
            f"{yt_base}/videos",
            params={
                "part": "contentDetails",
                "id": ",".join(batch),
                "key": api_key,
            },
        )
        for item in resp.json().get("items", []):
            vid_id = item["id"]
            iso_dur = item.get("contentDetails", {}).get("duration", "")
            durations[vid_id] = parse_iso8601_duration(iso_dur)
    return durations
