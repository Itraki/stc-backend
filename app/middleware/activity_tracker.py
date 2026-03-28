import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import logger
from app.db.client import mongodb_client

# Paths that don't need to be logged
_SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}


class ActivityTrackerMiddleware(BaseHTTPMiddleware):
    """
    Records every HTTP request into the MongoDB `activity_logs` collection.

    Captures: method, path, query string, status code, duration, IP,
    user-agent, and (when a valid JWT is present) user_id, email, role.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.monotonic()
        response = await call_next(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        # Try to decode user info from the Authorization header without
        # blocking the request — errors are silently ignored.
        user_id = user_email = role = None
        try:
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                from app.core.security import verify_token
                token_data = verify_token(auth[7:])
                user_id = token_data.user_id
                user_email = token_data.email
                role = token_data.role
        except Exception:
            pass

        try:
            db = mongodb_client.db
            if db is not None:
                await db.activity_logs.insert_one({
                    "timestamp": datetime.now(timezone.utc),
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query) or None,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                    "user_id": user_id,
                    "user_email": user_email,
                    "role": role,
                })
        except Exception as e:
            logger.warning(f"ActivityTracker: failed to log request: {e}")

        return response
