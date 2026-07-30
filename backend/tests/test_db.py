import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestDatabaseConnectivity:
    def test_database_connection(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        db_url = os.getenv("DATABASE_URL")
        if not db_url: pytest.skip("DATABASE_URL not set")
        from sqlmodel import create_engine, text, Session
        with Session(create_engine(db_url, echo=False, pool_pre_ping=True)) as session:
            assert session.exec(text("SELECT 1")).first() is not None

    def test_tables_exist_after_migration(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        db_url = os.getenv("DATABASE_URL")
        if not db_url: pytest.skip("DATABASE_URL not set")
        expected = ["users", "playlists", "videos", "user_progress", "quizzes", "questions", "quiz_attempts", "xp_log"]
        from sqlmodel import create_engine, text, Session
        with Session(create_engine(db_url, echo=False)) as session:
            existing = [r[0] for r in session.exec(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).all()]
        missing = [t for t in expected if t not in existing]
        assert not missing, f"Missing: {missing}"

class TestModelStructure:
    def test_user_model_fields(self):
        from models import User
        for f in ["email", "hashed_password", "total_xp", "current_level", "current_streak"]: assert f in User.model_fields

    def test_quiz_model_fields(self):
        from models import Quiz
        for f in ["playlist_id", "sequence_order", "title", "status"]: assert f in Quiz.model_fields

    def test_question_model_fields(self):
        from models import Question
        for f in ["quiz_id", "question_text", "options", "correct_option_index"]: assert f in Question.model_fields

    def test_quiz_attempt_model_fields(self):
        from models import QuizAttempt
        for f in ["user_id", "quiz_id", "score", "passed", "questions_asked"]: assert f in QuizAttempt.model_fields

    def test_user_progress_model_fields(self):
        from models import UserProgress
        for f in ["user_id", "video_id", "highest_watched_second", "last_watched_second", "is_completed"]: assert f in UserProgress.model_fields
