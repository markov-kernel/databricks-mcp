# Repository Guidelines

## Core Conventions
- Use `kebab-case` for every file and directory.
- Prefer `def` functions over lambdas; annotate parameters and returns.
- Represent collections with `list[T]`; keep hints current.
- Follow idiomatic Python (PEP 8, docstrings).
- Put reusable modules in `components/` packages (for example `components/mcp`, `components/databricks_mcp`); compose rather than duplicate.
- Validate inputs with `pydantic` models named `SomethingSchema`.
- Manage environments exclusively with `uv` (`uv venv`, `uv pip sync`, `uv run`).
- never use dynamic imports (unless asked to) like `await import(..)`
- never cast to `any`
- do not add extra defensive checks or try/catch blocks

## File Length
- Stay under 400 lines per file; extract helpers into `components/` or `tools/` early.

## Reading Files
- Read each file before editing and stage only code reviewed line by line.

## Ego
- Surface two implementation options, invite critique, and back decisions with evidence.

## Project Structure & Module Organization
The MCP runtime lives in `databricks_mcp/`, with `core/` for shared config and auth models, `api/` wrapping Databricks REST endpoints, `server/` exposing MCP tool handlers, and `cli/` providing command-line surfaces. `main.py` is the FastMCP entry point. Tests reside in `tests/`, mirroring server and API modules, and `ARCHITECTURE.md` gives a deeper component walkthrough.

## Build, Test, and Development Commands
- `uv pip install -e . && uv pip install -e ".[dev]"` sets up editable installs plus dev extras.
- `uvx databricks-mcp-server@latest` launches the MCP server over STDIO for local integration.
- `uv run databricks-mcp -- --help` lists CLI commands before manual smoke checks.
- `uv run pytest` executes the asynchronous test suite with verbose, short tracebacks.
- `uv run black .` and `uv run pylint databricks_mcp tests` enforce formatting and linting before submission.

## Coding Style & Naming Conventions
Write Python 3.10+ with 4-space indentation and Black defaults (88-character lines). Use type hints on public interfaces; keep modules and files in `snake_case`, classes in `PascalCase`, and MCP tool identifiers in lower snake (`list_clusters`). Return `CallToolResult` objects with concise `TextContent` summaries and stash structured payloads under `_meta['data']` (including `_meta['_request_id']`). For large artifacts, append resource references using the server cache helpers.

## Testing Guidelines
Pytest is configured via `pyproject.toml` (`asyncio_mode = auto`). Name files `test_*.py` and let pytest-asyncio manage async cases; mark slow or external tests explicitly. Mock Databricks REST helpers so tests remain offline-only, and assert that `_meta['data']` and optional `_meta['resources']` entries are populated as expected.

## Commit & Pull Request Guidelines
Use descriptive, sentence-case commit titles similar to `Release v0.3.1` or “Remove deprecated files…”. Reference issues with `Fixes #<id>` and keep body text wrapped near 72 columns. Pull requests should summarize scope, list impacted tools or modules, mention required environment variables, and include logs or CLI captures when behavior changes. Run the commands above and attach results when relevant.

## Security & Configuration Tips
Store secrets in `.env` (see `.env.example`) and exclude them from commits. Required variables: `DATABRICKS_HOST` and `DATABRICKS_TOKEN`; optionally set `DATABRICKS_WAREHOUSE_ID` for SQL defaults. Logs write to `databricks_mcp.log` in the working directory—clean or rotate before sharing artifacts.
