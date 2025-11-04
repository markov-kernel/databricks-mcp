<div align="center">

### 🤖 **Built by [Markov](https://markov.bot)** 
**When AI changes everything, you start from scratch.**

*Markov specializes in cutting-edge AI solutions and automation. From neural ledgers to MCP servers,  
we're building the tools that power the next generation of AI-driven applications.*

💼 **We're always hiring exceptional engineers!** Join us in shaping the future of AI.

**[🌐 Visit markov.bot](https://markov.bot) • [✉️ Get in Touch](mailto:olivier@markov.bot) • [🚀 Careers](mailto:olivier@markov.bot?subject=Engineering%20Career%20Opportunity)**

</div>

<br>

# Databricks MCP Server

A Model Completion Protocol (MCP) server for Databricks that provides access to Databricks functionality via the MCP protocol. This allows LLM-powered tools to interact with Databricks clusters, jobs, notebooks, and more.

> **Version 0.4.0** - Structured MCP responses, resource caching, and resilience upgrades.

## 🚀 One-Click Install

### For Cursor Users
**Click this link to install instantly:**
```
cursor://anysphere.cursor-deeplink/mcp/install?name=databricks-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJkYXRhYnJpY2tzLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7IkRBVEFCUklDS1NfSE9TVCI6IiR7REFUQUJSSUNLU19IT1NUfSIsIkRBVEFCUklDS1NfVE9LRU4iOiIke0RBVEFCUklDS1NfVE9LRU59IiwiREFUQUJSSUNLU19XQVJFSE9VU0VfSUQiOiIke0RBVEFCUklDS1NfV0FSRUhPVVNFX0lEfSJ9fQ==
```

**Or copy and paste this deeplink:**
`cursor://anysphere.cursor-deeplink/mcp/install?name=databricks-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJkYXRhYnJpY2tzLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7IkRBVEFCUklDS1NfSE9TVCI6IiR7REFUQUJSSUNLU19IT1NUfSIsIkRBVEFCUklDS1NfVE9LRU4iOiIke0RBVEFCUklDS1NfVE9LRU59IiwiREFUQUJSSUNLU19XQVJFSE9VU0VfSUQiOiIke0RBVEFCUklDS1NfV0FSRUhPVVNFX0lEfSJ9fQ==`

**[→ Install Databricks MCP in Cursor ←](cursor://anysphere.cursor-deeplink/mcp/install?name=databricks-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJkYXRhYnJpY2tzLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7IkRBVEFCUklDS1NfSE9TVCI6IiR7REFUQUJSSUNLU19IT1NUfSIsIkRBVEFCUklDS1NfVE9LRU4iOiIke0RBVEFCUklDS1NfVE9LRU59IiwiREFUQUJSSUNLU19XQVJFSE9VU0VfSUQiOiIke0RBVEFCUklDS1NfV0FSRUhPVVNFX0lEfSJ9fQ==)**

This project is maintained by Olivier Debeuf De Rijcker <olivier@markov.bot>.

Credit for the initial version goes to [@JustTryAI](https://github.com/JustTryAI/databricks-mcp-server).

## Features

- **Structured MCP Responses**: Tools return `CallToolResult` objects with summaries in `content` and full payloads in `_meta['data']`.
- **Resource Caching**: Large exports (workspace files, notebooks) are stored once and exposed as `resource://databricks/exports/{id}` URIs under `_meta['resources']`.
- **Progress & Metrics**: Long-running tools stream MCP progress notifications and track per-tool success/error counters.
- **Resilient Networking**: Shared HTTP client adds request IDs, timeout controls, and exponential backoff for retryable Databricks errors.
- **Async MCP Runtime**: Built atop `mcp.server.FastMCP` for stdio transport with centralized JSON logging.

## Available Tools

The Databricks MCP Server exposes the following tools:

### Cluster Management
- **list_clusters**: List all Databricks clusters
- **create_cluster**: Create a new Databricks cluster
- **terminate_cluster**: Terminate a Databricks cluster
- **get_cluster**: Get information about a specific Databricks cluster
- **start_cluster**: Start a terminated Databricks cluster

### Job Management
- **list_jobs**: List all Databricks jobs
- **run_job**: Run a Databricks job
- **run_notebook**: Submit and wait for a one-time notebook run
- **create_job**: Create a new Databricks job
- **delete_job**: Delete a Databricks job
- **get_run_status**: Get status information for a job run
- **list_job_runs**: List recent runs for a job
- **cancel_run**: Cancel a running job

### Workspace Files
- **list_notebooks**: List notebooks in a workspace directory
- **export_notebook**: Export a notebook from the workspace
- **import_notebook**: Import a notebook into the workspace
- **delete_workspace_object**: Delete a notebook or directory
- **get_workspace_file_content**: Retrieve content of any workspace file (JSON, notebooks, scripts, etc.)
- **get_workspace_file_info**: Get metadata about workspace files

### File System
- **list_files**: List files and directories in a DBFS path
- **dbfs_put**: Upload a small file to DBFS
- **dbfs_delete**: Delete a DBFS file or directory

### Cluster Libraries
- **install_library**: Install libraries on a cluster
- **uninstall_library**: Remove libraries from a cluster
- **list_cluster_libraries**: Check installed libraries on a cluster

### Repos
- **create_repo**: Clone a Git repository
- **update_repo**: Update an existing repo
- **list_repos**: List repos in the workspace
- **pull_repo**: Pull the latest commit for a Databricks repo

### Unity Catalog
- **list_catalogs**: List catalogs
- **create_catalog**: Create a catalog
- **list_schemas**: List schemas in a catalog
- **create_schema**: Create a schema
- **list_tables**: List tables in a schema
- **create_table**: Execute a CREATE TABLE statement
- **get_table_lineage**: Fetch lineage information for a table

### Composite
- **sync_repo_and_run_notebook**: Pull a repo and execute a notebook in one call

### SQL Execution
- **execute_sql**: Execute a SQL statement (optional `warehouse_id`, `catalog`, `schema_name`)

## 🎉 Recent Updates

**Structured Output Refresh (current)**
- ✅ **Typed MCP Schemas**: Tools expose precise input schemas using FastMCP's metadata (no `{ "params": ... }` envelope).
- ✅ **Structured Results**: Each tool now returns `CallToolResult` with a concise text summary and the full Databricks payload in `_meta['data']`.
- ✅ **Resource URIs for Large Payloads**: Notebook/workspace exports stash `resource://databricks/exports/{id}` entries in `_meta['resources']` instead of embedding large blobs.
- ✅ **Resilience Improvements**: Per-tool concurrency limits, timeouts, and retry-with-backoff for transient Databricks errors.
- ✅ **Progress & Telemetry**: Tools publish MCP progress notifications and surface `_meta._request_id` plus per-tool success/error counters for easier observability.
- ✅ **Correlation IDs**: All API requests and tool responses carry `_meta._request_id` for traceability.

**v0.3.0 Highlights**
- ✅ **Repository Management**: Pull latest commits from Databricks repos with `pull_repo`.
- ✅ **One-time Notebook Execution**: Submit and wait for notebook runs with `run_notebook`.
- ✅ **Composite Operations**: Combined repo sync + notebook execution with `sync_repo_and_run_notebook`.
- ✅ **Enhanced Job Management**: Extended job APIs with submit, status checking, and run management.

**Previous Updates:**
- **v0.2.1**: Enhanced Codespaces support, documentation improvements, publishing process streamlining
- **v0.2.0**: Major package refactoring from `src/` to `databricks_mcp/` structure

**Backwards Compatibility:** Breaking change alert — tools now require flat arguments and emit structured responses; update custom clients accordingly.

## Installation

### Quick Install (Recommended)

Use the link above to install with one click:

**[→ Install Databricks MCP in Cursor ←](cursor://anysphere.cursor-deeplink/mcp/install?name=databricks-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJkYXRhYnJpY2tzLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7IkRBVEFCUklDS1NfSE9TVCI6IiR7REFUQUJSSUNLU19IT1NUfSIsIkRBVEFCUklDS1NfVE9LRU4iOiIke0RBVEFCUklDS1NfVE9LRU59IiwiREFUQUJSSUNLU19XQVJFSE9VU0VfSUQiOiIke0RBVEFCUklDS1NfV0FSRUhPVVNFX0lEfSJ9fQ==)**

This will automatically install the MCP server using `uvx` and configure it in Cursor. You'll need to set these environment variables:

- `DATABRICKS_HOST` - Your Databricks workspace URL
- `DATABRICKS_TOKEN` - Your Databricks personal access token  
- `DATABRICKS_WAREHOUSE_ID` - (Optional) Your default SQL warehouse ID

### Manual Installation

#### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended for MCP servers)

### Setup

1. Install `uv` if you don't have it already:

   ```bash
   # MacOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (in PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   ```

   Restart your terminal after installation.

2. Clone the repository:
   ```bash
   git clone https://github.com/markov-kernel/databricks-mcp.git
   cd databricks-mcp
   ```

3. Create a virtual environment (optional) and install dependencies for local development:
   ```bash
   # Create and activate virtual environment
   uv venv
   
   # On Windows
   .\.venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies in development mode
   uv pip install -e .
   
   # Install development dependencies
   uv pip install -e ".[dev]"
   ```

4. Set up environment variables:
   ```bash
   # Required variables
   # Windows
   set DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   set DATABRICKS_TOKEN=your-personal-access-token
   
   # Linux/Mac
   export DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net
   export DATABRICKS_TOKEN=your-personal-access-token
   
   # Optional: Set default SQL warehouse (makes warehouse_id optional in execute_sql)
   export DATABRICKS_WAREHOUSE_ID=sql_warehouse_12345
   ```

   You can also create an `.env` file based on the `.env.example` template.

## Running the MCP Server

### Standalone

To start the MCP server directly for testing or development, run:

```bash
uvx databricks-mcp-server@latest
```

> Tip: add `--refresh` (for example `uvx databricks-mcp-server@latest --refresh`) to force-install the newest release after publishing.

Pass `--log-level DEBUG` or other options using standard CLI flags:

```bash
uvx databricks-mcp-server@latest -- --log-level DEBUG
```

### Integrating with AI Clients

To use this server with AI clients like Cursor or Claude CLI, you need to register it.

#### Cursor Setup

1.  Open your global MCP configuration file located at `~/.cursor/mcp.json` (create it if it doesn't exist).
2.  Add the following entry within the `mcpServers` object, replacing placeholders with your actual values:

    ```json
    {
      "mcpServers": {
        // ... other servers ...
        "databricks-mcp-local": { 
          "command": "uvx",
          "args": ["databricks-mcp-server@latest"],
          "env": {
            "DATABRICKS_HOST": "https://your-databricks-instance.azuredatabricks.net", 
            "DATABRICKS_TOKEN": "dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "DATABRICKS_WAREHOUSE_ID": "sql_warehouse_12345",
            "RUNNING_VIA_CURSOR_MCP": "true" 
          }
        }
        // ... other servers ...
      }
    }
    ```

3.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials, then **restart Cursor**.
4.  You can now invoke tools using `databricks-mcp-local:<tool_name>` (e.g., `databricks-mcp-local:list_jobs`).

#### Claude CLI Setup

1.  Use the `claude mcp add` command to register the server. Provide your credentials using the `-e` flag for environment variables and point the command to `uvx databricks-mcp-server@latest`:

    ```bash
    claude mcp add databricks-mcp-local \
      -s user \
      -e DATABRICKS_HOST="https://your-databricks-instance.azuredatabricks.net" \
      -e DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
      -e DATABRICKS_WAREHOUSE_ID="sql_warehouse_12345" \
      -- uvx databricks-mcp-server@latest
    ```

2.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials.
3.  You can now invoke tools using `databricks-mcp-local:<tool_name>` in your Claude interactions.

## Usage Examples

### SQL Execution with Default Warehouse
```python
result = await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10"
})

print(result.content[0].text)  # Human summary from the server
rows = (result.meta or {}).get("data", {}).get("result", [])
print(rows)

# Override the default warehouse if needed
await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10",
    "warehouse_id": "sql_warehouse_specific"
})
```

### Workspace File Content Retrieval
```python
# Get JSON file content from workspace (resource cached server-side)
result = await session.call_tool("get_workspace_file_content", {
    "path": "/Users/user@domain.com/config/settings.json"
})

resource_uri = (result.meta or {}).get("resources", [{}])[0].get("uri")
if resource_uri:
    contents = await session.read_resource(resource_uri)

# Get notebook content in Jupyter format
await session.call_tool("get_workspace_file_content", {
    "path": "/Users/user@domain.com/my_notebook",
    "format": "JUPYTER"
})

# Get file metadata without downloading content
await session.call_tool("get_workspace_file_info", {
    "path": "/Users/user@domain.com/large_file.py"
})
```

### Repo Sync and Notebook Execution
```python
await session.call_tool("sync_repo_and_run_notebook", {
    "repo_id": 123,
    "notebook_path": "/Repos/user/project/run_me"
})
```

### Create Nightly ETL Job
```python
job_conf = {
    "name": "Nightly ETL",
    "tasks": [
        {
            "task_key": "etl",
            "notebook_task": {"notebook_path": "/Repos/me/etl.py"},
            "existing_cluster_id": "abc-123"
        }
    ]
}
await session.call_tool("create_job", job_conf)
```

## Project Structure

```
databricks-mcp/
├── AGENTS.md                        # Contributor guide (MCP agent focus)
├── ARCHITECTURE.md                  # Deep architecture walkthrough
├── README.md                        # Project overview (this file)
├── TODO.md                          # Active refactor checklist
├── databricks_mcp/                  # Main package
│   ├── api/                         # Databricks REST wrappers
│   ├── cli/commands.py              # CLI entry points
│   ├── core/                        # Settings, logging, models, utils
│   └── server/                      # FastMCP server implementation
├── docs/                            # Historical docs (kept for reference)
├── tests/                           # Pytest suites (mocked, no shell scripts)
├── pyproject.toml                   # Package metadata (v0.4.0)
├── uv.lock                          # Locked dependency versions
└── .env.example                     # Environment variable template
```

## Development

- Format with Black: `uv run black databricks_mcp tests`
- Lint with Pylint: `uv run pylint databricks_mcp tests`
- Run tests locally: `uv run pytest`
- Build distributables: `uv build`
- Publish (requires `PYPI_TOKEN`): `uv publish --token "$PYPI_TOKEN"`

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [AGENTS.md](AGENTS.md)
- [TODO.md](TODO.md)

## Cross-Platform Notes

- `uvx databricks-mcp-server@latest` works on macOS, Linux, and Windows.
- All examples assume environment variables are set or provided by the host (Cursor, Claude, etc.).

## Testing

```bash
uv run pytest
```

## License

Released under the MIT License. See [LICENSE](LICENSE).
