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
  - [Domain management](#domain-management)
  - [Groups management](#groups-management)
  - [Custom DNS records and blocking management](#custom-dns-records-and-blocking-management)
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
| | Regex list management | 📋 |
| | Import/export lists | 📋 |
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

## Usage

### Connect to your Pi-hole

```python
from pihole_lib import PiHoleClient

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    print(f"Connected with session: {client.get_session_id()}")

    # Update gravity database
    for line in client.actions.update_gravity():
        print(line.strip())

    # Get system information
    login_info = client.info.get_login_info()
    print(f"Pi-hole version: {login_info.version}")

    # Manage lists
    all_lists = client.lists.get_lists()
    print(f"Found {len(all_lists)} lists")

    # Session closed when exiting context

# Alternative usage with explicit class imports
from pihole_lib import PiHoleActions

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    actions = PiHoleActions(client)
    for line in actions.update_gravity():
        print(line.strip())
```

### Get login page information

```python
from pihole_lib import PiHoleClient

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get login page information (no authentication required for this endpoint)
    login_info = client.info.get_login_info()
    print(f"HTTPS Port: {login_info.https_port}")  # 443 or 0 if disabled
    print(f"DNS Status: {login_info.dns}")         # True if DNS is running

    # Get client request information
    client_info = client.info.get_client_info()
    print(f"Client IP: {client_info.remote_addr}")
    print(f"HTTP Version: {client_info.http_version}")
    print(f"Method: {client_info.method}")
    print(f"Headers: {len(client_info.headers)} headers")
    for header in client_info.headers:
        print(f"  {header.name}: {header.value}")

    # Get database information
    database_info = client.info.get_database_info()
    print(f"Database size: {database_info.size} bytes")
    print(f"SQLite version: {database_info.sqlite_version}")
    print(f"Queries in memory: {database_info.queries}")
    print(f"Queries on disk: {database_info.queries_disk}")
    print(f"File owner: {database_info.owner.user.name}")
    print(f"File group: {database_info.owner.group.name}")
    print(f"File permissions: {database_info.mode}")

    # Get FTL runtime information
    ftl_info = client.info.get_ftl_info()
    print(f"Process ID: {ftl_info.ftl.pid}")
    print(f"Uptime: {ftl_info.ftl.uptime} seconds")
    print(f"Memory usage: {ftl_info.ftl.mem_percent}%")
    print(f"CPU usage: {ftl_info.ftl.cpu_percent}%")
    print(f"Gravity domains: {ftl_info.ftl.database.gravity}")
    print(f"Total clients: {ftl_info.ftl.clients.total}")
    print(f"Active clients: {ftl_info.ftl.clients.active}")
    print(f"DNS queries forwarded: {ftl_info.ftl.dnsmasq.dns_queries_forwarded}")

    # Get host system information
    host_info = client.info.get_host_info()
    print(f"Hostname: {host_info.host.uname.nodename}")
    print(f"OS: {host_info.host.uname.sysname} {host_info.host.uname.release}")
    print(f"Architecture: {host_info.host.uname.machine}")
    print(f"Hardware model: {host_info.host.model}")
    if host_info.host.dmi.sys.vendor:
        print(f"System vendor: {host_info.host.dmi.sys.vendor}")

    # Get version information
    version_info = client.info.get_version_info()
    print(f"Pi-hole Core: {version_info.version.core.local.version}")
    print(f"Web Interface: {version_info.version.web.local.version}")
    print(f"FTL: {version_info.version.ftl.local.version}")
    print(f"Docker: {version_info.version.docker.local}")

    # Check if updates are available
    if version_info.version.core.local.version != version_info.version.core.remote.version:
        print("Core update available!")

    # Get system resource information
    system_info = client.info.get_system_info()
    print(f"Uptime: {system_info.system.uptime} seconds")
    print(f"RAM Usage: {system_info.system.memory.ram.percent_used:.1f}%")
    print(f"CPU Cores: {system_info.system.cpu.nprocs}")
    print(f"CPU Usage: {system_info.system.cpu.percent_cpu:.1f}%")
    print(f"Processes: {system_info.system.procs}")
    print(f"FTL Memory: {system_info.system.ftl.percent_mem:.2f}%")
    print(f"Load Average: {system_info.system.cpu.load.raw}")

    # Get system messages
    messages_info = client.info.get_messages()
    print(f"Total messages: {len(messages_info.messages)}")
    for message in messages_info.messages:
        print(f"[{message.type.upper()}] {message.plain}")
        print(f"  ID: {message.id}, Time: {message.timestamp}")

    # Get messages count
    messages_count = client.info.get_messages_count()
    print(f"Message count: {messages_count.count}")

# Alternative usage with explicit class imports
from pihole_lib import PiHoleInfo

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

### Network information

```python
from pihole_lib import PiHoleClient, PiHoleNetwork

# Get advanced network information about your Pi-hole
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    network = PiHoleNetwork(client)

    # Get network devices seen by Pi-hole
    devices = network.get_devices()
    print(f"Found {len(devices.devices)} network devices")

    for device in devices.devices:
        print(f"Device: {device.name} ({device.hwaddr})")
        print(f"  Interface: {device.interface}")
        print(f"  First seen: {device.first_seen}")
        print(f"  Last query: {device.last_query}")
        print(f"  Total queries: {device.num_queries}")

        for address in device.addresses:
            print(f"  Address: {address.ip}")
            if address.hostname:
                print(f"    Hostname: {address.hostname}")
            print(f"    Last query: {address.last_query}")

    # Get devices with limits
    limited_devices = network.get_devices(max_devices=5, max_addresses=3)
    print(f"Limited to {len(limited_devices.devices)} devices")

    # Get gateway information
    gateway = network.get_gateway()
    print(f"Found {len(gateway.gateway)} gateway entries")

    for gw in gateway.gateway:
        print(f"Gateway: {gw.address} (family: {gw.family})")
        print(f"  Interface: {gw.interface}")
        print(f"  Local addresses: {gw.local}")

    # Get detailed gateway information (includes routes and interfaces)
    detailed_gateway = network.get_gateway(detailed=True)
    print(f"Detailed gateway info:")
    print(f"  Gateways: {len(detailed_gateway.gateway)}")
    print(f"  Routes: {len(detailed_gateway.routes)}")
    print(f"  Interfaces: {len(detailed_gateway.interfaces)}")

    # Get network interfaces
    interfaces = network.get_interfaces()
    print(f"Found {len(interfaces.interfaces)} network interfaces")

    for interface in interfaces.interfaces:
        print(f"Interface: {interface.name}")
        print(f"  Type: {interface.type}")
        print(f"  State: {interface.state}")
        print(f"  Speed: {interface.speed}")
        print(f"  Flags: {interface.flags}")
        print(f"  Carrier: {interface.carrier}")
        print(f"  Address: {interface.address}")
        print(f"  Broadcast: {interface.broadcast}")

        # Interface statistics
        stats = interface.stats
        print(f"  RX bytes: {stats.rx_bytes}")
        print(f"  TX bytes: {stats.tx_bytes}")
        print(f"  Architecture: {stats.bits}-bit")

        # IP addresses on interface
        if interface.addresses:
            for addr in interface.addresses:
                print(f"  IP: {addr.address}/{addr.prefixlen} ({addr.family})")
                print(f"    Scope: {addr.scope}")
                print(f"    Type: {addr.address_type}")
                if addr.local:
                    print(f"    Local: {addr.local}")

    # Get detailed interface information
    detailed_interfaces = network.get_interfaces(detailed=True)
    print(f"Detailed interfaces: {len(detailed_interfaces.interfaces)}")

    # Get network routes
    routes = network.get_routes()
    print(f"Found {len(routes.routes)} network routes")

    for route in routes.routes:
        print(f"Route: {route.dst}")
        print(f"  Table: {route.table}")
        print(f"  Family: {route.family}")
        print(f"  Protocol: {route.protocol}")
        print(f"  Scope: {route.scope}")
        print(f"  Type: {route.type}")
        print(f"  Output interface: {route.oif}")
        if route.gateway:
            print(f"  Gateway: {route.gateway}")
        if route.prefsrc:
            print(f"  Preferred source: {route.prefsrc}")

    # Get detailed route information
    detailed_routes = network.get_routes(detailed=True)
    print(f"Detailed routes: {len(detailed_routes.routes)}")

    # Delete a network device (removes device and all associated addresses/hostnames)
    # Note: This requires a valid device ID from the devices list
    if devices.devices:
        device_id = devices.devices[0].id
        try:
            result = network.delete_device(device_id)
            print(f"Device {device_id} deleted successfully")
        except Exception as e:
            print(f"Failed to delete device {device_id}: {e}")

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get network information directly via client property
    devices = client.network.get_devices(max_devices=10)
    gateway = client.network.get_gateway()
    interfaces = client.network.get_interfaces()
    routes = client.network.get_routes()

    print(f"Network summary:")
    print(f"  Devices: {len(devices.devices)}")
    print(f"  Gateways: {len(gateway.gateway)}")
    print(f"  Interfaces: {len(interfaces.interfaces)}")
    print(f"  Routes: {len(routes.routes)}")
```

### Backup and restore operations

```python
from pihole_lib import PiHoleClient, TeleporterImportOptions

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Export current Pi-hole configuration (filename auto-generated with timestamp)
    backup_file = client.backup.export_backup("/path/to/backups")
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

    result = client.backup.import_backup(backup_file, import_options)
    print(f"Imported {len(result)} files")
    for file in result:
        print(f"  - {file}")

# Alternative usage with explicit class imports
from pihole_lib import PiHoleBackup

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
from pihole_lib import PiHoleClient, ListType, BatchDeleteItem

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get all lists
    all_lists = client.lists.get_lists()
    print(f"Found {len(all_lists)} total lists")

    # Get only block lists
    block_lists = client.lists.get_lists(list_type=ListType.BLOCK)
    print(f"Found {len(block_lists)} block lists")

    # Get only allow lists
    allow_lists = client.lists.get_lists(list_type=ListType.ALLOW)
    print(f"Found {len(allow_lists)} allow lists")

    # Get specific list by name
    specific_lists = client.lists.get_lists(list_name="my_blocklist")
    if specific_lists:
        list_info = specific_lists[0]
        print(f"List: {list_info.address}")
        print(f"Type: {list_info.type.value}")
        print(f"Enabled: {list_info.enabled}")
        print(f"Domains: {list_info.number}")
        print(f"Invalid domains: {list_info.invalid_domains}")

    # Add a new blocklist
    new_lists = client.lists.add_list(
        address="https://hosts-file.net/ad_servers.txt",
        list_type=ListType.BLOCK,
        comment="Ad servers blocklist",
        groups=[0],
        enabled=True
    )
    print(f"Successfully added list: {new_lists[0].address}")

    # Add an allowlist for a specific domain
    allow_lists = client.lists.add_list(
        address="example.com",
        list_type=ListType.ALLOW,
        comment="Allow example.com"
    )
    print(f"Added allowlist: {allow_lists[0].address}")

    # Update an existing list
    update_response = client.lists.update_list(
        address="example.com",
        list_type=ListType.ALLOW,
        comment="Updated comment for example.com",
        groups=[0, 1],
        enabled=False
    )

    # Update returns ListsResponse object with processing results
    if update_response.processed and update_response.processed.errors:
        for error in update_response.processed.errors:
            print(f"Error updating list: {error.error}")
    else:
        updated_list = update_response.lists[0]
        print(f"Updated list: {updated_list.address}")
        print(f"New comment: {updated_list.comment}")
        print(f"Enabled: {updated_list.enabled}")

    # Search for domains in lists
    search_response = client.lists.search_domains("example.com")
    print(f"Search found {search_response.search.results.total} results")

    for domain_match in search_response.search.domains:
        print(f"Domain match: {domain_match.address} ({domain_match.type})")

    for gravity_match in search_response.search.gravity:
        print(f"Gravity match: {gravity_match.address} ({gravity_match.type})")

    # Partial search with more results
    partial_search = client.lists.search_domains(
        domain="example",
        partial=True,
        max_results=50,
        debug=True
    )
    print(f"Partial search parameters: {partial_search.search.parameters}")
    print(f"Domain matches: {partial_search.search.results.domains.exact}")
    print(f"Gravity matches: {partial_search.search.results.gravity.block}")

    # Batch delete multiple lists
    items_to_delete = [
        BatchDeleteItem(item="https://hosts-file.net/ad_servers.txt", type=ListType.BLOCK),
        BatchDeleteItem(item="example.com", type=ListType.ALLOW),
    ]

    batch_success = client.lists.batch_delete_lists(items_to_delete)
    print(f"Batch deletion successful: {batch_success}")

    # Individual delete (existing functionality)
    success = client.lists.delete_list(
        address="remaining.example.com",
        list_type=ListType.ALLOW
    )
    print(f"Individual deletion successful: {success}")

# Alternative usage with explicit class imports
from pihole_lib import PiHoleLists

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    lists = PiHoleLists(client)

    all_lists = lists.get_lists()
    print(f"Found {len(all_lists)} total lists")

    # Add list
    new_lists = lists.add_list(
        address="https://example.com/blocklist.txt",
        list_type=ListType.BLOCK,
        comment="Example blocklist",
        groups=[0],
        enabled=True
    )
    print(f"Added list, API returned {len(new_lists)} lists")

    # Update list
    update_response = lists.update_list(
        address="https://example.com/blocklist.txt",
        list_type=ListType.BLOCK,
        comment="Updated blocklist comment",
        groups=[0],
        enabled=True
    )

    # Access processing results
    if update_response.processed:
        print(f"Successful updates: {len(update_response.processed.success)}")
        print(f"Errors: {len(update_response.processed.errors)}")

        for success_item in update_response.processed.success:
            print(f"Successfully processed: {success_item.item}")

        for error_item in update_response.processed.errors:
            print(f"Error processing {error_item.item}: {error_item.error}")

    # Search functionality
    search_response = lists.search_domains("example.com")
    print(f"Search took {search_response.took}s")
    print(f"Found {search_response.search.results.total} total matches")

    # Delete a blocklist
    success = lists.delete_list(
        address="https://example.com/blocklist.txt",
        list_type=ListType.BLOCK
    )
    print(f"Blocklist deletion successful: {success}")
```

### Domain management

```python
from pihole_lib import PiHoleClient, DomainType, DomainKind

with PiHoleClient("http://192.168.1.100", password="secret") as client:
    domains = client.domains

    # Get all domains
    all_domains = domains.get_domains()
    print(f"Total domains: {len(all_domains)}")

    # Get domains by type
    allowed_domains = domains.get_domains(domain_type=DomainType.ALLOW)
    blocked_domains = domains.get_domains(domain_type=DomainType.DENY)
    print(f"Allowed: {len(allowed_domains)}, Blocked: {len(blocked_domains)}")

    # Get domains by kind
    exact_domains = domains.get_domains(domain_kind=DomainKind.EXACT)
    regex_domains = domains.get_domains(domain_kind=DomainKind.REGEX)
    print(f"Exact: {len(exact_domains)}, Regex: {len(regex_domains)}")

    # Get specific domain
    domain = domains.get_domain("example.com", DomainType.ALLOW, DomainKind.EXACT)
    if domain:
        print(f"Found domain: {domain.domain} (enabled: {domain.enabled})")

    # Add a new blocked domain
    result = domains.add_domain(
        domain="badsite.com",
        domain_type=DomainType.DENY,
        domain_kind=DomainKind.EXACT,
        comment="Malicious site",
        groups=[0],
        enabled=True
    )
    print(f"Added domain: {result.processed.success}")

    # Add a regex pattern
    result = domains.add_domain(
        domain=r".*\.ads\..*",
        domain_type=DomainType.DENY,
        domain_kind=DomainKind.REGEX,
        comment="Block ads subdomains"
    )
    print(f"Added regex pattern: {result.processed.success}")

    # Update a domain
    result = domains.update_domain(
        domain="example.com",
        domain_type=DomainType.ALLOW,
        domain_kind=DomainKind.EXACT,
        comment="Updated comment",
        enabled=False
    )
    print(f"Updated domain: {result.processed.success}")

    # Move domain from allow to deny list
    result = domains.update_domain(
        domain="example.com",
        domain_type=DomainType.ALLOW,
        domain_kind=DomainKind.EXACT,
        new_type=DomainType.DENY,
        new_kind=DomainKind.EXACT
    )
    print(f"Moved domain: {result.processed.success}")

    # Delete a domain
    domains.delete_domain("badsite.com", DomainType.DENY, DomainKind.EXACT)
    print("Domain deleted")

    # Batch delete multiple domains
    from pihole_lib import DomainBatchDeleteItem

    batch_items = [
        DomainBatchDeleteItem(
            item="site1.com",
            type=DomainType.DENY,
            kind=DomainKind.EXACT
        ),
        DomainBatchDeleteItem(
            item="site2.com",
            type=DomainType.DENY,
            kind=DomainKind.EXACT
        )
    ]
    result = domains.batch_delete_domains(batch_items)
    print(f"Batch delete completed successfully: {result}")
```

### Custom DNS records and blocking management

```python
from pihole_lib import PiHoleClient, PiHoleDNS

# Manage custom DNS records and blocking (A records, CNAME records, and blocking control)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    dns = PiHoleDNS(client)

    # Get DNS configuration
    config = dns.get_config()
    print(f"Upstream servers: {config.upstreams}")
    print(f"DNS port: {config.port}")
    print(f"Query logging: {config.query_logging}")
    print(f"DNSSEC: {config.dnssec}")
    print(f"Blocking active: {config.blocking_active}")

    # Access parsed host records (A records)
    for host in config.hosts:
        print(f"A record: {host.domain} -> {host.target}")

    # Access parsed CNAME records
    for cname in config.cname_records:
        print(f"CNAME: {cname.domain} -> {cname.target}")

    # Or access all records directly
    for record in config.records:
        print(f"{record.record_type}: {record.domain} -> {record.target}")

    # Get all custom DNS records
    records = dns.get_records()
    print(f"Found {len(records)} custom DNS records")

    for record in records:
        if record.record_type == "A":
            print(f"A: {record.domain} -> {record.target}")
        elif record.record_type == "CNAME":
            print(f"CNAME: {record.domain} -> {record.target}")

    # Get only A records
    a_records = dns.get_records(record_type="A")
    print(f"Found {len(a_records)} A records")

    # Get only CNAME records
    cname_records = dns.get_records(record_type="CNAME")
    print(f"Found {len(cname_records)} CNAME records")

    # Add custom A record
    success = dns.add_a_record("server.local", "192.168.1.100")
    if success:
        print("A record added successfully")

    # Add CNAME record
    success = dns.add_cname_record("www.local", "server.local")
    if success:
        print("CNAME record added successfully")

    # Remove A record
    success = dns.remove_a_record("server.local", "192.168.1.100")
    if success:
        print("A record removed successfully")

    # Remove CNAME record
    success = dns.remove_cname_record("www.local", "server.local")
    if success:
        print("CNAME record removed successfully")

    # DNS Blocking Control
    # Check current DNS blocking status
    status = dns.get_blocking_status()
    print(f"DNS blocking: {status.blocking}")
    if status.timer:
        print(f"Temporarily disabled for {status.timer} seconds")

    # Enable blocking permanently
    status = dns.enable_blocking()
    print(f"Blocking enabled: {status.blocking}")

    # Disable blocking for 5 minutes (300 seconds)
    status = dns.disable_blocking(timer=300)
    print(f"Blocking disabled for {status.timer} seconds")

    # Enable blocking for 1 hour, then auto-disable
    status = dns.enable_blocking(timer=3600)
    print(f"Blocking enabled with auto-disable in {status.timer} seconds")

    # Use the general set_blocking_status method
    # Disable permanently
    status = dns.set_blocking_status(blocking=False)
    print(f"Blocking status: {status.blocking}")

    # Enable with 10-minute timer
    status = dns.set_blocking_status(blocking=True, timer=600)
    print(f"Blocking enabled for {status.timer} seconds")

    # Cancel any timer and enable permanently
    status = dns.set_blocking_status(blocking=True, timer=None)
    print(f"Blocking permanently enabled: {status.blocking}")
```

### Groups management

```python
from pihole_lib import PiHoleClient, PiHoleGroups

# Manage Pi-hole groups
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    groups = PiHoleGroups(client)

    # Get all groups
    all_groups = groups.get_groups()
    print(f"Found {len(all_groups.groups)} groups")

    for group in all_groups.groups:
        print(f"Group: {group.name} (ID: {group.id})")
        print(f"  Comment: {group.comment}")
        print(f"  Enabled: {group.enabled}")

    # Get specific group
    specific_group = groups.get_groups(name="Default")
    if specific_group.groups:
        group = specific_group.groups[0]
        print(f"Default group ID: {group.id}")

    # Create a new group
    new_group = groups.create_group(
        name="family_devices",
        comment="Devices used by family members",
        enabled=True
    )

    if new_group.processed and new_group.processed.errors:
        for error in new_group.processed.errors:
            print(f"Error creating {error.item}: {error.error}")
    else:
        print(f"Created group: {new_group.groups[0].name}")

    # Update a group
    updated_group = groups.update_group(
        name="family_devices",
        new_name="family_devices_updated",
        comment="Updated comment for family devices",
        enabled=False
    )
    print(f"Updated group: {updated_group.groups[0].name}")

    # Delete a group
    success = groups.delete_group("family_devices_updated")
    if success:
        print("Group deleted successfully")

    # Batch operations
    # Create multiple groups
    test_groups = ["group1", "group2", "group3"]
    for group_name in test_groups:
        groups.create_group(
            name=group_name,
            comment=f"Test group {group_name}",
            enabled=True
        )

    # Batch delete groups
    delete_result = groups.delete_groups(test_groups)
    if delete_result.processed:
        print(f"Successfully deleted: {len(delete_result.processed.success)} groups")
        for error in delete_result.processed.errors:
            print(f"Failed to delete {error.item}: {error.error}")

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get all groups - no need to import PiHoleGroups
    all_groups = client.groups.get_groups()
    print(f"Found {len(all_groups.groups)} groups")

    # Create a group
    new_group = client.groups.create_group(
        name="test_group",
        comment="Test group via property access",
        enabled=True
    )

    # Delete the group
    success = client.groups.delete_group("test_group")
    print(f"Group deleted: {success}")
```

### Client management

```python
from pihole_lib import PiHoleClient, PiHoleClients, ClientBatchDeleteItem

# Manage Pi-hole clients
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    clients = PiHoleClients(client)

    # Get all clients
    all_clients = clients.get_clients()
    print(f"Found {len(all_clients)} clients")

    for client_info in all_clients:
        print(f"Client: {client_info.client}")
        print(f"  Name: {client_info.name}")
        print(f"  Comment: {client_info.comment}")
        print(f"  Groups: {client_info.groups}")
        print(f"  ID: {client_info.id}")

    # Get specific client by IP address
    specific_client = clients.get_clients(client="192.168.1.50")
    if specific_client:
        client_info = specific_client[0]
        print(f"Found client: {client_info.client}")

    # Get client by MAC address
    mac_client = clients.get_clients(client="12:34:56:78:9A:BC")

    # Get client by hostname
    hostname_client = clients.get_clients(client="laptop.local")

    # Add a new client by IP address
    new_clients = clients.add_client(
        client="192.168.1.100",
        comment="John's laptop",
        groups=[0, 1]
    )
    print(f"Added client: {new_clients[0].client}")

    # Add client by MAC address
    mac_clients = clients.add_client(
        client="12:34:56:78:9A:BC",
        comment="Smart TV",
        groups=[0]
    )

    # Add client by hostname
    hostname_clients = clients.add_client(
        client="laptop.local",
        comment="Development machine"
    )

    # Add client by subnet (CIDR notation)
    subnet_clients = clients.add_client(
        client="192.168.2.0/24",
        comment="Guest network devices"
    )

    # Add client by interface
    interface_clients = clients.add_client(
        client=":eth0",
        comment="Ethernet interface clients"
    )

    # Update an existing client
    update_response = clients.update_client(
        client="192.168.1.100",
        comment="Updated comment for John's laptop",
        groups=[0, 1, 2]
    )

    if update_response.processed and update_response.processed.errors:
        for error in update_response.processed.errors:
            print(f"Error updating client: {error.error}")
    else:
        updated_client = update_response.clients[0]
        print(f"Updated client: {updated_client.client}")
        print(f"New comment: {updated_client.comment}")
        print(f"Groups: {updated_client.groups}")

    # Get client suggestions (unconfigured clients that have been seen)
    suggestions = clients.get_client_suggestions()
    print(f"Found {len(suggestions)} unconfigured clients")

    for suggestion in suggestions:
        print(f"Suggested client: {suggestion.client}")
        if suggestion.name:
            print(f"  Name: {suggestion.name}")
        print(f"  Last seen: {suggestion.date_modified}")

    # Add suggested clients to configuration
    for suggestion in suggestions[:3]:  # Add first 3 suggestions
        clients.add_client(
            client=suggestion.client,
            comment=f"Auto-added from suggestions: {suggestion.name or 'Unknown'}"
        )

    # Delete a single client
    delete_success = clients.delete_client("192.168.1.100")
    print(f"Client deletion successful: {delete_success}")

    # Batch delete multiple clients
    items_to_delete = [
        ClientBatchDeleteItem(item="12:34:56:78:9A:BC"),
        ClientBatchDeleteItem(item="laptop.local"),
        ClientBatchDeleteItem(item="192.168.2.0/24"),
    ]

    batch_success = clients.batch_delete_clients(items_to_delete)
    print(f"Batch deletion successful: {batch_success}")

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get all clients - no need to import PiHoleClients
    all_clients = client.clients.get_clients()
    print(f"Found {len(all_clients)} clients")

    # Add a client
    new_clients = client.clients.add_client(
        client="192.168.1.200",
        comment="Test client via property access",
        groups=[0]
    )

    # Update the client
    update_response = client.clients.update_client(
        client="192.168.1.200",
        comment="Updated test client",
        groups=[0]
    )

    # Get client suggestions
    suggestions = client.clients.get_client_suggestions()
    print(f"Client suggestions: {len(suggestions)}")

    # Delete the client
    success = client.clients.delete_client("192.168.1.200")
    print(f"Client deleted: {success}")
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

    # UPDATE CONFIGURATION
    # Update DNS settings
    new_dns_config = {
        "dns": {
            "upstreams": ["1.1.1.1", "1.0.0.1"],
            "queryLogging": True,
            "dnssec": True
        }
    }
    updated_config = config.update_config(new_dns_config)
    print(f"Updated DNS upstreams: {updated_config['dns']['upstreams']}")

    # Update DHCP settings
    dhcp_config = {
        "dhcp": {
            "active": True,
            "start": "192.168.1.100",
            "end": "192.168.1.200",
            "router": "192.168.1.1",
            "netmask": "255.255.255.0",
            "leaseTime": "24h"
        }
    }
    updated_config = config.update_config(dhcp_config)
    print(f"DHCP now active: {updated_config['dhcp']['active']}")

    # Update multiple sections at once
    multi_config = {
        "dns": {
            "upstreams": ["8.8.8.8", "8.8.4.4"],
            "port": 53
        },
        "webserver": {
            "port": "80o,443os"
        }
    }
    updated_config = config.update_config(multi_config)

    # Update without restarting FTL (for batch operations)
    config.update_config({"dns": {"upstreams": ["1.1.1.1"]}}, restart=False)
    config.update_config({"dns": {"port": 5353}}, restart=False)
    # Restart FTL with the final update
    config.update_config({"dns": {"queryLogging": False}}, restart=True)

    # ADD/REMOVE INDIVIDUAL CONFIG ITEMS
    # Add upstream DNS server
    success = config.add_config_item("dns/upstreams", "9.9.9.9")
    print(f"Added upstream: {success}")

    # Add custom DNS host entry
    success = config.add_config_item("dns/hosts", "192.168.1.10 myserver.local")
    print(f"Added host entry: {success}")

    # Add web server header
    success = config.add_config_item(
        "webserver/headers",
        "X-Custom-Header: MyValue"
    )
    print(f"Added header: {success}")

    # Add DHCP static host entry
    success = config.add_config_item(
        "dhcp/hosts",
        "12:34:56:78:9A:BC,192.168.1.50,laptop"
    )
    print(f"Added DHCP host: {success}")

    # Remove upstream DNS server
    success = config.remove_config_item("dns/upstreams", "9.9.9.9")
    print(f"Removed upstream: {success}")

    # Remove custom DNS host entry
    success = config.remove_config_item("dns/hosts", "192.168.1.10 myserver.local")
    print(f"Removed host entry: {success}")

    # Add/remove without restarting FTL
    success = config.add_config_item("dns/upstreams", "8.8.8.8", restart=False)
    success = config.remove_config_item("dns/upstreams", "8.8.8.8", restart=False)

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get configuration - no need to import PiHoleConfig
    config_data = client.config.get_config()
    print(f"DNS upstreams: {config_data['dns']['upstreams']}")

    # Get specific configuration element
    dns_config = client.config.get_config("dns")
    print(f"DNS settings: {dns_config['dns']}")

    # Update configuration
    new_config = {
        "dns": {
            "upstreams": ["1.1.1.1", "1.0.0.1"],
            "queryLogging": True
        }
    }
    updated_config = client.config.update_config(new_config)
    print(f"Updated upstreams: {updated_config['dns']['upstreams']}")

    # Add/remove config items
    success = client.config.add_config_item("dns/upstreams", "8.8.8.8")
    print(f"Added upstream: {success}")

    success = client.config.remove_config_item("dns/upstreams", "8.8.8.8")
    print(f"Removed upstream: {success}")
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

### Statistics and analytics

```python
from pihole_lib import PiHoleClient, PiHoleStats
import time

# Get comprehensive Pi-hole statistics and analytics
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    stats = PiHoleStats(client)

    # Get activity summary
    summary = stats.get_summary()
    print(f"Total queries: {summary.queries.total}")
    print(f"Blocked queries: {summary.queries.blocked}")
    print(f"Percent blocked: {summary.queries.percent_blocked}%")
    print(f"Active clients: {summary.clients.active}")
    print(f"Domains on blocklists: {summary.gravity.domains_being_blocked}")

    # Get activity history (last 24 hours)
    history = stats.get_history()
    for entry in history.history:
        print(f"Time: {entry.timestamp}, Total: {entry.total}, Blocked: {entry.blocked}")

    # Get per-client activity
    client_history = stats.get_client_history()
    print(f"Client mappings: {client_history.clients}")

    # Get top domains and clients
    top_domains = stats.get_top_domains(count=10)
    for domain in top_domains.domains:
        print(f"{domain.domain}: {domain.count} queries")

    top_clients = stats.get_top_clients(count=10)
    for client in top_clients.clients:
        print(f"{client.name or client.ip}: {client.count} queries")

    # Get blocked domains specifically
    blocked_domains = stats.get_top_domains(blocked=True, count=5)
    blocked_clients = stats.get_top_clients(blocked=True, count=5)

    # Get recent queries with filtering
    recent_queries = stats.get_queries(length=50)
    print(f"Total records: {recent_queries.records_total}")

    # Filter queries by domain
    domain_queries = stats.get_queries(domain="example.com")

    # Filter queries by client
    client_queries = stats.get_queries(client="192.168.1.100")

    # Get query types breakdown
    query_types = stats.get_query_types()
    for query_type, count in query_types.types.items():
        print(f"{query_type}: {count}")

    # Get recently blocked domains
    recent_blocked = stats.get_recent_blocked(count=10)
    print(f"Recently blocked: {recent_blocked.blocked}")

    # Get upstream server metrics
    upstreams = stats.get_upstreams()
    for upstream in upstreams.upstreams:
        print(f"{upstream.name}: {upstream.count} queries")
        if upstream.statistics:
            print(f"  Response time: {upstream.statistics.response}ms")

    # Get query filter suggestions
    suggestions = stats.get_query_suggestions()
    print(f"Available domains: {suggestions.suggestions.domain}")
    print(f"Available clients: {suggestions.suggestions.client_ip}")

    # Long-term database analytics
    now = int(time.time())
    week_ago = now - (7 * 24 * 60 * 60)

    # Get historical data from database
    db_history = stats.get_database_history(week_ago, now)
    db_summary = stats.get_database_summary(week_ago, now)
    db_top_domains = stats.get_database_top_domains(week_ago, now)
    db_top_clients = stats.get_database_top_clients(week_ago, now)
    db_query_types = stats.get_database_query_types(week_ago, now)
    db_upstreams = stats.get_database_upstreams(week_ago, now)

    print(f"Week summary - Total: {db_summary.sum_queries}, Blocked: {db_summary.sum_blocked}")

# Simplified usage with property access (recommended)
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get statistics directly via client property
    summary = client.stats.get_summary()
    top_domains = client.stats.get_top_domains(count=15)
    recent_blocked = client.stats.get_recent_blocked(count=20)
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

**List Operations:**
- `get_lists(list_name=None, list_type=None)` - Get domain lists with optional filtering by name or type.
- `add_list(address, list_type, comment=None, groups=None, enabled=True)` - Add a new domain list.
- `delete_list(address, list_type)` - Delete a single domain list. Returns True if successful, raises exceptions on failure.
- `update_list(address, list_type, comment=None, groups=None, enabled=True)` - Update an existing domain list. Returns ListsResponse object with updated list and processing results.
- `batch_delete_lists(items)` - Delete multiple domain lists in batch. Takes list of BatchDeleteItem objects. Returns True if successful.

**Search Operations:**
- `search_domains(domain, partial=False, max_results=20, debug=False)` - Search for domains in Pi-hole's lists. Returns SearchResponse object with search results and metadata.

**List Types:**
- `ListType.ALLOW` - Allow lists (domains that bypass blocking)
- `ListType.BLOCK` - Block lists (domains that are blocked)

**Response Objects:**
- `ListsResponse` - Contains lists array, processing results, and timing information (returned by update_list)
- `SearchResponse` - Contains search results, parameters used, and result counts (returned by search_domains)
- `BatchDeleteItem` - Specifies item address and type for batch deletion operations

### PiHoleDomains

The domains class for Pi-hole individual domain management (allow/deny lists).

**Methods:**
- `PiHoleDomains(client)` - Create a new domains client using an existing PiHoleClient

**Domain Operations:**
- `get_domains(domain_type=None, domain_kind=None, domain=None)` - Get domains with optional filtering by type (allow/deny), kind (exact/regex), or specific domain name. Returns list of Domain objects.
- `get_domain(domain, domain_type, domain_kind)` - Get a specific domain by exact match. Returns Domain object if found, None otherwise.
- `add_domain(domain, domain_type, domain_kind, comment=None, groups=None, enabled=True)` - Add a new domain. Returns DomainMutationResponse object with processing results.
- `update_domain(domain, domain_type, domain_kind, new_type=None, new_kind=None, comment=None, groups=None, enabled=None)` - Update an existing domain. Can move domains between lists using new_type/new_kind. Returns DomainMutationResponse object.
- `delete_domain(domain, domain_type, domain_kind)` - Delete a domain. No return value on success.
- `batch_delete_domains(domains)` - Delete multiple domains in a single request. Takes list of DomainBatchDeleteItem objects. Returns True if successful.

**Domain Types and Kinds:**
- `DomainType.ALLOW` - Allowed domains (bypass blocking)
- `DomainType.DENY` - Denied domains (blocked)
- `DomainKind.EXACT` - Exact domain matching
- `DomainKind.REGEX` - Regular expression pattern matching

**Response Objects:**
- `Domain` - Represents a domain entry with name, type, kind, comment, groups, enabled status, and timestamps
- `DomainMutationResponse` - Contains domains array and processing results (returned by add_domain and update_domain)
- `DomainsResponse` - Contains list of domains (returned by get_domains)
- `DomainBatchDeleteItem` - Specifies domain, type, and kind for batch deletion operations

### PiHoleGroups

The groups class for Pi-hole group management.

**Methods:**
- `PiHoleGroups(client)` - Create a new groups client using an existing PiHoleClient
- `get_groups(name=None)` - Get groups with optional filtering by name. Returns GroupsResponse object with groups array and metadata.
- `create_group(name, comment=None, enabled=True)` - Create a new group. Returns GroupsResponse object with created group and processing results.
- `create_groups(groups)` - Create multiple groups from a list of GroupRequest objects. Returns GroupsResponse object with processing results.
- `update_group(name, new_name=None, comment=None, enabled=True)` - Update an existing group. Can rename by providing new_name. Returns GroupsResponse object.
- `delete_group(name)` - Delete a single group by name. Returns True if successful.
- `delete_groups(group_names)` - Delete multiple groups by names. Returns GroupsResponse object with processing results.

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

### PiHoleDNS

The DNS class for Pi-hole custom DNS record management and blocking control.

**Methods:**
- `PiHoleDNS(client)` - Create a new DNS client using an existing PiHoleClient
- `get_config()` - Get complete DNS configuration including upstream servers, custom records, and settings. Returns a DNSConfig object with properties like `upstreams`, `records` (list of DNSRecord objects), `hosts` (filtered A records), `cname_records` (filtered CNAME records), `port`, `query_logging`, `dnssec`, `blocking`, and `blocking_active`.
- `get_records(record_type=None)` - Get all custom DNS records (A records and CNAME records). Use `record_type="A"` for A records only, `record_type="CNAME"` for CNAME records only, or `record_type=None` for all records. Returns a list of DNSRecord objects.
- `add_a_record(domain, ip)` - Add a custom A record for local domain resolution. Returns True if successful.
- `remove_a_record(domain, ip)` - Remove a custom A record. Returns True if successful.
- `add_cname_record(domain, target)` - Add a custom CNAME record for domain aliasing. Returns True if successful.
- `remove_cname_record(domain, target)` - Remove a custom CNAME record. Returns True if successful.
- `get_blocking_status()` - Get DNS blocking status. Returns a DNSBlockingStatus object with current blocking state and any temporary disable timer.
- `set_blocking_status(blocking=True, timer=None)` - Change DNS blocking status. Set `blocking=True` to enable or `blocking=False` to disable. Optional `timer` parameter sets automatic revert after specified seconds. Returns DNSBlockingStatus object.
- `enable_blocking(timer=None)` - Convenience method to enable DNS blocking. Optional `timer` parameter sets automatic disable after specified seconds. Returns DNSBlockingStatus object.
- `disable_blocking(timer=None)` - Convenience method to disable DNS blocking. Optional `timer` parameter sets automatic re-enable after specified seconds. Returns DNSBlockingStatus object.

### PiHolePADD

The PADD class for Pi-hole dashboard data retrieval.

**Methods:**
- `PiHolePADD(client)` - Create a new PADD client using an existing PiHoleClient
- `get_dashboard_data()` - Get comprehensive Pi-hole dashboard data including query statistics, system information, network details, version information, and configuration summaries. Returns a PADDInfo object with all dashboard data.

### PiHoleNetwork

The network class for Pi-hole network information operations.

**Methods:**
- `PiHoleNetwork(client)` - Create a new network client using an existing PiHoleClient
- `get_devices(max_devices=None, max_addresses=None)` - Get info about devices in your local network as seen by Pi-hole. By default, device count is limited to 10, ordered by most recent query. Optional parameters limit the number of devices and addresses per device shown. Returns NetworkDevicesResponse with device information including hardware addresses, interfaces, query counts, and associated IP addresses.
- `get_gateway(detailed=False)` - Get info about Pi-hole's gateway. Set `detailed=True` to include detailed interface and routing information (dependent on interface type and state). Returns NetworkGatewayResponse or NetworkGatewayDetailedResponse with gateway information.
- `get_interfaces(detailed=False)` - Get info about Pi-hole's network interfaces. Set `detailed=True` for more detailed information where available (dependent on interface type and state). Returns NetworkInterfacesResponse with interface information including names, types, states, statistics, and IP addresses.
- `get_routes(detailed=False)` - Get info about Pi-hole's network routes. Set `detailed=True` for more detailed information where available (dependent on route type and state). Returns NetworkRoutesResponse with routing table information including destinations, gateways, and interface mappings.
- `delete_device(device_id)` - Delete a device from the network table, removing all associated IP addresses and hostnames. Returns NetworkDeviceDeleteResponse with operation timing.

### PiHoleStats

The stats class for Pi-hole statistics and analytics operations.

**Methods:**
- `PiHoleStats(client)` - Create a new stats client using an existing PiHoleClient

**History and Activity:**
- `get_history()` - Get activity graph data for the last 24 hours. Returns HistoryResponse with timestamp-based query counts.
- `get_client_history()` - Get per-client activity graph data for the last 24 hours. Returns ClientHistoryResponse with client-specific query counts.
- `get_database_history(from_timestamp, until_timestamp)` - Get long-term activity data from database for specified time range.
- `get_database_client_history(from_timestamp, until_timestamp)` - Get long-term per-client activity data from database.

**Query Analysis:**
- `get_queries(length=100, cursor=None, from_timestamp=None, until_timestamp=None, upstream=None, domain=None, client=None)` - Get detailed query logs with optional filtering and pagination. Returns QueriesResponse with individual query entries.
- `get_query_suggestions()` - Get available filter suggestions for queries endpoint. Returns QuerySuggestionsResponse with domain, client, upstream, type, and status suggestions.

**Statistics:**
- `get_summary()` - Get comprehensive Pi-hole activity overview including query stats, client counts, and gravity info. Returns SummaryResponse.
- `get_query_types()` - Get query types breakdown (A, AAAA, PTR, etc.) for recent queries. Returns QueryTypesResponse.
- `get_recent_blocked(count=10)` - Get most recently blocked domains. Returns RecentBlockedResponse.
- `get_top_clients(blocked=None, count=10)` - Get top clients by query count. Use `blocked=True/False` to filter by blocked/permitted queries. Returns TopClientsResponse.
- `get_top_domains(blocked=None, count=10)` - Get top domains by query count. Use `blocked=True/False` to filter by blocked/permitted queries. Returns TopDomainsResponse.
- `get_upstreams()` - Get upstream server metrics including response times and query counts. Returns UpstreamsResponse.

**Database Analytics:**
- `get_database_query_types(from_timestamp, until_timestamp)` - Get query types breakdown from database for specified time range.
- `get_database_summary(from_timestamp, until_timestamp)` - Get database summary statistics for specified time range.
- `get_database_top_clients(from_timestamp, until_timestamp)` - Get top clients from database for specified time range.
- `get_database_top_domains(from_timestamp, until_timestamp)` - Get top domains from database for specified time range.
- `get_database_upstreams(from_timestamp, until_timestamp)` - Get upstream metrics from database for specified time range.

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

**Statistics and Analytics Models:**
- `HistoryResponse` - Activity graph data with timestamp-based query counts
- `ClientHistoryResponse` - Per-client activity data with client mappings
- `QueriesResponse` - Detailed query logs with filtering and pagination
- `QuerySuggestionsResponse` - Available filter suggestions for queries
- `SummaryResponse` - Comprehensive Pi-hole activity overview
- `TopClientsResponse` - Top clients by query count
- `TopDomainsResponse` - Top domains by query count
- `UpstreamsResponse` - Upstream server metrics and statistics
- `QueryTypesResponse` - Query types breakdown (A, AAAA, PTR, etc.)
- `RecentBlockedResponse` - Recently blocked domains
- `DatabaseSummaryResponse` - Database summary statistics for time ranges

**Network Models:**
- `NetworkDevice` - Represents a network device with hardware address, interface, name, query statistics, and associated IP addresses
- `NetworkDeviceAddress` - IP address information for a network device including hostname and last query timestamp
- `NetworkDevicesResponse` - Container for network devices information
- `NetworkGateway` - Gateway information including address family, interface, IP address, and local addresses
- `NetworkGatewayResponse` - Container for gateway information
- `NetworkGatewayDetailedResponse` - Detailed gateway information including routes and interfaces
- `NetworkInterface` - Network interface information including name, type, state, statistics, and IP addresses
- `NetworkInterfaceAddress` - IP address configuration for a network interface
- `NetworkInterfaceStats` - Network interface statistics (RX/TX bytes, architecture)
- `NetworkInterfacesResponse` - Container for network interfaces information
- `NetworkRoute` - Network route information including destination, gateway, interface, and routing table details
- `NetworkRoutesResponse` - Container for network routes information
- `NetworkDeviceDeleteResponse` - Response for network device deletion operations

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
