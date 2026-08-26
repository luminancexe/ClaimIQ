"""FastAPI Dependency Injection helpers for ClaimIQ Phase 7 Backend API."""

from typing import Generator, Optional, Dict, Any, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pymysql
import jwt

from backend.config import BackendConfig
from backend.database import get_api_connection
from backend.services.auth import verify_token, get_user_by_id

# Reusable security scheme
security = HTTPBearer(auto_error=False)


def get_config() -> BackendConfig:
    """Dependency providing backend configuration."""
    return BackendConfig()


def get_db(config: BackendConfig = Depends(get_config)) -> Generator[Optional[pymysql.Connection], None, None]:
    """Yield a read-only MySQL connection per request, ensuring cleanup."""
    conn: Optional[pymysql.Connection] = None
    try:
        conn = get_api_connection(config)
    except Exception:
        # Connection failed; yield None so routes or mock fixtures can handle it
        conn = None

    try:
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    config: BackendConfig = Depends(get_config),
) -> Dict[str, Any]:
    """Extract and validate JWT access token, returning authenticated user record."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = verify_token(token, expected_type="access", config=config)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")

    user = get_user_by_id(user_id) if user_id else None
    if not user:
        # Fallback to payload data if user not in memory (e.g. valid signed token)
        user = {
            "user_id": user_id,
            "username": username,
            "role": role,
        }

    return user


def require_role(*roles: str) -> Callable:
    """Dependency factory checking if current user possesses one of the required roles."""
    allowed_roles = {r.upper() for r in roles}

    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "").upper()
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Insufficient privileges. Required: {sorted(list(allowed_roles))}, current: {user_role}",
            )
        return current_user

    return role_checker
