#!/bin/bash
# Run tests for the Databricks MCP server

# Default values
TEST_PATH="${1:-tests/}"
COVERAGE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "uv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Base command
cmd="pytest"

# Add verbose flag if specified
if [ "$VERBOSE" = true ]; then
    cmd="$cmd -v"
fi

# Add coverage if specified
if [ "$COVERAGE" = true ]; then
    cmd="$cmd --cov=src --cov-report=term-missing"
fi

# Add test path
cmd="$cmd $TEST_PATH"

echo "Running: $cmd"
$cmd

# Print summary
echo ""
echo "Test run completed at $(date)" 