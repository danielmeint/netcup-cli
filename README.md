# netcup CLI

A Python command-line interface for managing DNS records via the netcup DNS API.

## Features

✅ **Authentication Management**: Secure credential storage using system keyring  
✅ **DNS Zone Info**: View zone details, TTL, serial, DNSSEC status  
✅ **DNS Records**: List, add, update, and delete DNS records  
✅ **Rich Output**: Beautiful formatted tables and clear status messages  
✅ **Debug Mode**: Comprehensive debugging for troubleshooting  

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd netcup-cli

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

### 1. Authentication

First, log in with your netcup credentials:

```bash
netcup auth login
```

You'll be prompted for:
- Customer Number (found in your netcup Customer Control Panel)
- API Key (generated in CCP under "API")  
- API Password (generated in CCP under "API")

Credentials are securely stored in your system keyring.

### 2. DNS Management

**View DNS zone information:**
```bash
netcup dns zone info example.com
```

**List all DNS records:**
```bash
netcup dns records list example.com
```

**Add a new DNS record:**
```bash
netcup dns record add example.com subdomain A 192.168.1.1
netcup dns record add example.com mail MX mail.example.com --priority 10
```

**Update an existing record:**
```bash
netcup dns record update example.com 12345 subdomain A 192.168.1.2
```

**Delete a record:**
```bash
netcup dns record delete example.com 12345
```

### 3. Other Commands

**Check authentication status:**
```bash
netcup auth status
```

**View configuration:**
```bash
netcup config show
```

**Logout:**
```bash
netcup auth logout
```

**Enable debug mode:**
```bash
netcup --debug dns zone info example.com
```

## Requirements

- Python 3.8+
- netcup account with DNS API access
- Domain(s) registered with netcup using netcup nameservers

## API Access Setup

1. Log into your [netcup Customer Control Panel](https://www.customercontrolpanel.de)
2. Navigate to "API" section
3. Generate an API Key and API Password
4. Ensure DNS management is enabled for your domains

## Troubleshooting

- Use `--debug` flag for detailed API response logging
- Verify your domains are using netcup nameservers
- Check that DNS management is enabled in your CCP
- Ensure API credentials have proper permissions

## License

MIT License - see LICENSE file for details. 