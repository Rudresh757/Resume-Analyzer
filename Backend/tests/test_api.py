import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Create an in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

def test_auth_workflow():
    # 1. Register a user
    reg_data = {
        "username": "fastapi_dev",
        "email": "dev@fastapi.org",
        "password": "SecretPassword123"
    }
    reg_res = client.post("/api/auth/register", json=reg_data)
    assert reg_res.status_code == 201
    reg_json = reg_res.json()
    assert reg_json["message"] == "User registered successfully"
    assert reg_json["user"]["username"] == "fastapi_dev"
    assert "token" in reg_res.cookies

    # 2. Duplicate registration should return 400
    dup_res = client.post("/api/auth/register", json=reg_data)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["message"]

    # 3. Login with wrong password should fail
    wrong_login = client.post("/api/auth/login", json={
        "email": "dev@fastapi.org",
        "password": "WrongPassword"
    })
    assert wrong_login.status_code == 400
    assert wrong_login.json()["message"] == "Invalid email or password"

    # 4. Login with correct password
    login_res = client.post("/api/auth/login", json={
        "email": "dev@fastapi.org",
        "password": "SecretPassword123"
    })
    assert login_res.status_code == 200
    assert login_res.json()["user"]["email"] == "dev@fastapi.org"
    token = login_res.cookies.get("token")
    assert token is not None

    # 5. Access /get-me with cookie
    me_res = client.get("/api/auth/get-me", cookies={"token": token})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["username"] == "fastapi_dev"

    # 6. Access /get-me without cookie should fail 401
    client.cookies.clear()
    unauth_res = client.get("/api/auth/get-me")
    assert unauth_res.status_code == 401

    # 7. Logout should blacklist the token
    logout_res = client.get("/api/auth/logout", cookies={"token": token})
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "User logged out successfully"

    # 8. Access /get-me with blacklisted token should fail 401
    blacklisted_res = client.get("/api/auth/get-me", cookies={"token": token})
    assert blacklisted_res.status_code == 401
    assert "invalid" in blacklisted_res.json()["message"]
