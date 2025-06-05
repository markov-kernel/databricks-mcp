"""API for Unity Catalog."""

import logging
from typing import Any, Dict, Optional

from databricks_mcp.core.utils import make_api_request
from databricks_mcp.api import sql

logger = logging.getLogger(__name__)


async def list_catalogs() -> Dict[str, Any]:
    logger.info("Listing catalogs")
    return await make_api_request("GET", "/api/2.1/unity-catalog/catalogs")


async def create_catalog(name: str, comment: Optional[str] = None) -> Dict[str, Any]:
    payload = {"name": name}
    if comment:
        payload["comment"] = comment
    return await make_api_request("POST", "/api/2.1/unity-catalog/catalogs", data=payload)


async def list_schemas(catalog_name: str) -> Dict[str, Any]:
    return await make_api_request("GET", "/api/2.1/unity-catalog/schemas", params={"catalog_name": catalog_name})


async def create_schema(catalog_name: str, name: str, comment: Optional[str] = None) -> Dict[str, Any]:
    payload = {"catalog_name": catalog_name, "name": name}
    if comment:
        payload["comment"] = comment
    return await make_api_request("POST", "/api/2.1/unity-catalog/schemas", data=payload)


async def list_tables(catalog_name: str, schema_name: str) -> Dict[str, Any]:
    params = {"catalog_name": catalog_name, "schema_name": schema_name}
    return await make_api_request("GET", "/api/2.1/unity-catalog/tables", params=params)


async def create_table(warehouse_id: str, statement: str) -> Dict[str, Any]:
    """Execute a CREATE TABLE statement using the SQL API."""
    return await sql.execute_statement(statement, warehouse_id=warehouse_id)


async def get_table_lineage(full_name: str) -> Dict[str, Any]:
    endpoint = f"/api/2.1/unity-catalog/lineage-tracking/table-lineage/{full_name}"
    return await make_api_request("GET", endpoint)
