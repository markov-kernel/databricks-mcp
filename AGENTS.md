# Repository Guidelines

## 1. Core Philosophy

Our development is guided by a few key principles. Always consider these when making design decisions.

-   **Simplicity and Pragmatism**: Prefer simple, explicit, and readable solutions. If a complex design pattern isn't immediately necessary, don't implement it. Code should be easy to delete.
-   **Compose, Don't Duplicate**: Encapsulate reusable logic into `components/` modules. Build complex features by composing these smaller, independent units. This improves testability and maintainability.
-   **Stateless by Default**: Design tools and components to be stateless whenever possible. State adds significant complexity to testing, reasoning, and scaling. Pass state explicitly as parameters rather than relying on side effects or implicit context.
-   **Fail Fast and Loud**: Don't swallow errors. Let exceptions propagate up to a centralized handler. This makes bugs immediately obvious and debugging far simpler. Avoid defensive `try/except` blocks deep within application logic.

## 2. Code Conventions & Style

Consistency is key to a readable and maintainable codebase.

-   **File and Directory Naming**: Use `kebab-case` for all files and directories (e.g., `databricks-api.py`, `utils/`).
-   **Function Definitions**: Always prefer `def` functions over `lambda`. `def` provides a name for debugging, supports docstrings, and allows for proper type annotation.
-   **Type Hinting**:
    -   Annotate all function parameters and return types. Use Python 3.10+ syntax (e.g., `list[str]` instead of `List[str]`).
    -   Never cast to `Any`. If you must use it, use `typing.cast` with a clear comment explaining why no stricter type is available.
    -   Represent collections with standard types like `list[T]`, `dict[K, V]`, and `set[T]`.
-   **Input Validation**: Use `pydantic` models for validating the structure and types of external inputs (e.g., API requests, tool arguments).
    -   Name schemas with a `Schema` suffix (e.g., `CreateClusterSchema`).
    -   Keep Pydantic models as pure data contracts. Avoid adding business logic or complex methods to them.
-   **Imports**: Use absolute imports for project modules. Never use dynamic imports like `importlib.import_module` or `await import(...)` unless it's a core requirement of a plug-in system.
-   **Formatting**: Follow PEP 8, enforced by Black with a line length of 88 characters and 4-space indentation.

## 3. Project Structure & Modularity

A clear structure makes the system easier to navigate and understand.

-   **`databricks_mcp/`**: The primary application package.
    -   **`core/`**: Shared Pydantic models, custom exception classes, and authentication logic. This code should be generic and application-agnostic.
    -   **`api/`**: Thin, stateless clients for external REST APIs (e.g., Databricks). This layer is responsible for HTTP requests, authentication, and translating API errors into well-defined exceptions. It should not contain any business logic.
    -   **`components/`**: Reusable modules that encapsulate specific business logic (e.g., parsing a notebook, calculating cluster costs). Components should be independent and easily testable in isolation.
    -   **`server/` or `tools/`**: The layer that composes components into agent-callable tools. It defines tool inputs (`SomethingSchema`), orchestrates calls to components, and formats the final `CallToolResult`.
    -   **`cli/`**: Command-line entry points and interfaces.
-   **`tests/`**: Contains all tests, mirroring the application structure.
-   **File Length**: Aim to keep files under 400 lines. A long file is often a sign that logic can be refactored into a separate, more focused component in `components/` or a helper in a `utils/` module.

## 4. Agent Tool Design

Well-designed tools are the foundation of a capable agent.

-   **Single Responsibility**: Each tool should do one thing and do it well. A tool to `list_clusters` should not also have an option to delete one.
-   **Clear Inputs & Outputs**:
    -   Define inputs with a dedicated Pydantic `...Schema` model. This provides automatic validation and clear documentation.
    -   Return a `CallToolResult` object.
        -   The `TextContent` should be a concise, human-readable summary for the LLM.
        -   Store structured, machine-readable data in `_meta['data']`. This is what downstream tools or programmatic clients will use.
        -   For large artifacts (e.g., files, query results), use server cache helpers and place a reference handle in `_meta['resources']`.
-   **Idempotency**: Strive to make tools idempotent where possible. A tool that creates a resource should be safely runnable multiple times without creating duplicate resources.
-   **Naming**: Tool identifiers should be `snake_case` and clearly describe their action (e.g., `get_cluster_details`, `submit_spark_job`).

## 5. Error Handling & Logging

A robust system anticipates and reports failures clearly.

-   **Error Handling**:
    -   Use custom, specific exceptions for predictable application errors (e.g., `ClusterNotFoundError`, `InvalidConfigurationError`).
    -   Use `try/except` blocks sparingly, primarily at system boundaries (e.g., in the `api/` layer to catch network errors, or in the main server loop to catch unhandled exceptions).
    -   Avoid broad `except Exception:` blocks that hide bugs. If you must catch a broad exception, re-raise it or log it with a full traceback.
-   **Logging**:
    -   Use the standard `logging` module.
    -   Log at appropriate levels:
        -   `INFO`: Key lifecycle events (e.g., "Server starting," "Tool 'list_clusters' invoked").
        -   `DEBUG`: Verbose, detailed information useful for tracing execution flow (e.g., API request bodies, intermediate values).
        -   `WARNING`: A potential issue was encountered but the operation succeeded (e.g., "API deprecated, using fallback").
        -   `ERROR`: An operation failed due to a handled exception.
    -   Logs write to `databricks_mcp.log`. Be mindful of logging sensitive information.

## 6. Development & Testing Workflow

Follow these steps to ensure code quality and a smooth contribution process.

-   **Environment Setup**: Manage environments exclusively with `uv`.
    -   Initial setup: `uv pip install -e . && uv pip install -e ".[dev]"`
-   **Local Development & Testing**:
    1.  Write your code and corresponding tests.
    2.  Run tests locally: `uv run pytest`
    3.  Format and lint your code: `uv run black .` and `uv run pylint databricks_mcp tests`
    4.  Manually test CLI or server functionality if needed: `uv run databricks-mcp -- --help`
-   **Testing Guidelines**:
    -   Use `pytest` with `pytest-asyncio` for asynchronous code.
    -   Mock external dependencies at the `api/` boundary. Tests must be fast and runnable offline.
    -   **Test behavior, not implementation.** Assert that a function produces the correct output for a given input, not that it calls internal helpers in a specific way.
    -   For tool tests, assert the structure and content of `_meta['data']` and `_meta['resources']`.

## 7. Commits & Pull Requests

Clear communication helps the team review and integrate your work efficiently.

-   **Commit Messages**:
    -   Use descriptive, sentence-case titles (e.g., "Add tool to retrieve Spark job status").
    -   Reference issues in the body with `Fixes #<id>` or `Refs #<id>`.
    -   Keep body text wrapped at 72 columns for readability.
-   **Pull Requests (PRs)**:
    -   Write a clear summary of the changes and the problem being solved.
    -   Use a checklist for complex changes.
    -   Include screenshots, logs, or command-line captures to demonstrate new behavior.
    -   Ensure all automated checks (CI) are passing before requesting a review.
    -   Surface at least two implementation options for complex features, invite critique, and justify your chosen approach.

## 8. Security & Configuration

-   **Secrets Management**: Store secrets and environment-specific configuration in a `.env` file (see `.env.example`). This file is git-ignored.
-   **Required Variables**: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`.
-   **Log Rotation**: Before sharing log artifacts, ensure `databricks_mcp.log` has been rotated or cleared of sensitive information.