#!/usr/bin/env python
"""
Databricks MCP Server - Direct Usage Example

This example demonstrates how to directly use the Databricks MCP server
without going through the MCP protocol. It shows how to instantiate the
server class and call its methods directly.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def print_section_header(title: str) -> None:
    """Print a section header with the given title."""
    print(f"\n{title}")
    print("=" * len(title))

def print_clusters(clusters: List[Dict[str, Any]]) -> None:
    """Print information about Databricks clusters."""
    print_section_header("Databricks Clusters")
    
    for i, cluster in enumerate(clusters, 1):
        print(f"\nCluster {i}:")
        print(f"  ID: {cluster.get('cluster_id')}")
        print(f"  Name: {cluster.get('cluster_name')}")
        print(f"  State: {cluster.get('state')}")
        print(f"  Spark Version: {cluster.get('spark_version')}")
        print(f"  Node Type: {cluster.get('node_type_id')}")

def print_notebooks(notebooks: List[Dict[str, Any]], path: str) -> None:
    """Print information about Databricks notebooks."""
    print_section_header(f"Databricks Notebooks in {path}")
    
    for notebook in notebooks:
        if notebook.get('object_type') == 'NOTEBOOK':
            print(f"\nNotebook: {notebook.get('path')}")
        elif notebook.get('object_type') == 'DIRECTORY':
            print(f"Directory: {notebook.get('path')}")

def print_jobs(jobs: List[Dict[str, Any]]) -> None:
    """Print information about Databricks jobs."""
    print_section_header("Databricks Jobs")
    
    for i, job in enumerate(jobs, 1):
        print(f"\nJob {i}:")
        print(f"  ID: {job.get('job_id')}")
        print(f"  Name: {job.get('settings', {}).get('name')}")
        print(f"  Created: {job.get('created_time')}")

def main() -> None:
    """Main function for the direct usage example."""
    print("\nDatabricks MCP Server - Direct Usage Example")
    print("===========================================")
    
    # Check for Databricks credentials
    if not os.environ.get("DATABRICKS_HOST") or not os.environ.get("DATABRICKS_TOKEN"):
        logger.error("Please set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables")
        sys.exit(1)
    
    # Create the Databricks MCP server
    server = DatabricksMCPServer()
    
    try:
        # List clusters
        logger.info("Listing Databricks clusters...")
        clusters_result = server.list_clusters()
        clusters_data = json.loads(clusters_result)
        if 'error' in clusters_data:
            logger.error(f"Error listing clusters: {clusters_data['error']}")
        else:
            print_clusters(clusters_data.get('clusters', []))
        
        # List notebooks in root path
        logger.info("Listing Databricks notebooks...")
        notebooks_result = server.list_notebooks({"path": "/"})
        notebooks_data = json.loads(notebooks_result)
        if 'error' in notebooks_data:
            logger.error(f"Error listing notebooks: {notebooks_data['error']}")
        else:
            print_notebooks(notebooks_data.get('objects', []), "/")
        
        # List jobs
        logger.info("Listing Databricks jobs...")
        jobs_result = server.list_jobs()
        jobs_data = json.loads(jobs_result)
        if 'error' in jobs_data:
            logger.error(f"Error listing jobs: {jobs_data['error']}")
        else:
            print_jobs(jobs_data.get('jobs', []))
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 