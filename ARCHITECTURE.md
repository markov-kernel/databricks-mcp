# Databricks MCP Server — Architecture and Deep Dive

This document provides a comprehensive, highly detailed, end‑to‑end overview of the Databricks MCP Server contained in this repository. It covers the project structure, runtime architecture, MCP tools and their parameters, data flow and error handling, configuration, testing, and known caveats.

> Package: `databricks-mcp-server` (v0.4.4 in packaging metadata)


## 1) Repository at a Glance

```
.
├─ AGENTS.md
├─ ARCHITECTURE.md
├─ README.md
├─ databricks_mcp/
│  ├─ __init__.py
│  ├─ __main__.py
│  ├─ main.py
│  ├─ api/
│  │  ├─ clusters.py
│  │  ├─ dbfs.py
│  │  ├─ jobs.py
│  │  ├─ libraries.py
│  │  ├─ notebooks.py
│  │  ├─ repos.py
│  │  └─ unity_catalog.py
│  ├─ cli/
│  │  └─ commands.py
│  ├─ core/
│  │  ├─ auth.py
│  │  ├─ config.py
│  │  ├─ logging_utils.py
│  │  ├─ models.py
│  │  └─ utils.py
│  └─ server/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ app.py
│     ├─ databricks_mcp_server.py
│     └─ tool_helpers.py
├─ tests/
│  ├─ test_additional_features.py
│  ├─ test_clusters.py
│  ├─ test_server_structured.py
│  ├─ test_tool_metadata.py
│  └─ test_transcript.py
├─ .env.example
├─ pyproject.toml
└─ uv.lock
```


## 2) Build, Packaging, and Entry Points

- Packaging is configured via Hatch (`hatchling`).
- Python ≥ 3.10.
- Key dependencies: `mcp[cli]` (1.2.0+), `httpx`, `databricks-sdk`. Dev extras add `pytest`, `pytest-asyncio`, `fastapi`, `anyio` for local HTTP testing and async test support.
- Console scripts are declared in packaging metadata (`pyproject.toml`):
  - `databricks-mcp-server` → `databricks_mcp.server.databricks_mcp_server:main`
  - `databricks-mcp` → `databricks_mcp.cli.commands:main`

Module entrypoints for `python -m` execution:
- `databricks_mcp/__main__.py` delegates to `databricks_mcp.main:main`.
- `databricks_mcp/server/__main__.py` invokes `server.databricks_mcp_server:main()` directly.


## 3) Configuration & Environment

File: `databricks_mcp/core/config.py`
- `.env` loading is silent (no stdout noise) unless Cursor provides env via `RUNNING_VIA_CURSOR_MCP`.
- Pydantic `Settings` surface:
  - Core Databricks auth: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, optional `DATABRICKS_WAREHOUSE_ID`.
  - Logging/runtime: `LOG_LEVEL`, plus `TOOL_TIMEOUT_SECONDS`, `MAX_CONCURRENT_REQUESTS` controlling server execution safeguards.
  - HTTP behaviour: `HTTP_TIMEOUT_SECONDS`, `API_MAX_RETRIES`, `API_RETRY_BACKOFF_SECONDS` used by `core.utils` for exponential backoff.
- Helpers:
  - `get_api_headers()` returns Authorization and JSON headers.
  - `get_databricks_api_url(endpoint)` joins host + endpoint, trimming extra slashes.

Example `.env` (see `.env.example`):
```
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=dapi_your_token_here
DATABRICKS_WAREHOUSE_ID=sql_warehouse_12345
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
TOOL_TIMEOUT_SECONDS=300
MAX_CONCURRENT_REQUESTS=8
HTTP_TIMEOUT_SECONDS=60
API_MAX_RETRIES=3
API_RETRY_BACKOFF_SECONDS=0.5
```

Note: Package and runtime versions are unified via `settings.VERSION` (currently `0.4.4`).


## 4) Core Utilities and Error Handling

