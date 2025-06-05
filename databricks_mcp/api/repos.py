"""API for managing Databricks repos."""

import logging
from typing import Any, Dict

from databricks_mcp.core.utils import DatabricksAPIError, make_api_request

logger = logging.getLogger(__name__)


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
