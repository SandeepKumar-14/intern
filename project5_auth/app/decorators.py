from functools import wraps

import jwt
from flask import request, jsonify, g

from .jwt_utils import decode_token
from .models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        if payload.get("type") != "access":
            return jsonify({"error": "Wrong token type"}), 401

        user = User.query.get(payload["sub"])
        if user is None or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated
