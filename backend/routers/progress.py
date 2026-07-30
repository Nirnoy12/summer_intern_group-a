from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from core.deps import get_current_user, get_session
from models import User
from .progress_helpers import update_video_progress_logic

router = APIRouter(prefix="/api/progress", tags=["Progress"])

class VideoProgressRequest(BaseModel):
    video_id: UUID
    current_time: float
    duration: float

@router.post("/update")
def update_video_progress(
    req: VideoProgressRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return update_video_progress_logic(req, current_user, session)
