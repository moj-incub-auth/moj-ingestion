#!/usr/bin/env python3
"""
Parse MOJ Component Markdown Files to JSON

This script parses concatenated markdown files containing MOJ component documentation
and extracts structured information into JSON format.
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Markdown content

    Returns:
        Dictionary of frontmatter fields
    """
    frontmatter = {}

    # Find frontmatter blocks (between --- markers)
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        # Parse simple key: value pairs
        for line in match.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                if value:
                    frontmatter[key] = value

    return frontmatter


def extract_component_title(content: str, frontmatter: Dict[str, Any]) -> str:
    """Extract the component title from frontmatter or content."""
    # Try to find the title from index.md section specifically
    index_match = re.search(
        r'# Source: index\.md.*?---\s*\ntitle:\s*(.+?)(?:\n|$)',
        content,
        re.MULTILINE | re.DOTALL
    )
    if index_match:
        title = index_match.group(1).strip()
        # Clean up any trailing content
        title = title.split('\n')[0].strip()
        return title

    # Fallback: look through all frontmatter titles
    title_pattern = re.compile(r'^title:\s*(.+?)$', re.MULTILINE)
    titles = title_pattern.findall(content)

    # Filter out section titles
    section_titles = ['Overview', 'How to use', 'Examples', 'Get help and contribute']
    for title in titles:
        title = title.strip()
        if title not in section_titles:
            return title

    return "Unknown Component"


def extract_description(content: str, frontmatter: Dict[str, Any]) -> str:
    """Extract the component description."""
    # Try lede from frontmatter
    if 'lede' in frontmatter:
        return frontmatter['lede']

    # Try to find overview section
    overview_match = re.search(r'## Overview\s*\n+(.+?)(?=\n##|\n#|$)', content, re.DOTALL)
    if overview_match:
        # Get first paragraph
        paragraphs = overview_match.group(1).strip().split('\n\n')
        for para in paragraphs:
            # Skip example blocks and empty lines
            if para.strip() and not para.startswith('{%') and not para.startswith('<'):
                return para.strip()

    return "Component documentation"


def extract_url(content: str, title: str) -> str:
    """Generate a URL for the component."""
    # Try to extract from path if available
    path_match = re.search(r'\*Path: .+/components/([^/]+)/', content)
    if path_match:
        component_slug = path_match.group(1)
        return f"https://design-patterns.service.justice.gov.uk/components/{component_slug}/"

    # Fallback to generated URL
    slug = title.lower().replace(' ', '-')
    return f"https://design-patterns.service.justice.gov.uk/components/{slug}/"


def extract_parent(content: str) -> str:
    """Extract the parent design system name."""
    # Check if it's MOJ or GOV.UK
    if 'moj-frontend' in content.lower() or '/moj/' in content:
        return "MOJ Design System"
    elif 'govuk' in content.lower():
        return "GOV.UK Design System"

    return "MOJ Design System"


def extract_accessibility(content: str) -> str:
    """Extract accessibility level (assume AA if not specified)."""
    # Look for WCAG mentions
    if 'WCAG' in content:
        if '2.1' in content or '2.2' in content:
            return "AA"

    # Default to AA for government services
    return "AA"


def extract_dates(frontmatter: Dict[str, Any]) -> tuple:
    """Extract or generate created_at and updated_at dates."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check for status date in frontmatter
    if 'statusDate' in frontmatter:
        try:
            # Parse date like "February 2025"
            date_str = frontmatter['statusDate']
            # Convert to ISO format (assume first day of month)
            date_obj = datetime.strptime(date_str, "%B %Y")
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            return formatted_date, formatted_date
        except:
            pass

    return now, now


def has_research_content(content: str) -> bool:
    """Check if the component documentation includes research."""
    research_keywords = [
        'research',
        'user testing',
        'user research',
        'tested with',
        'feedback from users',
        'case study',
        'Examples'
    ]

    content_lower = content.lower()
    return any(keyword.lower() in content_lower for keyword in research_keywords)


def parse_component_markdown(file_path: str) -> Dict[str, Any]:
    """
    Parse a concatenated markdown file and extract component information.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary containing component data in the specified JSON format
    """
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)

    # Extract component information
    title = extract_component_title(content, frontmatter)
    description = extract_description(content, frontmatter)
    url = extract_url(content, title)
    parent = extract_parent(content)
    accessibility = extract_accessibility(content)
    created_at, updated_at = extract_dates(frontmatter)
    has_research = has_research_content(content)

    # Build the JSON structure
    result = {
        "filecontent": content,
        "components": [{
            "title": title,
            "url": url,
            "description": description,
            "parent": parent,
            "accessibility": accessibility,
            "created_at": created_at,
            "updated_at": updated_at,
            "has_research": has_research,
            "views": 0,  # Default value as this is typically tracked separately
            "status": frontmatter.get('status', 'Unknown'),
            "statusDate": frontmatter.get('statusDate', ''),
            "sections": extract_sections(content)
        }]
    }

    return result


def extract_sections(content: str) -> List[Dict[str, str]]:
    """Extract document sections for additional metadata."""
    sections = []

    # Find all source file sections
    source_pattern = r'# Source: (.+?)\.md\s*\n.*?\*Path: (.+?)\*'
    matches = re.finditer(source_pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        section_name = match.group(1)
        section_path = match.group(2)
        sections.append({
            "name": section_name,
            "path": section_path
        })

    return sections


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Parse MOJ component markdown files and extract structured JSON data"
    )

    parser.add_argument(
        "markdown_file",
        type=str,
        help="Path to the concatenated markdown file"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file path (default: print to stdout)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output"
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)"
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.markdown_file).exists():
        print(f"❌ Error: File not found: {args.markdown_file}")
        return

    print(f"📄 Parsing markdown file: {args.markdown_file}")

    # Parse the markdown file
    result = parse_component_markdown(args.markdown_file)

    # Convert to JSON
    if args.pretty:
        json_output = json.dumps(result, indent=args.indent, ensure_ascii=False)
    else:
        json_output = json.dumps(result, ensure_ascii=False)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json_output, encoding='utf-8')
        print(f"✅ JSON output written to: {args.output}")
        print(f"📊 Component: {result['components'][0]['title']}")
        print(f"📝 Description: {result['components'][0]['description'][:80]}...")
        print(f"🔗 URL: {result['components'][0]['url']}")
    else:
        print("\n" + "="*80)
        print("JSON OUTPUT:")
        print("="*80)
        print(json_output)

    print(f"\n✅ Successfully parsed component: {result['components'][0]['title']}")


if __name__ == "__main__":
    main()
