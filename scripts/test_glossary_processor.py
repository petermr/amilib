"""
Test script for glossary processor Phase 1.
Tests on WG3 Annex VI (Acronyms) - smallest file.
"""
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources
from scripts.glossary_processor.glossary_processor import GlossaryProcessor

def main():
    """Test the glossary processor."""
    # Test file: WG3 Annex VI (Acronyms)
    input_html = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", 
                     "wg3", "annex-vi-acronyms", "annex-vi-acronyms.html")
    
    if not input_html.exists():
        print(f"❌ Input file not found: {input_html}")
        return 1
    
    # Output file - save alongside original in permanent location
    output_dir = input_html.parent
    output_html = output_dir / "structured.html"
    
    print(f"Input:  {input_html}")
    print(f"Output: {output_html}")
    print()
    
    # Process
    success = GlossaryProcessor.process(
        input_html_path=input_html,
        output_html_path=output_html,
        report="wg3",
        annex="vi",
        entry_type="acronym"
    )
    
    if success:
        print(f"\n✅ Success! Output written to: {output_html}")
        print(f"   File size: {output_html.stat().st_size:,} bytes")
        return 0
    else:
        print("\n❌ Processing failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

