# YouTube Playlist–Based Gamified Learning Management System

**Group A — Summer Internship Project**

---

# Preliminary Pages

## Title Page

| Field | Details |
|---|---|
| **Project Title** | YouTube Playlist–Based Gamified Learning Management System |
| **Team / Group** | Group A — Summer Intern Cohort |
| **Team Members** | Nirnoy Nath |
| **Programme** | Software Engineering Internship |
| **Organisation** | *(Host Organisation Name)* |
| **Supervisor / Mentor** | *(Supervisor Name)* |
| **Submission Date** | July 2026 |

---

## Declaration

We hereby declare that the work presented in this report is original and was carried out by the members of Group A during the summer internship programme. All external sources, libraries, frameworks, and APIs that contributed to this project have been properly cited and acknowledged in the References section.

The following third-party tools and services were used and are fully acknowledged:

- **FastAPI** — Python web framework (MIT Licence)
- **SQLModel** — ORM layer over SQLAlchemy (MIT Licence)
- **CockroachDB** — Distributed SQL database (BSL / CockroachDB Community Licence)
- **React 19** — UI library (MIT Licence)
- **Vite 6** — Frontend build tool (MIT Licence)
- **Tailwind CSS v4** — Utility-first CSS framework (MIT Licence)
- **Framer Motion** — Animation library (MIT Licence)
- **YouTube Data API v3** — Google LLC (Subject to YouTube API Services Terms of Service)
- **YouTube IFrame Player API** — Google LLC
- **Ollama** — Local LLM inference runtime (MIT Licence)
- **MediaPipe Tasks Vision** — Google LLC (Apache 2.0)
- **python-jose** — JWT handling (MIT Licence)
- **passlib / argon2-cffi** — Password hashing (BSD Licence)

This report has not been submitted for any other programme, qualification, or assessment.

---

## Acknowledgement

The team extends its gratitude to the project mentor and supervisor for their technical guidance throughout the internship. We thank the host organisation for providing the infrastructure, development environment, and collaborative workspace necessary to complete this project. We also acknowledge the open-source communities behind FastAPI, React, CockroachDB, Ollama, and MediaPipe, whose publicly available documentation and examples were instrumental in the implementation.

---

## Abstract

Traditional Learning Management Systems often suffer from low engagement and completion rates, while platforms such as YouTube host vast quantities of structured educational content in the form of public playlists. This project presents a Gamified Learning Management System with YouTube Ingestion, designed to bridge this gap by transforming any public YouTube playlist into a structured, progress-tracked, and gamified learning course.

The system enables users to import a playlist by pasting its URL. The backend then fetches all video metadata through the YouTube Data API v3, constructs a sequential course structure, and persists it in CockroachDB. Learners watch embedded videos through the YouTube IFrame Player API; their playback progress is saved to the second, and the system enforces sequential lesson unlocking to prevent skipping ahead. Gamification mechanics — Experience Points (XP), levels, and daily login streaks — are awarded for completing lessons. An integrated local Large Language Model (Ollama running qwen2.5:3b) automatically generates a pool of sixty multiple-choice questions per quiz from video transcripts, from which thirty are randomly selected per attempt, requiring a 70% score to pass. An optional webcam proctoring layer powered by MediaPipe Face Landmarker pauses video playback when the learner is detected as looking away for more than three seconds.

The frontend is built with React 19, TypeScript, Vite 6, and Tailwind CSS v4, featuring a glassmorphic dark/light-mode interface. The backend is powered by FastAPI with modular routers. The principal limitation is dependence on YouTube's API quotas and the availability of auto-generated captions, which directly affects quiz quality for videos lacking transcripts.

---

## Table of Contents

1. Introduction
2. Requirement Analysis
3. System Design
4. Technology Stack
5. Implementation
6. Testing and Security Analysis
7. Deployment and User Guide
8. Results and Evaluation
9. Limitations and Future Scope
10. Conclusion
11. References
12. Project Artefacts

---

## List of Figures

- Figure 1: Learner User-Flow Diagram
- Figure 2: High-Level System Architecture Diagram
- Figure 3: Entity Relationship (ER) Diagram
- Figure 4: Backend Module Breakdown
- Figure 5: Sequence Diagram — Playlist Ingestion
- Figure 6: Sequence Diagram — Video Progress Update
- Figure 7: Quiz Generation Pipeline
- Figure 8: Screenshot — Registration Page
- Figure 9: Screenshot — Login Page
- Figure 10: Screenshot — Gamified Dashboard
- Figure 11: Screenshot — Playlist Import Modal
- Figure 12: Screenshot — Course Player Page
- Figure 13: Screenshot — Quiz Interface
- Figure 14: Screenshot — Webcam Proctoring Overlay

---

## List of Tables

- Table 1: Functional Requirements
- Table 2: Non-Functional Requirements
- Table 3: Use Case Summary
- Table 4: API Endpoint Documentation
- Table 5: Database Entity Descriptions
- Table 6: Technology Stack Summary
- Table 7: Functional Test Cases
- Table 8: API Testing Scenarios
- Table 9: Security Findings and Resolutions
- Table 10: Defects and Resolutions
- Table 11: Feature Completion Status
- Table 12: Requirement Traceability Matrix

---

## List of Abbreviations

| Abbreviation | Full Form |
|---|---|
| LMS | Learning Management System |
| API | Application Programming Interface |
| UI | User Interface |
| UX | User Experience |
| REST | Representational State Transfer |
| JWT | JSON Web Token |
| ERD | Entity Relationship Diagram |
| ORM | Object-Relational Mapping |
| LLM | Large Language Model |
| MVP | Minimum Viable Product |
| XP | Experience Points |
| VRAM | Video Random Access Memory |
| CORS | Cross-Origin Resource Sharing |
| ASGI | Asynchronous Server Gateway Interface |
| MCQ | Multiple Choice Question |
| RAF | RequestAnimationFrame |

---

# Chapter 1 — Introduction

## 1.1 Background

The growth of video-based online learning has been exponential over the past decade. Platforms such as YouTube have democratised access to high-quality educational content: professional instructors, universities, and independent educators regularly publish complete course curricula as sequenced public playlists at no cost to the learner. Despite the abundance of content, consuming these playlists as informal viewing resources presents significant structural limitations.

A learner watching a YouTube playlist has no mechanism to record which videos have been completed, no enforced progression order, and no sense of measurable achievement. Revisiting a playlist after a break requires manually recalling the last watched position. There is no accountability layer, no comprehension check, and no reward for consistent engagement. These deficiencies are well-established in educational technology literature: without structure, goal-setting, and feedback, self-directed online learners exhibit high dropout rates.

Formal Learning Management Systems address these concerns through structured course organisation, progress tracking, and assessment. However, most institutional LMS platforms do not integrate YouTube content, require instructor accounts to create courses, and lack gamification mechanics that are known to improve sustained engagement. The gap between the richness of freely available YouTube educational content and the structured accountability of a proper LMS represents the core problem this project addresses.

## 1.2 Problem Statement

Learners who use YouTube playlists as primary learning resources face the following concrete problems:

1. **No progress tracking** — There is no record of which videos have been completed and which remain.
2. **No resumption support** — Returning to a playlist requires the learner to manually remember the correct video and the playback position within it.
3. **No structured progression** — Learners can skip to any video regardless of whether they have understood prior material.
4. **No completion status** — There is no indicator of overall course progress or course completion.
5. **No comprehension verification** — Nothing confirms that the learner has understood the material, not merely that the video was open.
6. **No engagement incentive** — There is no reward system to motivate daily or consistent learning behaviour.

## 1.3 Project Objective

The primary objective is to develop a gamified web application that converts any public YouTube playlist into a structured, trackable, and accountable learning course.

Supporting objectives include:

- Implement secure user authentication so that progress is persisted per learner.
- Preserve the original video sequence from the YouTube playlist and enforce sequential lesson unlocking.
- Save playback progress to the second and resume from the exact last position on return.
- Award Experience Points and track levels and daily streaks to sustain learner engagement.
- Integrate a locally-run Large Language Model to generate multiple-choice quizzes from video transcripts, providing structured comprehension checks.
- Implement webcam-based attention detection as an optional proctoring layer.

## 1.4 Project Scope

The following features are included in the final Minimum Viable Product:

- User registration and JWT-based authentication with Argon2 password hashing.
- Import of any public YouTube playlist by pasting its URL.
- Automatic creation of a structured course with one lesson per usable video.
- Embedded video playback using the YouTube IFrame Player API.
- Continuous playback progress tracking saved every few seconds.
- Resume-from-last-position functionality on returning to a course.
- Sequential lesson unlocking: a lesson is only accessible after the previous lesson is completed.
- Gamification: XP awarded per completed video, level calculated from cumulative XP, daily login streak tracking.
- AI-generated quizzes: a pool of up to 60 MCQs generated from video transcripts using Ollama; 30 are randomly selected per attempt; 70% score required to pass.
- Optional webcam proctoring: MediaPipe Face Landmarker detects whether the learner is looking at the screen; video pauses after 3 seconds of inattention.
- Course dashboard showing all imported courses, thumbnail, progress percentage, status badge, and last-accessed date.
- Course deletion with cascade removal of all associated progress and quiz data.
- Dark and light theme toggle.

## 1.5 Out-of-Scope Features

The following features are explicitly excluded from the current version:

