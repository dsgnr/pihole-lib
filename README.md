# Pi-hole Python Library

A non-official Python library for interacting with Pi-hole's API. This library provides a clean, Pythonic interface to manage your Pi-hole instance programmatically.

This library is pretty much a scrape of the Pi-hole docs found at `<pihole-instance>/api/docs`.

## Table of Contents

- [Disclaimer](#disclaimer)
- [Features](#features)
- [Supported Pi-hole Versions](#supported-pi-hole-versions)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Development and Testing](#development-and-testing)
- [API Reference](#api-reference)
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
| | GitHub Actions | 📋 |
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
| **Metrics** | Query statistics | ✅ |
| | Top clients/domains | ✅ |
| | Query types over time | ✅ |
| | Activity history graphs | ✅ |
| | Recent blocked domains | ✅ |
| | Upstream server metrics | ✅ |
| | Database analytics | ✅ |
| | Long-term database queries | ✅ |
| | Query filtering and search | ✅ |
| | Detailed query logs | ✅ |
| **DNS Control** | Enable/disable Pi-hole blocking | ✅ |
| | Custom DNS records (A/CNAME) | ✅ |
| | Get DNS configuration | ✅ |
| | DNS blocking status | ✅ |
| **Domain Management** | Add/remove domains | ✅ |
| | Exact/regex domain matching | ✅ |
| | Domain comments and descriptions | ✅ |
| | Batch domain operations | ✅ |
| | Move domains between lists | ✅ |
| **List Management** | Get domain lists (by type, and name) | ✅ |
| | List metadata and statistics | ✅ |
| | Add/remove lists | ✅ |
| | Update existing lists | ✅ |
| | Batch list operations | ✅ |
| | Domain search in lists | ✅ |
| **Group Management** | Get groups | ✅ |
| | Create/update/delete groups | ✅ |
| | Batch group operations | ✅ |
| **Client Management** | Get clients | ✅ |
| | Add/update/delete clients | ✅ |
| | Batch client operations | ✅ |
| | Client suggestions | ✅ |
| | Client identification (IP/MAC/hostname/interface) | ✅ |
| **Pi-hole Configuration** | Get configuration (with filtering) | ✅ |
| | Update configuration (PATCH) | ✅ |
| | Add/remove config array items | ✅ |
| | DNS settings management | ✅ |
| | DHCP settings management | ✅ |
| | Web server settings management | ✅ |
| | Batch configuration updates | ✅ |
| **Actions** | Update gravity | ✅ |
| | Restart DNS | ✅ |
| | Flush logs | ✅ |
| | Flush network table | ✅ |
| **Teleporter** | Backup configuration | ✅ |
| | Restore from backup | ✅ |
| **DHCP** | Get active DHCP leases | ✅ |
| | Delete DHCP lease | ✅ |
| **PADD** | Get dashboard data | ✅ |
| **Network** | Get network devices | ✅ |
| | Get gateway information | ✅ |
| | Get network interfaces | ✅ |
| | Get network routes | ✅ |
| | Delete network devices | ✅ |
| **Other** | Better documentation format (Sphinx?) | 📋 |
| | Initial Pypi release | 📋 |

## Supported Pi-hole Versions

This library is designed to work with Pi-hole v6.0+ and uses the endpoints defined at `/api/docs`. It's tested against the latest Pi-hole releases to ensure compatibility.

## Installation

```bash
pip install pihole-lib
```

## Quick Start

```python
from pihole_lib import PiHoleClient

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Update gravity database
    for line in client.actions.update_gravity():
        print(line.strip())

    # Manage lists
    all_lists = client.lists.get_lists()
    print(f"Found {len(all_lists)} lists")
```

### Configuration Options

```python
client = PiHoleClient(
    base_url="https://pihole.local",      # Your Pi-hole's address
    password="your-admin-password",       # Pi-hole admin password
    timeout=60,                           # Request timeout in seconds (default: 30)
    verify_ssl=False                      # SSL certificate verification (default: True)
)
```

## Documentation

For comprehensive examples covering all features, see the [Examples Documentation](https://github.com/dsgnr/pihole-lib/blob/main/docs/examples.md).

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

For complete API documentation, build the docs locally with `make docs`.

## Contributing

I'm thrilled that you're interested in contributing to this project! Here's how you can get involved:

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

See the LICENSE file for more details on terms and conditions.
