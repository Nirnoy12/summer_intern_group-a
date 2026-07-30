# TrackTube: An Open-Source YouTube-based LMS Framework for Structured Learning, Roadmap Generation and Progress Tracking

**A Project Report submitted for the successful completion of the internship as Data Science Intern**  
*[Period of Internship: 18th May 2026 – 31st July 2026]*  
**Summer Internship 2026 Program**  
**IDEAS - Institute of Data Engineering, Analytics and Science Foundation, Technology Innovation Hub, Indian Statistical Institute, Kolkata, West Bengal, India**

---

### Submitted by:
1. **Nirnoy Chatterjee** (Registration No: 231160110175) — B.Tech in Computer Science Engineering (AIML), MCKV Institute of Engineering ([nirnoychatterjee2004@gmail.com](mailto:nirnoychatterjee2004@gmail.com))
2. **Shreyan Ghosh** (Registration No: 2024ITB063) — B.Tech in Information Technology, Indian Institute of Engineering Science and Technology (IIEST), Shibpur ([shreyan.ghosh0710@gmail.com](mailto:shreyan.ghosh0710@gmail.com))
3. **Prince Kumar Singh** (Registration No: A91005223013) — B.Tech in Computer Science Engineering, Amity University Kolkata ([princekrsingh780@gmail.com](mailto:princekrsingh780@gmail.com))

### Supervisor:
**Mr. Samyabrata Roy**  
Associate Software Developer, Institute of Data Engineering, Analytics and Science Foundation (IDEAS-TIH), Indian Statistical Institute, Kolkata ([sroy@ideas-tih.org](mailto:sroy@ideas-tih.org))

