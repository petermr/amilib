"""
Stage 1.2-1.3: Entry Detection Module
Detects entry boundaries and groups entry components.
"""
import re
from typing import List, Dict, Optional, Tuple
import lxml.etree as ET

from amilib.util import Util

logger = Util.get_logger(__name__)


class EntryDetector:
    """Detects glossary/acronym entry boundaries."""
    
    # Vertical spacing threshold for new entry
    ENTRY_GAP_THRESHOLD = 15.0  # pixels
    
    # Horizontal position ranges for acronym/term (left column)
    TERM_LEFT_MIN = 50.0
    TERM_LEFT_MAX = 350.0
    
    # Horizontal position for definition start (right column)
    DEFINITION_LEFT_MIN = 380.0
    
    @classmethod
    def detect_entries(cls, html_elem: ET.Element, entry_type: str = 'acronym') -> List[Dict]:
        """
        Detect entry boundaries based on position and font analysis.
        
        Args:
            html_elem: HTML element with positioned divs
            entry_type: 'acronym' or 'glossary'
            
        Returns:
            List of entry dictionaries, each containing:
            - 'divs': list of div elements belonging to entry
            - 'term': extracted term/acronym
            - 'definition': extracted definition
        """
        logger.info(f"Detecting {entry_type} entries...")
        
        # Get all positioned divs
        divs = html_elem.xpath('//div[@left and @top]')
        if not divs:
            logger.warning("No positioned divs found")
            return []
        
        # Sort by vertical position
        sorted_divs = cls._sort_divs_by_position(divs)
        
        # Detect entry boundaries
        entry_boundaries = cls._detect_entry_boundaries(sorted_divs, entry_type)
        
        # Group divs into entries
        entries = cls._group_entry_components(sorted_divs, entry_boundaries, entry_type)
        
        logger.info(f"Detected {len(entries)} entries")
        return entries
    
    @classmethod
    def _sort_divs_by_position(cls, divs: List[ET.Element]) -> List[ET.Element]:
        """Sort divs by vertical position (top attribute)."""
        def get_top(div):
            try:
                return float(div.get('top', '0'))
            except (ValueError, TypeError):
                return 0.0
        
        return sorted(divs, key=get_top)
    
    @classmethod
    def _detect_entry_boundaries(cls, divs: List[ET.Element], entry_type: str) -> List[int]:
        """
        Detect where new entries start.
        
        Returns:
            List of indices where new entries begin
        """
        boundaries = [0]  # First entry starts at index 0
        
        if len(divs) < 2:
            return boundaries
        
        for i in range(1, len(divs)):
            prev_div = divs[i - 1]
            curr_div = divs[i]
            
            # Calculate vertical gap
            gap = cls._calculate_vertical_gap(prev_div, curr_div)
            
            # Check if this is a new entry
            is_new_entry = (
                gap > cls.ENTRY_GAP_THRESHOLD or
                cls._is_term_start(curr_div, entry_type)
            )
            
            if is_new_entry:
                boundaries.append(i)
                logger.debug(f"Entry boundary at index {i}, gap={gap:.1f}")
        
        return boundaries
    
    @classmethod
    def _calculate_vertical_gap(cls, prev_div: ET.Element, curr_div: ET.Element) -> float:
        """Calculate vertical gap between two divs."""
        try:
            prev_top = float(prev_div.get('top', '0'))
            prev_bottom = cls._get_bottom(prev_div)
            curr_top = float(curr_div.get('top', '0'))
            return curr_top - prev_bottom
        except (ValueError, TypeError):
            return 0.0
    
    @classmethod
    def _get_bottom(cls, div: ET.Element) -> float:
        """Get bottom Y coordinate of div."""
        try:
            top = float(div.get('top', '0'))
            height = cls._estimate_height(div)
            return top + height
        except (ValueError, TypeError):
            return 0.0
    
    @classmethod
    def _estimate_height(cls, div: ET.Element) -> float:
        """Estimate div height from font size."""
        spans = div.xpath('.//span[@style]')
        if spans:
            style = spans[0].get('style', '')
            match = re.search(r'font-size:\s*([\d.]+)', style)
            if match:
                font_size = float(match.group(1))
                return font_size * 1.2
        return 12.0
    
    @classmethod
    def _is_term_start(cls, div: ET.Element, entry_type: str) -> bool:
        """
        Check if div starts a new term/acronym entry.
        
        Criteria:
        - Bold text at left margin (for acronyms/glossary)
        - Positioned in term column
        """
        try:
            left = float(div.get('left', '0'))
            
            # Check if in term column
            if not (cls.TERM_LEFT_MIN <= left <= cls.TERM_LEFT_MAX):
                return False
            
            # Check if contains bold text
            spans = div.xpath('.//span[@style]')
            for span in spans:
                style = span.get('style', '')
                # Check for bold font (BlackCn, BoldCn, etc.)
                if 'BlackCn' in style or 'BoldCn' in style or 'Bold' in style:
                    return True
            
            return False
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def _group_entry_components(cls, divs: List[ET.Element], boundaries: List[int], entry_type: str) -> List[Dict]:
        """Group divs into entries."""
        entries = []
        
        for i in range(len(boundaries)):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1] if i + 1 < len(boundaries) else len(divs)
            
            entry_divs = divs[start_idx:end_idx]
            
            # Extract term and definition
            term, definition = cls._extract_term_and_definition(entry_divs, entry_type)
            
            entries.append({
                'divs': entry_divs,
                'term': term,
                'definition': definition,
                'index': i
            })
        
        return entries
    
    @classmethod
    def _extract_term_and_definition(cls, divs: List[ET.Element], entry_type: str) -> Tuple[str, str]:
        """
        Extract term and definition from entry divs.
        
        Returns:
            Tuple of (term, definition)
        """
        term_parts = []
        definition_parts = []
        
        for div in divs:
            try:
                left = float(div.get('left', '0'))
                
                # Get text from spans
                spans = div.xpath('.//span')
                text = ''.join(span.text or '' for span in spans if span.text).strip()
                
                if not text:
                    continue
                
                # Determine if term or definition based on position
                if cls.TERM_LEFT_MIN <= left <= cls.TERM_LEFT_MAX:
                    # Check if bold (term/acronym)
                    is_bold = any(
                        'BlackCn' in span.get('style', '') or 
                        'BoldCn' in span.get('style', '') or
                        'Bold' in span.get('style', '')
                        for span in spans if span.get('style')
                    )
                    if is_bold:
                        term_parts.append(text)
                    else:
                        definition_parts.append(text)
                elif left >= cls.DEFINITION_LEFT_MIN:
                    definition_parts.append(text)
                else:
                    # Middle column or ambiguous - try to determine from content
                    definition_parts.append(text)
            
            except (ValueError, TypeError):
                continue
        
        term = ' '.join(term_parts).strip()
        definition = ' '.join(definition_parts).strip()
        
        return term, definition

