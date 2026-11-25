import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv(
    "SQLITE_DB_PATH", str(Path(__file__).with_name("wowelse_auth.db"))
)


@contextmanager
def _connection():
    if DATABASE_PATH != ":memory:":
        Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _user_from_row(row):
    if row is None:
        return None

    user = dict(row)
    user["_id"] = user.pop("id")
    user["created_at"] = datetime.fromisoformat(user["created_at"])
    return user


def initialize_database():
    with _connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                name TEXT,
                email TEXT NOT NULL UNIQUE,
                hashed_password TEXT,
                google_id TEXT UNIQUE,
                auth_provider TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS oauth_codes (
                code_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            );
            """
        )


def find_user_by_id(user_id):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return _user_from_row(row)


def find_user_by_username_or_email(username, email):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ? OR email = ? LIMIT 1",
            (username, email),
        ).fetchone()
    return _user_from_row(row)


def find_user_by_login(value):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ? OR email = ? LIMIT 1",
            (value, value),
        ).fetchone()
    return _user_from_row(row)


def find_user_by_email(email):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    return _user_from_row(row)


def find_user_by_google_id(google_id):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE google_id = ?", (google_id,)
        ).fetchone()
    return _user_from_row(row)


def insert_user(user):
    user_id = uuid.uuid4().hex
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO users (
                id, username, name, email, hashed_password, google_id,
                auth_provider, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user.get("username"),
                user.get("name"),
                user["email"],
                user.get("hashed_password"),
                user.get("google_id"),
                user["auth_provider"],
                user["created_at"].isoformat(),
            ),
        )
    return {**user, "_id": user_id}


def save_google_code(code_hash, user_id, expires_at):
    with _connection() as connection:
        connection.execute(
            "INSERT INTO oauth_codes (code_hash, user_id, expires_at) VALUES (?, ?, ?)",
            (code_hash, user_id, expires_at.isoformat()),
        )


def consume_google_code(code_hash):
    with _connection() as connection:
        row = connection.execute(
            "SELECT user_id, expires_at FROM oauth_codes WHERE code_hash = ?",
            (code_hash,),
        ).fetchone()
        if row is not None:
            connection.execute(
                "DELETE FROM oauth_codes WHERE code_hash = ?", (code_hash,)
            )

    if row is None or datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
        return None
    return find_user_by_id(row["user_id"])


initialize_database()
