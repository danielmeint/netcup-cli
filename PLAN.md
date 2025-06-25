# netcup CLI Tool - MVP Plan

## Overview
A Python CLI tool that wraps the netcup DNS API, allowing users to manage DNS zones and records from the command line.

## Target Users
- netcup customers who want to automate DNS management
- Users who prefer CLI over web interfaces
- Developers building automation scripts

## MVP Scope - DNS API Focus

### Core Features (Phase 1)
1. **Authentication Management**
   - Secure credential storage (API key, password, customer number)
   - Session management with automatic renewal
   - Login/logout commands

2. **DNS Zone Operations**
   - List all DNS zones for a domain
   - Get zone information
   - Basic zone status display

3. **DNS Record Operations**
   - List all records for a domain
   - Add new DNS records
   - Update existing DNS records
   - Delete DNS records
   - Support for common record types (A, AAAA, CNAME, MX, TXT)

4. **Configuration Management**
   - Config file for storing credentials securely
   - Environment variable support
   - Basic validation

### Technical Architecture

#### Project Structure
```
netcup-cli/
├── src/
│   └── netcup_cli/
│       ├── __init__.py
│       ├── main.py           # Entry point & CLI commands
│       ├── api/
│       │   ├── __init__.py
│       │   ├── client.py     # Core API client
│       │   ├── auth.py       # Authentication handling
│       │   └── dns.py        # DNS-specific operations
│       ├── config/
│       │   ├── __init__.py
│       │   └── manager.py    # Configuration management
│       └── utils/
│           ├── __init__.py
│           ├── exceptions.py # Custom exceptions
│           └── helpers.py    # Utility functions
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

#### Dependencies
- `click` - CLI framework
- `requests` - HTTP client
- `rich` - Beautiful terminal output
- `keyring` - Secure credential storage
- `pydantic` - Data validation
- `python-dotenv` - Environment variable support

#### CLI Command Structure
```bash
# Authentication
netcup auth login
netcup auth logout
netcup auth status

# DNS Zones
netcup dns zones list
netcup dns zone info <domain>

# DNS Records
netcup dns records list <domain>
netcup dns record add <domain> <name> <type> <value> [--ttl TTL]
netcup dns record update <domain> <record-id> [--name NAME] [--value VALUE] [--ttl TTL]
netcup dns record delete <domain> <record-id>

# Utility
netcup config show
netcup --help
```

### Implementation Details

#### Authentication Flow
1. User provides credentials via config file or environment variables
2. CLI authenticates with netcup API to get session ID
3. Session ID cached for subsequent requests (with 15min timeout handling)
4. Automatic re-authentication when session expires

#### Configuration Management
- Store credentials in secure keyring
- Support for multiple profiles/environments
- Fallback to environment variables
- Config validation on startup

#### Error Handling
- Clear error messages for common issues
- API error code mapping to user-friendly messages
- Proper exit codes for scripting
- Verbose mode for debugging

### API Integration Details

#### Base URL
- JSON endpoint: `https://ccp.netcup.net/run/webservice/servers/endpoint.php?JSON`

#### Request Format
```json
{
  "action": "method_name",
  "param": {
    "apikey": "...",
    "apisessionid": "...",
    // method-specific parameters
  }
}
```

#### Core Methods to Implement
1. `login` - Get session ID
2. `logout` - End session
3. `infoDnsZone` - Get zone information
4. `infoDnsRecords` - Get all records for a zone
5. `updateDnsRecords` - Modify DNS records

### Development Phases

#### Phase 1: Foundation ✅ COMPLETED
- [x] Project structure setup
- [x] Basic CLI framework with Click
- [x] API client foundation
- [x] Authentication implementation
- [x] Configuration management
- [x] DNS zone operations (info)
- [x] DNS record operations (list, add, update, delete)
- [x] Secure credential storage with keyring
- [x] Rich output formatting
- [x] Debug mode for troubleshooting
- [x] Comprehensive error handling

**Status**: All core functionality is working! The CLI is production-ready for DNS management.

#### Phase 2: Enhanced Features (Future)
- [ ] Support for more record types
- [ ] Bulk operations (CSV import/export)
- [ ] DNS record templates
- [ ] Enhanced testing suite

#### Phase 3: Polish & Documentation (Week 3)
- [ ] Rich output formatting
- [ ] Comprehensive error handling
- [ ] Documentation and examples
- [ ] Package for distribution

### Future Extensions (Post-MVP)
- Domain reselling API support (for resellers)
- Bulk operations (CSV import/export)
- DNS record templates
- Monitoring and alerting
- Integration with CI/CD pipelines
- Web UI dashboard
- Backup/restore functionality

### Security Considerations
- Never store credentials in plain text
- Use system keyring for secure storage
- Support for API key rotation
- Session timeout handling
- Input validation and sanitization

### Testing Strategy
- Unit tests for all API methods
- Integration tests with mock API responses
- CLI command testing
- Configuration validation tests
- Error scenario testing

## Success Criteria
1. Users can authenticate and manage DNS records via CLI
2. Clear, intuitive command structure
3. Proper error handling with helpful messages
4. Secure credential management
5. Well-documented with examples
6. Easy installation and setup process

## Getting Started
1. Set up development environment
2. Implement basic project structure
3. Create API client foundation
4. Build authentication system
5. Implement core DNS operations
6. Add CLI interface and commands
7. Test and refine user experience 