File: `databricks_mcp/core/utils.py`
- `DatabricksAPIError` captures message, status code, and raw response.
- `request_context_id` (`ContextVar[str | None]`) propagates per-request correlation IDs from the MCP layer into HTTP headers (`X-Databricks-MCP-Request-ID`).
- `make_api_request(...)` now includes:
  - `httpx.AsyncClient` with configurable timeout from settings.
  - Exponential backoff (`API_MAX_RETRIES`, `API_RETRY_BACKOFF_SECONDS`) for retryable status codes (408/429/5xx) and transport hiccups.
  - Redaction of payload logs and structured logging on failures before raising `DatabricksAPIError`.
- `format_response(...)` remains available for legacy helpers but primary paths return raw dicts that the server wraps into `CallToolResult` metadata.


## 5) Domain Models

File: `databricks_mcp/core/models.py`
- Lightweight Pydantic models for common structures: `ClusterConfig`, `JobTask`, `Job`, `Run`, `WorkspaceObject`, `DbfsItem`, `Library`, `Repo`, `Catalog`, `Schema`, `Table`.
- `ClusterConfig` backs the structured `create_cluster` tool signature so MCP schemas expose the Databricks create API fields.


## 6) Server Architecture (MCP)

File: `databricks_mcp/server/databricks_mcp_server.py:1`
- Implements an MCP server using `mcp.server.FastMCP`.
- On construction, logs environment, registers all tools, and serves over stdio using `FastMCP.run()` in `main()`.
- Logging targets `databricks_mcp.log` with level from `LOG_LEVEL`.

### 6.1 Parameter Handling and Client Compatibility
- Tools expose explicit, flat parameters via FastMCP's schema generation, so clients see the canonical JSON shape (e.g., `{ "cluster_id": "..." }`).
- Legacy `{ "params": { ... } }` envelopes were removed in favour of consistent argument validation.

