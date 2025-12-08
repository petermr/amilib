#!/usr/bin/env python3
"""
Process AR6 Annexes - Download and Process Selected Annexes

Downloads selected AR6 annexes (Glossaries and Acronyms) to:
test/resources/ipcc/cleaned_content/{report}/annex-{number}-{type}/

Then processes them to add semantic IDs and Wikimedia IDs.

Date: 2025-12-06
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.ipcc_classes import IPCCGatsby
from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL
from test.resources import Resources

# Selected annexes based on decisions
SELECTED_ANNEXES = [
    # WG1
    {"report": "wg1", "annex": "annex-i", "type": "glossary", "url_suffix": "annex/glossary"},
    {"report": "wg1", "annex": "annex-ii", "type": "acronyms", "url_suffix": "annex/acronyms"},
    
    # WG2
    {"report": "wg2", "annex": "annex-ii", "type": "glossary", "url_suffix": "annex/glossary"},
    
    # WG3
    {"report": "wg3", "annex": "annex-i", "type": "glossary", "url_suffix": "annex/glossary"},
    {"report": "wg3", "annex": "annex-ii", "type": "acronyms", "url_suffix": "annex/acronyms"},
]

# SYR annexes (partially processed, may need different handling)
SYR_ANNEXES = [
    {"report": "syr", "annex": "annex-i", "type": "glossary"},
    {"report": "syr", "annex": "annex-ii", "type": "acronyms"},
    {"report": "syr", "annex": "annexes-and-index", "type": "combined"},
]

REPORT_URLS = {
    "wg1": WG1_URL,
    "wg2": WG2_URL,
    "wg3": WG3_URL,
    "syr": SYR_URL,
}

BASE_OUTPUT_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")


def download_annex(report, annex_info, base_url):
    """Download and process an annex"""
    annex_name = annex_info["annex"]
    annex_type = annex_info["type"]
    url_suffix = annex_info.get("url_suffix", annex_name)
    
    # Create output directory: test/resources/ipcc/cleaned_content/{report}/{annex_name}-{type}/
    output_dir = BASE_OUTPUT_DIR / report / f"{annex_name}-{annex_type}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"Processing: {report.upper()} - {annex_name} ({annex_type})")
    print(f"Output: {output_dir}")
    print(f"{'='*80}")
    
    publisher = IPCCGatsby()
    
    try:
        # Download and clean chapter
        # Note: download_clean_chapter creates {outdir}/{report}/{chap} structure
        # download_save_chapter also creates {outdir}/{report}/{chap} structure
        # So we pass cleaned_content parent to avoid double nesting
        # We want: test/resources/ipcc/cleaned_content/{report}/annex-i-glossary/
        publisher.download_clean_chapter(
            annex_name,  # Use annex_name as chapter identifier
            minsize=10000,  # Lower threshold for annexes
            outdir=BASE_OUTPUT_DIR,  # Use cleaned_content directly
            report=report,
            wg_url=base_url
        )
        
        # Check if files were created (may be in nested path due to download_save_chapter)
        expected_raw = BASE_OUTPUT_DIR / report / annex_name / f"{publisher.raw_filename}.html"
        nested_raw = BASE_OUTPUT_DIR.parent / report / annex_name / report / annex_name / f"{publisher.raw_filename}.html"
        
        # Move files if they're in nested location
        if nested_raw.exists() and not expected_raw.exists():
            print(f"  Moving files from nested location...")
            nested_dir = nested_raw.parent
            target_dir = BASE_OUTPUT_DIR / report / annex_name
            target_dir.mkdir(parents=True, exist_ok=True)
            import shutil
            for file in nested_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, target_dir / file.name)
        
        print(f"✅ Successfully downloaded {annex_name}")
        return True
    except Exception as e:
        print(f"❌ Error downloading {annex_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_syr_annexes():
    """Process SYR annexes that are partially processed"""
    print(f"\n{'='*80}")
    print("Processing SYR Annexes (Partially Processed)")
    print(f"{'='*80}")
    
    syr_base = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "syr", "annexes")
    syr_output_base = BASE_OUTPUT_DIR / "syr"
    
    # Process Glossary
    glossary_source = syr_base / "html" / "glossary"
    if glossary_source.exists():
        print(f"\nProcessing SYR Glossary from: {glossary_source}")
        glossary_output = syr_output_base / "annex-i-glossary"
        glossary_output.mkdir(parents=True, exist_ok=True)
        print(f"Output: {glossary_output}")
        # TODO: Copy and process existing files
    
    # Process Acronyms
    acronyms_source = syr_base / "html" / "acronyms"
    if acronyms_source.exists():
        print(f"\nProcessing SYR Acronyms from: {acronyms_source}")
        acronyms_output = syr_output_base / "annex-ii-acronyms"
        acronyms_output.mkdir(parents=True, exist_ok=True)
        print(f"Output: {acronyms_output}")
        # TODO: Copy and process existing files
    
    # Process Annexes and Index
    annexes_index_source = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annexes-and-index")
    if annexes_index_source.exists():
        print(f"\nProcessing SYR Annexes and Index from: {annexes_index_source}")
        print(f"Output: {annexes_index_source}")
        # TODO: Clean and process existing content.html


def main():
    """Main entry point"""
    print("="*80)
    print("AR6 Annexes Download and Processing")
    print("="*80)
    print(f"Output Directory: {BASE_OUTPUT_DIR}")
    print(f"Selected Annexes: {len(SELECTED_ANNEXES)}")
    print()
    
    success_count = 0
    fail_count = 0
    
    # Process selected annexes
    for annex_info in SELECTED_ANNEXES:
        report = annex_info["report"]
        base_url = REPORT_URLS.get(report)
        
        if not base_url:
            print(f"❌ No URL found for {report}")
            fail_count += 1
            continue
        
        if download_annex(report, annex_info, base_url):
            success_count += 1
        else:
            fail_count += 1
    
    # Process SYR annexes
    print("\n" + "="*80)
    print("SYR Annexes (Partially Processed)")
    print("="*80)
    process_syr_annexes()
    
    # Summary
    print("\n" + "="*80)
    print("Download Summary")
    print("="*80)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Total: {len(SELECTED_ANNEXES)}")
    print()
    print(f"Files saved to: {BASE_OUTPUT_DIR}")
    print()
    print("Next Steps:")
    print("1. Verify downloaded files")
    print("2. Add semantic IDs using IPCCGatsby.add_ids()")
    print("3. Add Wikimedia IDs (Wikidata/Wiktionary) to terms")
    print("4. Run validation script")


if __name__ == "__main__":
    main()

