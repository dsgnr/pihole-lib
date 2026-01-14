"""Utility functions for Pi-hole API interactions."""

from typing import TYPE_CHECKING, Any

import requests

from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError,
)

if TYPE_CHECKING:
    from pihole_lib.client import PiHoleClient

# Pre-computed error messages for common HTTP status codes
_CLIENT_ERROR_MESSAGES: dict[int, str] = {
    400: "Bad request",
    402: "Request failed",
    404: "Endpoint not found",
    429: "Too many requests",
}

# Status code sets for fast lookup
_AUTH_ERROR_CODES: frozenset[int] = frozenset((401, 403))
_SUCCESS_CODES: frozenset[int] = frozenset((200, 201, 204))


def handle_pihole_response(response: requests.Response) -> None:
    """Handle Pi-hole API response and raise appropriate exceptions.

    Args:
        response: The HTTP response from Pi-hole API.

    Raises:
        PiHoleAuthenticationError: Authentication failed or access denied.
        PiHoleServerError: Server error (5xx status codes).
        PiHoleAPIError: Other API errors (4xx status codes).
    """
    status_code = response.status_code

    if status_code in _SUCCESS_CODES:
        return  # Success, no error handling needed

    # Handle authentication-related errors (common in Pi-hole)
    if status_code in _AUTH_ERROR_CODES:
        if status_code == 401:
            raise PiHoleAuthenticationError("Invalid credentials")
        else:  # 403
            raise PiHoleAuthenticationError("Access denied")

    # Handle common client errors (4xx) with pre-computed messages
    if status_code in _CLIENT_ERROR_MESSAGES:
        try:
            error_message = response.json().get("error", {}).get("message")
        except (ValueError, requests.JSONDecodeError):
            error_message = None
        base_message = _CLIENT_ERROR_MESSAGES[status_code]
        raise PiHoleAPIError(
            f"{base_message}: {error_message}" if error_message else base_message
        )

    # Handle server errors (5xx)
    if status_code >= 500:
        raise PiHoleServerError(f"Server error: {status_code}")

    # Handle any other non-200 status codes
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise PiHoleAPIError(f"HTTP error: {e}") from e


def make_pihole_request(
    client: "PiHoleClient",
    method: str,
    endpoint: str,
    json: dict[str, Any] | list[dict[str, Any]] | None = None,
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


def check_api_errors(
    response_data: dict, item_name: str, operation: str = "process"
) -> None:
    """Check for API errors in the response and raise appropriate exceptions.

    Args:
        response_data: The response data from the API.
        item_name: The item name that was being processed.
        operation: The operation being performed (e.g., "create", "add").

    Raises:
        PiHoleServerError: If Pi-hole reports an error.
    """
    processed = response_data.get("processed")
    if processed and processed.get("errors"):
        errors = processed["errors"]
        for error in errors:
            if error.get("item") == item_name:
                error_msg = error.get("error", "Unknown error")
                raise PiHoleServerError(
                    f"Failed to {operation} '{item_name}': {error_msg}"
                )
