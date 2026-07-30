"""
Groq LLM Caller
"""
import asyncio
import logging
import httpx
from .config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL
from .llm_prompt import _build_prompt, _extract_json_array

logger = logging.getLogger(__name__)


async def _call_groq(prompt: str) -> list[dict]:
    if not GROQ_API_KEY:
        logger.error("[Groq] GROQ_API_KEY is missing")
        return []
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert educator. You always respond with valid JSON only. "
                    "Never include markdown fences or any explanation outside the JSON array."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.65,
        "max_tokens": 3072,
        "top_p": 0.90,
        "response_format": {"type": "json_object"},
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(GROQ_API_URL, headers=headers, json=payload)
            if resp.status_code == 429:
                logger.warning("[Groq] Rate limited (429), retrying after 10 seconds...")
                await asyncio.sleep(10)
                resp = await client.post(GROQ_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            return _extract_json_array(resp.json()["choices"][0]["message"]["content"])
    except Exception as exc:
        logger.error(f"[Groq] Unexpected error calling API: {exc}")
    return []


async def _call_llm(prompt: str) -> list[dict]:
    return await _call_groq(prompt)
