#!/usr/bin/env pwsh
# PowerShell script to run the simple tool lister

# Check if virtual environment exists
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please create it first:"
    Write-Host "uv venv"
    exit 1
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Make sure there are no existing MCP server processes
$serverProcesses = Get-Process -Name pwsh | Where-Object { $_.CommandLine -like "*start_mcp_server.ps1*" }
if ($serverProcesses) {
    Write-Host "Found existing MCP server processes, stopping them first..."
    $serverProcesses | ForEach-Object { 
        Stop-Process -Id $_.Id -Force 
        Write-Host "Stopped process $($_.Id)"
    }
}

# Set timeout in seconds
$timeout = 20

# Run the CLI command with a timeout
Write-Host "Running CLI tool listing with a $timeout second timeout..."
$job = Start-Job -ScriptBlock { 
    cd $using:PWD
    cd ..
    uv run -m databricks_mcp.cli.commands list-tools
}

# Monitor the job and output in real-time
$start = Get-Date
while ($job.State -eq "Running") {
    # Get any new output
    $output = Receive-Job -Job $job
    if ($output) {
        Write-Host $output
    }
    
    # Check if we've hit the timeout
    $elapsed = (Get-Date) - $start
    if ($elapsed.TotalSeconds -gt $timeout) {
        Write-Host "Command is taking too long, terminating..."
        Stop-Job -Job $job
        break
    }
    
    # Sleep briefly
    Start-Sleep -Milliseconds 500
}

# Output final results
$output = Receive-Job -Job $job
if ($output) {
    Write-Host $output
}

Remove-Job -Job $job -Force

# Clean up any leftover processes
$serverProcesses = Get-Process -Name pwsh | Where-Object { $_.CommandLine -like "*start_mcp_server.ps1*" }
if ($serverProcesses) {
    Write-Host "Cleaning up any remaining MCP server processes..."
    $serverProcesses | ForEach-Object { 
        Stop-Process -Id $_.Id -Force 
        Write-Host "Stopped process $($_.Id)"
    }
} 