"""
Simple script to show clusters from Databricks
"""

import asyncio
import json
import sys
from databricks_mcp.api import clusters

async def show_all_clusters():
    """Show all clusters in the Databricks workspace."""
    print("Fetching clusters from Databricks...")
    try:
        result = await clusters.list_clusters()
        print("\nClusters found:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error listing clusters: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(show_all_clusters()) 