- Native video hosting: all video content remains hosted on YouTube.
- Payment gateways or monetisation of any kind.
- Instructor-specific dashboards or course-creation tools for third parties.
- Social features: leaderboards, discussion forums, direct messaging, or peer interaction.
- Official certificates or credentials.
- AI-generated video summaries or transcription editing.
- Advanced analytics or learner behaviour dashboards beyond basic XP and streak.
- Mobile application (iOS or Android).
- Offline access.
- Multi-language support.

This section exists to prevent the report from creating false expectations regarding functionality that was not developed.

## 1.6 Intended Users

The primary users of this system are self-directed learners who consume educational content through public YouTube playlists. These learners are typically motivated but lack a structured framework to track, assess, and sustain their learning. The system does not require any instructor account: a learner registers, imports a playlist of their choice, and proceeds entirely independently.

Secondarily, the system is intended for small teams of students who wish to follow the same playlist-based curriculum collaboratively under separate accounts.

## 1.7 Organisation of the Report

Chapter 2 presents the full requirement analysis, including stakeholders, functional and non-functional requirements, assumptions, constraints, and use cases. Chapter 3 covers system design across architecture, component structure, database design, API design, interface design, progress-tracking design, and security design. Chapter 4 documents the complete technology stack with justifications. Chapter 5 details the implementation of each major system module. Chapter 6 presents the testing strategy, functional test cases, API tests, security findings, and defect log. Chapter 7 provides deployment architecture and a step-by-step user guide. Chapter 8 evaluates results against planned requirements. Chapter 9 documents limitations and future scope. Chapter 10 concludes the report.

---

# Chapter 2 — Requirement Analysis

## 2.1 Stakeholders

| Stakeholder | Role |
|---|---|
| **Learner** | Primary user who imports playlists, watches videos, earns XP, and takes quizzes |
| **Development Team** | Group A interns responsible for design, implementation, and testing |
| **Project Mentor / Supervisor** | Provides technical and project management guidance |
| **YouTube (Google LLC)** | External service provider supplying the Data API v3, IFrame Player API, and video content |
| **CockroachDB** | External cloud database provider |
| **Ollama** | Local inference runtime used for quiz generation |

## 2.2 Functional Requirements

**Table 1: Functional Requirements**

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow a user to register with an email address and password. |
| FR-02 | The system shall allow a registered user to log in and receive a JWT access token. |
| FR-03 | The system shall allow an authenticated user to import a public YouTube playlist by URL. |
| FR-04 | The system shall extract the playlist ID from the full YouTube URL. |
| FR-05 | The system shall fetch all video metadata from the YouTube Data API v3, handling pagination. |
| FR-06 | The system shall skip deleted and private videos during ingestion. |
| FR-07 | The system shall preserve the original video sequence order from the playlist. |
| FR-08 | The system shall prevent a user from importing the same playlist twice. |
| FR-09 | The system shall save playback progress (current second and highest watched second) per video per user. |
| FR-10 | The system shall enforce sequential lesson unlocking: a video is locked until the previous video is completed. |
| FR-11 | The system shall prevent the learner from seeking ahead beyond 15 seconds of the highest recorded position. |
| FR-12 | The system shall mark a video as completed when the learner reaches within 15 seconds of the end. |
| FR-13 | The system shall award 50 XP to the user on first completion of a video. |
| FR-14 | The system shall calculate the learner's level as (total_xp ÷ 500) + 1. |
| FR-15 | The system shall track and display a daily login streak, incrementing if the user logged in on the previous calendar day. |
| FR-16 | The system shall generate quizzes after every 3 videos in a playlist and one final quiz covering the entire playlist. |
| FR-17 | The system shall generate a pool of up to 60 MCQs per quiz using the Ollama LLM from YouTube video transcripts. |
| FR-18 | The system shall randomly select 30 questions from the pool per quiz attempt. |
| FR-19 | The system shall require a minimum score of 70% to pass a quiz. |
| FR-20 | The system shall enforce that a quiz must be passed before the next video is unlocked. |
| FR-21 | The system shall optionally activate webcam-based attention detection during video playback. |
| FR-22 | The system shall pause video playback if the learner looks away for more than 3 seconds (when proctoring is active). |
| FR-23 | The system shall display a dashboard showing all imported courses with progress, status, and thumbnail. |
| FR-24 | The system shall allow a user to delete a course and all associated progress data. |
| FR-25 | The system shall prevent any user from accessing or modifying another user's data. |

## 2.3 Non-Functional Requirements

**Table 2: Non-Functional Requirements**

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Security | Passwords shall be stored using Argon2 hashing; no plaintext password shall be persisted. |
| NFR-02 | Security | All protected endpoints shall require a valid JWT bearer token; expired or invalid tokens shall be rejected with HTTP 401. |
| NFR-03 | Security | The backend shall verify that the requesting user owns the playlist before permitting progress updates or deletions. |
| NFR-04 | Security | API keys and secrets shall be loaded from environment variables and never hardcoded in source code. |
| NFR-05 | Performance | The dashboard page shall load within 3 seconds on a standard broadband connection. |
| NFR-06 | Performance | Progress update API calls shall complete within 500 ms under normal database conditions. |
| NFR-07 | Reliability | The backend shall handle YouTube API failures gracefully without crashing, returning descriptive error messages. |
| NFR-08 | Reliability | Quiz generation failure shall set the quiz status to an error state without affecting the rest of the course. |
| NFR-09 | Usability | The interface shall support both dark and light themes, switchable at any point. |
| NFR-10 | Usability | Error states shall display human-readable messages, not raw stack traces. |
| NFR-11 | Scalability | The CockroachDB database shall support horizontal scaling independent of backend instances. |
| NFR-12 | Maintainability | Backend business logic shall be split into feature-specific routers, not placed in a single monolithic file. |
| NFR-13 | Data Integrity | Cascade deletion shall remove all videos, progress records, quizzes, questions, and attempts when a playlist is deleted. |
| NFR-14 | Responsiveness | The frontend shall render correctly on desktop (≥1280 px), tablet (768–1279 px), and mobile (≤767 px) screen widths. |
| NFR-15 | API Compliance | All YouTube API usage shall comply with the YouTube API Services Terms of Service. |

## 2.4 Assumptions

- The playlist URL submitted by the learner points to a public YouTube playlist.
- The videos within the playlist permit embedding via the YouTube IFrame Player API.
- The learner has a stable internet connection sufficient for video streaming.
- YouTube's Data API v3 and IFrame API remain available and their response schemas remain consistent.
- Playlist content may be modified on YouTube after ingestion; such changes are not automatically reflected in the imported course.
- Completion of a video does not prove genuine understanding by the learner; it proves only that the playback position reached near the end.
- Webcam availability is not guaranteed; the proctoring feature degrades gracefully when webcam access is denied.
- The Ollama instance is running locally; quiz generation is not available if Ollama is not active.

## 2.5 Constraints

- **YouTube API quota**: The YouTube Data API v3 imposes a default quota of 10,000 units per day. Playlist import consumes quota proportional to playlist length. Large deployments may exhaust quota.
- **Deleted and private videos**: Videos that become private or deleted after playlist import remain as entries in the course but cannot be played.
- **Embedding restrictions**: Some YouTube videos have embedding disabled by the uploader. Such videos display an error within the player.
- **Transcript availability**: AI quiz generation relies on YouTube's auto-generated captions. Videos without captions or with captions in unsupported formats will produce quizzes labelled `error_no_transcript`.
- **Local LLM compute constraint**: Quiz generation is performed by a locally-running Ollama model. Generation time per quiz is proportional to hardware capability.
- **Project duration**: The system was designed and implemented within a summer internship period of approximately 8 weeks.
- **Team size**: The project was carried out by a small group of interns, limiting the breadth of testing and features achievable.

## 2.6 Use Cases

**Table 3: Use Case Summary**

| Use Case ID | Name | Actor |
|---|---|---|
| UC-01 | Register Account | Unauthenticated User |
| UC-02 | Log In | Registered User |
| UC-03 | Import Playlist | Authenticated Learner |
| UC-04 | View Dashboard | Authenticated Learner |
| UC-05 | Open Course | Authenticated Learner |
| UC-06 | Watch and Progress Through Video | Authenticated Learner |
| UC-07 | Resume Video | Authenticated Learner |
| UC-08 | Take Quiz | Authenticated Learner |
| UC-09 | Unlock Next Lesson | System (automatic on completion) |
| UC-10 | Enable Webcam Proctoring | Authenticated Learner |
| UC-11 | Delete Course | Authenticated Learner |

**UC-03: Import Playlist (detailed)**

- **Actor**: Authenticated Learner
- **Preconditions**: User is logged in; the target playlist is public on YouTube.
- **Main Flow**:
  1. User clicks "Import Playlist" on the dashboard.
  2. User pastes a YouTube playlist URL into the input field.
  3. Frontend extracts the `list` query parameter as the playlist ID.
  4. Frontend sends `POST /api/ingest/playlist` with the playlist ID and JWT token.
  5. Backend validates the YouTube API key is configured.
  6. Backend calls YouTube Data API v3 `/playlists` to fetch playlist metadata.
  7. Backend checks the playlist does not already exist for this user.
  8. Backend calls `/playlistItems` (paginated) to fetch all video entries.
  9. Backend filters out deleted and private videos.
  10. Backend saves the Playlist and all Video records to CockroachDB.
  11. Backend creates Quiz records at every 3-video boundary and one final quiz.
  12. Background task starts Ollama quiz generation sequentially per quiz.
  13. Backend returns success response; dashboard reloads to show the new course.
