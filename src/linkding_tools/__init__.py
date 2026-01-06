#!/usr/bin/env python3
"""
Linkding Tools - Bookmark Management Toolkit
Supported features:
  - upload-markdown: Extract links from Markdown file and upload
  - upload-jsonl: Upload links from JSONL file
  - import-chrome: Import Chrome bookmarks
  - rename-tag: Batch rename tags
"""

import argparse
import json
import os
import re
import ssl
import sys
import http.client
import time
from pathlib import Path
from urllib.parse import urlparse, quote


# ============================================================
# Configuration
# ============================================================

def load_config():
    """Load configuration from environment variables or .env file"""
    config = {
        'url': os.getenv('LINKDING_URL'),
        'token': os.getenv('LINKDING_TOKEN')
    }
    
    # Try to read from .env file
    env_file = Path(__file__).parent.parent.parent / '.env'
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key == 'LINKDING_URL' and not config['url']:
                            config['url'] = value
                        elif key == 'LINKDING_TOKEN' and not config['token']:
                            config['token'] = value
        except Exception as e:
            print(f"Warning: Failed to read .env file - {e}")
    
    return config


def get_config_interactive(config):
    """Interactively get missing configuration"""
    if not config['url']:
        config['url'] = input("Please enter Linkding service URL: ").strip()
    if not config['token']:
        config['token'] = input("Please enter Linkding API Token: ").strip()
    return config


# ============================================================
# HTTP Utilities
# ============================================================

def make_request(method, path, config, data=None):
    """Send HTTP request"""
    parsed = urlparse(config['url'])
    
    if parsed.scheme == 'https':
        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(parsed.netloc, context=context)
    else:
        conn = http.client.HTTPConnection(parsed.netloc)
    
    headers = {
        "Authorization": f"Token {config['token']}",
        "Content-Type": "application/json"
    }
    
    body = json.dumps(data).encode('utf-8') if data else None
    
    try:
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        response_body = response.read().decode('utf-8')
        return response.status, response_body
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def test_connection(config):
    """Test API connection"""
    status, body = make_request("GET", "/api/bookmarks/?limit=1", config)
    return status == 200, status


def create_bookmark(url, tag_names, config):
    """Create a bookmark"""
    data = {
        "url": url,
        "tag_names": tag_names
    }
    
    status, body = make_request("POST", "/api/bookmarks/", config, data)
    
    if status in [200, 201]:
        return True, status, None
    else:
        return False, status, body


# ============================================================
# Markdown Parsing
# ============================================================

