"""
Tests for individual tools in the Databricks MCP server.

This module contains tests for each individual tool in the Databricks MCP server.
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
    """Test the list_clusters tool."""
    logger.info("Testing list_clusters tool")
    server = DatabricksMCPServer()
    
    result = await server.call_tool("list_clusters", {"params": {}})
    
    # Check if result is valid
    assert isinstance(result, List), "Result should be a List"
    assert len(result) > 0, "Result should not be empty"
    assert hasattr(result[0], 'text'), "Result item should have 'text' attribute"
    
    # Parse the JSON data
    text = result[0].text
    data = json.loads(text)
    
    assert 'text' in data, "Result should contain 'text' field"
    inner_data = json.loads(data['text'])
    
    assert 'clusters' in inner_data, "Result should contain 'clusters' field"
    logger.info(f"Found {len(inner_data['clusters'])} clusters")
    
    return True


async def test_list_notebooks():
    """Test the list_notebooks tool."""
    logger.info("Testing list_notebooks tool")
    server = DatabricksMCPServer()
    
    result = await server.call_tool("list_notebooks", {"params": {"path": "/"}})
    
    # Check if result is valid
    assert isinstance(result, List), "Result should be a List"
    assert len(result) > 0, "Result should not be empty"
    assert hasattr(result[0], 'text'), "Result item should have 'text' attribute"
    
    # Parse the JSON data
    text = result[0].text
    data = json.loads(text)
    
    assert 'text' in data, "Result should contain 'text' field"
    inner_data = json.loads(data['text'])
    
    assert 'objects' in inner_data, "Result should contain 'objects' field"
    logger.info(f"Found {len(inner_data['objects'])} objects")
    
    return True


async def test_list_jobs():
    """Test the list_jobs tool."""
    logger.info("Testing list_jobs tool")
    server = DatabricksMCPServer()
    
    result = await server.call_tool("list_jobs", {"params": {}})
    
    # Check if result is valid
    assert isinstance(result, List), "Result should be a List"
    assert len(result) > 0, "Result should not be empty"
    assert hasattr(result[0], 'text'), "Result item should have 'text' attribute"
    
    # Parse the JSON data
    text = result[0].text
    data = json.loads(text)
    
    assert 'text' in data, "Result should contain 'text' field"
    inner_data = json.loads(data['text'])
    
    assert 'jobs' in inner_data, "Result should contain 'jobs' field"
    logger.info(f"Found {len(inner_data['jobs'])} jobs")
    
    return True


async def test_list_files():
    """Test the list_files tool."""
    logger.info("Testing list_files tool")
    server = DatabricksMCPServer()
    
    result = await server.call_tool("list_files", {"params": {"dbfs_path": "/"}})
    
    # Check if result is valid
    assert isinstance(result, List), "Result should be a List"
    assert len(result) > 0, "Result should not be empty"
    assert hasattr(result[0], 'text'), "Result item should have 'text' attribute"
    
    # Parse the JSON data
    text = result[0].text
    data = json.loads(text)
    
    assert 'text' in data, "Result should contain 'text' field"
    inner_data = json.loads(data['text'])
    
    assert 'files' in inner_data, "Result should contain 'files' field"
    logger.info(f"Found {len(inner_data['files'])} files")
    
    return True


async def main():
    """Run all tool tests."""
    logger.info("Running tool tests for Databricks MCP server")
    
    try:
        # Run tests
        tests = [
            ("list_clusters", test_list_clusters),
            ("list_notebooks", test_list_notebooks),
            ("list_jobs", test_list_jobs),
            ("list_files", test_list_files),
        ]
        
        success = True
        for name, test_func in tests:
            try:
                logger.info(f"Running test for {name}")
                result = await test_func()
                if result:
                    logger.info(f"Test for {name} passed")
                else:
                    logger.error(f"Test for {name} failed")
                    success = False
            except Exception as e:
                logger.error(f"Error in test for {name}: {e}", exc_info=True)
                success = False
        
        if success:
            logger.info("All tool tests passed!")
            return 0
        else:
            logger.error("Some tool tests failed")
            return 1
    except Exception as e:
        logger.error(f"Error in tests: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 