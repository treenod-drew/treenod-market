---
title: ADF Spacing Improvement Spec
created: 2025-01-14
status: completed
version: 0.1.0
---

## Overview

Confluence pages rendered from ADF have poor vertical spacing around horizontal rules (`---`) and headings (`##`). The default line height in Confluence makes these elements appear cramped without additional spacing.

## Problem

### Current Behavior

When markdown like this is converted to ADF:

```markdown
Some paragraph text.

---

## Section Title
```

The rendered Confluence page shows:
- Horizontal rule too close to preceding content
- H2 headings too close to preceding content
- Overall cramped appearance

### Root Cause

Atlassian's default page styling has insufficient line-height for visual separation. The ADF structure itself is correct, but needs additional empty paragraphs to create visual breathing room.

## Solution

Insert an empty paragraph node before `rule` and `heading` nodes in ADF output to create visual spacing.

### ADF Empty Paragraph

```json
{"type": "paragraph", "content": []}
```

This creates a blank line without any text content, providing vertical spacing in the rendered page.

### Target Elements

| Element | Markdown | ADF Type | Add Spacing Before |
|---------|----------|----------|-------------------|
| Horizontal rule | `---`, `***`, `___` | `rule` | Yes |
| Heading 2 | `##` | `heading` (level: 2) | Yes |
| Heading 3 | `###` | `heading` (level: 3) | Yes |
| Heading 4 | `####` | `heading` (level: 4) | Yes |

Note: H1 (`#`) is typically the page title and appears at the top, so no spacing is added before it.

### Expected Output

Input markdown:

```markdown
Some text.

---

## Section
```

Current ADF output:

```json
{
  "type": "doc",
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Some text."}]},
    {"type": "rule"},
    {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Section"}]}
  ]
}
```

Expected ADF output with spacing:

```json
{
  "type": "doc",
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Some text."}]},
    {"type": "paragraph", "content": []},
    {"type": "rule"},
    {"type": "paragraph", "content": []},
    {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Section"}]}
  ]
}
```

## Implementation

### Files to Modify

1. `scripts/adf_converter.py` - `markdown_to_adf()` function
2. `scripts/html_to_adf.py` - `html_to_adf()` function

### Approach

Add a post-processing step after building the content list that inserts empty paragraphs before target nodes.

```python
def add_spacing_before_blocks(content: list) -> list:
    """
    Add empty paragraph before rule and heading nodes for visual spacing.

    Args:
        content: List of ADF content nodes

    Returns:
        list: Content with spacing paragraphs inserted
    """
    result = []
    empty_para = {"type": "paragraph", "content": []}

    for i, node in enumerate(content):
        node_type = node.get("type")

        # Add spacing before rule (but not at document start)
        if node_type == "rule" and i > 0:
            result.append(empty_para.copy())

        # Add spacing before h2-h4 headings (but not at document start)
        if node_type == "heading" and i > 0:
            level = node.get("attrs", {}).get("level", 1)
            if level >= 2:
                result.append(empty_para.copy())

        result.append(node)

    return result
```

### Integration Points

#### adf_converter.py

In `markdown_to_adf()`, apply post-processing before returning:

```python
def markdown_to_adf(markdown: str) -> dict:
    # ... existing parsing logic ...

    # Add spacing for better Confluence rendering
    content = add_spacing_before_blocks(content)

    return {
        "version": 1,
        "type": "doc",
        "content": content
    }
```

#### html_to_adf.py

In `html_to_adf()`, apply post-processing to the nodes list:

```python
def html_to_adf(html_content: str) -> list:
    # ... existing parsing logic ...

    # Add spacing for better Confluence rendering
    nodes = add_spacing_before_blocks(nodes)

    return nodes
```

## Testing

### Manual Test

1. Create markdown with horizontal rules and h2/h3/h4 headings
2. Convert to ADF using the updated converter
3. Create Confluence page with the ADF content
4. Verify visual spacing is improved

### Test Cases

| Input | Expected Spacing |
|-------|-----------------|
| `text\n---` | Empty para before rule |
| `text\n## H2` | Empty para before h2 |
| `# H1\n## H2` | Empty para before h2 |
| `---\n## H2` | Empty para before rule, empty para before h2 |
| `## H2` (at start) | No spacing (first element) |

## Rollout

### Phase 1

1. Implement `add_spacing_before_blocks()` in both converters
2. Test with sample documents

### Phase 2

3. Monitor for edge cases (nested content, tables, etc.)
4. Adjust spacing rules if needed
