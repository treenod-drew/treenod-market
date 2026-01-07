"""Debug script to fetch and analyze raw ADF from Confluence page."""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from utils import get_auth_headers, get_base_urls


def fetch_raw_adf(page_id: str) -> dict:
    """Fetch raw ADF content from Confluence page."""
    confluence_url, _ = get_base_urls()
    headers = get_auth_headers()

    url = f"{confluence_url}/wiki/api/v2/pages/{page_id}"
    params = {"body-format": "atlas_doc_format"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def collect_node_types(node: dict, types: set, depth: int = 0) -> None:
    """Recursively collect all node types in ADF."""
    node_type = node.get('type')
    if node_type:
        types.add(node_type)

    # Check for content array
    for child in node.get('content', []):
        collect_node_types(child, types, depth + 1)

    # Check for marks
    for mark in node.get('marks', []):
        mark_type = mark.get('type')
        if mark_type:
            types.add(f"mark:{mark_type}")


def analyze_adf(adf: dict) -> dict:
    """Analyze ADF structure and return statistics."""
    node_types = set()
    collect_node_types(adf, node_types)

    return {
        "node_types": sorted(node_types),
        "total_nodes": count_nodes(adf)
    }


def count_nodes(node: dict) -> int:
    """Count total nodes in ADF."""
    count = 1
    for child in node.get('content', []):
        count += count_nodes(child)
    return count


def find_nodes_by_type(node: dict, target_type: str, results: list, path: str = "root") -> None:
    """Find all nodes of a specific type."""
    if node.get('type') == target_type:
        results.append({"path": path, "node": node})

    for i, child in enumerate(node.get('content', [])):
        find_nodes_by_type(child, target_type, results, f"{path}.content[{i}]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Debug ADF content from Confluence")
    parser.add_argument("page_id", help="Confluence page ID")
    parser.add_argument("--raw", action="store_true", help="Output raw ADF JSON")
    parser.add_argument("--find", help="Find nodes of specific type")
    parser.add_argument("-o", "--output", help="Save raw ADF to file")

    args = parser.parse_args()

    # Fetch page
    print(f"Fetching page {args.page_id}...")
    data = fetch_raw_adf(args.page_id)

    print(f"Title: {data['title']}")
    print(f"Page ID: {data['id']}")
    print(f"Version: {data['version']['number']}")
    print()

    # Parse ADF
    adf_string = data['body']['atlas_doc_format']['value']
    adf = json.loads(adf_string)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(adf, f, indent=2, ensure_ascii=False)
        print(f"Raw ADF saved to: {args.output}")

    if args.raw:
        print("Raw ADF:")
        print(json.dumps(adf, indent=2, ensure_ascii=False))
    else:
        # Analyze
        analysis = analyze_adf(adf)
        print("Node types found in document:")
        for t in analysis['node_types']:
            print(f"  - {t}")
        print(f"\nTotal nodes: {analysis['total_nodes']}")

    if args.find:
        results = []
        find_nodes_by_type(adf, args.find, results)
        print(f"\nFound {len(results)} nodes of type '{args.find}':")
        for r in results:
            print(f"\nPath: {r['path']}")
            print(json.dumps(r['node'], indent=2, ensure_ascii=False))
