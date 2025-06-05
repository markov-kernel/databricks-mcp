"""
Direct tests for the Databricks MCP server.

This module contains tests that directly instantiate and test the server without using MCP protocol.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_list_clusters():
    """Test the list_clusters tool directly."""
    try:
        logger.info("Creating Databricks MCP server instance")
        server = DatabricksMCPServer()
        
        # Test the list_clusters tool
        tool_name = "list_clusters"
        logger.info(f"Testing tool: {tool_name}")
        
        # Call the tool with the required params parameter
        params: Dict[str, Any] = {"params": {}}
        result = await server.call_tool(tool_name, params)
        
        # Extract text content from the result
        if isinstance(result, List) and len(result) > 0:
            # Get the first item in the list
            item = result[0]
            
            # Check if the item has a 'text' attribute
            if hasattr(item, 'text'):
                text = item.text
                logger.info(f"Text content: {text[:100]}...")  # Show first 100 chars
                
                # Parse the JSON from the text
                try:
                    # First level of parsing (the text is a JSON string)
                    parsed_json = json.loads(text)
                    
                    # Check if the parsed JSON has a 'text' field (double JSON encoding)
                    if 'text' in parsed_json:
                        # Second level of parsing (the text field is also a JSON string)
                        inner_json = json.loads(parsed_json['text'])
                        logger.info(f"Parsed clusters data: {json.dumps(inner_json, indent=2)}")
                        
                        # Extract cluster information
                        if 'clusters' in inner_json:
                            clusters = inner_json['clusters']
                            logger.info(f"Found {len(clusters)} clusters")
                            
                            # Print information about each cluster
                            for i, cluster in enumerate(clusters):
                                logger.info(f"Cluster {i+1}:")
                                logger.info(f"  ID: {cluster.get('cluster_id')}")
                                logger.info(f"  Name: {cluster.get('cluster_name')}")
                                logger.info(f"  State: {cluster.get('state')}")
                            
                            return True
                    else:
                        logger.info(f"Parsed JSON: {json.dumps(parsed_json, indent=2)}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
        
        logger.error("Test failed: Could not parse cluster data")
        return False
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logger.info("Running direct tests for Databricks MCP server")
    
    # Run tests
    success = await test_list_clusters()
    
    if success:
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 