#!/usr/bin/env python3
"""
Simple Website Crawler using Firecrawl
Downloads a website to N level depth and saves as markdown files.
"""

import os
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, ScrapeOptions

load_dotenv()

def create_safe_filename(url, page_title="", max_length=100):
    """Create a safe filename from URL and page title."""
    parsed = urlparse(url)
    
    # Use page title if available, otherwise use path
    if page_title:
        base_name = page_title.strip()
    else:
        path = parsed.path.strip('/')
        base_name = path.replace('/', '_') if path else 'index'
    
    # Clean filename
    safe_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    safe_name = ''.join(c for c in base_name if c in safe_chars)
    
    # Truncate if too long
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    
    return safe_name if safe_name else 'page'

def save_crawl_results(crawl_result, base_url, output_dir="firecrawl_output"):
    """Save crawl results to organized markdown files."""
    
    # Create output directory structure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(base_url).netloc.replace('.', '_')
    crawl_dir = Path(output_dir) / f"{domain}_{timestamp}"
    crawl_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metadata - access object attributes instead of dict keys
    metadata = {
        'base_url': base_url,
        'crawl_timestamp': timestamp,
        'total_pages': getattr(crawl_result, 'total', 0),
        'status': getattr(crawl_result, 'status', 'unknown'),
        'credits_used': getattr(crawl_result, 'creditsUsed', 0)
    }
    
    with open(crawl_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Save individual pages
    pages_dir = crawl_dir / 'pages'
    pages_dir.mkdir(exist_ok=True)
    
    saved_files = []
    
    # Access data attribute directly instead of using .get()
    crawl_data = getattr(crawl_result, 'data', [])
    
    for idx, page in enumerate(crawl_data):
        # Handle both dict and object access patterns
        if hasattr(page, 'metadata'):
            page_metadata = page.metadata
            page_url = getattr(page_metadata, 'sourceURL', f'page_{idx}')
            page_title = getattr(page_metadata, 'title', '')
            markdown_content = getattr(page, 'markdown', '')
        else:
            # Fallback to dict access
            page_metadata = page.get('metadata', {})
            page_url = page_metadata.get('sourceURL', f'page_{idx}')
            page_title = page_metadata.get('title', '')
            markdown_content = page.get('markdown', '')
        
        # Create filename
        filename = create_safe_filename(page_url, page_title)
        file_path = pages_dir / f"{idx:03d}_{filename}.md"
        
        # Ensure unique filename
        counter = 1
        while file_path.exists():
            file_path = pages_dir / f"{idx:03d}_{filename}_{counter}.md"
            counter += 1
        
        # Save markdown content
        if markdown_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Add header with metadata
                f.write(f"# {page_title}\n\n")
                f.write(f"**URL:** {page_url}\n\n")
                f.write(f"**Crawled:** {timestamp}\n\n")
                f.write("---\n\n")
                f.write(markdown_content)
            
            saved_files.append({
                'filename': file_path.name,
                'url': page_url,
                'title': page_title
            })
    
    # Save index file
    with open(crawl_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write(f"# Crawl Results: {domain}\n\n")
        f.write(f"**Base URL:** {base_url}\n")
        f.write(f"**Crawled:** {timestamp}\n")
        f.write(f"**Total Pages:** {len(saved_files)}\n\n")
        f.write("## Pages\n\n")
        
        for file_info in saved_files:
            f.write(f"- [{file_info['title'] or 'Untitled'}](pages/{file_info['filename']}) - {file_info['url']}\n")
    
    return crawl_dir, len(saved_files)

def crawl_website(url, depth=2, max_pages=100):
    """
    Crawl a website to specified depth using Firecrawl.
    
    Args:
        url (str): The base URL to crawl
        depth (int): Maximum depth to crawl (0 = only base URL, 1 = base + direct links, etc.)
        max_pages (int): Maximum number of pages to crawl
    
    Returns:
        tuple: (crawl_result, output_directory)
    """
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Firecrawl
    app = FirecrawlApp()  # Will use FIRECRAWL_API_KEY from environment
    
    print(f"Starting crawl of: {url}")
    print(f"Max depth: {depth}")
    print(f"Max pages: {max_pages}")
    print("="*50)
    
    try:
        # Perform the crawl with correct parameters
        crawl_result = app.crawl_url(
            url=url,
            limit=max_pages,
            max_depth=depth,  # Changed from maxDepth to max_depth
            scrape_options=ScrapeOptions(
                formats=['markdown'],
                onlyMainContent=True  # Get cleaner content without headers/footers
            )
        )
        
        print(f"Crawl completed!")
        print(f"Status: {getattr(crawl_result, 'status', 'unknown')}")
        print(f"Total pages: {getattr(crawl_result, 'total', 0)}")
        print(f"Credits used: {getattr(crawl_result, 'creditsUsed', 0)}")
        
        # Save results
        output_dir, saved_count = save_crawl_results(crawl_result, url)
        
        print(f"Saved {saved_count} pages to: {output_dir}")
        print("\nFiles created:")
        print(f"  - {output_dir}/metadata.json (crawl metadata)")
        print(f"  - {output_dir}/index.md (page index)")
        print(f"  - {output_dir}/pages/ (individual markdown files)")
        
        return crawl_result, output_dir
        
    except Exception as e:
        print(f"Error during crawl: {e}")
        raise

def main():
    """Main function with command line argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="🔥 Firecrawl Website Crawler - Downloads websites to markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://docs.firecrawl.dev
  python main.py --url https://example.com --depth 3 --max-pages 100
  python main.py -u https://blog.example.com -d 1 -m 25
        """
    )
    
    parser.add_argument(
        '-u', '--url', 
        required=True,
        help='The base URL to crawl (required)'
    )
    
    parser.add_argument(
        '-d', '--depth', 
        type=int, 
        default=2,
        help='Maximum crawl depth (default: 2)'
    )
    
    parser.add_argument(
        '-m', '--max-pages', 
        type=int, 
        default=50,
        help='Maximum number of pages to crawl (default: 50)'
    )
    
    args = parser.parse_args()
    
    print("🔥 Firecrawl Website Crawler")
    print("="*40)
    
    # Check if API key is available
    if not os.getenv('FIRECRAWL_API_KEY'):
        print("❌ Error: FIRECRAWL_API_KEY not found in environment variables.")
        print("Please set your Firecrawl API key in the .env file:")
        print("FIRECRAWL_API_KEY=fc-your-api-key-here")
        return
    
    try:
        # Perform the crawl with command line arguments
        result, output_path = crawl_website(
            url=args.url,
            depth=args.depth,
            max_pages=args.max_pages
        )
        
        print(f"\n✅ Crawl completed successfully!")
        print(f"📁 Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Crawl failed: {e}")

if __name__ == "__main__":
    main()