#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["databricks-sdk"]
# ///
"""
Validate SQL query syntax without execution.

Usage:
    uv run validate.py -q "SELECT * FROM table"
    uv run validate.py -f query.sql
    uv run validate.py -f query.sql --format json
"""

import argparse
import re
import sys

from utils import (
    get_config, get_client, get_warehouse_id,
    execute_statement, format_json, is_safe_query, read_sql_file
)


def extract_tables(sql: str) -> list[str]:
    """Extract table names from SQL query."""
    # Simple regex to find table references
    # Matches: FROM table, JOIN table, database.table
    patterns = [
        r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
        r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
    ]

    tables = set()
    sql_upper = sql.upper()

    for pattern in patterns:
        matches = re.findall(pattern, sql, re.IGNORECASE)
        for match in matches:
            # Skip SQL keywords that might be matched
            if match.upper() not in ["SELECT", "WHERE", "AND", "OR", "ON", "AS"]:
                tables.add(match)

    return sorted(tables)


def validate_query(client, warehouse_id: str, sql: str) -> dict:
    """
    Validate query using EXPLAIN.

    Returns dict with:
        - valid: bool
        - explain_plan: str (if valid)
        - error: str (if invalid)
        - tables: list of referenced tables
        - warnings: list of warnings
    """
    # Safety check
    is_safe, error_msg = is_safe_query(sql)
    if not is_safe:
        return {
            "valid": False,
            "error": error_msg,
            "tables": extract_tables(sql),
            "warnings": [],
        }

    # Run EXPLAIN
    explain_sql = f"EXPLAIN {sql}"
    result = execute_statement(client, warehouse_id, explain_sql, timeout_seconds=30)

    if not result["success"]:
        return {
            "valid": False,
            "error": result["error"],
            "tables": extract_tables(sql),
            "warnings": [],
        }

    # Parse explain output
    explain_lines = []
    for row in result["rows"]:
        if row and row[0]:
            explain_lines.append(row[0])

    explain_plan = "\n".join(explain_lines)

    # Check for warnings in plan
    warnings = []
    if "FileScan" in explain_plan and "PartitionFilters: []" in explain_plan:
        warnings.append("No partition filters - may scan entire table")
    if "BroadcastHashJoin" not in explain_plan and "Join" in explain_plan:
        warnings.append("Using SortMergeJoin - consider adding broadcast hint for small tables")

    return {
        "valid": True,
        "explain_plan": explain_plan,
        "tables": extract_tables(sql),
        "warnings": warnings,
    }


def check_tables_exist(client, warehouse_id: str, tables: list[str]) -> dict:
    """Check if tables exist and are accessible."""
    results = {}
    for table in tables:
        result = execute_statement(
            client, warehouse_id,
            f"DESCRIBE TABLE {table}",
            timeout_seconds=10
        )
        results[table] = {
            "exists": result["success"],
            "error": result.get("error") if not result["success"] else None,
        }
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate SQL query")
    parser.add_argument("-q", "--query", help="SQL query string")
    parser.add_argument("-f", "--file", help="SQL file path")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--check-tables", action="store_true", help="Check if tables exist")
    parser.add_argument("--explain-only", action="store_true", help="Show only EXPLAIN plan")

    args = parser.parse_args()

    # Get SQL
    if args.query:
        sql = args.query
    elif args.file:
        sql = read_sql_file(args.file)
    else:
        print("[ERROR] Must provide -q or -f", file=sys.stderr)
        sys.exit(1)

    config = get_config()
    client = get_client(config)
    warehouse_id = get_warehouse_id(client, config)

    # Validate
    result = validate_query(client, warehouse_id, sql)

    # Check tables if requested
    if args.check_tables and result["tables"]:
        result["table_check"] = check_tables_exist(client, warehouse_id, result["tables"])

    # Output
    if args.format == "json":
        print(format_json(result))
    else:
        if result["valid"]:
            print("[OK] Query is valid")
            print()

            if result["tables"]:
                print("Referenced tables:")
                for table in result["tables"]:
                    print(f"  - {table}")
                print()

            if args.check_tables and "table_check" in result:
                print("Table existence check:")
                for table, status in result["table_check"].items():
                    if status["exists"]:
                        print(f"  [OK] {table}")
                    else:
                        print(f"  [ERROR] {table}: {status['error']}")
                print()

            if result["warnings"]:
                print("Warnings:")
                for warning in result["warnings"]:
                    print(f"  - {warning}")
                print()

            if args.explain_only or True:  # Always show explain for now
                print("EXPLAIN plan:")
                print("-" * 60)
                print(result["explain_plan"])
        else:
            print(f"[ERROR] Query validation failed: {result['error']}", file=sys.stderr)
            if result["tables"]:
                print()
                print("Referenced tables:", file=sys.stderr)
                for table in result["tables"]:
                    print(f"  - {table}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
