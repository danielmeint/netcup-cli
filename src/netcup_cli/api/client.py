"""
Core API client for netcup API.
"""

import time
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel

from ..config.manager import ConfigManager
from ..utils.debug import is_debug_mode, log_api_response, print_debug_info
from ..utils.exceptions import APIError, SessionExpiredError


class APIResponse(BaseModel):
    """Model for API response structure."""

    status: str
    statuscode: int
    longmessage: str
    shortmessage: str
    responsedata: Optional[Any] = None  # Can be dict, list, null, etc.


class NetcupAPIClient:
    """Client for interacting with the netcup API."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get_config()
        self.session_id: Optional[str] = None
        self.session_created_at: Optional[float] = None

    def _make_request(self, action: str, params: Dict[str, Any]) -> APIResponse:
        """
        Make a request to the netcup API.

        Args:
            action: The API action to perform
            params: Parameters for the API call

        Returns:
            APIResponse: The parsed API response

        Raises:
            APIError: If the API returns an error
        """
        payload = {"action": action, "param": params}

        try:
            response = requests.post(
                self.config.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

        except requests.RequestException as e:
            raise APIError(f"Failed to connect to netcup API: {e}")

        try:
            data = response.json()
        except ValueError as e:
            raise APIError(f"Invalid JSON response from API: {e}")

        # Debug logging
        if is_debug_mode():
            print_debug_info(f"Raw API Response for {action}", data)
            log_api_response(action, data, params)

        api_response = APIResponse(**data)

        # Check if the API returned an error
        if api_response.statuscode >= 4000:
            # Check for session expiry
            if api_response.statuscode == 4013:  # Session expired
                self._clear_session()
                raise SessionExpiredError("API session has expired")

            raise APIError(
                f"API error: {api_response.shortmessage} - {api_response.longmessage}",
                status_code=api_response.statuscode,
            )

        return api_response

    def _get_base_params(self) -> Dict[str, str]:
        """Get base parameters that are included in most API calls."""
        params = {
            "apikey": self.config.api_key,
            "customernumber": self.config.customer_number,  # This was missing!
        }

        if self.session_id:
            params["apisessionid"] = self.session_id

        return params

    def _is_session_valid(self) -> bool:
        """Check if the current session is still valid."""
        if not self.session_id or not self.session_created_at:
            return False

        # Check if session has expired (15 minutes = 900 seconds)
        session_age = time.time() - self.session_created_at
        return session_age < self.config.session_timeout

    def _clear_session(self) -> None:
        """Clear the current session."""
        self.session_id = None
        self.session_created_at = None
        self.config_manager.clear_session_id()

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authenticated session."""
        # Try to restore session from storage
        if not self.session_id:
            self.session_id = self.config_manager.get_session_id()
            if self.session_id:
                # We don't know when this session was created, so assume it's fresh
                self.session_created_at = time.time()

        # Check if we need to authenticate
        if not self._is_session_valid():
            self.login()

    def login(self) -> str:
        """
        Authenticate with the netcup API.

        Returns:
            str: The session ID

        Raises:
            APIError: If authentication fails
        """
        params = {
            "apikey": self.config.api_key,
            "apipassword": self.config.api_password,
            "customernumber": self.config.customer_number,
        }

        response = self._make_request("login", params)

        if not response.responsedata or "apisessionid" not in response.responsedata:
            raise APIError("Login successful but no session ID received")

        self.session_id = response.responsedata["apisessionid"]
        self.session_created_at = time.time()

        # Store session ID for future use
        self.config_manager.save_session_id(self.session_id)

        return self.session_id

    def logout(self) -> None:
        """
        End the current API session.

        Raises:
            APIError: If logout fails
        """
        if not self.session_id:
            return

        params = self._get_base_params()

        try:
            self._make_request("logout", params)
        except APIError as e:
            # Log the error but don't fail - we'll clear session anyway
            if is_debug_mode():
                print_debug_info("Logout Error", str(e))
        finally:
            # Always clear the session, even if logout fails
            self._clear_session()

    def make_authenticated_request(
        self, action: str, params: Dict[str, Any]
    ) -> APIResponse:
        """
        Make an authenticated request to the API.

        Args:
            action: The API action to perform
            params: Additional parameters for the API call

        Returns:
            APIResponse: The API response

        Raises:
            APIError: If the request fails
            SessionExpiredError: If the session expires and re-authentication fails
        """
        self._ensure_authenticated()

        # Merge base params with provided params
        request_params = self._get_base_params()
        request_params.update(params)

        try:
            return self._make_request(action, request_params)
        except SessionExpiredError:
            # Try to re-authenticate once
            self.login()
            request_params = self._get_base_params()
            request_params.update(params)
            return self._make_request(action, request_params)
