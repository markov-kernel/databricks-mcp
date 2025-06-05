"""
Command-line interface for the Databricks MCP server.

This module provides command-line functionality for interacting with the Databricks MCP server.
"""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer, main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Databricks MCP Server CLI")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Start server command
    start_parser = subparsers.add_parser("start", help="Start the MCP server")
    start_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    
    # List tools command
    list_parser = subparsers.add_parser("list-tools", help="List available tools")
    
    # Version command
    subparsers.add_parser("version", help="Show server version")
    
    return parser.parse_args(args)


async def list_tools() -> None:
    """List all available tools in the server."""
    server = DatabricksMCPServer()
    tools = await server.list_tools()
    
    print("\nAvailable tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")


def show_version() -> None:
    """Show the server version."""
    server = DatabricksMCPServer()
    print(f"\nDatabricks MCP Server v{server.version}")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)
    
    # Set log level
    if hasattr(parsed_args, "debug") and parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute the appropriate command
    if parsed_args.command == "start":
        logger.info("Starting Databricks MCP server")
        asyncio.run(server_main())
    elif parsed_args.command == "list-tools":
        asyncio.run(list_tools())
    elif parsed_args.command == "version":
        show_version()
    else:
        # If no command is provided, show help
        parse_args(["--help"])
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 