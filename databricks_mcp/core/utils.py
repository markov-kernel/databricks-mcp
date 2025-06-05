"""
Utility functions for the Databricks MCP server.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException

from databricks_mcp.core.config import get_api_headers, get_databricks_api_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabricksAPIError(Exception):
    """Exception raised for errors in the Databricks API."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


def make_api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make a request to the Databricks API.
    
    Args:
        method: HTTP method ("GET", "POST", "PUT", "DELETE")
        endpoint: API endpoint path
        data: Request body data
        params: Query parameters
        files: Files to upload
        
    Returns:
        Response data as a dictionary
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    url = get_databricks_api_url(endpoint)
    headers = get_api_headers()
    
    try:
        # Log the request (omit sensitive information)
        safe_data = "**REDACTED**" if data else None
        logger.debug(f"API Request: {method} {url} Params: {params} Data: {safe_data}")
        
        # Convert data to JSON string if provided
        json_data = json.dumps(data) if data and not files else data
        
        # Make the request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=json_data if not files else data,
            files=files,
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        if response.content:
            return response.json()
        return {}
        
    except RequestException as e:
        # Handle request exceptions
        status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None
        error_msg = f"API request failed: {str(e)}"
        
        # Try to extract error details from response
        error_response = None
        if hasattr(e, "response") and e.response is not None:
            try:
                error_response = e.response.json()
                error_msg = f"{error_msg} - {error_response.get('error', '')}"
            except ValueError:
                error_response = e.response.text
        
        # Log the error
        logger.error(f"API Error: {error_msg}", exc_info=True)
        
        # Raise custom exception
        raise DatabricksAPIError(error_msg, status_code, error_response) from e


def format_response(
    success: bool, 
    data: Optional[Union[Dict[str, Any], List[Any]]] = None, 
    error: Optional[str] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Format a standardized response.
    
    Args:
        success: Whether the operation was successful
        data: Response data
        error: Error message if not successful
        status_code: HTTP status code
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "success": success,
        "status_code": status_code,
    }
    
    if data is not None:
        response["data"] = data
        
    if error:
        response["error"] = error
        
    return response 