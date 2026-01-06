# Linkding Tools

[中文文档](README_zh-CN.md) | English

A powerful toolkit for managing Linkding bookmarks, supporting imports from multiple data sources.

## Features

### Configuration Management Commands (First-Time Setup)

#### `setup-config` - Interactive Configuration Wizard
Run this command for secure interactive configuration before first use:

```bash
uv run linkding-tools setup-config
```

This command will:
1. Prompt for Linkding service URL
2. Prompt for API Token
3. Validate the configuration
4. Save configuration to `.env` file

#### `test-config` - Validate Configuration
Test if current configuration can connect to Linkding service:

```bash
uv run linkding-tools test-config
```

#### `show-config` - Display Current Configuration
Show currently loaded configuration (Token will be masked):

```bash
uv run linkding-tools show-config
```

### Functional Commands

### 1. Upload Markdown File (`upload-markdown`)
Extract links and tags from a single Markdown file and upload to Linkding.

**Features:**
- Supports Markdown link format: `[text](URL)`
- Supports plain URLs: `https://example.com`
- Automatically generates multi-level tags from list structure
- Supports custom base tags

**Example Markdown File Structure:**
```markdown
# Tutorials

## Python

- [Python Official Site](https://www.python.org)
- [Flask Documentation](https://flask.palletsprojects.com)

## JavaScript

- [Node.js](https://nodejs.org)
- https://www.npmjs.com
```

**Usage:**
```bash
# Basic usage (uses filename as base tag)
python3 linkding-tools.py upload-markdown links.md

# Specify base tag
python3 linkding-tools.py upload-markdown links.md -t programming-tutorials

# Skip confirmation
python3 linkding-tools.py upload-markdown links.md -y
```

### 2. Upload JSONL File (`upload-jsonl`)
Upload link data in JSONL format (one JSON object per line).

**JSONL Format:**
```jsonl
{"url": "https://example.com", "tag_names": ["tag1", "tag2"]}
{"url": "https://example.org", "tag_names": ["tag1", "tag3"]}
```

**Usage:**
```bash
python3 linkding-tools.py upload-jsonl bookmarks.jsonl

# Skip confirmation
python3 linkding-tools.py upload-jsonl bookmarks.jsonl -y
```

### 3. Import Chrome Bookmarks (`import-chrome`)
Import bookmarks HTML file exported from Chrome, automatically preserving folder structure as tags.

**Usage:**
```bash
# After exporting bookmarks from Chrome (HTML format), run:
python3 linkding-tools.py import-chrome bookmarks_2026_1_6.html

# Skip confirmation
python3 linkding-tools.py import-chrome bookmarks_2026_1_6.html -y
```

### 4. Rename Tags (`rename-tag`)
Batch rename tags in Linkding.

**Usage:**
```bash
# Replace tag "python" with "Python"
python3 linkding-tools.py rename-tag python Python

# Skip confirmation
python3 linkding-tools.py rename-tag python Python -y
```

## Installation

### Using uv (Recommended)

```bash
# Clone or navigate to project directory
cd /path/to/links

# Install dependencies with uv
uv sync
```

### Using pip

```bash
python3 -m pip install -r requirements.txt
```

## First-Time Configuration (Required)

### Method 1: Interactive Configuration Wizard (Recommended)

```bash
# First time use, run configuration wizard
uv run linkding-tools setup-config

# Follow prompts to enter Linkding service URL and API Token
# Configuration will be automatically saved to .env file
```

### Method 2: Manual .env File Configuration

```bash
# Copy configuration template
cp .env.example .env

# Edit .env file, fill in actual configuration
# LINKDING_URL=https://your-linkding-instance.com
# LINKDING_TOKEN=your_api_token_here
```

### Method 3: Environment Variables

```bash
export LINKDING_URL=https://your-linkding-instance.com
export LINKDING_TOKEN=your_api_token_here
uv run linkding-tools
```

### Verify Configuration

After configuration, verify it's valid:

```bash
uv run linkding-tools test-config
```

## Configuration

### Configuration Commands (Recommended)

Use built-in configuration management commands to manage credentials:

