"""
Parser for acronym/abbreviation entries.

Detects when definitions start with the full term and reorganizes entries:
- Extracts full term from definition
- Moves acronym/abbreviation to abbreviation field
- Updates entry structure accordingly
"""
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import lxml.etree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.util import Util
from scripts.glossary_processor.dictionary_template_constants import (
    ROLE_TERM, ROLE_DEFINITION, ROLE_ABBREVIATION, CLASS_ENTRY,
    DATA_TERM, DATA_HAS_ABBREVIATION, ANNEX_TYPE_ACRONYMS,
    CLASS_ROLE_TERM, CLASS_ROLE_DEFINITION, CLASS_ABBREVIATION
)

logger = Util.get_logger(__name__)


class AcronymParser:
    """Parses acronym/abbreviation entries to extract full terms."""
    
    # Patterns to detect if definition starts with full term
    # Common patterns: "Full Term Name", "Full Term Name (additional info)", etc.
    FULL_TERM_PATTERNS = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Capitalized words: "Intergovernmental Panel"
        r'^([a-z]+(?:\s+[a-z]+)*)',  # Lowercase words: "assets under management"
        r'^([A-Z][a-z]+(?:\s+[a-z]+)*)',  # Mixed: "Carbon dioxide"
    ]
    
    # Maximum words to consider as full term (usually 2-5 words)
    MAX_FULL_TERM_WORDS = 6
    
    # Minimum words for full term (usually 2+ words)
    MIN_FULL_TERM_WORDS = 2
    
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
        if not cls._is_acronym(term_text):
            return False
        
        # Try to extract full term from definition
        full_term, remaining_def = cls._extract_full_term(term_text, def_text)
        
        if full_term:
            # Reorganize entry
            cls._reorganize_entry(entry_elem, term_elem[0], def_elem[0], 
                                 term_text, full_term, remaining_def)
            return True
        
        return False
    
    @classmethod
    def _is_acronym(cls, text: str) -> bool:
        """
        Check if text looks like an acronym/abbreviation.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be an acronym
        """
        text = text.strip()
        
        # Acronym patterns:
        # - All uppercase, 2-10 characters: "IPCC", "AR6", "NDC"
        # - Mixed case with periods: "U.S.", "U.K."
        # - Numbers allowed: "AR6", "CO2"
        
        # All uppercase, short
        if re.match(r'^[A-Z]{2,10}$', text):
            return True
        
        # Mixed case with periods
        if re.match(r'^[A-Z]\.?[A-Z]\.?[A-Z]?\.?$', text):
            return True
        
        # Contains numbers (e.g., "AR6", "CO2")
        if re.match(r'^[A-Z0-9]{2,10}$', text):
            return True
        
        # Single word, all caps, short
        if len(text) <= 10 and text.isupper() and not ' ' in text:
            return True
        
        return False
    
    @classmethod
    def _extract_full_term(cls, acronym: str, definition: str) -> Tuple[Optional[str], str]:
        """
        Extract full term from definition if it starts with it.
        
        Args:
            acronym: The acronym/abbreviation
            definition: The definition text
            
        Returns:
            Tuple of (full_term, remaining_definition) or (None, definition) if not found
        """
        definition = definition.strip()
        
        # Try to match patterns where definition starts with full term
        # Common patterns:
        # - "Full Term Name" (exact match)
        # - "Full Term Name, additional info"
        # - "Full Term Name (additional info)"
        # - "Full Term Name. Additional info"
        
        # Split definition into words
        words = definition.split()
        
        # Try different lengths of initial words, starting from longest possible match
        # This ensures we get the complete full term
        # Stop at sentence boundaries (period, exclamation, question mark)
        for num_words in range(min(len(words), cls.MAX_FULL_TERM_WORDS), 
                              cls.MIN_FULL_TERM_WORDS - 1, -1):
            # Get potential full term
            potential_full_term = ' '.join(words[:num_words])
            
            # Check if we should stop at sentence boundary first
            # If the last word ends with sentence punctuation, check if this matches
            last_word = words[num_words - 1] if num_words > 0 else ''
            if last_word and last_word[-1] in '.!?':
                # Remove punctuation for matching
                potential_full_term_clean = potential_full_term.rstrip('.!?')
                if cls._could_be_full_term(acronym, potential_full_term_clean):
                    # This looks like end of sentence - use this as full term
                    remaining = ' '.join(words[num_words:]).strip()
                    remaining = re.sub(r'^[,;:\-–—]\s*', '', remaining)
                    return potential_full_term_clean, remaining
            
            # Check if this could be the full term for the acronym (without punctuation)
            if cls._could_be_full_term(acronym, potential_full_term):
                # Get remaining definition
                remaining = ' '.join(words[num_words:]).strip()
                
                # Clean up remaining definition (remove leading punctuation)
                remaining = re.sub(r'^[,;:\-–—]\s*', '', remaining)
                
                return potential_full_term, remaining
        
        return None, definition
    
    @classmethod
    def _could_be_full_term(cls, acronym: str, potential_full_term: str) -> bool:
        """
        Check if potential_full_term could be the full term for acronym.
        
        Uses heuristics:
        - First letters of words match acronym exactly
        - Handles stop words (the, of, on, etc.) that don't contribute
        
        Args:
            acronym: The acronym/abbreviation
            potential_full_term: Potential full term to check
            
        Returns:
            True if this could be the full term
        """
        # Remove common words that don't contribute to acronym
        stop_words = {'the', 'a', 'an', 'of', 'for', 'and', 'or', 'in', 'on', 'at', 'to'}
        words = [w for w in potential_full_term.split() if w.lower() not in stop_words]
        
        if not words:
            return False
        
        # Extract first letters (case-insensitive)
        first_letters = ''.join([w[0].upper() for w in words if w])
        acronym_clean = acronym.upper().replace('.', '').replace('-', '').replace(' ', '')
        
        # Exact match is best
        if first_letters == acronym_clean:
            return True
        
        # For acronyms with numbers (e.g., AR6), check if letters match
        # Extract only letters from acronym
        acronym_letters = ''.join([c for c in acronym_clean if c.isalpha()])
        if acronym_letters and first_letters == acronym_letters:
            return True
        
        # For very short acronyms (2-3 chars), be more lenient
        # Check if first letters start with acronym
        if len(acronym_clean) <= 3 and len(first_letters) >= len(acronym_clean):
            if first_letters[:len(acronym_clean)] == acronym_clean:
                return True
        
        # Special case: "GHG" -> "greenhouse gas"
        # This is a common abbreviation where GHG stands for "greenhouse gas(es)"
        # Even though "greenhouse gas" starts with G-G, GHG is widely accepted
        # Accept if we have words starting with G and the phrase relates to greenhouse/gas
        if acronym_clean == "GHG":
            # Check if we have at least 2 words and first word starts with G
            if len(words) >= 2:
                word1_first = words[0][0].upper() if words[0] else ''
                # Accept if first word starts with G and it's a two-word phrase
                # (common pattern: "greenhouse gas", "greenhouse gases")
                if word1_first == 'G':
                    # Check if second word relates to gas/gases
                    word2_lower = words[1].lower() if len(words) > 1 else ''
                    if 'gas' in word2_lower:
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
        normalized_term = cls._normalize_term(full_term)
        entry_id = f"{entry_elem.get('id', '').split('-entry-')[0]}-entry-{normalized_term}"
        entry_elem.set('id', entry_id)
        
        logger.debug(f"Reorganized entry: '{acronym}' -> term='{full_term}', abbrev='{acronym}'")
    
    @classmethod
    def _normalize_term(cls, term: str) -> str:
        """Normalize term for use in ID."""
        # Convert to lowercase, replace spaces with hyphens
        normalized = term.lower().strip()
        normalized = re.sub(r'[^\w\s-]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', '-', normalized)  # Replace spaces with hyphens
        return normalized
    
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

