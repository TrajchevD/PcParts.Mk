from fastapi import APIRouter, Depends, HTTPException

from app.core.db import execute, fetchone
from app.core.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.schemas.auth import UserOut, UserUpdateIn

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    row = fetchone(
        "SELECT user_id, email, created_at FROM users WHERE user_id = %s",
        (user["user_id"],),
    )
    if not row:
        raise HTTPException(404, "User not found")
    return row


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdateIn, user=Depends(get_current_user)):
    row = fetchone(
        "SELECT user_id, email, password_hash, created_at FROM users WHERE user_id = %s",
        (user["user_id"],),
    )
    if not row:
        raise HTTPException(404, "User not found")

    if body.new_password:
        if not body.current_password:
            raise HTTPException(400, "current_password is required to set a new password")
        if not verify_password(body.current_password, row["password_hash"]):
            raise HTTPException(400, "Current password is incorrect")

    updates: dict = {}

    if body.email and body.email != row["email"]:
        taken = fetchone("SELECT user_id FROM users WHERE email = %s", (body.email,))
        if taken:
            raise HTTPException(400, "Email already in use")
        updates["email"] = body.email

    if body.new_password:
        updates["password_hash"] = hash_password(body.new_password)

    if updates:
        set_clause = ", ".join(f"{col} = %s" for col in updates)
        execute(
            f"UPDATE users SET {set_clause} WHERE user_id = %s",
            (*updates.values(), user["user_id"]),
        )

    updated = fetchone(
        "SELECT user_id, email, created_at FROM users WHERE user_id = %s",
        (user["user_id"],),
    )
    return updated
