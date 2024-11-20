import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import csv
from datetime import datetime
from urllib.parse import urljoin
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

def check_link(url: str, base_url: str) -> Tuple[str, bool, str]:
    """Check if a link is accessible"""
    try:
        full_url = urljoin(base_url, url)
        response = requests.head(full_url, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            return url, False, f"Broken link (Status {response.status_code})"
        return url, True, "OK"
    except requests.RequestException as e:
        return url, False, f"Failed to access: {str(e)}"

def find_html_issues(html_content: str, url: str) -> List[str]:
    """Find HTML tag issues using BeautifulSoup"""
    soup = BeautifulSoup(html_content, 'html.parser')
    issues = []
    
    # Check for empty tags that should have content
    for tag in soup.find_all(['div', 'p', 'span', 'a']):
        if not tag.contents and not tag.get('href') and not tag.get('id') and not tag.get('class'):
            issues.append(f"Empty {tag.name} tag found")
    
    # Check images
    for img in soup.find_all('img'):
        if not img.get('alt'):
            issues.append(f"Image missing alt text: {img.get('src', 'unknown source')}")
        if not img.get('src'):
            issues.append("Image missing src attribute")
        
    # Check for duplicate IDs
    ids = {}
    for tag in soup.find_all(attrs={'id': True}):
        id_value = tag.get('id')
        if id_value in ids:
            issues.append(f"Duplicate ID found: {id_value}")
        ids[id_value] = True
    
    # Check heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if not soup.find('h1'):
        issues.append("No H1 heading found")
    prev_level = 0
    for heading in headings:
        current_level = int(heading.name[1])
        if current_level > prev_level + 1:
            issues.append(f"Heading level skipped: from h{prev_level} to h{current_level}")
        prev_level = current_level

    # Check for deprecated HTML tags
    deprecated_tags = ['center', 'font', 'strike', 'u', 'marquee', 'blink']
    for tag in deprecated_tags:
        found_tags = soup.find_all(tag)
        if found_tags:
            issues.append(f"Deprecated tag found: {tag} ({len(found_tags)} instances)")

    # Check forms
    for form in soup.find_all('form'):
        if not form.get('action'):
            issues.append("Form missing action attribute")
        
        for input_tag in form.find_all('input'):
            if input_tag.get('type') not in ['submit', 'button', 'hidden']:
                if not input_tag.get('label') and not soup.find('label', {'for': input_tag.get('id')}):
                    issues.append(f"Input missing associated label: {input_tag.get('name', 'unnamed input')}")

    # Check meta tags
    meta_tags = soup.find_all('meta')
    meta_names = [meta.get('name', '').lower() for meta in meta_tags]
    if 'viewport' not in meta_names:
        issues.append("Missing viewport meta tag")
    if 'description' not in meta_names:
        issues.append("Missing description meta tag")
    
    # Check character encoding
    if not soup.find('meta', charset=True):
        issues.append("No character encoding declared")

    # Check links
    links = soup.find_all('a')
    with ThreadPoolExecutor(max_workers=5) as executor:
        link_checks = [
            executor.submit(check_link, link.get('href'), url)
            for link in links
            if link.get('href') and not link['href'].startswith('#')
        ]
        for future in link_checks:
            link, is_valid, message = future.result()
            if not is_valid:
                issues.append(f"Link issue ({link}): {message}")

    # Check for inline styles (not recommended for maintainability)
    inline_styles = soup.find_all(style=True)
    if inline_styles:
        issues.append(f"Found {len(inline_styles)} inline style attributes")

    # Check for JavaScript event attributes
    js_attrs = ['onclick', 'onload', 'onsubmit', 'onmouseover']
    for attr in js_attrs:
        elements = soup.find_all(attrs={attr: True})
        if elements:
            issues.append(f"Found {len(elements)} inline JavaScript {attr} attributes")

    # Check for proper list structure
    for list_tag in soup.find_all(['ul', 'ol']):
        if not list_tag.find_all('li'):
            issues.append(f"Empty {list_tag.name} list found")
        invalid_children = [child for child in list_tag.children 
                          if child.name and child.name != 'li']
        if invalid_children:
            issues.append(f"List contains non-li elements")

    # Check table structure
    for table in soup.find_all('table'):
        if not table.find('thead') and not table.find('th'):
            issues.append("Table missing headers")
        if not table.find('tbody'):
            issues.append("Table missing tbody")

    return issues

def check_html_tags(url: str) -> Tuple[bool, str]:
    """Main function to check HTML at given URL"""
    try:
        response = requests.get(url.strip(), timeout=10)
        response.raise_for_status()
        
        issues = find_html_issues(response.text, url)
        
        if issues:
            return False, "HTML issues found:\n" + "\n".join(issues)
        return True, "HTML is well-formed"
        
    except requests.RequestException as e:
        return False, f"Error accessing URL: {str(e)}"
    except Exception as e:
        return False, f"Error processing HTML: {str(e)}"

def main():
    # Get the directory of the current script
    script_dir = Path(__file__).parent
    urls_file = script_dir / 'urls.txt'
    
    # Create output CSV filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = script_dir / f'errors_{timestamp}.csv'
    
    error_results = []  # Store errors for CSV output
    
    try:
        with open(urls_file, 'r') as f:
            urls = f.readlines()
            
        print(f"Checking {len(urls)} URLs for HTML validity...")
        print("-" * 50)
        
        for url in urls:
            url = url.strip()
            if not url:
                continue
                
            print(f"\nChecking: {url}")
            is_valid, message = check_html_tags(url)
            
            if is_valid:
                print("✅ " + message)
            else:
                print("❌ " + message)
                error_results.append([url, message])
        
        # Write errors to CSV if any were found
        if error_results:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['URL', 'Error'])
                writer.writerows(error_results)
            print(f"\nError report saved to: {output_file}")
                
    except FileNotFoundError:
        print(f"Error: urls.txt not found in {script_dir}")
        sys.exit(1)

if __name__ == "__main__":
    main()
