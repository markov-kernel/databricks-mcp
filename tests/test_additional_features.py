import pytest
from unittest.mock import AsyncMock

from databricks_mcp.api import libraries, repos, unity_catalog


@pytest.mark.asyncio
async def test_install_library():
    libraries.install_library = AsyncMock(return_value={})
    resp = await libraries.install_library("cluster", [])
    assert resp == {}
    libraries.install_library.assert_called_once()


@pytest.mark.asyncio
async def test_create_repo():
    repos.create_repo = AsyncMock(return_value={"id": 1})
    resp = await repos.create_repo("https://example.com", "git")
    assert resp["id"] == 1
    repos.create_repo.assert_called_once()


@pytest.mark.asyncio
async def test_list_catalogs():
    unity_catalog.list_catalogs = AsyncMock(return_value={"catalogs": []})
    resp = await unity_catalog.list_catalogs()
    assert resp["catalogs"] == []
    unity_catalog.list_catalogs.assert_called_once()

