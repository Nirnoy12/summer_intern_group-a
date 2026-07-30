import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class SharedQuiz(SQLModel, table=True):
    __tablename__ = "shared_quizzes"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    yt_playlist_id: str = Field(index=True)
    sequence_order: int
    title: str
    status: str = Field(default="pending")
    video_yt_ids: List[Any] = Field(default=[], sa_column=Column(JSON))
    questions_per_attempt: int = Field(default=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    playlist_id: uuid.UUID = Field(foreign_key="playlists.id", index=True)
    shared_quiz_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="shared_quizzes.id", index=True
    )
    sequence_order: float
    title: str
    status: str = Field(default="pending")
    questions_per_attempt: int = Field(default=10)
    video_yt_ids: List[Any] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Question(SQLModel, table=True):
    __tablename__ = "questions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quiz_id: uuid.UUID = Field(foreign_key="shared_quizzes.id", index=True)
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
    questions_asked: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
