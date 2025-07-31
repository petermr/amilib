#!/usr/bin/env python3
"""
Script to clean git history of problematic filenames.
WARNING: This rewrites git history and should be used carefully!
"""

import subprocess
import sys
from pathlib import Path


def run_git_command(cmd, check=True):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode


def find_problematic_files_in_history():
    """Find files with problematic characters in git history."""
    print("🔍 Searching git history for problematic filenames...")
    
    # Get all files that have ever been in the repository
    stdout, stderr, returncode = run_git_command([
        'log', '--name-only', '--pretty=format:', '--all'
    ])
    
    if returncode != 0:
        print(f"Error getting git history: {stderr}")
        return []
    
    # Find files with problematic characters
    problematic_files = set()
    for line in stdout.split('\n'):
        line = line.strip()
        if line and any(char in line for char in '<>:"|?*[];\\'):
            problematic_files.add(line)
    
    return sorted(problematic_files)


def create_filter_script(problematic_files):
    """Create a filter script for git filter-branch."""
    script_content = """#!/bin/bash
# Git filter script to rename problematic files

"""
    
    for file_path in problematic_files:
        # Create sanitized name
        sanitized_name = file_path
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
        }
        
        for char, replacement in char_map.items():
            sanitized_name = sanitized_name.replace(char, replacement)
        
        if sanitized_name != file_path:
            script_content += f'if [ -f "{file_path}" ]; then\n'
            script_content += f'    git mv "{file_path}" "{sanitized_name}" 2>/dev/null || true\n'
            script_content += f'fi\n'
    
    return script_content


def main():
    """Main function to clean git history."""
    print("⚠️  WARNING: This script will rewrite git history!")
    print("⚠️  Make sure you have a backup and all team members are aware!")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Find problematic files
    problematic_files = find_problematic_files_in_history()
    
    if not problematic_files:
        print("✅ No problematic files found in git history!")
        return
    
    print(f"Found {len(problematic_files)} problematic files in git history:")
    for file_path in problematic_files:
        print(f"  - {file_path}")
    
    print("\n" + "="*60)
    print("RECOMMENDED APPROACH:")
    print("1. Use .gitignore to prevent future problematic files")
    print("2. For existing files, consider manual cleanup instead of history rewriting")
    print("3. If you must rewrite history, coordinate with all team members")
    print()
    
    response = input("Do you want to proceed with history rewriting? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted. Consider using .gitignore instead.")
        return
    
    # Create filter script
    filter_script = create_filter_script(problematic_files)
    filter_script_path = Path("temp_git_filter.sh")
    
    with open(filter_script_path, 'w') as f:
        f.write(filter_script)
    
    # Make script executable
    filter_script_path.chmod(0o755)
    
    print(f"📝 Created filter script: {filter_script_path}")
    print("🔧 To apply the filter, run:")
    print(f"   git filter-branch --tree-filter '{filter_script_path}' --all")
    print()
    print("⚠️  After running filter-branch:")
    print("   1. Force push: git push --force-with-lease")
    print("   2. All team members must re-clone or reset their repositories")
    print("   3. Delete the filter script: rm {filter_script_path}")
    
    # Clean up
    if input("\nDelete the filter script now? (yes/no): ").lower() == 'yes':
        filter_script_path.unlink()
        print("Filter script deleted.")


if __name__ == "__main__":
    main() 