- **Alternative Flow**: If the playlist is already imported, the backend returns HTTP 400 and the frontend displays an error in the modal.
- **Alternative Flow**: If the YouTube playlist is not found, HTTP 404 is returned.
- **Postconditions**: A Playlist record, Video records, and Quiz skeleton records exist in the database. Quiz question generation is in progress in the background.

**UC-06: Watch and Progress Through Video (detailed)**

- **Actor**: Authenticated Learner
- **Preconditions**: The learner has opened a course. The first video is unlocked.
- **Main Flow**:
  1. Learner clicks a video in the course sidebar.
  2. If webcam proctoring is enabled, the system verifies the learner is looking at the screen.
  3. The YouTube IFrame player loads the video.
  4. Every few seconds of playback, the frontend sends `POST /api/progress/update` with the current playback position and video duration.
  5. Backend validates the user owns the playlist and all prior videos/quizzes are completed.
  6. Backend validates the reported position is not more than 15 seconds ahead of the highest previously recorded position.
  7. Backend saves the updated progress record.
  8. When progress reaches within 15 seconds of the video duration, backend marks the video as completed and awards 50 XP.
  9. Backend recalculates the learner's level.
  10. Frontend reflects the completion and unlocked state of the next item.
- **Alternative Flow**: If the learner attempts to seek ahead, the backend rejects the progress update and the frontend seeks the player back to the last allowed position.
- **Alternative Flow**: If webcam proctoring detects inattention for 3 seconds, the player pauses and an overlay is displayed.

## 2.7 User-Flow Diagram

```
[Register / Login]
        |
        v
[Dashboard: View Imported Courses]
        |
        |--[No courses]-->[Import Playlist Modal]
        |                         |
        |                         v
        |               [Validate & Fetch from YouTube API]
        |                         |
        |                         v
        |               [Course Created in DB]
        |                         |
        v                         v
[Open Course: View Video + Quiz Sequence]
        |
        v
[Watch Video 1 (with optional proctoring)]
        |
        v
[Progress Saved Per Second to Backend]
        |
        v
[Video 1 Completed → 50 XP Awarded]
        |
        v
[Video 2 and Video 3 Unlocked Sequentially]
        |
        v
[Quiz 1 Unlocked → AI Questions Generated by Ollama]
        |
        v
[Take Quiz: 30 Random MCQs, 70% Pass Threshold]
        |
  [Pass]           [Fail]
    |                 |
    v                 v
[Next Videos       [Retake Quiz with
 Unlocked]          Different Questions]
    |
    v
[... Continue through all videos and quizzes ...]
    |
    v
[Final Playlist Quiz]
    |
    v
[Course Completed: Status = Completed]
```

---

# Chapter 3 — System Design

## 3.1 High-Level Architecture

The system follows a three-tier decoupled architecture:

```
+------------------------------------------+
|        Browser (React 19 + Vite 6)       |
|   TypeScript · Tailwind CSS v4 · Axios   |
|      Port 5173 (development)             |
+------------------+-----------------------+
                   | HTTP REST / JWT Bearer Token
                   v
+------------------------------------------+
|       FastAPI Backend (Python 3.11+)     |
|   Uvicorn ASGI · Modular Router Design   |
|      Port 8000                           |
|  +-----------+ +-----------+ +--------+  |
|  | /api/auth | |/api/playlists| |/api/ |  |
|  |  router   | |   router   | |quizzes|  |
|  +-----------+ +-----------+ +--------+  |
+------+---------+---------+--------------+
       |         |         |
       v         v         v
+------------+ +-------+ +-------------------+
|CockroachDB | |YouTube| |  Ollama (local)    |
|(Serverless)| |API v3 | |  qwen2.5:3b model  |
|Port 26257  | |       | |  Port 11434        |
+------------+ +-------+ +-------------------+
```

**Component responsibilities:**

- **React Frontend**: Renders all UI, manages JWT in localStorage, makes REST calls via Axios, runs MediaPipe Face Landmarker in the browser for proctoring.
- **FastAPI Backend**: Handles authentication, business logic, YouTube API orchestration, sequential locking enforcement, XP calculation, and spawns background tasks for quiz generation.
- **CockroachDB**: Stores all persistent data (users, playlists, videos, progress, quizzes, questions, attempts, XP logs). Selected for its serverless tier, distributed SQL capabilities, and PostgreSQL-compatible wire protocol.
- **YouTube Data API v3**: Supplies playlist and video metadata during ingestion.
- **Ollama**: Runs the quantised qwen2.5:3b language model locally to generate quiz questions from video transcripts supplied by `youtube-transcript-api`.

## 3.2 Component Design

**Authentication Module** (`routers/auth.py`)
Handles user registration and login. On registration, the password is hashed with Argon2 using passlib. On login, the hash is verified and a signed JWT (HS256, 24-hour expiry) is returned. The streak counter is updated on each login.

**Playlist Ingestion Module** (`routers/playlists.py` — ingest endpoints)
Orchestrates YouTube API calls, video record creation, quiz scheduling, and background task dispatch. The quiz schedule is computed by a pure helper function `_build_quiz_schedule` to keep it testable independently of the route handler.

**Course Management Module** (`routers/playlists.py` — CRUD endpoints)
Provides listing, retrieval, and deletion of playlists. The `GET /api/playlists` endpoint computes progress statistics, thumbnail URL, and last-accessed date for each playlist before returning.

**Video Player Module** (`frontend/src/course-player/`)
Wraps the YouTube IFrame Player API in a custom React hook (`useYouTubePlayer.ts`). The hook exposes `play()`, `pause()`, `seekTo()`, `getCurrentTime()`, and `getDuration()` functions to the parent component.

**Progress Tracking Module** (`routers/progress.py`)
Enforces the sequential locking rules and the anti-cheat seek buffer on every progress update. Awards XP and updates level on first completion.

**Proctoring Module** (`frontend/src/course-player/useProctoring.ts`)
Uses MediaPipe FaceLandmarker with the GPU delegate at approximately 15 frames per second. Computes yaw (horizontal) and pitch (vertical) head pose from facial landmark positions. If yaw exceeds ±25° or pitch exceeds ±25° for more than 3 seconds, the attention-lost callback fires and the video pauses.

**Quiz Module** (`routers/quizzes.py` + `llm_service.py`)
The quiz start endpoint selects 30 questions at random from the pool and creates an attempt record linking those specific question IDs to the attempt. This prevents the learner from being scored against questions they were not asked. The submit endpoint re-fetches each question from the database to verify the correct answer, preventing client-side answer manipulation.

**Dashboard Module** (`frontend/src/dashboard/DashboardPage.tsx`)
Fetches user profile and all playlists in parallel on mount. Renders XP total, current level with progress bar, daily streak, and a responsive grid of course cards.

## 3.3 Database Design

### Entity Descriptions

**Table 5: Database Entity Descriptions**

| Table | Description |
|---|---|
| `users` | Stores registered learner accounts, XP, level, and streak data |
| `playlists` | Represents an imported YouTube playlist as a course, linked to the user who imported it |
| `videos` | One record per usable video in a playlist, with sequence order and YouTube metadata |
| `user_progress` | Composite-key table tracking how far each user has watched each video |
| `quizzes` | Quiz checkpoint records placed between video groups, with generation status |
| `questions` | Individual MCQ question pool entries linked to a quiz |
| `quiz_attempts` | Records each attempt by a user on a quiz, including which 30 questions were presented and the final score |
| `xp_log` | Append-only audit log of every XP-awarding event |

### ER Diagram (Textual)

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

### Key Design Decisions

- `user_progress` uses a **composite primary key** (`user_id`, `video_id`) to ensure only one progress record per user per video, without a surrogate key.
- The `quiz_attempts.questions_asked` field stores a JSON array of the specific question UUIDs presented in that attempt. This is intentional: it binds the scoring to exactly the questions shown, even if the pool changes due to regeneration.
- `quizzes.sequence_order` stores a float (e.g., `3.5`, `3.25`, `3.75`) to interleave quizzes with videos without renumbering all existing records.
- `videos.yt_metadata` stores the raw YouTube API snippet JSON in a `JSON` column for future use (thumbnails, descriptions, channel data) without requiring schema migrations.
- A `UniqueConstraint` on (`user_id`, `yt_playlist_id`) in the `playlists` table enforces the duplicate-import prevention at the database level.

## 3.4 API Design

**Table 4: API Endpoint Documentation**

| Method | Endpoint | Auth | Purpose | Key Responses |
|---|---|---|---|---|
| `GET` | `/` | No | Health check | 200: version message |
| `POST` | `/api/auth/register` | No | Register a new user | 200: success; 400: email exists |
| `POST` | `/api/auth/login` | No | Authenticate and receive JWT (form body) | 200: access_token; 400: invalid credentials |
| `GET` | `/api/users/me` | Yes | Return current user's profile and stats | 200: user object; 401: unauthorised |
| `POST` | `/api/ingest/playlist` | Yes | Import a YouTube playlist as a course | 200: course created; 400: duplicate; 404: playlist not found; 500: no API key |
| `GET` | `/api/playlists` | Yes | List all courses for the user with progress stats | 200: array of playlist objects |
| `DELETE` | `/api/playlists/{id}` | Yes | Delete a course and all its data | 200: success; 404: not found |
| `GET` | `/api/playlists/{id}/videos` | Yes | Return ordered videos and quizzes with lock/completion state | 200: mixed array; 404: not found |
| `POST` | `/api/progress/update` | Yes | Save playback position, enforce order, award XP on completion | 200: allowed/rejected with seek position; 403: order violated; 404: video not found |
| `GET` | `/api/quizzes/{id}/start` | Yes | Begin a quiz attempt, receive 30 random questions | 200: questions + attempt_id; or status if not ready |
| `POST` | `/api/quizzes/{id}/submit` | Yes | Score a quiz attempt | 200: score, passed flag, correct count |

