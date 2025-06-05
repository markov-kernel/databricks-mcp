#!/bin/bash

set -e  # Exit on any error

echo "🚀 Setting up Databricks MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install the project in development mode
echo "📥 Installing project dependencies..."
uv pip install -e .

# Install development dependencies
echo "📥 Installing development dependencies..."
uv pip install -e ".[dev]"

# Verify installation
echo "🔍 Verifying installation..."
python -c "import databricks_mcp.server.databricks_mcp_server; print('✅ MCP server module imported successfully')"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your environment variables:"
echo "   export DATABRICKS_HOST=https://your-databricks-instance.azuredatabricks.net"
echo "   export DATABRICKS_TOKEN=your-personal-access-token"
echo ""
echo "2. Start the server:"
echo "   ./scripts/start_mcp_server.sh"
echo ""
echo "3. Or run tests:"
echo "   ./scripts/run_tests.ps1" 