def is_valid_url(url):
    """Check if it is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_links_from_markdown(content, base_tag):
    """
    Extract links and corresponding tags from Markdown content
    Returns: [(url, tags), ...]
    """
    results = []
    lines = content.split('\n')
    current_sections = []
    
    for line in lines:
        # Check if it is a list item
        list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
        
        if list_match:
            indent = list_match.group(1)
            content_text = list_match.group(3).strip()
            level = len(indent) // 2 if indent else 0
            
            # Check if it is a markdown link
            has_md_link = bool(re.search(r'\[([^\]]*)\]\(https?://', content_text))
            
            if has_md_link:
                md_links = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content_text)
                for text, url in md_links:
                    url = re.sub(r'[,;。，；]+$', '', url)
                    if is_valid_url(url):
                        tags = [base_tag] + current_sections.copy() if base_tag else current_sections.copy()
                        results.append((url, tags))
            else:
                has_plain_url = bool(re.search(r'https?://', content_text))
                
                if has_plain_url:
                    plain_urls = re.findall(r'https?://[^\s\)]+', content_text)
                    for url in plain_urls:
                        url = re.sub(r'[,;。，；]+$', '', url)
                        if is_valid_url(url):
                            tags = [base_tag] + current_sections.copy() if base_tag else current_sections.copy()
                            results.append((url, tags))
                else:
                    # Plain title
                    clean_title = content_text
                    clean_title = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_title)
                    clean_title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_title)
                    
                    if level >= len(current_sections):
                        current_sections.append(clean_title)
                    else:
                        current_sections = current_sections[:level] + [clean_title]
        else:
            # Non-list item, check plain URL
            plain_urls = re.findall(r'https?://[^\s\)]+', line)
            for url in plain_urls:
                url = re.sub(r'[,;。，；]+$', '', url)
                if is_valid_url(url):
                    tags = [base_tag] + current_sections.copy() if base_tag else current_sections.copy()
                    results.append((url, tags))
    
    return results


# ============================================================
# Chrome Bookmarks Parsing
# ============================================================

def parse_chrome_bookmarks(html_content):
    """Parse Chrome bookmarks HTML file"""
    bookmarks = []
    folder_stack = []
    lines = html_content.split('\n')
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        indent_level = (len(line) - len(line.lstrip())) // 4
        
        # Handle folder closing: </DL> closes the folder at current indent_level
        # The folder at level N is stored at folder_stack[N-1], so we need to remove it
        if '</DL>' in line_stripped:
            # Keep only folders before this level (folder_stack[:N-1] for level N)
            if indent_level > 0:
                folder_stack = folder_stack[:indent_level-1]
        
        elif '<H3' in line_stripped:
            h3_match = re.search(r'>([^<]+)<', line_stripped)
            if h3_match:
                folder_name = h3_match.group(1).strip()
                folder_name = folder_name.replace('&amp;', '&')
                folder_name = folder_name.replace('&lt;', '<')
                folder_name = folder_name.replace('&gt;', '>')
                folder_name = folder_name.replace('&quot;', '"')
                folder_name = folder_name.replace('&apos;', "'")
                folder_stack = folder_stack[:indent_level] + [folder_name]
        
        elif '<A HREF=' in line_stripped:
            url_match = re.search(r'HREF="([^"]+)"', line_stripped)
            text_match = re.search(r'>([^<]+)<', line_stripped)
            
            if url_match:
                url = url_match.group(1)
                title = text_match.group(1) if text_match else ""
                
                if url.startswith('http://') or url.startswith('https://'):
                    tags = folder_stack[:indent_level] if indent_level > 0 else []
                    bookmarks.append({
                        'url': url,
                        'tags': tags,
                        'title': title
                    })
    
    return bookmarks


# ============================================================
# Tag Operations
# ============================================================

def get_bookmarks_with_tag(tag, config):
    """Get all bookmarks with specified tag"""
    all_bookmarks = []
    offset = 0
    limit = 100
    
    while True:
        query = quote(f"#{tag}")
        path = f"/api/bookmarks/?q={query}&limit={limit}&offset={offset}"
        
        status, body = make_request("GET", path, config)
        
        if status != 200:
            print(f"Failed to get bookmarks: {status} - {body}")
            return None
        
        data = json.loads(body)
        results = data.get("results", [])
        all_bookmarks.extend(results)
        
        if data.get("next") is None or len(results) < limit:
            break
        
        offset += limit
    
    return all_bookmarks


def update_bookmark_tags(bookmark_id, new_tags, config):
    """Update bookmark tags"""
    path = f"/api/bookmarks/{bookmark_id}/"
    data = {"tag_names": new_tags}
    
    status, body = make_request("PATCH", path, config, data)
    
    if status in [200, 201]:
        return True, None
    else:
        return False, f"{status}: {body}"


# ============================================================
# Command Implementations
# ============================================================

def cmd_upload_markdown(args, config):
    """Extract links from Markdown file and upload"""
    md_file = Path(args.file)
    
    if not md_file.exists():
        print(f"Error: File {md_file} does not exist")
        return 1
    
    # Read Markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Determine base tag
    base_tag = args.tag if args.tag else md_file.stem
    
    # Extract links
    links = extract_links_from_markdown(content, base_tag)
    
    if not links:
        print("No links found")
        return 0
    
    print(f"Found {len(links)} links")
    
    if not args.yes:
        confirm = input("\nStart upload? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Upload cancelled")
            return 0
    
    # Upload
    stats = {"success": 0, "skipped": 0, "failed": 0}
    
    for url, tags in links:
        success, status_code, error = create_bookmark(url, tags, config)
        
        if success or status_code in [200, 201]:
            stats["success"] += 1
            print(f"  ✓ {url[:60]}...")
        elif status_code == 400:
            stats["skipped"] += 1
            print(f"  ⊘ {url[:60]}... (already exists or invalid)")
        else:
            stats["failed"] += 1
            print(f"  ✗ {url[:60]}... (error: {status_code})")
        
        time.sleep(0.1)
    
    print(f"\nUpload completed: success {stats['success']}, skipped {stats['skipped']}, failed {stats['failed']}")
    return 0


def cmd_upload_jsonl(args, config):
    """Upload links from JSONL file"""
    jsonl_file = Path(args.file)
    
    if not jsonl_file.exists():
        print(f"Error: File {jsonl_file} does not exist")
        return 1
    
    # Read JSONL file
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    links = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                data = json.loads(line)
                url = data.get("url", "")
                tag_names = data.get("tag_names", [])
                if url:
                    links.append((url, tag_names))
            except json.JSONDecodeError:
                pass
    
    if not links:
        print("No links found")
        return 0
    
    print(f"Found {len(links)} links")
    
    if not args.yes:
        confirm = input("\nStart upload? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Upload cancelled")
            return 0
    
    # Upload
    stats = {"success": 0, "skipped": 0, "failed": 0}
    
    for url, tags in links:
        success, status_code, error = create_bookmark(url, tags, config)
        
        if success or status_code in [200, 201]:
            stats["success"] += 1
            print(f"  ✓ {url[:60]}...")
        elif status_code == 400:
            stats["skipped"] += 1
            print(f"  ⊘ {url[:60]}... (already exists or invalid)")
        else:
            stats["failed"] += 1
            print(f"  ✗ {url[:60]}... (error: {status_code})")
        
        time.sleep(0.1)
    
    print(f"\nUpload completed: success {stats['success']}, skipped {stats['skipped']}, failed {stats['failed']}")
    return 0


def cmd_import_chrome(args, config):
    """Import Chrome bookmarks"""
    html_file = Path(args.file)
    
    if not html_file.exists():
        print(f"Error: File {html_file} does not exist")
        return 1
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse bookmarks
    bookmarks = parse_chrome_bookmarks(html_content)
    
    if not bookmarks:
        print("No bookmarks found")
        return 0
    
    print(f"Found {len(bookmarks)} bookmarks")
    
    if not args.yes:
        confirm = input("\nStart import? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Import cancelled")
            return 0
    
    # import
    stats = {"success": 0, "skipped": 0, "failed": 0}
    
    for bookmark in bookmarks:
        url = bookmark['url']
        tags = [t for t in bookmark['tags'] if t and t.strip()]
        
        success, status_code, error = create_bookmark(url, tags, config)
        
        if success or status_code in [200, 201]:
            stats["success"] += 1
            tag_str = " > ".join(tags) if tags else "((no tags))"
            print(f"  ✓ [{tag_str}] {url[:50]}...")
        elif status_code == 400:
            stats["skipped"] += 1
            print(f"  ⊘ {url[:50]}... (already exists or invalid)")
        else:
            stats["failed"] += 1
            print(f"  ✗ {url[:50]}... (error: {status_code})")
        
        time.sleep(0.1)
    
    print(f"\nImport complete: success {stats['success']}, skipped {stats['skipped']}, failed {stats['failed']}")
    return 0


def cmd_rename_tag(args, config):
    """Batch rename tags"""
    old_tag = args.old_tag
    new_tag = args.new_tag
    
    if old_tag == new_tag:
        print("error: old tag and new tag are the same")
        return 1
    
    print(f"Replace tag [{old_tag}] with [{new_tag}]")
    
    # Get bookmarks with original tag
    print(f"\nSearching for bookmarks with tag [{old_tag}] ]...")
    bookmarks = get_bookmarks_with_tag(old_tag, config)
    
    if bookmarks is None:
        print("Failed to get bookmarks")
        return 1
    
    if not bookmarks:
        print(f"No bookmarks found with tag [{old_tag}] ")
        return 0
    
    print(f"Found {len(bookmarks)} bookmarks")
    
    if not args.yes:
        confirm = input("\nContinue with replacement? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled")
            return 0
    
    # Execute replacement
    stats = {"replaced": 0, "removed": 0, "failed": 0, "skipped": 0}
    
    for bookmark in bookmarks:
        bookmark_id = bookmark.get("id")
        url = bookmark.get("url", "")
        current_tags = bookmark.get("tag_names", [])
        
        if old_tag not in current_tags:
            stats["skipped"] += 1
            continue
        
        new_tags = current_tags.copy()
        
        if new_tag in new_tags:
            new_tags.remove(old_tag)
            action = "Delete"
        else:
            index = new_tags.index(old_tag)
            new_tags[index] = new_tag
            action = "Replace"
        
        success, error = update_bookmark_tags(bookmark_id, new_tags, config)
        
        if success:
            if action == "Delete":
                stats["removed"] += 1
            else:
                stats["replaced"] += 1
            print(f"  ✓ {action}: {url[:50]}...")
        else:
            stats["failed"] += 1
            print(f"  ✗ failed: {url[:50]}... ({error})")
    
    print(f"\nCompleted: Replaced {stats['replaced']}, removed (already has new tag) {stats['removed']}, skipped {stats['skipped']}, failed {stats['failed']}")
    return 0


# ============================================================
# Configuration Management Commands
# ============================================================

def cmd_setup_config(args):
    """Interactive configuration setup"""
    print("\n" + "=" * 60)
    print("Linkding Configuration Wizard")
    print("=" * 60)
    print("\nThis wizard will help you securely configure Linkding credentials.\n")
    
    # Read existing configuration
    env_file = Path(__file__).parent.parent.parent / '.env'
    existing_url = None
    existing_token = None
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key == 'LINKDING_URL':
                            existing_url = value
                        elif key == 'LINKDING_TOKEN':
                            existing_token = value
        except Exception as e:
            print(f"Warning: Failed to read existing configuration - {e}\n")
    
    # Ask for URL
    if existing_url:
        prompt = f"Linkding service URL [{existing_url}]: "
    else:
        prompt = "Linkding Service URL: "
    
    url = input(prompt).strip()
    if not url and existing_url:
        url = existing_url
    
    if not url:
        print("error: service URL cannot be empty")
        return 1
    
    # Ask for Token
    if existing_token:
        use_existing = input(f"\nUse existing Token？(y/n) [y]: ").strip().lower()
        if use_existing != 'n':
            token = existing_token
        else:
            token = input("New API Token: ").strip()
    else:
        token = input("\nAPI Token (get from Linkding Settings): ").strip()
    
    if not token:
        print("error: Token cannot be empty")
        return 1
    
    # Confirm configuration
    print("\n" + "-" * 60)
    print("Please confirm configuration：")
    print(f"  Service URL: {url}")
    print(f"  Token: {token[:10]}...{token[-5:]}" if len(token) > 15 else f"  Token: {token}")
    print("-" * 60)
    
    confirm = input("\nConfiguration is correct? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Configuration cancelled")
        return 0
    
    # Save to .env file
    env_file = Path(__file__).parent.parent.parent / '.env'
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# Linkding configuration\n")
            f.write(f"LINKDING_URL={url}\n")
            f.write(f"LINKDING_TOKEN={token}\n")
        
        print(f"\n✓ Configuration saved to {env_file}")
        print(f"✓ Configuration will be automatically loaded on next run\n")
        
        # Testing connection
        print("Testing connection...")
        config = {'url': url, 'token': token}
        success, status = test_connection(config)
        
        if success:
            print("✓ Connection test succeeded！\n")
            print("You can now use the following commands：")
            print("  uv run linkding-tools upload-markdown links.md")
            print("  uv run linkding-tools import-chrome bookmarks.html")
            print("  uv run linkding-tools")
            return 0
        else:
            print(f"✗ Connection failed (status code: {status})")
            print("Please check:")
            print("  1. LINKDING_URL is correct (including https://)")
            print("  2. LINKDING_TOKEN is valid")
            print("  3. Network connection is working\n")
            return 1
    
    except Exception as e:
        print(f"✗ failed to save configuration: {e}")
        return 1


def cmd_test_config(args):
    """Test if configuration is valid"""
    print("\n" + "=" * 60)
    print("Configuration Verification")
    print("=" * 60 + "\n")
    
    # Load configuration
    config = load_config()
    
    # Display configuration source
    if config['url']:
        print("✓ Found LINKDING_URL")
    else:
        print("✗ not Found LINKDING_URL")
        return 1
    
    if config['token']:
        print("✓ Found LINKDING_TOKEN")
    else:
        print("✗ not Found LINKDING_TOKEN")
        return 1
    
    # Testing connection
    print("\nTesting connection...")
    success, status = test_connection(config)
    
    if success:
        print(f"✓ Connection successful！")
        print(f"\nConfiguration is valid, you can start using：")
        print(f"  uv run linkding-tools")
        return 0
    else:
        print(f"✗ Connection failed (status code: {status})")
        print(f"\nService URL: {config['url']}")
        print(f"Token: {config['token'][:10]}...{config['token'][-5:] if len(config['token']) > 15 else config['token']}")
        print(f"\nPossible causes:")
        print(f"  • Service address is incorrect or offline")
        print(f"  • Token has expired or is invalid")
        print(f"  • Network connection issue\n")
        print(f"Run 'uv run linkding-tools setup-config' to reconfigure")
        return 1


def cmd_show_config(args):
    """Show current configuration (do not show complete token)"""
    print("\n" + "=" * 60)
    print("Current Configuration")
    print("=" * 60 + "\n")
    
    # Load configuration
    config = load_config()
    
    if config['url']:
        print(f"✓ Linkding URL: {config['url']}")
    else:
        print("✗ Linkding URL: Not configured")
    
    if config['token']:
        masked_token = f"{config['token'][:10]}...{config['token'][-5:]}"
        print(f"✓ API Token:     {masked_token}")
    else:
        print("✗ API Token:     Not configured")
    
    # Display configuration file location
    env_file = Path(__file__).parent.parent.parent / '.env'
    if env_file.exists():
        print(f"\nConfiguration file location: {env_file}")
    else:
        print(f"\nConfig file: does not exist ({env_file})")
        print("Tip: Run 'uv run linkding-tools setup-config' to create configuration")
    
    # Display loading priority
    print("\n" + "-" * 60)
    print("Configuration loading priority：")
    print("  1. Environment variables (LINKDING_URL, LINKDING_TOKEN)")
    print("  2. .env file")
    print("  3. Interactive prompts")
    print("-" * 60 + "\n")
    
    return 0


# ============================================================
# Interactive menu
# ============================================================

def interactive_menu(config):
    """Interactive menu"""
    while True:
        print("\n" + "=" * 50)
        print("Linkding Tools - Bookmark Management Tool")
        print("=" * 50)
        print(f"Service URL: {config['url']}")
        print("-" * 50)
        print("1. Upload links from Markdown file")
        print("2. Upload links from JSONL file")
        print("3. Import Chrome bookmarks")
        print("4. Rename tag")
        print("0. Exit")
        print("-" * 50)
        
        choice = input("Please select function [0-4]: ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        elif choice == '1':
            file_path = input("Please enter Markdown file path: ").strip()
            tag = input("Enter base tag (leave empty to use filename): ").strip() or None
            
            class Args:
                pass
            args = Args()
            args.file = file_path
            args.tag = tag
            args.yes = False
            
            cmd_upload_markdown(args, config)
        
        elif choice == '2':
            file_path = input("Please enter JSONL file path: ").strip()
            
            class Args:
                pass
            args = Args()
            args.file = file_path
            args.yes = False
            
            cmd_upload_jsonl(args, config)
        
        elif choice == '3':
            file_path = input("Enter Chrome bookmarks HTML file path: ").strip()
            
            class Args:
                pass
            args = Args()
            args.file = file_path
            args.yes = False
            
            cmd_import_chrome(args, config)
        
        elif choice == '4':
            old_tag = input("Enter old tag to replace: ").strip()
            new_tag = input("Enter new tag: ").strip()
            
            class Args:
                pass
            args = Args()
            args.old_tag = old_tag
            args.new_tag = new_tag
            args.yes = False
            
            cmd_rename_tag(args, config)
        
        else:
            print("Invalid selection, please try again")


# ============================================================
# Main Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Linkding Tools - Bookmark Management Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  LINKDING_URL     Linkding service URL
  LINKDING_TOKEN   API Token

Alternatively, set the above variables in .env file.

Examples:
  %(prog)s upload-markdown links.md
  %(prog)s upload-jsonl bookmarks.jsonl
  %(prog)s import-chrome bookmarks.html
  %(prog)s rename-tag python Python
  %(prog)s  # Enter interactive menu without parameters
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # setup-config
    p_setup = subparsers.add_parser('setup-config', help='Interactive configuration wizard (recommended for first-time use)')
    
    # test-config
    p_test = subparsers.add_parser('test-config', help='Test if current configuration is valid')
    
    # show-config
    p_show = subparsers.add_parser('show-config', help='Show current configuration (Token masked)')
    
    # upload-markdown
    p_md = subparsers.add_parser('upload-markdown', help='Extract links from Markdown file and upload')
    p_md.add_argument('file', help='Markdown file path')
    p_md.add_argument('-t', '--tag', help='Base tag (default: use filename)')
    p_md.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    
    # upload-jsonl
    p_jsonl = subparsers.add_parser('upload-jsonl', help='Upload links from JSONL file')
    p_jsonl.add_argument('file', help='JSONL file path')
    p_jsonl.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    
    # import-chrome
    p_chrome = subparsers.add_parser('import-chrome', help='Import Chrome bookmarks')
    p_chrome.add_argument('file', help='Chrome bookmarks HTML file path')
    p_chrome.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    
    # rename-tag
    p_tag = subparsers.add_parser('rename-tag', help='Batch rename tags')
    p_tag.add_argument('old_tag', help='Old tag name')
    p_tag.add_argument('new_tag', help='New tag name')
    p_tag.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # If no command, enter interactive mode
    if not args.command:
        config = get_config_interactive(config)
        
        if not config['url'] or not config['token']:
            print("error: LINKDING_URL and LINKDING_TOKEN configuration required")
            return 1
        
        # Testing connection
        print("\nTesting API connection...")
        success, status = test_connection(config)
        if not success:
            print(f"✗ Connection failed: {status}")
            return 1
        print("✓ Connection successful!")
        
        interactive_menu(config)
        return 0
    
    # Configuration management commands don't need connection test
    if args.command == 'setup-config':
        return cmd_setup_config(args)
    elif args.command == 'test-config':
        return cmd_test_config(args)
    elif args.command == 'show-config':
        return cmd_show_config(args)
    
    # Other commands need configuration
    if not config['url'] or not config['token']:
        config = get_config_interactive(config)
    
    if not config['url'] or not config['token']:
        print("error: LINKDING_URL and LINKDING_TOKEN configuration required")
        print("Configuration can be set in the following ways:")
        print("  1. Run 'uv run linkding-tools setup-config' for interactive configuration")
        print("  2. Set environment variables: export LINKDING_URL=... LINKDING_TOKEN=...")
        print("  3. Edit .env file")
        return 1
    
    # Testing connection
    success, status = test_connection(config)
    if not success:
        print(f"✗ API Connection failed: {status}")
        print("\nTip: Run 'uv run linkding-tools test-config' to diagnose the issue")
        return 1
    
    # Execute command
    if args.command == 'upload-markdown':
        return cmd_upload_markdown(args, config)
    elif args.command == 'upload-jsonl':
        return cmd_upload_jsonl(args, config)
    elif args.command == 'import-chrome':
        return cmd_import_chrome(args, config)
    elif args.command == 'rename-tag':
        return cmd_rename_tag(args, config)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
