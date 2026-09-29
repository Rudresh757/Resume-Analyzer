from app.services.auth_service import hash_password, verify_password, create_access_token, decode_token

def test_password_hashing():
    raw_pass = "SecurePass123!"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    payload = {"id": 42, "username": "testuser"}
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded["id"] == 42
    assert decoded["username"] == "testuser"
    assert "exp" in decoded
