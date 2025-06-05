"""
Authentication functionality for the Databricks MCP server.
"""

import logging
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from databricks_mcp.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# API key header scheme
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def validate_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> Dict[str, str]:
    """
    Validate API key for protected endpoints.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        Dictionary with authentication info
        
    Raises:
        HTTPException: If authentication fails
    """
    # For now, we're using a simple token comparison
    # In a production environment, you might want to use a database or more secure method
    
    # Check if API key is required in the current environment
    if not settings.DEBUG:
        if not api_key:
            logger.warning("Authentication failed: Missing API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
            
        # In a real scenario, you would validate against a secure storage
        # For demo purposes, we'll just check against an environment variable
        # NEVER do this in production - use a proper authentication system!
        valid_keys = ["test-api-key"]  # Replace with actual implementation
        
        if api_key not in valid_keys:
            logger.warning("Authentication failed: Invalid API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
    
    # Return authentication info
    return {"authenticated": True}


def get_current_user():
    """
    Dependency to get current user.
    
    For future implementation of user-specific functionality.
    Currently returns a placeholder.
    """
    # This would be expanded in a real application with actual user information
    return {"username": "admin"} 