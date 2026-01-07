"""Constants for Pi-hole API interactions."""

# API Endpoints
API_AUTH = "/api/auth"
API_INFO_LOGIN = "/api/info/login"
API_INFO_CLIENT = "/api/info/client"
API_INFO_DATABASE = "/api/info/database"
API_INFO_FTL = "/api/info/ftl"
API_INFO_HOST = "/api/info/host"
API_INFO_MESSAGES = "/api/info/messages"
API_INFO_MESSAGES_COUNT = "/api/info/messages/count"
API_INFO_SYSTEM = "/api/info/system"
API_INFO_VERSION = "/api/info/version"
API_DHCP_LEASES = "/api/dhcp/leases"
API_PADD = "/api/padd"
API_TELEPORTER = "/api/teleporter"
API_LISTS = "/api/lists"
API_ACTION_GRAVITY = "/api/action/gravity"
API_ACTION_RESTART_DNS = "/api/action/restartdns"
API_ACTION_FLUSH_LOGS = "/api/action/flush/logs"
API_ACTION_FLUSH_NETWORK = "/api/action/flush/network"
API_CONFIG = "/api/config"
API_DNS_CONFIG = "/api/config/dns"
API_DNS_HOSTS = "/api/config/dns/hosts"
API_DNS_CNAME_RECORDS = "/api/config/dns/cnameRecords"
API_DNS_UPSTREAMS = "/api/config/dns/upstreams"
API_DNS_BLOCKING = "/api/dns/blocking"
API_GROUPS = "/api/groups"

# HTTP Headers
HEADER_SESSION_ID = "X-FTL-SID"

# Default Values
DEFAULT_TIMEOUT = 30
DEFAULT_GROUP_ID = 0

# File Extensions
ZIP_EXTENSION = ".zip"

# MIME Types
MIME_ZIP = "application/zip"
