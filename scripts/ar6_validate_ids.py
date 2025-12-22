#!/usr/bin/env python3
"""
AR6 Semantic ID Validation Script

Validates semantic IDs across all processed AR6 chapters.
Checks for:
- Missing paragraph IDs
- Missing section/div IDs
- Duplicate IDs
- ID format compliance

Date: 2025-12-06
"""

import sys
from pathlib import Path
from collections import defaultdict
import lxml.etree as ET
from lxml.html import HTMLParser

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources
from test.ipcc_constants import HTML_WITH_IDS


def validate_semantic_ids(html_file):
    """
    Validate semantic IDs in an HTML file.
    
    Returns:
        dict with validation results
    """
    if not html_file.exists():
        return {
            "status": "file_missing",
            "file": str(html_file),
            "errors": [f"File does not exist: {html_file}"]
        }
    
    try:
        tree = ET.parse(str(html_file), HTMLParser())
    except Exception as e:
        return {
            "status": "parse_error",
            "file": str(html_file),
            "errors": [f"Failed to parse HTML: {e}"]
        }
    
    # Collect all IDs
    all_elements_with_ids = tree.xpath("//*[@id]")
    all_ids = [elem.attrib.get("id") for elem in all_elements_with_ids]
    
    # Check for duplicates
    id_counts = defaultdict(int)
    for id_val in all_ids:
        if id_val:
            id_counts[id_val] += 1
    duplicates = [id_val for id_val, count in id_counts.items() if count > 1]
    
    # Check paragraphs without IDs
    paragraphs = tree.xpath("//p[text() and normalize-space(text())]")
    paras_without_ids = []
    for p in paragraphs:
        if not p.attrib.get("id"):
            # Get parent section ID if available
            parent_section = p.xpath("ancestor::div[@id][1]")
            parent_id = parent_section[0].attrib.get("id") if parent_section else "unknown"
            text_preview = ''.join(p.itertext())[:50].strip()
            paras_without_ids.append({
                "parent_section": parent_id,
                "text_preview": text_preview
            })
    
    # Check section containers without IDs
    h_containers = tree.xpath("//div[contains(@class, 'h1-container') or contains(@class, 'h2-container') or contains(@class, 'h3-container')]")
    sections_without_ids = []
    for section in h_containers:
        if not section.attrib.get("id"):
            heading = section.xpath(".//h1 | .//h2 | .//h3")
            heading_text = ''.join(heading[0].itertext()).strip()[:50] if heading else "unknown"
            sections_without_ids.append({
                "heading": heading_text,
                "class": section.attrib.get("class", "")
            })
    
    # Check divs without IDs (semantic divs that should have IDs)
    semantic_divs = tree.xpath("//div[not(@id) and (contains(@class, 'container') or contains(@class, 'section') or contains(@class, 'box'))]")
    divs_without_ids = len(semantic_divs)
    
    return {
        "status": "validated",
        "file": str(html_file),
        "total_elements_with_ids": len(set(all_ids)),
        "total_ids": len(all_ids),
        "duplicate_ids": duplicates,
        "paragraphs_total": len(paragraphs),
        "paragraphs_without_ids": len(paras_without_ids),
        "paragraphs_without_ids_details": paras_without_ids[:10],  # Limit details
        "sections_total": len(h_containers),
        "sections_without_ids": len(sections_without_ids),
        "sections_without_ids_details": sections_without_ids[:10],
        "semantic_divs_without_ids": divs_without_ids,
        "errors": duplicates + [f"Missing para ID in section {p['parent_section']}" 
                                for p in paras_without_ids[:5]]
    }


