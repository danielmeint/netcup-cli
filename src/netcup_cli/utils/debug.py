"""
Debug utilities for netcup CLI.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def log_api_response(
    action: str,
    response_data: Dict[str, Any],
    request_params: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log API response to a debug file for analysis.

    Args:
        action: The API action performed
        response_data: The full response data
        request_params: The request parameters (optional)
    """
    debug_dir = Path.cwd() / "debug"
    debug_dir.mkdir(exist_ok=True)

    debug_file = debug_dir / "api_responses.jsonl"

    debug_entry = {
        "action": action,
        "response": response_data,
        "request_params": request_params,
    }

    with open(debug_file, "a") as f:
        f.write(json.dumps(debug_entry, indent=None) + "\n")


def print_debug_info(label: str, data: Any) -> None:
    """Print debug information in a formatted way."""
    print(f"\n🐛 DEBUG - {label}:")
    print(f"Type: {type(data)}")
    if hasattr(data, "__dict__"):
        print(f"Attributes: {data.__dict__}")
    else:
        print(f"Value: {data}")
    print("=" * 50)


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return os.getenv("NETCUP_DEBUG", "").lower() in ("1", "true", "yes")
