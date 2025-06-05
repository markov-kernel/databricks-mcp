# Agent Guidelines

This repository uses `uv` for dependency management and `pytest` for testing.

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

Pull request messages should include **Summary** and **Testing** sections describing code changes and test results.
