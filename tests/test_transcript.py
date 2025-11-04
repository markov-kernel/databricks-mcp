import importlib.util
import json

import pytest

if importlib.util.find_spec("mcp") is None:  # pragma: no cover
    pytest.skip("mcp package not available", allow_module_level=True)

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer
import databricks_mcp.api.clusters as clusters_api


@pytest.mark.asyncio
async def test_list_clusters_transcript(monkeypatch):
    async def fake_list_clusters():
        return {"clusters": [{"cluster_id": "transcript", "state": "RUNNING"}]}

    monkeypatch.setattr(clusters_api, "list_clusters", fake_list_clusters)

    server = DatabricksMCPServer()
    result = await server.call_tool("list_clusters", {})

    transcript = {
        "request": {"name": "list_clusters", "arguments": {}},
        "response": {
            "isError": result.isError,
            "structuredContent": result.structuredContent,
        },
    }

    expected = {
        "request": {"name": "list_clusters", "arguments": {}},
        "response": {
            "isError": False,
            "structuredContent": {"clusters": [{"cluster_id": "transcript", "state": "RUNNING"}]},
        },
    }

    assert transcript == expected
    # Ensure transcript is JSON-serializable for golden comparisons.
    json.dumps(transcript)
