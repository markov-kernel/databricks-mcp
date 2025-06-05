"""
Main entry point for running the server module directly.
This allows the module to be run with 'python -m databricks_mcp.server' or 'uv run databricks_mcp.server'.
"""

import asyncio
from databricks_mcp.server.databricks_mcp_server import main

if __name__ == "__main__":
    asyncio.run(main()) 
