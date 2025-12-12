"""
Parser for acronym/abbreviation entries.

Detects when definitions start with the full term and reorganizes entries:
- Extracts full term from definition
- Moves acronym/abbreviation to abbreviation field
- Updates entry structure accordingly

Uses AcronymExtractor from amilib for business logic.
"""
import sys
from pathlib import Path
from typing import Dict
import lxml.etree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.util import Util
from amilib.acronym_extractor import AcronymExtractor
from scripts.glossary_processor.dictionary_template_constants import (
    ROLE_TERM, ROLE_DEFINITION, ROLE_ABBREVIATION, CLASS_ENTRY,
    DATA_TERM, DATA_HAS_ABBREVIATION, ANNEX_TYPE_ACRONYMS,
    CLASS_ROLE_TERM, CLASS_ROLE_DEFINITION, CLASS_ABBREVIATION
)

logger = Util.get_logger(__name__)


class AcronymParser:
    """
    Parses acronym/abbreviation entries in HTML to extract full terms.
    
    Uses AcronymExtractor from amilib for business logic.
    Handles HTML-specific structure manipulation.
    """
    
    @classmethod
    def parse_entry(cls, entry_elem: ET.Element, entry_type: str = ANNEX_TYPE_ACRONYMS) -> bool:
        """
        Parse an entry to extract full term from definition if it starts with it.
        
        Args:
            entry_elem: Entry element to parse
            entry_type: Type of entry ('acronyms' or 'glossary')
            
        Returns:
            True if entry was modified, False otherwise
        """
        # Only process acronym entries
        if entry_type != ANNEX_TYPE_ACRONYMS:
            return False
        
        # Get term and definition
        term_elem = entry_elem.xpath(f'.//div[@role="{ROLE_TERM}"]')
        def_elem = entry_elem.xpath(f'.//div[@role="{ROLE_DEFINITION}"]')
        
        if not term_elem or not def_elem:
            return False
        
        term_text = ''.join(term_elem[0].itertext()).strip()
        def_text = ''.join(def_elem[0].itertext()).strip()
        
        if not term_text or not def_text:
            return False
        
        # Check if term looks like an acronym/abbreviation
        if not AcronymExtractor.is_acronym(term_text):
            return False
        
        # Try to extract full term from definition
        full_term, remaining_def = AcronymExtractor.extract_full_term(term_text, def_text)
        
        if full_term:
            # Reorganize entry
            cls._reorganize_entry(entry_elem, term_elem[0], def_elem[0], 
                                 term_text, full_term, remaining_def)
            return True
        
        return False
    
    
    @classmethod
    def _reorganize_entry(cls, entry_elem: ET.Element, term_elem: ET.Element,
                         def_elem: ET.Element, acronym: str, full_term: str,
                         remaining_def: str):
        """
        Reorganize entry to have full term as term and acronym as abbreviation.
        
        Args:
            entry_elem: Entry element
            term_elem: Current term element
            def_elem: Current definition element
            acronym: The acronym/abbreviation
            full_term: The full term extracted from definition
            remaining_def: Remaining definition text
        """
        # Preserve role attribute
        term_role = term_elem.get("role")
        def_role = def_elem.get("role")
        
        # Update term element with full term
        term_elem.clear()
        if term_role:
            term_elem.set("role", term_role)
        
        term_span = ET.SubElement(term_elem, "span")
        term_span.set("class", CLASS_ROLE_TERM)
        term_span.text = full_term
        
        # Add abbreviation
        abbrev_span = ET.SubElement(term_elem, "span")
        abbrev_span.set("role", ROLE_ABBREVIATION)
        abbrev_span.set("class", CLASS_ABBREVIATION)
        abbrev_span.set("data-variant", acronym)
        abbrev_span.text = acronym
        
        # Update definition element
        def_elem.clear()
        if def_role:
            def_elem.set("role", def_role)
        
        if remaining_def:
            def_span = ET.SubElement(def_elem, "span")
            def_span.set("class", CLASS_ROLE_DEFINITION)
            def_span.text = remaining_def
        
        # Update data attributes
        entry_elem.set(DATA_TERM, full_term)
        entry_elem.set(DATA_HAS_ABBREVIATION, "true")
        
        # Update entry ID if needed (normalize full term)
        normalized_term = AcronymExtractor.normalize_term(full_term)
        entry_id = f"{entry_elem.get('id', '').split('-entry-')[0]}-entry-{normalized_term}"
        entry_elem.set('id', entry_id)
        
        logger.debug(f"Reorganized entry: '{acronym}' -> term='{full_term}', abbrev='{acronym}'")
    
    @classmethod
    def parse_dictionary(cls, html_elem: ET.Element, entry_type: str = ANNEX_TYPE_ACRONYMS) -> int:
        """
        Parse all entries in a dictionary.
        
        Args:
            html_elem: Root HTML element containing dictionary
            entry_type: Type of entries ('acronyms' or 'glossary')
            
        Returns:
            Number of entries modified
        """
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        modified_count = 0
        
        for entry in entries:
            if cls.parse_entry(entry, entry_type):
                modified_count += 1
        
        logger.info(f"Parsed {len(entries)} entries, modified {modified_count}")
        return modified_count


def main():
    """Command-line interface for testing."""
    from amilib.ami_html import HtmlUtil, HtmlLib
    
    if len(sys.argv) < 2:
        print("Usage: acronym_parser.py <input_html> [output_html]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Parse HTML
    html_tree = HtmlUtil.parse_html_lxml(str(input_path))
    html_elem = html_tree.getroot()
    
    # Parse entries
    modified = AcronymParser.parse_dictionary(html_elem, ANNEX_TYPE_ACRONYMS)
    
    print(f"Modified {modified} entries")
    
    # Write output if specified
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)
        print(f"Output written to: {output_path}")


if __name__ == '__main__':
    main()

