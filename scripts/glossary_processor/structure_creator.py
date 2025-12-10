"""
Stage 3: Structure Creation Module
Creates semantic paragraph structure from detected entries.
"""
import re
from typing import List, Dict
import lxml.etree as ET

from amilib.ami_html import HtmlLib
from amilib.util import Util

logger = Util.get_logger(__name__)


class StructureCreator:
    """Creates structured HTML from detected entries."""
    
    @classmethod
    def create_entry_structure(cls, entries: List[Dict], sections: List[Dict], 
                              report: str, annex: str, entry_type: str) -> ET.Element:
        """
        Create structured HTML from entries and sections.
        
        Args:
            entries: List of entry dictionaries
            sections: List of section dictionaries
            report: Report name (e.g., 'wg3')
            annex: Annex identifier (e.g., 'vi')
            entry_type: 'acronym' or 'glossary'
            
        Returns:
            Structured HTML element
        """
        logger.info(f"Creating structure for {len(entries)} entries...")
        
        # Create root HTML structure
        html_elem = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html_elem)
        
        # Create glossary container
        glossary_div = ET.SubElement(body, 'div')
        glossary_div.set('class', 'glossary')
        glossary_div.set('data-report', report)
        glossary_div.set('data-annex', annex)
        glossary_div.set('data-type', entry_type)
        
        # Add title
        title = ET.SubElement(glossary_div, 'h1')
        annex_name = annex.replace('-', ' ').title()
        title.text = f"Annex {annex_name}: {entry_type.title()}"
        
        # Process sections
        for section in sections:
            section_elem = cls._create_section(section, entries, report, annex, entry_type)
            if section_elem is not None:
                glossary_div.append(section_elem)
        
        logger.info("Structure created successfully")
        return html_elem
    
    @classmethod
    def _create_section(cls, section: Dict, entries: List[Dict], 
                       report: str, annex: str, entry_type: str) -> ET.Element:
        """Create a section element with its entries."""
        section_elem = ET.Element('section')
        section_elem.set('class', 'section')
        
        # Add section heading if present
        if section.get('heading'):
            heading_elem = ET.SubElement(section_elem, 'h2')
            heading_elem.text = section['heading']
            section_elem.set('data-letter', section['heading'].strip())
        
        # Add entries in this section
        start_idx = section.get('start_index', 0)
        end_idx = section.get('end_index', len(entries) - 1)
        
        for i in range(start_idx, end_idx + 1):
            if i < len(entries):
                entry_elem = cls._create_entry(entries[i], report, annex, entry_type, i)
                if entry_elem is not None:
                    section_elem.append(entry_elem)
        
        return section_elem
    
    @classmethod
    def _create_entry(cls, entry: Dict, report: str, annex: str, 
                     entry_type: str, index: int) -> ET.Element:
        """Create an entry element."""
        entry_elem = ET.Element('div')
        entry_elem.set('class', 'entry')
        
        # Generate entry ID
        term = entry.get('term', '').strip()
        if term:
            normalized_term = cls._normalize_term(term)
            entry_id = f"{report}-{annex}-entry-{normalized_term}"
            entry_elem.set('id', entry_id)
        
        # Add term/acronym
        term_elem = ET.SubElement(entry_elem, 'span')
        term_elem.set('class', 'term')
        term_elem.text = term
        
        # Add definition
        definition = entry.get('definition', '').strip()
        if definition:
            definition_elem = ET.SubElement(entry_elem, 'span')
            definition_elem.set('class', 'definition')
            
            # Create paragraph structure for definition
            # Split by common paragraph markers
            paragraphs = cls._split_into_paragraphs(definition)
            
            if len(paragraphs) == 1:
                # Single paragraph
                para_elem = ET.SubElement(definition_elem, 'p')
                para_elem.text = paragraphs[0]
            else:
                # Multiple paragraphs
                for para_text in paragraphs:
                    para_elem = ET.SubElement(definition_elem, 'p')
                    para_elem.text = para_text
        
        # Add metadata
        entry_elem.set('data-report', report)
        entry_elem.set('data-annex', annex)
        entry_elem.set('data-type', entry_type)
        entry_elem.set('data-entry-number', str(index))
        
        return entry_elem
    
    @classmethod
    def _normalize_term(cls, term: str) -> str:
        """Normalize term for use in ID."""
        # Remove special characters, lowercase, replace spaces with hyphens
        normalized = re.sub(r'[^\w\s-]', '', term)
        normalized = normalized.lower()
        normalized = re.sub(r'\s+', '-', normalized)
        normalized = normalized.strip('-')
        return normalized
    
    @classmethod
    def _split_into_paragraphs(cls, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split by double newlines or common paragraph markers
        paragraphs = re.split(r'\n\n+', text)
        # Also check for sentence-ending patterns that might indicate paragraphs
        # For now, return as single paragraph
        return [p.strip() for p in paragraphs if p.strip()]

