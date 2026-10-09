"""Pi-hole API client."""

import time
from functools import cached_property
from typing import Any

import requests

from pihole_lib.actions import PiHoleActions
from pihole_lib.backup import PiHoleBackup
from pihole_lib.clients import PiHoleClients
from pihole_lib.config import PiHoleConfig
from pihole_lib.dhcp import PiHoleDHCP
from pihole_lib.dns import PiHoleDNS
from pihole_lib.domains import PiHoleDomains
from pihole_lib.exceptions import (
    PiHoleAPIError,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
)
from pihole_lib.groups import PiHoleGroups
from pihole_lib.info import PiHoleInfo
from pihole_lib.lists import PiHoleLists
from pihole_lib.network import PiHoleNetwork
from pihole_lib.padd import PiHolePADD
from pihole_lib.stats import PiHoleStats
from pihole_lib.utils import make_pihole_request


class PiHoleClient:
    """Pi-hole API client.

    Handles authentication and session management for Pi-hole API interactions.
    Can be used as a context manager for automatic cleanup.

    Examples::

        # Basic usage with property access
        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            # Get system information
            login_info = client.info.get_login_info()

            # Perform actions
            for line in client.actions.update_gravity():
                print(line.strip())

            # Manage lists
            all_lists = client.lists.get_lists()

            # Configuration management
            current_config = client.config.get_config()

        # Alternative usage with explicit class imports
        from pihole_lib import PiHoleInfo, PiHoleActions

        with PiHoleClient("http://192.168.1.100", password="secret") as client:
            info = PiHoleInfo(client)
            actions = PiHoleActions(client)

    """

    DEFAULT_TIMEOUT = 30
    HEADER_SESSION_ID = "X-FTL-SID"

    def __init__(
        self,
        base_url: str,
        password: str,
        timeout: int | None = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize a Pi-hole client.

        Args:
            base_url: Pi-hole base URL (e.g., "http://192.168.1.100").
            password: Pi-hole admin password.
            timeout: Request timeout in seconds. Defaults to 30.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
        """
        self.base_url = base_url.rstrip("/")
        self._password = password
        self._session_id: str | None = None
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session: requests.Session | None = None

    def __enter__(self) -> "PiHoleClient":
        """Enter context manager and authenticate."""
        self._ensure_session()
        self.authenticate()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and clean up resources."""
        self.close()

    def _ensure_session(self) -> None:
        """Ensure HTTP session exists with optimized configuration."""
        if self._session is None:
            self._session = requests.Session()
            self._session.verify = self.verify_ssl

            adapter = requests.adapters.HTTPAdapter(
                pool_connections=1,
                pool_maxsize=10,
                max_retries=0,
            )
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)

        if self._session_id:
            self._session.headers[self.HEADER_SESSION_ID] = self._session_id

    def close(self) -> None:
        """Close session and clean up resources."""
        if self._session_id:
            self._delete_session()
        if self._session:
            self._session.close()
            self._session = None

    _AUTH_CONNECT_RETRIES = 5
    _AUTH_CONNECT_RETRY_DELAY = 2.0

    def _post_auth(self) -> "requests.Response":
        """POST to /api/auth, retrying transient failures.

        Pi-hole can briefly refuse TCP connections while FTL is restarting
        (for example after a config change) and rate limits repeated logins
        with a 429 response. Both are retried a handful of times so a short
        outage doesn't permanently break the client for the caller. Any other
        API error is raised immediately.
        """
        last_error: PiHoleAPIError | None = None
        for attempt in range(self._AUTH_CONNECT_RETRIES):
            try:
                return make_pihole_request(
                    self,
                    "POST",
                    "/api/auth",
                    json={"password": self._password},
                )
            except PiHoleConnectionError as exc:
                last_error = exc
                # Drop any stale keep-alive sockets before retrying.
                if self._session is not None:
                    self._session.close()
                    self._session = None
                self._ensure_session()
            except PiHoleAPIError as exc:
                if exc.status_code != 429:
                    raise
                last_error = exc
            if attempt < self._AUTH_CONNECT_RETRIES - 1:
                time.sleep(self._AUTH_CONNECT_RETRY_DELAY)

        assert last_error is not None
        raise last_error

    def authenticate(self) -> None:
        """Authenticate with Pi-hole."""
        self._ensure_session()

        response = self._post_auth()

        data = response.json()
        session = data.get("session", {})

        if not session.get("valid"):
            raise PiHoleAuthenticationError("Login failed")

        self._session_id = session.get("sid")
        if not self._session_id:
            raise PiHoleAuthenticationError("No session ID received")

        self._ensure_session()

    def _delete_session(self) -> None:
        """Delete Pi-hole session."""
        if not self._session_id or not self._session:
            return

        try:
            self._session.delete(
                f"{self.base_url}/api/auth",
                headers={self.HEADER_SESSION_ID: self._session_id},
                timeout=self.timeout,
            )
        except Exception:
            pass
        finally:
            self._session_id = None

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self._session_id is not None

    def get_session_id(self) -> str | None:
        """Get current session ID."""
        return self._session_id

    # API client sub-clients, created on first access

    @cached_property
    def info(self) -> PiHoleInfo:
        """Get Pi-hole info API client."""
        return PiHoleInfo(self)

    @cached_property
    def actions(self) -> PiHoleActions:
        """Get Pi-hole actions API client."""
        return PiHoleActions(self)

    @cached_property
    def backup(self) -> PiHoleBackup:
        """Get Pi-hole backup API client."""
        return PiHoleBackup(self)

    @cached_property
    def config(self) -> PiHoleConfig:
        """Get Pi-hole config API client."""
        return PiHoleConfig(self)

    @cached_property
    def dhcp(self) -> PiHoleDHCP:
        """Get Pi-hole dhcp API client."""
        return PiHoleDHCP(self)

    @cached_property
    def dns(self) -> PiHoleDNS:
        """Get Pi-hole dns API client."""
        return PiHoleDNS(self)

    @cached_property
    def lists(self) -> PiHoleLists:
        """Get Pi-hole lists API client."""
        return PiHoleLists(self)

    @cached_property
    def groups(self) -> PiHoleGroups:
        """Get Pi-hole groups API client."""
        return PiHoleGroups(self)

    @cached_property
    def padd(self) -> PiHolePADD:
        """Get Pi-hole padd API client."""
        return PiHolePADD(self)

    @cached_property
    def stats(self) -> PiHoleStats:
        """Get Pi-hole stats API client."""
        return PiHoleStats(self)

    @cached_property
    def domains(self) -> PiHoleDomains:
        """Get Pi-hole domains API client."""
        return PiHoleDomains(self)

    @cached_property
    def network(self) -> PiHoleNetwork:
        """Get Pi-hole network API client."""
        return PiHoleNetwork(self)

    @cached_property
    def clients(self) -> PiHoleClients:
        """Get Pi-hole clients API client."""
        return PiHoleClients(self)
