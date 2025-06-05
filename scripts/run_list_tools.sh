#!/bin/bash

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "uv venv"
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Run the list tools test
echo "Running list tools test at $(date)"

# Check if the server is already running
if ! pgrep -f "uv run.*databricks_mcp.server.databricks_mcp_server" > /dev/null; then
    echo "Starting MCP server in the background..."
    # Start the server in the background
    uv run databricks_mcp.server.databricks_mcp_server > server.log 2>&1 &
    SERVER_PID=$!
    echo "Server started with PID $SERVER_PID"
    # Give the server a moment to start
    sleep 2
    SERVER_STARTED=true
else
    echo "MCP server is already running"
    SERVER_STARTED=false
fi

# Run the list tools test
echo "Running list tools test..."
uv run -m tests.list_tools_test

# If we started the server, stop it
if [ "$SERVER_STARTED" = true ]; then
    echo "Stopping MCP server (PID $SERVER_PID)..."
    kill $SERVER_PID
    echo "Server stopped"
fi

echo "Test completed at $(date)" 