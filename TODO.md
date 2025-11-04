# TODO

## A. Audit STDIO Discipline ✅
- Configure centralized logging to emit JSON lines on `stderr` and ensure the server main entry point reconfigures stdout buffering without writing log output.

## B. Block Dotenv Prints ✅
- Loading `.env` now happens silently when available, preventing accidental stdout contamination during startup.

## C. Centralize Logging Configuration ✅
- Introduced `databricks_mcp/core/logging_utils.py` to standardize JSON logging, replacing previous scattered `logging.basicConfig` usage.

## D. Deconflict Version Constants ✅
- `settings.VERSION` now matches `pyproject.toml`, and all entry points use that single source of truth.

## E. Evaluate Entry Points ✅
- `python -m databricks_mcp.server` and CLI `start` delegate to the synchronous server `main()` without redundant `asyncio.run` wrappers; `databricks_mcp.main` centralizes asynchronous startup.

## F. Flatten Parameter Compatibility ✅
- Tool signatures now take explicit, flat arguments (powered by Pydantic models where applicable), eliminating the legacy nested `params` shim.

## G. Generate Tool Schemas ✅
- Typed tool signatures allow FastMCP to emit precise JSON Schemas; new models such as `ClusterConfig` ensure richer validation.

## H. Handle Structured Outputs ✅
- Tool executions return `CallToolResult` objects with concise text summaries and full structured payloads, replacing double-JSON responses.

## I. Implement Resource Registry ✅
- Added an in-memory resource cache exposed via `resource://databricks/exports/{id}` URIs for notebook and workspace exports, advertising the handles through `_meta['resources']`.

## J. Join Cancellation Hooks ✅
- `_run_tool` now watches for `asyncio.CancelledError`, returning a structured cancellation response and updating per-tool metrics.

## K. Keep Error Taxonomy Consistent ✅
- Centralized `_run_tool` maps protocol errors to JSON-RPC failures and wraps Databricks errors in structured `CallToolResult` envelopes with status codes.

## L. Limit Concurrency & Add Backoff ✅
- Introduced per-server semaphores, `asyncio.wait_for` timeouts, and HTTP retry w/ exponential backoff driven by new settings.

## M. Monitor with Correlation IDs ✅
- Propagate per-request IDs via contextvars into logs, Databricks headers, and tool responses (`_meta['_request_id']`).

## N. Normalize UV Packaging & Docs ✅
- README now promotes `uvx databricks-mcp-server@latest`, including CLI flag guidance, replacing all references to legacy shell/PowerShell scripts.

## O. Overhaul Test Harness ✅
- Replaced PowerShell-based tests with pytest suites that monkeypatch API calls and assert structured `CallToolResult` behavior.

## P. Prepare Golden Protocol Tests ✅
- Added `tests/test_transcript.py` to capture a deterministic request/response pair, acting as a golden transcript for structured output validation.

## Q. Qualify CLI for Structured Responses ✅
- CLI `sync-run` command now inspects `CallToolResult`, surfaces summaries, and pretty-prints structured payloads.

## R. Revise README & Contributor Docs ✅
- README documents structured outputs, Codex/Claude setup via `uvx`, and links directly to `ARCHITECTURE.md` and `AGENTS.md`.

## S. Synchronize Architecture Narrative ✅
- `ARCHITECTURE.md` now captures flat parameters, structured outputs, resource links, and the new concurrency/backoff pipeline.

## T. Triage Legacy Script References ✅
- Purged stale script references (start/setup/test) from docs in favor of portable `uvx` workflows.

## U. Upgrade Environment Handling ✅
- `.env` loading no longer prints, and the server now warns when required `DATABRICKS_*` variables retain placeholder values.

## V. Validate Deprecation Timeline ✅
- README now flags the flat-argument/structured-output change; code emits warnings when credentials are missing and remnants of legacy paths have been removed.

## W. Wire Progress Notifications ✅
- Server broadcasts start/finish progress events (with mid-phase updates for composite tools) via `ctx.report_progress`.

## X. X-Check Cross-Platform Support ✅
- README documents `uvx` workflows and portable testing instructions; legacy shell/PowerShell launchers removed.

## Y. Yield Metrics & Health Signals ✅
- `_run_tool` maintains per-tool counters and logs structured success/error events retrievable via `get_metrics_snapshot()`.

## Z. Zero Out Double-JSON Fallback ✅
- Response flow now emits direct `CallToolResult` objects and legacy `_unwrap_params` handling has been removed.
