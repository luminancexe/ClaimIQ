"""Authentication and JWT service for ClaimIQ Phase 7 API."""

import os
import secrets
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
import jwt

from backend.config import BackendConfig

# Standard roles
VALID_ROLES = {"ADMIN", "ANALYST", "QA_REVIEWER", "VIEWER"}

# In-memory user store for Phase 7 (no users table in MySQL schema per roadmap)
_USER_STORE: Dict[str, Dict[str, Any]] = {}


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored PBKDF2 hash."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hex = parts[3]
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return secrets.compare_digest(derived.hex(), expected_hex)
    except Exception:
        return False


def create_user(
    username: str,
    password: str,
    role: str = "VIEWER",
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Register or seed a user into the in-memory store."""
    clean_role = role.upper()
    if clean_role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Valid roles: {sorted(list(VALID_ROLES))}")

    clean_user = username.strip().lower()
    uid = user_id or f"usr-{secrets.token_hex(6)}"
    user_record = {
        "user_id": uid,
        "username": clean_user,
        "password_hash": hash_password(password),
        "role": clean_role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }
    _USER_STORE[clean_user] = user_record
    return user_record


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by username."""
    return _USER_STORE.get(username.strip().lower())


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by user_id."""
    for u in _USER_STORE.values():
        if u["user_id"] == user_id:
            return u
    return None


def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate username and password."""
    user = get_user_by_username(username)
    if not user or not user.get("is_active", True):
        return None
    if verify_password(password, user["password_hash"]):
        return user
    return None


def create_access_token(
    user_id: str,
    username: str,
    role: str,
    config: Optional[BackendConfig] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a signed JWT access token."""
    cfg = config or BackendConfig()
    exp_min = expires_minutes if expires_minutes is not None else cfg.jwt_expiration_minutes
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_min)

    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def create_refresh_token(
    user_id: str,
    username: str,
    role: str,
    config: Optional[BackendConfig] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a signed JWT refresh token."""
    cfg = config or BackendConfig()
    exp_min = expires_minutes if expires_minutes is not None else cfg.jwt_refresh_expiration_minutes
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_min)

    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def verify_token(
    token: str,
    expected_type: str = "access",
    config: Optional[BackendConfig] = None,
) -> Dict[str, Any]:
    """Verify, decode, and validate a JWT token."""
    cfg = config or BackendConfig()
    try:
        payload = jwt.decode(
            token,
            cfg.jwt_secret,
            algorithms=[cfg.jwt_algorithm],
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            raise jwt.InvalidTokenError(f"Expected token type '{expected_type}', got '{token_type}'")
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError:
        raise


def seed_default_users():
    """Seed initial development users into the in-memory store."""
    if not _USER_STORE:
        create_user("admin", "Admin@123", role="ADMIN", user_id="usr-admin-001")
        create_user("analyst", "Analyst@123", role="ANALYST", user_id="usr-analyst-001")
        create_user("qa_reviewer", "QaReviewer@123", role="QA_REVIEWER", user_id="usr-qareviewer-001")
        create_user("viewer", "Viewer@123", role="VIEWER", user_id="usr-viewer-001")


# Automatically seed default users
seed_default_users()
