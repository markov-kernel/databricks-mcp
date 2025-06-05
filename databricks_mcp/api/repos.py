"""API for Databricks Repos."""

import logging
from typing import Any, Dict, Optional

from databricks_mcp.core.utils import DatabricksAPIError, make_api_request

logger = logging.getLogger(__name__)


async def create_repo(url: str, provider: str, branch: Optional[str] = None, path: Optional[str] = None) -> Dict[str, Any]:
    """Create or clone a repo."""
    payload = {"url": url, "provider": provider}
    if branch:
        payload["branch"] = branch
    if path:
        payload["path"] = path
    return await make_api_request("POST", "/api/2.0/repos", data=payload)


async def update_repo(repo_id: int, branch: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
    """Update repo branch or pull latest."""
    payload: Dict[str, Any] = {}
    if branch:
        payload["branch"] = branch
    if tag:
        payload["tag"] = tag
    return await make_api_request("PATCH", f"/api/2.0/repos/{repo_id}", data=payload)


async def list_repos(path_prefix: Optional[str] = None) -> Dict[str, Any]:
    """List repos, optionally filtered by path prefix."""
    params = {"path_prefix": path_prefix} if path_prefix else None
    return await make_api_request("GET", "/api/2.0/repos", params=params)


async def pull_repo(repo_id: int) -> Dict[str, Any]:
    """Pull the latest code for a repository.

    Args:
        repo_id: ID of the repository to pull

    Returns:
        Response from the Databricks API

    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Pulling repo {repo_id}")
    endpoint = f"/api/2.0/repos/{repo_id}/pull"
    return await make_api_request("POST", endpoint)
