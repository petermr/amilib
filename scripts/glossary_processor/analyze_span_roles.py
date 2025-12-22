"""
Standalone tool to analyze spans and their potential roles.

Analyzes font properties and coordinates to identify patterns
that can be used for role detection.
"""
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import sys
import lxml.etree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.ami_html import AmiFont, CSSStyle, HtmlLib
from amilib.util import Util

logger = Util.get_logger(__name__)


class SpanRoleAnalyzer:
    """Analyzes spans to identify potential roles based on font and coordinates."""
    
    def __init__(self):
        self.font_patterns = defaultdict(lambda: {
            "count": 0,
            "elements": [],
            "font_properties": {},
            "coordinate_ranges": {"x0": [], "y0": [], "x1": [], "y1": []},
            "font_sizes": []
        })
    
    def analyze_html(self, html_path: Path) -> Dict:
        """
        Analyze all spans in HTML file.
        
        Returns:
            Dictionary with analysis results
        """
        html_elem = HtmlLib.parse_html(str(html_path))
        if html_elem is None:
            logger.error(f"Failed to parse HTML: {html_path}")
            return {}
        
        # Find all spans with style attributes
        spans = html_elem.xpath(".//span[@style]")
        logger.info(f"Found {len(spans)} spans with styles")
        
        for span in spans:
            self._analyze_span(span)
        
        return self._summarize_analysis()
    
    def _analyze_span(self, span: ET.Element):
        """Analyze a single span."""
        # Extract CSS style from style attribute
        style_attr = span.get("style")
        if not style_attr:
            return
        
        css_style = CSSStyle.create_css_style_from_css_string(style_attr)
        if css_style is None:
            return
        
        font_family = css_style.font_family
        if not font_family:
            return
        
        # Extract font properties using AmiFont (truncates prefix automatically)
        ami_font = AmiFont.extract_name_weight_style_stretched_as_font(font_family)
        
        # Get coordinates from style or attributes
        x0 = css_style.get_numeric_attval("x0") or (float(span.get("x0")) if span.get("x0") else None)
        y0 = css_style.get_numeric_attval("y0") or (float(span.get("y0")) if span.get("y0") else None)
        x1 = css_style.get_numeric_attval("x1") or (float(span.get("x1")) if span.get("x1") else None)
        y1 = css_style.get_numeric_attval("y1") or (float(span.get("y1")) if span.get("y1") else None)
        
        # Get font size
        font_size = css_style.font_size
        
        # Create font pattern key (using trimmed font name)
        font_name_trimmed = AmiFont.trim_pdf_prefix(font_family)
        pattern_key = f"{font_name_trimmed}|{ami_font.weight}|{ami_font.style}|{ami_font.stretched}"
        
        # Update pattern statistics
        pattern = self.font_patterns[pattern_key]
        pattern["count"] += 1
        pattern["elements"].append(span)
        
        # Store font properties
        if not pattern["font_properties"]:
            pattern["font_properties"] = {
                "family": font_name_trimmed,
                "weight": str(ami_font.weight),
                "style": str(ami_font.style),
                "stretched": str(ami_font.stretched),
                "is_bold": ami_font.is_bold,
                "is_italic": ami_font.is_italic
            }
        
        # Store coordinates
        if x0 is not None:
            pattern["coordinate_ranges"]["x0"].append(x0)
        if y0 is not None:
            pattern["coordinate_ranges"]["y0"].append(y0)
        if x1 is not None:
            pattern["coordinate_ranges"]["x1"].append(x1)
        if y1 is not None:
            pattern["coordinate_ranges"]["y1"].append(y1)
        
        # Store font sizes
        if font_size:
            try:
                pattern["font_sizes"].append(float(font_size))
            except (ValueError, TypeError):
                pass
    
    def _summarize_analysis(self) -> Dict:
        """Summarize analysis results."""
        summary = {
            "total_patterns": len(self.font_patterns),
            "patterns": []
        }
        
        for pattern_key, pattern_data in sorted(self.font_patterns.items(), 
                                                 key=lambda x: x[1]["count"], 
                                                 reverse=True):
            pattern_info = {
                "font_family": pattern_data["font_properties"]["family"],
                "weight": pattern_data["font_properties"]["weight"],
                "style": pattern_data["font_properties"]["style"],
                "stretched": pattern_data["font_properties"]["stretched"],
                "is_bold": pattern_data["font_properties"]["is_bold"],
                "is_italic": pattern_data["font_properties"]["is_italic"],
                "count": pattern_data["count"],
                "font_size_range": self._get_range(pattern_data["font_sizes"]),
                "x0_range": self._get_range(pattern_data["coordinate_ranges"]["x0"]),
                "y0_range": self._get_range(pattern_data["coordinate_ranges"]["y0"]),
                "sample_texts": self._get_sample_texts(pattern_data["elements"], 5)
            }
            summary["patterns"].append(pattern_info)
        
        return summary
    
    def _get_range(self, values: List[float]) -> Dict:
        """Get min/max range from list of values."""
        if not values:
            return {"min": None, "max": None}
        return {"min": min(values), "max": max(values)}
    
    def _get_sample_texts(self, elements: List[ET.Element], max_samples: int) -> List[str]:
        """Get sample text from elements."""
        samples = []
        for elem in elements[:max_samples]:
            text = ''.join(elem.itertext()).strip()
            if text:
                samples.append(text[:50])  # First 50 chars
        return samples
    
    def print_analysis_report(self, summary: Dict):
        """Print formatted analysis report."""
        print(f"\n{'='*80}")
        print(f"Span Role Analysis Report")
        print(f"{'='*80}")
        print(f"Total font patterns found: {summary['total_patterns']}\n")
        
        for i, pattern in enumerate(summary["patterns"], 1):
            print(f"\nPattern {i}: {pattern['font_family']}")
            print(f"  Count: {pattern['count']}")
            print(f"  Weight: {pattern['weight']}, Style: {pattern['style']}, Stretched: {pattern['stretched']}")
            print(f"  Bold: {pattern['is_bold']}, Italic: {pattern['is_italic']}")
            
            if pattern['font_size_range']['min'] is not None:
                print(f"  Font Size: {pattern['font_size_range']['min']:.1f} - {pattern['font_size_range']['max']:.1f}")
            
            if pattern['x0_range']['min'] is not None:
                print(f"  X0 Range: {pattern['x0_range']['min']:.1f} - {pattern['x0_range']['max']:.1f}")
            
            if pattern['y0_range']['min'] is not None:
                print(f"  Y0 Range: {pattern['y0_range']['min']:.1f} - {pattern['y0_range']['max']:.1f}")
            
            print(f"  Sample texts:")
            for text in pattern['sample_texts']:
                print(f"    - {text}")


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: analyze_span_roles.py <html_file>")
        sys.exit(1)
    
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)
    
    analyzer = SpanRoleAnalyzer()
    summary = analyzer.analyze_html(html_path)
    analyzer.print_analysis_report(summary)


if __name__ == '__main__':
    main()

