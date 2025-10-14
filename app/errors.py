from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    VALIDATION = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INTERNAL = "internal_error"


@dataclass
class AppError(Exception):
    """Domain-level error; mapped to HTTP by a global handler."""

    status: int
    code: ErrorCode
    title: str
    detail: str | None = None
    extra: dict[str, Any] | None = None


# Convenience domain errors
class DomainValidationError(AppError):
    def __init__(self, detail: str, extra: dict[str, Any] | None = None):
        super().__init__(
            status=400,
            code=ErrorCode.VALIDATION,
            title="Validation error",
            detail=detail,
            extra=extra,
        )


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            status=404,
            code=ErrorCode.NOT_FOUND,
            title=f"{resource} not found",
            detail=f"{resource} with id={resource_id} not found",
        )


class ConflictError(AppError):
    def __init__(self, detail: str):
        super().__init__(status=409, code=ErrorCode.CONFLICT, title="Conflict", detail=detail)
