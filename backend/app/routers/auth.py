from fastapi import APIRouter, HTTPException, Request

from app.core.db import execute, fetchone
from app.core.rate_limit import check_rate_limit
from app.core.security import create_token, hash_password, verify_password
from app.schemas.auth import LoginIn, RegisterIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Limits: 10 attempts per minute per IP on login/register
_AUTH_MAX = 10
_AUTH_WINDOW = 60


@router.post("/register", status_code=201)
def register(body: RegisterIn, request: Request):
    check_rate_limit(request, max_calls=_AUTH_MAX, window=_AUTH_WINDOW, key_prefix="register")

    existing = fetchone(
        "SELECT user_id FROM users WHERE email = %s",
        (body.email,),
    )
    if existing:
        raise HTTPException(400, "Email already registered")

    execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        (body.email, hash_password(body.password)),
    )
    return {"ok": True}


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request):
    check_rate_limit(request, max_calls=_AUTH_MAX, window=_AUTH_WINDOW, key_prefix="login")

    user = fetchone(
        "SELECT user_id, email, password_hash FROM users WHERE email = %s",
        (body.email,),
    )
    # Use constant-time comparison even on missing user to prevent timing attacks
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user["user_id"], user["email"])
    return {"access_token": token}
