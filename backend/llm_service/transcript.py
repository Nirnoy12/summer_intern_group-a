import logging
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

def get_transcripts(video_ids: list[str]) -> str:
    parts: list[str] = []
    for vid in video_ids:
        try:
            entries = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join(e["text"] for e in entries)
            parts.append(f"=== Video: {vid} ===\n{text.strip()}\n")
        except Exception as exc:
            logger.warning(f"[Transcript] Unavailable for {vid}: {exc}")
            parts.append(f"=== Video: {vid} ===\n[No transcript available]\n")
    return "\n".join(parts)
