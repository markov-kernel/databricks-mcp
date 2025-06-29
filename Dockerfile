FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files + readme
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv
RUN uv sync

# Copy the rest of the source code
COPY . .

# Use uv to run the script
ENTRYPOINT ["uv", "run", "databricks-mcp-server"]