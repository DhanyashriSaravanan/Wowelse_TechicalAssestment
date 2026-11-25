# Wowelse User Registration and Authentication

A beginner-friendly full-stack implementation of the Wowelse assessment using React, Python FastAPI, SQLite, JWT, password hashing, and Google OAuth 2.0 / OpenID Connect.

## 1. Features

- Register with username, email, password, and confirm password.
- Validate email and input fields.
- Prevent duplicate usernames and email addresses.
- Hash passwords before saving them.
- Log in using username or email.
- Return a JWT after successful password login.
- Protect the dashboard profile API.
- Sign up and log in using Google.
- Store Google profile name, email, and Google subject ID.
- Google users do not need a separate application password.
- Log out from the dashboard.

## 2. Technology

- Frontend: React, JavaScript, HTML, CSS, Vite
- Backend: Python, FastAPI
- Database: SQLite (built into Python)
- Password hashing: pwdlib with Argon2
- Token: PyJWT
- Google authentication: Authlib and OpenID Connect

## 3. Folder structure

```text
wowelse_fastapi_mongodb/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── security.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/Navbar.jsx
│   │   ├── pages/Register.jsx
│   │   ├── pages/Login.jsx
│   │   ├── pages/Dashboard.jsx
│   │   ├── pages/GoogleCallback.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   ├── index.html
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 4. Requirements

Install:
- Python 3.10 or newer
- Node.js LTS and npm

## 5. SQLite storage

The backend creates `backend/wowelse_auth.db` and its tables automatically the first time it starts. Set `SQLITE_DB_PATH` in `backend/.env` only if you want to store the database file elsewhere.

### Example user records

Local account:

```json
{
  "username": "sample_user",
  "name": "sample_user",
  "email": "sample@example.com",
  "hashed_password": "argon2-hash-value",
  "google_id": null,
  "auth_provider": "local"
}
```

Google account:

```json
{
  "username": null,
  "name": "Sample Person",
  "email": "person@gmail.com",
  "hashed_password": null,
  "google_id": "google-subject-id",
  "auth_provider": "google"
}
```

These are examples; SQLite also stores a unique ID and `created_at` timestamp.

## 6. Backend setup

Open a terminal in the project folder:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` inside `backend` and set:
- `SECRET_KEY`
- `FRONTEND_URL`
- `BACKEND_URL`
- `SQLITE_DB_PATH` only if you want to override the default database location
- Google client ID and secret when configuring Google login

Create a long random secret for `SECRET_KEY`. Keep `.env` private and never commit it.

Start FastAPI:

```bash
uvicorn main:app --reload
```

Backend URL: http://localhost:8000

Interactive API docs: http://localhost:8000/docs

## 7. Frontend setup

Open a second terminal in the project folder:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally http://localhost:5173.

### Deploy the frontend to Netlify

Set the Netlify base directory to `frontend`, build command to `npm run build`, and publish directory to `dist`. Add `VITE_API_URL` as a site environment variable with the public base URL of the deployed FastAPI backend (without a trailing slash). The backend must also allow the Netlify site URL in `FRONTEND_URL`. Netlify hosts the React frontend; it does not run this FastAPI server.

## 8. Google OAuth setup

Google sign-in requires credentials; it will not work until configured.

1. Open https://console.cloud.google.com/
2. Create or select a Google Cloud project.
3. Configure the OAuth consent screen and add a test user if the app remains in testing mode.
4. Create an OAuth Client ID with application type **Web application**.
5. Add this authorized redirect URI exactly:

   `http://localhost:8000/api/auth/google/callback`

6. Put the Client ID and Client Secret into `backend/.env`.
7. Restart the backend.

The browser starts Google sign-in at `/api/auth/google/login`. Google returns to the backend callback. The backend creates a short-lived, one-time code, and the React callback page exchanges that code for the application's JWT. The Google access token and client secret are not sent to React.

## 9. API endpoint documentation

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check whether API is running |
| POST | `/api/register` | Register with username/email/password |
| POST | `/api/login` | Login using username/email and password |
| GET | `/api/me` | Get the authenticated user's profile |
| GET | `/api/auth/google/login` | Start Google sign-in |
| GET | `/api/auth/google/callback` | Handle Google's callback |
| POST | `/api/auth/google/exchange` | Exchange one-time code for JWT |

### Register request

```json
{
  "username": "sample_user",
  "email": "sample@example.com",
  "password": "Example@123",
  "confirm_password": "Example@123"
}
```

### Login request

```json
{
  "username_or_email": "sample_user",
  "password": "Example@123"
}
```

### Protected profile request

Add this HTTP header:

```text
Authorization: Bearer YOUR_JWT_TOKEN
```

## 10. Assessment testing checklist

### Registration
- [ ] Register with valid information.
- [ ] Reject an invalid email.
- [ ] Reject a username shorter than 3 characters.
- [ ] Reject a password shorter than 8 characters.
- [ ] Reject mismatched passwords.
- [ ] Reject an existing username.
- [ ] Reject an existing email.
- [ ] Confirm the stored password is a hash, not plain text.
- [ ] Redirect to login after successful registration.

### Login
- [ ] Login using username.
- [ ] Login using email.
- [ ] Reject an incorrect password.
- [ ] Reject an unregistered user.
- [ ] Reject a Google-only account using password login.
- [ ] Redirect a successful login to the dashboard.
- [ ] Reject an expired or invalid JWT on the profile endpoint.

### Google authentication
- [ ] Start Google sign-up.
- [ ] Confirm Google profile name and email are stored.
- [ ] Confirm Google subject ID is stored.
- [ ] Sign in again with the same Google account.
- [ ] Confirm the existing account is reused.
- [ ] Confirm Google account has no application password.
- [ ] Reject unverified Google email.
- [ ] Confirm an existing local account is not silently linked.

### Dashboard
- [ ] Open dashboard after login.
- [ ] Refresh dashboard and confirm profile is loaded.
- [ ] Open dashboard without login and confirm redirect.
- [ ] Logout and confirm token is cleared.

## 11. Important security notes

This project is intended as a local assessment and learning implementation. Before production use:
- Use HTTPS.
- Store JWTs in secure, HttpOnly cookies rather than localStorage.
- Enable secure session cookies and review CSRF protections.
- Add rate limiting to login and registration.
- Add token revocation or refresh-token handling.
- Keep environment secrets out of Git.
- Configure production OAuth redirect URLs.
- Consider email verification and account recovery.

The application intentionally does not silently merge a Google account with an existing local account that has the same email. A separate authenticated account-linking process would be needed.

## 12. Interview explanation

**Why FastAPI?**  
FastAPI is a Python framework used to create backend APIs. It provides request validation and automatic API documentation.

**Why SQLite?**  
SQLite stores application data in a local database file and does not require a separate database server for local development.

**Why password hashing?**  
We should not store plain-text passwords. Password hashing protects user credentials if the database is exposed.

**Why JWT?**  
JWT allows the backend to verify a user's identity on protected API requests.

**Why Google OAuth?**  
OAuth/OpenID Connect lets users authenticate using their Google account without creating another application password.

**What is the difference between authentication and authorization?**  
Authentication verifies who the user is. Authorization determines what the user is allowed to access.