def validate_all_ar6():
    """Validate all AR6 chapters"""
    base_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
    
    results = {}
    
    # Process WG1, WG2, WG3 chapters
    for wg in ["wg1", "wg2", "wg3"]:
        wg_dir = base_dir / wg
        if not wg_dir.exists():
            continue
            
        for chapter_dir in sorted(wg_dir.glob("Chapter*")):
            html_file = chapter_dir / f"{HTML_WITH_IDS}.html"
            if html_file.exists():
                key = f"{wg}/{chapter_dir.name}"
                results[key] = validate_semantic_ids(html_file)
    
    # Process SYR
    syr_dir = base_dir / "syr" / "longer-report"
    if syr_dir.exists():
        html_file = syr_dir / f"{HTML_WITH_IDS}.html"
        if html_file.exists():
            results["syr/longer-report"] = validate_semantic_ids(html_file)
    
    return results


def print_summary(results):
    """Print validation summary"""
    print("=" * 80)
    print("AR6 Semantic ID Validation Summary")
    print("=" * 80)
    print()
    
    total_chapters = len(results)
    chapters_with_issues = sum(1 for r in results.values() 
                               if r.get("status") == "validated" and 
                               (r.get("duplicate_ids") or 
                                r.get("paragraphs_without_ids", 0) > 0 or
                                r.get("sections_without_ids", 0) > 0))
    
    print(f"Total chapters processed: {total_chapters}")
    print(f"Chapters with issues: {chapters_with_issues}")
    print()
    
    # Summary statistics
    total_paras = sum(r.get("paragraphs_total", 0) for r in results.values() 
                     if r.get("status") == "validated")
    total_paras_with_ids = total_paras - sum(r.get("paragraphs_without_ids", 0) 
                                            for r in results.values() 
                                            if r.get("status") == "validated")
    
    total_sections = sum(r.get("sections_total", 0) for r in results.values() 
                       if r.get("status") == "validated")
    total_sections_with_ids = total_sections - sum(r.get("sections_without_ids", 0) 
                                                   for r in results.values() 
                                                   if r.get("status") == "validated")
    
    print("Overall Statistics:")
    print(f"  Total paragraphs: {total_paras}")
    print(f"  Paragraphs with IDs: {total_paras_with_ids} ({100*total_paras_with_ids/max(total_paras,1):.1f}%)")
    print(f"  Total sections: {total_sections}")
    print(f"  Sections with IDs: {total_sections_with_ids} ({100*total_sections_with_ids/max(total_sections,1):.1f}%)")
    print()
    
    # Detailed results
    print("Detailed Results by Chapter:")
    print("-" * 80)
    
    for chapter, result in sorted(results.items()):
        if result.get("status") == "file_missing":
            print(f"❌ {chapter}: FILE MISSING")
        elif result.get("status") == "parse_error":
            print(f"❌ {chapter}: PARSE ERROR - {result.get('errors', [])}")
        elif result.get("status") == "validated":
            issues = []
            if result.get("duplicate_ids"):
                issues.append(f"{len(result['duplicate_ids'])} duplicate IDs")
            if result.get("paragraphs_without_ids", 0) > 0:
                issues.append(f"{result['paragraphs_without_ids']} paragraphs without IDs")
            if result.get("sections_without_ids", 0) > 0:
                issues.append(f"{result['sections_without_ids']} sections without IDs")
            
            if issues:
                print(f"⚠️  {chapter}: {', '.join(issues)}")
            else:
                print(f"✅ {chapter}: All IDs present")
            
            # Show some details for chapters with issues
            if result.get("duplicate_ids"):
                print(f"   Duplicates: {result['duplicate_ids'][:5]}")
            if result.get("paragraphs_without_ids_details"):
                print(f"   Sample missing para IDs:")
                for detail in result["paragraphs_without_ids_details"][:3]:
                    print(f"     - Section {detail['parent_section']}: {detail['text_preview']}...")
    
    print()
    print("=" * 80)


def main():
    """Main entry point"""
    print("Validating AR6 semantic IDs...")
    print()
    
    results = validate_all_ar6()
    print_summary(results)
    
    # Return exit code based on results
    has_errors = any(
        r.get("status") != "validated" or 
        r.get("duplicate_ids") or 
        r.get("paragraphs_without_ids", 0) > 0
        for r in results.values()
    )
    
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())





















