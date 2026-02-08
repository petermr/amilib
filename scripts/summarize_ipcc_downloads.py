#!/usr/bin/env python3
"""
Summarize IPCC Downloads - File Counts by Report and Chapter

Generates a comprehensive table of all downloaded files in:
test/resources/ipcc/cleaned_content/
"""

import sys
from pathlib import Path
from collections import defaultdict
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources

base_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")

# File patterns to count
patterns = {
    "gatsby_raw": r"gatsby_raw\.html$",
    "wordpress_raw": r"wordpress_raw\.html$",
    "de_gatsby": r"de_gatsby\.html$",
    "de_wordpress": r"de_wordpress\.html$",
    "gatsby": r"^gatsby\.html$",  # Not de_gatsby
    "wordpress": r"^wordpress\.html$",  # Not de_wordpress
    "html_with_ids": r"html_with_ids\.html$",
    "id_list": r"id_list\.html$",
    "para_list": r"para_list\.html$",
}

# Count by report and file type
counts_by_report = defaultdict(lambda: defaultdict(int))
counts_by_chapter = defaultdict(lambda: defaultdict(int))
reports = set()

# Scan all HTML files
for html_file in base_dir.rglob("*.html"):
    rel_path = html_file.relative_to(base_dir)
    parts = rel_path.parts
    
    # Skip files in root directory
    if len(parts) < 2:
        continue
    
    # Extract report (wg1, wg2, wg3, syr, etc.)
    report = parts[0]
    reports.add(report)
    
    # Extract chapter/annex name
    chapter = parts[1] if len(parts) > 1 else "root"
    
    filename = html_file.name
    
    # Match against patterns
    matched = False
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, filename):
            counts_by_report[report][pattern_name] += 1
            counts_by_chapter[f"{report}/{chapter}"][pattern_name] += 1
            matched = True
            break

# Print summary table
print("=" * 120)
print("AR6 IPCC Downloads Summary - File Counts by Report")
print("=" * 120)
print()

# Header
print(f"{'Report':<12} {'Raw HTML':<20} {'Partially Processed':<30} {'With IDs':<25} {'ID Lists':<20}")
print(f"{'':<12} {'gatsby_raw':<10} {'wordpress_raw':<10} {'de_gatsby':<10} {'de_wordpress':<10} {'gatsby':<10} {'wordpress':<10} {'html_with_ids':<15} {'id_list':<10} {'para_list':<10}")
print("-" * 120)

# Sort reports (AR6 first, then others)
ar6_reports = ["wg1", "wg2", "wg3", "syr"]
other_reports = sorted([r for r in reports if r not in ar6_reports])
sorted_reports = ar6_reports + other_reports

for report in sorted_reports:
    if report not in reports:
        continue
    
    row = [report]
    row.append(str(counts_by_report[report].get("gatsby_raw", 0)))
    row.append(str(counts_by_report[report].get("wordpress_raw", 0)))
    row.append(str(counts_by_report[report].get("de_gatsby", 0)))
    row.append(str(counts_by_report[report].get("de_wordpress", 0)))
    row.append(str(counts_by_report[report].get("gatsby", 0)))
    row.append(str(counts_by_report[report].get("wordpress", 0)))
    row.append(str(counts_by_report[report].get("html_with_ids", 0)))
    row.append(str(counts_by_report[report].get("id_list", 0)))
    row.append(str(counts_by_report[report].get("para_list", 0)))
    
    print(f"{row[0]:<12} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10} {row[6]:<10} {row[7]:<15} {row[8]:<10} {row[9]:<10}")

# Totals
print("-" * 120)
totals = defaultdict(int)
for report in reports:
    for pattern_name in patterns.keys():
        totals[pattern_name] += counts_by_report[report].get(pattern_name, 0)

row = ["TOTAL"]
row.append(str(totals.get("gatsby_raw", 0)))
row.append(str(totals.get("wordpress_raw", 0)))
row.append(str(totals.get("de_gatsby", 0)))
row.append(str(totals.get("de_wordpress", 0)))
row.append(str(totals.get("gatsby", 0)))
row.append(str(totals.get("wordpress", 0)))
row.append(str(totals.get("html_with_ids", 0)))
row.append(str(totals.get("id_list", 0)))
row.append(str(totals.get("para_list", 0)))

print(f"{row[0]:<12} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10} {row[6]:<10} {row[7]:<15} {row[8]:<10} {row[9]:<10}")
print()

# Summary statistics
print("=" * 120)
print("Summary Statistics")
print("=" * 120)
print()
print(f"Raw HTML files:           {totals.get('gatsby_raw', 0) + totals.get('wordpress_raw', 0):>4}")
print(f"  - gatsby_raw:            {totals.get('gatsby_raw', 0):>4}")
print(f"  - wordpress_raw:         {totals.get('wordpress_raw', 0):>4}")
print()
print(f"Partially Processed:      {totals.get('de_gatsby', 0) + totals.get('de_wordpress', 0) + totals.get('gatsby', 0) + totals.get('wordpress', 0):>4}")
print(f"  - de_gatsby:             {totals.get('de_gatsby', 0):>4}")
print(f"  - de_wordpress:          {totals.get('de_wordpress', 0):>4}")
print(f"  - gatsby:                {totals.get('gatsby', 0):>4}")
print(f"  - wordpress:            {totals.get('wordpress', 0):>4}")
print()
print(f"Files with IDs:           {totals.get('html_with_ids', 0):>4}")
print(f"ID Lists:                 {totals.get('id_list', 0):>4}")
print(f"Para Lists:               {totals.get('para_list', 0):<4}")
print()

# Detailed breakdown for AR6 reports
print("=" * 120)
print("AR6 Detailed Breakdown by Chapter/Annex")
print("=" * 120)
print()

for report in ar6_reports:
    if report not in reports:
        continue
    
    print(f"\n{report.upper()}:")
    print("-" * 120)
    print(f"{'Chapter/Annex':<35} {'Raw':<6} {'Processed':<10} {'With IDs':<10} {'ID List':<10} {'Para List':<10}")
    print("-" * 120)
    
    # Get all chapters/annexes for this report
    report_dir = base_dir / report
    if not report_dir.exists():
        continue
    
    chapters = sorted([d.name for d in report_dir.iterdir() if d.is_dir()])
    
    for chapter in chapters:
        chapter_key = f"{report}/{chapter}"
        chapter_counts = counts_by_chapter.get(chapter_key, {})
        
        # Only show chapters with files
        if any(chapter_counts.values()):
            raw_count = chapter_counts.get("gatsby_raw", 0) + chapter_counts.get("wordpress_raw", 0)
            processed_count = (chapter_counts.get("de_gatsby", 0) + 
                             chapter_counts.get("de_wordpress", 0) + 
                             chapter_counts.get("gatsby", 0) + 
                             chapter_counts.get("wordpress", 0))
            ids_count = chapter_counts.get("html_with_ids", 0)
            id_list_count = chapter_counts.get("id_list", 0)
            para_list_count = chapter_counts.get("para_list", 0)
            
            print(f"  {chapter:<33} {raw_count:<6} {processed_count:<10} {ids_count:<10} {id_list_count:<10} {para_list_count:<10}")

print()






















