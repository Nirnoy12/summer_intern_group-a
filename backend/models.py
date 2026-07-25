import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    total_xp: int = Field(default=0)
    current_level: int = Field(default=1)
    current_streak: int = Field(default=0)
    last_activity_date: Optional[date] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class Playlist(SQLModel, table=True):
    __tablename__ = "playlists"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "yt_playlist_id",
            name="uq_user_playlist"
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True
    )

    yt_playlist_id: str = Field(index=True)

    title: str
    description: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

class Video(SQLModel, table=True):
    __tablename__ = "videos"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    playlist_id: uuid.UUID = Field(foreign_key="playlists.id")
    yt_video_id: str
    sequence_order: int
    title: str
    xp_reward: int = Field(default=50)

    # Duration in seconds fetched from YouTube contentDetails API.
    # 0 = unknown (e.g. live streams, private videos).
    duration_seconds: int = Field(default=0)

    yt_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"

    user_id: uuid.UUID = Field(primary_key=True, foreign_key="users.id")
    video_id: uuid.UUID = Field(primary_key=True, foreign_key="videos.id")
    highest_watched_second: float = Field(default=0)
    last_watched_second: float = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None

class XpLog(SQLModel, table=True):
    __tablename__ = "xp_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    xp_amount: int
    source_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    playlist_id: uuid.UUID = Field(foreign_key="playlists.id", index=True)
    sequence_order: int
    title: str
    status: str = Field(default="pending")  # pending, generating, ready, error_*

    # How many questions are shown per attempt for this specific quiz.
    # Set by the smart quiz scheduler based on chapter duration:
    #   light (< 60 min chapter)    →  8 questions
    #   standard (1–3 hr chapter)   → 15 questions
    #   deep (3 hr+ chapter)        → 25 questions
    questions_per_attempt: int = Field(default=15)

    # YouTube video IDs whose transcripts feed this quiz.
    # Persisted so the priority-queue worker can regenerate from just the DB
    # after a server restart — no in-memory state required.
    video_yt_ids: List[Any] = Field(default=[], sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quiz_id: uuid.UUID = Field(foreign_key="quizzes.id", index=True)
    question_text: str
    options: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    correct_option_index: int
    explanation: Optional[str] = None

class QuizAttempt(SQLModel, table=True):
    __tablename__ = "quiz_attempts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    quiz_id: uuid.UUID = Field(foreign_key="quizzes.id", index=True)
    score: int = Field(default=0)
    passed: bool = Field(default=False)
    questions_asked: Dict[str, Any] = Field(default={}, sa_column=Column(JSON)) # List of question IDs asked
    created_at: datetime = Field(default_factory=datetime.utcnow)