```bash
# Interactive configuration (recommended for first-time use)
uv run linkding-tools setup-config

# Verify configuration is valid
uv run linkding-tools test-config

# View current configuration (Token masked)
uv run linkding-tools show-config
```

### Configuration Loading Priority

The tool loads configuration in the following priority order:

1. **Environment Variables** - `LINKDING_URL` and `LINKDING_TOKEN` (highest priority)
2. **.env File** - `.env` file in project root directory
3. **Interactive Prompts** - Automatically prompts for missing configuration (lowest priority)

### Method 1: Environment Variables (Recommended for CI/CD)

```bash
export LINKDING_URL=https://your-linkding-instance.com
export LINKDING_TOKEN=your_api_token_here
uv run linkding-tools upload-markdown links.md
```

### Method 2: .env File (Recommended for Local Development)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```
   LINKDING_URL=https://your-linkding-instance.com
   LINKDING_TOKEN=your_api_token_here
   ```

3. Run the tool directly, it will automatically read `.env` file:
   ```bash
   python3 linkding-tools.py upload-markdown links.md
   ```

### Method 3: Interactive Input

When environment variables or .env file are not provided, the tool will prompt interactively:
```bash
python3 linkding-tools.py upload-markdown links.md
# Will prompt for LINKDING_URL and LINKDING_TOKEN
```

## Usage Modes

### Command-Line Mode

Execute tasks directly using subcommands:

```bash
# View all available commands
python3 linkding-tools.py --help

# View help for specific command
python3 linkding-tools.py upload-markdown --help

# Execute command
python3 linkding-tools.py upload-markdown links.md -t my-tag
```

### Interactive Menu

Run without any parameters to enter interactive menu:

```bash
python3 linkding-tools.py
```

The menu displays all available features and guides you through operations step by step:

```
==================================================
Linkding Tools - Bookmark Management Tool
==================================================
Service URL: https://your-linkding-instance.com
--------------------------------------------------
1. Upload links from Markdown file
2. Upload links from JSONL file
3. Import Chrome bookmarks
4. Rename tag
0. Exit
--------------------------------------------------
Please select function [0-4]:
```

## Getting API Token

1. Log in to your Linkding instance
2. Click on user avatar in top right corner, select "Settings"
3. In "API" or "API Token" section, generate or copy your token
4. Save it to `.env` file

## Quick Start

### 1. Installation and Configuration

```bash
# Clone or navigate to project directory
cd /path/to/links

# Install dependencies with uv
uv sync

# Interactive configuration (recommended)
uv run linkding-tools setup-config

# Verify configuration
uv run linkding-tools test-config
```

### 2. Basic Usage

```bash
# Interactive menu (suitable for beginners)
uv run linkding-tools

# Command-line mode (quick execution)
uv run linkding-tools upload-markdown links.md
uv run linkding-tools import-chrome bookmarks.html
uv run linkding-tools rename-tag old-tag new-tag
```

### 3. Common Tasks

**Import Chrome Bookmarks**
```bash
# 1. Chrome → Bookmarks → Bookmark Manager → Export bookmarks
# 2. Run import command
uv run linkding-tools import-chrome bookmarks.html
```

**Upload Markdown Notes**
```bash
# Create Markdown file
# ## Category 1
# - [Link 1](https://example1.com)

uv run linkding-tools upload-markdown mylinks.md
```

## Configuration Details

### Configuration Priority

The tool loads configuration in the following priority order:
1. **Environment Variables** (highest) - `LINKDING_URL` and `LINKDING_TOKEN`
2. **.env File** - `.env` file in project root directory
3. **Interactive Prompts** (lowest) - Automatically prompts when missing

### Configuration Methods for Different Scenarios

| Scenario | Recommended Method | Example |
|----------|-------------------|---------|  
| Local Development | .env file | `uv run linkding-tools setup-config` |
| CI/CD | Environment variables | `export LINKDING_URL=... LINKDING_TOKEN=...` |
| Docker | Environment variables | `docker run -e LINKDING_URL=...` |
| First-time Use | Interactive | `uv run linkding-tools setup-config` |

### Configuration Commands

```bash
# Interactive configuration wizard
uv run linkding-tools setup-config

