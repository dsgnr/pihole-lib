"""Exceptions for Pi-hole API interactions."""


class PiHoleAPIError(Exception):
    """Base exception for Pi-hole API errors.

    Attributes:
        message: Error description.
        status_code: HTTP status code if available.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize API error.

        Args:
            message: Error description.
            status_code: HTTP status code if available.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class PiHoleConnectionError(PiHoleAPIError):
    """Connection-related error."""

    pass


class PiHoleAuthenticationError(PiHoleAPIError):
    """Authentication-related error."""

    pass


class PiHoleServerError(PiHoleAPIError):
    """Server-side error."""

    pass
