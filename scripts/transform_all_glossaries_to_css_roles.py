"""
Batch transform all AR6 glossary/acronym files to use CSS role-based styles.
"""
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources
from scripts.glossary_processor.css_role_transformer import CSSRoleTransformer

# Files to transform (original HTML files, not structured.html)
FILES_TO_TRANSFORM = [
    {
        "report": "wg1",
        "annex": "i",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "annex-i-glossary"),
    },
    {
        "report": "wg1",
        "annex": "ii",
        "input_file": "annex-ii-acronyms.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "annex-ii-acronyms"),
    },
    {
        "report": "wg3",
        "annex": "i",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg3", "annex-i-glossary"),
    },
    {
        "report": "wg3",
        "annex": "vi",
        "input_file": "annex-vi-acronyms.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg3", "annex-vi-acronyms"),
    },
    {
        "report": "syr",
        "annex": "i",
        "input_file": "annex-i-glossary.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annex-i-glossary"),
    },
    {
        "report": "syr",
        "annex": "ii",
        "input_file": "annex-ii-acronyms.html",
        "input_dir": Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annex-ii-acronyms"),
    },
]


def transform_file(file_info):
    """Transform a single file."""
    input_path = file_info["input_dir"] / file_info["input_file"]
    output_path = file_info["input_dir"] / "semantic.html"
    
    print(f"\n{'='*70}")
    print(f"Transforming: {file_info['report'].upper()} Annex {file_info['annex'].upper()}")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"{'='*70}")
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return False
    
    # Check if already transformed
    if output_path.exists():
        print(f"⚠️  Output file already exists: {output_path}")
        response = input("   Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("   Skipping...")
            return True
    
    # Transform
    transformer = CSSRoleTransformer()
    success = transformer.transform_html(
        input_html_path=input_path,
        output_html_path=output_path,
        report=file_info["report"],
        annex=file_info["annex"]
    )
    
    if success:
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"✅ Success! Output written to: {output_path}")
            print(f"   File size: {size:,} bytes")
        else:
            print(f"⚠️  Transformation reported success but output file not found")
        return True
    else:
        print(f"❌ Transformation failed")
        return False


def main():
    """Transform all files."""
    print("AR6 Glossary/Acronym CSS Role Transformation")
    print("=" * 70)
    print(f"Transforming {len(FILES_TO_TRANSFORM)} files...")
    
    results = []
    for file_info in FILES_TO_TRANSFORM:
        success = transform_file(file_info)
        results.append({
            "file": f"{file_info['report']} Annex {file_info['annex']}",
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









