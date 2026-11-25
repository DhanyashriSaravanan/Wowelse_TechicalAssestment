Wowelse – User Registration and Authentication System
1. Project Overview
Developed a full-stack authentication application as part of the Wowelse assessment. It allows users to register, log in, and access a protected dashboard using either email/password authentication or Google sign-in.
2. Key Features
- User registration with username, email, and password.
- Input validation and duplicate account prevention.
- Secure password hashing using Argon2.
- Login using username or email.
- JWT-based authentication.
- Protected dashboard and profile API.
- Google sign-up and login using OAuth 2.0 / OpenID Connect.
- Secure logout functionality.
3. Technology Stack
Frontend	Backend	Security & Database
React	Python	SQLite
JavaScript	FastAPI	JWT
HTML, CSS	REST APIs	Argon2
Vite	Authlib	Google OAuth 2.0

4. Project Structure
The application is divided into two modules:
- Frontend: Registration, login, Google sign-in, and dashboard.
- Backend: Authentication, validation, database operations, and API management.
5. Setup and Execution
Backend:
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn main:app --reload


Frontend:
cd frontend
npm install
npm run dev


Application URL: http://localhost:5173

API Documentation: http://localhost:8000/docs
6. API Endpoints
Method	Endpoint	Purpose
POST	/api/register	User registration
POST	/api/login	User login
GET	/api/me	Fetch user profile
GET	/api/auth/google/login	Google sign-in
GET	/api/auth/google/callback	Google callback
POST	/api/auth/google/exchange	JWT exchange

7. Security
- Passwords are stored as Argon2 hashes.
- JWT validates authenticated users.
- Protected APIs prevent unauthorized access.
- Google identity is verified using OpenID Connect.
- Sensitive credentials are maintained in environment variables.
8. Testing
Tested the main application scenarios:
- Valid and invalid registration.
- Duplicate username and email validation.
- Username and email-based login.
- Incorrect password handling.
- Google authentication.
- Protected dashboard access.
- JWT validation and logout.
9. Authentication vs Authorization
- Authentication: Verifies the identity of a user.
- Authorization: Determines what resources the user can access.
10. Conclusion
This project demonstrates practical implementation of a full-stack authentication system using React and FastAPI. It provides hands-on experience with API integration, database management, password security, JWT authentication, and Google OAuth integration.