### Progress Update Request/Response Example

**Request** `POST /api/progress/update`
```json
{
  "video_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "current_time": 142.5,
  "duration": 600.0
}
```

**Response (allowed)**
```json
{
  "allowed": true,
  "highest_watched_second": 142.5,
  "last_watched_second": 142.5,
  "completed": false,
  "xp_awarded": 0,
  "total_xp": 150,
  "current_level": 1,
  "leveled_up": false
}
```

**Response (seek rejected)**
```json
{
  "allowed": false,
  "seek_to": 142.5,
  "completed": false
}
```

## 3.5 Interface Design

The interface uses a glassmorphic design system built entirely with Tailwind CSS v4 utility classes and Framer Motion animations. Key design decisions:

- A dark/light mode is supported at the system level via CSS custom properties and toggled through a `ThemeToggle` component.
- An `AnimatedBackground` component renders subtle gradient orbs behind content on the login, register, and dashboard pages.
- The dashboard renders XP, level, and streak in three equal-width stat cards above a responsive grid of course cards.
- Course cards display: thumbnail (fetched from YouTube CDN), title, description excerpt, video count badge, status badge (Not Started / In Progress / Completed), progress bar, completion fraction, last-accessed date, and a Continue button.
- The course player page uses a two-panel layout: a scrollable sidebar listing videos and quizzes (with lock icons on locked items) and a main area showing the YouTube embed or quiz interface.
- A picture-in-picture webcam preview (`CameraPip`) is shown in the bottom-right corner when proctoring is active.

## 3.6 Progress-Tracking Design

Progress is tracked through a polling mechanism in the frontend. Every 5 seconds during active playback, the `CoursePlayerPage` calls the progress update endpoint. The design decisions are:

1. **Highest-position tracking**: The backend stores both `last_watched_second` (where the player currently is) and `highest_watched_second` (the furthest point ever reached). The anti-cheat check uses the `highest_watched_second`.
2. **Seek buffer**: A tolerance of 15 seconds (`SEEK_BUFFER_SECONDS`) is applied to the seek detection to accommodate YouTube IFrame player seeking inaccuracies and network latency in reporting.
3. **Completion threshold**: A video is marked complete when `highest_watched_second >= duration - 15`. This allows for non-skippable YouTube endscreens and avoids requiring the learner to watch credits.
4. **Backend enforcement**: All ordering and completion checks are performed server-side. The frontend does not have the authority to unlock videos; it only reflects the backend state.
5. **Resumption**: On loading the course player, the frontend receives the `last_watched_second` for each video from `GET /api/playlists/{id}/videos` and calls `seekTo()` on the player when the video is selected.

## 3.7 Security Design

- **Password hashing**: Argon2id via `passlib[argon2]`. Argon2id is the current recommended winner of the Password Hashing Competition and is resistant to GPU and side-channel attacks.
- **JWT authentication**: Tokens are signed with HS256 using a secret key loaded from the `SECRET_KEY` environment variable. Tokens expire after 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES = 1440`).
- **Authorisation**: Every protected route verifies the JWT and retrieves the user from the database on every request. There is no session cache that could be stale.
- **Ownership checks**: Before any progress update or playlist deletion, the backend verifies `playlist.user_id == current_user.id`. A valid JWT for User A cannot be used to modify User B's data.
- **Anti-cheat**: The sequential locking and seek-buffer checks are enforced entirely in the backend. The frontend cannot bypass them by modifying JavaScript.
- **Environment variable protection**: `DATABASE_URL`, `SECRET_KEY`, `YOUTUBE_API_KEY` are never committed to source control and are loaded via `python-dotenv`.
- **CORS**: The FastAPI CORS middleware is configured to allow only the `FRONTEND_URL` origin, preventing arbitrary cross-origin requests.
- **Input validation**: FastAPI uses Pydantic models for all request bodies. Invalid types or missing fields return HTTP 422 before any business logic runs.
- **Error messages**: The global exception handler returns generic messages for 500-class errors, not stack traces.
- **Quiz answer verification**: Correct answers are stored in the database and fetched server-side during scoring. The client never receives the `correct_option_index` when questions are served.

---

# Chapter 4 — Technology Stack

## 4.1 Frontend

**Table 6: Frontend Technology Stack**

| Technology | Version | Purpose | Reason for Selection |
|---|---|---|---|
| React | 19.1.0 | UI component library | Concurrent features; wide ecosystem |
| TypeScript | 5.8.3 | Type-safe JavaScript | Catches type errors at compile time; improves IDE support |
| Vite | 6.3.5 | Build tool and dev server | Extremely fast HMR; native ESM; modern defaults |
| Tailwind CSS | v4.3.2 | Utility-first CSS | Rapid styling; design tokens; dark mode; no CSS file management |
| Framer Motion | 12.10.0 | Animation library | Declarative, performant animations; spring physics |
| React Router DOM | 7.6.2 | Client-side routing | File-based and declarative route definition |
| Axios | 1.9.0 | HTTP client | Interceptor support for global error toasting; cleaner API than fetch |
| Lucide React | 0.511.0 | Icon library | Consistent, tree-shakeable SVG icons |
| React Toastify | 11.0.3 | Toast notifications | Simple global notification system with dark theme support |
| MediaPipe Tasks Vision | 0.10.35 | Face landmark detection | Google's official library; GPU delegate; 468-point facial mesh |

## 4.2 Backend

| Technology | Version | Purpose | Reason for Selection |
|---|---|---|---|
| Python | 3.11+ | Runtime | Broad ML/AI library ecosystem; async support |
| FastAPI | 0.115+ | Web framework | Native async; automatic OpenAPI docs; Pydantic integration |
| Uvicorn | 0.34+ | ASGI server | Production-grade async server; standard for FastAPI |
| SQLModel | 0.0.22 | ORM | Combines Pydantic and SQLAlchemy; avoids duplication of model definitions |
| SQLAlchemy | 2.0.41 | ORM backend | Industry-standard; CockroachDB-compatible dialect |
| python-jose | 3.3.0 | JWT handling | Standard library for JWT encode/decode with HS256 |
| passlib[argon2] | 1.7.4 | Password hashing | Argon2id — best current algorithm for password storage |
| httpx | 0.28.1 | Async HTTP client | Used for async YouTube API calls within async route handlers |
| youtube-transcript-api | 1.0.3 | Transcript fetching | Retrieves auto-generated captions for quiz generation |
| python-dotenv | 1.1.0 | Environment variables | Standard .env file loading |
| ollama | 0.4.8 | LLM client (optional) | Python client for Ollama REST API |

## 4.3 Database

**Database**: CockroachDB (Serverless Cloud Tier)

- **Type**: Distributed SQL (PostgreSQL-compatible wire protocol)
- **Reason for selection**: The PostgreSQL compatibility means SQLAlchemy and psycopg2 work without modification. The serverless tier eliminates database server management. CockroachDB's distributed architecture provides high availability.
- **ORM**: SQLModel (wrapping SQLAlchemy 2.x) with the `sqlalchemy-cockroachdb` dialect.
- **Schema management**: SQLModel's `SQLModel.metadata.create_all(engine)` creates all tables on application startup. There is no separate migration tool in the current version.
- **Indexing**: Foreign key columns (`user_id`, `playlist_id`, `video_id`, `quiz_id`) and the `email` column in `users` carry database indexes defined in the SQLModel field declarations.
- **Connection pooling**: The engine is configured with `pool_size=20` and `max_overflow=50` to handle concurrent requests during playlist ingestion.

## 4.4 Development Tools

| Tool | Purpose |
|---|---|
| Git | Version control |
| GitHub | Remote repository, pull request workflow |
| Visual Studio Code | Primary IDE |
| npm | Frontend package manager |
| pip / venv | Python dependency management |
| Husky | Git pre-commit hooks |
| Ruff | Python linter and formatter |
| ESLint | TypeScript/JavaScript linter |
| pytest | Backend testing framework |
| FastAPI TestClient | In-process API testing without a live server |
| Postman / curl | Manual API exploration |

## 4.5 Deployment Stack

In its current MVP form, the application is designed for local development deployment. Production deployment guidance is as follows:

| Component | Hosting | Notes |
|---|---|---|
| Frontend | Static hosting (e.g., Vercel, Netlify) | `npm run build` produces a static dist/ folder |
| Backend | Any ASGI-compatible host (e.g., Railway, Render, Fly.io) | Run with `uvicorn main:app` |
| Database | CockroachDB Serverless (cloud) | Connection string in `DATABASE_URL` env var |
| Ollama | Local machine only | Not suitable for public cloud without significant cost; quiz generation is a background task and can tolerate latency |
| Environment | `.env` files per environment | Secrets managed outside source control |

No CI/CD pipeline was implemented during this internship. Future work should add GitHub Actions for automated testing and deployment.

---

# Chapter 5 — Implementation

## 5.1 Project Structure

```
summer_intern_group-a/
|
+-- backend/
|   +-- core/
|   |   +-- deps.py          # Shared: DB engine, session, JWT, auth dependencies
|   |   +-- __init__.py
|   +-- routers/
|   |   +-- auth.py          # POST /api/auth/register, POST /api/auth/login
|   |   +-- users.py         # GET /api/users/me
|   |   +-- playlists.py     # Ingestion, listing, deletion, video retrieval
|   |   +-- progress.py      # POST /api/progress/update
|   |   +-- quizzes.py       # GET /start, POST /submit
|   |   +-- __init__.py
|   +-- tests/
|   |   +-- test_environment.py  # 31-test verification suite
|   |   +-- __init__.py
|   +-- main.py              # App bootstrap + router mounting (~75 lines)
|   +-- models.py            # All SQLModel ORM table definitions
|   +-- llm_service.py       # Ollama quiz generation pipeline
|   +-- requirements.txt     # Pinned production dependencies
|   +-- requirements-dev.txt # Pinned dev/test dependencies
|   +-- pyproject.toml       # Project metadata + ruff + pytest config
|   +-- .env.example         # Template for required environment variables
|
+-- frontend/
|   +-- src/
|   |   +-- auth/            # AuthContext, LoginPage, RegisterPage, axios instance
|   |   +-- dashboard/       # DashboardPage (course cards, stats, import modal)
|   |   +-- course-player/   # CoursePlayerPage, QuizView, useYouTubePlayer,
|   |   |                    # useProctoring, WebcamPermissionGate, AttentionOverlay, CameraPip
|   |   +-- landing/         # LandingPage, Navbar, Footer
|   |   +-- ui/              # Reusable base components (Button, Card, Input, Badge...)
|   |   +-- theme/           # ThemeToggle, AnimatedBackground
|   |   +-- types/           # youtube.d.ts (IFrame API type definitions)
|   |   +-- App.tsx           # Root router
|   |   +-- main.tsx          # React DOM entry point
|   |   +-- index.css         # Global CSS + Tailwind v4 design tokens
|   +-- scripts/
|   |   +-- verify-env.mjs   # Node.js environment verification script
|   +-- package.json         # Pinned npm dependencies
|   +-- vite.config.ts
|   +-- tsconfig.json
|
+-- README.md
+-- Makefile
```

## 5.2 Authentication Implementation

**Registration**: The `POST /api/auth/register` endpoint accepts `{ email, password }` as JSON. It queries the `users` table for an existing record with the same email. If found, it returns HTTP 400. Otherwise, it hashes the password with Argon2 via `pwd_context.hash(password)` and creates a `User` record.

**Login**: The `POST /api/auth/login` endpoint accepts OAuth2 form data (`username` field maps to email). It fetches the user by email, then verifies the submitted password against the stored Argon2 hash using `pwd_context.verify()`. If the credentials match, the streak counter is updated based on `last_activity_date`, and a JWT is created with `sub` set to the user's UUID.

**Token handling**: The JWT is returned to the frontend, which stores it in `localStorage`. Subsequent API calls include it as `Authorization: Bearer <token>`. The `get_current_user` dependency in `core/deps.py` decodes the token on every request, fetching the user fresh from the database to ensure the user still exists.

**Protected routes**: All routes that require authentication use `Depends(get_current_user)`. Unauthenticated requests receive HTTP 401 before any business logic executes.

**Frontend routing**: `App.tsx` wraps protected routes in conditional redirects using `useAuth()`. If `token` is null (not in localStorage), the user is redirected to `/login`.

## 5.3 Playlist Import Implementation

1. **URL parsing**: The frontend uses the browser's `URL` API to parse the pasted URL and extract the `list` query parameter as the `playlist_id`.
2. **API call**: `POST /api/ingest/playlist` sends `{ playlist_id }` to the backend.
3. **YouTube API — playlist metadata**: `httpx.AsyncClient` calls `https://www.googleapis.com/youtube/v3/playlists?part=snippet&id={id}&key={key}`. If `items` is empty, HTTP 404 is returned.
4. **Duplicate check**: A query for an existing `Playlist` with the same `(user_id, yt_playlist_id)` pair prevents re-import. This check is at both the application and database level (unique constraint).
5. **YouTube API — video pages**: The `/playlistItems` endpoint is called in a `while True` loop, fetching up to 50 items per page. The loop terminates when `nextPageToken` is absent. Private and deleted videos (identified by title matching `"Deleted video"` or `"Private video"`) are skipped.
6. **Database insertion**: `session.add_all(videos_to_insert)` performs a single bulk insert for efficiency.
7. **Quiz scheduling**: The `_build_quiz_schedule` helper places Quiz records after every 3 videos (sequence_order + 0.5), one for the trailing remainder (+ 0.25), and one final quiz (+ 0.75).
8. **Background task**: `background_tasks.add_task` queues `_process_quizzes_sequentially`, which runs each quiz's Ollama generation in a new event loop in a background thread.

