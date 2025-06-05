"""
Tests for the clusters API.
"""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from databricks_mcp.api import clusters
from databricks_mcp.server.app import create_app


@pytest.fixture
def client():
    """Create a test client for the API."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_cluster_response():
    """Mock response for cluster operations."""
    return {
        "cluster_id": "1234-567890-abcdef",
        "cluster_name": "Test Cluster",
        "spark_version": "10.4.x-scala2.12",
        "node_type_id": "Standard_D3_v2",
        "num_workers": 2,
        "state": "RUNNING",
        "creator_user_name": "test@example.com",
    }


@pytest.mark.asyncio
async def test_create_cluster():
    """Test creating a cluster."""
    # Mock the API call
    clusters.create_cluster = AsyncMock(return_value={"cluster_id": "1234-567890-abcdef"})
    
    # Create cluster config
    cluster_config = {
        "cluster_name": "Test Cluster",
        "spark_version": "10.4.x-scala2.12",
        "node_type_id": "Standard_D3_v2",
        "num_workers": 2,
    }
    
    # Call the function
    response = await clusters.create_cluster(cluster_config)
    
    # Check the response
    assert response["cluster_id"] == "1234-567890-abcdef"
    
    # Verify the mock was called with the correct arguments
    clusters.create_cluster.assert_called_once_with(cluster_config)


@pytest.mark.asyncio
async def test_list_clusters():
    """Test listing clusters."""
    # Mock the API call
    mock_response = {
        "clusters": [
            {
                "cluster_id": "1234-567890-abcdef",
                "cluster_name": "Test Cluster 1",
                "state": "RUNNING",
            },
            {
                "cluster_id": "9876-543210-fedcba",
                "cluster_name": "Test Cluster 2",
                "state": "TERMINATED",
            },
        ]
    }
    clusters.list_clusters = AsyncMock(return_value=mock_response)
    
    # Call the function
    response = await clusters.list_clusters()
    
    # Check the response
    assert len(response["clusters"]) == 2
    assert response["clusters"][0]["cluster_id"] == "1234-567890-abcdef"
    assert response["clusters"][1]["cluster_id"] == "9876-543210-fedcba"
    
    # Verify the mock was called
    clusters.list_clusters.assert_called_once()


@pytest.mark.asyncio
async def test_get_cluster():
    """Test getting cluster information."""
    # Mock the API call
    mock_response = {
        "cluster_id": "1234-567890-abcdef",
        "cluster_name": "Test Cluster",
        "state": "RUNNING",
    }
    clusters.get_cluster = AsyncMock(return_value=mock_response)
    
    # Call the function
    response = await clusters.get_cluster("1234-567890-abcdef")
    
    # Check the response
    assert response["cluster_id"] == "1234-567890-abcdef"
    assert response["state"] == "RUNNING"
    
    # Verify the mock was called with the correct arguments
    clusters.get_cluster.assert_called_once_with("1234-567890-abcdef")


@pytest.mark.asyncio
async def test_terminate_cluster():
    """Test terminating a cluster."""
    # Mock the API call
    clusters.terminate_cluster = AsyncMock(return_value={})
    
    # Call the function
    response = await clusters.terminate_cluster("1234-567890-abcdef")
    
    # Check the response
    assert response == {}
    
    # Verify the mock was called with the correct arguments
    clusters.terminate_cluster.assert_called_once_with("1234-567890-abcdef")


@pytest.mark.asyncio
async def test_start_cluster():
    """Test starting a cluster."""
    # Mock the API call
    clusters.start_cluster = AsyncMock(return_value={})
    
    # Call the function
    response = await clusters.start_cluster("1234-567890-abcdef")
    
    # Check the response
    assert response == {}
    
    # Verify the mock was called with the correct arguments
    clusters.start_cluster.assert_called_once_with("1234-567890-abcdef")


@pytest.mark.asyncio
async def test_resize_cluster():
    """Test resizing a cluster."""
    # Mock the API call
    clusters.resize_cluster = AsyncMock(return_value={})
    
    # Call the function
    response = await clusters.resize_cluster("1234-567890-abcdef", 4)
    
    # Check the response
    assert response == {}
    
    # Verify the mock was called with the correct arguments
    clusters.resize_cluster.assert_called_once_with("1234-567890-abcdef", 4)


@pytest.mark.asyncio
async def test_restart_cluster():
    """Test restarting a cluster."""
    # Mock the API call
    clusters.restart_cluster = AsyncMock(return_value={})
    
    # Call the function
    response = await clusters.restart_cluster("1234-567890-abcdef")
    
    # Check the response
    assert response == {}
    
    # Verify the mock was called with the correct arguments
    clusters.restart_cluster.assert_called_once_with("1234-567890-abcdef") 