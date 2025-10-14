from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create a shared limiter instance
limiter = Limiter(key_func=get_remote_address)


def register_rate_limit(app: FastAPI) -> None:
    """Attach limiter to app and register the 429 handler."""
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: PlainTextResponse("Too Many Requests", status_code=429),
    )
