# Deployment Guide

This guide covers everything you need to know to deploy the LMS application (Frontend + Backend + Database).

## 1. Database (CockroachDB)

The backend expects a PostgreSQL-compatible database. We recommend [CockroachDB Serverless](https://www.cockroachlabs.com/) since it offers a generous free tier.

1. Create a free cluster on CockroachDB Cloud.
2. Get the connection string (make sure you select the format with the password).
3. Important: Ensure the connection string starts with `cockroachdb://` instead of `postgresql://` and includes `?sslmode=verify-full&sslrootcert=system` at the end (for Windows/local usage, the rootcert parameter is sometimes necessary).

## 2. Backend Deployment

You can deploy the backend on platforms like [Render](https://render.com), [Railway](https://railway.app/), or [Heroku](https://heroku.com/).

### Required Environment Variables
Set the following environment variables in your hosting provider's dashboard:
- `DATABASE_URL`: Your CockroachDB connection string.
- `SECRET_KEY`: A 64-character random hex string.
- `YOUTUBE_API_KEY`: Your YouTube Data API v3 key.
- `LLM_PROVIDER`: Set to `groq` since cloud hosting providers generally don't have GPUs for Ollama.
- `GROQ_API_KEY`: Your Groq API key.
- `GROQ_MODEL`: `llama-3.1-8b-instant` (or your preferred Groq model).
- `FRONTEND_URL`: The URL of your deployed frontend (e.g., `https://my-lms-app.vercel.app`).

### Build & Start Commands
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** The provided `Procfile` uses `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`. If your platform allows specifying a custom start command, use that.

## 3. Frontend Deployment

We recommend deploying the frontend on [Vercel](https://vercel.com/) or [Netlify](https://netlify.com/).

### Required Environment Variables
- `VITE_API_URL`: The URL of your deployed backend (e.g., `https://my-lms-backend.onrender.com`).

### Build Settings
- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Root Directory:** `frontend` (if deploying from a monorepo, configure the root directory to be `frontend`).

## Notes on Migrations
The backend uses `SQLModel.metadata.create_all(engine)` on startup to create tables. Note that this command **does not** handle schema migrations for existing tables (e.g., adding a new column). For structural changes to an existing database, you will need to apply the changes manually or reset the tables if you are just starting out.
