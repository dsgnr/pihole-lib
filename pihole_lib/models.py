"""Data models for Pi-hole API responses."""

from enum import Enum

from pydantic import BaseModel, Field


class ListType(str, Enum):
    """Pi-hole list types."""

    ALLOW = "allow"
    BLOCK = "block"


class PiHoleList(BaseModel):
    """Pi-hole domain list.

    Attributes:
        address: Address of the list.
        type: Type of list (allow or block).
        comment: User-provided free-text comment for this list.
        groups: Array of group IDs.
        enabled: Status of domain.
        id: Database ID.
        date_added: Unix timestamp of item addition.
        date_modified: Unix timestamp of last item modification.
        date_updated: Unix timestamp of last update of list content.
        number: Number of VALID domains on this list.
        invalid_domains: Number of INVALID domains on this list.
        abp_entries: Number of ABP entries on this list.
        status: List status.
    """

    address: str = Field(..., description="Address of the list")
    type: ListType = Field(..., description="Type of list")
    comment: str | None = Field(
        None, description="User-provided free-text comment for this list"
    )
    groups: list[int] = Field(..., description="Array of group IDs")
    enabled: bool = Field(True, description="Status of domain")
    id: int = Field(..., description="Database ID")
    date_added: int = Field(..., description="Unix timestamp of item addition")
    date_modified: int = Field(
        ..., description="Unix timestamp of last item modification"
    )
    date_updated: int = Field(
        ..., description="Unix timestamp of last update of list content"
    )
    number: int = Field(..., description="Number of VALID domains on this list")
    invalid_domains: int = Field(
        ..., description="Number of INVALID domains on this list"
    )
    abp_entries: int = Field(..., description="Number of ABP entries on this list")
    status: int = Field(..., description="List status")


class LoginInfo(BaseModel):
    """Pi-hole login page information.

    Attributes:
        https_port: HTTPS port of the Pi-hole webserver (0 if disabled).
        dns: Whether the DNS server is up and running. False only in failed state.
    """

    https_port: int = Field(
        ..., description="HTTPS port of the Pi-hole webserver (0 if disabled)"
    )
    dns: bool = Field(..., description="Whether the DNS server is up and running")


class ClientHeader(BaseModel):
    """HTTP header from client request.

    Attributes:
        name: Header name.
        value: Header value.
    """

    name: str = Field(..., description="Header name")
    value: str = Field(..., description="Header value")


class ClientInfo(BaseModel):
    """Pi-hole client request information.

    Attributes:
        remote_addr: Client's remote IP address.
        http_version: HTTP version used by client.
        method: HTTP method used.
        headers: List of HTTP headers sent by client.
    """

    remote_addr: str = Field(..., description="Client's remote IP address")
    http_version: str = Field(..., description="HTTP version used by client")
    method: str = Field(..., description="HTTP method used")
    headers: list[ClientHeader] = Field(..., description="HTTP headers sent by client")


class DatabaseUser(BaseModel):
    """Database file user information.

    Attributes:
        uid: User ID.
        name: User name.
        info: Additional user information.
    """

    uid: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    info: str = Field(..., description="Additional user information")


class DatabaseGroup(BaseModel):
    """Database file group information.

    Attributes:
        gid: Group ID.
        name: Group name.
    """

    gid: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")


class DatabaseOwner(BaseModel):
    """Database file ownership information.

    Attributes:
        user: User information.
        group: Group information.
    """

    user: DatabaseUser = Field(..., description="User information")
    group: DatabaseGroup = Field(..., description="Group information")


