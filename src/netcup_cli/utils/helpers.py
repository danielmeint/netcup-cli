"""
Helper utility functions for netcup CLI.
"""

import re
from typing import Optional


def validate_domain(domain: str) -> bool:
    """
    Validate if a string is a valid domain name.

    Args:
        domain: The domain name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not domain or len(domain) > 253:
        return False

    # Remove trailing dot if present
    if domain.endswith("."):
        domain = domain[:-1]

    # Domain name regex pattern
    pattern = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
    )

    return bool(pattern.match(domain))


def validate_record_type(record_type: str) -> bool:
    """
    Validate if a string is a valid DNS record type.

    Args:
        record_type: The record type to validate

    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = {"A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "PTR", "CAA"}
    return record_type.upper() in valid_types


def validate_hostname(hostname: str) -> bool:
    """
    Validate if a string is a valid hostname.

    Args:
        hostname: The hostname to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not hostname or len(hostname) > 63:
        return False

    # Allow @ for root domain and * for wildcards
    if hostname in ["@", "*"]:
        return True

    # Hostname pattern (can include wildcards)
    pattern = re.compile(r"^[a-zA-Z0-9*]([a-zA-Z0-9*-]{0,61}[a-zA-Z0-9*])?$")
    return bool(pattern.match(hostname))


def validate_ip_address(ip: str) -> bool:
    """
    Validate if a string is a valid IP address (IPv4 or IPv6).

    Args:
        ip: The IP address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # IPv4 pattern
    ipv4_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )

    # IPv6 pattern (simplified)
    ipv6_pattern = re.compile(r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$")

    return bool(ipv4_pattern.match(ip) or ipv6_pattern.match(ip))


def format_record_destination(record_type: str, destination: str) -> str:
    """
    Format a record destination based on the record type.

    Args:
        record_type: The DNS record type
        destination: The destination value

    Returns:
        str: The formatted destination
    """
    record_type = record_type.upper()

    # For MX and SRV records, ensure proper formatting
    if record_type == "MX" and not destination.endswith("."):
        # MX records should end with a dot if they're FQDNs
        if "." in destination:
            destination += "."

    elif record_type == "CNAME" and not destination.endswith("."):
        # CNAME records should end with a dot if they're FQDNs
        if "." in destination:
            destination += "."

    return destination


def suggest_record_type(destination: str) -> Optional[str]:
    """
    Suggest a DNS record type based on the destination.

    Args:
        destination: The destination value

    Returns:
        Optional[str]: Suggested record type or None
    """
    if validate_ip_address(destination):
        if ":" in destination:
            return "AAAA"  # IPv6
        else:
            return "A"  # IPv4
    elif "." in destination:
        return "CNAME"  # Domain name

    return None


def format_ttl(ttl: Optional[str]) -> str:
    """
    Format TTL value for display.

    Args:
        ttl: The TTL value

    Returns:
        str: Formatted TTL string
    """
    if not ttl:
        return "N/A"

    try:
        ttl_seconds = int(ttl)
        if ttl_seconds >= 86400:  # 1 day
            days = ttl_seconds // 86400
            return f"{days}d"
        elif ttl_seconds >= 3600:  # 1 hour
            hours = ttl_seconds // 3600
            return f"{hours}h"
        elif ttl_seconds >= 60:  # 1 minute
            minutes = ttl_seconds // 60
            return f"{minutes}m"
        else:
            return f"{ttl_seconds}s"
    except (ValueError, TypeError):
        return str(ttl)


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length with ellipsis.

    Args:
        text: The text to truncate
        max_length: Maximum length before truncation

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def normalize_hostname(hostname: str, domain: str) -> str:
    """
    Normalize a hostname relative to a domain.

    Args:
        hostname: The hostname
        domain: The domain name

    Returns:
        str: Normalized hostname
    """
    if hostname == "@":
        return domain
    elif hostname.endswith(f".{domain}"):
        return hostname
    elif hostname.endswith("."):
        return hostname[:-1]
    else:
        return hostname
