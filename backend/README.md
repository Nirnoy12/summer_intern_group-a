# LMS Gamified Platform — Backend Documentation

Welcome to the backend of the Gamified Learning Management System (LMS). This service provides a RESTful API powered by **FastAPI**, handles async operations, orchestrates database interactions with **CockroachDB**, and leverages **Groq Cloud AI (`llama-3.1-8b-instant`)** to dynamically generate AI quiz pools from YouTube transcripts.

---

## 🛠️ Tech Stack & Architecture

- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **ORM & Validation**: [SQLModel](https://sqlmodel.tiangolo.com/) (Combines Pydantic & SQLAlchemy 2.x)
- **Database**: [CockroachDB](https://www.cockroachlabs.com/) (Distributed Serverless Postgres-compatible SQL database)
- **Authentication**: JWT (JSON Web Tokens) + [Argon2](https://argon2-cffi.readthedocs.io/en/stable/) password hashing
- **HTTP Client**: [httpx](https://www.python-httpx.org/) (used for calling YouTube Data API v3 & Groq Cloud AI API)
- **LLM Engine**: [Groq Cloud AI](https://console.groq.com) (High-speed LPU inference, `llama-3.1-8b-instant`)
- **Transcript Extraction**: `youtube-transcript-api`

---

## 📁 Modular Directory Structure

```
backend/
├── core/                             # Core Infrastructure & Configuration
│   ├── deps.py                       # Auth, DB Session & JWT Dependencies
│   └── lifespan.py                   # App Lifespan & DB Initialization
│
├── models/                           # Modular SQLModel Schemas (CockroachDB)
│   ├── playlist.py                   # Playlist & Video Schemas
│   ├── quiz.py                       # SharedQuiz, Quiz & Question Schemas
│   └── user.py                       # User & XpLog Schemas
│
├── routers/                          # Modular API Endpoints & Handlers
│   ├── auth.py                       # Authentication (Register, Login, Token)
│   ├── users.py                      # User Profile & Stats Endpoint (/users/me)
│   ├── playlists.py                  # Playlist Router Dispatcher
│   ├── playlists_ingest.py           # YouTube Playlist Ingestion Pipeline
│   ├── playlists_get.py              # Playlist Retrieval & Listing
│   ├── playlists_delete.py           # Playlist Deletion
│   ├── playlists_yt_fetch.py         # YouTube Data API Integration
│   ├── playlists_videos.py           # Video Sequence & Progress Endpoint
│   ├── playlists_helpers.py          # Sequence & Chapter Helper Utilities
│   ├── progress.py                   # Anti-Cheat Video Progress Tracking
│   ├── progress_helpers.py           # Seek Prevention & XP Calculation
│   ├── quizzes.py                    # Quiz Start & Submission Router
│   ├── quizzes_helpers.py            # Quiz Queue & Attempt Verification
│   └── video_durations.py            # YouTube Video Duration Utilities
│
├── llm_service/                      # Groq AI Quiz Generation Engine
│   ├── config.py                     # Groq Model & Batch Configuration
│   ├── generator.py                  # Async Quiz Pool Generator
│   ├── llm_caller.py                 # Groq Cloud API Caller (llama-3.1-8b-instant)
│   ├── llm_prompt.py                 # Structured Prompt & JSON Parsing
│   ├── questions.py                  # Question Validation & DB Persistence
│   ├── queue.py                      # Priority Generation Queue
│   ├── transcript.py                 # YouTube Transcript API Fetcher
│   └── worker.py                     # Background Worker Task Loop
│
├── tests/                            # Pytest Automated Test Suite
│   ├── test_api.py                   # Auth, Route & Authorization Tests
│   ├── test_db.py                    # Database Model & Query Tests
│   ├── test_environment.py           # Environment & Secret Validation Tests
│   └── test_llm.py                   # Groq AI Service & Quiz Logic Tests
│
├── .env                              # Local Environment Secrets (Git Ignored)
├── .env.example                      # Template Environment Configuration
├── main.py                           # FastAPI App Entry Point
├── pyproject.toml                    # Project Metadata & Ruff/Pytest Config
├── requirements.txt                  # Production Dependencies
└── requirements-dev.txt              # Development & Testing Dependencies
```

---

## 🤖 Groq Cloud AI Engine

The backend relies exclusively on **Groq Cloud AI** for high-speed, reliable JSON quiz generation from YouTube video transcripts.

### Environment Configuration

Add your Groq API credentials to `backend/.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### Features & Rate Limit Resilience
- **Model**: `llama-3.1-8b-instant` (near-instant response latency with strong JSON formatting enforcement).
- **Auto Retry**: Handles HTTP 429 rate limits gracefully with built-in backoff logic in `llm_service/llm_caller.py`.
- **Background Worker**: Asynchronously generates questions in batches so users can watch videos without delay.

---

## 🧪 Testing

Run all backend unit tests using pytest:

```bash
pytest
```
