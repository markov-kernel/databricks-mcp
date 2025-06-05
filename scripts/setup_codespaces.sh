#!/bin/bash

set -e  # Exit on any error

echo "🚀 Setting up Databricks MCP Server for Codespaces..."

# Update package lists
echo "📦 Updating system packages..."
sudo apt-get update

# Install system dependencies if needed
echo "📦 Installing system dependencies..."
sudo apt-get install -y curl build-essential

# Check if uv is installed, install if not
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Add uv to PATH for future sessions
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Ensure uv is in PATH for this session
export PATH="$HOME/.cargo/bin:$PATH"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
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

# Install CLI dependencies
echo "📥 Installing CLI dependencies..."
uv pip install -e ".[cli]"

# Alternative: If you prefer using pip and requirements.txt instead of uv:
# pip install -r requirements.txt
# pip install -r requirements-dev.txt

# Verify installation
echo "🔍 Verifying installation..."
python -c "import databricks_mcp.server.databricks_mcp_server; print('✅ MCP server module imported successfully')"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

echo ""
echo "🎉 Codespaces setup complete!"
echo ""
echo "Environment variables detected:"
echo "  DATABRICKS_HOST: ${DATABRICKS_HOST:-'Not set'}"
echo "  DATABRICKS_TOKEN: ${DATABRICKS_TOKEN:-'Not set'}"
echo "  DATABRICKS_WAREHOUSE_ID: ${DATABRICKS_WAREHOUSE_ID:-'Not set'}"
echo "  SERVER_HOST: ${SERVER_HOST:-'Not set'}"
echo "  SERVER_PORT: ${SERVER_PORT:-'Not set'}"
echo ""
echo "Next steps:"
echo "1. Verify your Databricks connection:"
echo "   python scripts/show_clusters.py"
echo ""
echo "2. Start the MCP server:"
echo "   ./scripts/start_mcp_server.sh"
echo ""
echo "3. Test the server:"
echo "   ./scripts/run_mcp_client_test.sh"
echo ""
echo "4. Run tests:"
echo "   ./scripts/run_tests.sh"
echo ""
echo "📚 For more information, see README.md" 