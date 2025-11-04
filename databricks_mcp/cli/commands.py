"""
Command-line interface for the Databricks MCP server.

This module provides command-line functionality for interacting with the Databricks MCP server.
"""

import argparse
import asyncio
import json
import logging
from typing import List, Optional

from databricks_mcp.core.logging_utils import configure_logging
from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer, main as server_main

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

    # Sync repo and run notebook command
    sync_parser = subparsers.add_parser(
        "sync-run",
        help="Pull a repo and run a notebook",
    )
    sync_parser.add_argument("--repo-id", type=int, required=True, help="Repo ID")
    sync_parser.add_argument("--notebook-path", required=True, help="Notebook path")
    sync_parser.add_argument("--cluster-id", help="Existing cluster ID")

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


async def sync_run(repo_id: int, notebook_path: str, cluster_id: Optional[str]) -> None:
    """Convenience wrapper for the sync_repo_and_run_notebook tool."""
    server = DatabricksMCPServer()
    params = {
        "repo_id": repo_id,
        "notebook_path": notebook_path,
    }
    if cluster_id:
        params["existing_cluster_id"] = cluster_id
    result = await server.call_tool("sync_repo_and_run_notebook", params)
    if result.isError:
        print(f"\nError: {result.content[0].text if result.content else 'Unknown failure'}")
        if result.meta and result.meta.get("data"):
            print(json.dumps(result.meta["data"], indent=2))
        return

    if result.content:
        summary = next((block.text for block in result.content if hasattr(block, "text")), None)
        if summary:
            print(f"\n{summary}")

    if result.meta and result.meta.get("data"):
        print(json.dumps(result.meta["data"], indent=2))


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    configure_logging()
    parsed_args = parse_args(args)
    
    # Set log level
    if hasattr(parsed_args, "debug") and parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Execute the appropriate command
    if parsed_args.command == "start":
        logger.info("Starting Databricks MCP server")
        server_main()
    elif parsed_args.command == "list-tools":
        asyncio.run(list_tools())
    elif parsed_args.command == "version":
        show_version()
    elif parsed_args.command == "sync-run":
        asyncio.run(sync_run(parsed_args.repo_id, parsed_args.notebook_path, parsed_args.cluster_id))
    else:
        # If no command is provided, show help
        parse_args(["--help"])
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
