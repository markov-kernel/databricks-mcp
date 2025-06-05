# Agent Guidelines

This repository uses `uv` for dependency management and `pytest` for testing.

## Scope of Work

**Refactoring, Restructuring, and Feature Development is ENCOURAGED and AUTHORIZED.** Agents should feel empowered to:

- Perform comprehensive code refactoring to improve structure, readability, and maintainability
- Restructure the entire repository when it improves organization and follows best practices  
- Reorganize files and directories to better align with software engineering standards
- Refactor code to eliminate duplication, improve performance, and enhance testability
- Update project structure to follow modern Python package organization patterns
- Modernize code to use current best practices and patterns
- **Add new features, functionality, and capabilities when requested by users**
- Implement additional tools, APIs, integrations, and enhancements
- Extend existing functionality with new options, parameters, and capabilities

**No arbitrary scope limitations apply to code improvements or feature additions.**

## Required Steps for Contributions

1. Run `scripts/setup.sh` to create and activate the virtual environment. This will install all project and development dependencies.
   - For Codespaces environments, use `./setup_codespaces.sh` instead
2. After making changes, ensure tests pass with:
   ```bash
   # Unix/Mac/Linux
   ./scripts/run_tests.sh
   
   # Windows
   ./scripts/run_tests.ps1
   
   # Or if you prefer to run pytest directly:
   source .venv/bin/activate  # Unix/Mac
   pytest -q
   ```
3. Update documentation when relevant.
4. **For major refactoring:** Ensure all existing functionality is preserved and enhanced test coverage is provided.

## Refactoring Guidelines

When performing refactoring work:
- Maintain backward compatibility where possible
- Ensure all existing tests continue to pass
- Add new tests for any new functionality or edge cases discovered
- Update documentation to reflect structural changes
- Follow the project's coding standards and best practices
- Break large refactoring into logical, reviewable chunks when possible

Pull request messages should include **Summary** and **Testing** sections describing code changes and test results.
