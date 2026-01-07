# Pi-hole Python Library

A non-official Python library for interacting with Pi-hole's API. This library provides a clean, Pythonic interface to manage your Pi-hole instance programmatically.

This library is pretty much a scrape of the Pi-hole docs found at `<pihole-instance>/api/docs`.

## Table of Contents

- [Disclaimer](#disclaimer)
- [Features](#features)
- [Supported Pi-hole Versions](#supported-pi-hole-versions)
- [Installation](#installation)
- [Usage](#usage)
  - [Connect to your Pi-hole](#connect-to-your-pi-hole)
  - [Get login page information](#get-login-page-information)
  - [Backup and restore operations](#backup-and-restore-operations)
  - [Domain lists management](#domain-lists-management)
  - [Configuration management](#configuration-management)
  - [Actions and maintenance](#actions-and-maintenance)
  - [Manual session control](#manual-session-control)
  - [Error Handling](#error-handling)
  - [Configuration Options](#configuration-options)
- [Development and Testing](#development-and-testing)
  - [Development Setup](#development-setup)
  - [Running the tests](#running-the-tests)
  - [Test setup](#test-setup)
  - [Other useful commands](#other-useful-commands)
- [API Reference](#api-reference)
  - [PiHoleClient](#piholeclient)
  - [Exception Classes](#exception-classes)
  - [Data Models](#data-models)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## Disclaimer

This is an unofficial library and is not affiliated with or endorsed by the Pi-hole project. Pi-hole is a trademark of Pi-hole LLC.

I made this tool to use in my homelab. Feel free to contribute, but use at your own risk.

## Features

| Feature Category | Feature | Status |
|------------------|---------|--------|
| **Testing** | Integration tests against a live Pi-hole instance | ✅ |
| | Lint and type checking | ✅ |
| **Authentication** | Session-based authentication | ✅ |
| | Automatic session management | ✅ |
| | Context manager support | ✅ |
| **Information** | Login page information | ✅ |
| | Client information | ✅ |
| | Database information | ✅ |
| | FTL runtime information | ✅ |
| | Host system information | ✅ |
| | Version information | ✅ |
| | System resource information | ✅ |
| | System messages | ✅ |
| | System messages count | ✅ |
| **Error Handling** | Comprehensive error handling | ✅ |
| | Specific exception types | ✅ |
| **Metrics** | Query statistics | 📋 |
| | Top clients/domains | 📋 |
| | Query types over time | 📋 |
| **DNS Control** | Enable/disable Pi-hole | 📋 |
| | Restart DNS resolver | 📋 |
| **Domain Management** | Add/remove domains | 📋 |
| | Exact/regex domain matching | 📋 |
| | Domain comments and descriptions | 📋 |
| **List Management** | Get domain lists | ✅ |
| | Filter lists by type (allow/block) | ✅ |
| | Filter lists by name | ✅ |
| | List metadata and statistics | ✅ |
| | Add lists | ✅ |
| | Remove lists | ✅ |
| | Regex list management | 📋 |
| | Import/export lists | 📋 |
| **Pi-hole Configuration** | Network settings | 📋 |
| | DNS settings | 📋 |
| | Web interface settings | 📋 |
| | Privacy settings | 📋 |
| | Get configuration | ✅ |
| **Actions** | Update gravity | ✅ |
| | Restart DNS | ✅ |
| | Flush logs | ✅ |
| | Flush network table | ✅ |
| **Teleporter** | Backup configuration | ✅ |
| | Restore from backup | ✅ |
| **DHCP** | Get active DHCP leases | ✅ |
| | Delete DHCP lease | ✅ |
| **PADD** | Get dashboard data | ✅ |

## Supported Pi-hole Versions

This library is designed to work with Pi-hole v6.0+ and uses the endpoints defined at `/api/docs`. It's tested against the latest Pi-hole releases to ensure compatibility.

## Installation

```bash
pip install pihole-lib
```

## Usage

### Connect to your Pi-hole

```python
from pihole_lib import PiHoleClient

# Connect to your Pi-hole
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    print(f"Connected with session: {client.get_session_id()}")

    # Update gravity database
    from pihole_lib import PiHoleActions
    actions = PiHoleActions(client)
    for line in actions.update_gravity():
        print(line.strip())

    # Session closed when exiting context
```

### Get login page information

```python
from pihole_lib import PiHoleClient, PiHoleInfo

# Create a client
client = PiHoleClient("http://192.168.1.100", password="your-password")

# Use the info class with the client (no authentication required for login info)
info = PiHoleInfo(client)
login_info = info.get_login_info()

print(f"HTTPS Port: {login_info.https_port}")  # 443 or 0 if disabled
print(f"DNS Status: {login_info.dns}")         # True if DNS is running

# Get client request information
client_info = info.get_client_info()
print(f"Client IP: {client_info.remote_addr}")
print(f"HTTP Version: {client_info.http_version}")
print(f"Method: {client_info.method}")
print(f"Headers: {len(client_info.headers)} headers")
for header in client_info.headers:
    print(f"  {header.name}: {header.value}")

# Get database information
database_info = info.get_database_info()
print(f"Database size: {database_info.size} bytes")
print(f"SQLite version: {database_info.sqlite_version}")
print(f"Queries in memory: {database_info.queries}")
print(f"Queries on disk: {database_info.queries_disk}")
print(f"File owner: {database_info.owner.user.name}")
print(f"File group: {database_info.owner.group.name}")
print(f"File permissions: {database_info.mode}")

# Get FTL runtime information
ftl_info = info.get_ftl_info()
print(f"Process ID: {ftl_info.ftl.pid}")
print(f"Uptime: {ftl_info.ftl.uptime} seconds")
print(f"Memory usage: {ftl_info.ftl.mem_percent}%")
print(f"CPU usage: {ftl_info.ftl.cpu_percent}%")
print(f"Gravity domains: {ftl_info.ftl.database.gravity}")
print(f"Total clients: {ftl_info.ftl.clients.total}")
print(f"Active clients: {ftl_info.ftl.clients.active}")
print(f"DNS queries forwarded: {ftl_info.ftl.dnsmasq.dns_queries_forwarded}")

# Get host system information
host_info = info.get_host_info()
print(f"Hostname: {host_info.host.uname.nodename}")
print(f"OS: {host_info.host.uname.sysname} {host_info.host.uname.release}")
print(f"Architecture: {host_info.host.uname.machine}")
print(f"Hardware model: {host_info.host.model}")
if host_info.host.dmi.sys.vendor:
    print(f"System vendor: {host_info.host.dmi.sys.vendor}")

# Get version information
version_info = info.get_version_info()
print(f"Pi-hole Core: {version_info.version.core.local.version}")
print(f"Web Interface: {version_info.version.web.local.version}")
print(f"FTL: {version_info.version.ftl.local.version}")
print(f"Docker: {version_info.version.docker.local}")

# Check if updates are available
if version_info.version.core.local.version != version_info.version.core.remote.version:
    print("Core update available!")

# Get system resource information
system_info = info.get_system_info()
print(f"Uptime: {system_info.system.uptime} seconds")
print(f"RAM Usage: {system_info.system.memory.ram.percent_used:.1f}%")
print(f"CPU Cores: {system_info.system.cpu.nprocs}")
print(f"CPU Usage: {system_info.system.cpu.percent_cpu:.1f}%")
print(f"Processes: {system_info.system.procs}")
print(f"FTL Memory: {system_info.system.ftl.percent_mem:.2f}%")
print(f"Load Average: {system_info.system.cpu.load.raw}")

# Get system messages
messages_info = info.get_messages()
print(f"Total messages: {len(messages_info.messages)}")
for message in messages_info.messages:
    print(f"[{message.type.upper()}] {message.plain}")
    print(f"  ID: {message.id}, Time: {message.timestamp}")

# Get messages count
messages_count = info.get_messages_count()
print(f"Message count: {messages_count.count}")

client.close()

# Or use within client context manager
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    info = PiHoleInfo(client)
    login_info = info.get_login_info()
    print(f"HTTPS Port: {login_info.https_port}")

    client_info = info.get_client_info()
    print(f"Client IP: {client_info.remote_addr}")

    database_info = info.get_database_info()
    print(f"Database size: {database_info.size} bytes")

    ftl_info = info.get_ftl_info()
    print(f"Process ID: {ftl_info.ftl.pid}")

    host_info = info.get_host_info()
    print(f"Hostname: {host_info.host.uname.nodename}")

    version_info = info.get_version_info()
    print(f"Pi-hole Core: {version_info.version.core.local.version}")

    system_info = info.get_system_info()
    print(f"RAM Usage: {system_info.system.memory.ram.percent_used:.1f}%")

    messages_info = info.get_messages()
    print(f"Messages: {len(messages_info.messages)}")

    messages_count = info.get_messages_count()
    print(f"Message count: {messages_count.count}")
```

### Backup and restore operations

```python
from pihole_lib import PiHoleClient, PiHoleBackup, TeleporterImportOptions

# Backup and restore with authentication
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    backup = PiHoleBackup(client)

    # Export current Pi-hole configuration (filename auto-generated with timestamp)
    backup_file = backup.export_backup("/path/to/backups")
    print(f"Backup created: {backup_file}")
    # Example output: /path/to/backups/pi-hole_pihole_teleporter_2024-01-15_14-30-25_UTC.zip

    # Import/restore from backup with custom options
    import_options = TeleporterImportOptions(
        config=True,           # Import configuration files
        dhcp_leases=False,     # Skip DHCP leases
        gravity=TeleporterGravityOptions(
            group=True,        # Import groups
            adlist=True,       # Import adlists
            client=False       # Skip clients
        )
    )

    result = backup.import_backup(backup_file, import_options)
    print(f"Imported {len(result)} files")
    for file in result:
        print(f"  - {file}")
```

### Domain lists management

```python
from pihole_lib import PiHoleClient, PiHoleLists, ListType

# Manage domain lists (blocklists and allowlists)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    lists = PiHoleLists(client)

    # Get all lists
    all_lists = lists.get_lists()
    print(f"Found {len(all_lists)} total lists")

    # Get only block lists
    block_lists = lists.get_lists(list_type=ListType.BLOCK)
    print(f"Found {len(block_lists)} block lists")

    # Get only allow lists
    allow_lists = lists.get_lists(list_type=ListType.ALLOW)
    print(f"Found {len(allow_lists)} allow lists")

    # Get specific list by name
    specific_list = lists.get_lists(list_name="my_blocklist")
    if specific_list:
        list_info = specific_list[0]
        print(f"List: {list_info.address}")
        print(f"Type: {list_info.type.value}")
        print(f"Enabled: {list_info.enabled}")
        print(f"Domains: {list_info.number}")
        print(f"Invalid domains: {list_info.invalid_domains}")

    # Add a new blocklist
    new_lists = lists.add_list(
        address="https://hosts-file.net/ad_servers.txt",
        list_type=ListType.BLOCK,
        comment="Ad servers blocklist",
        groups=[0],
        enabled=True
    )
    print(f"Added list, API returned {len(new_lists)} lists")

    # Add an allowlist for a specific domain
    allow_lists = lists.add_list(
        address="example.com",
        list_type=ListType.ALLOW,
        comment="Allow example.com"
    )
    print(f"Added allowlist, API returned {len(allow_lists)} lists")

    # Delete a blocklist
    success = lists.delete_list(
        address="https://hosts-file.net/ad_servers.txt",
        list_type=ListType.BLOCK
    )
    print(f"Blocklist deletion successful: {success}")

    # Delete an allowlist
    success = lists.delete_list(
        address="example.com",
        list_type=ListType.ALLOW
    )
    print(f"Allowlist deletion successful: {success}")
```

### Configuration management

```python
from pihole_lib import PiHoleClient, PiHoleConfig

# Manage Pi-hole configuration
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    config = PiHoleConfig(client)

    # Get current configuration
    current_config = config.get_config()

    # Access DNS settings
    dns_config = current_config['dns']
    print(f"Upstream DNS servers: {dns_config['upstreams']}")
    print(f"Query logging enabled: {dns_config['queryLogging']}")
    print(f"DNS port: {dns_config['port']}")

    # Access DHCP settings
    dhcp_config = current_config['dhcp']
    print(f"DHCP server active: {dhcp_config['active']}")

    # Access web server settings
    web_config = current_config['webserver']
    print(f"Web interface domain: {web_config['domain']}")

    # Access file locations
    files_config = current_config['files']
    print(f"Database location: {files_config['database']}")
    print(f"Log file location: {files_config['log']['ftl']}")

    # Get specific configuration elements (more efficient)
    # Get only DNS configuration
    dns_only = config.get_config('dns')
    print(f"DNS upstreams: {dns_only['dns']['upstreams']}")

    # Get only upstream DNS servers
    upstreams_only = config.get_config('dns/upstreams')
    print(f"Upstreams: {upstreams_only['dns']['upstreams']}")

    # Get only DHCP configuration
    dhcp_only = config.get_config('dhcp')
    print(f"DHCP active: {dhcp_only['dhcp']['active']}")

    # Get only webserver configuration
    web_only = config.get_config('webserver')
    print(f"Web domain: {web_only['webserver']['domain']}")
```

### Actions and maintenance

```python
from pihole_lib import PiHoleClient, PiHoleActions

# Perform Pi-hole maintenance actions
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    actions = PiHoleActions(client)

    # Update gravity database (download and process all adlists)
    print("Updating gravity database...")
    for line in actions.update_gravity():
        print(line.strip())

    # Update gravity with colored output (useful for terminal display)
    print("Updating gravity with colored output...")
    for line in actions.update_gravity(color=True):
        print(line.strip())

    # Restart DNS service
    print("Restarting DNS service...")
    success = actions.restart_dns()
    print(f"DNS restart: {'success' if success else 'failed'}")

    # Flush DNS logs
    print("Flushing DNS logs...")
    success = actions.flush_logs()
    print(f"DNS logs flush: {'success' if success else 'failed'}")

    # Flush network table
    print("Flushing network table...")
    success = actions.flush_network()
    print(f"Network table flush: {'success' if success else 'failed'}")
```

### DHCP management

```python
from pihole_lib import PiHoleClient, PiHoleDHCP

# Manage DHCP leases
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    dhcp = PiHoleDHCP(client)

    # Get currently active DHCP leases
    leases = dhcp.get_leases()
    print(f"Found {len(leases.leases)} active DHCP leases")

    for lease in leases.leases:
        print(f"Device: {lease.name}")
        print(f"IP: {lease.ip}")
        print(f"MAC: {lease.hwaddr}")
        print(f"Client ID: {lease.clientid}")

    # Delete a specific DHCP lease
    if leases.leases:
        first_lease_ip = leases.leases[0].ip
        success = dhcp.delete_lease(first_lease_ip)
        print(f"Deleted lease for {first_lease_ip}: {'success' if success else 'failed'}")
```

### PADD dashboard data

```python
from pihole_lib import PiHoleClient, PiHolePADD

# Get comprehensive dashboard data
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    padd = PiHolePADD(client)

    # Get dashboard data
    dashboard = padd.get_dashboard_data()

    print(f"Pi-hole Status: {dashboard.blocking}")
    print(f"Active clients: {dashboard.active_clients}")
    print(f"Gravity database size: {dashboard.gravity_size}")

    # Query statistics
    print(f"Total queries: {dashboard.queries.total}")
    print(f"Blocked queries: {dashboard.queries.blocked}")
    print(f"Percent blocked: {dashboard.queries.percent_blocked}%")

    # System information
    print(f"System uptime: {dashboard.system.uptime} seconds")
    print(f"Memory usage: {dashboard.system.memory.ram.percent_used}%")
    print(f"CPU usage: {dashboard.system.cpu.percent_cpu}%")

    # Network information
    print(f"IPv4 address: {dashboard.iface.v4.addr}")
    print(f"Gateway: {dashboard.iface.v4.gw_addr}")

    # Version information
    print(f"Pi-hole core: {dashboard.version.core.local.version}")
    print(f"FTL version: {dashboard.version.ftl.local.version}")

    # Configuration summary
    print(f"DHCP active: {dashboard.config.dhcp_active}")
    print(f"DNS port: {dashboard.config.dns_port}")
```

### Manual session control

If you need more control over the connection lifecycle:

```python
from pihole_lib import PiHoleClient

client = PiHoleClient("http://192.168.1.100", password="your-password")

try:
    # Set up the connection
    client._ensure_session()
    client._authenticate()

    if client.is_authenticated():
        print(f"Session ID: {client.get_session_id()}")

finally:
    # Close the session
    client.close()
```

### Error Handling

The library provides specific exceptions for different error scenarios:

```python
from pihole_lib import (
    PiHoleClient,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError
)

try:
    with PiHoleClient("http://192.168.1.100", password="wrong-password") as client:
        # Do a thing
        pass

except PiHoleAuthenticationError:
    print("Authentication failed - check your password")

except PiHoleConnectionError:
    print("Can't reach Pi-hole - check the URL and network connection")

except PiHoleServerError:
    print("Pi-hole server is experiencing issues")
```

### Configuration Options

Customise the client behavior for your specific setup:

```python
client = PiHoleClient(
    base_url="https://pihole.local",      # Your Pi-hole's address
    password="your-admin-password",       # Pi-hole admin password
    timeout=60,                           # Request timeout in seconds (default: 30) - maybe useful for remote instances?
    verify_ssl=False                      # SSL certificate verification (default: True)
)
```

## Development and Testing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dsgnr/pihole-lib.git
cd pihole-lib

# Install dependencies
poetry install

# Run tests
make test

# Run linting and type checking
make check
```

### Running the tests

The test suite combines unit tests and integration tests against the official Docker Pi-hole image from [https://github.com/pi-hole/docker-pi-hole](https://github.com/pi-hole/docker-pi-hole). Most tests run against the real Pi-hole instance to ensure authentic behavior.

```bash
# Start a test Pi-hole container
make docker-up

# Run all tests
make test

# Run tests with coverage report
make test-cov

# Clean up
make docker-down
```

### Test setup

The tests use these settings:
- Pi-hole URL: `http://localhost:8080`
- Admin password: `test-password-123`

### Other useful commands

```bash
make lint          # Check code style
make type-check    # Check types with mypy
make check         # Run linting, type checking, and tests
make format        # Auto-format code
```

## API Reference

### PiHoleClient

The main class for interacting with your Pi-hole.

**Methods:**
- `PiHoleClient(base_url, password, timeout=30, verify_ssl=True)` - Create a new client
- `is_authenticated()` - Check if currently authenticated with Pi-hole
- `get_session_id()` - Get the current session ID
- `close()` - Close the session and clean up resources

### PiHoleInfo

The info class for accessing Pi-hole information endpoints that don't require authentication.

**Methods:**
- `PiHoleInfo(client)` - Create a new info client using an existing PiHoleClient
- `get_login_info()` - Get login page information (HTTPS port, DNS status, processing time)
- `get_client_info()` - Get client request information (IP address, HTTP version, method, headers)
- `get_database_info()` - Get database information (file size, permissions, ownership, query counts, SQLite version)
- `get_ftl_info()` - Get FTL runtime information (process details, resource usage, database stats, dnsmasq stats)
- `get_host_info()` - Get host system information (uname details, hardware model, DMI/SMBIOS data)
- `get_version_info()` - Get version information (core, web, FTL, Docker versions with local/remote comparison)
- `get_system_info()` - Get system resource information (uptime, memory, CPU, processes, FTL resource usage)
- `get_messages()` - Get system messages (notifications, warnings, errors with plain text and HTML content)
- `get_messages_count()` - Get system messages count (efficient way to get just the message count)

### PiHoleBackup

The backup class for Pi-hole Teleporter operations (backup and restore).

**Methods:**
- `PiHoleBackup(client)` - Create a new backup client using an existing PiHoleClient
- `export_backup(backup_dir)` - Export Pi-hole configuration to a timestamped backup file in the specified directory
- `import_backup(backup_path, import_options=None)` - Import/restore from a backup file

### PiHoleLists

The lists class for Pi-hole domain list management (blocklists and allowlists).

**Methods:**
- `PiHoleLists(client)` - Create a new lists client using an existing PiHoleClient
- `get_lists(list_name=None, list_type=None)` - Get domain lists with optional filtering by name or type
- `add_list(address, list_type, comment=None, groups=None, enabled=True)` - Add a new domain list
- `delete_list(address, list_type)` - Delete a domain list. Returns True if successful, raises exceptions on failure.

**List Types:**
- `ListType.ALLOW` - Allow lists (domains that bypass blocking)
- `ListType.BLOCK` - Block lists (domains that are blocked)

### PiHoleConfig

The config class for Pi-hole configuration management.

**Methods:**
- `PiHoleConfig(client)` - Create a new config client using an existing PiHoleClient
- `get_config(element=None)` - Get the complete current configuration or a specific subset of your Pi-hole instance. If `element` is provided (e.g., 'dns', 'dns/upstreams', 'dhcp'), returns only that configuration subset. Returns a dictionary with sections like 'dns', 'dhcp', 'webserver', 'files', 'misc', and 'debug'.

### PiHoleActions

The actions class for Pi-hole maintenance and administrative operations.

**Methods:**
- `PiHoleActions(client)` - Create a new actions client using an existing PiHoleClient
- `update_gravity(color=False)` - Update Pi-hole's gravity database (adlists). Returns an iterator that yields lines of output as they're streamed from Pi-hole. Set `color=True` to include ANSI color escape codes in the output.
- `restart_dns()` - Restart Pi-hole's DNS service (pihole-FTL). Returns True if successful, False otherwise.
- `flush_logs()` - Flush Pi-hole's DNS logs, including emptying the log file and purging recent data from database and memory. Returns True if successful, False otherwise.
- `flush_network()` - Flush Pi-hole's network table, removing all known devices and their addresses. Returns True if successful, False otherwise.

### PiHoleDHCP

The DHCP class for Pi-hole DHCP lease management.

**Methods:**
- `PiHoleDHCP(client)` - Create a new DHCP client using an existing PiHoleClient
- `get_leases()` - Get currently active DHCP leases. Returns a DHCPLeasesInfo object containing a list of DHCPLease objects with information about each active lease including hostname, IP address, MAC address, client ID, and expiration time.
- `delete_lease(ip)` - Delete a currently active DHCP lease by IP address. Returns True if successful. Requires DHCP server to be enabled.

### PiHolePADD

The PADD class for Pi-hole dashboard data retrieval.

**Methods:**
- `PiHolePADD(client)` - Create a new PADD client using an existing PiHoleClient
- `get_dashboard_data()` - Get comprehensive Pi-hole dashboard data including query statistics, system information, network details, version information, and configuration summaries. Returns a PADDInfo object with all dashboard data.

**Context Manager:**
The client supports Python's `with` statement for automatic resource management:

```python
with PiHoleClient(base_url, password) as client:
    # Client is automatically authenticated
    # Session is automatically cleaned up on exit
    pass
```

### Exception Classes

- `PiHoleAPIError` - Base exception for all Pi-hole API related errors
- `PiHoleAuthenticationError` - Authentication failed or access denied
- `PiHoleConnectionError` - Cannot connect to Pi-hole (network/URL issues)
- `PiHoleServerError` - Pi-hole server returned an internal error

### Data Models

- `PiHoleAuthSession` - Represents a Pi-hole authentication session
- `LoginInfo` - Login page information including HTTPS port and DNS status
- `TeleporterImportOptions` - Backup import options specifying which components to restore
- `TeleporterGravityOptions` - Gravity database specific import options
- `PiHoleList` - Represents a single Pi-hole domain list with metadata
- `ListType` - Enum for list types (ALLOW or BLOCK)
- `DHCPLease` - Represents a single DHCP lease with hostname, IP, MAC address, client ID, and expiration
- `DHCPLeasesInfo` - Container for DHCP lease information
- `PADDInfo` - Comprehensive Pi-hole dashboard data including statistics, system info, network details, and configuration
- `PADDQueries` - Query statistics (total, blocked, percent blocked)
- `PADDCache` - Cache information (size, inserted, evicted)
- `PADDSystem` - System resource information (uptime, memory, CPU, processes)
- `PADDInterface` - Network interface information (IPv4/IPv6 addresses, gateway, traffic)
- `PADDVersion` - Version information for all Pi-hole components
- `PADDConfig` - Configuration summary (DHCP, DNS, privacy settings)

## Contributing

I'm thrilled that you’re interested in contributing to this project! Here’s how you can get involved:

### How to Contribute

1. **Submit Issues**:

   - If you encounter any bugs or have suggestions for improvements, please submit an issue on our [GitHub Issues](https://github.com/dsgnr/pihole-lib/issues) page.
   - Provide as much detail as possible, including steps to reproduce and screenshots if applicable.

2. **Propose Features**:

   - Have a great idea for a new feature? Open a feature request issue in the same [GitHub Issues](https://github.com/dsgnr/pihole-lib/issues) page.
   - Describe the feature in detail and explain how it will benefit the project.

3. **Submit Pull Requests**:
   - Fork the repository and create a new branch for your changes.
   - Make your modifications and test thoroughly.
   - Open a pull request against the `devel` branch of the original repository. Include a clear description of your changes and any relevant context.

## Author

- Website: https://danielhand.io
- Github: [@dsgnr](https://github.com/dsgnr)

## License

See the [LICENSE](LICENSE) file for more details on terms and conditions.
