from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from typing import Any

from jose import jwt

from app.core.config import get_settings


HASH_NAME = "sha256"
HASH_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Hash a plain password before storing it in the database."""

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_{HASH_NAME}${HASH_ITERATIONS}${salt}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt, stored_digest = hashed_password.split("$", 3)
        if algorithm != f"pbkdf2_{HASH_NAME}":
            return False
        digest = hashlib.pbkdf2_hmac(
            HASH_NAME,
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
    except ValueError:
        return False
    return hmac.compare_digest(digest, stored_digest)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
