from datetime import datetime, timezone

import jwt
from flask import Blueprint, request, jsonify, current_app, g
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from . import db, limiter
from .models import User, RefreshToken
from .schemas import RegisterSchema, LoginSchema, RefreshSchema
from .jwt_utils import create_access_token, create_refresh_token, decode_token
from .decorators import token_required

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
refresh_schema = RefreshSchema()


@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    try:
        data = register_schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User(email=data["email"].lower(), username=data["username"])
    user.set_password(data["password"], rounds=current_app.config["BCRYPT_ROUNDS"])

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email or username already registered"}), 409

    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    try:
        data = login_schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"].lower()).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401
    if not user.is_active:
        return jsonify({"error": "Account disabled"}), 403

    access_token = create_access_token(user.id)
    refresh_token, jti, expires_at = create_refresh_token(user.id)

    db.session.add(
        RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at)
    )
    db.session.commit()

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }
    )


@auth_bp.post("/refresh")
@limiter.limit("20 per minute")
def refresh():
    try:
        data = refresh_schema.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        payload = decode_token(data["refresh_token"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    if payload.get("type") != "refresh":
        return jsonify({"error": "Wrong token type"}), 401

    stored = RefreshToken.query.filter_by(jti=payload["jti"]).first()
    if stored is None or stored.revoked:
        return jsonify({"error": "Token has been revoked"}), 401
    if stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return jsonify({"error": "Token has expired"}), 401

    # Rotate: revoke old, issue new
    stored.revoked = True
    new_access = create_access_token(payload["sub"])
    new_refresh, new_jti, new_expires = create_refresh_token(payload["sub"])
    db.session.add(RefreshToken(user_id=payload["sub"], jti=new_jti, expires_at=new_expires))
    db.session.commit()

    return jsonify({"access_token": new_access, "refresh_token": new_refresh})


@auth_bp.post("/logout")
@token_required
def logout():
    data = request.get_json(silent=True) or {}
    jti = data.get("jti")
    if jti:
        token = RefreshToken.query.filter_by(jti=jti, user_id=g.current_user.id).first()
        if token:
            token.revoked = True
            db.session.commit()
    else:
        RefreshToken.query.filter_by(user_id=g.current_user.id, revoked=False).update(
            {"revoked": True}
        )
        db.session.commit()

    return jsonify({"message": "Logged out"})


@auth_bp.get("/me")
@token_required
def me():
    return jsonify({"user": g.current_user.to_dict()})
