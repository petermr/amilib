#!/usr/bin/env python3
"""
Read AR6 Annexes Decisions from JSON file

Reads exported decisions from ar6_annexes_decisions.json and proposes next steps.
"""

import json
import sys
from pathlib import Path

def read_decisions(json_file):
    """Read decisions from JSON file"""
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        print("\nPlease export your decisions from the HTML table first:")
        print("1. Open docs/ar6_annexes_decision_table.html in your browser")
        print("2. Make your selections")
        print("3. Click 'Export to JSON' button")
        print("4. The file will be saved as ar6_annexes_decisions.json")
        return None
    
    with open(json_file, 'r') as f:
        return json.load(f)

def analyze_decisions(decisions):
    """Analyze decisions and categorize"""
    selected = []
    not_selected = []
    
    for decision in decisions:
        if decision.get('process'):
            selected.append(decision)
        else:
            not_selected.append(decision)
    
    return selected, not_selected

def propose_next_steps(selected, not_selected):
    """Propose next steps based on decisions"""
    print("=" * 80)
    print("AR6 Annexes Processing - Next Steps Proposal")
    print("=" * 80)
    print()
    
    print(f"Total Annexes Reviewed: {len(selected) + len(not_selected)}")
    print(f"Selected for Processing: {len(selected)}")
    print(f"Not Selected: {len(not_selected)}")
    print()
    
    if not selected:
        print("⚠️  No annexes selected for processing.")
        print("   If this is correct, no action needed.")
        return
    
    # Group by report
    by_report = {}
    for annex in selected:
        report = annex['report']
        if report not in by_report:
            by_report[report] = []
        by_report[report].append(annex)
    
    print("Selected Annexes by Report:")
    print("-" * 80)
    for report in sorted(by_report.keys()):
        print(f"\n{report}:")
        for annex in by_report[report]:
            reason = annex.get('reason', 'No reason provided')
            print(f"  ✅ {annex['annex']}: {annex['title']}")
            if reason:
                print(f"     Reason: {reason}")
    
    print()
    print("=" * 80)
    print("PROPOSED PROCESSING PLAN")
    print("=" * 80)
    print()
    
    # Processing steps
    print("Phase 1: Download and Clean")
    print("-" * 80)
    for report in sorted(by_report.keys()):
        annexes = by_report[report]
        print(f"\n{report}:")
        for annex in annexes:
            annex_name = annex['annex'].lower().replace(' ', '-')
            title_slug = annex['title'].lower().replace(' ', '-')
            print(f"  - Download: {report}/{annex_name} ({annex['title']})")
            print(f"  - Clean: Remove navigation, tooltips, etc.")
    
    print()
    print("Phase 2: Add Semantic IDs")
    print("-" * 80)
    print("  - Add paragraph IDs (format: {section_id}_p{index})")
    print("  - Add section/div IDs")
    print("  - Generate id_list.html and para_list.html")
    print("  - Validate no duplicate IDs")
    
    print()
    print("Phase 3: Validation")
    print("-" * 80)
    print("  - Run validation script: python scripts/ar6_validate_ids.py")
    print("  - Check ID coverage (target: 95%+ paragraphs)")
    print("  - Fix any duplicate IDs")
    print("  - Verify semantic structure")
    
    print()
    print("Implementation Script:")
    print("-" * 80)
    print("""
from test.ipcc_classes import IPCCGatsby
from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL
from pathlib import Path
from test.resources import Resources

def process_selected_annexes():
    publisher = IPCCGatsby()
    outdir = Path(Resources.TEMP_DIR, "ipcc", "ar6")
    
    # Map of report to URL
    report_urls = {
        "wg1": WG1_URL,
        "wg2": WG2_URL,
        "wg3": WG3_URL,
        "syr": SYR_URL
    }
    
    # Process each selected annex
    selected_annexes = [
        # Add your selected annexes here based on decisions
    ]
    
    for annex_info in selected_annexes:
        report = annex_info['report']
        annex_name = annex_info['annex'].lower().replace(' ', '-')
        wg_url = report_urls.get(report.lower())
        
        if wg_url:
            publisher.download_clean_chapter(
                annex_name, minsize=100000,
                outdir=outdir, report=report.lower(),
                wg_url=wg_url
            )
""")
    
    print()
    print("Estimated Time:")
    print("-" * 80)
    print(f"  - Download & Clean: ~{len(selected) * 0.5} hours")
    print(f"  - Add IDs: ~{len(selected) * 0.5} hours")
    print(f"  - Validation: ~{len(selected) * 0.25} hours")
    print(f"  - Total: ~{len(selected) * 1.25} hours")

def main():
    """Main entry point"""
    # Check for JSON file in current directory or docs directory
    json_file = Path("ar6_annexes_decisions.json")
    if not json_file.exists():
        json_file = Path(__file__).parent.parent / "docs" / "ar6_annexes_decisions.json"
    
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
    
    decisions = read_decisions(json_file)
    if not decisions:
        return 1
    
    selected, not_selected = analyze_decisions(decisions)
    propose_next_steps(selected, not_selected)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())












