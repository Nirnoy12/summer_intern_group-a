"""
LMS Core API — Application Entry Point
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from core.lifespan import lifespan
import routers.auth as auth
import routers.users as users
import routers.playlists as playlists
import routers.progress as progress
import routers.quizzes as quizzes

logger = logging.getLogger(__name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(playlists.router)
app.include_router(progress.router)
app.include_router(quizzes.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"message": "LMS API is running.", "version": "1.0.0"}
