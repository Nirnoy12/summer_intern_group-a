"""
App Lifespan Manager
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from core.deps import engine
from llm_service import quiz_generation_worker, recover_pending_quizzes

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: Creating/verifying database tables…")
    SQLModel.metadata.create_all(engine)

    logger.info("Running quiz generation recovery check…")
    await recover_pending_quizzes(engine)

    worker_task = asyncio.create_task(
        quiz_generation_worker(),
        name="quiz-generation-worker",
    )
    logger.info("Quiz generation worker started.")

    yield

    logger.info("Shutting down: cancelling quiz generation worker…")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Quiz generation worker stopped cleanly.")
