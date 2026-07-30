# YouTube Playlist–Based Gamified Learning Management System

**Group A — Summer Internship Project**

---

# Preliminary Pages

## Title Page

**Project Title:** YouTube Playlist–Based Gamified Learning Management System
**Team / Group:** Group A — Summer Intern Cohort
**Team Members:** Nirnoy Nath
**Programme:** Software Engineering Internship
**Submission Date:** July 2026

---

## Declaration

We hereby declare that the work presented in this report is original and was carried out by the members of Group A during the summer internship programme. All external sources and tools that contributed to this project have been properly cited.

Key third-party tools and services utilized include:
- **FastAPI & SQLModel:** For robust backend routing and database ORM management.
- **CockroachDB:** As a highly available, distributed SQL database.
- **React 19 & Tailwind CSS v4:** For building a responsive, glassmorphic user interface.
- **YouTube APIs:** Data API v3 and IFrame Player API for content ingestion and playback.
- **Groq Cloud AI & MediaPipe:** For high-speed cloud AI quiz generation (`llama-3.1-8b-instant`) and webcam-based attention proctoring.
- **Vite & React Ecosystem:** Providing rapid development tools and modular state management.

This report has not been submitted for any other programme, qualification, or assessment.

---

## Acknowledgement

The team extends its gratitude to the project mentor and supervisor for their technical guidance throughout the internship. We also thank the host organisation for providing the infrastructure necessary to complete this project.

Special thanks to the open-source communities:
- The maintainers of FastAPI and React for their extensive documentation.
- The developers behind Groq Cloud AI and MediaPipe for making advanced AI models accessible.
- Cockroach Labs for providing a robust serverless database tier.

---

## Abstract

Traditional Learning Management Systems often suffer from low engagement, while platforms like YouTube host vast quantities of structured educational content without accountability. This project bridges that gap by transforming any public YouTube playlist into a structured, gamified learning course.

The system's core capabilities include:
- **Automated Ingestion:** Importing full playlists and video metadata via the YouTube Data API.
- **Progress Enforcement:** Tracking playback to the second and strictly locking future lessons until current ones are completed.
- **Gamification Mechanics:** Rewarding learners with Experience Points (XP), level progressions, and daily login streaks.
- **AI Comprehension Checks:** Utilizing Groq Cloud AI (`llama-3.1-8b-instant`) to generate a pool of multiple-choice questions from video transcripts, requiring a 70% passing score.
- **Proctoring:** Employing MediaPipe Face Landmarker to pause videos if the learner looks away for over three seconds.

---

## Index

