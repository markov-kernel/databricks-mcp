import json
import pytest
from unittest.mock import AsyncMock, patch

from databricks_mcp.api import jobs, repos
from databricks_mcp.server.databricks_mcp_server import DatabricksMCPServer


@pytest.mark.asyncio
async def test_create_job():
    jobs.create_job = AsyncMock(return_value={"job_id": 123})
    payload = {"name": "Test", "tasks": []}

    resp = await jobs.create_job(payload)

    assert resp["job_id"] == 123
    jobs.create_job.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_delete_job():
    jobs.delete_job = AsyncMock(return_value={})

    resp = await jobs.delete_job(123)

    assert resp == {}
    jobs.delete_job.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_list_runs():
    jobs.list_runs = AsyncMock(return_value={"runs": []})

    resp = await jobs.list_runs(123)

    assert resp["runs"] == []
    jobs.list_runs.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_get_run_status():
    jobs.get_run_status = AsyncMock(return_value={"state": "SUCCESS"})

    resp = await jobs.get_run_status(1)

    assert resp["state"] == "SUCCESS"
    jobs.get_run_status.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_cancel_run():
    jobs.cancel_run = AsyncMock(return_value={})

    resp = await jobs.cancel_run(5)

    assert resp == {}
    jobs.cancel_run.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_pull_repo():
    with patch("databricks_mcp.api.repos.make_api_request", new=AsyncMock(return_value={"ok": True})) as mock_req:
        result = await repos.pull_repo(42)
        assert result == {"ok": True}
        mock_req.assert_awaited_once_with("POST", "/api/2.0/repos/42/pull")


@pytest.mark.asyncio
async def test_run_notebook():
    with (
        patch("databricks_mcp.api.jobs.submit_run", new=AsyncMock(return_value={"run_id": 99})) as mock_submit,
        patch("databricks_mcp.api.jobs.await_until_state", new=AsyncMock(return_value={})),
        patch("databricks_mcp.api.jobs.get_run_output", new=AsyncMock(return_value={"result": "ok"})) as mock_out,
    ):
        output = await jobs.run_notebook("/Test")
        assert output["run_id"] == 99
        assert output["result"] == "ok"
        mock_submit.assert_awaited_once()
        mock_out.assert_awaited_once_with(99)


@pytest.mark.asyncio
async def test_sync_repo_and_run_notebook_tool():
    server = DatabricksMCPServer()
    with (
        patch("databricks_mcp.api.repos.pull_repo", new=AsyncMock(return_value={"pulled": True})) as mock_pull,
        patch("databricks_mcp.api.jobs.run_notebook", new=AsyncMock(return_value={"run_id": 5})) as mock_run,
    ):
        res = await server.call_tool("sync_repo_and_run_notebook", {"params": {"repo_id": 1, "notebook_path": "/nb"}})
        assert isinstance(res, list)
        data = json.loads(res[0].text)
        inner = json.loads(data["text"])
        assert inner["run_id"] == 5
        mock_pull.assert_awaited_once_with(1)
        mock_run.assert_awaited_once()
