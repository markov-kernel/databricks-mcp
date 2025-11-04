import importlib.util

import pytest

if importlib.util.find_spec("mcp") is None:  # pragma: no cover - environment guard
    pytest.skip("mcp package not available", allow_module_level=True)

from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer


@pytest.mark.asyncio
async def test_list_tools_has_schemas():
    server = DatabricksMCPServer()
    tools = await server.list_tools()
    assert any(tool.name == "list_clusters" for tool in tools)
    list_clusters_tool = next(tool for tool in tools if tool.name == "list_clusters")
    assert "properties" in list_clusters_tool.inputSchema
    if list_clusters_tool.outputSchema is not None:
        assert "type" in list_clusters_tool.outputSchema