# Verify configuration validity
uv run linkding-tools test-config

# View current configuration (Token masked)
uv run linkding-tools show-config
```

## Getting API Token

1. Log in to your Linkding instance
2. Click on user avatar in top right corner, select "Settings"
3. In "API" or "API Token" section, generate or copy your token
4. Save it to `.env` file

## Workflow Examples

### Scenario 1: Import Chrome Bookmarks

```bash
# 1. Export bookmarks from Chrome as HTML file
# Chrome Menu > Bookmarks > Bookmark Manager > Top right menu > Export bookmarks

# 2. Import using the tool
python3 linkding-tools.py import-chrome bookmarks.html

# 3. Confirm import
Start import? (y/n): y

# Success! All bookmarks imported, preserving original folder structure as tags
```

### Scenario 2: Organize Markdown Notes and Upload

```bash
# 1. Create Markdown file, organize links by structure
# Example: dev-tools.md, with multiple categories

# 2. Upload to Linkding
python3 linkding-tools.py upload-markdown dev-tools.md

# 3. Links will automatically be tagged according to Markdown's hierarchical structure
# For example:
# - Base tag: dev-tools
# - Multi-level tags: dev-tools > IDE, dev-tools > version-control
```

### Scenario 3: Batch Rename Tags

```bash
# 1. Found a tag name that needs to be unified
python3 linkding-tools.py rename-tag python Python

# 2. All links with "python" tag will be automatically updated to "Python"
# If link already has "Python" tag, only removes "python" tag
```

## Project Structure

```
links/
├── src/linkding_tools/          # Main module
│   ├── __init__.py              # Main implementation
│   └── __main__.py              # Entry point
├── bak/                         # Backup of old scripts (excluded)
├── tmp/                         # Test files (excluded)
├── linkding-tools.py            # Standalone executable version
├── pyproject.toml               # uv project configuration
├── README.md                    # This file
├── README_zh-CN.md              # Chinese documentation
└── .env.example                 # Configuration template
```

## Advanced Usage

### Batch Processing

```bash
#!/bin/bash
# Upload multiple Markdown files in batch

for file in *.md; do
    echo "Processing $file..."
    uv run linkding-tools upload-markdown "$file" -y
done
```

### Integration with Other Tools

```bash
# Generate Markdown from URL list file
# Then upload to Linkding

# Or use pipes
cat url_list.txt | uv run linkding-tools upload-markdown -
```

## Troubleshooting

### Connection Failed

```bash
# Run diagnostic command
uv run linkding-tools test-config

# Common issues:
# 1. Is LINKDING_URL correct (including https://)?
# 2. Is LINKDING_TOKEN valid?
# 3. Is network connection working?
```

### Configuration Not Taking Effect

```bash
# Check environment variables (higher priority)
echo $LINKDING_URL
echo $LINKDING_TOKEN

# Clear environment variables
unset LINKDING_URL LINKDING_TOKEN

# Verify configuration
uv run linkding-tools show-config
```

### Import Fails Midway

The tool displays processing results for each link:
- Successfully uploaded links won't be duplicated
- Use `-y` parameter to skip confirmation and speed up retry

## Project Structure

```
links/
├── src/linkding_tools/          # Main module
│   ├── __init__.py              # Main implementation
│   └── __main__.py              # Entry point
├── bak/                         # Backup of old scripts (excluded)
├── tmp/                         # Test files (excluded)
├── linkding-tools.py            # Standalone executable version
├── pyproject.toml               # uv project configuration
├── README.md                    # This file
├── README_zh-CN.md              # Chinese documentation
└── .env.example                 # Configuration template
```

## Project Dependencies

This project uses uv to manage dependencies, currently only depends on Python standard library:
- `json` - Handle JSON/JSONL data
- `re` - Regular expression parsing
- `http.client` - HTTP requests
- `ssl` - HTTPS support
- `urllib.parse` - URL parsing

## Contributing

Issues and Pull Requests are welcome!

## License

MIT
