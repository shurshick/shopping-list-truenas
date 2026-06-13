import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status


_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if forwarded_for:
        return forwarded_for
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    scope: str,
    identity: str = "",
    *,
    limit: int = 10,
    window_seconds: int = 60,
) -> None:
    now = time.monotonic()
    identity_key = identity.strip().lower() or "anonymous"
    key = f"{scope}:{_client_ip(request)}:{identity_key}"
    with _lock:
        attempts = _attempts[key]
        while attempts and now - attempts[0] > window_seconds:
            attempts.popleft()
        if len(attempts) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Слишком много попыток. Подождите минуту и попробуйте снова.",
            )
        attempts.append(now)


def reset_rate_limits() -> None:
    with _lock:
        _attempts.clear()
