"""
Stage 1.1: Page Joining Module
Removes page boundaries and merges consecutive divs that belong to the same entry.
"""
import re
from typing import List, Optional
import lxml.etree as ET

from amilib.util import Util

logger = Util.get_logger(__name__)


class PageJoiner:
    """Joins pages seamlessly by removing page breaks and merging content."""
    
    # Threshold for detecting page breaks (large vertical gaps)
    PAGE_BREAK_THRESHOLD = 100.0  # pixels
    
    @classmethod
    def join_pages(cls, html_elem: ET.Element) -> ET.Element:
        """
        Remove page boundaries and merge consecutive divs.
        
        Args:
            html_elem: Root HTML element containing page-separated divs
            
        Returns:
            HTML element with pages joined seamlessly (same element, modified in place)
        """
        logger.info("Joining pages...")
        
        # Get all divs with position attributes
        divs = html_elem.xpath('//div[@left and @top]')
        logger.debug(f"Found {len(divs)} positioned divs")
        
        if not divs:
            logger.warning("No positioned divs found")
            return html_elem
        
        # Sort divs by vertical position (top)
        sorted_divs = cls._sort_divs_by_position(divs)
        
        # Detect page breaks (for logging/debugging)
        # Note: Actual merging happens during entry detection
        page_breaks = cls._detect_page_breaks(sorted_divs)
        
        logger.info(f"Found {len(page_breaks)} page breaks in {len(sorted_divs)} divs")
        return html_elem
    
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
    def _detect_page_breaks(cls, divs: List[ET.Element]) -> List[int]:
        """
        Detect page breaks.
        
        Page breaks are detected by:
        - Large vertical gaps (> PAGE_BREAK_THRESHOLD)
        - Reset of vertical position (top goes back to small value)
        
        Returns:
            List of indices where page breaks occur
        """
        if not divs:
            return []
        
        page_breaks = []
        prev_div = None
        
        for i, div in enumerate(divs):
            if prev_div is None:
                prev_div = div
                continue
            
            # Calculate vertical gap
            try:
                prev_top = float(prev_div.get('top', '0'))
                prev_bottom = cls._get_bottom(prev_div)
                curr_top = float(div.get('top', '0'))
                gap = curr_top - prev_bottom
            except (ValueError, TypeError):
                gap = 0
            
            # Check if this is a page break
            is_page_break = (
                gap > cls.PAGE_BREAK_THRESHOLD or
                (prev_bottom > 700 and curr_top < 100)  # New page
            )
            
            if is_page_break:
                logger.debug(f"Page break detected at index {i}: gap={gap:.1f}, prev_bottom={prev_bottom:.1f}, curr_top={curr_top:.1f}")
                page_breaks.append(i)
            
            prev_div = div
        
        return page_breaks
    
    @classmethod
    def _get_bottom(cls, div: ET.Element) -> float:
        """Get bottom Y coordinate of div."""
        try:
            top = float(div.get('top', '0'))
            # Estimate height from font size or use default
            height = cls._estimate_height(div)
            return top + height
        except (ValueError, TypeError):
            return 0.0
    
    @classmethod
    def _estimate_height(cls, div: ET.Element) -> float:
        """Estimate div height from font size."""
        # Look for font-size in spans
        spans = div.xpath('.//span[@style]')
        if spans:
            style = spans[0].get('style', '')
            match = re.search(r'font-size:\s*([\d.]+)', style)
            if match:
                font_size = float(match.group(1))
                # Estimate line height as 1.2x font size
                return font_size * 1.2
        
        # Default height
        return 12.0

