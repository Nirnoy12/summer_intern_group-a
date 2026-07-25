"""
Users Router
────────────
Endpoints: GET /api/users/me
"""
from fastapi import APIRouter, Depends

from core.deps import get_current_user
from models import User

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user.model_dump()
