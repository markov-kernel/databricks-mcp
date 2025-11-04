"""
Main entry point for the Databricks MCP server.
"""

import argparse
import asyncio
import logging
from typing import Optional

from databricks_mcp.core.config import settings
from databricks_mcp.core.logging_utils import configure_logging
from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer


async def start_mcp_server() -> None:
    """Start the MCP server via the FastMCP stdio helper."""
    server = DatabricksMCPServer()
    await server.run_stdio_async()


def setup_logging(log_level: Optional[str] = None) -> None:
    """Set up centralized logging before any server work begins."""
    level = (log_level or settings.LOG_LEVEL).upper()
    configure_logging(level=level, log_file="databricks_mcp.log")


async def main(log_level: Optional[str] = None) -> None:
    """Main asynchronous entry point."""
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Databricks MCP server v%s", settings.VERSION)
    logger.info("Databricks host resolved")
    await start_mcp_server()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Databricks MCP Server")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override default log level",
    )
    args = parser.parse_args()
    asyncio.run(main(args.log_level))
