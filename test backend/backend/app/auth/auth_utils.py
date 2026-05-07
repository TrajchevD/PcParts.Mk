import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

JWT_SECRET = "super-secret"
JWT_ALGO = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)


def create_token(user: dict) -> str:
    payload = {
        "user_id": user["user_id"],
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_token(token: str) -> dict:
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    return {
        "user_id": decoded["user_id"],
        "email": decoded["email"],
    }
