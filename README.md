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

> **Version 0.3.1** - Latest release with issue #9 fix and enhanced MCP client compatibility.

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

- **MCP Protocol Support**: Implements the MCP protocol to allow LLMs to interact with Databricks
- **Databricks API Integration**: Provides access to Databricks REST API functionality
- **Tool Registration**: Exposes Databricks functionality as MCP tools
- **Async Support**: Built with asyncio for efficient operation

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
# With DATABRICKS_WAREHOUSE_ID set, warehouse_id is optional
await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10"
})

# You can still override the default warehouse
await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10",
    "warehouse_id": "sql_warehouse_specific"
})
```

### Workspace File Content Retrieval
```python
# Get JSON file content from workspace
await session.call_tool("get_workspace_file_content", {
    "path": "/Users/user@domain.com/config/settings.json"
})

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
├── AGENTS.md                        # Contributor guidelines (agents/LLM focus)
├── ARCHITECTURE.md                  # Deep architecture walkthrough
├── databricks_mcp/                  # Main package
│   ├── __init__.py                  # Package initialization
│   ├── __main__.py                  # Run via `python -m databricks_mcp`
│   ├── main.py                      # CLI/stdio launcher
│   ├── api/                         # Databricks API clients
│   │   ├── clusters.py              # Cluster management
│   │   ├── jobs.py                  # Job management
│   │   ├── notebooks.py             # Notebook operations
│   │   ├── sql.py                   # SQL execution
│   │   └── dbfs.py                  # DBFS operations
│   ├── core/                        # Core functionality
│   │   ├── auth.py                  # Authentication helpers
│   │   ├── config.py                # Settings and env loading
│   │   ├── logging_utils.py         # Centralized logging
│   │   └── utils.py                 # HTTP utilities & error helpers
│   ├── server/                      # MCP server implementation
│   │   ├── __main__.py              # Server entry point
│   │   ├── databricks_mcp_server.py # Main MCP server class
│   │   └── tool_helpers.py          # Shared response builders
│   └── cli/                         # Command-line interface
│       └── commands.py              # CLI commands
├── tests/                           # Test directory
│   ├── test_clusters.py             # Cluster tests
│   ├── test_mcp_server.py           # Server tests
│   └── test_*.py                    # Other test files
├── README.md                        # Project overview (this file)
├── TODO.md                          # Active refactor checklist
├── pyproject.toml                   # Package metadata
├── uv.lock                          # Dependency lock file
└── .gitignore                       # Git ignore rules
```

## Development

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — End-to-end component overview, resource flow, and integration details.
- [AGENTS.md](AGENTS.md) — Contributor guidelines and MCP agent conventions.

## Cross-Platform Notes

- `uvx databricks-mcp-server@latest` works on macOS, Linux, and Windows (PowerShell) without per-platform scripts.
- Tests run portably with `uv run pytest`; no shell-specific harnesses remain.
- Progress notifications and structured outputs follow the MCP spec, so clients on any OS receive the same responses.

### Code Standards

- Python code follows PEP 8 style guide with a maximum line length of 100 characters
- Use 4 spaces for indentation (no tabs)
- Use double quotes for strings
- All classes, methods, and functions should have Google-style docstrings
- Type hints are required for all code except tests

### Linting

The project uses the following linting tools:

```bash
# Run all linters
uv run pylint databricks_mcp/ tests/
uv run flake8 databricks_mcp/ tests/
uv run mypy databricks_mcp/
```

## Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests with our convenient script
.\scripts\run_tests.ps1

# Run with coverage report
.\scripts\run_tests.ps1 -Coverage

# Run specific tests with verbose output
.\scripts\run_tests.ps1 -Verbose -Coverage tests/test_clusters.py
```

You can also run the tests directly with pytest:

```bash
# Run all tests
uv run pytest tests/

# Run with coverage report
uv run pytest --cov=databricks_mcp tests/ --cov-report=term-missing
```

A minimum code coverage of 80% is the goal for the project.

## Documentation

- API documentation is generated using Sphinx and can be found in the `docs/api` directory
- All code includes Google-style docstrings
- See the `examples/` directory for usage examples

## Examples

Check the `examples/` directory for usage examples. To run examples:

```bash
# Run example scripts with uv
uv run examples/direct_usage.py
uv run examples/mcp_client_usage.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Ensure your code follows the project's coding standards
2. Add tests for any new functionality
3. Update documentation as necessary
4. Verify all tests pass before submitting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About

 A Model Completion Protocol (MCP) server for interacting with Databricks services. Maintained by markov.bot. 
