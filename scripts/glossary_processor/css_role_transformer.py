"""
Transform glossary/acronym HTML files to use CSS role-based styles.

Replaces font-family styles with CSS classes based on detected roles.
"""
from pathlib import Path
from typing import Dict, Optional
import sys
import lxml.etree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.ami_html import HtmlLib, HtmlUtil, CSSStyle
from amilib.util import Util
from scripts.glossary_processor.font_role_detector import FontRoleDetector

logger = Util.get_logger(__name__)


class CSSRoleTransformer:
    """Transforms HTML to use CSS role-based styles instead of font families."""
    
    # CSS styles for each role
    ROLE_STYLES = {
        "term": {
            "font-weight": "bold",
            "font-style": "normal",
            "color": "#000000"
        },
        "definition": {
            "font-weight": "normal",
            "font-style": "normal",
            "color": "#000000"
        },
        "cross_reference": {
            "font-weight": "normal",
            "font-style": "italic",
            "color": "#0066cc",
            "text-decoration": "underline"
        },
        "section_heading": {
            "font-weight": "bold",
            "font-style": "normal",
            "font-size": "larger",
            "color": "#000000"
        },
        "metadata": {
            "font-weight": "lighter",
            "font-style": "normal",
            "font-size": "smaller",
            "color": "#666666"
        },
        "special_character": {
            "font-weight": "normal",
            "font-style": "normal",
            "color": "#000000"
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize transformer.
        
        Args:
            config_path: Path to font role configuration JSON file
        """
        self.role_detector = FontRoleDetector(config_path)
    
    def transform_html(self, input_html_path: Path, output_html_path: Path, 
                      report: str, annex: str) -> bool:
        """
        Transform HTML file to use CSS role-based styles.
        
        Args:
            input_html_path: Path to input HTML file
            output_html_path: Path to save transformed HTML
            report: Report name (e.g., 'wg3')
            annex: Annex identifier (e.g., 'vi')
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Transforming {input_html_path} -> {output_html_path}")
        
        try:
            # Parse HTML
            html_elem = HtmlLib.parse_html(str(input_html_path))
            if html_elem is None:
                logger.error(f"Failed to parse HTML: {input_html_path}")
                return False
            
            # Detect roles for all styled elements
            logger.info("Detecting roles...")
            role_map = self.role_detector.detect_roles_in_html(html_elem, report, annex)
            logger.info(f"Detected roles for {len(role_map)} elements")
            
            # Apply role classes and styles
            logger.info("Applying role classes...")
            self._apply_role_classes(html_elem, role_map)
            
            # Add CSS stylesheet to head
            logger.info("Adding CSS stylesheet...")
            self._add_role_stylesheet(html_elem)
            
            # Write output
            output_html_path.parent.mkdir(parents=True, exist_ok=True)
            HtmlLib.write_html_file(html_elem, output_html_path, debug=True)
            
            logger.info(f"✅ Successfully transformed HTML")
            logger.info(f"   Output: {output_html_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error transforming {input_html_path}: {e}", exc_info=True)
            return False
    
    def _apply_role_classes(self, html_elem: ET.Element, role_map: Dict[ET.Element, str]):
        """Apply role classes to elements and replace inline styles."""
        for elem, role in role_map.items():
            # Add role class
            existing_class = elem.get("class", "")
            if existing_class:
                elem.set("class", f"{existing_class} role-{role}")
            else:
                elem.set("class", f"role-{role}")
            
            # Replace style attribute with role-based CSS
            # Keep non-font properties (coordinates, etc.)
            style_attr = elem.get("style", "")
            if style_attr:
                # Parse existing style
                css_style = CSSStyle.create_css_style_from_css_string(style_attr)
                if css_style:
                    # Remove font-family, font-weight, font-style
                    css_style.name_value_dict.pop("font-family", None)
                    css_style.name_value_dict.pop("font-weight", None)
                    css_style.name_value_dict.pop("font-style", None)
                    
                    # Keep other properties (coordinates, sizes, etc.)
                    new_style = str(css_style).strip()
                    if new_style:
                        elem.set("style", new_style)
                    else:
                        # Remove style attribute if empty
                        if "style" in elem.attrib:
                            del elem.attrib["style"]
    
    def _add_role_stylesheet(self, html_elem: ET.Element):
        """Add CSS stylesheet for role classes to HTML head."""
        head = HtmlLib.get_head(html_elem)
        if head is None:
            logger.warning("No head element found, creating one")
            head = ET.SubElement(html_elem, "head")
        
        # Create style element
        style_elem = ET.SubElement(head, "style")
        style_elem.set("type", "text/css")
        
        # Build CSS content
        css_content = []
        css_content.append("/* Role-based styles for glossary/acronym entries */\n")
        
        for role, styles in self.ROLE_STYLES.items():
            css_content.append(f".role-{role} {{")
            for prop, value in styles.items():
                css_content.append(f"  {prop}: {value};")
            css_content.append("}\n")
        
        style_elem.text = "\n".join(css_content)


def main():
    """Command-line interface."""
    if len(sys.argv) < 5:
        print("Usage: css_role_transformer.py <input_html> <output_html> <report> <annex>")
        print("Example: css_role_transformer.py input.html output.html wg3 vi")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    report = sys.argv[3]
    annex = sys.argv[4]
    
    transformer = CSSRoleTransformer()
    success = transformer.transform_html(input_path, output_path, report, annex)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