### 6.2 Content Shape and Structured Results
- Tool handlers return `CallToolResult` objects with a short human summary (`TextContent`) and the full Databricks payload in `structuredContent` (validated by each tool's `outputSchema`).
- Each response annotates `_meta['_request_id']` for correlation and attaches cached resource references for large exports.
- Tests such as `tests/test_server_structured.py` assert the presence of structured JSON and resource metadata.

### 6.3 Progress & Metrics
- `_report_progress` invokes `ctx.report_progress(...)` so clients receive start/finish updates (with midpoints for multi-phase tools like repo sync + notebook run).
- A `Counter` tracks success/error/timeout/cancelled tallies per tool, retrievable via `get_metrics_snapshot()`.

### 6.4 Startup
- `main()` reconfigures stdout line buffering (useful for stdio-based protocols) and calls `server.run()`.
- The server does not expose HTTP routes by default; HTTP is provided by a separate FastAPI stub for testing.


## 7) HTTP Stub (FastAPI) for Tests

File: `databricks_mcp/server/app.py:1`
- Minimal FastAPI app that routes a subset of cluster and workspace operations directly to the async API layer.
- Intended only for test compatibility and not used by the MCP runtime.


## 8) CLI

File: `databricks_mcp/cli/commands.py`
- Subcommands:
  - `start` — runs the MCP server (stdio entrypoint).
  - `list-tools` — prints tool name + description via `FastMCP.list_tools()`.
  - `version` — instantiates the server to display `server.version` and warn about missing env vars.
  - `sync-run` — wraps `sync_repo_and_run_notebook`, printing the summary text block and pretty-printing `structuredContent` on success/errors.

Examples:
```
# Start server (stdio MCP host must spawn this)
databricks-mcp start

# List tools
databricks-mcp list-tools

# Version
databricks-mcp version

# Pull repo and run notebook
databricks-mcp sync-run --repo-id 42 --notebook-path /Shared/foo --cluster-id 1234-abc
```


## 9) Databricks API Modules

All modules delegate HTTP calls to `core.utils.make_api_request` and are fully async.

### 9.1 Clusters — `databricks_mcp/api/clusters.py:1`
- `create_cluster(cluster_config)` → `POST /api/2.0/clusters/create`
- `terminate_cluster(cluster_id)` → `POST /api/2.0/clusters/delete`
- `list_clusters()` → `GET /api/2.0/clusters/list`
- `get_cluster(cluster_id)` → `GET /api/2.0/clusters/get`
- `start_cluster(cluster_id)` → `POST /api/2.0/clusters/start`
- `resize_cluster(cluster_id, num_workers)` → `POST /api/2.0/clusters/resize`
- `restart_cluster(cluster_id)` → `POST /api/2.0/clusters/restart`

### 9.2 Jobs — `databricks_mcp/api/jobs.py:1`
- CRUD & execution:
  - `create_job(job_config)` → `POST /api/2.2/jobs/create`
  - `run_job(job_id, notebook_params=None)` → `POST /api/2.0/jobs/run-now`
  - `list_jobs()` → `GET /api/2.0/jobs/list`
  - `get_job(job_id)` → `GET /api/2.0/jobs/get`
  - `update_job(job_id, new_settings)` → `POST /api/2.0/jobs/update`
  - `delete_job(job_id)` → `POST /api/2.2/jobs/delete`
- Runs & polling:
  - `submit_run(run_config)` → `POST /api/2.0/jobs/runs/submit`
  - `get_run(run_id)` → `GET /api/2.1/jobs/runs/get`
  - `list_runs(job_id=None, limit=20)` → `GET /api/2.1/jobs/runs/list`
  - `get_run_status(run_id)` → extracts concise `state` and `life_cycle` fields
  - `cancel_run(run_id)` → `POST /api/2.1/jobs/runs/cancel`
  - `get_run_output(run_id)` → `GET /api/2.0/jobs/runs/get-output`
- Notebook one-off execution helper:
  - `run_notebook(notebook_path, existing_cluster_id=None, base_parameters=None, ...)`
    - Builds a transient run task and waits until termination (`await_until_state`) before fetching output.

### 9.3 Notebooks & Workspace — `databricks_mcp/api/notebooks.py:1`
- `import_notebook(path, content, format='SOURCE', language=None, overwrite=False)` → `POST /api/2.0/workspace/import`
  - If `content` is not base64, it will be encoded.
- `export_notebook(path, format='SOURCE')` → `GET /api/2.0/workspace/export`
  - Decodes base64 when possible, attaching `decoded_content` and `content_type`.
- `list_notebooks(path)` → `GET /api/2.0/workspace/list`
- `delete_notebook(path, recursive=False)` → `POST /api/2.0/workspace/delete`
- `create_directory(path)` → `POST /api/2.0/workspace/mkdirs`
- `export_workspace_file(path, format='SOURCE')` → general-purpose export for non-notebook files
- `get_workspace_file_info(path)` → directory listing lookup to return metadata for a specific file

### 9.4 DBFS — `databricks_mcp/api/dbfs.py:1`
- Small uploads: `put_file(dbfs_path, file_content_bytes, overwrite=True)` → `POST /api/2.0/dbfs/put`
- Large uploads: `upload_large_file(dbfs_path, local_file_path, overwrite=True, buffer_size=1MB)`
  - Orchestrates `create` → repeated `add-block` → `close` with base64 chunks.
  - Attempts a best-effort `close` on error for cleanup.
- Reads: `get_file(dbfs_path, offset=0, length=1MB)` → `GET /api/2.0/dbfs/read` (decodes base64 into `decoded_data`).
- Listings & metadata: `list_files(dbfs_path)`, `get_status(dbfs_path)`, `create_directory(dbfs_path)`, `delete_file(dbfs_path, recursive=False)`.

### 9.5 SQL Warehouses — `databricks_mcp/api/sql.py:1`
- `execute_statement(statement, warehouse_id=None, catalog=None, schema=None, parameters=None, row_limit=10000, byte_limit=100MB)` → `POST /api/2.0/sql/statements`
  - Falls back to `settings.DATABRICKS_WAREHOUSE_ID` if `warehouse_id` not provided.
  - Uses `format=JSON_ARRAY`, `disposition=INLINE`, `wait_timeout=10s`.
- `execute_and_wait(...)` → kicks off `execute_statement`, then polls `get_statement_status(statement_id)` until `SUCCEEDED` or failure/timeout.
- `get_statement_status(statement_id)`, `cancel_statement(statement_id)`.

### 9.6 Cluster Libraries — `databricks_mcp/api/libraries.py:1`
- `install_library(cluster_id, libraries)` → `POST /api/2.0/libraries/install`
- `uninstall_library(cluster_id, libraries)` → `POST /api/2.0/libraries/uninstall`
- `list_cluster_libraries(cluster_id)` → `GET /api/2.0/libraries/cluster-status`

### 9.7 Repos — `databricks_mcp/api/repos.py:1`
- `create_repo(url, provider, branch=None, path=None)` → `POST /api/2.0/repos`
- `update_repo(repo_id, branch=None, tag=None)` → `PATCH /api/2.0/repos/{id}`
- `list_repos(path_prefix=None)` → `GET /api/2.0/repos`
- `pull_repo(repo_id)` → `POST /api/2.0/repos/{id}/pull`

### 9.8 Unity Catalog — `databricks_mcp/api/unity_catalog.py:1`
- Catalogs: `list_catalogs()`, `create_catalog(name, comment=None)`
- Schemas: `list_schemas(catalog_name)`, `create_schema(catalog_name, name, comment=None)`
- Tables: `list_tables(catalog_name, schema_name)`, `create_table(warehouse_id, statement)` (via SQL API)
- Lineage: `get_table_lineage(full_name)` → `GET /api/2.1/unity-catalog/lineage-tracking/table-lineage/{full_name}`


## 10) MCP Tool Inventory (Names, Purpose, Parameters)

All registered in `databricks_mcp/server/databricks_mcp_server.py`:

- Clusters:
  - `list_clusters`
  - `create_cluster` — params mirror Databricks create API (name, spark_version, node_type_id, …)
  - `terminate_cluster` — `cluster_id`
  - `get_cluster` — `cluster_id`
  - `start_cluster` — `cluster_id`
- Jobs:
  - `list_jobs`
  - `create_job` — `{ name, tasks, … }`
  - `delete_job` — `job_id`
  - `run_job` — `job_id`, optional `notebook_params`
  - `run_notebook` — `notebook_path`, optional `existing_cluster_id`, `base_parameters`
  - `sync_repo_and_run_notebook` — `repo_id`, `notebook_path`, optional cluster/parameters
  - `get_run_status` — `run_id`
  - `list_job_runs` — `job_id`
  - `cancel_run` — `run_id`
- Workspace/Notebooks:
  - `list_notebooks` — `path`
  - `export_notebook` — `path`, optional `format`
  - `import_notebook` — `path`, `content` (base64 or text), optional `format`
  - `delete_workspace_object` — `path`, optional `recursive`
  - `get_workspace_file_content` — `path`, optional `format`
  - `get_workspace_file_info` — `path`
- DBFS:
  - `list_files` — `path`
  - `dbfs_put` — `path`, `content` (UTF-8 string)
  - `dbfs_delete` — `path`, optional `recursive`
- SQL:
  - `execute_sql` — `statement`, optional `warehouse_id`, `catalog`, `schema_name`
- Cluster Libraries:
  - `install_library` — `cluster_id`, `libraries`
  - `uninstall_library` — `cluster_id`, `libraries`
  - `list_cluster_libraries` — `cluster_id`
- Repos:
  - `create_repo` — `url`, `provider`, optional `branch`, `path`
  - `update_repo` — `repo_id`, `branch` or `tag`
  - `list_repos` — optional `path_prefix`
  - `pull_repo` — `repo_id`
- Unity Catalog:
  - `list_catalogs`, `create_catalog`
  - `list_schemas`, `create_schema`
  - `list_tables`, `create_table`
  - `get_table_lineage`


## 11) Data Flow (Typical Lifecycles)

### 11.1 MCP Tool Invocation → Databricks
1. MCP clients invoke tool `X` with flat JSON arguments generated from FastMCP's auto-synthesised `inputSchema`.
2. Server validates/coerces arguments via Pydantic-toned metadata and dispatches to the async API module.
3. API utilities issue REST calls with exponential retry, correlation headers, and bounded concurrency.
4. Tool handler wraps the API payload in a `CallToolResult`, emitting a concise text summary and attaching the raw JSON to `structuredContent` (with `_meta['_request_id']`).
5. For large artifacts (notebook exports, workspace files), the handler caches the payload and emits `resource_link` content blocks using URIs such as `resource://databricks/exports/{id}`, allowing clients to fetch the data through the MCP resources API.

### 11.2 SQL Execution
1. `execute_sql` builds a statement payload; uses explicit `warehouse_id` or `settings.DATABRICKS_WAREHOUSE_ID` and forwards `catalog` / `schema_name` when provided.
2. Returns inline results (JSON array format). For long-running queries, use `execute_and_wait`.

### 11.3 Notebook One-Off Run
1. `run_notebook` constructs a submit run with `notebook_task`.
2. Waits until lifecycle reaches target state; fetches output via `get_run_output`.

### 11.4 DBFS Large Upload
1. `upload_large_file` issues `create` to get a handle.
2. Splits local file into 1MB chunks, base64 encodes, and `add-block` for each.
3. `close` finalizes the upload; attempts cleanup on failure.


## 12) Error Handling, Progress, and Metrics

- HTTP layer retries transient failures and raises `DatabricksAPIError` with structured response payloads when available.
- `_run_tool` wraps calls in `asyncio.wait_for`, tracks success/error/timeout/cancel counters, and injects `_meta['_request_id']` for every response.
- On failure, `error_result(...)` places details in `structuredContent`; clients can inspect `isError` and use `_meta` solely for request metadata.
- Progress updates are reported through `Context.report_progress`, emitting start/mid/end notifications for long-running actions (repo sync + notebook run, SQL execution, etc.).
- Logging is centralized via `core.logging_utils.configure_logging`, emitting JSON lines to stderr (and `databricks_mcp.log` when configured) with correlation IDs.


## 13) Security Considerations

- MCP server communicates over stdio to its client (no socket binding), so access control is pushed to the embedding tool.
- The FastAPI stub includes a very basic API key mechanism (intended for local demos only) and should not be used in production (`databricks_mcp/core/auth.py`).
- Secrets are read from environment; avoid committing `.env`.


## 14) Testing Overview

Configuration (`pyproject.toml`) enables async tests with concise output and short tracebacks. The current suite is fully self-contained and does not depend on the removed PowerShell harnesses.

Representative suites:
- `tests/test_clusters.py` / `tests/test_additional_features.py` — patch API modules to validate tool orchestration logic.
- `tests/test_server_structured.py` — exercises structured `CallToolResult` payloads, ensuring `structuredContent` and cached resource URIs behave correctly.
- `tests/test_tool_metadata.py` — verifies FastMCP emits input/output schemas for registered tools.
- `tests/test_transcript.py` — captures a deterministic request/response transcript for regression detection.

All tests run offline by monkeypatching the Databricks API modules; real credentials are only required when manually invoking tools against live workspaces.


## 15) Known Caveats, Inconsistencies, and Suggested Fixes

- **Resource cache lifecycle**: cached exports accumulate in-memory without eviction. Consider TTL-based purging or exposing a `clear_cache` tool for long-lived processes.
- **Cancellation semantics**: incoming cancellation stops local awaiting (`asyncio.CancelledError`), but outstanding Databricks jobs/statements are not actively cancelled. A future iteration could call the corresponding Databricks cancel endpoints when feasible.
- **Progress granularity**: current progress notifications cover major phases only. Additional instrumentation (e.g., chunk counts for large uploads) may enhance UX.
- **FastAPI stub**: remains demo-only, unauthenticated aside from a simple API key helper. Production deployments should rely on the stdio MCP transport.


## 16) Usage Examples

### 16.1 Running via CLI
```
# Ensure env vars are set (see .env.example)
export DATABRICKS_HOST=...
export DATABRICKS_TOKEN=...
export DATABRICKS_WAREHOUSE_ID=...

# List tools
uvx databricks-mcp list-tools

# Start (typically the MCP client launches this via stdio)
uvx databricks-mcp start
```

### 16.2 Calling MCP tools (conceptual)
Pseudocode using an MCP client:
```python
# After session.initialize()
result = await session.call_tool("list_clusters", {})

summary = next((block.text for block in result.content if getattr(block, "type", "") == "text"), "")
data = result.structuredContent or {}

print(summary)
print(data.get("clusters", []))

resource_links = [block for block in result.content if isinstance(block, dict) and block.get("type") == "resource_link"]
print(resource_links)
```

### 16.3 DBFS upload (small)
```json
{
  "tool": "dbfs_put",
  "params": {
    "path": "/FileStore/samples/foo.txt",
    "content": "Hello, Databricks!"
  }
}
```

### 16.4 Notebook export and resource retrieval
```python
result = await session.call_tool("export_notebook", {"path": "/Repos/user/demo", "format": "SOURCE"})
resource_link = next((block for block in result.content if isinstance(block, dict) and block.get("type") == "resource_link"), None)
if resource_link:
    contents = await session.read_resource(resource_link["uri"])
```


## 17) Appendix A — MCP vs FastAPI

- MCP Server (primary): stdio transport; tools registered in `DatabricksMCPServer`.
- FastAPI stub (secondary): small HTTP facade for clusters/notebooks used by tests.
- Both reuse the same async API modules.


## 18) Appendix B — File/Module Cross-Reference

- Entrypoints: `databricks_mcp/__main__.py`, `databricks_mcp/main.py`, and `databricks_mcp/server/__main__.py`.
- MCP server implementation: `databricks_mcp/server/databricks_mcp_server.py`, helpers in `databricks_mcp/server/tool_helpers.py`.
- HTTP stub: `databricks_mcp/server/app.py` and related auth helpers in `databricks_mcp/core/auth.py`.
- Core utilities: configuration (`databricks_mcp/core/config.py`), logging (`core/logging_utils.py`), HTTP utilities (`core/utils.py`), domain models (`core/models.py`).
- CLI surface: `databricks_mcp/cli/commands.py`.
- Databricks API adapters: modules under `databricks_mcp/api/` for clusters, jobs, notebooks, dbfs, sql, libraries, repos, and unity catalog.


## 19) Appendix C — Troubleshooting Checklist

- “Missing Databricks credentials” warnings — set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` before running CLI commands or MCP clients.
- “warehouse_id must be provided…” — set `DATABRICKS_WAREHOUSE_ID` in the environment or pass `warehouse_id` to `execute_sql` explicitly.
- Notebook export returns no resource URIs — ensure the target path exists and the calling principal can read the workspace object.
- Cached resource URIs missing data — the `resources` cache is in-memory; long-lived processes may need manual cleanup or restarts if URIs expire.


## 20) Roadmap Ideas

- Add eviction/TTL controls to the resource cache to prevent unbounded growth.
- Invoke Databricks cancellation endpoints when MCP cancellation notifications arrive for long-running jobs/statements.
- Emit richer progress telemetry (e.g., per-chunk updates for large uploads) and expose metrics via a lightweight diagnostic tool.
- Consider removing or hardening the FastAPI stub to avoid confusion with the primary MCP transport.

---

Maintainer: Olivier Debeuf De Rijcker <olivier@markov.bot>
