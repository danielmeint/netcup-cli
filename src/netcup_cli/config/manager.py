"""
Configuration management for netcup CLI.
"""

import os
from pathlib import Path
from typing import Optional

import keyring
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from ..utils.exceptions import ConfigurationError


class NetcupConfig(BaseModel):
    """Configuration model for netcup CLI."""
    
    customer_number: str = Field(..., description="Netcup customer number")
    api_key: str = Field(..., description="Netcup API key")
    api_password: str = Field(..., description="Netcup API password")
    api_endpoint: str = Field(
        default="https://ccp.netcup.net/run/webservice/servers/endpoint.php?JSON",
        description="Netcup API endpoint"
    )
    session_timeout: int = Field(default=900, description="Session timeout in seconds (15 minutes)")
    

class ConfigManager:
    """Manages configuration and credentials for netcup CLI."""
    
    KEYRING_SERVICE = "netcup-cli"
    CONFIG_DIR = Path.home() / ".config" / "netcup-cli"
    CONFIG_FILE = CONFIG_DIR / "config"
    
    def __init__(self):
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self._ensure_config_dir()
        
        # Load environment variables from .env file if it exists
        load_dotenv()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self) -> NetcupConfig:
        """
        Get configuration from environment variables or keyring.
        
        Priority:
        1. Environment variables
        2. Keyring storage
        
        Returns:
            NetcupConfig: The configuration object
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Try environment variables first
        customer_number = os.getenv("NETCUP_CUSTOMER_NUMBER")
        api_key = os.getenv("NETCUP_API_KEY")
        api_password = os.getenv("NETCUP_API_PASSWORD")
        
        # If not in environment, try keyring
        if not customer_number:
            customer_number = keyring.get_password(self.KEYRING_SERVICE, "customer_number")
        
        if not api_key:
            api_key = keyring.get_password(self.KEYRING_SERVICE, "api_key")
            
        if not api_password:
            api_password = keyring.get_password(self.KEYRING_SERVICE, "api_password")
        
        # Validate that we have all required fields
        if not all([customer_number, api_key, api_password]):
            missing = []
            if not customer_number:
                missing.append("customer_number")
            if not api_key:
                missing.append("api_key")
            if not api_password:
                missing.append("api_password")
            
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing)}. "
                "Please run 'netcup auth login' or set environment variables."
            )
        
        return NetcupConfig(
            customer_number=customer_number,
            api_key=api_key,
            api_password=api_password,
            api_endpoint=os.getenv("NETCUP_API_ENDPOINT", NetcupConfig.model_fields["api_endpoint"].default),
        )
    
    def save_credentials(
        self, 
        customer_number: str, 
        api_key: str, 
        api_password: str
    ) -> None:
        """
        Save credentials to keyring.
        
        Args:
            customer_number: Netcup customer number
            api_key: Netcup API key
            api_password: Netcup API password
        """
        keyring.set_password(self.KEYRING_SERVICE, "customer_number", customer_number)
        keyring.set_password(self.KEYRING_SERVICE, "api_key", api_key)
        keyring.set_password(self.KEYRING_SERVICE, "api_password", api_password)
    
    def clear_credentials(self) -> None:
        """Clear all stored credentials from keyring."""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, "customer_number")
        except keyring.errors.PasswordDeleteError:
            pass
            
        try:
            keyring.delete_password(self.KEYRING_SERVICE, "api_key")
        except keyring.errors.PasswordDeleteError:
            pass
            
        try:
            keyring.delete_password(self.KEYRING_SERVICE, "api_password")
        except keyring.errors.PasswordDeleteError:
            pass
    
    def has_credentials(self) -> bool:
        """Check if credentials are available."""
        try:
            self.get_config()
            return True
        except ConfigurationError:
            return False
    
    def get_session_id(self) -> Optional[str]:
        """Get stored session ID."""
        return keyring.get_password(self.KEYRING_SERVICE, "session_id")
    
    def save_session_id(self, session_id: str) -> None:
        """Save session ID to keyring."""
        keyring.set_password(self.KEYRING_SERVICE, "session_id", session_id)
    
    def clear_session_id(self) -> None:
        """Clear stored session ID."""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, "session_id")
        except keyring.errors.PasswordDeleteError:
            pass 