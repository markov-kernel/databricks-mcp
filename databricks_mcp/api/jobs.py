"""
API for managing Databricks jobs.
"""

import logging
import asyncio
import time
from typing import Any, Dict, List, Optional, Union

from databricks_mcp.core.models import Job
from databricks_mcp.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def create_job(job_config: Union[Job, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a new Databricks job.
    
    Args:
        job_config: Job configuration
        
    Returns:
        Response containing the job ID
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Creating new job")

    if isinstance(job_config, Job):
        payload = job_config.model_dump(exclude_none=True)
    else:
        payload = job_config

    return await make_api_request("POST", "/api/2.2/jobs/create", data=payload)


async def run_job(job_id: int, notebook_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run a job now.
    
    Args:
        job_id: ID of the job to run
        notebook_params: Optional parameters for the notebook
        
    Returns:
        Response containing the run ID
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Running job: {job_id}")
    
    run_params = {"job_id": job_id}
    if notebook_params:
        run_params["notebook_params"] = notebook_params
        
    return await make_api_request("POST", "/api/2.0/jobs/run-now", data=run_params)


async def list_jobs() -> Dict[str, Any]:
    """
    List all jobs.
    
    Returns:
        Response containing a list of jobs
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info("Listing all jobs")
    return await make_api_request("GET", "/api/2.0/jobs/list")


async def get_job(job_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Response containing job information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for job: {job_id}")
    return await make_api_request("GET", "/api/2.0/jobs/get", params={"job_id": job_id})


async def update_job(job_id: int, new_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing job.
    
    Args:
        job_id: ID of the job to update
        new_settings: New job settings
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Updating job: {job_id}")
    
    update_data = {
        "job_id": job_id,
        "new_settings": new_settings
    }
    
    return await make_api_request("POST", "/api/2.0/jobs/update", data=update_data)


async def delete_job(job_id: int) -> Dict[str, Any]:
    """
    Delete a job.
    
    Args:
        job_id: ID of the job to delete
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting job: {job_id}")
    return await make_api_request("POST", "/api/2.2/jobs/delete", data={"job_id": job_id})


async def get_run(run_id: int) -> Dict[str, Any]:
    """
    Get information about a specific job run.
    
    Args:
        run_id: ID of the run
        
    Returns:
        Response containing run information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting information for run: {run_id}")
    return await make_api_request("GET", "/api/2.1/jobs/runs/get", params={"run_id": run_id})


async def list_runs(job_id: Optional[int] = None, limit: int = 20) -> Dict[str, Any]:
    """List job runs."""
    logger.info("Listing job runs")
    params: Dict[str, Any] = {"limit": limit}
    if job_id is not None:
        params["job_id"] = job_id
    return await make_api_request("GET", "/api/2.1/jobs/runs/list", params=params)


async def get_run_status(run_id: int) -> Dict[str, Any]:
    """Get concise status information for a run."""
    info = await get_run(run_id)
    state = info.get("state", {})
    return {
        "state": state.get("result_state") or state.get("life_cycle_state"),
        "life_cycle": state.get("life_cycle_state"),
        "run_id": run_id,
    }


async def cancel_run(run_id: int) -> Dict[str, Any]:
    """
    Cancel a job run.
    
    Args:
        run_id: ID of the run to cancel
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Cancelling run: {run_id}")
    return await make_api_request("POST", "/api/2.1/jobs/runs/cancel", data={"run_id": run_id})


async def await_until_state(run_id: int, target_state: str = "TERMINATED", poll_interval: int = 5, timeout: int = 600) -> Dict[str, Any]:
    """Poll a run until it reaches the desired lifecycle state."""
    start = time.monotonic()
    while True:
        info = await get_run(run_id)
        state = info.get("state", {}).get("life_cycle_state")
        if state == target_state:
            return info
        if time.monotonic() - start > timeout:
            raise TimeoutError(f"Run {run_id} did not reach {target_state} in {timeout}s")
        await asyncio.sleep(poll_interval)
