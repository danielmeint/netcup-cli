"""
Custom exceptions for netcup CLI.
"""

from typing import Optional


class NetcupError(Exception):
    """Base exception for all netcup CLI errors."""

    pass


class AuthenticationError(NetcupError):
    """Raised when authentication fails."""

    pass


class APIError(NetcupError):
    """Raised when the API returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ConfigurationError(NetcupError):
    """Raised when there's a configuration problem."""

    pass


class ValidationError(NetcupError):
    """Raised when input validation fails."""

    pass


class SessionExpiredError(AuthenticationError):
    """Raised when the API session has expired."""

    pass
