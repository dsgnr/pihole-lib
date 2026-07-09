"""Pi-hole API client."""

from typing import TYPE_CHECKING, Any

import requests

from pihole_lib.exceptions import PiHoleAuthenticationError, PiHoleConnectionError
from pihole_lib.utils import make_pihole_request

if TYPE_CHECKING:
    from pihole_lib.actions import PiHoleActions
    from pihole_lib.backup import PiHoleBackup
    from pihole_lib.clients import PiHoleClients
    from pihole_lib.config import PiHoleConfig
    from pihole_lib.dhcp import PiHoleDHCP
    from pihole_lib.dns import PiHoleDNS
    from pihole_lib.domains import PiHoleDomains
    from pihole_lib.groups import PiHoleGroups
    from pihole_lib.info import PiHoleInfo
    from pihole_lib.lists import PiHoleLists
    from pihole_lib.network import PiHoleNetwork
    from pihole_lib.padd import PiHolePADD
    from pihole_lib.stats import PiHoleStats


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

        # Cached API client instances
        self._info: PiHoleInfo | None = None
        self._actions: PiHoleActions | None = None
        self._backup: PiHoleBackup | None = None
        self._config: PiHoleConfig | None = None
        self._dhcp: PiHoleDHCP | None = None
        self._dns: PiHoleDNS | None = None
        self._lists: PiHoleLists | None = None
        self._groups: PiHoleGroups | None = None
        self._padd: PiHolePADD | None = None
        self._stats: PiHoleStats | None = None
        self._domains: PiHoleDomains | None = None
        self._network: PiHoleNetwork | None = None
        self._clients: PiHoleClients | None = None

    def __enter__(self) -> "PiHoleClient":
        """Enter context manager and authenticate."""
        self._ensure_session()
        self._authenticate()
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
        """POST to /api/auth with transient connection retry.

        Pi-hole can briefly refuse TCP connections while FTL is restarting
        (for example after a config change). Retry the auth request a
        handful of times so a short outage doesn't permanently break the
        client for the caller.
        """
        import time

        last_error: PiHoleConnectionError | None = None
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
                if attempt == self._AUTH_CONNECT_RETRIES - 1:
                    break
                # Drop any stale keep-alive sockets before retrying.
                if self._session is not None:
                    self._session.close()
                    self._session = None
                self._ensure_session()
                time.sleep(self._AUTH_CONNECT_RETRY_DELAY)

        assert last_error is not None
        raise last_error

    def _authenticate(self) -> None:
        """Authenticate with Pi-hole."""
        self._ensure_session()

        response = self._post_auth()

        # Handle rate limiting with retry
        if response.status_code == 429:
            import time

            time.sleep(1)
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

    # API client properties with lazy loading

    @property
    def info(self) -> "PiHoleInfo":
        """Get Pi-hole info API client."""
        if self._info is None:
            from pihole_lib.info import PiHoleInfo

            self._info = PiHoleInfo(self)
        return self._info

    @property
    def actions(self) -> "PiHoleActions":
        """Get Pi-hole actions API client."""
        if self._actions is None:
            from pihole_lib.actions import PiHoleActions

            self._actions = PiHoleActions(self)
        return self._actions

    @property
    def backup(self) -> "PiHoleBackup":
        """Get Pi-hole backup API client."""
        if self._backup is None:
            from pihole_lib.backup import PiHoleBackup

            self._backup = PiHoleBackup(self)
        return self._backup

    @property
    def config(self) -> "PiHoleConfig":
        """Get Pi-hole config API client."""
        if self._config is None:
            from pihole_lib.config import PiHoleConfig

            self._config = PiHoleConfig(self)
        return self._config

    @property
    def dhcp(self) -> "PiHoleDHCP":
        """Get Pi-hole DHCP API client."""
        if self._dhcp is None:
            from pihole_lib.dhcp import PiHoleDHCP

            self._dhcp = PiHoleDHCP(self)
        return self._dhcp

    @property
    def dns(self) -> "PiHoleDNS":
        """Get Pi-hole DNS API client."""
        if self._dns is None:
            from pihole_lib.dns import PiHoleDNS

            self._dns = PiHoleDNS(self)
        return self._dns

    @property
    def lists(self) -> "PiHoleLists":
        """Get Pi-hole lists API client."""
        if self._lists is None:
            from pihole_lib.lists import PiHoleLists

            self._lists = PiHoleLists(self)
        return self._lists

    @property
    def groups(self) -> "PiHoleGroups":
        """Get Pi-hole groups API client."""
        if self._groups is None:
            from pihole_lib.groups import PiHoleGroups

            self._groups = PiHoleGroups(self)
        return self._groups

    @property
    def padd(self) -> "PiHolePADD":
        """Get Pi-hole PADD API client."""
        if self._padd is None:
            from pihole_lib.padd import PiHolePADD

            self._padd = PiHolePADD(self)
        return self._padd

    @property
    def stats(self) -> "PiHoleStats":
        """Get Pi-hole stats API client."""
        if self._stats is None:
            from pihole_lib.stats import PiHoleStats

            self._stats = PiHoleStats(self)
        return self._stats

    @property
    def domains(self) -> "PiHoleDomains":
        """Get Pi-hole domains API client."""
        if self._domains is None:
            from pihole_lib.domains import PiHoleDomains

            self._domains = PiHoleDomains(self)
        return self._domains

    @property
    def network(self) -> "PiHoleNetwork":
        """Get Pi-hole network API client."""
        if self._network is None:
            from pihole_lib.network import PiHoleNetwork

            self._network = PiHoleNetwork(self)
        return self._network

    @property
    def clients(self) -> "PiHoleClients":
        """Get Pi-hole clients API client."""
        if self._clients is None:
            from pihole_lib.clients import PiHoleClients

            self._clients = PiHoleClients(self)
        return self._clients
