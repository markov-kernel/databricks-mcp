"""
Main entry point for the Databricks MCP server.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

from databricks_mcp.core.config import settings
from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer

# Function to start the server - extracted from the server file
async def start_mcp_server():
    """Start the MCP server."""
    server = DatabricksMCPServer()
    await server.run_stdio_async()


def setup_logging(log_level: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Optional log level to override the default
    """
    level = getattr(logging, log_level or settings.LOG_LEVEL)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def main():
    """Main entry point."""
    # Set up logging
    setup_logging()
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Databricks MCP server v{settings.VERSION}")
    logger.info(f"Databricks host: {settings.DATABRICKS_HOST}")
    
    # Start the MCP server
    await start_mcp_server()


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Databricks MCP Server")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the log level",
    )
    
    args = parser.parse_args()
    
    # Set up logging with command line arguments
    setup_logging(args.log_level)
    
    # Run the main function
    asyncio.run(main()) 