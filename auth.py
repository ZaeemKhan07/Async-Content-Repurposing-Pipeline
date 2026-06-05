import os
import json
import datetime
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    keys_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys")
    if os.path.isdir(keys_dir):
        for fname in os.listdir(keys_dir):
            if fname.startswith("client_secret_") and fname.endswith(".json"):
                with open(os.path.join(keys_dir, fname), "r", encoding="utf-8") as f:
                    GOOGLE_CLIENT_ID = json.load(f).get("web", {}).get("client_id")
                    break

JWT_SECRET = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGO = "HS256"
JWT_TTL_DAYS = 7
COOKIE_NAME = "session"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"


def verify_google_id_token(id_token_str: str) -> dict:
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured on the server",
        )
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {e}",
        )

    if idinfo.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token issuer")

    return idinfo


def upsert_user(db: Session, idinfo: dict) -> models.User:
    google_sub = idinfo["sub"]
    user = db.query(models.User).filter(models.User.id == google_sub).first()
    now = datetime.datetime.utcnow()
    if user:
        user.email = idinfo.get("email", user.email)
        user.name = idinfo.get("name", user.name)
        user.picture = idinfo.get("picture", user.picture)
        user.last_login_at = now
    else:
        user = models.User(
            id=google_sub,
            email=idinfo.get("email"),
            name=idinfo.get("name"),
            picture=idinfo.get("picture"),
            created_at=now,
            last_login_at=now,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_session_jwt(user_id: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(days=JWT_TTL_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_session_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session payload")
    return user_id


def get_current_user(
    request: Request,
    db: Session = Depends(models.get_db),
) -> models.User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_session_jwt(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user
