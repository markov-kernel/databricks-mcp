"""
Simple script to show notebooks from Databricks
"""

import asyncio
import json
import sys
from databricks_mcp.api import notebooks

async def show_all_notebooks():
    """Show all notebooks in the Databricks workspace."""
    print("Fetching notebooks from Databricks...")
    try:
        result = await notebooks.list_notebooks(path="/")
        print("\nNotebooks found:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error listing notebooks: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(show_all_notebooks()) 