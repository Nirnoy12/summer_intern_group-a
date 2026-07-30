import logging
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)

LLM_PROVIDER = "groq"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_TRANSCRIPT_CHARS = 12_800
QUESTIONS_PER_BATCH  = 12
POOL_MULTIPLIER      = 4
MAX_BATCHES          = 6

def _validate_config() -> None:
    if not GROQ_API_KEY:
        logger.warning("[Config] LLM Provider is set to Groq, but GROQ_API_KEY is not set.")
    else:
        logger.info(f"[Config] LLM Provider: Groq Cloud AI  |  Model: {GROQ_MODEL}")

_validate_config()
