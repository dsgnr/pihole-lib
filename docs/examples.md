# Examples

This page contains practical examples for using the Pi-hole Python library.

## Quick Start

```python
from pihole_lib import PiHoleClient

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get system info
    login_info = client.info.get_login_info()
    print(f"Pi-hole version: {login_info.version}")

    # Update gravity
    for line in client.actions.update_gravity():
        print(line.strip())
```

## System Information

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Login info
    login_info = client.info.get_login_info()
    print(f"DNS Status: {login_info.dns}")

    # Version info
    version = client.info.get_version_info()
    print(f"Core: {version.version.core.local.version}")

    # System resources
    system = client.info.get_system_info()
    print(f"RAM: {system.system.memory.ram.percent_used:.1f}%")
```

## DNS Management

```python
from pihole_lib import PiHoleClient

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    dns = client.dns

    # Get DNS config
    config = dns.get_config()
    print(f"Blocking active: {config.blocking_active}")

    # Add/remove A records
    dns.add_a_record("server.local", "192.168.1.100")
    dns.remove_a_record("server.local", "192.168.1.100")

    # Add/remove CNAME records
    dns.add_cname_record("www.local", "server.local")
    dns.remove_cname_record("www.local", "server.local")

    # Blocking control
    dns.disable_blocking(timer=300)  # Disable for 5 minutes
    dns.enable_blocking()
```

## Domain Lists

```python
from pihole_lib import PiHoleClient, ListType

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    # Get lists
    all_lists = client.lists.get_lists()
    block_lists = client.lists.get_lists(list_type=ListType.BLOCK)

    # Add a blocklist
    client.lists.add_list(
        address="https://example.com/blocklist.txt",
        list_type=ListType.BLOCK,
        comment="Example blocklist"
    )

    # Search domains
    results = client.lists.search_domains("example.com")
    print(f"Found {results.search.results.total} matches")

    # Delete a list
    client.lists.delete_list("https://example.com/blocklist.txt", ListType.BLOCK)
```

## Domain Management

```python
from pihole_lib import PiHoleClient, DomainType, DomainKind

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    domains = client.domains

    # Get domains
    all_domains = domains.get_domains()
    blocked = domains.get_domains(domain_type=DomainType.DENY)

    # Add a blocked domain
    domains.add_domain(
        domain="badsite.com",
        domain_type=DomainType.DENY,
        domain_kind=DomainKind.EXACT,
        comment="Malicious site"
    )

    # Add a regex pattern
    domains.add_domain(
        domain=r".*\.ads\..*",
        domain_type=DomainType.DENY,
        domain_kind=DomainKind.REGEX
    )

    # Delete a domain
    domains.delete_domain("badsite.com", DomainType.DENY, DomainKind.EXACT)
```

## Groups

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    groups = client.groups

    # Get all groups
    all_groups = groups.get_groups()

    # Create a group
    groups.create_group(name="family_devices", comment="Family devices")

    # Update a group
    groups.update_group(name="family_devices", comment="Updated comment")

    # Delete a group
    groups.delete_group("family_devices")
```

## Client Management

```python
from pihole_lib import PiHoleClient

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    clients = client.clients

    # Get all clients
    all_clients = clients.get_clients()

    # Add a client
    clients.add_client(
        client="192.168.1.100",
        comment="John's laptop",
        groups=[0]
    )

    # Get suggestions (unconfigured clients)
    suggestions = clients.get_client_suggestions()

    # Delete a client
    clients.delete_client("192.168.1.100")
```

## Configuration

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    config = client.config

    # Get configuration
    current = config.get_config()
    dns_only = config.get_config("dns")

    # Update configuration
    config.update_config({
        "dns": {
            "upstreams": ["1.1.1.1", "1.0.0.1"],
            "queryLogging": True
        }
    })

    # Add/remove config items
    config.add_config_item("dns/upstreams", "8.8.8.8")
    config.remove_config_item("dns/upstreams", "8.8.8.8")
```

## Actions & Maintenance

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    actions = client.actions

    # Update gravity
    for line in actions.update_gravity():
        print(line.strip())

    # Restart DNS
    actions.restart_dns()

    # Flush logs
    actions.flush_logs()

    # Flush network table
    actions.flush_network()
```

## Backup & Restore

```python
from pihole_lib import PiHoleClient, TeleporterImportOptions, TeleporterGravityOptions

with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    backup = client.backup

    # Export backup
    backup_file = backup.export_backup("/path/to/backups")

    # Import with options
    options = TeleporterImportOptions(
        config=True,
        dhcp_leases=False,
        gravity=TeleporterGravityOptions(group=True, adlist=True)
    )
    backup.import_backup(backup_file, options)
```

## Statistics

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    stats = client.stats

    # Summary
    summary = stats.get_summary()
    print(f"Blocked: {summary.queries.percent_blocked}%")

    # Top domains/clients
    top_domains = stats.get_top_domains(count=10)
    top_clients = stats.get_top_clients(count=10)

    # Recent blocked
    blocked = stats.get_recent_blocked(count=10)

    # Query history
    history = stats.get_history()
```

## DHCP

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    dhcp = client.dhcp

    # Get leases
    leases = dhcp.get_leases()
    for lease in leases.leases:
        print(f"{lease.name}: {lease.ip}")

    # Delete a lease
    dhcp.delete_lease("192.168.1.50")
```

## Network

```python
with PiHoleClient("http://192.168.1.100", password="your-password") as client:
    network = client.network

    # Get devices
    devices = network.get_devices(max_devices=10)

    # Get gateway info
    gateway = network.get_gateway()

    # Get interfaces
    interfaces = network.get_interfaces()

    # Get routes
    routes = network.get_routes()
```

## Error Handling

```python
from pihole_lib import (
    PiHoleClient,
    PiHoleAuthenticationError,
    PiHoleConnectionError,
    PiHoleServerError
)

try:
    with PiHoleClient("http://192.168.1.100", password="wrong") as client:
        pass
except PiHoleAuthenticationError:
    print("Authentication failed")
except PiHoleConnectionError:
    print("Connection failed")
except PiHoleServerError:
    print("Server error")
```

## Manual Session Control

```python
from pihole_lib import PiHoleClient

client = PiHoleClient("http://192.168.1.100", password="your-password")

try:
    client._ensure_session()
    client._authenticate()

    if client.is_authenticated():
        print(f"Session: {client.get_session_id()}")
finally:
    client.close()
```
