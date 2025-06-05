# PowerShell setup script for Databricks MCP Server
param(
    [switch]$Force  # Force reinstallation
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Databricks MCP Server..." -ForegroundColor Green

# Check if uv is installed
try {
    $uvVersion = uv --version 2>$null
    Write-Host "✅ uv is already installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ uv is not installed. Installing uv..." -ForegroundColor Red
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Host "✅ uv installed successfully" -ForegroundColor Green
    Write-Host "⚠️  Please restart your terminal and run this script again" -ForegroundColor Yellow
    exit 0
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv") -or $Force) {
    if ($Force -and (Test-Path ".venv")) {
        Write-Host "🗑️  Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
    }
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    uv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& .\.venv\Scripts\Activate.ps1

# Install the project in development mode
Write-Host "📥 Installing project dependencies..." -ForegroundColor Blue
uv pip install -e .

# Install development dependencies
Write-Host "📥 Installing development dependencies..." -ForegroundColor Blue
uv pip install -e ".[dev]"

# Verify installation
Write-Host "🔍 Verifying installation..." -ForegroundColor Blue
try {
    python -c "import databricks_mcp.server.databricks_mcp_server; print('✅ MCP server module imported successfully')"
    Write-Host "✅ Installation verified successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Installation verification failed" -ForegroundColor Red
    throw
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set your environment variables:" -ForegroundColor White
Write-Host "   `$env:DATABRICKS_HOST='https://your-databricks-instance.azuredatabricks.net'" -ForegroundColor Gray
Write-Host "   `$env:DATABRICKS_TOKEN='your-personal-access-token'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the server:" -ForegroundColor White
Write-Host "   .\scripts\start_mcp_server.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Or run tests:" -ForegroundColor White
Write-Host "   .\scripts\run_tests.ps1" -ForegroundColor Gray 