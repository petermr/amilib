"""
Stage 2: Section Detection Module
Identifies section headings (e.g., "A", "B", "C" sections).
"""
import re
from typing import List, Dict, Optional
import lxml.etree as ET

from amilib.util import Util

logger = Util.get_logger(__name__)


class SectionDetector:
    """Detects section headings in glossary/acronym documents."""
    
    # Font size threshold for section headings (larger than entries)
    SECTION_FONT_SIZE_MIN = 10.0
    
    # Patterns for section headings
    SECTION_PATTERNS = [
        re.compile(r'^[A-Z]$'),  # Single letter
        re.compile(r'^[A-Z]\s*$'),  # Single letter with spaces
        re.compile(r'^Numbers?$', re.IGNORECASE),
        re.compile(r'^Special\s+Characters?$', re.IGNORECASE),
    ]
    
    @classmethod
    def detect_sections(cls, html_elem: ET.Element, entries: List[Dict]) -> List[Dict]:
        """
        Detect section headings and create section hierarchy.
        
        Args:
            html_elem: HTML element
            entries: List of entry dictionaries
            
        Returns:
            List of section dictionaries, each containing:
            - 'heading': section heading text
            - 'start_index': index of first entry in section
            - 'end_index': index of last entry in section
        """
        logger.info("Detecting sections...")
        
        # Find potential section headings in the HTML
        section_headings = cls._find_section_headings(html_elem)
        
        # Map sections to entries
        sections = cls._map_sections_to_entries(section_headings, entries)
        
        logger.info(f"Detected {len(sections)} sections")
        return sections
    
    @classmethod
    def _find_section_headings(cls, html_elem: ET.Element) -> List[Dict]:
        """Find potential section headings in HTML."""
        headings = []
        
        # Look for divs that might be section headings
        divs = html_elem.xpath('//div[@left and @top]')
        
        for div in divs:
            # Check font size
            font_size = cls._get_font_size(div)
            if font_size < cls.SECTION_FONT_SIZE_MIN:
                continue
            
            # Get text
            text = cls._get_text(div).strip()
            if not text:
                continue
            
            # Check if matches section pattern
            if cls._matches_section_pattern(text):
                try:
                    top = float(div.get('top', '0'))
                    headings.append({
                        'text': text,
                        'top': top,
                        'div': div
                    })
                    logger.debug(f"Found section heading: '{text}' at top={top:.1f}")
                except (ValueError, TypeError):
                    continue
        
        # Sort by position
        headings.sort(key=lambda h: h['top'])
        return headings
    
    @classmethod
    def _get_font_size(cls, div: ET.Element) -> float:
        """Get font size from div."""
        spans = div.xpath('.//span[@style]')
        if spans:
            style = spans[0].get('style', '')
            match = re.search(r'font-size:\s*([\d.]+)', style)
            if match:
                return float(match.group(1))
        return 0.0
    
    @classmethod
    def _get_text(cls, div: ET.Element) -> str:
        """Get text content from div."""
        spans = div.xpath('.//span')
        return ''.join(span.text or '' for span in spans if span.text)
    
    @classmethod
    def _matches_section_pattern(cls, text: str) -> bool:
        """Check if text matches section heading pattern."""
        for pattern in cls.SECTION_PATTERNS:
            if pattern.match(text):
                return True
        return False
    
    @classmethod
    def _map_sections_to_entries(cls, headings: List[Dict], entries: List[Dict]) -> List[Dict]:
        """Map section headings to entry indices."""
        if not headings:
            # No sections found - create single section with all entries
            return [{
                'heading': None,
                'start_index': 0,
                'end_index': len(entries) - 1 if entries else 0
            }]
        
        sections = []
        
        # Get entry positions
        entry_positions = []
        for i, entry in enumerate(entries):
            if entry['divs']:
                try:
                    top = float(entry['divs'][0].get('top', '0'))
                    entry_positions.append((i, top))
                except (ValueError, TypeError):
                    entry_positions.append((i, 0.0))
        
        # Map headings to entries
        for i, heading in enumerate(headings):
            heading_top = heading['top']
            
            # Find first entry after this heading
            start_idx = 0
            for entry_idx, entry_top in entry_positions:
                if entry_top >= heading_top:
                    start_idx = entry_idx
                    break
            
            # End index is start of next section or end of entries
            if i + 1 < len(headings):
                next_heading_top = headings[i + 1]['top']
                end_idx = len(entries) - 1
                for entry_idx, entry_top in entry_positions:
                    if entry_top >= next_heading_top:
                        end_idx = entry_idx - 1
                        break
            else:
                end_idx = len(entries) - 1
            
            sections.append({
                'heading': heading['text'],
                'start_index': start_idx,
                'end_index': end_idx
            })
        
        return sections

