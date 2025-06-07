# Changelog

## [0.3.1] - 2025-06-07

### Fixed
- **Issue #9**: Fixed "Missing required parameter 'params'" error when using MCP tools in Cursor
  - Added `_unwrap_params()` helper function to handle both nested and flat parameter structures
  - Updated all MCP tool implementations to consistently handle parameter unwrapping
  - MCP clients like Cursor now work correctly with all available tools
  - Maintains backward compatibility with flat parameter structures

### Technical Details
MCP clients were passing parameters in a nested structure like:
```json
{
  "params": {
    "cluster_id": "example-cluster-123",
    "other_param": "value"
  }
}
```

But the tool implementations expected a flat structure like:
```json
{
  "cluster_id": "example-cluster-123", 
  "other_param": "value"
}
```

The fix automatically detects and unwraps nested parameters while maintaining backward compatibility.

### Changed
- All MCP tool functions now use consistent parameter handling
- Improved error logging to include parameter structure information

## Previous Versions

For previous version history, see git log. 