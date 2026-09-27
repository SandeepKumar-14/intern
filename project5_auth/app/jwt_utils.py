import uuid
from datetime import datetime, timezone

import jwt
from flask import current_app


def _now():
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": _now(),
        "exp": _now() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    jti = str(uuid.uuid4())
    expires_at = _now() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": _now(),
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token, jti, expires_at


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
    )
