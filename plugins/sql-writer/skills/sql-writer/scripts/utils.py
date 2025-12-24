# /// script
# requires-python = ">=3.11"
# dependencies = ["databricks-sdk"]
# ///
"""
Shared utilities for SQL Writer skill.
Handles authentication, error handling, and common operations.
"""

import os
import sys
import json
from typing import Optional
from dataclasses import dataclass

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


@dataclass
class Config:
    """Configuration for Databricks connection."""
    host: str
    token: str
    warehouse_id: Optional[str] = None
    timeout_seconds: int = 60
    max_rows: int = 10000


def get_config() -> Config:
    """Get configuration from environment variables."""
    token = os.environ.get("DATABRICKS_TOKEN")
    host = os.environ.get("DATABRICKS_HOST", "https://treenod-analytic.cloud.databricks.com")
    warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID")

    if not token:
        print("[ERROR] DATABRICKS_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    return Config(
        host=host,
        token=token,
        warehouse_id=warehouse_id,
    )


def get_client(config: Optional[Config] = None) -> WorkspaceClient:
    """Get authenticated Databricks client."""
    if config is None:
        config = get_config()

    return WorkspaceClient(host=config.host, token=config.token)


def get_warehouse_id(client: WorkspaceClient, config: Config) -> str:
    """Get SQL warehouse ID, either from config or by finding an available one."""
    if config.warehouse_id:
        return config.warehouse_id

    # Find first available SQL warehouse
    warehouses = list(client.warehouses.list())
    if not warehouses:
        print("[ERROR] No SQL warehouses found", file=sys.stderr)
        sys.exit(1)

    # Prefer running warehouses
    for wh in warehouses:
        if wh.state and wh.state.value == "RUNNING":
            return wh.id

    # Otherwise use first available
    return warehouses[0].id


def execute_statement(
    client: WorkspaceClient,
    warehouse_id: str,
    sql: str,
    timeout_seconds: int = 60,
) -> dict:
    """
    Execute SQL statement and return results.

    Returns dict with:
        - success: bool
        - columns: list of column names
        - rows: list of row data
        - row_count: number of rows
        - error: error message if failed
    """
    import time

    try:
        # Use wait_timeout within allowed range (5-50s), poll for longer
        wait_timeout = min(max(timeout_seconds, 5), 50)

        response = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=sql,
            wait_timeout="{}s".format(wait_timeout),
        )

        # Poll if still pending/running
        start_time = time.time()
        while response.status.state in [StatementState.PENDING, StatementState.RUNNING]:
            if time.time() - start_time > timeout_seconds:
                # Cancel and return timeout error
                try:
                    client.statement_execution.cancel_execution(response.statement_id)
                except Exception:
                    pass
                return {"success": False, "error": "Query timeout"}

            time.sleep(2)
            response = client.statement_execution.get_statement(response.statement_id)

        if response.status.state == StatementState.SUCCEEDED:
            columns = []
            rows = []

            if response.manifest and response.manifest.schema:
                columns = [col.name for col in response.manifest.schema.columns]

            if response.result and response.result.data_array:
                rows = response.result.data_array

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
        else:
            error_msg = "Unknown error"
            if response.status.error:
                error_msg = response.status.error.message
            return {
                "success": False,
                "error": error_msg,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def format_table(columns: list, rows: list, max_width: int = 50) -> str:
    """Format results as ASCII table."""
    if not columns:
        return "No columns"
    if not rows:
        return "No rows"

    # Calculate column widths
    widths = [len(str(col)) for col in columns]
    for row in rows[:100]:  # Sample first 100 rows for width calculation
        for i, val in enumerate(row):
            val_str = str(val) if val is not None else "NULL"
            widths[i] = min(max(widths[i], len(val_str)), max_width)

    # Build table
    lines = []

    # Header
    header = " | ".join(str(col)[:widths[i]].ljust(widths[i]) for i, col in enumerate(columns))
    lines.append(header)
    lines.append("-+-".join("-" * w for w in widths))

    # Rows
    for row in rows:
        row_str = " | ".join(
            (str(val) if val is not None else "NULL")[:widths[i]].ljust(widths[i])
            for i, val in enumerate(row)
        )
        lines.append(row_str)

    return "\n".join(lines)


def format_json(data: dict, indent: int = 2) -> str:
    """Format data as JSON."""
    return json.dumps(data, indent=indent, default=str)


def is_safe_query(sql: str) -> tuple[bool, str]:
    """
    Check if query is read-only (SELECT only).

    Returns (is_safe, error_message).
    """
    sql_upper = sql.upper().strip()

    # Remove comments
    lines = []
    for line in sql_upper.split("\n"):
        line = line.split("--")[0].strip()
        if line:
            lines.append(line)
    sql_clean = " ".join(lines)

    # Check for dangerous keywords
    dangerous = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "TRUNCATE", "GRANT", "REVOKE", "MERGE", "COPY",
    ]

    for keyword in dangerous:
        # Check if keyword appears as a word (not part of column name)
        import re
        if re.search(r"\b" + keyword + r"\b", sql_clean):
            return False, f"Query contains forbidden keyword: {keyword}"

    # Must start with SELECT, EXPLAIN, DESCRIBE, or SHOW
    allowed_starts = ["SELECT", "EXPLAIN", "DESCRIBE", "SHOW", "WITH"]
    if not any(sql_clean.startswith(kw) for kw in allowed_starts):
        return False, f"Query must start with one of: {', '.join(allowed_starts)}"

    return True, ""


def read_sql_file(path: str) -> str:
    """Read SQL from file."""
    with open(path, "r") as f:
        return f.read()
