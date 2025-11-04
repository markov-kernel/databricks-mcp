"""
Helper utilities for building consistent MCP tool responses.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from mcp.types import CallToolResult, TextContent


def _coerce_structured(data: Any) -> Dict[str, Any]:
    """Ensure structured payload is JSON-serializable as a dict."""
    if isinstance(data, dict):
        return data
    if hasattr(data, "model_dump"):
        return data.model_dump(mode="json")  # type: ignore[attr-defined]
    return {"result": data}


def success_result(
    summary: str,
    data: Any,
    *,
    meta: Optional[Dict[str, Any]] = None,
    resource_links: Optional[Sequence[Dict[str, Any]]] = None,
) -> CallToolResult:
    """
    Build a standardized success payload with structured content.

    Args:
        summary: Short human-readable description.
        data: Structured payload (or object convertible to dict via `.model_dump()`).
    """
    result = CallToolResult(
        content=[TextContent(type="text", text=summary)],
        structuredContent=_coerce_structured(data),
        isError=False,
    )
    if meta:
        result.meta = meta
    if resource_links:
        # Append resource_link content blocks (per MCP spec)
        for link in resource_links:
            result.content.append(
                {  # type: ignore[dict-item]
                    "type": "resource_link",
                    **link,
                }
            )
    return result


def error_result(message: str, *, details: Optional[Any] = None, status_code: Optional[int] = None) -> CallToolResult:
    """
    Build a standardized error payload.

    Args:
        message: Human-readable error summary.
        details: Optional structured detail block.
        status_code: Optional HTTP status code from upstream.
    """
    payload: Dict[str, Any] = {"message": message}
    if status_code is not None:
        payload["status_code"] = status_code
    if details is not None:
        payload["details"] = details if isinstance(details, dict) else {"raw": details}

    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        structuredContent=payload,
        isError=True,
    )
