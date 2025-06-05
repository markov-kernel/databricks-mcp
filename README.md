# Databricks MCP Server

A Model Completion Protocol (MCP) server for Databricks that provides access to Databricks functionality via the MCP protocol. This allows LLM-powered tools to interact with Databricks clusters, jobs, notebooks, and more.

> **Version 0.2.0** - Latest release with improved package structure and organization.

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

### Workspace Files
- **list_notebooks**: List notebooks in a workspace directory
- **export_notebook**: Export a notebook from the workspace
- **get_workspace_file_content**: Retrieve content of any workspace file (JSON, notebooks, scripts, etc.)
- **get_workspace_file_info**: Get metadata about workspace files

### File System
- **list_files**: List files and directories in a DBFS path

### SQL Execution
- **execute_sql**: Execute a SQL statement (warehouse_id optional if DATABRICKS_WAREHOUSE_ID env var is set)

## 🎉 Recent Updates (v0.2.0)

**Major Package Refactoring:**
- ✅ **Cleaner imports**: Package renamed from `src` to `databricks_mcp` for better clarity
- ✅ **Organized structure**: Documentation and scripts moved to dedicated directories
- ✅ **Simplified root**: Cleaner project root with better organization
- ✅ **Same functionality**: All features work exactly the same, just with better structure

**Backwards Compatibility:** All MCP tools and functionality remain unchanged. Only the internal package structure has been improved.

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

3. Run the setup script:
   ```bash
   # Linux/Mac
   ./scripts/setup.sh
   
   # Windows (PowerShell)
   .\scripts\setup.ps1
   ```

   The setup script will:
   - Install `uv` if not already installed
   - Create a virtual environment
   - Install all project dependencies
   - Verify the installation works

   **Alternative manual setup:**
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
# Activate your virtual environment if not already active
source .venv/bin/activate 

# Run the start script (handles finding env vars from .env if needed)
./scripts/start_mcp_server.sh
```

This is useful for seeing direct output and logs.

### Integrating with AI Clients

To use this server with AI clients like Cursor or Claude CLI, you need to register it.

#### Cursor Setup

1.  Open your global MCP configuration file located at `~/.cursor/mcp.json` (create it if it doesn't exist).
2.  Add the following entry within the `mcpServers` object, replacing placeholders with your actual values and ensuring the path to `start_mcp_server.sh` is correct:

    ```json
    {
      "mcpServers": {
        // ... other servers ...
        "databricks-mcp-local": { 
          "command": "/absolute/path/to/your/project/databricks-mcp-server/start_mcp_server.sh",
          "args": [],
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

3.  **Important:** Replace `/absolute/path/to/your/project/databricks-mcp-server/` with the actual absolute path to this project directory on your machine.
4.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials.
5.  Save the file and **restart Cursor**.

6.  You can now invoke tools using `databricks-mcp-local:<tool_name>` (e.g., `databricks-mcp-local:list_jobs`).

#### Claude CLI Setup

1.  Use the `claude mcp add` command to register the server. Provide your credentials using the `-e` flag for environment variables and point the command to the `start_mcp_server.sh` script using `--` followed by the absolute path:

    ```bash
    claude mcp add databricks-mcp-local \
      -s user \
      -e DATABRICKS_HOST="https://your-databricks-instance.azuredatabricks.net" \
      -e DATABRICKS_TOKEN="dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
      -e DATABRICKS_WAREHOUSE_ID="sql_warehouse_12345" \
      -- /absolute/path/to/your/project/databricks-mcp-server/start_mcp_server.sh
    ```

2.  **Important:** Replace `/absolute/path/to/your/project/databricks-mcp-server/` with the actual absolute path to this project directory on your machine.
3.  Replace the `DATABRICKS_HOST` and `DATABRICKS_TOKEN` values with your credentials.

4.  You can now invoke tools using `databricks-mcp-local:<tool_name>` in your Claude interactions.

## Querying Databricks Resources

The repository includes utility scripts to quickly view Databricks resources:

```bash
# View all clusters
uv run scripts/show_clusters.py

# View all notebooks
uv run scripts/show_notebooks.py
```

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
    "workspace_path": "/Users/user@domain.com/config/settings.json"
})

# Get notebook content in Jupyter format
await session.call_tool("get_workspace_file_content", {
    "workspace_path": "/Users/user@domain.com/my_notebook",
    "format": "JUPYTER"
})

# Get file metadata without downloading content
await session.call_tool("get_workspace_file_info", {
    "workspace_path": "/Users/user@domain.com/large_file.py"
})
```

## Project Structure

```
databricks-mcp/
├── databricks_mcp/                  # Main package (renamed from src/)
│   ├── __init__.py                  # Package initialization
│   ├── __main__.py                  # Main entry point for the package
│   ├── main.py                      # Entry point for the MCP server
│   ├── api/                         # Databricks API clients
│   │   ├── clusters.py              # Cluster management
│   │   ├── jobs.py                  # Job management
│   │   ├── notebooks.py             # Notebook operations
│   │   ├── sql.py                   # SQL execution
│   │   └── dbfs.py                  # DBFS operations
│   ├── core/                        # Core functionality
│   │   ├── config.py                # Configuration management
│   │   ├── auth.py                  # Authentication
│   │   └── utils.py                 # Utilities
│   ├── server/                      # Server implementation
│   │   ├── __main__.py              # Server entry point
│   │   ├── databricks_mcp_server.py # Main MCP server
│   │   └── app.py                   # FastAPI app for tests
│   └── cli/                         # Command-line interface
│       └── commands.py              # CLI commands
├── tests/                           # Test directory
│   ├── test_clusters.py             # Cluster tests
│   ├── test_mcp_server.py           # Server tests
│   └── test_*.py                    # Other test files
├── scripts/                         # Helper scripts (organized)
│   ├── start_mcp_server.ps1         # Server startup script (Windows)
│   ├── start_mcp_server.sh          # Server startup script (Unix)
│   ├── run_tests.ps1                # Test runner script (Windows)
│   ├── run_tests.sh                 # Test runner script (Unix)
│   ├── setup.ps1                    # Setup script (Windows)
│   ├── setup.sh                     # Setup script (Unix)
│   ├── show_clusters.py             # Script to show clusters
│   ├── show_notebooks.py            # Script to show notebooks
│   ├── setup_codespaces.sh          # Codespaces setup
│   └── test_setup_local.sh          # Local test setup
├── examples/                        # Example usage
│   ├── direct_usage.py              # Direct usage examples
│   └── mcp_client_usage.py          # MCP client examples
├── docs/                            # Documentation (organized)
│   ├── AGENTS.md                    # Agent documentation
│   ├── project_structure.md         # Detailed structure docs
│   ├── new_features.md              # Feature documentation
│   └── phase1.md                    # Development phases
├── .gitignore                       # Git ignore rules
├── .cursor.json                     # Cursor configuration
├── pyproject.toml                   # Package configuration
├── uv.lock                          # Dependency lock file
└── README.md                        # This file
```

See `docs/project_structure.md` for a more detailed view of the project structure.

## Development

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