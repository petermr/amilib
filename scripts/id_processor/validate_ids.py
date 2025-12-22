#!/usr/bin/env python3
"""
Validate that all IDs are unique and properly formatted.
"""

import argparse
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lxml import html
from lxml.html import HTMLParser


def validate_ids(html_file: Path):
    """
    Validate IDs in HTML file.
    
    Checks:
    1. All IDs are unique
    2. IDs follow proper format (no spaces, valid characters)
    3. All IDs are non-empty
    """
    parser = HTMLParser(recover=True)
    tree = html.parse(str(html_file), parser=parser)
    root = tree.getroot()
    
    # Find all elements with IDs
    elements_with_ids = root.xpath('.//*[@id]')
    ids = [elem.get('id') for elem in elements_with_ids]
    
    print(f"Validating {len(ids)} IDs in {html_file}")
    
    errors = []
    warnings = []
    
    # Check for empty IDs
    empty_ids = [i for i, elem_id in enumerate(ids) if not elem_id or not elem_id.strip()]
    if empty_ids:
        errors.append(f"Found {len(empty_ids)} empty IDs")
    
    # Check for duplicate IDs
    id_counts = Counter(ids)
    duplicates = {id_val: count for id_val, count in id_counts.items() if count > 1}
    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate IDs:")
        for dup_id, count in duplicates.items():
            errors.append(f"  '{dup_id}': {count} occurrences")
    
    # Check ID format (should be valid HTML ID)
    import re
    invalid_format = []
    for elem_id in ids:
        if not elem_id:
            continue
        # HTML ID should start with letter, then letters/digits/hyphens/underscores/colons
        if not re.match(r'^[a-zA-Z][\w\-:.]*$', elem_id):
            invalid_format.append(elem_id)
    
    if invalid_format:
        warnings.append(f"Found {len(invalid_format)} IDs with invalid format:")
        for invalid_id in invalid_format[:10]:  # Show first 10
            warnings.append(f"  '{invalid_id}'")
        if len(invalid_format) > 10:
            warnings.append(f"  ... and {len(invalid_format) - 10} more")
    
    # Print results
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  ❌ {error}")
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    
    if not errors and not warnings:
        print("\n✅ All IDs are valid!")
        return True
    
    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description='Validate IDs in HTML file')
    parser.add_argument('--input', type=Path, required=True, help='Input HTML file')
    
    args = parser.parse_args()
    
    success = validate_ids(args.input)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()



