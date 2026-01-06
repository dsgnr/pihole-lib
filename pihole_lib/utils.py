"""Utility functions for Pi-hole API interactions."""

from typing import TYPE_CHECKING, Any

import requests

from .exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)

if TYPE_CHECKING:
    from .client import PiHoleClient


def handle_pihole_response(response: requests.Response) -> None:
    """Handle Pi-hole API response and raise appropriate exceptions.

    Args:
        response: The HTTP response from Pi-hole API.

    Raises:
        PiHoleAuthenticationError: Authentication failed or access denied.
        PiHoleServerError: Server error (5xx status codes).
        PiHoleAPIError: Other API errors (4xx status codes).
    """
    if response.status_code == 200:
        return  # Success, no error handling needed

    # Handle authentication-related errors (common in Pi-hole)
    if response.status_code in (401, 403):
        if response.status_code == 401:
            raise PiHoleAuthenticationError("Invalid credentials")
        else:  # 403
            raise PiHoleAuthenticationError("Access denied")

    # Handle common client errors (4xx)
    client_error_messages: dict[int, str] = {
        400: "Bad request - missing parameter",
        402: "Request failed",
        404: "Endpoint not found",
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
    client: "PiHoleClient",
    method: str,
    endpoint: str,
    json: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    stream: bool = False,
) -> requests.Response:
    """Make a request to Pi-hole API with error handling.

    Args:
        client: The PiHoleClient instance to use for the request.
        method: HTTP method (GET, POST, etc.).
        endpoint: The API endpoint path (e.g., "/api/info/login").
        json: Optional JSON data to send in the request body.
        files: Optional files to upload.
        params: Optional query parameters to include in the URL.
        stream: Whether to stream the response. Defaults to False.

    Returns:
        The HTTP response object.

    Raises:
        PiHoleConnectionError: Connection failed.
        PiHoleAuthenticationError: Authentication failed or access denied.
        PiHoleServerError: Server error (5xx status codes).
        PiHoleAPIError: Other API errors (4xx status codes).
    """
    # Ensure the client has a session
    client._ensure_session()
    assert client._session is not None

    try:
        response = client._session.request(
            method,
            f"{client.base_url}{endpoint}",
            json=json,
            files=files,
            params=params,
            timeout=client.timeout,
            stream=stream,
        )
        handle_pihole_response(response)
        return response
    except requests.RequestException as e:
        raise PiHoleConnectionError(f"Connection failed: {e}") from e
