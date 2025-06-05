#!/usr/bin/env pwsh
# Start script for the Databricks MCP server

param(
    [switch]$SkipPrompt
)

# Check if the virtual environment exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please create it first:"
    Write-Host "uv venv"
    exit 1
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Check if environment variables are set
if (-not (Get-Item -Path Env:DATABRICKS_HOST -ErrorAction SilentlyContinue) -or 
    -not (Get-Item -Path Env:DATABRICKS_TOKEN -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: DATABRICKS_HOST and/or DATABRICKS_TOKEN environment variables are not set."
    Write-Host "You can set them now or the server will look for them in other sources."
    
    # Skip prompt when called from tests
    if ($SkipPrompt) {
        Write-Host "Auto-continuing due to SkipPrompt flag..."
    } else {
        $continue = Read-Host "Do you want to continue? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
}

# Start the server
Write-Host "Starting Databricks MCP server at $(Get-Date)"
if (Get-Item -Path Env:DATABRICKS_HOST -ErrorAction SilentlyContinue) {
    Write-Host "Databricks Host: $env:DATABRICKS_HOST"
}

# Try to run the module using python -m
Write-Host "Attempting to start server using module path..."
python -m databricks_mcp.main

# If the above fails, fallback to direct script execution
if ($LASTEXITCODE -ne 0) {
    Write-Host "Module execution failed, trying direct script execution..."
    python "$PSScriptRoot\..\databricks_mcp\main.py"
}

Write-Host "Server stopped at $(Get-Date)" 