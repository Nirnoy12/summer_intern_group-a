import os, sys, pytest, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestFastAPIApplication:
    @pytest.fixture(scope="class")
    def client(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app, raise_server_exceptions=False)

    def test_root_endpoint_returns_200(self, client):
        assert client.get("/").status_code == 200; assert "message" in client.get("/").json()

    def test_openapi_schema_is_accessible(self, client):
        assert "paths" in client.get("/openapi.json").json()

    def test_auth_register_endpoint_exists(self, client):
        assert client.post("/api/auth/register", json={}).status_code in (422, 400)

    def test_auth_login_endpoint_exists(self, client):
        assert client.post("/api/auth/login", data={}).status_code in (422, 400)

    def test_protected_endpoints_require_auth(self, client):
        for method, path in [("GET", "/api/playlists"), ("GET", "/api/users/me")]:
            assert client.request(method, path).status_code == 401

    def test_cors_headers_present(self, client):
        assert client.options("/api/auth/login", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"}).status_code in (200, 204)

class TestAuthFlow:
    @pytest.fixture(scope="class")
    def client(self):
        from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        if not os.getenv("DATABASE_URL", ""): pytest.skip("DATABASE_URL not configured")
        from fastapi.testclient import TestClient; from main import app
        return TestClient(app)

    def test_full_register_login_cycle(self, client):
        email, pwd = f"test_{uuid.uuid4().hex[:8]}@verify.local", "SecurePassword123!"
        assert client.post("/api/auth/register", json={"email": email, "password": pwd}).status_code == 200
        login = client.post("/api/auth/login", data={"username": email, "password": pwd}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert login.status_code == 200
        token = login.json().get("access_token")
        assert token
        me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200 and me.json()["email"] == email
