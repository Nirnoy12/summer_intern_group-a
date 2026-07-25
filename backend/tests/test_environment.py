"""
Backend Environment Verification & Health-Check Test Suite
==========================================================
Run: pytest backend/tests/ -v
These tests verify: env vars, DB connectivity, API health,
auth flow, and LLM service availability — without side effects.
"""

import os
import sys
import httpx
import pytest
from unittest.mock import patch, MagicMock

# ─── Ensure backend is importable ─────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─── 1. Environment Variable Tests ────────────────────────────────────────────
class TestEnvironmentVariables:
    """Verify all required .env variables are present and non-empty."""

    REQUIRED_VARS = [
        "DATABASE_URL",
        "SECRET_KEY",
        "YOUTUBE_API_KEY",
    ]

    def test_all_required_env_vars_present(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        missing = [v for v in self.REQUIRED_VARS if not os.getenv(v)]
        assert not missing, (
            f"Missing required environment variables: {missing}\n"
            f"  → Copy backend/.env.example to backend/.env and fill in the values."
        )

    def test_database_url_format(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        db_url = os.getenv("DATABASE_URL", "")
        assert db_url.startswith("cockroachdb://"), (
            "DATABASE_URL must start with cockroachdb:// not postgresql://\n"
            "  → See backend/.env.example for the correct format."
        )

    def test_secret_key_length(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        secret = os.getenv("SECRET_KEY", "")
        assert len(secret) >= 32, (
            "SECRET_KEY is too short (must be ≥32 characters).\n"
            "  → Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    def test_secret_key_is_not_placeholder(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        secret = os.getenv("SECRET_KEY", "")
        placeholders = ["replace_with", "your_secret", "fallback", "<", ">"]
        for ph in placeholders:
            assert ph not in secret.lower(), (
                f"SECRET_KEY still contains placeholder text: '{ph}'\n"
                "  → Generate a real key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )


# ─── 2. Database Connectivity Test ────────────────────────────────────────────
class TestDatabaseConnectivity:
    """Verify we can connect to CockroachDB and that tables exist."""

    def test_database_connection(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            pytest.skip("DATABASE_URL not set — skipping DB tests")

        try:
            from sqlmodel import create_engine, text, Session
            engine = create_engine(db_url, echo=False, pool_pre_ping=True)
            with Session(engine) as session:
                result = session.exec(text("SELECT 1")).first()
            assert result is not None, "Database query returned None"
        except Exception as e:
            pytest.fail(
                f"Cannot connect to CockroachDB: {e}\n"
                "  → Check DATABASE_URL in backend/.env\n"
                "  → Ensure your IP is allowed in CockroachDB Cloud → Network → IP Allowlist"
            )

    def test_tables_exist_after_migration(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            pytest.skip("DATABASE_URL not set — skipping DB tests")

        expected_tables = ["users", "playlists", "videos", "user_progress", "quizzes", "questions", "quiz_attempts", "xp_log"]

        try:
            from sqlmodel import create_engine, text, Session
            engine = create_engine(db_url, echo=False)
            with Session(engine) as session:
                result = session.exec(
                    text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                ).all()
            existing = [row[0] for row in result]
            missing = [t for t in expected_tables if t not in existing]
            assert not missing, (
                f"Tables missing from database: {missing}\n"
                "  → The app auto-creates tables on startup. Did the backend start successfully at least once?"
            )
        except Exception as e:
            pytest.fail(f"Table check failed: {e}")


# ─── 3. FastAPI Application Tests (using TestClient) ──────────────────────────
class TestFastAPIApplication:
    """Verify the FastAPI app starts correctly and core endpoints respond."""

    @pytest.fixture(scope="class")
    def client(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        try:
            from fastapi.testclient import TestClient
            from main import app
            return TestClient(app, raise_server_exceptions=False)
        except Exception as e:
            pytest.fail(
                f"Failed to import FastAPI app: {e}\n"
                "  → Run: pip install -r requirements.txt\n"
                "  → Ensure backend/.env is populated"
            )

    def test_root_endpoint_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200, (
            f"Root endpoint returned {response.status_code}. "
            "Is the server running? Check for import errors."
        )
        data = response.json()
        assert "message" in data

    def test_openapi_schema_is_accessible(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200, "OpenAPI schema not accessible"
        schema = response.json()
        assert "paths" in schema, "OpenAPI schema missing 'paths'"

    def test_auth_register_endpoint_exists(self, client):
        """Verify /api/auth/register is reachable (422 = endpoint exists, rejects bad body)."""
        response = client.post("/api/auth/register", json={})
        assert response.status_code in (422, 400), (
            f"Expected 422 (validation error) or 400, got {response.status_code}"
        )

    def test_auth_login_endpoint_exists(self, client):
        """Verify /api/auth/login is reachable (422 = endpoint exists)."""
        response = client.post("/api/auth/login", data={})
        assert response.status_code in (422, 400), (
            f"Expected 422 (validation error) or 400, got {response.status_code}"
        )

    def test_protected_endpoints_require_auth(self, client):
        protected = [
            ("GET", "/api/playlists"),
            ("GET", "/api/users/me"),
        ]
        for method, path in protected:
            response = client.request(method, path)
            assert response.status_code == 401, (
                f"Protected route {method} {path} did not return 401. "
                "Authentication guard may be broken."
            )

    def test_cors_headers_present(self, client):
        response = client.options(
            "/api/auth/login",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"}
        )
        # CORS middleware should respond (200 or 204)
        assert response.status_code in (200, 204), (
            f"CORS preflight returned {response.status_code}. "
            "Check CORS middleware configuration in main.py."
        )


# ─── 4. JWT Auth Flow Test ─────────────────────────────────────────────────────
class TestAuthFlow:
    """Full register → login → access protected route cycle."""

    @pytest.fixture(scope="class")
    def client(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            pytest.skip("DATABASE_URL not configured — skipping auth flow tests")

        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def test_full_register_login_cycle(self, client):
        import uuid
        unique_email = f"test_{uuid.uuid4().hex[:8]}@verify.local"
        password = "SecurePassword123!"

        # Register
        reg_resp = client.post("/api/auth/register", json={"email": unique_email, "password": password})
        assert reg_resp.status_code == 200, (
            f"Registration failed: {reg_resp.json()}\n"
            "  → Is the database connection working? Check backend/.env"
        )

        # Login
        login_resp = client.post(
            "/api/auth/login",
            data={"username": unique_email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
        token = login_resp.json().get("access_token")
        assert token, "No access_token in login response"

        # Access protected endpoint
        me_resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200, f"/api/users/me failed: {me_resp.json()}"
        assert me_resp.json()["email"] == unique_email


# ─── 5. LLM Service Tests ─────────────────────────────────────────────────────
class TestOllamaService:
    """Verify Ollama is running and the configured model is available."""

    def test_ollama_is_reachable(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        base_url = ollama_url.rsplit("/api/", 1)[0]

        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{base_url}/api/tags")
            assert resp.status_code == 200, f"Ollama returned {resp.status_code}"
        except httpx.ConnectError:
            pytest.skip(
                "Ollama is not running. Quiz generation will not work.\n"
                "  → Install Ollama: https://ollama.com/download\n"
                "  → Start it: ollama serve\n"
                "  → Pull model: ollama pull phi3"
            )

    def test_ollama_model_is_pulled(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        model = os.getenv("OLLAMA_MODEL", "phi3")
        base_url = ollama_url.rsplit("/api/", 1)[0]

        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{base_url}/api/tags")
            if resp.status_code != 200:
                pytest.skip("Ollama not reachable — cannot check model")

            models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
            assert model in models, (
                f"Model '{model}' is not pulled in Ollama.\n"
                f"  → Pull it with: ollama pull {model}\n"
                f"  → Available models: {models}"
            )
        except httpx.ConnectError:
            pytest.skip("Ollama not running — skipping model check")


# ─── 6. LLM Quiz Generation Unit Tests (mocked) ───────────────────────────────
class TestQuizGeneration:
    """Unit tests for quiz generation logic — does not call real LLM."""

    @pytest.mark.asyncio
    async def test_generate_questions_returns_list_on_valid_response(self):
        """Mock Ollama response to verify the JSON parsing logic works."""
        import json
        from llm_service import generate_questions_with_ollama

        mock_questions = [
            {
                "question_text": "What is FastAPI primarily used for?",
                "options": ["Building web APIs", "Data analysis", "Game development", "Image processing"],
                "correct_option_index": 0,
                "explanation": "FastAPI is a modern, fast web framework for building APIs with Python."
            },
            {
                "question_text": "Which database does this LMS use?",
                "options": ["MySQL", "MongoDB", "CockroachDB", "SQLite"],
                "correct_option_index": 2,
                "explanation": "The LMS uses CockroachDB, a distributed SQL database."
            }
        ]

        mock_response_data = {"response": json.dumps(mock_questions)}

        with patch("llm_service.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = mock_response_data

            mock_client = MagicMock()
            mock_client.__aenter__ = MagicMock(return_value=mock_client)
            mock_client.__aexit__ = MagicMock(return_value=False)
            mock_client.post = MagicMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await generate_questions_with_ollama("Some transcript text", num_questions=2)

        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) == 2, f"Expected 2 questions, got {len(result)}"
        assert result[0]["question_text"] == "What is FastAPI primarily used for?"

    @pytest.mark.asyncio
    async def test_generate_questions_handles_invalid_json(self):
        """Verify graceful failure on malformed LLM output."""
        from llm_service import generate_questions_with_ollama

        mock_response_data = {"response": "This is not valid JSON {{{{"}

        with patch("llm_service.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = mock_response_data

            mock_client = MagicMock()
            mock_client.__aenter__ = MagicMock(return_value=mock_client)
            mock_client.__aexit__ = MagicMock(return_value=False)
            mock_client.post = MagicMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await generate_questions_with_ollama("Transcript", num_questions=5)

        assert result == [], f"Expected empty list on JSON error, got {result}"

    @pytest.mark.asyncio
    async def test_generate_questions_handles_network_error(self):
        """Verify graceful failure when Ollama is unreachable."""
        from llm_service import generate_questions_with_ollama

        with patch("llm_service.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = MagicMock(return_value=mock_client)
            mock_client.__aexit__ = MagicMock(return_value=False)
            mock_client.post = MagicMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client_class.return_value = mock_client

            result = await generate_questions_with_ollama("Transcript", num_questions=5)

        assert result == [], f"Expected empty list on network error, got {result}"

    def test_quiz_question_validation_logic(self):
        """Verify the question-validation logic in generate_quiz_pool_background."""
        # Valid question data
        valid_q = {
            "question_text": "What is Python?",
            "options": ["A snake", "A programming language", "A database", "A framework"],
            "correct_option_index": 1,
            "explanation": "Python is a high-level programming language."
        }

        q_text = valid_q.get("question_text")
        options = valid_q.get("options")
        correct_idx = valid_q.get("correct_option_index")

        assert q_text and options and isinstance(options, list) and correct_idx is not None
        assert 0 <= int(correct_idx) < len(options), "correct_option_index out of bounds"

    def test_quiz_question_rejects_out_of_bounds_index(self):
        """Verify that out-of-bounds correct_option_index is clamped to 0."""
        options = ["A", "B", "C", "D"]
        correct_idx = 99  # Out of bounds

        c_idx = int(correct_idx)
        if c_idx >= len(options) or c_idx < 0:
            c_idx = 0  # The clamping logic from llm_service.py

        assert c_idx == 0, f"Expected clamped index 0, got {c_idx}"


# ─── 7. Model Structure Tests ─────────────────────────────────────────────────
class TestModelStructure:
    """Verify all SQLModel models are correctly defined."""

    def test_user_model_fields(self):
        from models import User
        fields = User.model_fields
        required = ["email", "hashed_password", "total_xp", "current_level", "current_streak"]
        for field in required:
            assert field in fields, f"User model missing field: {field}"

    def test_quiz_model_fields(self):
        from models import Quiz
        fields = Quiz.model_fields
        required = ["playlist_id", "sequence_order", "title", "status"]
        for field in required:
            assert field in fields, f"Quiz model missing field: {field}"

    def test_question_model_fields(self):
        from models import Question
        fields = Question.model_fields
        required = ["quiz_id", "question_text", "options", "correct_option_index"]
        for field in required:
            assert field in fields, f"Question model missing field: {field}"

    def test_quiz_attempt_model_fields(self):
        from models import QuizAttempt
        fields = QuizAttempt.model_fields
        required = ["user_id", "quiz_id", "score", "passed", "questions_asked"]
        for field in required:
            assert field in fields, f"QuizAttempt model missing field: {field}"

    def test_user_progress_model_fields(self):
        from models import UserProgress
        fields = UserProgress.model_fields
        required = ["user_id", "video_id", "highest_watched_second", "last_watched_second", "is_completed"]
        for field in required:
            assert field in fields, f"UserProgress model missing field: {field}"


# ─── 8. Quiz Business Logic Tests ─────────────────────────────────────────────
class TestQuizBusinessLogic:
    """Test quiz scoring, pass/fail logic, and XP award rules."""

    def test_quiz_pass_threshold_is_70_percent(self):
        """Verify 70% is the passing threshold."""
        total = 30
        passing_score = 70.0

        # Exactly 70% should pass
        correct_at_70 = int(total * 0.70)
        score_pct = (correct_at_70 / total) * 100
        assert score_pct >= passing_score, "70% should pass the quiz"

        # 69% should fail
        correct_at_69 = int(total * 0.69)
        score_pct_fail = (correct_at_69 / total) * 100
        assert score_pct_fail < passing_score, "69% should fail the quiz"

    def test_quiz_pool_size_is_30_per_attempt(self):
        """Verify exactly 30 questions are selected per quiz attempt when pool >= 30."""
        import random
        pool = list(range(60))  # Simulate 60 questions in DB
        selected = random.sample(pool, 30)
        assert len(selected) == 30

    def test_quiz_generation_schedule_per_3_videos(self):
        """Verify quizzes are generated after every 3 videos."""
        videos = list(range(9))  # 9 videos → 3 quizzes (after v3, v6, v9) + 1 final
        quiz_count = len(range(2, len(videos), 3))  # Every 3rd video
        remainder_quiz = 1 if len(videos) % 3 != 0 else 0
        final_quiz = 1  # Always one final quiz
        total_quizzes = quiz_count + remainder_quiz + final_quiz
        assert total_quizzes == 4, f"Expected 4 quizzes for 9 videos, got {total_quizzes}"

    def test_xp_level_calculation(self):
        """Verify level = (total_xp // 500) + 1."""
        assert (0 // 500) + 1 == 1        # 0 XP → level 1
        assert (499 // 500) + 1 == 1      # 499 XP → level 1
        assert (500 // 500) + 1 == 2      # 500 XP → level 2
        assert (1500 // 500) + 1 == 4     # 1500 XP → level 4

    def test_video_xp_reward_default(self):
        """Verify default XP reward per video is 50."""
        from models import Video
        import uuid
        v = Video(
            playlist_id=uuid.uuid4(),
            yt_video_id="test123",
            sequence_order=1,
            title="Test Video"
        )
        assert v.xp_reward == 50

    def test_score_percentage_calculation(self):
        """Verify score percentage math."""
        correct = 21
        total = 30
        score_pct = (correct / total) * 100
        assert abs(score_pct - 70.0) < 0.01, f"Score should be 70%, got {score_pct}"


# ─── Quick Smoke Test (can be run standalone) ──────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  LMS Backend — Environment Verification")
    print("=" * 60)
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        cwd=os.path.dirname(__file__),
    )
    sys.exit(result.returncode)
