"""API for managing cluster libraries."""

import logging
from typing import Any, Dict, List

from databricks_mcp.core.utils import make_api_request, DatabricksAPIError

logger = logging.getLogger(__name__)


async def install_library(cluster_id: str, libraries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Install libraries on a cluster."""
    logger.info(f"Installing libraries on cluster {cluster_id}")
    payload = {"cluster_id": cluster_id, "libraries": libraries}
    return await make_api_request("POST", "/api/2.0/libraries/install", data=payload)


async def uninstall_library(cluster_id: str, libraries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Uninstall libraries from a cluster."""
    logger.info(f"Uninstalling libraries on cluster {cluster_id}")
    payload = {"cluster_id": cluster_id, "libraries": libraries}
    return await make_api_request("POST", "/api/2.0/libraries/uninstall", data=payload)


async def list_cluster_libraries(cluster_id: str) -> Dict[str, Any]:
    """List library status for a cluster."""
    logger.info(f"Listing libraries for cluster {cluster_id}")
    return await make_api_request("GET", "/api/2.0/libraries/cluster-status", params={"cluster_id": cluster_id})
