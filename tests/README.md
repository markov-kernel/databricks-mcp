# Tests for Databricks MCP Server

This directory contains automated tests for the Databricks MCP server. The
suite is written in `pytest` and relies on `uv` for dependency and virtualenv
management.

## Layout

- `test_additional_features.py` – smoke tests for auxiliary Databricks features
  (repos, workspace listings, etc.).
- `test_clusters.py` – CRUD and lifecycle coverage for cluster-oriented tools.
- `test_tool_metadata.py` – asserts that every registered tool exposes the
  expected description, schema metadata, and argument signatures.
- `test_server_structured.py` – validates that tool responses populate
  `structuredContent`, include human-readable text summaries, and surface
  resource links for large artifacts.
- `test_transcript.py` – golden transcript of a `tools/list` and representative
  `tools/call` interaction to guard against protocol regressions.

All tests are async-friendly and do not require live Databricks credentials;
HTTP calls are mocked.

## Running the Test Suite

From the repository root:

```bash
uv run pytest
```

The command above automatically creates an ephemeral virtual environment (if
needed), installs the `dev` extras, and executes every test module in this
directory. The suite completes in under a second on a typical laptop.

## Adding New Tests

1. Create a new `test_*.py` file in this directory and use `pytest` naming
   conventions for functions/classes.
2. Prefer fixtures from `tests/__init__.py` when mocking Databricks responses or
   seeding tool contexts.
3. Keep protocol-level assertions (structured content shape, resource links,
   progress notifications) close to the server modules they cover.
4. Run `uv run pytest` locally before opening a pull request and update this
   README if you add significant new suites or fixtures.
