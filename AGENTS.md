# Agent Guidelines

This repository uses `uv` for dependency management and `pytest` for testing.

## Required Steps for Contributions

1. Run `scripts/setup.sh` to create and activate the virtual environment. This will install all project and development dependencies.
2. After making changes, ensure tests pass with:
   ```bash
   pytest -q
   ```
3. Update documentation when relevant.

Pull request messages should include **Summary** and **Testing** sections describing code changes and test results.
