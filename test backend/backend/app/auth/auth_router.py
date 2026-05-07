from fastapi import APIRouter, HTTPException
from app.db import get_conn
from app.models.user_models import UserRegisterIn, UserLoginIn
from app.auth.auth_utils import create_token, verify_password, hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(data: UserRegisterIn):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        # check if email exists
        cur.execute("SELECT user_id FROM users WHERE email=%s", (data.email,))
        if cur.fetchone():
            raise HTTPException(400, "Email already registered")

        hashed = hash_password(data.password)

        cur.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            """,
            (data.email, hashed),
        )

        return {"ok": True}

    finally:
        conn.close()


@router.post("/login")
def login(data: UserLoginIn):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT user_id, email, password_hash FROM users WHERE email=%s",
            (data.email,),
        )
        user = cur.fetchone()

        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(401, "Invalid credentials")

        token = create_token(
            {"user_id": user["user_id"], "email": user["email"]}
        )

        return {"access_token": token}

    finally:
        conn.close()
