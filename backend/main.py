"""
LMS Core API — Application Entry Point
────────────────────────────────────────
This file is intentionally thin. All business logic lives in:
  routers/auth.py       → /api/auth/*
  routers/users.py      → /api/users/*
  routers/playlists.py  → /api/ingest/* and /api/playlists/*
  routers/progress.py   → /api/progress/*
  routers/quizzes.py    → /api/quizzes/*

Shared dependencies (engine, session, auth) live in:
  core/deps.py
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
import os

load_dotenv()

from core.deps import engine  # noqa: E402 — must come after load_dotenv()
import routers.auth as auth
import routers.users as users
import routers.playlists as playlists
import routers.progress as progress
import routers.quizzes as quizzes
from llm_service import quiz_generation_worker, recover_pending_quizzes  # noqa: E402

logger = logging.getLogger(__name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Starting up: Creating/verifying database tables…")
    SQLModel.metadata.create_all(engine)

    # Re-enqueue any quizzes that were interrupted by a previous shutdown.
    # This runs before the worker starts so recovery jobs are already in the
    # queue when the worker picks up its first item.
    logger.info("Running quiz generation recovery check…")
    await recover_pending_quizzes(engine)

    # Start the single global quiz generation worker.
    # It processes the priority queue until the server shuts down.
    worker_task = asyncio.create_task(
        quiz_generation_worker(),
        name="quiz-generation-worker",
    )
    logger.info("Quiz generation worker started.")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down: cancelling quiz generation worker…")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Quiz generation worker stopped cleanly.")


app = FastAPI(
    title="LMS Core API",
    description="Gamified LMS with YouTube ingestion and AI-generated quizzes.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred", "details": str(exc)},
    )


# ── Mount all feature routers ──────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(playlists.router)
app.include_router(progress.router)
app.include_router(quizzes.router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint."""
    return {"message": "LMS API is running.", "version": "1.0.0"}
