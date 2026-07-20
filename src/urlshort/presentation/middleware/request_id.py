from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_HEADER = "X-Request-ID"
_logger = structlog.get_logger("urlshort.http")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            _logger.exception("request_failed", duration_ms=round(duration_ms, 2))
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers[_HEADER] = request_id
        _logger.info(
            "request_handled",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
