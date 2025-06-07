"""
Test parameter unwrapping functionality.

This module tests that the parameter unwrapping helper function correctly handles
both nested and flat parameter structures from MCP clients.
"""

import pytest
from databricks_mcp.server.databricks_mcp_server import _unwrap_params


def test_unwrap_nested_params():
    """Test unwrapping nested parameter structure."""
    # Nested structure like what MCP clients send
    nested_params = {
        "params": {
            "cluster_id": "test-cluster-123",
            "path": "/test/path",
            "optional_param": "value"
        }
    }
    
    result = _unwrap_params(nested_params)
    
    assert result == {
        "cluster_id": "test-cluster-123",
        "path": "/test/path", 
        "optional_param": "value"
    }


def test_unwrap_flat_params():
    """Test that flat parameters are passed through unchanged."""
    # Flat structure for backward compatibility
    flat_params = {
        "cluster_id": "test-cluster-123",
        "path": "/test/path",
        "optional_param": "value"
    }
    
    result = _unwrap_params(flat_params)
    
    assert result == flat_params


def test_unwrap_empty_params():
    """Test unwrapping empty parameter structures."""
    # Empty nested structure
    empty_nested = {"params": {}}
    result = _unwrap_params(empty_nested)
    assert result == {}
    
    # Empty flat structure  
    empty_flat = {}
    result = _unwrap_params(empty_flat)
    assert result == {}


def test_unwrap_params_with_non_dict_params():
    """Test that non-dict params value is handled gracefully."""
    # params key exists but value is not a dict
    invalid_params = {"params": "not-a-dict", "other_key": "value"}
    
    result = _unwrap_params(invalid_params)
    
    # Should return the original dict since params is not a dict
    assert result == invalid_params


def test_unwrap_params_missing_params_key():
    """Test that missing params key returns original dict."""
    # No params key present
    no_params = {"cluster_id": "test-123", "other_key": "value"}
    
    result = _unwrap_params(no_params)
    
    assert result == no_params


def test_unwrap_complex_nested_params():
    """Test unwrapping complex nested parameter structures."""
    complex_params = {
        "params": {
            "cluster_id": "test-cluster-123",
            "libraries": [
                {"pypi": {"package": "requests"}},
                {"maven": {"coordinates": "com.example:library:1.0"}}
            ],
            "notebook_params": {
                "input_path": "/data/input",
                "output_path": "/data/output"
            }
        }
    }
    
    result = _unwrap_params(complex_params)
    
    expected = {
        "cluster_id": "test-cluster-123",
        "libraries": [
            {"pypi": {"package": "requests"}},
            {"maven": {"coordinates": "com.example:library:1.0"}}
        ],
        "notebook_params": {
            "input_path": "/data/input",
            "output_path": "/data/output"
        }
    }
    
    assert result == expected 