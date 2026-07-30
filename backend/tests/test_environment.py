import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestEnvironmentVariables:
    REQUIRED_VARS = ["DATABASE_URL", "SECRET_KEY", "YOUTUBE_API_KEY"]

    def test_all_required_env_vars_present(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        missing = [v for v in self.REQUIRED_VARS if not os.getenv(v)]
        assert not missing, f"Missing: {missing}"

    def test_database_url_format(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        assert os.getenv("DATABASE_URL", "").startswith("cockroachdb://")

    def test_secret_key_length(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        assert len(os.getenv("SECRET_KEY", "")) >= 32

    def test_secret_key_is_not_placeholder(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        secret = os.getenv("SECRET_KEY", "").lower()
        for ph in ["replace_with", "your_secret", "fallback", "<", ">"]:
            assert ph not in secret

if __name__ == "__main__":
    import subprocess
    sys.exit(subprocess.run(["python", "-m", "pytest", __file__, "-v", "--tb=short"], cwd=os.path.dirname(__file__)).returncode)
