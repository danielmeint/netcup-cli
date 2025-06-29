# netcup CLI

[![PyPI version](https://badge.fury.io/py/netcup-dns-cli.svg)](https://badge.fury.io/py/netcup-dns-cli)
[![Python Versions](https://img.shields.io/pypi/pyversions/netcup-dns-cli.svg)](https://pypi.org/project/netcup-dns-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python command-line interface for managing DNS records via the netcup DNS API.

## Features

✅ **Authentication Management**: Secure credential storage using system keyring  
✅ **DNS Zone Info**: View zone details, TTL, serial, DNSSEC status  
✅ **DNS Records**: List, add, update, and delete DNS records  
✅ **Rich Output**: Beautiful formatted tables and clear status messages  
✅ **Debug Mode**: Comprehensive debugging for troubleshooting  

## Installation

### From PyPI (Recommended)

```bash
pip install netcup-dns-cli
```

### From Source

```bash
# Clone the repository
git clone https://github.com/danielmeint/netcup-cli.git
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

To set up API access for your netcup account, follow the official guide: [**Applying for an API password and API keys**](https://helpcenter.netcup.com/en/wiki/general/our-api#applying-for-an-api-password-and-api-keys)

Ensure DNS management is enabled for your domains in your netcup Customer Control Panel.

## Troubleshooting

- Use `--debug` flag for detailed API response logging
- Verify your domains are using netcup nameservers
- Check that DNS management is enabled in your CCP
- Ensure API credentials have proper permissions

## License

MIT License - see LICENSE file for details. 