## 5.4 Course Generation

Playlist metadata (title, description, YouTube playlist ID) becomes a `Playlist` record (the "course"). Each video entry from the YouTube API becomes a `Video` record with a `sequence_order` integer starting at 1. The course status is derived at query time from the ratio of completed videos to total videos — it is not stored as a static field to avoid inconsistency.

## 5.5 Video Player Integration

The YouTube IFrame Player API is loaded by injecting a `<script>` tag referencing `https://www.youtube.com/iframe_api`. The `useYouTubePlayer` hook wraps the `YT.Player` constructor in a `useEffect`, passing a `containerId` and initial `videoId`. The hook exposes imperative methods: `play()`, `pause()`, `seekTo(seconds)`, `getCurrentTime()`, and `getDuration()`. The `onStateChange` callback propagates player state (playing, paused, ended) back to the parent component to coordinate proctoring.

When the learner selects a different video from the sidebar, `loadVideo(yt_video_id)` is called on the existing player instance, avoiding a full re-mount of the IFrame.

## 5.6 Progress-Tracking Implementation

- A `setInterval` in `CoursePlayerPage` fires every 5 seconds while the video is playing.
- Each tick calls `POST /api/progress/update` with `current_time = player.getCurrentTime()` and `duration = player.getDuration()`.
- The backend fetches the `UserProgress` record (creating one if absent), runs the order checks, runs the seek check, updates `last_watched_second` and `highest_watched_second`, and checks for completion.
- If `highest_watched_second >= duration - 15` and the video is not yet completed, the backend sets `is_completed = True`, credits 50 XP, recalculates the level, appends to `xp_log`, and returns the updated XP in the response.
- The frontend receives the response and updates local state: if `allowed == false`, it calls `seekTo(seek_to)` to roll the player back.
- On returning to a course, the `last_watched_second` from the API response is passed to `seekTo()` to resume automatically.

## 5.7 Dashboard Implementation

On mount, `DashboardPage` fires two parallel API requests using `Promise.all`: `GET /api/users/me` for XP, level, and streak, and `GET /api/playlists` for all courses. The playlists endpoint performs aggregate calculations in the backend (completed video count, progress percentage, thumbnail URL, last-accessed date) so the frontend only renders what it receives.

The XP progress bar within the "Current Level" card is calculated as `(total_xp / (current_level × 500)) × 100`. The import modal uses the browser `URL` API for client-side playlist ID extraction before making any network call, providing immediate validation feedback.

## 5.8 Error Handling

- **Frontend validation**: The import modal validates URL format and presence of the `list` parameter before calling the backend.
- **Axios interceptor**: `auth.ts` registers a response error interceptor that calls `toast.error(message)` for all non-401 errors, providing a global notification for backend errors without requiring per-component error handling.
- **Backend validation**: Pydantic automatically validates all request bodies. FastAPI returns HTTP 422 with detailed field error messages for malformed requests.
- **Global exception handler**: A FastAPI `exception_handler(Exception)` catches unhandled exceptions and returns HTTP 500 with a generic message, preventing raw stack trace exposure.
- **Empty states**: The dashboard renders a dashed-border empty state with a prompt to import when the playlist list is empty. The quiz view renders a countdown timer and retry button when the quiz status is `generating`.
- **Proctoring errors**: If camera permission is denied, `useProctoring` sets status to `"denied"` and the `WebcamPermissionGate` component displays an explanatory message. The learner can proceed without proctoring.

## 5.9 Key Implementation Challenges

**Challenge 1: Async background tasks calling an async function**
- **Problem**: FastAPI's `BackgroundTasks` runs callbacks in a thread pool executor. The quiz generation function `generate_quiz_pool_background` is `async`. Calling an async function from a synchronous background thread fails.
- **Why it occurred**: FastAPI's `BackgroundTasks` does not manage an event loop; it runs the function in the existing thread pool where no event loop is present.
- **Solution**: The wrapper `_process_quizzes_sequentially` creates a new event loop (`asyncio.new_event_loop()`), sets it as the current loop, and calls `loop.run_until_complete()` for each quiz task. The loop is closed in a `finally` block.

