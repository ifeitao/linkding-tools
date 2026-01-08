# Feature Implementation Summary: One-to-Many Tag Replacement

## Overview

Successfully enhanced the `rename-tag` command to support converting a single tag into multiple tags. This feature is useful for splitting compound tags, consolidating tags, or reorganizing bookmark categorization.

## Changes Made

### 1. Core Functionality (`src/linkding_tools/__init__.py`)

#### Modified: `cmd_rename_tag()` Function
- **Old behavior**: Only supported one-to-one tag replacement
- **New behavior**: Supports both one-to-one and one-to-many replacements

**Key improvements:**
- Parses comma-separated new tags from input string
- Strips whitespace around commas automatically
- Prevents duplicate tags (if target tag already exists on bookmark, won't add again)
- Maintains tag position (new tags inserted at original tag position)
- Updated action messages to reflect the operation type

**Example:**
```python
# Old: "数据集下载" -> "新标签" (only one replacement)
# New: "数据集下载" -> "数据集,下载" (multiple replacements)
```

#### Modified: Command-line Arguments
- Updated help text to describe comma-separated syntax
- Changed `new_tag` description to clarify multi-tag support

#### Modified: Interactive Menu
- Updated prompt to mention comma-separation for multiple tags

### 2. Testing (`tests/test_rename_tag.py`)

Added comprehensive test suite with 7 test cases:

1. **test_rename_single_tag_to_single_tag**: Verify one-to-one rename still works
2. **test_rename_single_tag_to_multiple_tags**: Verify one-to-many expansion works
3. **test_rename_to_multiple_tags_with_duplicates**: Prevent duplicate tags
4. **test_rename_same_tag_error**: Error handling for same old/new tags
5. **test_rename_empty_new_tag_error**: Error handling for empty tags
6. **test_rename_tag_not_found**: Handle missing tags gracefully
7. **test_rename_tag_with_spaces_in_multiple_tags**: Verify whitespace trimming

**Test Results:** ✅ All 7 tests passing
**Full Test Suite:** ✅ All 59 tests passing (no regressions)

### 3. Documentation

#### Updated: README.md
- Added new section explaining one-to-many functionality
- Included usage examples for both one-to-one and one-to-many
- Listed features and benefits

#### Updated: README_zh-CN.md
- Chinese documentation with the same enhancements
- Example: "数据集下载" -> "数据集,下载"

#### Created: TAG_REPLACEMENT_GUIDE.md
- Quick reference guide for the feature
- Use cases and examples
- Important notes about whitespace and duplicates
- Workflow examples

## Usage Examples

### Basic One-to-One (Unchanged)
```bash
uv run linkding-tools rename-tag python Python
```

### New One-to-Many Feature
```bash
# Split a compound tag into components
uv run linkding-tools rename-tag "数据集下载" "数据集,下载"

# Whitespace is automatically trimmed
uv run linkding-tools rename-tag "OldTag" "Tag1 , Tag2 , Tag3"

# Works with English tags too
uv run linkding-tools rename-tag "MachineLearning" "Machine,Learning"
```

### Interactive Menu
```bash
uv run linkding-tools
# Select option 4: Rename tag
# Old tag: 数据集下载
# New tags: 数据集,下载
```

## Technical Implementation Details

### Tag Processing Algorithm
1. Parse comma-separated input: `"tag1,tag2,tag3".split(',')`
2. Strip whitespace: `[t.strip() for t in tags]`
3. Remove empty strings: `[t for t in tags if t]`
4. For each bookmark with old_tag:
   - Find old_tag position in tag list
   - Remove old_tag
   - Insert new tags at that position
   - Skip tags that already exist (prevent duplicates)
   - Update bookmark via API

### Backward Compatibility
✅ All existing one-to-one rename operations continue to work unchanged
✅ No breaking changes to API or command syntax
✅ All previous tests still pass

## File Changes

| File | Changes | Type |
|------|---------|------|
| `src/linkding_tools/__init__.py` | 64 additions, 24 deletions | Implementation |
| `tests/test_rename_tag.py` | New file (7 tests) | Tests |
| `README.md` | Enhanced documentation | Docs |
| `README_zh-CN.md` | Enhanced documentation | Docs |
| `TAG_REPLACEMENT_GUIDE.md` | New quick reference | Docs |

## Commits

1. **Fix Chrome bookmarks folder parsing issue** (0eaf356)
   - Fixed bug with sibling folders inheriting tags
   - Added comprehensive test case

2. **Feature: Support one-to-many tag replacement** (a1ba6b3)
   - Core implementation
   - Test suite (7 tests)
   - Documentation updates

3. **Add tag replacement feature quick reference guide** (e9bec63)
   - Quick reference guide with examples

## Test Coverage

### New Tests (7)
- ✅ Single-to-single tag replacement
- ✅ Single-to-multiple tag replacement
- ✅ Duplicate prevention
- ✅ Error handling (same tag)
- ✅ Error handling (empty tags)
- ✅ Missing tag handling
- ✅ Whitespace trimming

### Regression Testing
- ✅ All 52 existing tests continue to pass
- ✅ Total test suite: 59 passing tests

## Status

✅ **COMPLETE AND DEPLOYED**

The feature is fully implemented, tested, documented, and pushed to GitHub.

### Ready for Use
```bash
# Clone or update to latest
git pull origin main

# Run with new feature
uv run linkding-tools rename-tag "old_tag" "new_tag1,new_tag2"
```