**GitHub repository:** [https://github.com/samyatih/summer_intern_group-a](https://github.com/samyatih/summer_intern_group-a)

---

## Declaration by the Students

We, Nirnoy Chatterjee, Shreyan Ghosh, and Prince Kumar Singh, hereby declare that the project entitled “TrackTube: An Open-Source YouTube-based LMS Framework for Structured Learning, Roadmap Generation and Progress Tracking”, submitted in fulfilment of the requirements for the completion of the internship at the Institute of Data Engineering, Analytics and Science Foundation (IDEAS), Technology Innovation Hub, Indian Statistical Institute, Kolkata, is an original work carried out by us during the period from 18th May 2026 to 31st July 2026.

We affirm that this report is the result of our own efforts and contributions. Any references to existing software, direct quotations, or paraphrased content have been duly acknowledged.

Date: 31st July, 2026  
Place: Kolkata

---

## Acknowledgement

We would like to express our profound and sincere gratitude to everyone whose contributions, encouragement, and expertise facilitated the successful completion of this project. First and foremost, we extend our deepest appreciation to our mentor, **Mr. Samyabrata Roy**, Associate Software Developer at IDEAS-TIH, for his invaluable guidance, continuous support and expert mentorship throughout the entire lifecycle of this project.

We also extend our heartfelt thanks to the **Institute of Data Engineering, Analytics and Science Foundation (IDEAS-TIH)** at the **Indian Statistical Institute, Kolkata**, for providing us with the exceptional opportunity to contribute to the *TrackTube* initiative.

We would also like to express our sincere gratitude to the **Vicharanashala Lab for Education Design (VLED)** at **Indian Institute of Technology Ropar**, especially **Prof. Sudarshan Iyengar** and **Mrs. Meenakshi V.**, for their pioneering work in education design. Their flagship educational platform, **ViBe#** ([https://vibe.vicharanashala.ai/](https://vibe.vicharanashala.ai/)), served as a significant source of inspiration during the conceptualisation and design of this project.

---

## Abstract

Traditional Learning Management Systems often struggle with low engagement and completion rates. Conversely, platforms such as YouTube host a vast repository of structured educational content in public playlists. This project bridges this gap by developing **TrackTube**, an open-source framework that transforms any standard public YouTube playlist into a structured, progress-tracked, and gamified learning course.

The system allows users to import any playlist by submitting its URL. The backend architecture fetches video metadata through the YouTube Data API v3, constructs a sequential course structure, and securely stores data within CockroachDB. Learners watch embedded videos using the YouTube IFrame Player API while progress is tracked to the exact second to strictly enforce sequential lesson unlocking.

To sustain engagement, learners are rewarded with Experience Points (XP), level progressions, and daily login streaks. To verify comprehension, **Groq Cloud AI (`llama-3.1-8b-instant`)** automatically generates a pool of multiple-choice questions directly from video transcripts. An optional webcam proctoring layer powered by Google's MediaPipe Face Landmarker pauses playback if the learner looks away from the screen for more than three consecutive seconds.

**Keywords:** Learning Management System, YouTube Ingestion, Gamification, Groq Cloud AI, Progress Tracking, MediaPipe Proctoring, FastAPI, React 19, CockroachDB.

---

## Table of Contents

- [Chapter 1 — Introduction](#chapter-1--introduction)
- [Chapter 2 — Tech Stack & Architecture](#chapter-2--tech-stack--architecture)
- [Chapter 3 — System Design](#chapter-3--system-design)
- [Chapter 4 — Testing & Security Analysis](#chapter-4--testing--security-analysis)
- [Chapter 5 — Deployment and User Guide](#chapter-5--deployment-and-user-guide)
- [Chapter 6 — Results and Evaluation](#chapter-6--results-and-evaluation)
- [Chapter 7 — Limitations and Future Scope](#chapter-7--limitations-and-future-scope)
- [Chapter 8 — Conclusion](#chapter-8--conclusion)
- [Chapter 9 — References](#chapter-9--references)
- [Appendix A — Userflow Screenshots](#appendix-a--userflow-screenshots)
- [Appendix B — File Structure](#appendix-b--file-structure)

---

# Chapter 1 — Introduction

## 1.1 Background
The growth of video-based online learning has democratised access to high-quality educational content. Platforms such as YouTube host complete course curricula published by universities and independent educators at no cost to the learner. However, consuming these playlists informally presents structural limitations:
- There is no mechanism to record which videos have been completed or to enforce a progression order.
- Returning to a playlist requires manually recalling the last watched video and the precise playback position.
- Without a structured accountability layer or gamified reward system, self-directed learners exhibit high dropout rates.

## 1.2 Problem Statement
Learners relying on YouTube playlists as their primary educational resource face significant tracking and motivation hurdles:
- **No progress tracking:** Learners cannot distinguish completed videos from remaining ones.
- **No structured progression:** Users can skip ahead without mastering prerequisite material.
- **No comprehension verification:** There is no mechanism to confirm the learner has actually understood the video content.
- **No engagement incentive:** The absence of a reward system fails to motivate daily learning behaviour.

## 1.3 Project Objective
The primary objective was to develop a gamified web application that converts any public YouTube playlist into a structured, trackable, and accountable learning course:
- Implement secure user authentication to persist individual learning progress.
- Preserve original playlist sequence and enforce sequential lesson unlocking.
- Track playback accurately to the second, allowing seamless resumption across sessions.
- Award Experience Points (XP) and track daily streaks to sustain long-term engagement.
- Integrate **Groq Cloud AI** to dynamically generate comprehension quizzes from video transcripts.
- Implement MediaPipe-based webcam proctoring to monitor focus during video playback.

---

# Chapter 2 — Tech Stack & Architecture

## 2.1 Frontend Frameworks and UI
- **React 19 & Vite 6:** Modern, concurrent UI layer with fast Hot Module Replacement (HMR).
- **TypeScript:** Strict type safety across components and hooks.
- **Tailwind CSS v4 & Modular CSS System:** Utility-first styling combined with modular vanilla CSS design tokens (`src/styles/`).
- **Framer Motion:** Declarative animations and glassmorphic UI elements.
- **MediaPipe Tasks Vision:** Browser-based 468-point facial landmark processing for attention proctoring.

## 2.2 Backend and APIs
- **FastAPI (Python 3.12):** Asynchronous REST API framework with native Pydantic validation.
- **Uvicorn:** High-performance production-grade ASGI server.
- **Authentication:** `python-jose` for JWT management and `passlib` with `argon2-cffi` for Argon2id password hashing.
- **Groq Cloud AI API:** Blazing-fast cloud LPU inference using `llama-3.1-8b-instant` via `httpx` for automated quiz generation.
- **YouTube Transcript API:** Automatic retrieval of video captions for AI prompt construction.

## 2.3 Database and Persistence
- **CockroachDB Serverless:** Distributed, highly available Postgres-compatible SQL database.
- **SQLModel:** Unifies SQLAlchemy 2.x ORM schemas with Pydantic validation models.

---

# Chapter 3 — System Design

## 3.1 High-Level Architecture

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

## 3.2 Database Design and ER Diagram

```
users (1)
  |-- (N) playlists
                |-- (N) videos
                |          |-- (N) user_progress [user_id FK, video_id FK]
                |-- (N) quizzes
                               |-- (N) questions
                               |-- (N) quiz_attempts [user_id FK, quiz_id FK]
users (1) -- (N) xp_log
```

---

# Chapter 4 — Testing & Security Analysis

## 4.1 Testing Strategy
- **Automated Backend Tests (`pytest`):** 29 comprehensive test cases covering authentication, database models, progress tolerance, and Groq LLM API response parsing.
- **Frontend Type & Build Checking (`npm run build`):** Clean TypeScript compilation across 2390 modules with 0 errors.

## 4.2 Security Measures
- **Argon2id Hashing:** Industry-standard password hashing.
- **Strict Origin Control:** CORS origin locking.
- **Server-Side Scoring:** Quiz answers and evaluation logic are kept strictly on the backend.

---

# Chapter 5 — Deployment and User Guide

## 5.1 Deployment Configuration
Backend `.env` configuration for Groq AI integration:

```env
DATABASE_URL=cockroachdb://<username>:<password>@<cluster-host>:26257/defaultdb?sslmode=verify-full&sslrootcert=system
SECRET_KEY=replace_with_64_char_random_hex_string_never_commit_this
YOUTUBE_API_KEY=replace_with_your_youtube_api_key
LLM_PROVIDER=groq
GROQ_API_KEY=replace_with_your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
FRONTEND_URL=http://localhost:5173
```

---

# Chapter 6 — Results and Evaluation

## 6.1 System Achievements
- **Rapid Playlist Ingestion:** Full 15-video YouTube playlist ingested and structured in under 4 seconds.
- **Accurate Playback Resumption:** Playback state saved to the exact second every 5 seconds.
- **Near-Instant AI Quiz Generation:** Groq Cloud AI generates valid multiple-choice quiz pools in under 2 seconds per batch.

---

# Chapter 7 — Limitations and Future Scope

## 7.1 System Limitations
- **API Quotas:** Subject to YouTube Data API v3 daily quota limits.
- **Caption Availability:** Quizzes depend on the presence of auto-generated or manual video captions.

## 7.2 Future Scope
- **AI Chapter Summarization:** Structured text summaries below the course player.
- **Cohort Leaderboards & Peer Discussion:** Collaborative community learning features.
- **Native Mobile Application:** Cross-platform mobile client with offline caching.

---

# Chapter 8 — Conclusion

TrackTube successfully bridges the gap between raw YouTube educational playlists and formal Learning Management Systems. By combining FastAPI, React 19, CockroachDB, Groq Cloud AI, and MediaPipe proctoring, the framework converts passive video viewing into an active, structured, and gamified educational journey.

---

# Chapter 9 — References

1. Google LLC. 2026. *YouTube Data API v3 Reference*. https://developers.google.com/youtube/v3/docs
2. Google LLC. 2026. *YouTube IFrame Player API Reference*. https://developers.google.com/youtube/iframe_api_reference
3. Sebastián Ramírez. 2026. *FastAPI Documentation*. https://fastapi.tiangolo.com/
4. Sebastián Ramírez. 2026. *SQLModel Documentation*. https://sqlmodel.tiangolo.com/
5. Meta Open Source. 2026. *React Documentation*. https://react.dev/
6. Evan You et al. 2026. *Vite Documentation*. https://vitejs.dev/guide/
7. Tailwind Labs. 2026. *Tailwind CSS v4 Documentation*. https://tailwindcss.com/docs
8. CockroachDB Inc. 2026. *CockroachDB Documentation*. https://www.cockroachlabs.com/docs/
9. Groq Technologies Inc. 2026. *Groq Cloud LPU API Documentation*. https://console.groq.com/docs
10. Google LLC. 2026. *MediaPipe Tasks Vision — Face Landmarker*. https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker

---

# Appendix A — Userflow Screenshots

*(Refer to platform live interface for Dashboard, Course Player, Attention Proctoring Overlay, and AI Quiz Views)*

---

# Appendix B — File Structure

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
