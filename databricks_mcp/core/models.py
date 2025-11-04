from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class JobTask(BaseModel):
    """Represents a Databricks job task."""

    task_key: str
    notebook_task: Optional[Dict[str, Any]] = None
    existing_cluster_id: Optional[str] = None
    new_cluster: Optional[Dict[str, Any]] = None


class Job(BaseModel):
    """Simplified Databricks Job model used for job creation."""

    name: str
    tasks: List[JobTask]
    existing_cluster_id: Optional[str] = None
    new_cluster: Optional[Dict[str, Any]] = None


class Run(BaseModel):
    """Represents a Databricks job run."""

    run_id: int
    job_id: int
    state: Dict[str, Any]


class WorkspaceObject(BaseModel):
    """Workspace object such as a notebook or directory."""

    path: str
    object_type: str
    language: Optional[str] = None


class DbfsItem(BaseModel):
    """File or directory within DBFS."""

    path: str
    is_dir: bool
    file_size: Optional[int] = None


class ClusterConfig(BaseModel):
    """Subset of Databricks cluster configuration supported by the MCP tools."""

    cluster_name: str
    spark_version: str
    node_type_id: str
    num_workers: Optional[int] = None
    autotermination_minutes: Optional[int] = None
    autoscale: Optional[Dict[str, int]] = None
    spark_conf: Optional[Dict[str, Any]] = None
    custom_tags: Optional[Dict[str, str]] = None


class Library(BaseModel):
    """Specification of a library to install on a cluster."""

    pypi: Optional[Dict[str, str]] = None
    maven: Optional[Dict[str, Any]] = None
    egg: Optional[str] = None
    whl: Optional[str] = None


class Repo(BaseModel):
    """Represents a Databricks repo."""

    id: Optional[int] = None
    url: str
    provider: str
    branch: Optional[str] = None
    path: Optional[str] = None


class Catalog(BaseModel):
    """Unity Catalog catalog."""

    name: str
    comment: Optional[str] = None


class Schema(BaseModel):
    """Unity Catalog schema."""

    name: str
    catalog_name: str
    comment: Optional[str] = None


class Table(BaseModel):
    """Unity Catalog table."""

    name: str
    schema_name: str
    catalog_name: str
    comment: Optional[str] = None
