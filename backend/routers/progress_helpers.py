from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from models import Playlist, Quiz, QuizAttempt, User, UserProgress, Video, XpLog

SEEK_BUFFER_SECONDS = 15.0

def update_video_progress_logic(
    req,
    current_user: User,
    session: Session,
):
    video = session.get(Video, req.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    playlist = session.get(Playlist, video.playlist_id)
    if not playlist or playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this playlist.")

    prior_videos = session.exec(
        select(Video)
        .where(Video.playlist_id == video.playlist_id, Video.sequence_order < video.sequence_order)
        .order_by(Video.sequence_order)
    ).all()
    for prior in prior_videos:
        prog = session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.video_id == prior.id)).first()
        if not prog or not prog.is_completed:
            raise HTTPException(status_code=403, detail="Previous video not completed. Complete videos in order.")

    prior_quizzes = session.exec(
        select(Quiz)
        .where(Quiz.playlist_id == video.playlist_id, Quiz.sequence_order < video.sequence_order)
        .order_by(Quiz.sequence_order)
    ).all()
    for pq in prior_quizzes:
        passed = session.exec(select(QuizAttempt).where(QuizAttempt.user_id == current_user.id, QuizAttempt.quiz_id == pq.id, QuizAttempt.passed == True)).first()
        if not passed:
            raise HTTPException(status_code=403, detail="Previous quiz not passed. Complete quizzes in order.")

    progress = session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id, UserProgress.video_id == req.video_id)).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, video_id=req.video_id, highest_watched_second=0, last_watched_second=0, is_completed=False)

    if req.current_time > progress.highest_watched_second + SEEK_BUFFER_SECONDS:
        return {"allowed": False, "seek_to": progress.highest_watched_second, "completed": progress.is_completed}

    progress.last_watched_second = req.current_time
    progress.last_updated = datetime.utcnow()
    if req.current_time > progress.highest_watched_second:
        progress.highest_watched_second = req.current_time

    xp_awarded = 0
    leveled_up = False
    if not progress.is_completed and progress.highest_watched_second >= req.duration - SEEK_BUFFER_SECONDS:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        xp_awarded = video.xp_reward
        current_user.total_xp += xp_awarded
        new_level = (current_user.total_xp // 500) + 1
        leveled_up = new_level > current_user.current_level
        current_user.current_level = new_level
        session.add(current_user)
        session.add(XpLog(user_id=current_user.id, xp_amount=xp_awarded, source_type="video_completion"))

    session.add(progress)
    session.commit()

    return {
        "allowed": True,
        "highest_watched_second": progress.highest_watched_second,
        "last_watched_second": progress.last_watched_second,
        "completed": progress.is_completed,
        "xp_awarded": xp_awarded,
        "total_xp": current_user.total_xp,
        "current_level": current_user.current_level,
        "leveled_up": leveled_up,
    }
