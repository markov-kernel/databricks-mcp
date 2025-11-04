"""
Databricks MCP Server implementation.

Provides MCP tools that wrap Databricks REST APIs with structured results,
resource links for large payloads, and standardized error handling.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import sys
import uuid
from collections import Counter
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

from mcp.server import FastMCP
from mcp.server.fastmcp.server import Context
from mcp.types import CallToolResult, TextContent

from databricks_mcp.api import clusters, dbfs, jobs, libraries, notebooks, repos, sql, unity_catalog
from databricks_mcp.core.config import settings
from databricks_mcp.core.logging_utils import configure_logging
from databricks_mcp.core.models import ClusterConfig, Job
from databricks_mcp.core.utils import DatabricksAPIError, request_context_id
from databricks_mcp.server.tool_helpers import error_result, success_result

logger = logging.getLogger(__name__)


@dataclass
class ResourcePayload:
    data: bytes
    mime_type: Optional[str]
    description: Optional[str]
    is_text: bool = False


class DatabricksMCPServer(FastMCP):
    """An MCP server for Databricks APIs with structured outputs."""

    def __init__(self) -> None:
        super().__init__(
            name="databricks-mcp",
            instructions="Use this server to manage Databricks resources",
        )
        self.version = settings.VERSION
        logger.info("Initializing Databricks MCP server")

        self._task_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
        self._resource_cache: Dict[str, ResourcePayload] = {}
        self._metrics: Counter[str] = Counter()

        self._validate_environment()
        self._register_resources()
        self._register_tools()

    async def _report_progress(self, ctx: Context | None, progress: float, total: float = 100.0, message: str | None = None) -> None:
        if ctx is None:
            return
        try:
            await ctx.report_progress(progress, total, message=message)
        except Exception:  # pragma: no cover - progress failures are non-fatal
            logger.debug("Failed to report progress %s for %s", progress, message, exc_info=True)

    def _validate_environment(self) -> None:
        missing = []
        if not settings.DATABRICKS_HOST or settings.DATABRICKS_HOST == "https://example.databricks.net":
            missing.append("DATABRICKS_HOST")
        if settings.DATABRICKS_TOKEN == "dapi_token_placeholder":
            missing.append("DATABRICKS_TOKEN")

        if missing:
            hint = ", ".join(missing)
            logger.warning("Missing Databricks credentials: %s", hint)

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:  # type: ignore[override]
        """Expose structured call_tool for in-process callers (CLI/tests)."""
        context = self.get_context()
        result = await self._tool_manager.call_tool(name, arguments, context=context, convert_result=False)

        if isinstance(result, CallToolResult):
            return result

        if isinstance(result, tuple) and len(result) == 2:
            unstructured, structured = result
            return CallToolResult(content=list(unstructured), _meta={"data": structured}, isError=False)

        if isinstance(result, dict):
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))],
                _meta={"data": result},
                isError=False,
            )

        if hasattr(result, "__iter__"):
            return CallToolResult(content=list(result), _meta={"data": {}}, isError=False)

        return CallToolResult(
            content=[TextContent(type="text", text=f"Unexpected return type: {type(result).__name__}")],
            _meta={"data": {"error": "unexpected_type"}},
            isError=True,
        )

    # ------------------------------------------------------------------
    # Resource helpers
    # ------------------------------------------------------------------
    def _register_resources(self) -> None:
        @self.resource("resource://databricks/exports/{resource_id}", description="Cached Databricks export")
        async def read_cached_resource(resource_id: str) -> str | bytes:
            payload = self._resource_cache.get(resource_id)
            if payload is None:
                raise ValueError(f"Resource {resource_id} not found")
            if payload.is_text:
                return payload.data.decode("utf-8")
            return payload.data

    def _cache_resource(
        self,
        content: bytes | str,
        *,
        mime_type: Optional[str],
        description: Optional[str],
    ) -> str:
        if isinstance(content, str):
            payload = ResourcePayload(data=content.encode("utf-8"), mime_type=mime_type, description=description, is_text=True)
        else:
            payload = ResourcePayload(data=content, mime_type=mime_type, description=description, is_text=False)

        resource_id = uuid.uuid4().hex
        self._resource_cache[resource_id] = payload
        return f"resource://databricks/exports/{resource_id}"

    # ------------------------------------------------------------------
    # Execution helper
    # ------------------------------------------------------------------
    async def _run_tool(
        self,
        name: str,
        action: Callable[[], Awaitable[Any]],
        summary_fn: Callable[[Any], str],
        ctx: Context | None,
    ) -> CallToolResult:
        inbound_request_id = getattr(ctx, "request_id", None) if ctx else None
        execution_id = inbound_request_id or uuid.uuid4().hex
        extra = {"request_id": execution_id}
        token = request_context_id.set(execution_id)

        try:
            await self._report_progress(ctx, 0, message=f"Starting {name}")
            async with self._task_semaphore:
                try:
                    result = await asyncio.wait_for(action(), timeout=settings.TOOL_TIMEOUT_SECONDS)
                except asyncio.TimeoutError:
                    message = f"{name} timed out after {settings.TOOL_TIMEOUT_SECONDS}s"
                    logger.warning("%s", message, extra=extra)
                    self._metrics[f"{name}.timeout"] += 1
                    err = error_result(message, status_code=504)
                    err.meta = {"tool": name, "_request_id": execution_id}
                    return err
                except asyncio.CancelledError:
                    message = f"{name} was cancelled"
                    logger.info(message, extra=extra)
                    self._metrics[f"{name}.cancelled"] += 1
                    err = error_result(message, status_code=499)
                    err.meta = {"tool": name, "_request_id": execution_id}
                    return err
                except DatabricksAPIError as err:
                    message = f"{name} failed: {err.message}"
                    logger.warning(message, extra=extra)
                    self._metrics[f"{name}.error"] += 1
                    err_result = error_result(message, details=err.response, status_code=err.status_code)
                    err_result.meta = {"tool": name, "_request_id": execution_id}
                    return err_result
                except Exception as err:  # pylint: disable=broad-except
                    logger.exception("Unexpected error running %s", name, extra=extra)
                    self._metrics[f"{name}.error"] += 1
                    err_result = error_result(f"{name} failed unexpectedly", details=str(err))
                    err_result.meta = {"tool": name, "_request_id": execution_id}
                    return err_result
        finally:
            request_context_id.reset(token)

        summary = summary_fn(result)
        response = success_result(summary, result, meta={"tool": name, "_request_id": execution_id})
        self._metrics[f"{name}.success"] += 1
        await self._report_progress(ctx, 100, message=f"Completed {name}")
        logger.info("Tool %s succeeded", name, extra={"request_id": execution_id, "tool": name})
        return response

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------
    def _register_tools(self) -> None:
        # Cluster tools
        @self.tool(name="list_clusters", description="List all Databricks clusters")
        async def list_clusters(ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_clusters",
                lambda: clusters.list_clusters(),
                lambda data: f"Found {len(data.get('clusters', []))} clusters",
                ctx,
            )

        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster",
                    )
        async def create_cluster(cluster: ClusterConfig, ctx: Context | None = None) -> CallToolResult:
            payload = cluster.model_dump(exclude_none=True)

            async def action() -> Any:
                return await clusters.create_cluster(payload)

            return await self._run_tool(
                "create_cluster",
                action,
                lambda data: f"Cluster {data.get('cluster_id', payload['cluster_name'])} creation submitted",
                ctx,
            )

        @self.tool(name="terminate_cluster", description="Terminate a cluster")
        async def terminate_cluster(cluster_id: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "terminate_cluster",
                lambda: clusters.terminate_cluster(cluster_id),
                lambda _: f"Termination requested for cluster {cluster_id}",
                ctx,
            )

        @self.tool(name="get_cluster", description="Get information about a cluster")
        async def get_cluster(cluster_id: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "get_cluster",
                lambda: clusters.get_cluster(cluster_id),
                lambda data: f"Cluster {data.get('cluster_id', cluster_id)} state: {data.get('state', 'unknown')}",
                ctx,
            )

        @self.tool(name="start_cluster", description="Start a terminated cluster")
        async def start_cluster(cluster_id: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "start_cluster",
                lambda: clusters.start_cluster(cluster_id),
                lambda _: f"Start requested for cluster {cluster_id}",
                ctx,
            )

        # Job tools
        @self.tool(name="list_jobs", description="List Databricks jobs")
        async def list_jobs(ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_jobs",
                lambda: jobs.list_jobs(),
                lambda data: f"Discovered {len(data.get('jobs', []))} jobs",
                ctx,
            )

        @self.tool(name="create_job", description="Create a Databricks job")
        async def create_job(job: Job, ctx: Context | None = None) -> CallToolResult:
            async def action() -> Any:
                return await jobs.create_job(job.model_dump(exclude_none=True))

            return await self._run_tool(
                "create_job",
                action,
                lambda data: f"Created job {data.get('job_id')} for {job.name}",
                ctx,
            )

        @self.tool(name="delete_job", description="Delete a Databricks job")
        async def delete_job(job_id: int, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "delete_job",
                lambda: jobs.delete_job(job_id),
                lambda _: f"Deleted job {job_id}",
                ctx,
            )

        @self.tool(name="run_job", description="Trigger a job run")
        async def run_job(job_id: int, notebook_params: Optional[Dict[str, Any]] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "run_job",
                lambda: jobs.run_job(job_id, notebook_params or {}),
                lambda data: f"Run {data.get('run_id')} started for job {job_id}",
                ctx,
            )

        @self.tool(
            name="run_notebook",
            description="Submit a one-time notebook run",
                    )
        async def run_notebook(
            notebook_path: str,
            existing_cluster_id: Optional[str] = None,
            base_parameters: Optional[Dict[str, Any]] = None,
            ctx: Context | None = None,
        ) -> CallToolResult:
            return await self._run_tool(
                "run_notebook",
                lambda: jobs.run_notebook(
                    notebook_path=notebook_path,
                    existing_cluster_id=existing_cluster_id,
                    base_parameters=base_parameters,
                ),
                lambda data: f"Notebook run {data.get('run_id')} started for {notebook_path}",
                ctx,
            )

        @self.tool(
            name="sync_repo_and_run_notebook",
            description="Pull a repo and run a notebook",
                    )
        async def sync_repo_and_run_notebook(
            repo_id: int,
            notebook_path: str,
            existing_cluster_id: Optional[str] = None,
            base_parameters: Optional[Dict[str, Any]] = None,
            ctx: Context | None = None,
        ) -> CallToolResult:
            async def action() -> Any:
                await self._report_progress(ctx, 25, message="Pulling repo")
                await repos.pull_repo(repo_id)
                await self._report_progress(ctx, 60, message="Triggering notebook run")
                return await jobs.run_notebook(
                    notebook_path=notebook_path,
                    existing_cluster_id=existing_cluster_id,
                    base_parameters=base_parameters,
                )

            return await self._run_tool(
                "sync_repo_and_run_notebook",
                action,
                lambda data: f"Repo {repo_id} synced; notebook run {data.get('run_id')} started",
                ctx,
            )

        @self.tool(name="get_run_status", description="Get status for a job run")
        async def get_run_status(run_id: int, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "get_run_status",
                lambda: jobs.get_run_status(run_id),
                lambda data: f"Run {run_id} state: {data.get('state')}",
                ctx,
            )

        @self.tool(name="list_job_runs", description="List recent job runs")
        async def list_job_runs(job_id: Optional[int] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_job_runs",
                lambda: jobs.list_runs(job_id=job_id),
                lambda data: f"Found {len(data.get('runs', []))} runs",
                ctx,
            )

        @self.tool(name="cancel_run", description="Cancel a job run")
        async def cancel_run(run_id: int, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "cancel_run",
                lambda: jobs.cancel_run(run_id),
                lambda _: f"Cancel requested for run {run_id}",
                ctx,
            )

        # Notebook workspace tools
        @self.tool(name="list_notebooks", description="List notebooks in a directory")
        async def list_notebooks(path: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_notebooks",
                lambda: notebooks.list_notebooks(path),
                lambda data: f"Found {len(data.get('objects', []))} objects in {path}",
                ctx,
            )

        @self.tool(name="export_notebook", description="Export a notebook")
        async def export_notebook(path: str, format: str = "SOURCE", ctx: Context | None = None) -> CallToolResult:
            result = await self._run_tool(
                "export_notebook",
                lambda: notebooks.export_notebook(path, format=format),
                lambda data: f"Exported notebook {path} in {format} format",
                ctx,
            )

            data_block = result.structuredContent or {}
            if result.isError or not data_block:
                return result

            content_b64 = data_block.get("content")
            decoded = data_block.get("decoded_content")

            mime = {
                "SOURCE": "text/plain",
                "HTML": "text/html",
                "JUPYTER": "application/json",
                "DBC": "application/x-databricks-notebook",
            }.get(format, "application/octet-stream")

            if decoded:
                resource_uri = self._cache_resource(decoded, mime_type=mime, description=f"Notebook {path} ({format})")
            elif content_b64:
                raw_bytes = base64.b64decode(content_b64)
                resource_uri = self._cache_resource(raw_bytes, mime_type=mime, description=f"Notebook {path} ({format})")
            else:
                return result

            result.content.append(
                {
                    "type": "resource_link",
                    "uri": resource_uri,
                    "name": f"Notebook export ({format})",
                    "description": f"Notebook {path} ({format})",
                    "mimeType": mime,
                }
            )
            structured = result.structuredContent or {}
            structured.setdefault("resource_uri", resource_uri)
            result.structuredContent = structured
            await self._report_progress(ctx, 90, message="Notebook export cached")
            return result

        @self.tool(name="import_notebook", description="Import a notebook")
        async def import_notebook(
            path: str,
            content: str,
            format: str = "SOURCE",
            language: Optional[str] = None,
            overwrite: bool = False,
            ctx: Context | None = None,
        ) -> CallToolResult:
            return await self._run_tool(
                "import_notebook",
                lambda: notebooks.import_notebook(path, content, format=format, language=language, overwrite=overwrite),
                lambda _: f"Imported notebook to {path}",
                ctx,
            )

        @self.tool(
            name="delete_workspace_object",
            description="Delete a workspace notebook or directory",
                    )
        async def delete_workspace_object(path: str, recursive: bool = False, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "delete_workspace_object",
                lambda: notebooks.delete_notebook(path, recursive=recursive),
                lambda _: f"Deleted workspace path {path}",
                ctx,
            )

        @self.tool(name="get_workspace_file_content", description="Retrieve workspace file content")
        async def get_workspace_file_content(path: str, format: str = "SOURCE", ctx: Context | None = None) -> CallToolResult:
            result = await self._run_tool(
                "get_workspace_file_content",
                lambda: notebooks.export_workspace_file(path, format=format),
                lambda data: f"Retrieved workspace file {path}",
                ctx,
            )

            data_block = result.structuredContent or {}
            if result.isError or not data_block:
                return result

            decoded = data_block.get("decoded_content")
            mime = "application/json" if data_block.get("content_type") == "json" else "text/plain"

            if decoded:
                resource_uri = self._cache_resource(decoded, mime_type=mime, description=f"Workspace file {path}")
            elif data_block.get("content"):
                raw_bytes = base64.b64decode(data_block["content"])
                resource_uri = self._cache_resource(raw_bytes, mime_type=mime, description=f"Workspace file {path}")
            else:
                resource_uri = None

            if resource_uri:
                result.content.append(
                    {
                        "type": "resource_link",
                        "uri": resource_uri,
                        "name": "Workspace export",
                        "description": f"Workspace file {path}",
                        "mimeType": mime,
                    }
                )
                structured = result.structuredContent or {}
                structured.setdefault("resource_uri", resource_uri)
                result.structuredContent = structured

            return result

        @self.tool(name="get_workspace_file_info", description="Retrieve workspace metadata")
        async def get_workspace_file_info(path: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "get_workspace_file_info",
                lambda: notebooks.get_workspace_file_info(path),
                lambda data: f"Metadata returned for {data.get('path', path)}",
                ctx,
            )

        # DBFS tools
        @self.tool(name="list_files", description="List DBFS files for a path")
        async def list_files(path: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_files",
                lambda: dbfs.list_files(path),
                lambda data: f"Found {len(data.get('paths') or data.get('files', []))} entries at {path}",
                ctx,
            )

        @self.tool(name="dbfs_put", description="Upload small content to DBFS")
        async def dbfs_put(path: str, content: str, overwrite: bool = True, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "dbfs_put",
                lambda: dbfs.put_file(path, content.encode("utf-8"), overwrite=overwrite),
                lambda _: f"Uploaded content to {path}",
                ctx,
            )

        @self.tool(name="dbfs_delete", description="Delete a DBFS path")
        async def dbfs_delete(path: str, recursive: bool = False, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "dbfs_delete",
                lambda: dbfs.delete_file(path, recursive=recursive),
                lambda _: f"Deleted DBFS path {path}",
                ctx,
            )

        # Library tools
        @self.tool(name="install_library", description="Install libraries on a cluster")
        async def install_library(cluster_id: str, libraries_spec: List[Dict[str, Any]], ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "install_library",
                lambda: libraries.install_library(cluster_id, libraries_spec),
                lambda _: f"Library install requested on cluster {cluster_id}",
                ctx,
            )

        @self.tool(name="uninstall_library", description="Uninstall libraries from a cluster")
        async def uninstall_library(cluster_id: str, libraries_spec: List[Dict[str, Any]], ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "uninstall_library",
                lambda: libraries.uninstall_library(cluster_id, libraries_spec),
                lambda _: f"Library uninstall requested on cluster {cluster_id}",
                ctx,
            )

        @self.tool(name="list_cluster_libraries", description="List libraries for a cluster")
        async def list_cluster_libraries(cluster_id: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_cluster_libraries",
                lambda: libraries.list_cluster_libraries(cluster_id),
                lambda data: f"Cluster {cluster_id} has {len(data.get('library_statuses', []))} enrolled libraries",
                ctx,
            )

        # Repo tools
        @self.tool(name="create_repo", description="Create or clone a repo")
        async def create_repo(url: str, provider: str, branch: Optional[str] = None, path: Optional[str] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "create_repo",
                lambda: repos.create_repo(url, provider, branch=branch, path=path),
                lambda data: f"Repo {data.get('id')} created from {url}",
                ctx,
            )

        @self.tool(name="update_repo", description="Update repo branch or tag")
        async def update_repo(repo_id: int, branch: Optional[str] = None, tag: Optional[str] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "update_repo",
                lambda: repos.update_repo(repo_id, branch=branch, tag=tag),
                lambda _: f"Updated repo {repo_id}",
                ctx,
            )

        @self.tool(name="list_repos", description="List repos in the workspace")
        async def list_repos(path_prefix: Optional[str] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_repos",
                lambda: repos.list_repos(path_prefix=path_prefix),
                lambda data: f"Found {len(data.get('repos', []))} repos",
                ctx,
            )

        @self.tool(name="pull_repo", description="Pull latest commit for a repo")
        async def pull_repo(repo_id: int, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "pull_repo",
                lambda: repos.pull_repo(repo_id),
                lambda _: f"Pulled latest changes for repo {repo_id}",
                ctx,
            )

        # SQL tools
        @self.tool(name="execute_sql", description="Execute a SQL statement")
        async def execute_sql(
            statement: str,
            warehouse_id: Optional[str] = None,
            catalog: Optional[str] = None,
            schema_name: Optional[str] = None,
            ctx: Context | None = None,
        ) -> CallToolResult:
            async def action() -> Any:
                await self._report_progress(ctx, 10, message="Submitting SQL statement")
                result = await sql.execute_statement(
                    statement=statement,
                    warehouse_id=warehouse_id,
                    catalog=catalog,
                    schema=schema_name,
                )
                await self._report_progress(ctx, 70, message="SQL statement completed")
                return result

            return await self._run_tool(
                "execute_sql",
                action,
                lambda data: f"SQL statement {data.get('statement_id', 'completed')} executed",
                ctx,
            )

        # Unity catalog tools
        @self.tool(name="list_catalogs", description="List Unity Catalog catalogs")
        async def list_catalogs(ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_catalogs",
                lambda: unity_catalog.list_catalogs(),
                lambda data: f"Found {len(data.get('catalogs', []))} catalogs",
                ctx,
            )

        @self.tool(name="create_catalog", description="Create a Unity Catalog catalog")
        async def create_catalog(name: str, comment: Optional[str] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "create_catalog",
                lambda: unity_catalog.create_catalog(name, comment),
                lambda _: f"Created catalog {name}",
                ctx,
            )

        @self.tool(name="list_schemas", description="List schemas in a catalog")
        async def list_schemas(catalog_name: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_schemas",
                lambda: unity_catalog.list_schemas(catalog_name),
                lambda data: f"Catalog {catalog_name} has {len(data.get('schemas', []))} schemas",
                ctx,
            )

        @self.tool(name="create_schema", description="Create a schema in Unity Catalog")
        async def create_schema(catalog_name: str, name: str, comment: Optional[str] = None, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "create_schema",
                lambda: unity_catalog.create_schema(catalog_name, name, comment),
                lambda _: f"Created schema {catalog_name}.{name}",
                ctx,
            )

        @self.tool(name="list_tables", description="List tables for a schema")
        async def list_tables(catalog_name: str, schema_name: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "list_tables",
                lambda: unity_catalog.list_tables(catalog_name, schema_name),
                lambda data: f"Schema {catalog_name}.{schema_name} has {len(data.get('tables', []))} tables",
                ctx,
            )

        @self.tool(name="create_table", description="Create a table via SQL")
        async def create_table(warehouse_id: str, statement: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "create_table",
                lambda: unity_catalog.create_table(warehouse_id, statement),
                lambda data: f"Table creation run {data.get('run_id', 'submitted')} for warehouse {warehouse_id}",
                ctx,
            )

        @self.tool(name="get_table_lineage", description="Get Unity Catalog table lineage")
        async def get_table_lineage(full_name: str, ctx: Context | None = None) -> CallToolResult:
            return await self._run_tool(
                "get_table_lineage",
                lambda: unity_catalog.get_table_lineage(full_name),
                lambda data: f"Lineage contains {len(data.get('upstream_tables', []))} upstream tables",
                ctx,
            )

    def get_metrics_snapshot(self) -> Dict[str, int]:
        """Return a copy of collected tool metrics."""
        return dict(self._metrics)

    # ------------------------------------------------------------------
    # Entrypoint
    # ------------------------------------------------------------------

def main() -> None:
    """Main entry point for the MCP server."""
    configure_logging(level=settings.LOG_LEVEL, log_file="databricks_mcp.log")
    try:
        logger.info("Starting Databricks MCP server")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(line_buffering=True)
        server = DatabricksMCPServer()
        server.run()
    except Exception:  # pylint: disable=broad-except
        logger.exception("Fatal error in Databricks MCP server")
        raise


if __name__ == "__main__":
    main()
