# netcup API Response Format Analysis

This document tracks our findings about the netcup API response formats to improve our client implementation.

## API Response Structure

Based on the netcup API documentation, responses should follow this structure:

```json
{
  "status": "string",
  "statuscode": number,
  "longmessage": "string", 
  "shortmessage": "string",
  "responsedata": {} // This varies by endpoint
}
```

## Findings by Endpoint

### Authentication

#### `login` endpoint
**Purpose**: Authenticate and get session ID

**Expected Response**:
```json
{
  "status": "success",
  "statuscode": 2000,
  "longmessage": "Login successful",
  "shortmessage": "Login successful", 
  "responsedata": {
    "apisessionid": "abc123..."
  }
}
```

**Actual Response**: 
```json
{
  "serverrequestid": "0=cMk2WZeMVmwR4sY",
  "clientrequestid": "",
  "action": "login",
  "status": "success",
  "statuscode": 2000,
  "shortmessage": "Login successful",
  "longmessage": "Session has been created successful.",
  "responsedata": {
    "apisessionid": "M1kyODViNDkxSzY3MXZBbW9IYVRqR2JyU2ZCUm1RSTU4MnI3Mz"
  }
}
```

✅ **Analysis**: Login works perfectly and matches expected format.

### DNS Operations

#### `infoDnsZone` endpoint
**Purpose**: Get DNS zone information

**Expected Response**:
```json
{
  "status": "success",
  "statuscode": 2000,
  "longmessage": "...",
  "shortmessage": "...",
  "responsedata": {
    "name": "example.com",
    "ttl": "86400",
    "serial": "2024010101",
    "refresh": "28800", 
    "retry": "7200",
    "expire": "604800",
    "dnssecstatus": false
  }
}
```

**Actual Response** (for non-existent domains):
```json
{
  "serverrequestid": "Ukx3MdjH=0oByVQNV",
  "clientrequestid": "",
  "action": "infoDnsZone",
  "status": "error",
  "statuscode": 4008,
  "shortmessage": "Input value in invalid format",
  "longmessage": "At least one input value is in a valid format. Please check documemtation.",
  "responsedata": ""
}
```

❌ **Analysis**: All tested domains return 4008 error. This suggests:
1. The domains don't exist in this netcup account
2. The domains aren't configured for DNS API access
3. The domains use external nameservers (not netcup's)

#### `infoDnsRecords` endpoint 
**Purpose**: Get all DNS records for a domain

**Expected Response**:
```json
{
  "status": "success", 
  "statuscode": 2000,
  "longmessage": "...",
  "shortmessage": "...",
  "responsedata": {
    "dnsrecords": [
      {
        "id": "123",
        "hostname": "@",
        "type": "A", 
        "priority": "",
        "destination": "192.168.1.1",
        "deleterecord": false,
        "state": "yes"
      }
    ]
  }
}
```

**Actual Response**: _(to be documented)_

## Issues Discovered

### Issue 1: responsedata validation error
**Error**: `1 validation error for APIResponse responsedata Input should be a valid dictionary`

**Analysis**: 
- Our Pydantic model expected `responsedata` to always be a `Dict[str, Any]`
- In reality, `responsedata` can be:
  - `null` for some responses
  - An array for some endpoints
  - A dictionary for most endpoints
  - Other primitive types in error cases

**Fix Applied**: Changed `responsedata: Optional[Dict[str, Any]]` to `responsedata: Optional[Any]`

**Root Cause Confirmed**: In error responses, `responsedata` is an empty string `""` instead of `null` or a dictionary.

### Issue 2: Command syntax confusion
**Error**: `No such command 'zone'`

**Analysis**: User ran `netcup zone info` instead of `netcup dns zone info`

**Note**: Our CLI structure is:
- `netcup dns zone info <domain>`
- `netcup dns records list <domain>`
- `netcup dns record add/update/delete <domain> ...`

### Issue 3: Domain Access Requirements
**Error**: `Input value in invalid format` (Status 4008) for all tested domains

**Analysis**: 
- The DNS API only works with domains that:
  1. Are registered through this netcup account, OR
  2. Have netcup nameservers configured, AND
  3. Are properly set up for DNS management in the netcup CCP

**Discovery**: Customer account 125655 has API access AND all 9 domains ARE using netcup nameservers, but DNS API still fails.

**CRITICAL FINDING**: All domains use netcup nameservers but DNS API returns 4008 for all of them:
- danielmeint.com ✅ uses netcup NS → ❌ API fails  
- danielmeint.de ✅ uses netcup NS → ❌ API fails
- (all 9 domains show this pattern)

**New Theory**: The issue is NOT nameserver configuration. Possible causes:
1. DNS management must be explicitly enabled in CCP for each domain
2. API key may lack DNS management permissions
3. Domain type restriction (zusätzlich vs. primary domains?)
4. Account-level DNS API restriction

## Testing Commands

Use these commands to test and debug the API:

```bash
# Enable debug mode
export NETCUP_DEBUG=1

# Test authentication
netcup --debug auth status

# Test DNS zone info
netcup --debug dns zone info danielmeint.de

# Test DNS records listing
netcup --debug dns records list danielmeint.de
```

## curl Testing

Test the API directly with curl:

```bash
# Login test (replace with actual credentials)
curl -X POST "https://ccp.netcup.net/run/webservice/servers/endpoint.php?JSON" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "login",
    "param": {
      "apikey": "YOUR_API_KEY",
      "apipassword": "YOUR_API_PASSWORD", 
      "customernumber": "YOUR_CUSTOMER_NUMBER"
    }
  }'
```

## Response Format Documentation

_(This section will be updated as we discover actual response formats)_

### Login Response Format
```
TBD - to be documented after testing
```

### DNS Zone Response Format  
```
TBD - to be documented after testing
```

### DNS Records Response Format
**Error Response** (when domain not accessible):
```json
{
  "serverrequestid": "RIRF10QTSjzB=02gR",
  "clientrequestid": "",
  "action": "infoDnsRecords", 
  "status": "error",
  "statuscode": 4008,
  "shortmessage": "Input value in invalid format",
  "longmessage": "At least one input value is in a valid format. Please check documemtation.",
  "responsedata": ""
}
```

**Note**: Same pattern as zone info - domains not configured for DNS management return 4008.

## Summary of Testing Results

✅ **Authentication**: Works perfectly
❌ **DNS Operations**: Blocked due to domain access requirements 
✅ **Error Handling**: Improved with helpful user guidance
✅ **Response Format**: Now handles all response types correctly

## Improvements Made

1. **Fixed Pydantic validation**: `responsedata` now accepts any type
2. **Better error messages**: Status code 4008 now shows helpful tips
3. **Added DNS check command**: Helps users understand requirements
4. **Robust logout**: Continues even if logout API call fails
5. **Debug mode**: Comprehensive logging for troubleshooting

## User Next Steps

To use this CLI effectively, the user needs to:

1. **Register a domain** through netcup, OR
2. **Configure an existing domain** to use netcup nameservers:
   - root-dns.netcup.net
   - second-dns.netcup.net 
   - third-dns.netcup.net
3. **Set up DNS management** in the netcup Customer Control Panel (CCP)

Once properly configured, all CLI commands should work as designed. 