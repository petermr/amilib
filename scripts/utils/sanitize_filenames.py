#!/usr/bin/env python3
"""
Script to sanitize filenames to be Windows-compatible.
Replaces problematic characters with safe alternatives.
"""

import os
import re
import argparse
from pathlib import Path


def sanitize_filename(filename):
    """
    Sanitize a filename to be Windows-compatible.
    
    Windows doesn't allow: < > : " | ? * [ ]
    We replace them with safe alternatives.
    """
    # Define character mappings
    char_map = {
        '<': '_lt_',
        '>': '_gt_',
        ':': '_',
        '"': '_',
        '|': '_',
        '?': '_',
        '*': '_',
        '[': '_lb_',
        ']': '_rb_',
        ';': '_',
        '\\': '_',
        '/': '_',
    }
    
    # Replace problematic characters
    sanitized = filename
    for char, replacement in char_map.items():
        sanitized = sanitized.replace(char, replacement)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized


def find_problematic_files(directory):
    """Find files with problematic characters in their names."""
    problematic_files = []
    
    for root, dirs, files in os.walk(directory):
        # Check directories
        for dir_name in dirs:
            if any(char in dir_name for char in '<>:"|?*[];\\'):
                problematic_files.append(Path(root) / dir_name)
        
        # Check files
        for file_name in files:
            if any(char in file_name for char in '<>:"|?*[];\\'):
                problematic_files.append(Path(root) / file_name)
    
    return problematic_files


def rename_file_safely(old_path, new_path, dry_run=True):
    """Rename a file safely, with conflict resolution."""
    if dry_run:
        print(f"  Would rename: {old_path} -> {new_path}")
        return True
    
    try:
        # Handle conflicts by adding a number suffix
        counter = 1
        final_path = new_path
        while final_path.exists():
            stem = new_path.stem
            suffix = new_path.suffix
            final_path = new_path.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        old_path.rename(final_path)
        print(f"  Renamed: {old_path} -> {final_path}")
        return True
    except Exception as e:
        print(f"  Error renaming {old_path}: {e}")
        return False


def main():
    """Main function to sanitize filenames."""
    parser = argparse.ArgumentParser(description="Sanitize filenames in a directory")
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("--execute", action="store_true", help="Actually rename files (default is dry-run)")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    dry_run = not args.execute
    
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return 1
    
    print(f"🔍 Scanning for problematic filenames in: {directory}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTING'}")
    print("=" * 60)
    
    # Find problematic files
    problematic_files = find_problematic_files(directory)
    
    if not problematic_files:
        print("✅ No problematic filenames found!")
        return
    
    print(f"Found {len(problematic_files)} files/directories with problematic names:")
    print()
    
    # Process each problematic file
    success_count = 0
    for file_path in problematic_files:
        old_name = file_path.name
        new_name = sanitize_filename(old_name)
        
        if old_name != new_name:
            new_path = file_path.parent / new_name
            print(f"📁 {file_path}")
            print(f"   Old: {old_name}")
            print(f"   New: {new_name}")
            
            if rename_file_safely(file_path, new_path, dry_run):
                success_count += 1
            print()
        else:
            print(f"⚠️  {file_path} - No changes needed")
            print()
    
    print("=" * 60)
    print(f"Summary: {success_count}/{len(problematic_files)} files processed successfully")
    
    if dry_run and problematic_files:
        print("\n💡 To actually rename files, run with --execute flag:")
        print(f"   python {Path(__file__).name} {directory} --execute")


if __name__ == "__main__":
    main() 