**Challenge 2: LLM JSON output inconsistency**
- **Problem**: The Ollama model's JSON output varied across runs: sometimes wrapped in markdown fences, sometimes nested in a dict key, sometimes with trailing commas.
- **Why it occurred**: LLMs are probabilistic; the format instruction in the prompt is not strictly enforced.
- **Solution**: A multi-strategy JSON extraction function (`_extract_json_array`) attempts five parsing strategies in sequence: direct parse, markdown-stripped parse, regex extraction of the first `[...]` block, trailing-comma repair, and combined transformations.
- **Remaining limitation**: Severely malformed output (e.g., truncated mid-question) cannot be recovered and results in a lower-than-expected question count.

**Challenge 3: MediaPipe GPU delegate initialisation time**
- **Problem**: Loading the FaceLandmarker model from CDN and initialising the GPU delegate takes 3–8 seconds the first time, during which the video may already be playing.
- **Why it occurred**: The MediaPipe WASM runtime and model file (~4 MB) are fetched from external CDNs and compiled at runtime.
- **Solution**: The `WebcamPermissionGate` component fully blocks video playback until proctoring reaches `status === "active"`. The learner sees a loading state with a spinner during this initialisation.

**Challenge 4: CockroachDB connection string format on Windows**
- **Problem**: CockroachDB requires the connection string to start with `cockroachdb://` rather than `postgresql://`. On Windows, SSL certificate verification requires `&sslrootcert=system` appended to the URL.
- **Why it occurred**: CockroachDB uses the system certificate store on Windows rather than a bundled certificate file.
- **Solution**: This is documented explicitly in `backend/.env.example` and the README with step-by-step instructions.

---

# Chapter 6 — Testing and Security Analysis

## 6.1 Testing Strategy

- **Unit testing**: Business logic functions (XP calculation, level formula, quiz pass threshold, question validation) tested in isolation without database or HTTP calls.
- **Integration testing**: FastAPI `TestClient` tests validate the full request-response cycle including middleware, dependency injection, and database interaction.
- **Mocked unit testing**: LLM generation functions are tested with mocked `httpx.AsyncClient` responses to validate JSON parsing without requiring a live Ollama instance.
- **Manual API testing**: All endpoints were manually tested using Postman and curl during development.
- **Manual UI testing**: The React frontend was tested in Chromium-based browsers on desktop and tablet viewports.
- **Security testing**: Ownership checks and sequential locking were tested by manually constructing requests for resources belonging to a different user.

## 6.2 Functional Test Cases

**Table 7: Functional Test Cases**

| Test ID | Feature | Input | Expected Result | Status |
|---|---|---|---|---|
| TC-01 | Registration — valid | New email, valid password | 200: user created | Pass |
| TC-02 | Registration — duplicate | Existing email | 400: email already registered | Pass |
| TC-03 | Login — valid credentials | Correct email and password | 200: JWT token returned | Pass |
| TC-04 | Login — wrong password | Correct email, wrong password | 400: incorrect credentials | Pass |
| TC-05 | Protected endpoint — no token | GET /api/users/me, no auth header | 401: unauthorised | Pass |
| TC-06 | Protected endpoint — valid token | GET /api/users/me, valid JWT | 200: user profile | Pass |
| TC-07 | Playlist import — valid public playlist | Valid playlist URL | 200: course created | Pass |
| TC-08 | Playlist import — duplicate | Same playlist URL as existing | 400: already imported | Pass |
| TC-09 | Playlist import — private playlist | URL to private playlist | 404: not found | Pass |
| TC-10 | Progress update — first video, in order | current_time=60, duration=600 | 200: allowed=true | Pass |
| TC-11 | Progress update — seek ahead | current_time=300, highest=60, buffer=15 | 200: allowed=false, seek_to=60 | Pass |
| TC-12 | Progress update — second video, first not done | Video 2 progress, Video 1 incomplete | 403: previous video not completed | Pass |
| TC-13 | Video completion — reaches end | current_time=592, duration=600 | 200: completed=true, xp_awarded=50 | Pass |
| TC-14 | Level up | total_xp crosses 500 threshold | current_level incremented | Pass |
| TC-15 | Quiz start — ready quiz | GET /start with ready quiz ID | 200: 30 questions returned | Pass |
| TC-16 | Quiz start — generating quiz | GET /start with generating quiz ID | 200: status=generating, eta_seconds | Pass |
| TC-17 | Quiz submit — pass | 21/30 correct (70%) | 200: passed=true | Pass |
| TC-18 | Quiz submit — fail | 15/30 correct (50%) | 200: passed=false | Pass |
| TC-19 | Course deletion | DELETE /api/playlists/{id} | 200: removed; all related records deleted | Pass |
| TC-20 | Ownership violation | User A's token accessing User B's playlist | 404 / 403 | Pass |

## 6.3 API Testing

**Table 8: API Testing Scenarios**

| Scenario | Method | Endpoint | Expected HTTP Code | Result |
|---|---|---|---|---|
| Register with missing email field | POST | /api/auth/register | 422 | Pass |
| Login with form body as JSON | POST | /api/auth/login | 422 | Pass |
| Access playlist of another user | GET | /api/playlists/{other_user_playlist_id}/videos | 404 | Pass |
| Submit quiz with invalid attempt_id | POST | /api/quizzes/{id}/submit | 400 | Pass |
| Progress update for video not in user's playlist | POST | /api/progress/update | 403 | Pass |
| Import with missing YouTube API key (env unset) | POST | /api/ingest/playlist | 500 | Pass |
| Delete non-existent playlist | DELETE | /api/playlists/{random_uuid} | 404 | Pass |
| Submit expired JWT | GET | /api/users/me | 401 | Pass |

## 6.4 Usability and Responsive Testing

The application was tested on the following configurations:

- **Desktop (1920×1080, Chrome 126)**: All pages render correctly. Dashboard grid shows two columns of course cards. Course player shows full sidebar and player.
- **Tablet (1024×768, Chrome mobile emulation)**: Dashboard grid collapses to single column. Course player sidebar scrolls independently.
- **Mobile (390×844, Chrome mobile emulation)**: Navigation and auth pages are fully usable. Dashboard and course player are functional but suboptimal — the split-panel layout on the player is too compressed. This is noted as a known limitation.
- **Dark/light mode**: Verified on all pages. CSS custom properties for `--background`, `--foreground`, and component tokens update correctly on toggle.
- **Loading states**: All API-dependent pages show a spinner (`Loader2` from Lucide) while data is fetching.
- **Empty states**: Dashboard empty state, quiz generating state, and webcam permission denied state all render appropriate messages.

## 6.5 Security Findings

**Table 9: Security Findings and Resolutions**

| ID | Finding | Severity | Resolution | Status |
|---|---|---|---|---|
| SF-01 | JWT secret was set to a default fallback `"fallback-secret-key"` in early development | High | Default removed from production path; env var is required | Resolved |
| SF-02 | Progress update endpoint did not verify quiz completion order in initial implementation | High | Prior quiz check added: all quizzes before the current video's sequence_order must have a passed attempt | Resolved |
| SF-03 | `/api/playlists` returned all playlists in the database in an early implementation | High | WHERE clause `Playlist.user_id == current_user.id` added | Resolved |
| SF-04 | Quiz submit returned correct option index in the response to aid debugging | Medium | `correct_option_index` removed from all quiz question responses | Resolved |
| SF-05 | CORS `allow_origins=["*"]` was set during initial development | Medium | Replaced with specific `FRONTEND_URL` environment variable | Resolved |
| SF-06 | Backend error responses included Python traceback strings | Low | Global exception handler added; only generic message returned | Resolved |
| SF-07 | YouTube API key logged to console during debug phase | Low | All API key logging removed; key is accessed only through `os.getenv()` | Resolved |

## 6.6 Security Measures Implemented

1. **Argon2id password hashing** via `passlib[argon2]` — memory-hard, GPU-resistant.
2. **JWT authentication** with 24-hour expiry and server-side user re-validation per request.
3. **Ownership verification** on every playlist and progress endpoint.
4. **Sequential order enforcement** entirely server-side — cannot be bypassed by frontend manipulation.
5. **Quiz answer server-side scoring** — correct answers are fetched from the database, never sent to the client.
6. **Pydantic input validation** on all request bodies — rejects malformed input before business logic.
7. **CORS restriction** to the configured frontend origin only.
8. **Environment variable protection** — all secrets in `.env` files excluded from version control via `.gitignore`.
9. **Generic error messages** for 500-class errors to avoid internal information disclosure.

## 6.7 Defects and Resolutions

**Table 10: Defects and Resolutions**

| ID | Description | Severity | Resolution | Status |
|---|---|---|---|---|
| BUG-01 | `generate_quiz_pool_background` (async) called without event loop in background thread | Critical | `asyncio.new_event_loop()` wrapper added in `_process_quizzes_sequentially` | Resolved |
| BUG-02 | `DetachedInstanceError` when accessing `quiz.id` after session commit | High | Quiz IDs extracted into `quiz_tasks` list before `session.commit()` | Resolved |
| BUG-03 | Daily streak incremented on every request, not once per day | High | Login-only streak update; streak logic moved solely to `POST /api/auth/login` | Resolved |
| BUG-04 | XP awarded multiple times if frontend sent rapid duplicate progress calls at completion boundary | Medium | `if not progress.is_completed` guard prevents re-awarding XP on already-completed videos | Resolved |
| BUG-05 | Course player crashed if YouTube API returned a video with no `resourceId` field | Medium | `.get()` with safe defaults applied to all YouTube metadata field accesses | Resolved |
| BUG-06 | MediaPipe FaceLandmarker crashed when video element was not yet at `readyState >= 2` | Low | Guard `if vid.readyState < 2` added in the detection loop | Resolved |
| BUG-07 | Quiz attempt created even when quiz had 0 questions (error state) | Low | Question count check ensures at least one question exists before creating an attempt | Resolved |

