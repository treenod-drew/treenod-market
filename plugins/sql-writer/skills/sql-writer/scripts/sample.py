#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["databricks-sdk"]
# ///
"""
Execute SQL query and return sample rows.

Usage:
    uv run sample.py -q "SELECT * FROM table LIMIT 10"
    uv run sample.py -f query.sql
    uv run sample.py -f query.sql --limit 100
    uv run sample.py -f query.sql --output result.csv
"""

import argparse
import csv
import sys
import time

from utils import (
    get_config, get_client, get_warehouse_id,
    execute_statement, format_table, format_json, is_safe_query, read_sql_file
)


def check_partition_filter(sql: str) -> tuple[bool, str]:
    """
    Check if query has partition filter (WHERE clause with date filter).

    Returns (has_filter, warning_message).
    """
    sql_upper = sql.upper()

    # Check for WHERE clause
    if "WHERE" not in sql_upper:
        return False, "Query has no WHERE clause - will scan entire table"

    # Common partition column patterns
    partition_patterns = [
        r"\bLOG_DATE\s*[=<>]",
        r"\bLOG_DATE\s+BETWEEN",
        r"\bLOG_DATE\s+IN\s*\(",
        r"\bDT\s*[=<>]",
        r"\bDT\s+BETWEEN",
        r"\bDT\s+IN\s*\(",
        r"\bDATE\s*[=<>]",
        r"\bDATE\s+BETWEEN",
        r"\bPARTITION\s*\(",
    ]

    import re
    for pattern in partition_patterns:
        if re.search(pattern, sql_upper):
            return True, ""

    return False, "Query may not have partition filter (log_date, dt) - could scan large data range"


def add_limit(sql: str, limit: int) -> str:
    """Add or replace LIMIT clause in SQL."""
    sql_stripped = sql.strip().rstrip(";")
    sql_upper = sql_stripped.upper()

    # Check if LIMIT already exists
    if "LIMIT" in sql_upper:
        # Replace existing limit if it's larger
        import re
        match = re.search(r"LIMIT\s+(\d+)", sql_upper)
        if match:
            existing_limit = int(match.group(1))
            if existing_limit > limit:
                return re.sub(r"LIMIT\s+\d+", f"LIMIT {limit}", sql_stripped, flags=re.IGNORECASE)
        return sql_stripped

    return f"{sql_stripped} LIMIT {limit}"


def execute_sample(client, warehouse_id: str, sql: str, limit: int = 10, timeout: int = 60) -> dict:
    """
    Execute query and return sample results.

    Returns dict with:
        - success: bool
        - columns: list of column names
        - rows: list of row data
        - row_count: number of rows returned
        - execution_time: seconds
        - error: error message if failed
    """
    # Safety check
    is_safe, error_msg = is_safe_query(sql)
    if not is_safe:
        return {"success": False, "error": error_msg}

    # Add limit
    sql_limited = add_limit(sql, limit)

    # Execute
    start_time = time.time()
    result = execute_statement(client, warehouse_id, sql_limited, timeout_seconds=timeout)
    execution_time = time.time() - start_time

    if result["success"]:
        result["execution_time"] = round(execution_time, 2)
        result["query"] = sql_limited
    return result


def save_csv(columns: list, rows: list, path: str):
    """Save results to CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Execute SQL and get sample rows")
    parser.add_argument("-q", "--query", help="SQL query string")
    parser.add_argument("-f", "--file", help="SQL file path")
    parser.add_argument("--limit", type=int, default=10, help="Max rows to return (default: 10)")
    parser.add_argument("--timeout", type=int, default=60, help="Query timeout in seconds (default: 60)")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--no-filter-check", action="store_true", help="Skip partition filter check")

    args = parser.parse_args()

    # Get SQL
    if args.query:
        sql = args.query
    elif args.file:
        sql = read_sql_file(args.file)
    else:
        print("[ERROR] Must provide -q or -f", file=sys.stderr)
        sys.exit(1)

    # Enforce max limit
    limit = min(args.limit, 10000)

    # Check for partition filter
    if not args.no_filter_check:
        has_filter, warning = check_partition_filter(sql)
        if not has_filter:
            print(f"[WARNING] {warning}", file=sys.stderr)
            print("[WARNING] Add partition filter (e.g., WHERE log_date = '2024-01-01') or use --no-filter-check to skip", file=sys.stderr)
            sys.exit(1)

    config = get_config()
    client = get_client(config)
    warehouse_id = get_warehouse_id(client, config)

    # Execute
    result = execute_sample(client, warehouse_id, sql, limit=limit, timeout=args.timeout)

    if not result["success"]:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.format == "json":
        output = format_json(result)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)

    elif args.format == "csv":
        if args.output:
            save_csv(result["columns"], result["rows"], args.output)
            print(f"Results saved to {args.output} ({result['row_count']} rows)")
        else:
            # Print CSV to stdout
            writer = csv.writer(sys.stdout)
            writer.writerow(result["columns"])
            writer.writerows(result["rows"])

    else:  # table
        print(f"Query executed in {result['execution_time']}s")
        print(f"Rows returned: {result['row_count']}")
        print()
        print(format_table(result["columns"], result["rows"]))

        if args.output:
            save_csv(result["columns"], result["rows"], args.output)
            print()
            print(f"Results also saved to {args.output}")


if __name__ == "__main__":
    main()
