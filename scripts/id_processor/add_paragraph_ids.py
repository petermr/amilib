#!/usr/bin/env python3
"""
Add IDs to paragraphs based on their parent section container.

This is Step 2 in the cascading ID addition process.
Paragraph IDs are generated based on their parent section container ID.
Format: {section_id}_p{index}
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lxml import html
from lxml.html import HTMLParser

from scripts.id_processor.id_schema import IDSchema


def find_parent_section_id(para_elem):
    """
    Find the ID of the parent section container.
    
    Looks up the DOM tree for a section container (h1-container, h2-container, etc.)
    """
    parent = para_elem.getparent()
    
    while parent is not None:
        parent_class = parent.get('class', '')
        if 'h1-container' in parent_class or 'h2-container' in parent_class or \
           'h3-container' in parent_class or 'h4-container' in parent_class:
            section_id = parent.get('id')
            if section_id:
                return section_id
        
        parent = parent.getparent()
    
    return None


def add_paragraph_ids(input_file: Path, output_file: Path, report: str):
    """
    Add IDs to paragraphs.
    
    Args:
        input_file: Input HTML file (html_with_section_ids.html)
        output_file: Output HTML file (html_with_ids.html)
        report: Report identifier (wg1, wg2, wg3)
    """
    print(f"Processing: {input_file}")
    print(f"Report: {report}")
    
    # Parse HTML
    parser = HTMLParser(recover=True)
    tree = html.parse(str(input_file), parser=parser)
    root = tree.getroot()
    
    # Find all paragraphs
    paragraphs = root.xpath('.//p')
    print(f"Found {len(paragraphs)} paragraphs")
    
    ids_added = 0
    ids_existing = 0
    ids_failed = 0
    
    # Track paragraph indices per section
    section_para_counts = {}
    
    for para in paragraphs:
        # Skip if already has ID
        if para.get('id'):
            ids_existing += 1
            continue
        
        # Find parent section ID
        section_id = find_parent_section_id(para)
        
        if not section_id:
            ids_failed += 1
            continue
        
        # Get paragraph index within section
        if section_id not in section_para_counts:
            section_para_counts[section_id] = 0
        
        section_para_counts[section_id] += 1
        para_index = section_para_counts[section_id]
        
        # Generate paragraph ID
        para_id = IDSchema.generate_paragraph_id(para, section_id, para_index)
        para.set('id', para_id)
        ids_added += 1
    
    print(f"IDs added: {ids_added}")
    print(f"IDs existing: {ids_existing}")
    print(f"IDs failed (no parent section): {ids_failed}")
    print(f"Total paragraphs: {len(paragraphs)}")
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_file), pretty_print=True, encoding='utf-8')
    print(f"Output written: {output_file}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Add IDs to paragraphs')
    parser.add_argument('--input', type=Path, required=True, help='Input HTML file')
    parser.add_argument('--output', type=Path, required=True, help='Output HTML file')
    parser.add_argument('--report', type=str, required=True, help='Report identifier (wg1, wg2, wg3)')
    
    args = parser.parse_args()
    
    success = add_paragraph_ids(args.input, args.output, args.report)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()




