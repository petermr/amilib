"""
Batch process all AR6 glossary and acronym files.

Processes all available AR6 glossary/acronym files through Phase 1 pipeline.
"""
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources
from scripts.glossary_processor.glossary_processor import GlossaryProcessor

# Files to process
FILES_TO_PROCESS = [
    {
        "report": "wg1",
        "annex": "i",
        "entry_type": "glossary",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "annex-i-glossary"),
    },
    {
        "report": "wg1",
        "annex": "ii",
        "entry_type": "acronym",
        "input_file": "annex-ii-acronyms.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "annex-ii-acronyms"),
    },
    {
        "report": "wg3",
        "annex": "i",
        "entry_type": "glossary",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg3", "annex-i-glossary"),
    },
    {
        "report": "syr",
        "annex": "i",
        "entry_type": "glossary",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annex-i-glossary"),
    },
    {
        "report": "syr",
        "annex": "ii",
        "entry_type": "acronym",
        "input_file": "annex-ii-acronyms.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annex-ii-acronyms"),
    },
]


def process_file(file_info):
    """Process a single file."""
    input_path = file_info["input_dir"] / file_info["input_file"]
    output_path = file_info["input_dir"] / "structured.html"
    
    print(f"\n{'='*70}")
    print(f"Processing: {file_info['report'].upper()} Annex {file_info['annex'].upper()} ({file_info['entry_type']})")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"{'='*70}")
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return False
    
    # Check if already processed
    if output_path.exists():
        print(f"⚠️  Output file already exists: {output_path}")
        response = input("   Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("   Skipping...")
            return True
    
    # Process
    success = GlossaryProcessor.process(
        input_html_path=input_path,
        output_html_path=output_path,
        report=file_info["report"],
        annex=file_info["annex"],
        entry_type=file_info["entry_type"]
    )
    
    if success:
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"✅ Success! Output written to: {output_path}")
            print(f"   File size: {size:,} bytes")
        else:
            print(f"⚠️  Processing reported success but output file not found")
        return True
    else:
        print(f"❌ Processing failed")
        return False


def main():
    """Process all files."""
    print("AR6 Glossary/Acronym Batch Processing")
    print("=" * 70)
    print(f"Processing {len(FILES_TO_PROCESS)} files...")
    
    results = []
    for file_info in FILES_TO_PROCESS:
        success = process_file(file_info)
        results.append({
            "file": f"{file_info['report']} Annex {file_info['annex']} ({file_info['entry_type']})",
            "success": success
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['file']}")
    
    print(f"\nTotal: {len(results)} files")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())








