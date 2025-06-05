# New Features Documentation

This document describes the two new features added to the Databricks MCP server.

## Feature 1: Warehouse ID Environment Variable

### Overview
Previously, the `execute_sql` tool required a `warehouse_id` parameter every time. Now you can set a default warehouse ID as an environment variable, making the parameter optional.

### Configuration
Set the environment variable:
```bash
export DATABRICKS_WAREHOUSE_ID=sql_warehouse_12345
```

### Usage
```python
# Without warehouse_id (uses environment variable)
await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10"
})

# With explicit warehouse_id (overrides environment variable)
await session.call_tool("execute_sql", {
    "statement": "SELECT * FROM my_table LIMIT 10",
    "warehouse_id": "sql_warehouse_specific"
})
```

### Implementation Details
- Added `DATABRICKS_WAREHOUSE_ID` to `src/core/config.py`
- Modified `src/api/sql.py` to use environment variable as fallback
- Updated MCP tool description to indicate optional parameter
- Maintains backward compatibility

## Feature 2: Workspace File Content Retrieval

### Overview
Two new tools have been added to retrieve content and metadata from Databricks workspace files (JSON files, notebooks, scripts, etc.).

### New Tools

#### `get_workspace_file_content`
Retrieves the actual content of a workspace file.

**Parameters:**
- `workspace_path` (required): Path to the file in workspace (e.g., `/Users/user@domain.com/file.json`)
- `format` (optional): Export format - SOURCE, HTML, JUPYTER, DBC (default: SOURCE)

**Example:**
```python
await session.call_tool("get_workspace_file_content", {
    "workspace_path": "/Users/huytl@remitano.com/azasend_schema/azasend_overview.json"
})
```

#### `get_workspace_file_info`
Gets metadata about a workspace file without downloading content.

**Parameters:**
- `workspace_path` (required): Path to the file in workspace

**Example:**
```python
await session.call_tool("get_workspace_file_info", {
    "workspace_path": "/Users/user@domain.com/config/settings.json"
})
```

### Response Format

#### File Content Response
```json
{
  "content": "base64_encoded_content",
  "decoded_content": "actual_text_content",
  "content_type": "json|text|binary",
  "path": "/Users/user@domain.com/file.json",
  "language": "JSON",
  "object_type": "FILE"
}
```

#### File Info Response
```json
{
  "path": "/Users/user@domain.com/file.json",
  "object_type": "FILE",
  "language": "JSON",
  "created_at": 1640995200000,
  "modified_at": 1640995200000,
  "size": 1024
}
```

### Features
- **Automatic decoding**: Base64 content is automatically decoded to text
- **JSON detection**: JSON files are automatically detected and marked
- **Error handling**: Graceful handling of encoding issues and missing files
- **Multiple formats**: Supports SOURCE, HTML, JUPYTER, DBC formats
- **Content type detection**: Automatically detects JSON, text, or binary content

### API Endpoint Used
Both tools use the Databricks Workspace API:
- Endpoint: `/api/2.0/workspace/export`
- Method: GET
- Parameters: `path`, `format`

### Implementation Details
- Added `export_workspace_file()` and `get_workspace_file_info()` to `src/api/notebooks.py`
- Added two new MCP tools to `src/server/databricks_mcp_server.py`
- Handles encoding issues gracefully with fallback strategies
- Uses existing authentication and error handling infrastructure

## Testing

### Test Scripts
Two test scripts are provided:

1. **`test_new_features.py`**: Comprehensive test of both features
2. **`test_example_file.py`**: Quick test with the specific example path

### Running Tests
```bash
# Set environment variables
export DATABRICKS_HOST=https://your-workspace.databricks.com
export DATABRICKS_TOKEN=dapi_your_token
export DATABRICKS_WAREHOUSE_ID=sql_warehouse_12345

# Run comprehensive test
python test_new_features.py

# Test with example file
python test_example_file.py
```

## Backward Compatibility

Both features maintain full backward compatibility:
- Existing `execute_sql` calls with `warehouse_id` parameter continue to work
- No changes to existing tools or APIs
- Optional parameters remain optional

## Error Handling

### Warehouse ID Feature
- If no `warehouse_id` provided and no environment variable set: Clear error message
- Invalid warehouse ID: Databricks API error is returned

### Workspace File Feature
- File not found: Clear error message with file path
- Access denied: Databricks API error is returned
- Encoding issues: Graceful fallback with warnings
- Binary files: Detected and handled appropriately

## Configuration Examples

### Environment Variables (.env file)
```bash
# Required
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=dapi_your_token_here

# Optional - enables default warehouse for SQL
DATABRICKS_WAREHOUSE_ID=sql_warehouse_12345

# Optional - other settings
LOG_LEVEL=INFO
DEBUG=false
```

### Cursor MCP Configuration
```json
{
  "mcpServers": {
    "databricks-mcp-local": {
      "command": "/path/to/start_mcp_server.sh",
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.databricks.com",
        "DATABRICKS_TOKEN": "dapi_your_token",
        "DATABRICKS_WAREHOUSE_ID": "sql_warehouse_12345"
      }
    }
  }
}
```

## Use Cases

### SQL Execution
- **Data Analysis**: Quick SQL queries without specifying warehouse each time
- **Automated Reports**: Scripts that run SQL without hardcoded warehouse IDs
- **Multi-environment**: Different warehouses for dev/staging/prod via env vars

### Workspace Files
- **Configuration Management**: Retrieve JSON config files from workspace
- **Code Review**: Get content of Python/R scripts for analysis
- **Notebook Export**: Export notebooks in different formats
- **File Inspection**: Check file metadata before downloading large files

## Security Considerations

- Environment variables are not logged in debug output
- File content is transmitted securely via existing Databricks authentication
- No additional authentication required beyond existing Databricks token
- Large files are handled efficiently without memory issues
