#!/bin/bash

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "uv venv"
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Check if environment variables are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "Warning: DATABRICKS_HOST and/or DATABRICKS_TOKEN environment variables are not set."
    echo "Please set them before running the test."
    exit 1
fi

# Run the direct test
echo "Running direct test at $(date)"
echo "Databricks Host: $DATABRICKS_HOST"

uv run -m tests.direct_test

echo "Test completed at $(date)" 