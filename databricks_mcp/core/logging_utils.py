"""
Shared logging configuration utilities for the Databricks MCP server.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - inherited docstring covers behavior
        payload = {
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = record.stack_info
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure application-wide logging, emitting JSON lines to stderr and an optional file.

    Args:
        level: Root log level name.
        log_file: Optional path for a synchronized file handler.
    """
    root = logging.getLogger()
    if getattr(root, "_mcp_configured", False):  # type: ignore[attr-defined]
        root.setLevel(level)
        return

    root.setLevel(level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root.handlers.clear()
    root.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        root.addHandler(file_handler)

    # Mark configuration to avoid duplicate handlers on repeated calls.
    setattr(root, "_mcp_configured", True)  # type: ignore[attr-defined]
