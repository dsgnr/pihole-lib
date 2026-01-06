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
| **Testing** | Integration tests against a live Pi-hole instance | Complete |
| | Lint and type checking | Complete |
| **Authentication** | Session-based authentication | Complete |
| | Automatic session management | Complete |
| | Context manager support | Complete |
| **Information** | Login page information | Complete |
| **Error Handling** | Comprehensive error handling | Complete |
| | Specific exception types | Complete |
| **Metrics** | Query statistics | Planned |
| | Top clients/domains | Planned |
| | Query types over time | Planned |
| **DNS Control** | Enable/disable Pi-hole | Planned |
| | Flush network table | Planned |
| | Restart DNS resolver | Planned |
| **Domain Management** | Add/remove domains | Planned |
| | Exact/regex domain matching | Planned |
| | Domain comments and descriptions | Planned |
| **List Management** | Get domain lists | Complete |
| | Filter lists by type (allow/block) | Complete |
| | Filter lists by name | Complete |
| | List metadata and statistics | Complete |
| | Add/remove lists | Planned |
| | Regex list management | Planned |
| | Import/export lists | Planned |
| **FTL Information** | FTL version and status | Planned |
| | Database statistics | Planned |
| **Pi-hole Configuration** | Network settings | Planned |
| | DNS settings | Planned |
| | Web interface settings | Planned |
| | Privacy settings | Planned |
| **Actions** | Update gravity | Planned |
| | Flush logs | Planned |
| | Restart DNS | Planned |
| **Teleporter** | Backup configuration | Complete |
| | Restore from backup | Complete |

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
print(f"Request Time: {login_info.took}s")     # Processing time

client.close()

# Or use within client context manager
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    info = PiHoleInfo(client)
    login_info = info.get_login_info()
    print(f"HTTPS Port: {login_info.https_port}")
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
    print(f"Imported {len(result.files)} files")
    print(f"Import took: {result.took}s")
```

### Domain lists management

```python
from pihole_lib import PiHoleClient, PiHoleLists, ListType

# Manage domain lists (blocklists and allowlists)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    lists = PiHoleLists(client)

    # Get all lists
    all_lists = lists.get_lists()
    print(f"Found {len(all_lists.lists)} total lists")

    # Get only block lists
    block_lists = lists.get_lists(list_type=ListType.BLOCK)
    print(f"Found {len(block_lists.lists)} block lists")

    # Get only allow lists
    allow_lists = lists.get_lists(list_type=ListType.ALLOW)
    print(f"Found {len(allow_lists.lists)} allow lists")

    # Get specific list by name
    specific_list = lists.get_lists(list_name="my_blocklist")
    if specific_list.lists:
        list_info = specific_list.lists[0]
        print(f"List: {list_info.address}")
        print(f"Type: {list_info.type.value}")
        print(f"Enabled: {list_info.enabled}")
        print(f"Domains: {list_info.number}")
        print(f"Invalid domains: {list_info.invalid_domains}")
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

**List Types:**
- `ListType.ALLOW` - Allow lists (domains that bypass blocking)
- `ListType.BLOCK` - Block lists (domains that are blocked)

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
- `AuthResponse` - Response data from Pi-hole authentication endpoint
- `LoginInfo` - Login page information including HTTPS port, DNS status, and processing time
- `TeleporterImportOptions` - Backup import options specifying which components to restore
- `TeleporterGravityOptions` - Gravity database specific import options
- `TeleporterImportResult` - Result of backup import operation with imported files and timing
- `PiHoleList` - Represents a single Pi-hole domain list with metadata
- `ListsResponse` - Response containing multiple domain lists and processing time
- `ListType` - Enum for list types (ALLOW or BLOCK)

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
