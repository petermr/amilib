"""
Main Glossary Processor
Orchestrates the processing pipeline for Phase 1 (Stages 1-3).
"""
from pathlib import Path
from typing import Optional
import lxml.etree as ET

from amilib.ami_html import HtmlLib, HtmlUtil
from amilib.util import Util
import lxml.etree as ET
from lxml.html import HTMLParser

from scripts.glossary_processor.page_joiner import PageJoiner
from scripts.glossary_processor.entry_detector import EntryDetector
from scripts.glossary_processor.section_detector import SectionDetector
from scripts.glossary_processor.structure_creator import StructureCreator

logger = Util.get_logger(__name__)


class GlossaryProcessor:
    """Main processor for glossary/acronym PDF-to-HTML conversion."""
    
    @classmethod
    def process(cls, input_html_path: Path, output_html_path: Path,
                report: str, annex: str, entry_type: str = 'acronym') -> bool:
        """
        Process raw HTML from PDF conversion into structured dictionary.
        
        Args:
            input_html_path: Path to raw HTML file from PDF conversion
            output_html_path: Path to save structured HTML
            report: Report name (e.g., 'wg3')
            annex: Annex identifier (e.g., 'vi')
            entry_type: 'acronym' or 'glossary'
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing {input_html_path} -> {output_html_path}")
        
        try:
            # Stage 1.1: Join pages
            logger.info("Stage 1.1: Joining pages...")
            html_tree = HtmlUtil.parse_html_lxml(str(input_html_path))
            html_elem = html_tree.getroot()
            html_elem = PageJoiner.join_pages(html_elem)
            
            # Stage 1.2-1.3: Detect entries
            logger.info("Stage 1.2-1.3: Detecting entries...")
            entries = EntryDetector.detect_entries(html_elem, entry_type)
            
            if not entries:
                logger.warning("No entries detected!")
                return False
            
            # Stage 2: Detect sections
            logger.info("Stage 2: Detecting sections...")
            sections = SectionDetector.detect_sections(html_elem, entries)
            
            # Stage 3: Create structure
            logger.info("Stage 3: Creating structure...")
            structured_html = StructureCreator.create_entry_structure(
                entries, sections, report, annex, entry_type
            )
            
            # Write output
            output_html_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_html_path, 'wb') as f:
                f.write(ET.tostring(structured_html, encoding='UTF-8', pretty_print=True))
            
            logger.info(f"✅ Successfully processed {len(entries)} entries")
            logger.info(f"   Output: {output_html_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {input_html_path}: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Test the processor on a sample file."""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: glossary_processor.py <input_html> <output_html> <report> <annex> [entry_type]")
        print("Example: glossary_processor.py input.html output.html wg3 vi acronym")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    report = sys.argv[3]
    annex = sys.argv[4]
    entry_type = sys.argv[5] if len(sys.argv) > 5 else 'acronym'
    
    success = GlossaryProcessor.process(input_path, output_path, report, annex, entry_type)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

