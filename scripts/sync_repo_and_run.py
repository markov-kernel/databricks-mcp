"""Utility script to pull a repo and run a notebook."""

import argparse
import asyncio
import json

from databricks_mcp.cli.commands import sync_run


async def main() -> None:
    parser = argparse.ArgumentParser(description="Sync repo and run notebook")
    parser.add_argument("--repo-id", type=int, required=True)
    parser.add_argument("--notebook-path", required=True)
    parser.add_argument("--cluster-id")
    args = parser.parse_args()

    await sync_run(args.repo_id, args.notebook_path, args.cluster_id)


if __name__ == "__main__":
    asyncio.run(main())
