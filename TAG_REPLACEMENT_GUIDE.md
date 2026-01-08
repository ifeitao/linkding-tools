# Tag Replacement Feature - Quick Reference

## Overview

The `rename-tag` command has been enhanced to support both one-to-one and one-to-many tag replacement operations.

## Syntax

```bash
# Basic syntax
uv run linkding-tools rename-tag <old_tag> <new_tags>

# With confirmation skip
uv run linkding-tools rename-tag <old_tag> <new_tags> -y
```

## Use Cases

### 1. One-to-One Rename (Traditional)
Replace a single tag with another single tag.

```bash
# Rename "python" to "Python"
uv run linkding-tools rename-tag python Python

# Rename Chinese tags
uv run linkding-tools rename-tag "机器学习" "ML"
```

### 2. One-to-Many Expansion (New Feature)
Replace a single tag with multiple tags, useful for:
- Splitting compound tags into components
- Consolidating tags for better organization

```bash
# Split "数据集下载" into "数据集" and "下载"
uv run linkding-tools rename-tag "数据集下载" "数据集,下载"

# Split "MachineLearning" into "Machine,Learning"
uv run linkding-tools rename-tag "MachineLearning" "Machine,Learning"

# Expand to three tags (with spaces - they're trimmed automatically)
uv run linkding-tools rename-tag "OldTag" "Tag1 , Tag2 , Tag3"
```

## Important Notes

### Whitespace Handling
- Whitespace around commas is automatically trimmed
- These all produce the same result:
  ```bash
  "tag1,tag2,tag3"
  "tag1, tag2, tag3"
  "tag1 , tag2 , tag3"
  ```

### Duplicate Prevention
- If a new tag already exists on a bookmark, it won't be added again
- This prevents duplicate tags

Example:
```bash
# If bookmark has tags: ["old_tag", "existing"]
# Running: rename-tag "old_tag" "new_tag,existing"
# Result: ["new_tag", "existing"]  (no duplicate "existing")
```

### Tag Position
- New tags are inserted at the position where the old tag was
- This helps maintain a logical tag ordering

## Example Workflow

Suppose you have many bookmarks tagged with "MachineLearning" but want to split them into "Machine" and "Learning":

```bash
# Step 1: Check what you're about to do (without -y flag)
uv run linkding-tools rename-tag "MachineLearning" "Machine,Learning"
# Output shows found X bookmarks

# Step 2: Press 'y' to confirm when prompted

# Step 3: Verify in Linkding that bookmarks now have both tags
```

## Comparison with Previous Behavior

| Operation | Old Behavior | New Behavior |
|-----------|-------------|--------------|
| `rename-tag python Python` | ✓ Works | ✓ Works (unchanged) |
| `rename-tag old "new"` | ✓ Works | ✓ Works (unchanged) |
| `rename-tag tag1 "tag2,tag3"` | ✗ Not supported | ✓ Works (new!) |
| `rename-tag tag "tag1, tag2"` | ✗ Not supported | ✓ Works (new!) |

## Command-Line Help

```bash
uv run linkding-tools rename-tag --help
```

This will show:
- All available options
- Help text explaining the comma-separated syntax
