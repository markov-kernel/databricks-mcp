"""
Configuration settings for the Databricks MCP server.
"""

import os
from typing import Any, Dict, Optional

# Import dotenv if available, but don't require it.
# Only load dotenv if not running via Cursor MCP (which provides env vars directly).
if not os.environ.get("RUNNING_VIA_CURSOR_MCP"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Version
VERSION = "0.4.4"


class Settings(BaseSettings):
    """Base settings for the application."""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Databricks API configuration
    DATABRICKS_HOST: str = os.environ.get("DATABRICKS_HOST", "https://example.databricks.net")
    DATABRICKS_TOKEN: str = os.environ.get("DATABRICKS_TOKEN", "dapi_token_placeholder")
    DATABRICKS_WAREHOUSE_ID: Optional[str] = os.environ.get("DATABRICKS_WAREHOUSE_ID")

    # Server configuration
    SERVER_HOST: str = os.environ.get("SERVER_HOST", "0.0.0.0") 
    SERVER_PORT: int = int(os.environ.get("SERVER_PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # Runtime controls
    TOOL_TIMEOUT_SECONDS: int = int(os.environ.get("TOOL_TIMEOUT_SECONDS", "300"))
    MAX_CONCURRENT_REQUESTS: int = int(os.environ.get("MAX_CONCURRENT_REQUESTS", "8"))

    # HTTP / retry behavior
    HTTP_TIMEOUT_SECONDS: float = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "60"))
    API_MAX_RETRIES: int = int(os.environ.get("API_MAX_RETRIES", "3"))
    API_RETRY_BACKOFF_SECONDS: float = float(os.environ.get("API_RETRY_BACKOFF_SECONDS", "0.5"))

    # Version
    VERSION: str = VERSION

    @field_validator("DATABRICKS_HOST")
    def validate_databricks_host(cls, v: str) -> str:
        """Validate Databricks host URL."""
        if not v.startswith(("https://", "http://")):
            raise ValueError("DATABRICKS_HOST must start with http:// or https://")
        return v

    @field_validator("DATABRICKS_WAREHOUSE_ID")
    def validate_warehouse_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate warehouse ID format if provided."""
        if v and len(v) < 10:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Warehouse ID '{v}' seems unusually short")
        return v

# Create global settings instance
settings = Settings()


def get_api_headers() -> Dict[str, str]:
    """Get headers for Databricks API requests."""
    return {
        "Authorization": f"Bearer {settings.DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }


def get_databricks_api_url(endpoint: str) -> str:
    """
    Construct the full Databricks API URL.
    
    Args:
        endpoint: The API endpoint path, e.g., "/api/2.0/clusters/list"
    
    Returns:
        Full URL to the Databricks API endpoint
    """
    # Ensure endpoint starts with a slash
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    # Remove trailing slash from host if present
    host = settings.DATABRICKS_HOST.rstrip("/")
    
    return f"{host}{endpoint}" 
