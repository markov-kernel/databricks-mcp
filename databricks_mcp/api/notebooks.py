"""
API for managing Databricks notebooks.
"""

import base64
import logging
from typing import Any, Dict, List, Optional

from databricks_mcp.core.utils import DatabricksAPIError, make_api_request

# Configure logging
logger = logging.getLogger(__name__)


async def import_notebook(
    path: str,
    content: str,
    format: str = "SOURCE",
    language: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Import a notebook into the workspace.
    
    Args:
        path: The path where the notebook should be stored
        content: The content of the notebook (base64 encoded)
        format: The format of the notebook (SOURCE, HTML, JUPYTER, DBC)
        language: The language of the notebook (SCALA, PYTHON, SQL, R)
        overwrite: Whether to overwrite an existing notebook
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Importing notebook to path: {path}")
    
    # Ensure content is base64 encoded
    if not is_base64(content):
        content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    import_data = {
        "path": path,
        "format": format,
        "content": content,
        "overwrite": overwrite,
    }
    
    if language:
        import_data["language"] = language
        
    return await make_api_request("POST", "/api/2.0/workspace/import", data=import_data)


async def export_notebook(
    path: str,
    format: str = "SOURCE",
) -> Dict[str, Any]:
    """
    Export a notebook from the workspace.
    
    Args:
        path: The path of the notebook to export
        format: The format to export (SOURCE, HTML, JUPYTER, DBC)
        
    Returns:
        Response containing the notebook content
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Exporting notebook from path: {path}")
    
    params = {
        "path": path,
        "format": format,
    }
    
    response = await make_api_request("GET", "/api/2.0/workspace/export", params=params)
    
    # Optionally decode base64 content
    if "content" in response and format in ["SOURCE", "JUPYTER"]:
        try:
            response["decoded_content"] = base64.b64decode(response["content"]).decode("utf-8")
        except Exception as e:
            logger.warning(f"Failed to decode notebook content: {str(e)}")
            
    return response


async def list_notebooks(path: str) -> Dict[str, Any]:
    """
    List notebooks in a workspace directory.
    
    Args:
        path: The path to list
        
    Returns:
        Response containing the directory listing
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Listing notebooks in path: {path}")
    return await make_api_request("GET", "/api/2.0/workspace/list", params={"path": path})


async def delete_notebook(path: str, recursive: bool = False) -> Dict[str, Any]:
    """
    Delete a notebook or directory.
    
    Args:
        path: The path to delete
        recursive: Whether to recursively delete directories
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Deleting path: {path}")
    return await make_api_request(
        "POST",
        "/api/2.0/workspace/delete",
        data={"path": path, "recursive": recursive}
    )


async def create_directory(path: str) -> Dict[str, Any]:
    """
    Create a directory in the workspace.
    
    Args:
        path: The path to create
        
    Returns:
        Empty response on success
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Creating directory: {path}")
    return await make_api_request("POST", "/api/2.0/workspace/mkdirs", data={"path": path})


async def export_workspace_file(
    path: str,
    format: str = "SOURCE",
) -> Dict[str, Any]:
    """
    Export any file from the workspace (not just notebooks).
    
    Args:
        path: The workspace path of the file to export (e.g., /Users/user@domain.com/file.json)
        format: The format to export (SOURCE, HTML, JUPYTER, DBC)
        
    Returns:
        Response containing the file content
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Exporting workspace file from path: {path}")
    
    params = {
        "path": path,
        "format": format,
    }
    
    response = await make_api_request("GET", "/api/2.0/workspace/export", params=params)
    
    # Always try to decode base64 content for SOURCE format
    if "content" in response and format == "SOURCE":
        try:
            decoded_content = base64.b64decode(response["content"]).decode("utf-8")
            response["decoded_content"] = decoded_content
            response["content_type"] = "text"
            
            # Try to detect if it's JSON
            try:
                import json
                json.loads(decoded_content)  # Validate JSON
                response["content_type"] = "json"
            except json.JSONDecodeError:
                pass  # Keep as text
                
        except UnicodeDecodeError as e:
            logger.warning(f"Failed to decode file content as UTF-8: {str(e)}")
            # Try different encodings
            try:
                decoded_bytes = base64.b64decode(response["content"])
                # Return as text with error replacement
                response["decoded_content"] = decoded_bytes.decode("utf-8", errors="replace")
                response["content_type"] = "text"
                response["encoding_warning"] = "Some characters may not display correctly"
            except Exception as e2:
                logger.warning(f"Failed to decode content with any encoding: {str(e2)}")
                response["content_type"] = "binary"
                response["note"] = "Content could not be decoded as text"
    
    return response


async def get_workspace_file_info(path: str) -> Dict[str, Any]:
    """
    Get information about a workspace file without downloading content.
    
    Args:
        path: The workspace path to check
        
    Returns:
        Response containing file information
        
    Raises:
        DatabricksAPIError: If the API request fails
    """
    logger.info(f"Getting workspace file info for path: {path}")
    
    # Use the workspace list API to get file metadata
    # Split the path to get directory and filename
    import os
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    
    if not directory:
        directory = "/"
    
    # List the directory to find the file
    response = await make_api_request("GET", "/api/2.0/workspace/list", params={"path": directory})
    
    # Find the specific file in the listing
    if "objects" in response:
        for obj in response["objects"]:
            if obj.get("path") == path:
                return obj
    
    raise DatabricksAPIError(f"File not found: {path}")


def is_base64(content: str) -> bool:
    """
    Check if a string is already base64 encoded.
    
    Args:
        content: The string to check
        
    Returns:
        True if the string is base64 encoded, False otherwise
    """
    try:
        return base64.b64encode(base64.b64decode(content)) == content.encode('utf-8')
    except Exception:
        return False 