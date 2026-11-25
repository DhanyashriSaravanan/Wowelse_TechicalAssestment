import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from database import (
    consume_google_code,
    find_user_by_id,
    save_google_code,
)
from security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

def make_public_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "name": user.get("name"),
        "email": user["email"],
        "auth_provider": user.get("auth_provider", "local"),
    }

def save_one_time_google_code(user_id: str) -> str:
    raw_code = secrets.token_urlsafe(32)
    code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)

    save_google_code(code_hash, user_id, expires_at)
    return raw_code

def exchange_google_code(raw_code: str) -> dict | None:
    code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
    return consume_google_code(code_hash)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to continue",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Missing user ID")
        user = find_user_by_id(user_id)
    except Exception:
        user = None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired login token",
        )

    return user
