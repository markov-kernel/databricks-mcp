import pytest
from unittest.mock import AsyncMock

from databricks_mcp.api import jobs


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
