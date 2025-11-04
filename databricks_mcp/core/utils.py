"""
Utility functions for the Databricks MCP server.
"""

import asyncio
import logging
import random
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union

import httpx
from httpx import HTTPError, HTTPStatusError

from databricks_mcp.core.config import (
    get_api_headers,
    get_databricks_api_url,
    settings,
)

logger = logging.getLogger(__name__)

# Context for propagating correlation IDs into API calls.
request_context_id: ContextVar[Optional[str]] = ContextVar("databricks_mcp_request_id", default=None)


class DatabricksAPIError(Exception):
    """Exception raised for errors in the Databricks API."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


async def make_api_request(
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
    headers = get_api_headers().copy()
    request_id = request_context_id.get()
    if request_id:
        headers["X-Databricks-MCP-Request-ID"] = request_id
    retries = settings.API_MAX_RETRIES
    backoff_base = settings.API_RETRY_BACKOFF_SECONDS
    retry_statuses = {408, 425, 429, 500, 502, 503, 504}

    safe_data = "**REDACTED**" if data else None
    logger.debug("API Request: %s %s Params: %s Data: %s", method, url, params, safe_data)

    attempt = 0
    while True:
        try:
            timeout = httpx.Timeout(settings.HTTP_TIMEOUT_SECONDS)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data if not files else None,
                    data=data if files else None,
                    files=files,
                )

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except HTTPStatusError as e:
            status_code = e.response.status_code if e.response else None
            error_response = None
            error_msg = f"API request failed: {e!s}"
            if e.response is not None:
                try:
                    error_response = e.response.json()
                    error_text = error_response.get("error") or error_response.get("message")
                    if error_text:
                        error_msg = f"{error_msg} - {error_text}"
                except ValueError:
                    error_response = e.response.text

            if status_code in retry_statuses and attempt < retries:
                wait = backoff_base * (2 ** attempt) + random.uniform(0, backoff_base)
                logger.warning(
                    "Retryable Databricks API error (%s). Retrying in %.2fs",
                    status_code,
                    wait,
                )
                attempt += 1
                await asyncio.sleep(wait)
                continue

            logger.error("API Error: %s", error_msg, exc_info=True)
            raise DatabricksAPIError(error_msg, status_code, error_response) from e

        except HTTPError as e:
            status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            error_msg = f"API request failed: {e!s}"

            if status_code in retry_statuses and attempt < retries:
                wait = backoff_base * (2 ** attempt) + random.uniform(0, backoff_base)
                logger.warning(
                    "HTTP transport error (status=%s). Retrying in %.2fs",
                    status_code,
                    wait,
                )
                attempt += 1
                await asyncio.sleep(wait)
                continue

            error_response = None
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_response = e.response.json()
                except ValueError:
                    error_response = e.response.text

            logger.error("API Error: %s", error_msg, exc_info=True)
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
