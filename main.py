import os
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import (
    find_user_by_email,
    find_user_by_google_id,
    find_user_by_username_or_email,
    find_user_by_login,
    insert_user,
)
from models import create_local_user, create_google_user
from schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse, GoogleCodeRequest
from security import hash_password, verify_password, create_access_token
from auth import (
    get_current_user,
    make_public_user,
    save_one_time_google_code,
    exchange_google_code,
)

load_dotenv()

app = FastAPI(
    title="Wowelse User Authentication API",
    description="Registration, login and Google authentication for the Wowelse assessment.",
    version="1.0.0",
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_frontend_urls = {
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_frontend_urls),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    same_site="lax",
    https_only=False,  # Set True after deploying behind HTTPS.
)

oauth = OAuth()
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if google_client_id and google_client_secret:
    oauth.register(
        name="google",
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

@app.get("/")
def home():
    return {"message": "Wowelse Authentication API is running"}

@app.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    username = data.username.strip().lower()
    email = str(data.email).strip().lower()

    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password do not match")

    existing_user = find_user_by_username_or_email(username, email)
    if existing_user:
        if existing_user.get("username") == username:
            raise HTTPException(status_code=409, detail="Username is already taken")
        raise HTTPException(status_code=409, detail="Email is already registered")

    user_document = create_local_user(
        username=username,
        email=email,
        hashed_password=hash_password(data.password),
    )

    try:
        user_document = insert_user(user_document)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username or email is already registered")

    return make_public_user(user_document)

@app.post("/api/login", response_model=TokenResponse)
def login(data: LoginRequest):
    login_value = data.username_or_email.strip()
    user = find_user_by_login(login_value.lower())

    # Google accounts do not have a separate application password.
    if not user or not user.get("hashed_password"):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
        "user": make_public_user(user),
    }

@app.get("/api/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return make_public_user(current_user)

@app.get("/api/auth/google/login")
async def google_login(request: Request):
    if not google_client_id or not google_client_secret:
        return RedirectResponse(frontend_url + "/login?error=google_not_configured")

    redirect_uri = (
        os.getenv("BACKEND_URL", "http://localhost:8000")
        + "/api/auth/google/callback"
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/google/callback")
async def google_callback(request: Request):
    if not google_client_id or not google_client_secret:
        return RedirectResponse(frontend_url + "/login?error=google_not_configured")

    try:
        token = await oauth.google.authorize_access_token(request)
        google_profile = token.get("userinfo")

        if not google_profile:
            return RedirectResponse(frontend_url + "/login?error=profile_not_received")

        google_id = google_profile.get("sub")
        email = (google_profile.get("email") or "").strip().lower()
        name = google_profile.get("name") or email.split("@")[0]
        email_verified = google_profile.get("email_verified") is True

        if not google_id or not email or not email_verified:
            return RedirectResponse(frontend_url + "/login?error=google_email_not_verified")

        user = find_user_by_google_id(google_id)

        if user is None:
            existing_email_user = find_user_by_email(email)
            if existing_email_user:
                # Do not silently combine two different sign-in methods.
                return RedirectResponse(frontend_url + "/login?error=email_already_registered")

            user_document = create_google_user(
                name=name,
                email=email,
                google_id=google_id,
            )
            user = insert_user(user_document)

        one_time_code = save_one_time_google_code(str(user["_id"]))
        return RedirectResponse(
            frontend_url + "/auth/callback?code=" + one_time_code
        )

    except Exception:
        return RedirectResponse(frontend_url + "/login?error=google_sign_in_failed")

@app.post("/api/auth/google/exchange", response_model=TokenResponse)
def google_code_exchange(data: GoogleCodeRequest):
    user = exchange_google_code(data.code)
    if user is None:
        raise HTTPException(status_code=401, detail="Google sign-in code is invalid or expired")

    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
        "user": make_public_user(user),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
