"""
Main entry point for running the databricks-mcp-server package.
This allows the package to be run with 'python -m databricks_mcp. or 'uv run databricks_mcp'.
"""

import asyncio
from databricks_mcp.main import main

if __name__ == "__main__":
    asyncio.run(main()) 
