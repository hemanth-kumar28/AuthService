"""
Centralized error handling system.

Custom exception classes + global exception handler registration.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ── Custom Exceptions ──────────────────────────────────────────


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        status_code: int = 500,
        message: str = "Internal server error",
        details: Any = None,
    ):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__(status_code=404, message=message, details=details)


class UnauthorizedError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid credentials", details: Any = None):
        super().__init__(status_code=401, message=message, details=details)


class ForbiddenError(AppException):
    """Permission denied."""

    def __init__(self, message: str = "Permission denied", details: Any = None):
        super().__init__(status_code=403, message=message, details=details)


class ConflictError(AppException):
    """Resource already exists."""

    def __init__(self, message: str = "Resource already exists", details: Any = None):
        super().__init__(status_code=409, message=message, details=details)


class BadRequestError(AppException):
    """Invalid request."""

    def __init__(self, message: str = "Bad request", details: Any = None):
        super().__init__(status_code=400, message=message, details=details)


# ── Error Response Builder ─────────────────────────────────────


def _error_response(status_code: int, message: str, details: Any = None) -> JSONResponse:
    """Build a consistent JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": status_code,
                "message": message,
                "details": details,
            },
        },
    )


# ── Global Exception Handlers ─────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException: %s (status=%d)", exc.message, exc.status_code)
        return _error_response(exc.status_code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Flatten Pydantic validation errors into a readable list
        error_details = []
        for err in exc.errors():
            field = " → ".join(str(loc) for loc in err["loc"])
            error_details.append({"field": field, "message": err["msg"]})
        logger.warning("Validation error: %s", error_details)
        return _error_response(422, "Validation error", error_details)

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Never expose internal errors to the client
        logger.exception("Unhandled exception: %s", exc)
        return _error_response(500, "Internal server error")
