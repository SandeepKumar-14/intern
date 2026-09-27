# Secure Authentication System

Flask + PyJWT + bcrypt + PostgreSQL authentication service with access/refresh
token rotation, rate limiting, and input validation.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # then edit values
```

Create the database and run migrations:

```bash
createdb secure_auth_db
flask --app run db init
flask --app run db migrate -m "initial"
flask --app run db upgrade
```

Run the server:

```bash
python run.py
```

## Endpoints

| Method | Path                 | Auth | Description                     |
|--------|----------------------|------|----------------------------------|
| POST   | /api/auth/register   | No   | Create a new user                |
| POST   | /api/auth/login      | No   | Get access + refresh tokens      |
| POST   | /api/auth/refresh    | No   | Rotate an access/refresh pair    |
| POST   | /api/auth/logout     | Yes  | Revoke refresh token(s)          |
| GET    | /api/auth/me         | Yes  | Get current user profile         |

Send the access token as `Authorization: Bearer <token>`.

## Security notes

- Passwords are hashed with bcrypt (configurable cost factor).
- Passwords must be 8+ characters with upper, lower, digit, and symbol.
- Access tokens expire in 15 minutes; refresh tokens in 7 days and rotate on use.
- Refresh tokens are tracked in the database so they can be revoked (logout).
- Login/register endpoints are rate-limited to slow brute-force attempts.

## Tests

```bash
pytest
```
