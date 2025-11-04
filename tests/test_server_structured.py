import base64
import importlib.util

import pytest

if importlib.util.find_spec("mcp") is None:  # pragma: no cover - environment guard
    pytest.skip("mcp package not available", allow_module_level=True)

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer
import databricks_mcp.api.clusters as clusters_api
import databricks_mcp.api.notebooks as notebooks_api
from databricks_mcp.core.utils import DatabricksAPIError


@pytest.mark.asyncio
async def test_list_clusters_structured(monkeypatch):
    async def fake_list_clusters():
        return {"clusters": [{"cluster_id": "test", "state": "RUNNING"}]}

    monkeypatch.setattr(clusters_api, "list_clusters", fake_list_clusters)

    server = DatabricksMCPServer()
    result = await server.call_tool("list_clusters", {})

    assert result.isError is False
    data = result.structuredContent
    assert data == {"clusters": [{"cluster_id": "test", "state": "RUNNING"}]}
    assert "_request_id" in (result.meta or {})
    assert result.content and "Found 1 clusters" in result.content[0].text


@pytest.mark.asyncio
async def test_export_notebook_returns_resource_link(monkeypatch):
    payload = {
        "content": base64.b64encode(b"print('hello world')").decode("utf-8"),
        "format": "SOURCE",
    }

    async def fake_export_notebook(path: str, format: str = "SOURCE"):
        return payload

    monkeypatch.setattr(notebooks_api, "export_notebook", fake_export_notebook)

    server = DatabricksMCPServer()
    result = await server.call_tool("export_notebook", {"path": "/Users/demo", "format": "SOURCE"})

    assert result.isError is False
    assert any(block.get("type") == "resource_link" for block in result.content if isinstance(block, dict))
    data = result.structuredContent
    assert data["content"] == payload["content"]
    assert data.get("resource_uri", "").startswith("databricks://exports/")


@pytest.mark.asyncio
async def test_error_wrapped(monkeypatch):
    async def fake_list_clusters():
        raise DatabricksAPIError("Boom", status_code=500, response={"error": "boom"})

    monkeypatch.setattr(clusters_api, "list_clusters", fake_list_clusters)

    server = DatabricksMCPServer()
    result = await server.call_tool("list_clusters", {})

    assert result.isError is True
    data = result.structuredContent
    assert data["message"].startswith("list_clusters failed")
    assert data["status_code"] == 500
