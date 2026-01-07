#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["databricks-sdk"]
# ///
"""
Get table schema and metadata from Databricks.

Usage:
    uv run schema.py <table_name>
    uv run schema.py <table_name> --format json
    uv run schema.py --list-tables <database>
    uv run schema.py --generate-catalog <database> -o catalog.md
"""

import argparse
import sys
from typing import Optional

from utils import get_config, get_client, get_warehouse_id, execute_statement, format_table, format_json


def get_table_schema(client, warehouse_id: str, table_name: str) -> dict:
    """Get detailed schema for a table."""
    # Get column info
    result = execute_statement(
        client, warehouse_id,
        f"DESCRIBE TABLE EXTENDED {table_name}"
    )

    if not result["success"]:
        return {"success": False, "error": result["error"]}

    columns = []
    partitions = []
    properties = {}
    in_partition_section = False
    in_table_info_section = False

    for row in result["rows"]:
        col_name = row[0] if row[0] else ""
        data_type = row[1] if len(row) > 1 and row[1] else ""
        comment = row[2] if len(row) > 2 and row[2] else ""

        # Skip empty rows
        if not col_name.strip():
            continue

        # Detect section markers
        if col_name.startswith("# Partition"):
            in_partition_section = True
            in_table_info_section = False
            continue
        elif col_name.startswith("# Detailed Table"):
            in_partition_section = False
            in_table_info_section = True
            continue
        elif col_name.startswith("#"):
            in_partition_section = False
            in_table_info_section = False
            continue

        # Parse based on section
        if in_table_info_section:
            properties[col_name] = data_type
        elif in_partition_section:
            partitions.append({"name": col_name, "type": data_type})
        else:
            columns.append({
                "name": col_name,
                "type": data_type,
                "comment": comment,
            })

    return {
        "success": True,
        "table_name": table_name,
        "columns": columns,
        "partitions": partitions,
        "properties": properties,
    }


def list_tables(client, warehouse_id: str, database: str) -> dict:
    """List all tables in a database."""
    result = execute_statement(
        client, warehouse_id,
        f"SHOW TABLES IN {database}"
    )

    if not result["success"]:
        return {"success": False, "error": result["error"]}

    tables = []
    for row in result["rows"]:
        tables.append({
            "database": row[0] if row[0] else database,
            "table_name": row[1] if len(row) > 1 else "",
            "is_temporary": row[2] if len(row) > 2 else False,
        })

    return {"success": True, "tables": tables}


def list_databases(client, warehouse_id: str) -> dict:
    """List all databases."""
    result = execute_statement(client, warehouse_id, "SHOW DATABASES")

    if not result["success"]:
        return {"success": False, "error": result["error"]}

    databases = [row[0] for row in result["rows"]]
    return {"success": True, "databases": databases}


def generate_catalog(client, warehouse_id: str, database: str) -> str:
    """Generate markdown catalog for a database."""
    lines = [f"# {database} Data Catalog", ""]

    tables_result = list_tables(client, warehouse_id, database)
    if not tables_result["success"]:
        return f"Error: {tables_result['error']}"

    for table in tables_result["tables"]:
        table_name = f"{database}.{table['table_name']}"
        lines.append(f"## {table['table_name']}")
        lines.append("")

        schema = get_table_schema(client, warehouse_id, table_name)
        if schema["success"]:
            # Columns
            lines.append("### Columns")
            lines.append("")
            lines.append("| Column | Type | Comment |")
            lines.append("|--------|------|---------|")
            for col in schema["columns"]:
                lines.append(f"| {col['name']} | {col['type']} | {col['comment']} |")
            lines.append("")

            # Partitions
            if schema["partitions"]:
                lines.append("### Partitions")
                lines.append("")
                for part in schema["partitions"]:
                    lines.append(f"- {part['name']} ({part['type']})")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get table schema and metadata")
    parser.add_argument("table", nargs="?", help="Table name (database.table)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--list-tables", metavar="DATABASE", help="List tables in database")
    parser.add_argument("--list-databases", action="store_true", help="List all databases")
    parser.add_argument("--generate-catalog", metavar="DATABASE", help="Generate catalog for database")
    parser.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args()

    config = get_config()
    client = get_client(config)
    warehouse_id = get_warehouse_id(client, config)

    # List databases
    if args.list_databases:
        result = list_databases(client, warehouse_id)
        if not result["success"]:
            print(f"[ERROR] {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.format == "json":
            print(format_json(result))
        else:
            for db in result["databases"]:
                print(db)
        return

    # List tables
    if args.list_tables:
        result = list_tables(client, warehouse_id, args.list_tables)
        if not result["success"]:
            print(f"[ERROR] {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.format == "json":
            print(format_json(result))
        else:
            for table in result["tables"]:
                print(f"{table['database']}.{table['table_name']}")
        return

    # Generate catalog
    if args.generate_catalog:
        content = generate_catalog(client, warehouse_id, args.generate_catalog)
        if args.output:
            with open(args.output, "w") as f:
                f.write(content)
            print(f"Catalog saved to {args.output}")
        else:
            print(content)
        return

    # Get table schema
    if not args.table:
        parser.print_help()
        sys.exit(1)

    schema = get_table_schema(client, warehouse_id, args.table)
    if not schema["success"]:
        print(f"[ERROR] {schema['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.format == "json":
        output = format_json(schema)
    else:
        lines = [
            f"Table: {schema['table_name']}",
            "",
            "Columns:",
        ]
        for col in schema["columns"]:
            comment_str = f" -- {col['comment']}" if col["comment"] else ""
            lines.append(f"  {col['name']}: {col['type']}{comment_str}")

        if schema["partitions"]:
            lines.append("")
            lines.append("Partitions:")
            for part in schema["partitions"]:
                lines.append(f"  {part['name']}: {part['type']}")

        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Schema saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
