# Contributing to the Gamified LMS Platform

Welcome to the team! This document serves as your complete guide to understanding the project's architecture, technologies, data flow, and exact instructions on how to run the application locally.

## 🛠️ Technology Stack

Our platform is divided into a decoupled Frontend and Backend architecture:

### Frontend (User Interface)
- **Framework**: React 19 with Vite for lightning-fast builds.
- **Language**: TypeScript for type safety.
- **Styling**: Tailwind CSS v4 and `shadcn/ui` components for a modern, glassmorphic, and dynamic design.
- **Routing**: `react-router-dom` for client-side navigation.
- **State/API**: Standard React hooks (`useState`, `useEffect`) and `axios` for API calls.

### Backend (API Server)
- **Framework**: FastAPI (Python 3.10+) for high-performance async endpoints.
- **Database ORM**: SQLModel (built on top of SQLAlchemy and Pydantic).
- **Database Engine**: CockroachDB (Serverless distributed SQL).
- **Authentication**: JWT (JSON Web Tokens) with Argon2 password hashing.
- **External Integrations**: `httpx` for async calls to the YouTube Data API v3.

---

## 🌊 Architecture & Data Flow

Understanding how data moves through the application is critical for contributing effectively. Here is the exact data lifecycle:

### 1. Playlist Ingestion Flow
1. **Trigger**: An admin/user sends a POST request to `/api/ingest/playlist` with a YouTube Playlist ID.
2. **External API**: The FastAPI backend uses `httpx` to call the **YouTube Data API v3**.
3. **Database Write**: The backend parses the YouTube metadata and saves a new `Playlist` record and multiple `Video` records (maintaining sequence order) directly into CockroachDB via SQLModel.

### 2. User Authentication Flow
1. **Register/Login**: The React frontend (`Login.tsx`/`Register.tsx`) sends credentials to `/api/auth/register` or `/api/auth/login`.
2. **Token Generation**: The backend hashes the password (Argon2), saves the `User`, and generates a JWT `access_token`.
3. **Storage**: The frontend stores this token in `localStorage` and attaches it to the `Authorization: Bearer <token>` header for all subsequent API requests.

### 3. Dashboard Data Flow
1. **Initialization**: When a user navigates to `/dashboard`, the React component mounts.
2. **Data Fetching**: `Dashboard.tsx` concurrently calls:
   - `GET /api/users/me` -> Returns `total_xp`, `current_level`, `current_streak`.
   - `GET /api/playlists` -> Returns all available playlists and their video counts.
3. **Rendering**: The UI renders glowing stats and interactive course cards.

### 4. Course Player & Gamification Flow
1. **Video Playback**: In `CoursePlayer.tsx`, the frontend calls `GET /api/playlists/{playlist_id}/videos` to get the list of videos and checks which ones the current user has already completed via the `UserProgress` table.
2. **XP Reward**: When the user finishes a video, they click "Mark as Complete".
3. **Backend Logic**: The frontend sends a `POST /api/progress/complete-video/{video_id}` request.
4. **Database Transaction**: The backend creates a `UserProgress` record, adds a row to `XpLog`, increments the user's `total_xp`, calculates if they leveled up, and commits to CockroachDB. The UI updates instantly.

---

## 🚀 How to Run the Application Locally

Follow these exact steps to get the full stack running on your machine.

### Step 1: Environment Variables Setup
The backend requires certain environment variables to function properly. We have provided a template for you.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Copy the template to create your `.env` file:
   ```bash
   # Windows
   copy .env.example .env
   
   # Mac/Linux
   cp .env.example .env
   ```
3. Open the newly created `.env` file and fill in the required values:
   - **DATABASE_URL**: Ask the Tech Lead (Nirnoy) for the CockroachDB Connection String. Ensure the URL starts with `cockroachdb://`.
   - **SECRET_KEY**: Generate a random secure key by running `python -c "import secrets; print(secrets.token_hex(32))"` and paste it here.
   - **YOUTUBE_API_KEY**: Get a YouTube Data API v3 key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).

### Step 2: Setup Local LLM (Ollama)
The platform uses Ollama to run the `phi3` language model locally for generating quiz questions from transcripts.

1. Download and install [Ollama](https://ollama.com/download) for your operating system.
2. Once installed, open your terminal and pull the model:
   ```bash
   ollama pull phi3
   ```
3. Ensure Ollama is running in the background (default port `11434`).

### Step 3: Start the Backend (FastAPI)
Open your terminal and navigate to the backend folder:
```bash
cd backend
```
Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```
Install the exact required dependencies:
```bash
pip install -r requirements.txt
```
Run the server:
```bash
uvicorn main:app --reload
```
✅ The backend API is now running at `http://127.0.0.1:8000`
✅ Interactive Swagger API Docs available at `http://127.0.0.1:8000/docs`

### Step 4: Start the Frontend (React + Vite)
Open a **new, separate terminal** and navigate to the frontend folder:
```bash
cd frontend
```
Install Node modules:
```bash
npm install
```
Start the Vite development server:
```bash
npm run dev
```
✅ The frontend UI is now running at `http://localhost:5173`

---

## 🔄 Contribution Workflow Rules

1. **Never push to `main` directly.** All work must happen on feature branches (`feature/...`, `fix/...`, `chore/...`).
2. **Sync your fork** with the upstream repository before starting new work.
3. Open a Pull Request (PR) against the manager's repository when your feature is complete.
4. Ensure your frontend code compiles (`npm run build`) and your backend has no syntax errors before opening a PR.