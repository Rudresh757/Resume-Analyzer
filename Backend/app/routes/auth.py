import logging
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.blacklist import BlacklistedToken
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthSuccessResponse,
    MessageResponse,
)
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.middlewares.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthSuccessResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user with username, email, and password.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        or_(User.username == payload.username, User.email == payload.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists with this email address or username"
        )

    # Hash password and create user
    hashed = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT
    token = create_access_token({"id": user.id, "username": user.username})

    # Set HttpOnly cookie for frontend Axios compatibility
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production HTTPS
        max_age=86400  # 1 day
    )

    return AuthSuccessResponse(
        message="User registered successfully",
        user=UserResponse(id=user.id, username=user.username, email=user.email)
    )

@router.post("/login", response_model=AuthSuccessResponse, status_code=status.HTTP_200_OK)
async def login(payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    token = create_access_token({"id": user.id, "username": user.username})

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400
    )

    return AuthSuccessResponse(
        message="User loggedIn successfully.",
        user=UserResponse(id=user.id, username=user.username, email=user.email)
    )

@router.get("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logout user, clear cookie and blacklist token in MySQL.
    """
    token = request.cookies.get("token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if token:
        # Check if already blacklisted
        already_blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if not already_blacklisted:
            blacklisted = BlacklistedToken(token=token)
            db.add(blacklisted)
            db.commit()

    response.delete_cookie(key="token")

    return MessageResponse(message="User logged out successfully")

@router.get("/get-me", response_model=AuthSuccessResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get profile information of currently authenticated user.
    """
    return AuthSuccessResponse(
        message="User details fetched successfully",
        user=UserResponse(id=current_user.id, username=current_user.username, email=current_user.email)
    )