class DatabaseInfo(BaseModel):
    """Pi-hole database information.

    Attributes:
        size: Database file size in bytes.
        type: File type description.
        mode: File permissions.
        atime: Last access time (Unix timestamp).
        mtime: Last modification time (Unix timestamp).
        ctime: Creation time (Unix timestamp).
        owner: File ownership information.
        queries: Number of queries in memory.
        earliest_timestamp: Earliest query timestamp in memory.
        queries_disk: Number of queries on disk.
        earliest_timestamp_disk: Earliest query timestamp on disk.
        sqlite_version: SQLite version.
    """

    size: int = Field(..., description="Database file size in bytes")
    type: str = Field(..., description="File type description")
    mode: str = Field(..., description="File permissions")
    atime: int = Field(..., description="Last access time (Unix timestamp)")
    mtime: int = Field(..., description="Last modification time (Unix timestamp)")
    ctime: int = Field(..., description="Creation time (Unix timestamp)")
    owner: DatabaseOwner = Field(..., description="File ownership information")
    queries: int = Field(..., description="Number of queries in memory")
    earliest_timestamp: int = Field(
        ..., description="Earliest query timestamp in memory"
    )
    queries_disk: int = Field(..., description="Number of queries on disk")
    earliest_timestamp_disk: int = Field(
        ..., description="Earliest query timestamp on disk"
    )
    sqlite_version: str = Field(..., description="SQLite version")


class TeleporterGravityOptions(BaseModel):
    """Teleporter gravity database import options.

    Attributes:
        group: Whether to import groups.
        adlist: Whether to import adlists.
        adlist_by_group: Whether to import adlist-group associations.
        domainlist: Whether to import domain lists.
        domainlist_by_group: Whether to import domainlist-group associations.
        client: Whether to import clients.
        client_by_group: Whether to import client-group associations.
    """

    group: bool = Field(default=True, description="Whether to import groups")
    adlist: bool = Field(default=True, description="Whether to import adlists")
    adlist_by_group: bool = Field(
        default=True, description="Whether to import adlist-group associations"
    )
    domainlist: bool = Field(default=True, description="Whether to import domain lists")
    domainlist_by_group: bool = Field(
        default=True, description="Whether to import domainlist-group associations"
    )
    client: bool = Field(default=True, description="Whether to import clients")
    client_by_group: bool = Field(
        default=True, description="Whether to import client-group associations"
    )


class TeleporterImportOptions(BaseModel):
    """Pi-hole Teleporter import options.

    Attributes:
        config: Whether to import configuration files.
        dhcp_leases: Whether to import DHCP leases.
        gravity: Gravity database import options.
    """

    config: bool = Field(
        default=True, description="Whether to import configuration files"
    )
    dhcp_leases: bool = Field(default=True, description="Whether to import DHCP leases")
    gravity: TeleporterGravityOptions = Field(
        default_factory=lambda: TeleporterGravityOptions(),
        description="Gravity database import options",
    )


class AddListRequest(BaseModel):
    """Request model for adding a new Pi-hole list.

    Attributes:
        address: Address of the list (URL, IP, MAC address, hostname, or interface).
        comment: Optional user-provided comment for this list.
        groups: Array of group IDs (defaults to [0] for default group).
        enabled: Whether the list should be enabled (defaults to True).
    """

    address: str = Field(..., description="Address of the list")
    comment: str | None = Field(None, description="Optional comment for this list")
    groups: list[int] = Field(default=[0], description="Array of group IDs")
    enabled: bool = Field(default=True, description="Whether the list is enabled")


class PiHoleAuthSession(BaseModel):
    """Pi-hole authentication session data.

    Attributes:
        valid: Whether session is valid.
        totp: Whether two-factor auth is enabled.
        sid: Session ID token.
        csrf: CSRF protection token.
        validity: Session duration in seconds.
        message: Optional message from Pi-hole.
    """

    valid: bool = Field(..., description="Whether session is valid")
    totp: bool = Field(..., description="Whether two-factor auth is enabled")
    sid: str = Field(..., description="Session ID token")
    csrf: str = Field(..., description="CSRF protection token")
    validity: int = Field(..., description="Session duration in seconds")
    message: str | None = Field(None, description="Optional message from Pi-hole")
