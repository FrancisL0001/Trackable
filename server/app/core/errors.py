"""Domain-level exceptions mapped to HTTP responses in the API layer."""
from __future__ import annotations


class TrackableError(Exception):
    """Base class for expected, handled application errors."""

    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(TrackableError):
    status_code = 404


class ConflictError(TrackableError):
    status_code = 409


class AuthError(TrackableError):
    status_code = 401


class IntegrationError(TrackableError):
    status_code = 502
