#!/usr/bin/env python3
"""
Add IDs to nested divs based on their parent container.

This is Step 3 in the cascading ID addition process.
Nested divs get IDs based on their parent container.
Format: {parent_id}_{type}_{index}
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lxml import html
from lxml.html import HTMLParser

from scripts.id_processor.id_schema import IDSchema


def find_parent_id(elem):
    """
    Find the ID of the parent element (section container or other div with ID).
    """
    parent = elem.getparent()
    
    while parent is not None:
        parent_id = parent.get('id')
        if parent_id:
            return parent_id
        
        parent = parent.getparent()
    
    return None


def get_div_type(div_elem):
    """
    Determine the type of a div element based on its class or content.
    """
    div_class = div_elem.get('class', '')
    
    # Check for common div types
    if 'box' in div_class.lower():
        return 'box'
    elif 'figure' in div_class.lower():
        return 'figure'
    elif 'table' in div_class.lower():
        return 'table'
    elif 'list' in div_class.lower():
        return 'list'
    else:
        return 'div'


def add_nested_div_ids(input_file: Path, output_file: Path, report: str):
    """
    Add IDs to nested divs.
    
    Args:
        input_file: Input HTML file (html_with_ids.html)
        output_file: Output HTML file (html_with_all_ids.html)
        report: Report identifier (wg1, wg2, wg3)
    """
    print(f"Processing: {input_file}")
    print(f"Report: {report}")
    
    # Parse HTML
    parser = HTMLParser(recover=True)
    tree = html.parse(str(input_file), parser=parser)
    root = tree.getroot()
    
    # Get schema for nested divs
    schema = IDSchema.get_schema('nested_divs')
    if not schema:
        print("ERROR: Could not find schema for nested_divs")
        return False
    
    # Find all nested divs (excluding containers and siblings)
    nested_divs = root.xpath(schema['xpath'])
    print(f"Found {len(nested_divs)} nested divs")
    
    ids_added = 0
    ids_existing = 0
    ids_failed = 0
    
    # Track div indices per parent
    parent_div_counts = {}
    
    for div in nested_divs:
        # Skip if already has ID
        if div.get('id'):
            ids_existing += 1
            continue
        
        # Find parent ID
        parent_id = find_parent_id(div)
        
        if not parent_id:
            ids_failed += 1
            continue
        
        # Get div type
        div_type = get_div_type(div)
        
        # Get div index within parent
        key = f"{parent_id}_{div_type}"
        if key not in parent_div_counts:
            parent_div_counts[key] = 0
        
        parent_div_counts[key] += 1
        div_index = parent_div_counts[key]
        
        # Generate div ID
        div_id = IDSchema.generate_nested_div_id(div, parent_id, div_type, div_index)
        div.set('id', div_id)
        ids_added += 1
    
    print(f"IDs added: {ids_added}")
    print(f"IDs existing: {ids_existing}")
    print(f"IDs failed (no parent ID): {ids_failed}")
    print(f"Total nested divs: {len(nested_divs)}")
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_file), pretty_print=True, encoding='utf-8')
    print(f"Output written: {output_file}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Add IDs to nested divs')
    parser.add_argument('--input', type=Path, required=True, help='Input HTML file')
    parser.add_argument('--output', type=Path, required=True, help='Output HTML file')
    parser.add_argument('--report', type=str, required=True, help='Report identifier (wg1, wg2, wg3)')
    
    args = parser.parse_args()
    
    success = add_nested_div_ids(args.input, args.output, args.report)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()



