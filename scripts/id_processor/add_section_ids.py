#!/usr/bin/env python3
"""
Add IDs to section containers (h1-container, h2-container, etc.).

This is Step 1 in the cascading ID addition process.
Section IDs are extracted from headings and normalized.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lxml import html, etree
from lxml.html import HTMLParser

from scripts.id_processor.id_schema import IDSchema


def add_section_ids(input_file: Path, output_file: Path, report: str):
    """
    Add IDs to section containers.
    
    Args:
        input_file: Input HTML file (de_gatsby.html)
        output_file: Output HTML file (html_with_section_ids.html)
        report: Report identifier (wg1, wg2, wg3)
    """
    print(f"Processing: {input_file}")
    print(f"Report: {report}")
    
    # Parse HTML
    parser = HTMLParser(recover=True)
    tree = html.parse(str(input_file), parser=parser)
    root = tree.getroot()
    
    # Get schema for section containers
    schema = IDSchema.get_schema('section_containers')
    if not schema:
        print("ERROR: Could not find schema for section_containers")
        return False
    
    # Find all section containers
    containers = root.xpath(schema['xpath'])
    print(f"Found {len(containers)} section containers")
    
    ids_added = 0
    ids_existing = 0
    
    for container in containers:
        existing_id = container.get('id')
        if existing_id:
            ids_existing += 1
            continue
        
        # Generate new ID
        new_id = IDSchema.generate_section_id(container)
        if new_id:
            container.set('id', new_id)
            ids_added += 1
        else:
            print(f"WARNING: Could not generate ID for container")
            print(f"  Class: {container.get('class')}")
            print(f"  Heading: {IDSchema.extract_heading_text(container)}")
    
    print(f"IDs added: {ids_added}")
    print(f"IDs existing: {ids_existing}")
    print(f"Total containers: {len(containers)}")
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_file), pretty_print=True, encoding='utf-8')
    print(f"Output written: {output_file}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Add IDs to section containers')
    parser.add_argument('--input', type=Path, required=True, help='Input HTML file')
    parser.add_argument('--output', type=Path, required=True, help='Output HTML file')
    parser.add_argument('--report', type=str, required=True, help='Report identifier (wg1, wg2, wg3)')
    
    args = parser.parse_args()
    
    success = add_section_ids(args.input, args.output, args.report)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()



