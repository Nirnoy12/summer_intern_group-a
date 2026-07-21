import httpx
import random
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel

from models import User, Playlist, Video, UserProgress, XpLog, Quiz, Question, QuizAttempt
from llm_service import generate_quiz_pool_background

from datetime import datetime, timedelta, date
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

engine = create_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=50)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Creating database tables in CockroachDB ")
    SQLModel.metadata.create_all(engine)
    yield
    print("Shutting down ")

app = FastAPI(title='LMS Core API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_session():
    with Session(engine) as session:
        yield session

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = session.get(User, UUID(user_id))
    if user is None:
        raise credentials_exception
    return user

class UserRegister(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd_context.hash(user_data.password)

    new_user = User(email=user_data.email, hashed_password=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    today = date.today()
    if user.last_activity_date == today - timedelta(days=1):
        user.current_streak += 1 # Logged in yesterday, streak continues!
    elif user.last_activity_date != today:
        user.current_streak = 1  # Missed a day, reset to 1
        
    user.last_activity_date = today
    session.add(user)
    session.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}



@app.get('/')
def read_root():
    return {"message": "Hello World! The api is running."}


class PlaylistIngestRequest(BaseModel):
    playlist_id: str

@app.post("/api/ingest/playlist")
async def ingest_playlist(
    request: PlaylistIngestRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API key not configured.")

    base_url = "https://www.googleapis.com/youtube/v3"

    async with httpx.AsyncClient() as client:
        # 1. Fetch Playlist Metadata
        playlist_resp = await client.get(
            f"{base_url}/playlists",
            params={
                "part": "snippet",
                "id": request.playlist_id,
                "key": YOUTUBE_API_KEY
            }
        )
        playlist_data = playlist_resp.json()

        if not playlist_data.get("items"):
            raise HTTPException(status_code=404, detail="YouTube playlist not found.")

        snippet = playlist_data["items"][0]["snippet"]

        existing_playlist = session.exec(
            select(Playlist).where(
                Playlist.user_id == current_user.id,
                Playlist.yt_playlist_id == request.playlist_id
            )
        ).first()

        if existing_playlist:
            raise HTTPException(
                status_code=400,
                detail="Playlist already imported."
            )
                
        # 2. Save Playlist to CockroachDB (Matches models.py EXACTLY)
        new_playlist = Playlist(
            user_id=current_user.id,
            yt_playlist_id=request.playlist_id,
            title=snippet.get("title", "Unknown Title"),
            description=snippet.get("description", "")
        )
        session.add(new_playlist)
        session.flush() 

        # 3. Fetch all Videos in the Playlist
        videos_to_insert = []
        next_page_token = None
        seq_order = 1

        while True:
            items_resp = await client.get(
                f"{base_url}/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": request.playlist_id,
                    "maxResults": 50, # Max allowed by YouTube API
                    "pageToken": next_page_token,
                    "key": YOUTUBE_API_KEY
                }
            )
            items_data = items_resp.json()

            for item in items_data.get("items", []):
                video_snippet = item["snippet"]
                
                # 4. Create Video records (Matches models.py EXACTLY)
                video_record = Video(
                    playlist_id=new_playlist.id,
                    yt_video_id=video_snippet["resourceId"]["videoId"],
                    title=video_snippet["title"],
                    sequence_order=seq_order,
                    xp_reward=50,
                    yt_metadata=video_snippet # Saves the raw JSON to your sa_column=Column(JSON)
                )
                videos_to_insert.append(video_record)
                seq_order += 1

            next_page_token = items_data.get("nextPageToken")
            if not next_page_token:
                break # Exit loop when no more pages exist

        # 5. Bulk save videos to Database
        session.add_all(videos_to_insert)
        session.commit()
        session.refresh(new_playlist)

        # Generate Quizzes (every 3 videos)
        videos = sorted(videos_to_insert, key=lambda v: v.sequence_order)
        quiz_records = []
        for i in range(2, len(videos), 3):
            quiz = Quiz(
                playlist_id=new_playlist.id,
                sequence_order=videos[i].sequence_order + 0.5, # Place after 3rd video
                title=f"Quiz after {videos[i].title}",
                status="generating"
            )
            session.add(quiz)
            session.flush()
            quiz_records.append((quiz, [v.yt_video_id for v in videos[i-2:i+1]]))
            
        # Final quiz if the last chunk wasn't exactly 3
        if len(videos) % 3 != 0 and len(videos) > 0:
            last_idx = len(videos) - 1
            quiz = Quiz(
                playlist_id=new_playlist.id,
                sequence_order=videos[last_idx].sequence_order + 0.5,
                title=f"Final Playlist Quiz",
                status="generating"
            )
            session.add(quiz)
            session.flush()
            # grab the last chunk of videos
            start_idx = len(videos) - (len(videos) % 3)
            quiz_records.append((quiz, [v.yt_video_id for v in videos[start_idx:]]))
            
        session.commit()
        
        # Trigger background tasks
        for quiz, video_ids in quiz_records:
            background_tasks.add_task(generate_quiz_pool_background, quiz.id, video_ids, engine)

    return {
        "message": "Playlist ingested successfully",
        "playlist_title": new_playlist.title,
        "total_videos_added": len(videos_to_insert)
    }

@app.get("/api/playlists")
def get_playlists(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    playlists = session.exec(
        select(Playlist)
        .where(Playlist.user_id == current_user.id)
        .order_by(Playlist.created_at.desc())
    ).all()

    result = []

    for p in playlists:
        videos = session.exec(
            select(Video)
            .where(Video.playlist_id == p.id)
            .order_by(Video.sequence_order)
        ).all()

        p_dict = p.model_dump()
        p_dict["video_count"] = len(videos)

        # Thumbnail
        if videos:
            first_video = videos[0]
            try:
                thumb_url = (
                    first_video.yt_metadata
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                )
                if not thumb_url:
                    thumb_url = (
                        f"https://img.youtube.com/vi/"
                        f"{first_video.yt_video_id}/hqdefault.jpg"
                    )
                p_dict["thumbnail_url"] = thumb_url
            except Exception:
                p_dict["thumbnail_url"] = (
                    f"https://img.youtube.com/vi/"
                    f"{first_video.yt_video_id}/hqdefault.jpg"
                )
        else:
            p_dict["thumbnail_url"] = None

        # -------- Progress --------

        video_ids = [video.id for video in videos]

        completed_videos = 0

        if video_ids:
            completed_videos = len(
                session.exec(
                    select(UserProgress).where(
                        UserProgress.user_id == current_user.id,
                        UserProgress.video_id.in_(video_ids),
                        UserProgress.is_completed == True
                    )
                ).all()
            )

        p_dict["completed_videos"] = completed_videos
        p_dict["is_completed"] = (
            len(videos) > 0 and completed_videos == len(videos)
        )
        p_dict["course_progress_percentage"] = (completed_videos / len(videos)) * 100 if videos else 0
        p_dict["status"] = "Completed" if p_dict["is_completed"] else ("In Progress" if completed_videos > 0 else "Not Started")
        
        last_accessed = None
        if video_ids:
            latest_progress = session.exec(
                select(UserProgress).where(
                    UserProgress.user_id == current_user.id,
                    UserProgress.video_id.in_(video_ids)
                ).order_by(UserProgress.last_updated.desc())
            ).first()
            if latest_progress:
                last_accessed = latest_progress.last_updated
        p_dict["last_accessed_date"] = last_accessed

        result.append(p_dict)

    return result

@app.delete("/api/playlists/{playlist_id}")
def delete_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    playlist = session.exec(
        select(Playlist).where(
            Playlist.id == playlist_id,
            Playlist.user_id == current_user.id
        )
    ).first()

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Delete all associated videos and progress
    videos = session.exec(select(Video).where(Video.playlist_id == playlist.id)).all()
    video_ids = [v.id for v in videos]
    
    if video_ids:
        progress_records = session.exec(
            select(UserProgress).where(UserProgress.video_id.in_(video_ids))
        ).all()
        for p in progress_records:
            session.delete(p)

    for v in videos:
        session.delete(v)
        
    quizzes = session.exec(select(Quiz).where(Quiz.playlist_id == playlist.id)).all()
    for q in quizzes:
        questions = session.exec(select(Question).where(Question.quiz_id == q.id)).all()
        for qq in questions:
            session.delete(qq)
        attempts = session.exec(select(QuizAttempt).where(QuizAttempt.quiz_id == q.id)).all()
        for a in attempts:
            session.delete(a)
        session.delete(q)

    session.delete(playlist)
    session.commit()

    return {"message": "Playlist removed successfully"}

@app.get("/api/playlists/{playlist_id}/videos")
def get_playlist_videos(
    playlist_id: UUID, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    playlist = session.exec(
        select(Playlist).where(
            Playlist.id == playlist_id,
            Playlist.user_id == current_user.id
        )
    ).first()

    if not playlist:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found."
        )
    
    videos = session.exec(select(Video).where(Video.playlist_id == playlist_id).order_by(Video.sequence_order)).all()
    quizzes = session.exec(select(Quiz).where(Quiz.playlist_id == playlist_id).order_by(Quiz.sequence_order)).all()
    
    progress_records = session.exec(select(UserProgress).where(UserProgress.user_id == current_user.id)).all()
    progress_lookup = {p.video_id: p for p in progress_records}
    
    quiz_attempts = session.exec(select(QuizAttempt).where(QuizAttempt.user_id == current_user.id, QuizAttempt.passed == True)).all()
    passed_quizzes = {a.quiz_id for a in quiz_attempts}

    # Mix videos and quizzes
    items = []
    for v in videos:
        d = v.model_dump()
        d["type"] = "video"
        items.append(d)
    for q in quizzes:
        d = q.model_dump()
        d["type"] = "quiz"
        items.append(d)
        
    items.sort(key=lambda x: x["sequence_order"])
    
    prev_completed = True

    result = []
    for item in items:
        if item["type"] == "video":
            progress = progress_lookup.get(item["id"])
            if progress:
                item["is_completed"] = progress.is_completed
                item["highest_watched_second"] = progress.highest_watched_second
                item["last_watched_second"] = progress.last_watched_second
            else:
                item["is_completed"] = False
                item["highest_watched_second"] = 0
                item["last_watched_second"] = 0
            
            item["is_locked"] = not prev_completed
            prev_completed = item["is_completed"]
            
        elif item["type"] == "quiz":
            item["is_completed"] = item["id"] in passed_quizzes
            item["is_locked"] = not prev_completed
            prev_completed = item["is_completed"]
            
        result.append(item)

    return result

@app.get("/api/users/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user.model_dump()




class VideoProgressRequest(BaseModel):
    video_id: UUID
    current_time: float
    duration: float


@app.post("/api/progress/update")
def update_video_progress(
    request: VideoProgressRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    BUFFER = 15.0  # seconds of tolerance

    # Check if video exists
    video = session.get(Video, request.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    

    playlist = session.get(Playlist, video.playlist_id)

    if not playlist or playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this playlist."
        )

    # Sequential locking: verify all prior videos in the playlist are completed
    prior_videos = session.exec(
        select(Video).where(
            Video.playlist_id == video.playlist_id,
            Video.sequence_order < video.sequence_order
        ).order_by(Video.sequence_order)
    ).all()

    for prior in prior_videos:
        prior_progress = session.exec(
            select(UserProgress).where(
                UserProgress.user_id == current_user.id,
                UserProgress.video_id == prior.id
            )
        ).first()
        if not prior_progress or not prior_progress.is_completed:
            raise HTTPException(
                status_code=403,
                detail="Previous video not completed. Complete videos in order."
            )
            
    # Sequential locking: verify all prior quizzes in the playlist are completed
    prior_quizzes = session.exec(
        select(Quiz).where(
            Quiz.playlist_id == video.playlist_id,
            Quiz.sequence_order < video.sequence_order
        ).order_by(Quiz.sequence_order)
    ).all()

    for prior_quiz in prior_quizzes:
        attempt = session.exec(
            select(QuizAttempt).where(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.quiz_id == prior_quiz.id,
                QuizAttempt.passed == True
            )
        ).first()
        if not attempt:
            raise HTTPException(
                status_code=403,
                detail="Previous quiz not passed. Complete quizzes in order."
            )

    # Get or create progress record
    progress = session.exec(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.video_id == request.video_id
        )
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            video_id=request.video_id,
            highest_watched_second=0,
            last_watched_second=0,
            is_completed=False
        )

    # Prevent skipping ahead
    if request.current_time > progress.highest_watched_second + BUFFER:
        return {
            "allowed": False,
            "seek_to": progress.highest_watched_second,
            "completed": progress.is_completed
        }

    # Update watch progress
    progress.last_watched_second = request.current_time
    progress.last_updated = datetime.utcnow()

    if request.current_time > progress.highest_watched_second:
        progress.highest_watched_second = request.current_time

    # Completion check
    xp_awarded = 0
    leveled_up = False

    if (
        not progress.is_completed
        and progress.highest_watched_second >= request.duration - BUFFER
    ):
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()

        # Award XP
        xp_awarded = video.xp_reward
        current_user.total_xp += xp_awarded

        new_level = (current_user.total_xp // 500) + 1
        leveled_up = new_level > current_user.current_level
        current_user.current_level = new_level

        session.add(current_user)

        xp_log = XpLog(
            user_id=current_user.id,
            xp_amount=xp_awarded,
            source_type="video_completion"
        )
        session.add(xp_log)

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
        "leveled_up": leveled_up
    }


@app.get("/api/quizzes/{quiz_id}/start")
def start_quiz(quiz_id: UUID, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    if quiz.status != "ready":
        return {"status": quiz.status, "message": "Quiz is not ready yet."}
        
    questions = session.exec(select(Question).where(Question.quiz_id == quiz_id)).all()
    if len(questions) < 30:
        # Fallback if we didn't generate enough
        selected_questions = questions
    else:
        selected_questions = random.sample(questions, 30)
        
    # We will just return the questions, without correct_option_index
    q_data = []
    q_ids = []
    for q in selected_questions:
        q_ids.append(str(q.id))
        q_data.append({
            "id": str(q.id),
            "question_text": q.question_text,
            "options": q.options.get("choices", [])
        })
        
    # Create an attempt record to track these specific questions
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        questions_asked={"question_ids": q_ids}
    )
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    
    return {
        "status": "ready",
        "attempt_id": attempt.id,
        "questions": q_data
    }


class QuizSubmitRequest(BaseModel):
    attempt_id: UUID
    answers: dict[str, int] # question_id -> selected_option_index

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: UUID, request: QuizSubmitRequest, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    attempt = session.get(QuizAttempt, request.attempt_id)
    if not attempt or attempt.user_id != current_user.id or attempt.quiz_id != quiz_id:
        raise HTTPException(status_code=400, detail="Invalid attempt")
        
    if attempt.passed:
        return {"message": "Quiz already passed", "passed": True}
        
    asked_q_ids = attempt.questions_asked.get("question_ids", [])
    
    correct_count = 0
    total = len(asked_q_ids)
    
    for q_id_str in asked_q_ids:
        q = session.get(Question, UUID(q_id_str))
        if q and q_id_str in request.answers:
            if request.answers[q_id_str] == q.correct_option_index:
                correct_count += 1
                
    score_percentage = (correct_count / total) * 100 if total > 0 else 0
    passed = score_percentage >= 70.0
    
    attempt.score = int(score_percentage)
    attempt.passed = passed
    session.add(attempt)
    session.commit()
    
    return {
        "score": attempt.score,
        "passed": passed,
        "correct_count": correct_count,
        "total": total
    }

