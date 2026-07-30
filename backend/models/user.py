import uuid
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field

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

class XpLog(SQLModel, table=True):
    __tablename__ = "xp_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    xp_amount: int
    source_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
