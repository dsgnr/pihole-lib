"""Utility functions for Pi-hole API interactions."""

from typing import Any, Dict, Optional

import requests

from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)


def handle_pihole_response(
    response: requests.Response,
    endpoint_name: Optional[str] = None,
) -> None:
    """Handle Pi-hole API response and raise appropriate exceptions.

    Args:
        response: The HTTP response from Pi-hole API.
        endpoint_name: Optional name of the endpoint for error messages.

    Raises:
        PiHoleAuthenticationError: Authentication failed or access denied.
        PiHoleServerError: Server error (5xx status codes).
        PiHoleAPIError: Other API errors (4xx status codes).
    """
    if response.status_code == 200:
        return  # Success, no error handling needed

    # Build error message prefix
    endpoint_prefix = f"{endpoint_name} " if endpoint_name else ""

    # Handle authentication-related errors (common in Pi-hole)
    if response.status_code in (401, 403):
        if response.status_code == 401:
            raise PiHoleAuthenticationError("Invalid credentials")
        else:  # 403
            raise PiHoleAuthenticationError("Access denied")

    # Handle common client errors (4xx)
    client_error_messages: Dict[int, str] = {
        400: "Bad request - missing parameter",
        402: "Request failed",
        404: f"{endpoint_prefix}endpoint not found",
        429: "Too many requests - rate limited",
    }

    if response.status_code in client_error_messages:
        raise PiHoleAPIError(client_error_messages[response.status_code])

    # Handle server errors (5xx)
    if response.status_code >= 500:
        raise PiHoleServerError(f"Server error: {response.status_code}")

    # Handle any other non-200 status codes
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise PiHoleAPIError(f"HTTP error: {e}") from e


def make_pihole_request(
    session: requests.Session,
    method: str,
    url: str,
    endpoint_name: Optional[str] = None,
    **kwargs: Any,
) -> requests.Response:
    """Make a request to Pi-hole API with error handling.

    Args:
        session: The requests session to use.
        method: HTTP method (GET, POST, etc.).
        url: The full URL to request.
        endpoint_name: Optional name of the endpoint for error messages.
        **kwargs: Additional arguments to pass to the request method.

    Returns:
        The HTTP response object.

    Raises:
        PiHoleConnectionError: Connection failed.
        PiHoleAuthenticationError: Authentication failed or access denied.
        PiHoleServerError: Server error (5xx status codes).
        PiHoleAPIError: Other API errors (4xx status codes).
    """
    try:
        response = session.request(method, url, **kwargs)
        handle_pihole_response(response, endpoint_name)
        return response
    except requests.RequestException as e:
        raise PiHoleConnectionError(f"Connection failed: {e}") from e
