# netcup CLI

A command-line tool for managing netcup DNS records via the netcup API.

## Installation

```bash
pip install netcup-cli
```

## Usage

```bash
# Authenticate
netcup auth login

# List DNS records
netcup dns records list example.com

# Add a DNS record
netcup dns record add example.com www A 192.168.1.1
```

## Development

This project is in early development. See `PLAN.md` for the development roadmap.

## License

MIT 