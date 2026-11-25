from datetime import datetime, timezone

def create_local_user(username: str, email: str, hashed_password: str) -> dict:
    return {
        "username": username,
        "name": username,
        "email": email,
        "hashed_password": hashed_password,
        "google_id": None,
        "auth_provider": "local",
        "created_at": datetime.now(timezone.utc),
    }

def create_google_user(name: str, email: str, google_id: str) -> dict:
    return {
        "username": None,
        "name": name,
        "email": email,
        "hashed_password": None,
        "google_id": google_id,
        "auth_provider": "google",
        "created_at": datetime.now(timezone.utc),
    }