- [Chapter 1 — Introduction](#chapter-1--introduction)
- [Chapter 2 — Tech Stack Requirement](#chapter-2--tech-stack-requirement)
- [Chapter 3 — System Design](#chapter-3--system-design)
- [Chapter 4 — Testing and Security Analysis](#chapter-4--testing-and-security-analysis)
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

The growth of video-based online learning has democratised access to high-quality educational content. Platforms such as YouTube host complete course curricula published by universities and independent educators at no cost to the learner. 

However, consuming these playlists informally presents structural limitations:
- There is no mechanism to record which videos have been completed or to enforce a progression order.
- Returning to a playlist requires manually recalling the last watched video and the precise playback position.
- Without a structured accountability layer or gamified reward system, self-directed learners exhibit high dropout rates.

## 1.2 Problem Statement

Learners relying on YouTube playlists as their primary educational resource face significant tracking and motivation hurdles. Institutional LMS platforms address these issues but do not easily integrate with free YouTube content and often lack modern engagement mechanics.

The concrete problems faced by learners include:
- **No progress tracking:** Learners cannot distinguish completed videos from remaining ones.
- **No structured progression:** Users can skip ahead without mastering prerequisite material.
- **No comprehension verification:** There is no mechanism to confirm the learner has actually understood the video content.
- **No engagement incentive:** The absence of a reward system fails to motivate daily learning behaviour.

## 1.3 Project Objective

The primary objective was to develop a gamified web application that converts any public YouTube playlist into a structured, trackable, and accountable learning course. 

To achieve this, the system was designed to:
- Implement secure user authentication to persist individual learning progress.
- Preserve the original playlist sequence and enforce sequential lesson unlocking.
- Track playback accurately to the second, allowing seamless resumption across sessions.
- Award Experience Points (XP) and track daily streaks to sustain long-term engagement.
- Integrate a local Large Language Model (LLM) to dynamically generate quizzes from video transcripts.

## 1.4 Intended Users

The system is built primarily for highly motivated, self-directed learners who actively consume complex educational content through public YouTube playlists. It operates independently without requiring an instructor or administrator account.

Target user profiles include:
- **Independent Learners:** Individuals seeking a structured framework to track their progress and assess their comprehension.
- **Study Groups:** Small teams of students who wish to follow the same playlist-based curriculum collaboratively under separate, personalized accounts.
- **Continuous Upskillers:** Professionals relying on free video tutorials who require an accountability layer to ensure completion.


# Chapter 2 — Tech Stack Requirement

## 2.1 Frontend Frameworks and UI

The frontend of the application was engineered using React 19 to leverage its concurrent rendering features and vast ecosystem. TypeScript was strictly enforced across the codebase to ensure type safety and catch potential errors during development. 

Key frontend technologies include:
- **Vite 6:** Chosen for the build process and development server due to its exceptionally fast Hot Module Replacement (HMR).
- **Tailwind CSS v4:** Utilized for its utility-first approach, enabling rapid implementation of design tokens and a seamless dark mode.
- **Framer Motion:** Integrated to deliver fluid, declarative animations utilizing spring physics.
- **MediaPipe Tasks Vision:** Embedded directly in the browser to efficiently process a 468-point facial mesh for webcam proctoring.

## 2.2 Backend and APIs

The backend infrastructure required a runtime capable of robust asynchronous operations and a broad ecosystem for AI integration. Python 3.11+ running the FastAPI framework was selected for its native asynchronous support and seamless Pydantic validation.

Critical backend components include:
- **FastAPI & Uvicorn:** Acting as the core REST API framework and the production-grade ASGI server, respectively.
- **Authentication:** Employing `python-jose` for JWT creation and `passlib` with `argon2-cffi` to cryptographically hash user passwords using Argon2id.
- **External Integrations:** Utilizing the `httpx` library to asynchronously orchestrate calls to the YouTube Data API v3.
- **AI Services:** Integrating `youtube-transcript-api` to fetch auto-generated captions, which are then processed locally by the Ollama Python client to generate quizzes.

## 2.3 Database and Persistence

For data persistence, the system relies on the serverless cloud tier of CockroachDB. This distributed SQL database provides a PostgreSQL-compatible wire protocol, allowing the use of standard operations while completely eliminating manual database management.

Database management strategies involve:
- **SQLModel:** Acting as the ORM, seamlessly combining Pydantic and SQLAlchemy to eliminate the duplication of model definitions.
- **Dynamic Schema Creation:** Utilizing SQLModel's engine creation to dynamically manage database schemas on application startup.
- **Integrity Constraints:** Heavily utilizing database-level constraints (such as unique composite keys) to prevent duplicate data entry and maintain referential integrity.

## 2.4 Development and Deployment Tools

A suite of professional development tools was employed to ensure high code quality and streamline team collaboration. Version control was rigorously managed through Git and hosted on GitHub, facilitating a structured pull request workflow.

Development and deployment workflows include:
- **Code Quality:** Utilizing Husky for Git pre-commit hooks, Ruff for Python linting and formatting, and ESLint for maintaining the TypeScript codebase.
- **Testing:** Employing `pytest` alongside the FastAPI `TestClient` for comprehensive in-process API testing without requiring a live server.
- **Deployment:** Designing the MVP for local deployment, with the static React frontend easily hostable on platforms like Vercel, and the ASGI backend deployable to services like Railway or Render.

# Chapter 3 — System Design

## 3.1 High-Level Architecture

The system was architected following a decoupled, three-tier model designed to maximize separation of concerns and maintainability. The browser-based frontend operates independently, communicating with the backend exclusively via HTTP REST APIs secured with JWT bearer tokens. 

The responsibilities of each tier are strictly defined:
- **React Frontend:** Renders the user interface, manages local authentication state, orchestrates API requests, and executes privacy-preserving webcam proctoring locally.
- **FastAPI Backend:** Serves as the authoritative orchestrator, enforcing sequential lesson locking, calculating XP, and spawning asynchronous background tasks for AI quiz generation.
- **CockroachDB:** Acts as the unified, persistent storage layer, securely holding all user profiles, ingested playlists, tracked progress, and generated quizzes.

## 3.2 Database Design and ER Diagram

The structural foundation of the system is modeled relationally within CockroachDB. The central entity is the `users` table, which stores registered learner accounts along with their accumulated XP, current level, and daily streak data.

Below is the textual Entity Relationship (ER) diagram mapping the core data structures:

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

Key database design decisions include:
- **Composite Primary Keys:** The `user_progress` table employs a composite key (`user_id`, `video_id`) to mathematically guarantee only a single progress record per user per video.
- **Floating Sequence Orders:** Quizzes utilize floating-point sequence orders (e.g., 3.5) to interleave smoothly between videos without requiring mass renumbering of existing database rows.
- **Attempt Tracking:** The `quiz_attempts` table stores a JSON array of the exact question UUIDs presented, definitively binding the user's score to the specific questions they encountered.

## 3.3 Operational and Security Design

The operational design seamlessly merges the user interface, progress tracking, and security protocols into a cohesive experience. During playback, the progress-tracking mechanism relies on a precise frontend polling system that pings the backend every five seconds. 

The core operational and security mechanisms feature:
- **Anti-Cheat Buffer:** The backend maintains the highest watched second and applies a 15-second tolerance buffer to accommodate network latency while strictly preventing skipping ahead.
- **Server-Side Enforcement:** All sequential ordering and completion thresholds are enforced entirely server-side; the frontend possesses no authority to unlock videos.
- **Data Isolation:** Every protected API route retrieves the user context directly from the database on each request, guaranteeing that a valid token for one user cannot manipulate another user's progress.
- **Secure Quiz Scoring:** Quiz answers are scored strictly server-side, ensuring that correct options are never exposed to the client browser.

# Chapter 4 — Testing and Security Analysis

## 4.1 Testing Strategy and Proof of Tests

To ensure the reliability and performance of the system, a comprehensive testing strategy combining automated techniques with extensive manual validation was executed. Critical business logic functions were initially isolated and validated through strict unit testing.

The proof of our testing efforts includes:
- **Integration Testing:** FastAPI `TestClient` scripts validated the full request-response cycle, proving that database interactions and middleware performed flawlessly without a live server.
- **AI Pipeline Validation:** Mocked unit tests successfully demonstrated that our LLM generation functions could accurately parse JSON outputs using simulated `httpx` responses.
- **Functional Scenarios:** Explicit manual testing proved that duplicate playlist imports were successfully blocked, and that the anti-cheat seek-ahead prevention forcefully rejected attempts to bypass the 15-second buffer.

## 4.2 Security Measures

Security testing was paramount throughout development. We continuously attempted to break ownership checks and sequential locking mechanisms by manually constructing unauthorized requests to simulate malicious actors. 

Key security implementations included:
- **Robust Hashing:** Implementing Argon2id password hashing to heavily protect user credentials against advanced GPU and side-channel attacks.
- **Strict Origin Control:** Transitioning from an insecure wildcard CORS policy to a strictly enforced origin locking mechanism.
- **Data Isolation:** Ensuring that all protected routes retrieve user context directly from the database, unequivocally preventing cross-user data manipulation.
- **Server-Side Scoring:** Scrubbing the quiz submission endpoint of any response that might leak the correct option index to the client browser.

# Chapter 5 — Deployment and User Guide

## 5.1 Deployment Architecture

The deployment architecture is designed to be lightweight and cloud-ready, though currently optimized for a robust local development environment. The structure relies on the learner's browser connecting via HTTPS to a static host delivering the compiled React frontend.

The backend acts as the central orchestration hub, managing:
- **Database Connections:** Establishing secure TLS connections to the serverless CockroachDB instance.
- **API Requests:** Making authenticated, asynchronous requests to the YouTube Data API v3 for content ingestion.
- **AI Background Tasks:** Orchestrating communication with a locally running Ollama instance to generate quizzes seamlessly in the background.

## 5.2 User Guide

For end users, the experience is designed to be entirely frictionless. A learner begins by navigating to the registration page to create an account, which subsequently logs them into their personalized dashboard. 

The typical learning journey proceeds as follows:
- **Importing Content:** The user clicks "Import Playlist" and provides a valid YouTube URL. The backend ingests the course and renders it as a dedicated card on the dashboard.
- **Engaging with Lessons:** Upon opening a course, the learner selects the first unlocked video, optionally granting webcam permission to enable active attention monitoring.
- **Resuming and Progressing:** If a session is interrupted, the system flawlessly resumes playback from the last saved position. 
- **Earning Rewards:** As videos conclude, XP is awarded, streaks are updated, and the subsequent lesson or AI quiz is automatically unlocked.

# Chapter 6 — Results and Evaluation

## 6.1 System Achievements

The culmination of this project resulted in a highly functional and stable Gamified Learning Management System. The system successfully achieved its core mandate: transforming informal, unstructured YouTube viewing into a rigorous and engaging educational experience. 

Significant achievements include:
- **Rapid Ingestion:** Successfully demonstrating the ability to ingest a standard 15-video YouTube playlist in under four seconds, immediately rendering a fully structured course.
- **Flawless Tracking:** Proving that the backend reliably recorded real-time playback positions every five seconds, enabling perfect resume functionality even after sudden browser closures.
- **Robust Anti-Cheat:** Demonstrating that the server-enforced progression model successfully prevented learners from skipping ahead, ensuring XP was only awarded for genuine completion.

## 6.2 Performance Observations

The gamification layer proved to be highly responsive, with XP and level-ups reflecting instantaneously on the dashboard. Furthermore, our integration of a local LLM represented a major technical milestone for the project. 

Key performance metrics observed:
- **AI Generation Speed:** A quantised model (`qwen2.5:3b`) running on standard consumer hardware consistently generated 60 valid multiple-choice questions in just four to six minutes.
- **Proctoring Efficiency:** The browser-based MediaPipe Face Landmarker successfully ran at a throttled 15 fps, accurately detecting attention loss without severely taxing the user's CPU.
- **Dashboard Load Times:** Parallel API calls ensured that the heavily gamified dashboard consistently loaded in under 800 milliseconds on a standard broadband connection.

# Chapter 7 — Limitations and Future Scope

## 7.1 System Limitations

While the current system represents a robust application, there are several inherent limitations stemming from our architectural choices and reliance on external platforms. 

Primary constraints include:
- **API Dependency:** The system is entirely bound by YouTube's daily API quotas; widespread deployment could quickly exhaust these limits.
- **Content Volatility:** Videos that are subsequently deleted, made private, or have embedding disabled by the creator on YouTube will result in unplayable lessons.
- **Transcript Reliance:** Quizzes cannot be generated for videos lacking YouTube's auto-generated captions.
- **Local Infrastructure:** Requiring the Ollama LLM to run on the developer's local machine makes the system difficult to deploy broadly in a cloud environment without massive hosting costs.

## 7.2 Future Scope

Moving forward, the future scope of this project offers exciting avenues for expansion. A priority will be transitioning the AI infrastructure from a local Ollama instance to a scalable, cloud-hosted LLM API (such as Google Gemini) to enable true multi-user scaling. 

Planned future enhancements include:
- **AI Summarization:** Implementing advanced AI-driven video summarization to provide learners with structured text summaries directly below the player.
- **Topic Extraction:** Utilizing NLP to automatically tag courses and refine quiz question targeting based on extracted subjects.
- **Collaborative Features:** Developing peer review systems for quiz answers, cohort-level leaderboards, and video-specific discussion threads.
- **Mobile Application:** Building a native iOS and Android application equipped with offline video caching to vastly improve accessibility.

# Chapter 8 — Conclusion

## 8.1 Project Summary

The "YouTube Playlist–Based Gamified Learning Management System" successfully addressed the critical shortcomings of self-directed online learning. By recognizing that informal YouTube playlists lack structure, progress tracking, and engagement incentives, this project engineered a highly effective solution.

The final Minimum Viable Product delivered:
- **Structured Accountability:** Bridging the gap between abundant free content and the strict accountability of a formal educational platform.
- **Continuous Tracking:** Enforcing a sequential learning path and recording precise playback progress to perfectly track learner engagement.
- **Gamified Motivation:** Heavily incentivizing continuous learning through a robust gamification system of XP, levels, and daily streaks.
- **AI Integration:** Ensuring active absorption of material through dynamically generated comprehension quizzes and optional webcam proctoring.

# Chapter 9 — References

1. Google LLC. 2026. *YouTube Data API v3 Reference*. Retrieved July 28, 2026, from https://developers.google.com/youtube/v3/docs
2. Google LLC. 2026. *YouTube IFrame Player API Reference*. Retrieved July 28, 2026, from https://developers.google.com/youtube/iframe_api_reference
3. Sebastián Ramírez. 2026. *FastAPI Documentation*. Retrieved July 28, 2026, from https://fastapi.tiangolo.com/
4. Sebastián Ramírez. 2026. *SQLModel Documentation*. Retrieved July 28, 2026, from https://sqlmodel.tiangolo.com/
5. Meta Open Source. 2026. *React Documentation*. Retrieved July 28, 2026, from https://react.dev/
6. Evan You et al. 2026. *Vite Documentation*. Retrieved July 28, 2026, from https://vitejs.dev/guide/
7. Tailwind Labs. 2026. *Tailwind CSS v4 Documentation*. Retrieved July 28, 2026, from https://tailwindcss.com/docs
8. CockroachDB Inc. 2026. *CockroachDB Documentation*. Retrieved July 28, 2026, from https://www.cockroachlabs.com/docs/
9. Ollama Inc. 2026. *Ollama Documentation*. Retrieved July 28, 2026, from https://ollama.com/docs
10. Google LLC. 2026. *MediaPipe Tasks Vision — Face Landmarker*. Retrieved July 28, 2026, from https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker
11. Alibaba Cloud. 2024. *Qwen2.5 Technical Report*. Retrieved July 28, 2026, from https://qwenlm.github.io/blog/qwen2.5/
12. Alex Biryukov, Daniel Dinu, and Dmitry Khovratovich. 2015. *Argon2: the memory-hard function for password hashing and other applications*. Password Hashing Competition Winner. Retrieved July 28, 2026, from https://www.password-hashing.net/argon2-specs.pdf
13. Michael B. Jones, John Bradley, and Nat Sakimura. 2015. *RFC 7519 — JSON Web Token (JWT)*. Internet Engineering Task Force. Retrieved July 28, 2026, from https://datatracker.ietf.org/doc/html/rfc7519

# Appendix A — Userflow Screenshots

The following sequence of screenshots demonstrates the end-to-end user journey through the Gamified Learning Management System, capturing key interactions from initial registration to course completion.

**1. Registration and Authentication**
*(Insert Screenshot Here: Registration Page showing email/password input against the animated background)*
*(Insert Screenshot Here: Login Page confirming access)*

**2. Dashboard and Course Management**
*(Insert Screenshot Here: Dashboard view highlighting the XP, Level, and Streak stat cards at the top)*
*(Insert Screenshot Here: Playlist Import Modal showing a YouTube URL being pasted)*
*(Insert Screenshot Here: Dashboard updated with newly imported course cards displaying thumbnails and progress bars)*

**3. The Learning Experience**
*(Insert Screenshot Here: Course Player Page showing the embedded YouTube video actively playing, alongside the locked/unlocked sidebar)*
*(Insert Screenshot Here: Webcam proctoring overlay kicking in due to detected inattention)*

**4. Comprehension and Assessment**
*(Insert Screenshot Here: AI Quiz Interface presenting 30 multiple-choice questions to the learner)*
*(Insert Screenshot Here: Quiz results screen showing a passing score and the subsequent unlocking of the next module)*

# Appendix B — File Structure

The project was meticulously organized to maintain a clean separation of concerns between the frontend UI, backend logic, and necessary operational scripts. Below is a detailed breakdown of the complete folder and file structure.

**Root Directory (`summer_intern_group-a/`)**
The root directory acts as the container for the entire repository. It houses the fundamental `README.md` containing high-level project documentation, and a `Makefile` designed to orchestrate common development tasks.

**Backend Directory (`backend/`)**
The backend heavily utilizes the FastAPI framework and is structured into modular, domain-driven packages:
- `main.py`: Entry point for bootstrapping the FastAPI application and mounting CORS middleware.
- **Core Package (`core/`)**: Houses application lifespan handlers (`lifespan.py`) and authentication/DB dependency injectors (`deps.py`).
- **Models Package (`models/`)**: Contains modular SQLModel ORM declarations mapped to CockroachDB tables (`user.py`, `playlist.py`, `quiz.py`).
- **Routers Package (`routers/`)**: Contains modular API endpoints grouped by domain (`auth.py`, `users.py`, `playlists.py`, `progress.py`, `quizzes.py`).
- **LLM Engine Package (`llm_service/`)**: Encapsulates Groq Cloud AI quiz pool generation, priority async queuing (`queue.py`), prompt building (`llm_prompt.py`), and background worker execution (`worker.py`).
- **Test Suite Package (`tests/`)**: Automated pytest suite verifying auth flows, database operations, and Groq LLM response handling (`test_api.py`, `test_db.py`, `test_llm.py`).

**Frontend Directory (`frontend/`)**
The frontend is a React 19 application built with Vite, emphasizing modern design and robust component architecture.
- `package.json` & `vite.config.ts`: Defines npm dependencies and configures Vite aliases.
- **Source Package (`src/`)**:
  - `main.tsx` & `App.tsx`: Primary React DOM entry point and client-side routing component.
  - **Feature Modules (`auth/`, `dashboard/`, `course-player/`, `landing/`)**: Houses feature-isolated visual components and custom hooks (such as `useCoursePlayer`, `useYouTubePlayer`, and `useProctoring`).
  - **Subsystems (`proctoring/`, `quiz/`, `ytPlayer/`, `animatedBg/`)**: Isolated sub-modules for computer vision face landmarking, quiz UI controls, and particle canvas rendering.
  - **UI & Theme Modules (`ui/`, `theme/`, `styles/`)**: Contains atomic shadcn-inspired components, theme context toggles, and a modular vanilla CSS design system.

