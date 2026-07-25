# LMS Gamified Platform — Backend Documentation

Welcome to the backend of the Gamified Learning Management System (LMS). This service provides a RESTful API powered by **FastAPI**, handles async operations, orchestrates database interactions with **CockroachDB**, and leverages an LLM (either a local **Ollama** model or the free **Groq** cloud API) to dynamically generate quiz pools.

---

## 🛠️ Tech Stack & Architecture

- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **ORM & Validation**: [SQLModel](https://sqlmodel.tiangolo.com/) (Combines Pydantic & SQLAlchemy)
- **Database**: [CockroachDB](https://www.cockroachlabs.com/) (Distributed Postgres-compatible SQL database)
- **Authentication**: JWT (JSON Web Tokens) + [Argon2](https://argon2-cffi.readthedocs.io/en/stable/) password hashing
- **HTTP Client**: [httpx](https://www.python-httpx.org/) (used for calling the YouTube Data API & Groq API)
- **LLM Integration (switchable)**:
  - [Ollama](https://ollama.com/) — Local model (default, no internet needed)
  - [Groq](https://console.groq.com) — Free cloud API (no GPU required)
- **Transcript Extraction**: `youtube-transcript-api`

---

## 📂 File Structure

```
backend/
├── main.py            # API routes, app initialization, and background tasks config
├── models.py          # SQLModel declarations (database schemas and pydantic models)
├── llm_service.py     # YouTube transcript extraction & LLM quiz generation (Ollama/Groq)
├── requirements.txt   # Backend dependency list
├── .env.example       # Template for environment variables setup
└── .env               # Local configuration file (git-ignored)
```

---

## 🤖 LLM Provider Options

The quiz generation pipeline supports **two LLM backends**, switchable via a single env variable.

### Choosing a Provider

Set `LLM_PROVIDER` in your `.env` file:

| `LLM_PROVIDER` | When to use | Requirements |
|---|---|---|
| `ollama` *(default)* | You have a decent GPU / want fully offline | Ollama installed & model downloaded |
| `groq` | No GPU, or Ollama is slow/crashing | Free Groq API key from [console.groq.com](https://console.groq.com) |

---

### 🏠 Provider 1: Ollama (Local LLM)

Runs the LLM entirely on your own machine. Zero latency to an API, no cost, fully offline.

**Hardware requirements (optimised for RTX 3050 4 GB):**

| Model | VRAM | Speed | Quality | Pull command |
|---|---|---|---|---|
| `qwen2.5:3b` ✅ *recommended* | ~2.0 GB | Fast | Best | `ollama pull qwen2.5:3b` |
| `phi3:mini` | ~1.5 GB | Fastest | Good | `ollama pull phi3:mini` |
| `gemma2:2b` | ~1.8 GB | Fast | Good | `ollama pull gemma2:2b` |
| `llama3.1:8b` ❌ | 6+ GB | Very slow | — | Don't use on 4 GB VRAM |

**`.env` config:**
```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

**Common issues:**
- `ConnectError` → Ollama is not running. Run `ollama serve` in a separate terminal.
- Timeout → Model is too large for your VRAM. Switch to `phi3:mini` or use Groq instead.

---

### ☁️ Provider 2: Groq (Free Cloud API) — *Recommended for teammates without a GPU*

[Groq](https://groq.com) provides **blazing-fast free-tier access** to top open-source LLMs (Llama, Gemma) using their custom LPU inference chip. No credit card is needed.

**Free tier limits:** ~30 requests/min, ~6 000 requests/day — plenty for this app.

**Recommended Groq models:**

| Model | Speed | Quality | Best for |
|---|---|---|---|
| `llama-3.1-8b-instant` ✅ *default* | Near-instant | Great | Development & daily use |
| `llama-3.3-70b-versatile` | Fast | Best | Best quiz quality |
| `gemma2-9b-it` | Fast | Great | Alternative, accurate |
| `llama3-8b-8192` | Instant | Good | High-volume / testing |

**Setup (one-time):**
1. Sign up free at [console.groq.com](https://console.groq.com) — no credit card needed.
2. Go to **API Keys** → **Create API Key** → copy the key.
3. Add to `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

---

## 🗄️ Database Schema & Models (`models.py`)

The platform uses a relational database schema mapped via **SQLModel**.

### 1. `User`
Tracks user credentials, streaks, levels, and total experience points (XP).
- `id` (UUID, PK)
- `email` (String, Unique)
- `hashed_password` (String)
- `total_xp` (Integer, default `0`)
- `current_level` (Integer, default `1`)
- `current_streak` (Integer, default `0`)
- `last_activity_date` (Date, tracks streaks)

### 2. `Playlist`
Represents a course ingested from a YouTube playlist.
- `id` (String, PK - YouTube Playlist ID)
- `title` (String)
- `description` (String, Optional)
- `thumbnail_url` (String, Optional)
- `video_count` (Integer)

### 3. `Video`
Represents an individual video/lesson inside a playlist.
- `id` (String, PK - YouTube Video ID)
- `playlist_id` (String, FK -> Playlist.id)
- `title` (String)
- `description` (String, Optional)
- `thumbnail_url` (String, Optional)
- `sequence_number` (Integer, ensures ordered roadmap)

### 4. `UserProgress`
Tracks which videos have been completed by which users.
- `id` (UUID, PK)
- `user_id` (UUID, FK -> User.id)
- `video_id` (String, FK -> Video.id)
- `completed_at` (DateTime)

### 5. `XpLog`
A transactional audit log recording every XP addition.
- `id` (UUID, PK)
- `user_id` (UUID, FK -> User.id)
- `xp_amount` (Integer)
- `reason` (String, e.g., `"video_completion"`, `"quiz_completion"`)
- `created_at` (DateTime)

### 6. `Quiz`
Tracks the generation status of the quiz pool for a specific course/video.
- `id` (UUID, PK)
- `playlist_id` (String, FK -> Playlist.id)
- `status` (String, `"generating" | "ready" | "error_no_transcript" | "error_llm_failure"`)

### 7. `Question`
The specific questions generated by the LLM for a quiz pool.
- `id` (UUID, PK)
- `quiz_id` (UUID, FK -> Quiz.id)
- `question_text` (String)
- `options` (JSON, contains `choices` array)
- `correct_option_index` (Integer)
- `explanation` (String, explanation of the correct choice)

---

## 🧠 Smart Quiz Placement System (`routers/playlists.py`)

Quizzes are placed by **cumulative chapter duration**, not naively every N videos.
All quiz records are created in the DB immediately with `status="pending"` — generation
is then handed off to the **Priority Queue** (see below).

### Duration-based tier assignment

```
Chapter content < 10 min  → No quiz (merged into next chapter)
Chapter content 10–59 min → Light quiz   (8 Qs per attempt)
Chapter content 1–3 hrs   → Standard quiz (15 Qs per attempt)
Chapter content ≥ 3 hrs   → Deep quiz   (25 Qs per attempt)
Final Playlist quiz added if total playlist ≥ 15 min
```

---

## ⚡ Priority Queue — Intelligent Generation Scheduler (`llm_service.py`)

The core innovation: a single **asyncio `PriorityQueue`** driven by a long-lived background
worker (started in the FastAPI `lifespan`). Quizzes are generated one at a time, always
in the order that benefits the user most.

### Priority tiers

| Priority | Score | Triggered when |
|---|---|---|
| `URGENT` | 0 | User opens a quiz that's still `pending` → jumps to front |
| `FIRST` | 10 | First quiz of a new playlist / next quiz after user passes current one |
| `CHAIN` | 20 | Auto-cascade: after quiz N finishes, quiz N+1 is chained |
| `RECOVERY` | 30 | First pending quiz per playlist re-queued after server restart |

### Generation flow

```
User ingests playlist
  │
  ├─ All quizzes saved as status="pending" (with video_yt_ids stored)
  └─ Only Quiz 1 enqueued at PRIORITY_FIRST=10
          │
          ▼
    Worker picks Quiz 1 → generates → status="ready"
          │
          └─ _chain_to_next() → Quiz 2 enqueued at PRIORITY_CHAIN=20
                  │
            User passes Quiz 1
                  │
                  └─ submit_quiz() → Quiz 2 re-enqueued at PRIORITY_FIRST=10
                          │        (bumped ahead of other CHAIN-priority work)
                          ▼
                    Worker picks Quiz 2 → generates → chains to Quiz 3...

    User reaches Quiz 3 before generation reaches it
                  │
                  └─ start_quiz() detects "pending" → enqueues at PRIORITY_URGENT=0
                                                       (jumps to absolute front)
```

### Crash recovery

On every server startup, the lifespan calls `recover_pending_quizzes()`:
1. Quizzes stuck in `generating` → reset to `pending` (server crashed mid-generation)
2. For each playlist that has pending work, **only the first pending quiz** is re-enqueued
   at `PRIORITY_RECOVERY=30`. The rest will chain automatically — avoids flooding the queue.

### Pool sizing (dynamic)

| Quiz depth | Questions per attempt | Pool built | LLM batches |
|---|---|---|---|
| Light | 8 | 32 | 3 |
| Standard | 15 | 60 | 5 |
| Deep | 25 | 100 | 6 (cap) |

### Tunable via `.env`

All thresholds configurable without touching code — see `.env.example`:
`QUIZ_MIN_CHAPTER_SECONDS`, `QUIZ_LIGHT_THRESHOLD`, `QUIZ_STANDARD_THRESHOLD`,
`QUIZ_LIGHT_QUESTIONS`, `QUIZ_STANDARD_QUESTIONS`, `QUIZ_DEEP_QUESTIONS`, `QUIZ_FINAL_MIN_SECONDS`

---

## 🤖 LLM Quiz Generation Pipeline (`llm_service.py`)

A unique feature of this platform is the automatic generation of quizzes using an LLM:

1. **Trigger**: When a user accesses a playlist's quiz for the first time, a `Quiz` record is created with a `generating` status.
2. **Background Task**: FastAPI schedules `generate_quiz_pool_background` asynchronously.
3. **Transcript Fetching**: The `youtube-transcript-api` pulls the transcripts for all videos in the playlist.
4. **LLM Querying**: The backend sends the transcripts (truncated to fit context) along with a structured prompt to the **active LLM provider** — either local Ollama or the Groq cloud API.
5. **Batch Generation**: To build a robust pool, it requests 12 multiple-choice questions at a time in JSON format over 5 batches (up to 60 distinct questions).
6. **DB Commit**: Questions are validated, saved into the database, and the `Quiz.status` is updated to `ready`.

---

## ⚡ API Endpoint Reference (`main.py`)

### Authentication
* `POST /api/auth/register` — Registers a new user.
* `POST /api/auth/login` — Authenticates user, issues JWT access token.
* `GET /api/auth/me` — Fetches current user's profile, XP, streak, and level details.

### Ingestion
* `POST /api/ingest/playlist` — Ingests a YouTube playlist ID, fetches metadata from the YouTube Data API, parses and commits the playlist and its videos to the DB.

### Playlists / Courses
* `GET /api/playlists` — Lists all ingested playlists alongside their video counts and completion statistics for the logged-in user.
* `GET /api/playlists/{playlist_id}/videos` — Retrieves all videos associated with a specific playlist, including the user's completion status.
* `DELETE /api/playlists/{playlist_id}` — Deletes the course playlist and clears the user's progress.

### Progress & Gamification
* `POST /api/progress/complete-video/{video_id}` — Marks a video as completed, issues **100 XP** to the user, computes potential level-ups, logs the XP transaction, and increments the streak if relevant.

### Quizzes
* `GET /api/playlists/{playlist_id}/quiz` — Fetches the quiz status. If missing, automatically initializes background LLM generation.
* `GET /api/playlists/{playlist_id}/quiz/questions` — Fetches a randomized set of 5 questions from the quiz pool for the user to attempt.
* `POST /api/playlists/{playlist_id}/quiz/submit` — Scores the submitted answers, validates them, and awards **300 XP** if the user scores 80% or higher.

---

## ⚙️ Running Locally

1. Setup your `.env` following the [CONTRIBUTING.md](../CONTRIBUTING.md).
2. Start the local database (CockroachDB).
3. **Choose your LLM provider** and configure it in `.env`:
   - **Ollama** (local): Install [Ollama](https://ollama.com/download), then run:
     ```bash
     ollama pull qwen2.5:3b
     ollama serve
     ```
   - **Groq** (cloud, no GPU): Get a free key at [console.groq.com](https://console.groq.com), set `LLM_PROVIDER=groq` and `GROQ_API_KEY=...` in `.env`.
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the web server:
   ```bash
   uvicorn main:app --reload
   ```
