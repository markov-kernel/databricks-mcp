"""
Databricks MCP Server

This module implements a standalone MCP server that provides tools for interacting
with Databricks APIs. It follows the Model Context Protocol standard, communicating
via stdio and directly connecting to Databricks when tools are invoked.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional, Union, cast

from mcp.server import FastMCP
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

from databricks_mcp.api import clusters, dbfs, jobs, notebooks, sql, libraries, repos, unity_catalog
from databricks_mcp.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    filename="databricks_mcp.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _unwrap_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unwrap parameters from MCP client structure.
    
    MCP clients may pass parameters in nested structure like:
    {"params": {"actual_parameter": "value"}}
    
    This function handles both nested and flat parameter structures.
    
    Args:
        params: Parameters from MCP client
        
    Returns:
        Unwrapped parameters dictionary
    """
    if 'params' in params and isinstance(params['params'], dict):
        return params['params']
    return params


class DatabricksMCPServer(FastMCP):
    """An MCP server for Databricks APIs."""

    def __init__(self):
        """Initialize the Databricks MCP server."""
        super().__init__(name="databricks-mcp", 
                         version="0.3.1", 
                         instructions="Use this server to manage Databricks resources")
        logger.info("Initializing Databricks MCP server")
        logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Databricks MCP tools."""
        
        # Cluster management tools
        @self.tool(
            name="list_clusters",
            description="List all Databricks clusters",
        )
        async def list_clusters(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing clusters with params: {params}")
            try:
                result = await clusters.list_clusters()
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing clusters: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster with parameters: cluster_name (required), spark_version (required), node_type_id (required), num_workers, autotermination_minutes",
        )
        async def create_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Creating cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await clusters.create_cluster(actual_params)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="terminate_cluster",
            description="Terminate a Databricks cluster with parameter: cluster_id (required)",
        )
        async def terminate_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Terminating cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await clusters.terminate_cluster(actual_params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error terminating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="get_cluster",
            description="Get information about a specific Databricks cluster with parameter: cluster_id (required)",
        )
        async def get_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting cluster info with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await clusters.get_cluster(actual_params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting cluster info: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="start_cluster",
            description="Start a terminated Databricks cluster with parameter: cluster_id (required)",
        )
        async def start_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Starting cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await clusters.start_cluster(actual_params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error starting cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        # Job management tools
        @self.tool(
            name="list_jobs",
            description="List all Databricks jobs",
        )
        async def list_jobs(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing jobs with params: {params}")
            try:
                result = await jobs.list_jobs()
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing jobs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="create_job",
            description="Create a Databricks job. Provide name and tasks list.",
        )
        async def create_job_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Creating job with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.create_job(actual_params)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating job: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="delete_job",
            description="Delete a Databricks job with parameter: job_id",
        )
        async def delete_job_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Deleting job with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.delete_job(actual_params.get("job_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error deleting job: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="run_job",
            description="Run a Databricks job with parameters: job_id (required), notebook_params (optional)",
        )
        async def run_job(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Running job with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                notebook_params = actual_params.get("notebook_params", {})
                result = await jobs.run_job(actual_params.get("job_id"), notebook_params)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error running job: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="run_notebook",
            description="Submit a one-time notebook run with parameters: notebook_path (required), existing_cluster_id (optional), base_parameters (optional)",
        )
        async def run_notebook_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Running notebook with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.run_notebook(
                    notebook_path=actual_params.get("notebook_path"),
                    existing_cluster_id=actual_params.get("existing_cluster_id"),
                    base_parameters=actual_params.get("base_parameters"),
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error running notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="sync_repo_and_run_notebook",
            description="Pull a repo then run a notebook. Parameters: repo_id, notebook_path, existing_cluster_id (optional), base_parameters (optional)",
        )
        async def sync_repo_and_run_notebook(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Syncing repo and running notebook with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                await repos.pull_repo(actual_params.get("repo_id"))
                result = await jobs.run_notebook(
                    notebook_path=actual_params.get("notebook_path"),
                    existing_cluster_id=actual_params.get("existing_cluster_id"),
                    base_parameters=actual_params.get("base_parameters"),
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error syncing repo and running notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="get_run_status",
            description="Get status for a job run with parameter: run_id",
        )
        async def get_run_status(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting run status with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.get_run_status(actual_params.get("run_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting run status: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="list_job_runs",
            description="List recent runs for a job with parameter: job_id",
        )
        async def list_job_runs(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing job runs with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.list_runs(actual_params.get("job_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing job runs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="cancel_run",
            description="Cancel a job run with parameter: run_id",
        )
        async def cancel_run_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Cancelling run with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await jobs.cancel_run(actual_params.get("run_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error cancelling run: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        # Notebook management tools
        @self.tool(
            name="list_notebooks",
            description="List notebooks in a workspace directory with parameter: path (required)",
        )
        async def list_notebooks(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing notebooks with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await notebooks.list_notebooks(actual_params.get("path"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing notebooks: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="export_notebook",
            description="Export a notebook from the workspace with parameters: path (required), format (optional, one of: SOURCE, HTML, JUPYTER, DBC)",
        )
        async def export_notebook(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Exporting notebook with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                format_type = actual_params.get("format", "SOURCE")
                result = await notebooks.export_notebook(actual_params.get("path"), format_type)
                
                # For notebooks, we might want to trim the response for readability
                content = result.get("content", "")
                if len(content) > 1000:
                    summary = f"{content[:1000]}... [content truncated, total length: {len(content)} characters]"
                    result["content"] = summary
                
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error exporting notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="import_notebook",
            description="Import a notebook; parameters: path, content (base64 or text), format (optional)",
        )
        async def import_notebook_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Importing notebook with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                path = actual_params.get("path")
                content = actual_params.get("content")
                fmt = actual_params.get("format", "SOURCE")
                result = await notebooks.import_notebook(path, content, fmt)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error importing notebook: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="delete_workspace_object",
            description="Delete a notebook or directory with parameters: path, recursive (optional)",
        )
        async def delete_workspace_object(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Deleting workspace object with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await notebooks.delete_notebook(
                    actual_params.get("path"), actual_params.get("recursive", False)
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error deleting workspace object: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        # DBFS tools
        @self.tool(
            name="list_files",
            description="List files and directories in a DBFS path with parameter: dbfs_path (required)",
        )
        async def list_files(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing files with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await dbfs.list_files(actual_params.get("dbfs_path"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing files: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="dbfs_put",
            description="Upload a small file to DBFS with parameters: dbfs_path, content_base64",
        )
        async def dbfs_put(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Uploading file to DBFS with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                path = actual_params.get("dbfs_path")
                content = actual_params.get("content_base64", "").encode()
                import base64
                data = base64.b64decode(content)
                result = await dbfs.put_file(path, data)
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="dbfs_delete",
            description="Delete a file or directory in DBFS with parameters: dbfs_path, recursive (optional)",
        )
        async def dbfs_delete(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Deleting DBFS path with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await dbfs.delete_file(actual_params.get("dbfs_path"), actual_params.get("recursive", False))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error deleting file: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="pull_repo",
            description="Pull the latest commit for a repo with parameter: repo_id (required)",
        )
        async def pull_repo_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Pulling repo with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await repos.pull_repo(actual_params.get("repo_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error pulling repo: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        # SQL tools
        @self.tool(
            name="execute_sql",
            description="Execute a SQL statement with parameters: statement (required), warehouse_id (optional - uses DATABRICKS_WAREHOUSE_ID env var if not provided), catalog (optional), schema (optional)",
        )
        async def execute_sql(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Executing SQL with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                    
                statement = actual_params.get("statement")
                warehouse_id = actual_params.get("warehouse_id")
                catalog = actual_params.get("catalog")
                schema = actual_params.get("schema")
                
                result = await sql.execute_statement(
                    statement=statement,
                    warehouse_id=warehouse_id,
                    catalog=catalog,
                    schema=schema
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error executing SQL: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Cluster library tools
        @self.tool(
            name="install_library",
            description="Install a library on a cluster with parameters: cluster_id, libraries",
        )
        async def install_library_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Installing library with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await libraries.install_library(actual_params.get("cluster_id"), actual_params.get("libraries", []))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error installing library: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="uninstall_library",
            description="Uninstall a library from a cluster with parameters: cluster_id, libraries",
        )
        async def uninstall_library_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Uninstalling library with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await libraries.uninstall_library(actual_params.get("cluster_id"), actual_params.get("libraries", []))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error uninstalling library: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="list_cluster_libraries",
            description="List library status for a cluster with parameter: cluster_id",
        )
        async def list_cluster_libraries_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing cluster libraries with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await libraries.list_cluster_libraries(actual_params.get("cluster_id"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing cluster libraries: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Repos tools
        @self.tool(
            name="create_repo",
            description="Create or clone a repo with parameters: url, provider, branch (optional)",
        )
        async def create_repo_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Creating repo with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await repos.create_repo(
                    actual_params.get("url"),
                    actual_params.get("provider"),
                    branch=actual_params.get("branch"),
                    path=actual_params.get("path"),
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating repo: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="update_repo",
            description="Update repo branch with parameters: repo_id, branch or tag",
        )
        async def update_repo_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Updating repo with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await repos.update_repo(
                    actual_params.get("repo_id"),
                    branch=actual_params.get("branch"),
                    tag=actual_params.get("tag"),
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error updating repo: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(
            name="list_repos",
            description="List repos with optional path_prefix",
        )
        async def list_repos_tool(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Listing repos with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await repos.list_repos(actual_params.get("path_prefix"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing repos: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        # Workspace file tools
        @self.tool(
            name="get_workspace_file_content",
            description="Retrieve the content of a file from Databricks workspace with parameters: workspace_path (required), format (optional: SOURCE, HTML, JUPYTER, DBC - default SOURCE)",
        )
        async def get_workspace_file_content(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting workspace file content with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                    
                workspace_path = actual_params.get("workspace_path")
                format_type = actual_params.get("format", "SOURCE")
                
                if not workspace_path:
                    raise ValueError("workspace_path is required")
                
                # Use the workspace export API
                result = await notebooks.export_workspace_file(workspace_path, format_type)
                return [{"text": json.dumps(result)}]
                
            except Exception as e:
                logger.error(f"Error getting workspace file content: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]
        
        @self.tool(
            name="get_workspace_file_info",
            description="Get metadata about a workspace file with parameters: workspace_path (required)",
        )
        async def get_workspace_file_info(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting workspace file info with params: {params}")
            try:
                actual_params = _unwrap_params(params)

                workspace_path = actual_params.get("workspace_path")

                if not workspace_path:
                    raise ValueError("workspace_path is required")

                result = await notebooks.get_workspace_file_info(workspace_path)
                return [{"text": json.dumps(result)}]

            except Exception as e:
                logger.error(f"Error getting workspace file info: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        # Unity Catalog tools
        @self.tool(name="list_catalogs", description="List catalogs in Unity Catalog")
        async def list_catalogs_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                result = await unity_catalog.list_catalogs()
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing catalogs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="create_catalog", description="Create a catalog with parameters: name, comment")
        async def create_catalog_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.create_catalog(actual_params.get("name"), actual_params.get("comment"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating catalog: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="list_schemas", description="List schemas for a catalog with parameter: catalog_name")
        async def list_schemas_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.list_schemas(actual_params.get("catalog_name"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing schemas: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="create_schema", description="Create schema with parameters: catalog_name, name, comment")
        async def create_schema_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.create_schema(
                    actual_params.get("catalog_name"), actual_params.get("name"), actual_params.get("comment")
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating schema: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="list_tables", description="List tables with parameters: catalog_name, schema_name")
        async def list_tables_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.list_tables(
                    actual_params.get("catalog_name"), actual_params.get("schema_name")
                )
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error listing tables: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="create_table", description="Create table via SQL with parameters: warehouse_id, statement")
        async def create_table_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.create_table(actual_params.get("warehouse_id"), actual_params.get("statement"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error creating table: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]

        @self.tool(name="get_table_lineage", description="Get table lineage with parameter: full_name")
        async def get_table_lineage_tool(params: Dict[str, Any]) -> List[TextContent]:
            try:
                actual_params = _unwrap_params(params)
                result = await unity_catalog.get_table_lineage(actual_params.get("full_name"))
                return [{"text": json.dumps(result)}]
            except Exception as e:
                logger.error(f"Error getting lineage: {str(e)}")
                return [{"text": json.dumps({"error": str(e)})}]


def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Databricks MCP server")
        
        # Turn off buffering in stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(line_buffering=True)
        
        server = DatabricksMCPServer()
        
        # Use the FastMCP run method which handles async internally
        server.run()
            
    except Exception as e:
        logger.error(f"Error in Databricks MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main() 