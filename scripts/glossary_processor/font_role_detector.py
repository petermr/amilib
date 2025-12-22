"""
Font-based role detection for glossary/acronym entries.

Uses amilib's AmiFont and CSSStyle classes to extract font properties
and map them to semantic roles using configuration files.
"""
from pathlib import Path
from typing import Optional, Dict, List
import json
import sys
import lxml.etree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.ami_html import AmiFont, CSSStyle
from amilib.util import Util

logger = Util.get_logger(__name__)


class FontRoleDetector:
    """Detects semantic roles based on font properties."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize detector with configuration.
        
        Args:
            config_path: Path to font role configuration JSON file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "font_role_config.json"
        
        self.config = self._load_config(config_path)
        self.font_role_mappings = self.config.get("font_role_mappings", [])
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from JSON file."""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {"font_role_mappings": []}
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def detect_role(self, elem: ET.Element, report: str = None, annex: str = None) -> Optional[str]:
        """
        Detect semantic role of an element based on font properties.
        
        Args:
            elem: HTML element (span, div, etc.)
            report: Report name (e.g., 'wg3') for report-specific overrides
            annex: Annex identifier (e.g., 'vi') for report-specific overrides
            
        Returns:
            Role name ('term', 'definition', 'cross_reference', etc.) or None
        """
        # Extract CSS style from style attribute
        style_attr = elem.get("style")
        if not style_attr:
            return None
        
        css_style = CSSStyle.create_css_style_from_css_string(style_attr)
        if css_style is None:
            return None
        
        font_family = css_style.font_family
        if not font_family:
            return None
        
        # Extract font properties using AmiFont (truncates prefix automatically)
        ami_font = AmiFont.extract_name_weight_style_stretched_as_font(font_family)
        
        # Get coordinates
        x0 = css_style.get_numeric_attval("x0") or (float(elem.get("x0")) if elem.get("x0") else None)
        y0 = css_style.get_numeric_attval("y0") or (float(elem.get("y0")) if elem.get("y0") else None)
        
        # Get font size
        font_size = css_style.font_size
        
        # Get report-specific overrides if available
        mappings = self._get_mappings_for_report(report, annex)
        
        # Match against role mappings
        for mapping in mappings:
            if self._matches_mapping(ami_font, css_style, mapping, x0, y0, font_size):
                return mapping["role"]
        
        return None
    
    def _get_mappings_for_report(self, report: str, annex: str) -> List[Dict]:
        """Get font role mappings with report-specific overrides applied."""
        mappings = self.font_role_mappings.copy()
        
        # Apply report-specific overrides
        if report and annex:
            overrides = self.config.get("report_specific_overrides", {}).get(report, {}).get(annex, {})
            if overrides:
                # Merge overrides into mappings
                for mapping in mappings:
                    role = mapping["role"]
                    if role in overrides:
                        override = overrides[role]
                        # Merge font_family_patterns
                        if "font_family_patterns" in override:
                            mapping["font_family_patterns"] = override["font_family_patterns"]
                        # Merge coordinate_rules
                        if "coordinate_rules" in override:
                            if mapping.get("coordinate_rules"):
                                mapping["coordinate_rules"].update(override["coordinate_rules"])
                            else:
                                mapping["coordinate_rules"] = override["coordinate_rules"]
        
        return mappings
    
    def _matches_mapping(self, ami_font: AmiFont, css_style: CSSStyle, mapping: Dict, 
                        x0: Optional[float], y0: Optional[float], font_size: Optional[str]) -> bool:
        """Check if font properties match a role mapping."""
        # Check font properties
        font_props = mapping.get("font_properties", {})
        
        # Check weight
        if "weight" in font_props:
            weight_str = str(ami_font.weight).lower()
            # Handle empty string as "normal"
            if not weight_str or weight_str == "none":
                weight_str = "normal"
            if weight_str not in [w.lower() for w in font_props["weight"]]:
                return False
        
        # Check style
        if "style" in font_props:
            style_str = str(ami_font.style).lower()
            # Handle empty string as "normal"
            if not style_str or style_str == "none":
                style_str = "normal"
            if style_str not in [s.lower() for s in font_props["style"]]:
                return False
        
        # Check stretched
        if "stretched" in font_props:
            stretched_str = str(ami_font.stretched).lower()
            # Handle empty string as "normal"
            if not stretched_str or stretched_str == "none":
                stretched_str = "normal"
            if stretched_str not in [st.lower() for st in font_props["stretched"]]:
                return False
        
        # Check font family patterns
        font_family_patterns = mapping.get("font_family_patterns", [])
        if font_family_patterns:
            font_family = AmiFont.trim_pdf_prefix(ami_font.name or css_style.font_family)
            matches_pattern = False
            for pattern in font_family_patterns:
                if pattern in font_family:
                    matches_pattern = True
                    break
            if not matches_pattern:
                return False
        
        # Check font size range
        font_size_range = mapping.get("font_size_range")
        if font_size_range and font_size:
            try:
                size = float(font_size)
                min_size = font_size_range.get("min")
                max_size = font_size_range.get("max")
                if min_size is not None and size < min_size:
                    return False
                if max_size is not None and size > max_size:
                    return False
            except (ValueError, TypeError):
                pass
        
        # Check coordinate rules
        coord_rules = mapping.get("coordinate_rules")
        if coord_rules:
            # Check x0 range
            x0_range = coord_rules.get("x0_range")
            if x0_range and x0 is not None:
                min_x0 = x0_range.get("min")
                max_x0 = x0_range.get("max")
                if min_x0 is not None and x0 < min_x0:
                    return False
                if max_x0 is not None and x0 > max_x0:
                    return False
            
            # Check y0 range
            y0_range = coord_rules.get("y0_range")
            if y0_range and y0 is not None:
                min_y0 = y0_range.get("min")
                max_y0 = y0_range.get("max")
                if min_y0 is not None and y0 < min_y0:
                    return False
                if max_y0 is not None and y0 > max_y0:
                    return False
        
        return True
    
    def detect_roles_in_html(self, html_elem: ET.Element, report: str = None, annex: str = None) -> Dict[ET.Element, str]:
        """
        Detect roles for all elements in HTML.
        
        Returns:
            Dictionary mapping elements to their detected roles
        """
        role_map = {}
        
        # Find all elements with style attributes
        styled_elems = html_elem.xpath(".//*[@style]")
        
        for elem in styled_elems:
            role = self.detect_role(elem, report, annex)
            if role:
                role_map[elem] = role
        
        return role_map