---

# Chapter 7 — Deployment and User Guide

## 7.1 Deployment Architecture

```
[Learner Browser]
      |
      | HTTPS
      v
[Frontend: Static Host (e.g., Vercel)]
      |
      | HTTPS REST API
      v
[Backend: ASGI Host (e.g., Railway / Render)]
      |                        |
      | TLS/SQL                | HTTPS
      v                        v
[CockroachDB Serverless]  [YouTube Data API v3]

[Ollama: Local Machine] <--- Background task from Backend
```

In the current development setup, all components except CockroachDB run on the developer's local machine. The frontend connects to `http://localhost:8000`; the backend connects to CockroachDB via a TLS-secured connection string.

## 7.2 Environment Configuration

All secrets are stored in `backend/.env`. The following variables are required:

```
DATABASE_URL=cockroachdb://<username>:<password>@<host>:26257/defaultdb?sslmode=verify-full&sslrootcert=system
SECRET_KEY=<64-character random hex string>
YOUTUBE_API_KEY=<YouTube Data API v3 key>
FRONTEND_URL=http://localhost:5173
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen2.5:3b
```

Generate the secret key with:
```
python -c "import secrets; print(secrets.token_hex(32))"
```

## 7.3 Local Installation Instructions

**Prerequisites:**
- Python 3.11 or 3.12
- Node.js v20 LTS or v22 LTS
- Ollama (https://ollama.com/download)
- Git

**Step 1 — Clone the repository**
```bash
git clone https://github.com/<org>/summer_intern_group-a.git
cd summer_intern_group-a
```

**Step 2 — Backend setup**
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
# Edit .env and fill in all required values
```

**Step 3 — Frontend setup**
```bash
cd ../frontend
npm install
```

**Step 4 — Pull the Ollama model**
```bash
ollama pull qwen2.5:3b
```

**Step 5 — Start the backend** (Terminal 1, venv active)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Step 6 — Start the frontend** (Terminal 2)
```bash
cd frontend
npm run dev
```

**Step 7 — Verify** (Terminal 3, venv active)
```bash
cd backend
pytest tests/ -v --tb=short

cd ../frontend
npm run verify
```

Visit `http://localhost:5173` to access the application.

## 7.4 User Guide

**1. Creating an account**
- Navigate to `http://localhost:5173/register`.
- Enter your email address and a password.
- Click "Create Account".

**2. Logging in**
- Navigate to `http://localhost:5173/login`.
- Enter your registered email and password.
- Click "Sign in". You will be redirected to the dashboard.

**3. Importing a playlist**
- On the dashboard, click the "Import Playlist" button.
- Open YouTube, navigate to the playlist you want to import, and copy the page URL (it must contain `?list=`).
- Paste the URL into the input field and click "Import Course".
- The course appears on the dashboard once ingestion is complete.

**4. Opening a course**
- Click the "Continue" button on any course card on the dashboard.
- The course player page opens, showing the video list in the left sidebar.

**5. Starting a lesson**
- Click the first video in the sidebar (it will be unlocked by default).
- If prompted, grant webcam permission for attention monitoring, or dismiss the gate to watch without proctoring.
- The video loads in the embedded player. Click play.

**6. Resuming a lesson**
- If you have previously watched part of a video, the player will automatically seek to your last saved position when you select the video from the sidebar.

**7. Tracking progress**
- The progress bar on each course card on the dashboard updates after each session.
- The completion fraction (e.g., "3 / 12 completed") is shown below the progress bar.
- Your XP total, level, and streak are shown in the three stat cards at the top of the dashboard.

**8. Unlocking the next lesson**
- Watch the current video until the player reaches within 15 seconds of the end. The backend will mark it as complete and award 50 XP.
- The next video (or quiz) in the sidebar will become unlocked automatically. Refresh the sidebar if needed.

**9. Taking a quiz**
- When you reach a quiz checkpoint in the sidebar, click it to open the quiz view.
- If the quiz is still being generated by the AI, you will see a countdown timer. Check back when the timer expires.
- Answer all 30 questions and click "Submit Quiz".
- You need 70% (21/30) correct answers to pass. If you fail, you can retake with a different set of 30 questions from the pool.

**10. Removing a course**
- On the dashboard, click the trash icon on the course card you wish to remove.
- Confirm in the modal. All associated videos, progress records, and quiz data are permanently deleted.

## 7.5 Screenshots

*Note: Screenshots are to be captured from the running application and inserted here with labels as Figures 8–14 in the final submitted report.*

- **Figure 8** — Registration page showing the animated background, email/password fields, and "Create Account" button.
- **Figure 9** — Login page with glassmorphic card, dark mode active.
- **Figure 10** — Dashboard showing three stat cards (XP, Level, Streak), course cards with progress bars, and "Import Playlist" button.
- **Figure 11** — Import Playlist modal with YouTube URL input field.
- **Figure 12** — Course player showing video embed, sidebar with locked/unlocked/completed items, webcam PiP.
- **Figure 13** — Quiz interface showing 30 MCQs with selectable option buttons and submit bar.
- **Figure 14** — Webcam proctoring overlay when attention is lost.

---

# Chapter 8 — Results and Evaluation

## 8.1 Features Completed

**Table 11: Feature Completion Status**

| Feature | Planned | Implemented | Tested | Remarks |
|---|---|---|---|---|
| User Registration | Yes | Yes | Yes | Full Argon2 hashing |
| JWT Login | Yes | Yes | Yes | 24-hour expiry |
| YouTube Playlist Import | Yes | Yes | Yes | Pagination supported |
| Sequential Video Unlocking | Yes | Yes | Yes | Enforced server-side |
| Playback Progress Tracking | Yes | Yes | Yes | Per-second granularity |
| Resume from Last Position | Yes | Yes | Yes | On video selection |
| Seek-Ahead Prevention | Yes | Yes | Yes | 15-second buffer |
| XP Awarding | Yes | Yes | Yes | 50 XP per video |
| Levelling System | Yes | Yes | Yes | Level = (XP÷500)+1 |
| Daily Login Streak | Yes | Yes | Yes | Day-boundary detection |
| AI Quiz Generation (Ollama) | Yes | Yes | Partial | Quality varies by model |
| Sequential Quiz Unlocking | Yes | Yes | Yes | Mixed with video sequence |
| Quiz Random Sampling (30/60) | Yes | Yes | Yes | Per attempt |
| 70% Pass Threshold | Yes | Yes | Yes | Server-side scoring |
| Webcam Proctoring (MediaPipe) | Yes | Yes | Partial | FPS varies by hardware |
| Dashboard with Progress | Yes | Yes | Yes | Thumbnail, status, last-accessed |
| Course Deletion (cascade) | Yes | Yes | Yes | Full cascade in DB |
| Dark/Light Theme | Yes | Yes | Yes | System-level toggle |
| Responsive Layout | Partial | Partial | Partial | Mobile experience suboptimal |

## 8.2 Requirement Traceability

**Table 12: Requirement Traceability Matrix (Sample)**

| Req ID | Requirement | Implemented | Test ID | Status |
|---|---|---|---|---|
| FR-01 | User registration | Yes | TC-01, TC-02 | Verified |
| FR-02 | User login + JWT | Yes | TC-03, TC-04 | Verified |
| FR-03 | Import public playlist | Yes | TC-07, TC-08 | Verified |
| FR-09 | Save playback progress | Yes | TC-10, TC-11 | Verified |
| FR-10 | Sequential lesson unlocking | Yes | TC-12 | Verified |
| FR-11 | Seek-ahead prevention | Yes | TC-11 | Verified |
| FR-12 | Mark video as completed | Yes | TC-13 | Verified |
| FR-13 | Award 50 XP per video | Yes | TC-13 | Verified |
| FR-16 | Quiz every 3 videos + final | Yes | Manual | Verified |
| FR-17 | 60-question pool via Ollama | Yes | Unit test (mocked) | Verified |
| FR-19 | 70% pass threshold | Yes | TC-17, TC-18 | Verified |
| FR-21 | Webcam attention detection | Yes | Manual | Verified |
| FR-24 | Course deletion cascade | Yes | TC-19 | Verified |
| FR-25 | Data isolation between users | Yes | TC-20, SF-03 | Verified |

## 8.3 System Demonstration Results

- **Playlist import**: A 15-video public programming tutorial playlist was imported in under 4 seconds. The course appeared immediately on the dashboard with correct title, thumbnail, and video count.
- **Lesson order**: All 15 videos appeared in the sidebar in the exact order defined in the YouTube playlist.
- **Progress saving**: Progress updates were confirmed in the database after every 5-second interval. The `highest_watched_second` field advanced monotonically.
- **Resume**: Closing the browser and reopening the course correctly resumed the video at the last saved position.
- **Sequential unlocking**: Video 2 was inaccessible (locked icon, 403 response on progress update) until Video 1 was completed.
- **XP and level**: Completing Video 1 awarded 50 XP. After completing 10 videos (500 XP), the level automatically advanced from 1 to 2.
- **Quiz generation**: Quizzes for a 3-video group using `qwen2.5:3b` generated 55–60 valid questions in approximately 4–6 minutes on an RTX 3050 (4 GB VRAM).
- **Quiz scoring**: Correct answers stored in the database matched the displayed options. Submitting 21/30 correct returned `passed: true`.
- **User isolation**: Attempting to access another user's playlist ID with a valid JWT for a different user returned HTTP 404.

## 8.4 Performance Observations

| Metric | Observed Value | Notes |
|---|---|---|
| Playlist import (15 videos) | ~3.5 seconds | Dominated by YouTube API round-trips |
| Dashboard initial load | ~800 ms | Two parallel API calls |
| Course page load | ~600 ms | Single API call |
| Progress update response | ~120–180 ms | CockroachDB round-trip (cloud) |
| Quiz generation (3 videos, qwen2.5:3b, RTX 3050) | ~4–6 minutes | 5 batches × 12 questions |
| Proctoring detection frame rate | ~14–15 fps | Throttled to protect CPU |
| MediaPipe initialisation | ~4–7 seconds | First load; CDN + WASM compile |

## 8.5 Known Issues

| Issue | Impact | Workaround | Reason Unresolved |
|---|---|---|---|
| Mobile layout suboptimal on course player page | Minor — layout compressed | Use desktop or tablet | Scope limitation during internship |
| Quiz quality varies with video transcript quality | Some quizzes contain generic questions | Use playlists with good auto-captions | Inherent LLM limitation |
| MediaPipe loads from CDN — fails if CDN is unreachable | Proctoring unavailable | Student can proceed without proctoring | Bundling WASM locally increases build size significantly |
| Videos without embedding enabled show a player error | Student cannot watch those videos in the LMS | Open them directly on YouTube | YouTube uploader restriction; cannot be bypassed |
| Final quiz covers entire playlist; for long playlists transcripts are truncated | Final quiz may not cover all videos | Limitation acknowledged | Context window constraint of LLM |

---

# Chapter 9 — Limitations and Future Scope

## 9.1 Limitations

1. **YouTube API dependency**: All content metadata and playback depend on YouTube's availability and API quotas. A quota exhaustion or YouTube service outage renders the import feature non-functional.
2. **API quota ceiling**: The default 10,000 daily unit quota limits the number of playlists that can be imported per day at scale.
3. **Deleted and private videos**: Videos that become unavailable after import remain in the course structure but cannot be played. There is no mechanism to detect this automatically.
4. **Embedding restrictions**: Some video creators disable embedding. Affected videos show a YouTube error inside the player; there is no fallback.
5. **Transcript dependency for quizzes**: Videos without auto-generated captions cannot have AI quizzes generated. The quiz status is set to `error_no_transcript` and the quiz is skipped in the unlocking sequence.
6. **Local LLM requirement**: Ollama must run on the developer's local machine. There is no cloud-hosted quiz generation. This makes the system unsuitable for multi-user cloud deployment without significant additional infrastructure.
7. **No instructor functionality**: Courses can only be created by importing public playlists. There is no mechanism for an instructor to create structured content independently.
8. **No genuine attention proof**: The webcam proctoring system detects head pose but cannot verify genuine comprehension. A learner could look at the screen while not paying attention.
9. **No offline support**: The application requires a constant internet connection for both video streaming and API calls.
10. **Mobile experience**: The course player's split-panel layout is not optimised for small screen sizes.

## 9.2 Future Scope

1. **Cloud-hosted LLM inference**: Replace local Ollama with a cloud inference API (e.g., Google Gemini, OpenAI GPT-4o-mini) to enable multi-user quiz generation without local hardware constraints.
2. **AI-generated video summaries**: Use LLMs to produce a structured summary of each video's key concepts, displayed below the player.
3. **Automatic transcript processing and topic extraction**: Identify the main topics from transcripts to generate targeted quiz questions and tag videos with subject labels.
4. **Certificates**: Generate verifiable course completion certificates on 100% course completion.
5. **Instructor dashboard**: Allow educators to create curated playlists, add supplementary materials, and monitor learner cohort progress.
6. **Advanced analytics**: Track time spent per video, quiz attempt history, performance trends, and retention curves per learner.
7. **Collaborative learning**: Discussion threads attached to each video, peer review of quiz answers, and cohort-level leaderboards.
8. **Mobile application**: Native iOS and Android applications with offline video caching for downloaded content.
9. **Spaced repetition review**: Automatically resurface incorrectly answered quiz questions using the SM-2 algorithm to strengthen retention.
10. **Multiple learning paths**: Allow a learner to associate multiple playlists into a structured learning path with prerequisite dependencies.
11. **Institutional administration**: Multi-tenant support with organisation-level reporting, bulk learner enrollment, and SSO integration.
12. **Stale playlist synchronisation**: Periodically re-fetch playlist metadata from YouTube to detect and handle deleted, reordered, or newly added videos.

---

# Chapter 10 — Conclusion

This project addressed the problem of unstructured, untracked YouTube playlist learning by developing a Gamified Learning Management System that converts any public playlist into a structured, progress-tracked course. The core problem — that self-directed learners using YouTube playlists have no measurable progress, no accountability, and no sustained engagement incentive — was directly resolved through sequential lesson locking, second-precision progress tracking with resume functionality, and a gamification layer comprising XP, levels, and daily streaks.

The developed system successfully delivers all planned MVP features. A user can register, import a YouTube playlist, watch videos in enforced sequential order, have their progress saved continuously, earn XP on completion, and take AI-generated quizzes that must be passed before advancing. An optional webcam proctoring layer adds a further accountability dimension. The dashboard provides a unified view of all courses with real-time progress and status.

The principal technical contributions are: a robust quiz generation pipeline that fetches transcripts, generates a 60-question pool through a local LLM, applies multi-strategy JSON extraction, deduplicates across batches, and marks quizzes ready for serving; a seek-prevention mechanism enforced entirely server-side; and a head-pose estimation proctoring system using MediaPipe Face Landmarker running at 15 fps in the browser.

Testing confirmed that all 25 functional requirements are implemented and that the 7 significant bugs identified during development were resolved. Security analysis identified and resolved 7 vulnerabilities, including CORS misconfiguration, missing ownership checks, and JWT default key risk.

The current principal limitations are the dependency on YouTube's API quotas and transcript availability, and the requirement for a locally-running Ollama instance for quiz generation. These constrain the system to a well-resourced development environment and a motivated learner audience using playlists with good auto-captioning.

Overall, the project achieves its stated objective: it produces a functional, tested, and deployable MVP that transforms informal YouTube viewing into a structured gamified learning experience.

---

# References

1. Google LLC. *YouTube Data API v3 Reference*. https://developers.google.com/youtube/v3/docs
2. Google LLC. *YouTube IFrame Player API Reference*. https://developers.google.com/youtube/iframe_api_reference
3. Google LLC. *YouTube API Services Terms of Service*. https://developers.google.com/youtube/terms/api-services-terms-of-service
4. Ramírez, S. *FastAPI Documentation*. https://fastapi.tiangolo.com/
5. Ramírez, S. *SQLModel Documentation*. https://sqlmodel.tiangolo.com/
6. Meta Open Source. *React Documentation*. https://react.dev/
7. Evan You et al. *Vite Documentation*. https://vitejs.dev/guide/
8. Tailwind Labs. *Tailwind CSS v4 Documentation*. https://tailwindcss.com/docs
9. CockroachDB Inc. *CockroachDB Documentation*. https://www.cockroachlabs.com/docs/
10. Ollama Inc. *Ollama Documentation*. https://ollama.com/docs
11. Google LLC. *MediaPipe Tasks Vision — Face Landmarker*. https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker
12. Alibaba Cloud. *Qwen2.5 Technical Report*. https://qwenlm.github.io/blog/qwen2.5/
13. Biryukov, A. et al. *Argon2: the memory-hard function for password hashing and other applications*. PHC Winner, 2015. https://www.password-hashing.net/argon2-specs.pdf
14. Jones, M., Bradley, J., and Sakimura, N. *RFC 7519 — JSON Web Token (JWT)*. IETF, 2015. https://datatracker.ietf.org/doc/html/rfc7519
15. JulianGaal. *youtube-transcript-api*. https://github.com/jdepoix/youtube-transcript-api
16. Encode. *httpx — A next generation HTTP client for Python*. https://www.python-httpx.org/
17. Encode. *Starlette Documentation*. https://www.starlette.io/
18. Pydantic. *Pydantic v2 Documentation*. https://docs.pydantic.dev/

---

# Project Artefacts

| Artefact | Location |
|---|---|
| **GitHub Repository** | https://github.com/\<org\>/summer_intern_group-a |
| **Deployed Application** | *(To be added upon deployment)* |
| **API Interactive Docs** | http://localhost:8000/docs (Swagger UI, when running locally) |
| **Demonstration Video** | *(To be added)* |
| **Final Release Tag** | `v1.0.0-mvp` |
| **README** | `/README.md` in repository |
| **Installation Guide** | Chapter 7.3 of this report and `/README.md` |
| **Test Credentials (local)** | Register any email; no shared credentials exist |

> **Note**: The GitHub repository is the primary implementation artefact. This report references source file paths relative to the repository root. Screenshots referenced as Figures 8–14 should be captured from the running application and inserted at the relevant positions in the final submitted document.
