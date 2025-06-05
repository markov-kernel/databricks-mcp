"""
FastAPI application for Databricks API.

This is a stub module that provides compatibility with existing tests.
The actual implementation uses the MCP protocol directly.
"""

from fastapi import FastAPI

from databricks_mcp.api import clusters, dbfs, jobs, notebooks, sql
from databricks_mcp.core.config import settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(
        title="Databricks API",
        description="API for interacting with Databricks services",
        version=settings.VERSION,
    )
    
    # Add routes
    @app.get("/api/2.0/clusters/list")
    async def list_clusters():
        """List all clusters."""
        result = await clusters.list_clusters()
        return result
    
    @app.get("/api/2.0/clusters/get/{cluster_id}")
    async def get_cluster(cluster_id: str):
        """Get cluster details."""
        result = await clusters.get_cluster(cluster_id)
        return result
    
    @app.post("/api/2.0/clusters/create")
    async def create_cluster(request_data: dict):
        """Create a new cluster."""
        result = await clusters.create_cluster(request_data)
        return result
    
    @app.post("/api/2.0/clusters/delete")
    async def terminate_cluster(request_data: dict):
        """Terminate a cluster."""
        result = await clusters.terminate_cluster(request_data.get("cluster_id"))
        return result
    
    @app.post("/api/2.0/clusters/start")
    async def start_cluster(request_data: dict):
        """Start a cluster."""
        result = await clusters.start_cluster(request_data.get("cluster_id"))
        return result
    
    @app.post("/api/2.0/clusters/resize")
    async def resize_cluster(request_data: dict):
        """Resize a cluster."""
        result = await clusters.resize_cluster(
            request_data.get("cluster_id"),
            request_data.get("num_workers")
        )
        return result
    
    @app.post("/api/2.0/clusters/restart")
    async def restart_cluster(request_data: dict):
        """Restart a cluster."""
        result = await clusters.restart_cluster(request_data.get("cluster_id"))
        return result
    
    return app 