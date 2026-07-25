"""
Authentication Router
─────────────────────
Endpoints: POST /api/auth/register, POST /api/auth/login
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select

from core.deps import get_session, pwd_context, create_access_token
from models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class UserRegister(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    """Register a new user account."""
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd_context.hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Login with email + password. Returns a JWT bearer token."""
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Streak logic
    today = date.today()
    if user.last_activity_date == today - timedelta(days=1):
        user.current_streak += 1
    elif user.last_activity_date != today:
        user.current_streak = 1

    user.last_activity_date = today
    session.add(user)
    session.commit()

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
