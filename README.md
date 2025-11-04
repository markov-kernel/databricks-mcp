# Databricks MCP Server

A production-ready Model Completion Protocol (MCP) server that exposes Databricks REST capabilities to MCP-compatible agents and tooling. Version **0.4.1** introduces structured responses, resource caching, retry-aware networking, and end-to-end resilience improvements.

---

## Table of Contents
1. [Key Capabilities](#key-capabilities)
2. [Architecture Highlights](#architecture-highlights)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Server](#running-the-server)
6. [Integrating with MCP Clients](#integrating-with-mcp-clients)
7. [Working with Tool Responses](#working-with-tool-responses)
8. [Available Tools](#available-tools)
9. [Development Workflow](#development-workflow)
10. [Testing](#testing)
11. [Publishing Builds](#publishing-builds)
12. [Support & Contact](#support--contact)
13. [License](#license)

---

## Key Capabilities
- **Structured MCP Responses** – Each tool returns a `CallToolResult` with human-readable summaries in `content` and machine-readable payloads in `_meta['data']`.
- **Resource Caching** – Large notebook/workspace exports are cached once and exposed as `resource://databricks/exports/{id}` entries under `_meta['resources']`.
- **Progress & Metrics** – Long-running actions stream MCP progress notifications and track per-tool success/error/timeout/cancel metrics.
- **Resilient Networking** – Shared HTTP client injects request IDs, enforces timeouts, and retries retryable Databricks responses (408/429/5xx) with exponential backoff.
- **Async Runtime** – Built on `mcp.server.FastMCP` with centralized JSON logging and concurrency guards for predictable stdio behaviour.

## Architecture Highlights
- `databricks_mcp/server/databricks_mcp_server.py` – FastMCP server with tool registration, progress handling, metrics, and resource caching.
- `databricks_mcp/core/utils.py` – HTTP utilities with correlation IDs, retries, and error mapping to `DatabricksAPIError`.
- `databricks_mcp/core/logging_utils.py` – JSON logging configuration for stderr/file outputs.
- `databricks_mcp/core/models.py` – Pydantic models (e.g., `ClusterConfig`) used by tool schemas.
- Tests under `tests/` mock Databricks APIs to validate orchestration, structured responses, and schema metadata without shell scripts.

For an in-depth tour of data flow and design decisions, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Installation

### Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) for dependency management and publishing

### Quick Install (recommended)
Register the server with Cursor using the deeplink below – it resolves to `uvx databricks-mcp-server@latest` and picks up future updates automatically.

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=databricks-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJkYXRhYnJpY2tzLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7IkRBVEFCUklDS1NfSE9TVCI6IiR7REFUQUJSSUNLU19IT1NUfSIsIkRBVEFCUklDS1NfVE9LRU4iOiIke0RBVEFCUklDS1NfVE9LRU59IiwiREFUQUJSSUNLU19XQVJFSE9VU0VfSUQiOiIke0RBVEFCUklDS1NfV0FSRUhPVVNFX0lEfSJ9fQ==
```

### Manual Installation
```bash
# Clone and enter the repository
git clone https://github.com/markov-kernel/databricks-mcp.git
cd databricks-mcp

# Create an isolated environment (optional but recommended)
uv venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scriptsctivate  # Windows PowerShell

# Install package and development dependencies
uv pip install -e .
uv pip install -e ".[dev]"
```

## Configuration
Set the following environment variables (or populate `.env` from `.env.example`).

```bash
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXX"
export DATABRICKS_WAREHOUSE_ID="sql_warehouse_12345"  # optional default
export TOOL_TIMEOUT_SECONDS=300
export MAX_CONCURRENT_REQUESTS=8
export HTTP_TIMEOUT_SECONDS=60
export API_MAX_RETRIES=3
export API_RETRY_BACKOFF_SECONDS=0.5
```

## Running the Server
```bash
uvx databricks-mcp-server@latest
```
> Tip: append `--refresh` (e.g., `uvx databricks-mcp-server@latest --refresh`) to force `uv` to resolve the latest PyPI release after publishing.

To adjust logging:
```bash
uvx databricks-mcp-server@latest -- --log-level DEBUG
```

## Integrating with MCP Clients

### Cursor
```jsonc
{
  "mcpServers": {
    "databricks-mcp-local": {
      "command": "uvx",
      "args": ["databricks-mcp-server@latest"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.databricks.com",
        "DATABRICKS_TOKEN": "dapiXXXXXXXXXXXXXXXX",
        "DATABRICKS_WAREHOUSE_ID": "sql_warehouse_12345",
        "RUNNING_VIA_CURSOR_MCP": "true"
      }
    }
  }
}
```
Restart Cursor after saving. Invoke tools as `databricks-mcp-local:<tool>`.

### Claude CLI
```bash
claude mcp add databricks-mcp-local   -s user   -e DATABRICKS_HOST="https://your-workspace.databricks.com"   -e DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXX"   -e DATABRICKS_WAREHOUSE_ID="sql_warehouse_12345"   -- uvx databricks-mcp-server@latest
```

## Working with Tool Responses
Structured payloads live in `_meta['data']`; large resources are referenced in `_meta['resources']`.

```python
result = await session.call_tool("list_clusters", {})
summary = next((block.text for block in result.content if getattr(block, "type", "") == "text"), "")
clusters = (result.meta or {}).get("data", {}).get("clusters", [])
resources = (result.meta or {}).get("resources", [])
```

### Example – SQL Query
```python
result = await session.call_tool("execute_sql", {"statement": "SELECT * FROM samples LIMIT 10"})
print(result.content[0].text)
rows = (result.meta or {}).get("data", {}).get("result", [])
```

### Example – Workspace File Export
```python
result = await session.call_tool("get_workspace_file_content", {
    "path": "/Users/user@domain.com/report.ipynb",
    "format": "SOURCE"
})
resource_uri = (result.meta or {}).get("resources", [{}])[0].get("uri")
if resource_uri:
    contents = await session.read_resource(resource_uri)
```

## Available Tools
| Category | Tool | Description |
| --- | --- | --- |
| Clusters | `list_clusters`, `create_cluster`, `terminate_cluster`, `get_cluster`, `start_cluster` | Manage interactive clusters |
| Jobs | `list_jobs`, `create_job`, `run_job`, `run_notebook`, `sync_repo_and_run_notebook`, `get_run_status`, `list_job_runs`, `cancel_run` | Manage scheduled and ad-hoc jobs |
| Workspace | `list_notebooks`, `export_notebook`, `import_notebook`, `delete_workspace_object`, `get_workspace_file_content`, `get_workspace_file_info` | Inspect and manage workspace assets |
| DBFS | `list_files`, `dbfs_put`, `dbfs_delete` | Explore DBFS and manage files |
| SQL | `execute_sql` | Submit SQL statements with optional `warehouse_id`, `catalog`, `schema_name` |
| Libraries | `install_library`, `uninstall_library`, `list_cluster_libraries` | Manage cluster libraries |
| Repos | `create_repo`, `update_repo`, `list_repos`, `pull_repo` | Manage Databricks repos |
| Unity Catalog | `list_catalogs`, `create_catalog`, `list_schemas`, `create_schema`, `list_tables`, `create_table`, `get_table_lineage` | Unity Catalog operations |

## Development Workflow
```bash
uv run black databricks_mcp tests
uv run pylint databricks_mcp tests
uv run pytest
uv build
uv publish --token "$PYPI_TOKEN"
```

## Testing
```bash
uv run pytest
```
Pytest suites mock Databricks APIs, providing deterministic structured outputs and transcript tests.

## Publishing Builds
Ensure `PYPI_TOKEN` is available (via `.env` or environment) before publishing:
```bash
uv build
uv publish --token "$PYPI_TOKEN"
```

## Support & Contact
- Maintainer: Olivier Debeuf De Rijcker (olivier@markov.bot)
- Issues: [GitHub Issues](https://github.com/markov-kernel/databricks-mcp/issues)
- Architecture deep dive: [ARCHITECTURE.md](ARCHITECTURE.md)

## License

Released under the MIT License. See [LICENSE](LICENSE).
