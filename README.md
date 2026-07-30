# 🎓 Gamified LMS with YouTube Ingestion

> Convert any public YouTube playlist into a structured, gamified learning course with XP, levels, streaks, and AI-generated quizzes.

---

## 📑 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Directory Structure](#-directory-structure)
3. [Prerequisites](#-prerequisites-exact-versions)
4. [Setup in Under 5 Minutes](#-setup-in-under-5-minutes)
5. [Environment Variables](#-environment-variables-reference)
6. [Run Scripts Cheat-Sheet](#-run-scripts-cheat-sheet)
7. [Verify Your Setup](#-verify-your-setup)
8. [Feature Developer Guide](#-feature-developer-guide-where-does-my-code-go)
9. [API Endpoint Reference](#-api-endpoint-reference)
10. [Improving AI Quiz Quality](#-improving-ai-quiz-quality)
11. [Troubleshooting Guide](#-troubleshooting-guide)
12. [Git Workflow](#-git-workflow)

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (User)                           │
│           React 19 + Vite + TypeScript + Tailwind CSS v4        │
│         Port: 5173 (dev)  │  Port: 4173 (preview)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP / REST (axios)
                      │ JWT Bearer token in Authorization header
┌─────────────────────▼───────────────────────────────────────────┐
│                    FastAPI Backend (Python)                      │
│             Uvicorn ASGI server — Port: 8000                    │
│   • Auth (JWT + Argon2)    • YouTube Data API v3 ingestion      │
│   • Progress tracking      • Groq AI quiz generation            │
└──────────┬──────────────────────────┬───────────────────────────┘
           │ SQLModel ORM             │ httpx async (HTTPS)
           │ (SQLAlchemy 2.x)        │
┌──────────▼──────────┐   ┌──────────▼────────────────────────────┐
│   CockroachDB        │   │   Groq Cloud AI API                  │
│   (Cloud Serverless) │   │   Model: llama-3.1-8b-instant        │
│   Port: 26257        │   │   HTTPS Endpoint                     │
└─────────────────────┘   └───────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
summer_intern_group-a/
│
├── backend/                              # FastAPI Backend (Python 3.12)
│   ├── core/                             # Core Infrastructure & Configuration
│   │   ├── deps.py                       # Auth, DB Session & JWT Dependencies
│   │   └── lifespan.py                   # App Lifespan & DB Initialization
│   │
│   ├── models/                           # Modular SQLModel Schemas (CockroachDB)
│   │   ├── playlist.py                   # Playlist & Video Schemas
│   │   ├── quiz.py                       # SharedQuiz, Quiz & Question Schemas
│   │   └── user.py                       # User & XpLog Schemas
│   │
│   ├── routers/                          # Modular API Endpoints & Handlers
│   │   ├── auth.py                       # Authentication (Register, Login, Token)
│   │   ├── users.py                      # User Profile & Stats Endpoint (/users/me)
│   │   ├── playlists.py                  # Playlist Router Dispatcher
│   │   ├── playlists_ingest.py           # YouTube Playlist Ingestion Pipeline
│   │   ├── playlists_get.py              # Playlist Retrieval & Listing
│   │   ├── playlists_delete.py           # Playlist Deletion
│   │   ├── playlists_yt_fetch.py         # YouTube Data API Integration
│   │   ├── playlists_videos.py           # Video Sequence & Progress Endpoint
│   │   ├── playlists_helpers.py          # Sequence & Chapter Helper Utilities
│   │   ├── progress.py                   # Anti-Cheat Video Progress Tracking
│   │   ├── progress_helpers.py           # Seek Prevention & XP Calculation
│   │   ├── quizzes.py                    # Quiz Start & Submission Router
│   │   ├── quizzes_helpers.py            # Quiz Queue & Attempt Verification
│   │   └── video_durations.py            # YouTube Video Duration Utilities
│   │
│   ├── llm_service/                      # Groq AI Quiz Generation Engine
│   │   ├── config.py                     # Groq Model & Batch Configuration
│   │   ├── generator.py                  # Async Quiz Pool Generator
│   │   ├── llm_caller.py                 # Groq Cloud API Caller (llama-3.1-8b-instant)
│   │   ├── llm_prompt.py                 # Structured Prompt & JSON Parsing
│   │   ├── questions.py                  # Question Validation & DB Persistence
│   │   ├── queue.py                      # Priority Generation Queue
│   │   ├── transcript.py                 # YouTube Transcript API Fetcher
│   │   └── worker.py                     # Background Worker Task Loop
│   │
│   ├── tests/                            # Pytest Automated Test Suite
│   │   ├── test_api.py                   # Auth, Route & Authorization Tests
│   │   ├── test_db.py                    # Database Model & Query Tests
│   │   ├── test_environment.py           # Environment & Secret Validation Tests
│   │   └── test_llm.py                   # Groq AI Service & Quiz Logic Tests
│   │
│   ├── .env                              # Local Environment Secrets (Git Ignored)
│   ├── .env.example                      # Template Environment Configuration
│   ├── main.py                           # FastAPI App Entry Point
│   ├── pyproject.toml                    # Project Metadata & Tool Config
│   ├── requirements.txt                  # Production Dependencies
│   └── requirements-dev.txt              # Development & Testing Dependencies
│
├── frontend/                             # React + Vite + TypeScript Frontend
│   ├── src/                              # Modular Source Code
│   │   ├── auth/                         # Authentication Feature Module
│   │   │   ├── auth.ts                   # Axios API Client Configuration
│   │   │   ├── AuthContext.tsx           # React Context for Auth State
│   │   │   ├── LoginForm.tsx             # Modular Login Form Component
│   │   │   ├── LoginPage.tsx             # Login Route Container Page
│   │   │   ├── RegisterForm.tsx          # Modular Registration Form Component
│   │   │   └── RegisterPage.tsx          # Register Route Container Page
│   │   │
│   │   ├── dashboard/                    # Main Learning Dashboard
│   │   │   ├── CourseCard.tsx            # Modular Course Card Component
│   │   │   ├── DashboardPage.tsx         # Main Dashboard Layout Page
│   │   │   ├── ImportModal.tsx           # YouTube Playlist Import Modal
│   │   │   ├── RemoveCourseModal.tsx     # Course Removal Confirmation Modal
│   │   │   ├── StatsBar.tsx              # Gamified Level/XP & Streak Bar
│   │   │   └── useDashboardData.ts       # Custom Hook for Dashboard State
│   │   │
│   │   ├── course-player/                # Interactive Video & Quiz Player
│   │   │   ├── AttentionOverlay.tsx      # Distraction Pause Alert Overlay
│   │   │   ├── CameraPip.tsx             # Picture-in-Picture Webcam Feedback
│   │   │   ├── CoursePlayerPage.tsx      # Main Player Page Layout
│   │   │   ├── PlayerControls.tsx        # Video Control Bar
│   │   │   ├── PlayerSidebar.tsx         # Chapter Playlist & Quiz Sidebar
│   │   │   ├── WebcamPermissionGate.tsx  # MediaPipe Proctoring Permission Gate
│   │   │   ├── useCoursePlayer.ts        # Custom Hook for Course Player Logic
│   │   │   │
│   │   │   ├── proctoring/               # AI Webcam Proctoring Subsystem
│   │   │   │   ├── headPose.ts           # Head Pose (Yaw/Pitch) Calculator
│   │   │   │   ├── initFaceLandmarker.ts # MediaPipe Task Initialization
│   │   │   │   └── useProctoring.ts      # Gaze Tracking & Distraction Hook
│   │   │   │
│   │   │   ├── quiz/                     # Quiz Subsystem Components
│   │   │   │   ├── QuizQuestion.tsx      # Question & Multiple Choice UI
│   │   │   │   ├── QuizResult.tsx        # Score Summary & XP Result View
│   │   │   │   └── QuizView.tsx          # Quiz State & Submission Container
│   │   │   │
│   │   │   └── ytPlayer/                 # YouTube Player Integration
│   │   │       ├── loadYouTubeAPI.ts     # Asynchronous IFrame API Loader
│   │   │       ├── types.ts              # TypeScript Interfaces for Player API
│   │   │       └── useYouTubePlayer.ts   # Player Controls & Event Hook
│   │   │
│   │   ├── landing/                      # Landing Page Feature Module
│   │   │   ├── FeaturesSection.tsx       # Features Grid Component
│   │   │   ├── HeroSection.tsx           # Hero CTA Component
│   │   │   ├── HowItWorksSection.tsx     # 3-Step Process Component
│   │   │   └── LandingPage.tsx           # Public Home Page Container
│   │   │
│   │   ├── styles/                       # Modular CSS System
│   │   │   ├── animations.css            # Custom Animations & Keyframes
│   │   │   ├── base.css                  # Base Styles & CSS Variables
│   │   │   ├── components.css            # Component Layout & Glassmorphism Rules
│   │   │   └── utilities.css             # Helper Utility Classes
│   │   │
│   │   ├── theme/                        # Dynamic Design & Particle Theme
│   │   │   ├── AnimatedBackground.tsx    # Interactive Canvas Background
│   │   │   ├── ThemeToggle.tsx           # Dark / Light Mode Switch
│   │   │   ├── useTheme.ts               # Theme State Hook
│   │   │   └── animatedBg/               # Particle Animation Engine
│   │   │       ├── constants.ts          # Particle Dynamics Configuration
│   │   │       └── useParticles.ts       # Canvas Particle Movement Hook
│   │   │
│   │   ├── ui/                           # Base UI Primitives (shadcn)
│   │   │   ├── avatar.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── progress.tsx
│   │   │   └── separator.tsx
│   │   │
│   │   ├── lib/                          # Utility Utilities
│   │   │   └── utils.ts                  # Tailwind class merge helper (cn)
│   │   │
│   │   ├── App.tsx                       # React Router App Component
│   │   ├── main.tsx                      # Vite React DOM Entry Point
│   │   └── index.css                     # Primary Tailwind + Modular CSS Import
│   │
│   ├── eslint.config.js                  # ESLint Code Quality Rules
│   ├── index.html                        # Single Page App HTML Template
│   ├── package.json                      # Frontend Dependencies & Scripts
│   ├── postcss.config.js                 # PostCSS Configuration
│   ├── tailwind.config.js                # Tailwind CSS v4 Configuration
│   ├── tsconfig.json                     # Main TypeScript Configuration
│   ├── tsconfig.app.json                 # Application TypeScript Rules
│   └── vite.config.ts                    # Vite Bundler & Path Alias Config
│
├── .gitignore                            # Version Control Exclusions
├── CONTRIBUTING.md                       # Developer Contribution Guidelines
├── DEPLOYMENT.md                         # Production Deployment Instructions
├── LICENSE                               # Open Source License
├── Makefile                              # Automation Command Shortcuts
├── Procfile                              # Heroku / PaaS Process Definitions
├── README.md                             # Master Project Documentation
└── project_report.md                     # Comprehensive Project Report
```

---

## ✅ Prerequisites (Exact Versions)

Install these tools **before cloning**. Click the links to download.

| Tool | Required Version | Check Command | Download |
|---|---|---|---|
| **Python** | 3.11.x or 3.12.x | `python --version` | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20.x LTS or 22.x LTS | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | 10.x+ | `npm --version` | Bundled with Node.js |
| **Git** | Any recent | `git --version` | [git-scm.com](https://git-scm.com/) |
| **Ollama** | Latest | `ollama --version` | [ollama.com/download](https://ollama.com/download) |

> **Windows Users:** Use **PowerShell 7+** (not Command Prompt). Python must be on PATH.  
> Check with: `where python` — it should show a path, not nothing.

---

## 🚀 Setup in Under 5 Minutes

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR-ORG/summer_intern_group-a.git
cd summer_intern_group-a
```

---

### Step 2 — Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a Python virtual environment (use python3.11 or python3.12)
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Mac / Linux:
source venv/bin/activate

# Upgrade pip first (important!)
python -m pip install --upgrade pip

# Install all pinned production dependencies
pip install -r requirements.txt

# Install dev/test dependencies (optional but recommended)
pip install -r requirements-dev.txt

# Copy the environment template
# Windows (PowerShell):
Copy-Item .env.example .env
# Mac / Linux:
cp .env.example .env
```

Now **open `backend/.env`** in any text editor and fill in the three required values:

```ini
DATABASE_URL=cockroachdb://<username>:<password>@<host>:26257/defaultdb?sslmode=verify-full&sslrootcert=system
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
YOUTUBE_API_KEY=<your YouTube Data API v3 key>
```

---

### Step 3 — Frontend Setup

```bash
# From the project root, navigate to frontend
cd ../frontend

# Install all pinned dependencies
npm install

# (Optional) Verify the environment is healthy
npm run verify
```

---

### Step 4 — Install & Start Ollama (for AI Quizzes)

```bash
# 1. Download & install Ollama from https://ollama.com/download

# 2. Pull the phi3 model (~2.4 GB, runs on 8 GB RAM)
ollama pull phi3

# 3. Ollama starts automatically as a background service after install.
#    To manually start it:
ollama serve

# Verify it's running:
curl http://localhost:11434/api/tags
# Should return JSON with your available models
```

---

### Step 5 — Start Both Servers

Open **two terminal windows** (both with `venv` activated for the backend terminal):

**Terminal 1 — Backend:**
```bash
cd backend
# Ensure venv is active: (venv) should appear in your prompt
uvicorn main:app --reload --port 8000
```
Expected output:
```
INFO:     Started server process [...]
INFO:     Waiting for application startup.
Starting up: Creating database tables in CockroachDB
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
Expected output:
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**You're live!** Visit [http://localhost:5173](http://localhost:5173) 🎉

---

## 🔐 Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description | Example |
|---|---|---|---|
| `DATABASE_URL` | ✅ Yes | CockroachDB connection string | `cockroachdb://user:pass@host:26257/defaultdb?sslmode=verify-full&sslrootcert=system` |
| `SECRET_KEY` | ✅ Yes | JWT signing key (min 32 chars, random hex) | `a3f8c...` |
| `YOUTUBE_API_KEY` | ✅ Yes | YouTube Data API v3 key | `AIzaSy...` |
| `OLLAMA_URL` | ⬜ No | Ollama server URL (default: localhost) | `http://localhost:11434/api/generate` |
| `OLLAMA_MODEL` | ⬜ No | Ollama model for quiz generation | `phi3` |
| `FRONTEND_URL` | ⬜ No | Frontend URL for CORS (default: localhost:5173) | `http://localhost:5173` |

> **How to get a YouTube API Key:**
> 1. Go to [console.cloud.google.com](https://console.cloud.google.com)
> 2. Create a new project (or select existing)
> 3. APIs & Services → Library → Search "YouTube Data API v3" → Enable
> 4. APIs & Services → Credentials → Create Credentials → API Key
> 5. (Recommended) Restrict the key to "YouTube Data API v3"

> **How to get a CockroachDB connection string:**
> 1. Log in at [cockroachlabs.cloud](https://cockroachlabs.cloud)
> 2. Select your cluster → Connect → Connection string
> 3. Copy the `cockroachdb://` connection string
> 4. **Windows only:** Append `&sslrootcert=system` at the end

---

## 📋 Run Scripts Cheat-Sheet

### Backend

```bash
cd backend
source venv/bin/activate  # (or .\venv\Scripts\Activate.ps1 on Windows)

# Start dev server (auto-reload on save)
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run tests with coverage report
pytest tests/ -v --tb=short

# Lint code
ruff check .

# Format code
ruff format .

# Type check
mypy main.py models.py llm_service.py
```

### Frontend

```bash
cd frontend

# Start dev server
npm run dev

# Type-check without building
npm run typecheck

# Lint (zero warnings enforced)
npm run lint

# Verify entire environment
npm run verify

# Production build
npm run build

# Preview production build locally
npm run preview
```

---

## ✅ Verify Your Setup

Run these commands to confirm everything works before writing any code.

### Backend Verification

```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Run the full test suite
pytest tests/ -v --tb=short
```

You should see output like:
```
tests/test_environment.py::TestEnvironmentVariables::test_all_required_env_vars_present PASSED
tests/test_environment.py::TestEnvironmentVariables::test_database_url_format PASSED
tests/test_environment.py::TestEnvironmentVariables::test_secret_key_length PASSED
tests/test_environment.py::TestDatabaseConnectivity::test_database_connection PASSED
tests/test_environment.py::TestFastAPIApplication::test_root_endpoint_returns_200 PASSED
tests/test_environment.py::TestFastAPIApplication::test_protected_endpoints_require_auth PASSED
tests/test_environment.py::TestAuthFlow::test_full_register_login_cycle PASSED
tests/test_environment.py::TestQuizGeneration::test_generate_questions_returns_list_on_valid_response PASSED
tests/test_environment.py::TestQuizBusinessLogic::test_quiz_pass_threshold_is_70_percent PASSED
...
======= X passed in X.Xs =======
```

### Frontend Verification

```bash
cd frontend
npm run verify
```

You should see:
```
╔══════════════════════════════════════════════════╗
║   LMS Frontend — Environment Verification        ║
╚══════════════════════════════════════════════════╝

── Node.js Version ──────────────────────────────────
  ✔ Node.js v20.x.x  (compatible)
  ✔ npm v10.x.x  (compatible)

── Dependencies ────────────────────────────────────
  ✔ node_modules exists
  ...

── Backend API Connectivity ─────────────────────────
  ✔ Backend reachable at http://localhost:8000

✔ All checks passed! You're ready to develop.
```

### Manual API Test

```bash
# Test the root endpoint
curl http://localhost:8000/
# Expected: {"message":"Hello World! The api is running."}

# Test the OpenAPI docs (visit in browser)
# http://localhost:8000/docs
```

---

## 🛠 Feature Developer Guide: Where Does My Code Go?

### "I'm working on the Dashboard"
→ Edit `frontend/src/dashboard/DashboardPage.tsx`  
→ API calls go in `DashboardPage.tsx` using the `API` instance from `@/auth/auth`  
→ Backend routes: add to `backend/main.py` under a `# ─── Dashboard ───` comment

### "I'm adding a new UI component"
→ Add it to `frontend/src/ui/` if it's generic and reusable  
→ Add it directly inside the feature folder if it's feature-specific

### "I'm working on the Quiz feature"
→ Frontend: `frontend/src/course-player/QuizView.tsx`  
→ Backend routes: `backend/main.py` — search for `@app.get("/api/quizzes/`  
→ LLM generation: `backend/llm_service.py`  
→ DB models: `backend/models.py` — `Quiz`, `Question`, `QuizAttempt` classes

### "I'm adding a new database field"
1. Edit `backend/models.py` — add the field to the appropriate model class
2. The tables will be auto-updated on next backend start (SQLModel creates tables)
3. **Note:** SQLModel does NOT run migrations. For schema changes on an existing DB, you may need to DROP and recreate, or use Alembic manually

### "I'm adding a new API endpoint"
1. Add the route function to `backend/main.py`
2. Use `Depends(get_current_user)` to require authentication
3. Use `Depends(get_session)` for DB access
4. Test it via `http://localhost:8000/docs` (FastAPI auto-generates Swagger UI)

### "I'm adding a new frontend page/route"
1. Create your page component in the appropriate feature folder (e.g., `src/my-feature/MyPage.tsx`)
2. Register the route in `frontend/src/App.tsx`
3. Add a nav link if appropriate

### "I need a shared TypeScript type"
→ Add it to `frontend/src/types/` if it's global  
→ Or define it inline / in the feature file if it's only used locally

---

## 🌐 API Endpoint Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | ❌ | Health check |
| `POST` | `/api/auth/register` | ❌ | Register a new user |
| `POST` | `/api/auth/login` | ❌ | Login (returns JWT) |
| `GET` | `/api/users/me` | ✅ | Get current user profile |
| `POST` | `/api/ingest/playlist` | ✅ | Import a YouTube playlist |
| `GET` | `/api/playlists` | ✅ | List all user's playlists |
| `DELETE` | `/api/playlists/{id}` | ✅ | Delete a playlist |
| `GET` | `/api/playlists/{id}/videos` | ✅ | Get videos + quizzes for a playlist |
| `POST` | `/api/progress/update` | ✅ | Update video watch progress |
| `GET` | `/api/quizzes/{id}/start` | ✅ | Start a quiz attempt |
| `POST` | `/api/quizzes/{id}/submit` | ✅ | Submit quiz answers |

> **Interactive Docs:** Visit `http://localhost:8000/docs` while the backend is running.

---

## 🤖 Improving AI Quiz Quality

The quiz generation system (`backend/llm_service.py`) uses Ollama to generate questions from YouTube transcripts. Here's how to improve quality:

### Model Selection

| Model | RAM Required | Quality | Speed | Pull Command |
|---|---|---|---|---|
| `phi3` | 8 GB | Good | Fast | `ollama pull phi3` |
| `llama3.2` | 8 GB | Better | Medium | `ollama pull llama3.2` |
| `mistral` | 8 GB | Better | Medium | `ollama pull mistral` |
| `gemma2:9b` | 16 GB | Best | Slow | `ollama pull gemma2:9b` |
| `llama3.1:70b` | 48 GB | Excellent | Very Slow | `ollama pull llama3.1:70b` |

Change the model in `backend/.env`:
```ini
OLLAMA_MODEL=llama3.2
```

### Prompt Engineering Tips

The prompt is in `backend/llm_service.py` → `generate_questions_with_ollama()`.

Key improvements already in place:
- ✅ Structured JSON output format enforced
- ✅ Multiple fallback field names parsed (`question_text`, `question`, `text`)
- ✅ Out-of-bounds index clamping
- ✅ 4 batches of 15 questions = 60-question pool, 30 selected randomly per attempt

To further improve:
```python
# In llm_service.py, edit the prompt to add:
# 1. Difficulty distribution
prompt = f"""
...
Generate {num_questions} questions at VARIED difficulty:
- 30% easy (recall/definition)
- 50% medium (application/concept)
- 20% hard (analysis/synthesis)
...
"""

# 2. Topic coverage (avoid duplicate questions)
# 3. Distractors that are plausible but clearly wrong
```

### Transcript Quality

Quiz quality depends on transcript quality. Videos with auto-generated captions may have errors. The system already handles `[Unavailable]` transcripts gracefully.

---

## 🔧 Troubleshooting Guide

### ❌ `ModuleNotFoundError: No module named 'fastapi'`
**Cause:** Virtual environment is not activated.  
**Fix:**
```bash
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Mac / Linux:
source venv/bin/activate

# Verify venv is active (you should see "(venv)" in your prompt)
# Then re-install:
pip install -r requirements.txt
```

---

### ❌ `sqlalchemy.exc.OperationalError: could not connect to server`
**Cause:** `DATABASE_URL` is wrong, or your IP is blocked in CockroachDB.  
**Fix:**
1. Open `backend/.env` — verify `DATABASE_URL` starts with `cockroachdb://` (not `postgresql://`)
2. On **Windows**, ensure the URL ends with `&sslrootcert=system`
3. Go to CockroachDB Cloud → **Networking** → **IP Allowlist** → Add your current IP address
4. Test connection: `python -c "from sqlmodel import create_engine, text, Session; import os; from dotenv import load_dotenv; load_dotenv(); e=create_engine(os.getenv('DATABASE_URL')); print(Session(e).exec(text('SELECT 1')).first())"`

---

### ❌ `422 Unprocessable Entity` on login
**Cause:** The login endpoint uses form data, not JSON. The frontend must send `Content-Type: application/x-www-form-urlencoded`.  
**Fix (frontend):** Use `new URLSearchParams(...)` or `application/x-www-form-urlencoded` content type — already correct in `auth/LoginPage.tsx`.

---

### ❌ `CORS error` in browser console
**Cause:** `FRONTEND_URL` in `backend/.env` doesn't match the actual frontend URL.  
**Fix:**
```ini
# backend/.env
FRONTEND_URL=http://localhost:5173
```
Also check `main.py` — the `allow_origins` list must include your frontend origin exactly.

---

### ❌ `Quiz status is "generating"` and never becomes "ready"
**Cause:** Ollama is not running, or the model isn't pulled.  
**Fix:**
```bash
# Check if Ollama is running:
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# Check if the model is downloaded:
ollama list

# Pull the model if missing:
ollama pull phi3
```

---

### ❌ `Error: [ERR_MODULE_NOT_FOUND]` in frontend
**Cause:** `node_modules` is missing or corrupted.  
**Fix:**
```bash
cd frontend

# Delete node_modules and reinstall
# Windows:
Remove-Item -Recurse -Force node_modules
# Mac / Linux:
rm -rf node_modules

npm install
```

---

### ❌ `TypeError: Cannot read properties of undefined (reading 'token')`
**Cause:** A component is trying to use `useAuth()` outside of `<AuthProvider>`.  
**Fix:** Check `frontend/src/main.tsx` — `<AuthProvider>` must wrap `<App>` and `<BrowserRouter>`.

---

### ❌ `PowerShell: running scripts is disabled`
**Cause:** PowerShell execution policy blocks scripts.  
**Fix:** Run PowerShell as Administrator, then:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ `YouTube playlist not found` on ingest
**Cause:** The playlist is private, or `YOUTUBE_API_KEY` is incorrect/quota-exceeded.  
**Fix:**
1. Verify the playlist is **public** on YouTube
2. Check your API key in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. Check quota: APIs & Services → YouTube Data API v3 → Quotas (default: 10,000 units/day)
4. Test your key: `curl "https://www.googleapis.com/youtube/v3/playlists?part=snippet&id=PLtest&key=YOUR_KEY"`

---

### ❌ `pytest: command not found`
**Cause:** Dev dependencies not installed, or venv not active.  
**Fix:**
```bash
source venv/bin/activate   # (or .\venv\Scripts\Activate.ps1)
pip install -r requirements-dev.txt
pytest --version  # Should show pytest 8.3.x
```

---

### ❌ TypeScript errors after `npm install`
**Cause:** Version mismatch between dependencies.  
**Fix:**
```bash
cd frontend
npm run typecheck  # See exact errors
# If widespread errors, try:
npm ci  # Clean install from package-lock.json
```

---

## 🔀 Git Workflow

### Branch Naming Convention
```
feature/your-name/short-description
fix/your-name/what-youre-fixing
```
Example: `feature/nirno/quiz-timer` or `fix/alex/cors-headers`

### Before Every Commit
```bash
# Backend:
cd backend
ruff check .   # Must have zero errors
pytest tests/ -v --tb=short  # Must all pass

# Frontend:
cd frontend
npm run typecheck  # Must have zero errors
npm run lint       # Must have zero warnings
```

### Creating a Pull Request
1. Push your feature branch
2. Open a PR against `main`
3. Include: what you changed, screenshots (for UI), and test results
4. At least 1 review required before merging

---

*Last updated: July 2026 | Python 3.11+ | Node.js 20 LTS | FastAPI 0.115 | React 19 | Vite 6*
