import base64
import hmac
import secrets
import time
from hashlib import sha256
from urllib.parse import urlparse

from fastapi import HTTPException, Request, status

from .config import settings


CSRF_TOKEN_TTL_SECONDS = 60 * 60 * 2


def create_csrf_token() -> str:
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(18)
    payload = f"{timestamp}:{nonce}"
    signature = hmac.new(settings.jwt_secret.encode("utf-8"), payload.encode("utf-8"), sha256).digest()
    token = f"{payload}:{base64.urlsafe_b64encode(signature).decode('ascii')}"
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("ascii")


def verify_csrf_token(token: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        timestamp_raw, nonce, signature_raw = decoded.split(":", 2)
        timestamp = int(timestamp_raw)
    except Exception:
        return False
    if not nonce or time.time() - timestamp > CSRF_TOKEN_TTL_SECONDS:
        return False
    payload = f"{timestamp_raw}:{nonce}"
    expected = hmac.new(settings.jwt_secret.encode("utf-8"), payload.encode("utf-8"), sha256).digest()
    actual = base64.urlsafe_b64decode(signature_raw.encode("ascii"))
    return hmac.compare_digest(actual, expected)


def require_csrf_token(token: str) -> None:
    if not verify_csrf_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недействительный защитный токен формы. Обновите страницу и попробуйте снова.",
        )


def require_same_origin(request: Request) -> None:
    expected_host = request.headers.get("host", "")
    origin_or_referer = request.headers.get("origin") or request.headers.get("referer")
    if not origin_or_referer:
        return
    parsed = urlparse(origin_or_referer)
    actual_host = parsed.netloc
    if actual_host and expected_host and actual_host != expected_host:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Запрос отклонён: источник формы не совпадает с адресом сервера.",
        )
