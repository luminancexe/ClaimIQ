"""Authentication routes for ClaimIQ Phase 7 Backend API."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import jwt

from backend.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserProfile
from backend.config import BackendConfig
from backend.dependencies import get_config, get_current_user
from backend.services.auth import (
    authenticate,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user_by_id,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    config: BackendConfig = Depends(get_config),
):
    """Authenticate with username and password, returning JWT tokens."""
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user_id=user["user_id"],
        username=user["username"],
        role=user["role"],
        config=config,
    )
    refresh_token = create_refresh_token(
        user_id=user["user_id"],
        username=user["username"],
        role=user["role"],
        config=config,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.jwt_expiration_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    req: RefreshRequest,
    config: BackendConfig = Depends(get_config),
):
    """Exchange a valid refresh token for a new access and refresh token pair."""
    try:
        payload = verify_token(req.refresh_token, expected_type="refresh", config=config)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    username = payload["username"]
    role = payload.get("role", "VIEWER")

    new_access_token = create_access_token(
        user_id=user_id,
        username=username,
        role=role,
        config=config,
    )
    new_refresh_token = create_refresh_token(
        user_id=user_id,
        username=username,
        role=role,
        config=config,
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=config.jwt_expiration_minutes * 60,
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieve profile of the currently authenticated user."""
    return UserProfile(
        user_id=current_user["user_id"],
        username=current_user["username"],
        role=current_user.get("role", "VIEWER"),
        created_at=current_user.get("created_at"),
    )
