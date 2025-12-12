"""
Transform glossary/acronym HTML to semantic structure with role-based divs.

Creates:
- <div role="term">...</div>
- <div role="definition">...</div>

Or uses <dl><dt>...</dt><dd>...</dd></dl> structure.

Merges text/element/text sequences into single spans preserving mixed content.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import lxml.etree as ET
from lxml.etree import _ElementUnicodeResult

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amilib.ami_html import HtmlLib, HtmlUtil, CSSStyle, AmiFont
from amilib.util import Util
from scripts.glossary_processor.font_role_detector import FontRoleDetector
from scripts.glossary_processor.entry_detector import EntryDetector
from scripts.glossary_processor.page_joiner import PageJoiner
from scripts.glossary_processor.acronym_parser import AcronymParser

logger = Util.get_logger(__name__)


class SemanticStructureTransformer:
    """Transforms HTML to semantic structure with role-based divs."""
    
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
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None, use_dl: bool = False):
        """
        Initialize transformer.
        
        Args:
            config_path: Path to font role configuration JSON file
            use_dl: If True, use <dl><dt><dd> structure, else use <div role="...">
        """
        self.role_detector = FontRoleDetector(config_path)
        self.use_dl = use_dl
    
    def transform_html(self, input_html_path: Path, output_html_path: Path,
                       report: str, annex: str, entry_type: str = 'acronym') -> bool:
        """
        Transform HTML file to semantic structure.
        
        Args:
            input_html_path: Path to input HTML file (raw HTML with font styles)
            output_html_path: Path to save transformed HTML
            report: Report name (e.g., 'wg3')
            annex: Annex identifier (e.g., 'vi')
            entry_type: 'acronym' or 'glossary'
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Transforming {input_html_path} -> {output_html_path}")
        
        try:
            # Parse HTML
            html_tree = HtmlUtil.parse_html_lxml(str(input_html_path))
            html_elem = html_tree.getroot()
            
            # Stage 1: Join pages
            logger.info("Joining pages...")
            html_elem = PageJoiner.join_pages(html_elem)
            
            # Stage 2: Detect entries using EntryDetector
            logger.info("Detecting entries...")
            entries = EntryDetector.detect_entries(html_elem, entry_type)
            logger.info(f"Detected {len(entries)} entries")
            
            if not entries:
                logger.warning("No entries detected!")
                return False
            
            # Stage 3: Detect roles for all spans
            logger.info("Detecting roles for spans...")
            role_map = self.role_detector.detect_roles_in_html(html_elem, report, annex)
            logger.info(f"Detected roles for {len(role_map)} elements")
            
            # Stage 4: Create semantic structure
            logger.info("Creating semantic structure...")
            semantic_html = self._create_semantic_structure(html_elem, entries, role_map, report, annex)
            
            # Stage 4.5: Parse acronyms/abbreviations if entry type is acronyms
            if entry_type == 'acronyms':
                logger.info("Parsing acronyms to extract full terms...")
                modified_count = AcronymParser.parse_dictionary(semantic_html, entry_type)
                logger.info(f"Modified {modified_count} acronym entries")
            
            # Stage 5: Add CSS stylesheet
            logger.info("Adding CSS stylesheet...")
            self._add_role_stylesheet(semantic_html)
            
            # Write output
            output_html_path.parent.mkdir(parents=True, exist_ok=True)
            HtmlLib.write_html_file(semantic_html, output_html_path, debug=True)
            
            logger.info(f"✅ Successfully transformed HTML")
            logger.info(f"   Output: {output_html_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error transforming {input_html_path}: {e}", exc_info=True)
            return False
    
    def _create_semantic_structure(self, html_elem: ET.Element, entries: List[Dict],
                                  role_map: Dict[ET.Element, str], report: str, annex: str) -> ET.Element:
        """Create semantic HTML structure from detected entries."""
        # Create new HTML structure
        new_html = ET.Element("html")
        head = ET.SubElement(new_html, "head")
        body = ET.SubElement(new_html, "body")
        
        # Create glossary container
        glossary_div = ET.SubElement(body, "div")
        glossary_div.set("class", "glossary")
        glossary_div.set("data-report", report)
        glossary_div.set("data-annex", annex)
        
        # Add title
        title = ET.SubElement(glossary_div, "h1")
        title.text = f"Annex {annex.upper()}: {'Glossary' if 'glossary' in annex.lower() else 'Acronyms'}"
        
        # Process each entry
        for i, entry in enumerate(entries):
            # Get all spans from entry divs
            entry_spans = []
            for div in entry.get('divs', []):
                spans = div.xpath('.//span[@style]')
                entry_spans.extend(spans)
            
            # Separate spans by role
            term_spans = [s for s in entry_spans if role_map.get(s) == 'term']
            def_spans = [s for s in entry_spans if role_map.get(s) == 'definition']
            cross_ref_spans = [s for s in entry_spans if role_map.get(s) == 'cross_reference']
            
            # Add cross-references to definition
            def_spans.extend(cross_ref_spans)
            
            if self.use_dl:
                # Use <dl> structure
                if i == 0 or (i > 0 and entries[i-1].get('dl_elem') is None):
                    dl_elem = ET.SubElement(glossary_div, "dl")
                    entry['dl_elem'] = dl_elem
                else:
                    dl_elem = entries[i-1].get('dl_elem')
                
                # Term as <dt>
                if term_spans:
                    dt_elem = ET.SubElement(dl_elem, "dt")
                    dt_elem.set("role", "term")
                    self._merge_elements_into_container(dt_elem, term_spans, role_map)
                
                # Definition as <dd>
                if def_spans:
                    dd_elem = ET.SubElement(dl_elem, "dd")
                    dd_elem.set("role", "definition")
                    self._merge_elements_into_container(dd_elem, def_spans, role_map)
            else:
                # Use <div role="..."> structure
                entry_div = ET.SubElement(glossary_div, "div")
                entry_div.set("class", "entry")
                entry_div.set("id", f"{report}-{annex}-entry-{i}")
                
                # Term div
                if term_spans:
                    term_div = ET.SubElement(entry_div, "div")
                    term_div.set("role", "term")
                    self._merge_elements_into_container(term_div, term_spans, role_map)
                
                # Definition div
                if def_spans:
                    def_div = ET.SubElement(entry_div, "div")
                    def_div.set("role", "definition")
                    self._merge_elements_into_container(def_div, def_spans, role_map)
        
        return new_html
    
    def _merge_elements_into_container(self, container: ET.Element, elements: List[ET.Element], role_map: Dict[ET.Element, str]):
        """
        Merge elements into container, preserving mixed content.
        
        Handles text/element/text sequences by merging into single spans where appropriate.
        Preserves nested HTML elements (a, sub, sup, em, strong, etc.).
        
        Args:
            container: Container element to add merged spans to
            elements: List of span elements to merge
            role_map: Dictionary mapping elements to their roles
        """
        if not elements:
            return
        
        # Group elements by role
        current_group = []
        current_role = None
        
        for elem in elements:
            role = role_map.get(elem)
            
            # Check if we should merge with previous group
            if current_role == role and current_group:
                current_group.append(elem)
            else:
                # Process previous group
                if current_group:
                    self._create_merged_span_group(container, current_group, current_role)
                # Start new group
                current_group = [elem]
                current_role = role
        
        # Process last group
        if current_group:
            self._create_merged_span_group(container, current_group, current_role)
    
    def _create_merged_span_group(self, container: ET.Element, elements: List[ET.Element], role: Optional[str]):
        """
        Create a merged span from a group of elements with the same role.
        
        Preserves nested HTML elements (a, sub, sup, em, strong, etc.) and merges text content.
        """
        if not elements:
            return
        
        # Create new span
        merged_span = ET.SubElement(container, "span")
        
        if role:
            merged_span.set("class", f"role-{role}")
        
        # Collect all text content and nested elements
        text_parts = []
        nested_elems = []
        
        for elem in elements:
            # Get direct text content
            if elem.text:
                text_parts.append(elem.text.strip())
            
            # Collect nested elements (a, sub, sup, em, strong, etc.)
            for child in elem:
                nested_elems.append(self._deep_copy_element(child))
            
            # Handle tail text (text after element)
            if elem.tail:
                text_parts.append(elem.tail.strip())
        
        # Set merged text
        if text_parts:
            merged_span.text = " ".join(t for t in text_parts if t)
        
        # Add nested elements
        for nested in nested_elems:
            merged_span.append(nested)
    
    def _deep_copy_element(self, elem: ET.Element) -> ET.Element:
        """Deep copy an element preserving all children and attributes."""
        # Create new element with same tag
        new_elem = ET.Element(elem.tag)
        
        # Copy attributes
        for attr, value in elem.attrib.items():
            new_elem.set(attr, value)
        
        # Copy text content
        if elem.text:
            new_elem.text = elem.text
        
        # Copy children recursively
        for child in elem:
            child_copy = self._deep_copy_element(child)
            new_elem.append(child_copy)
            # Copy tail text
            if child.tail:
                child_copy.tail = child.tail
        
        # Copy tail
        if elem.tail:
            new_elem.tail = elem.tail
        
        return new_elem
    
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
        
        # Styles for role attributes (divs)
        css_content.append("[role=\"term\"] {")
        css_content.append("  font-weight: bold;")
        css_content.append("  font-style: normal;")
        css_content.append("  color: #000000;")
        css_content.append("}\n")
        
        css_content.append("[role=\"definition\"] {")
        css_content.append("  font-weight: normal;")
        css_content.append("  font-style: normal;")
        css_content.append("  color: #000000;")
        css_content.append("}\n")
        
        # Styles for role classes (for spans)
        for role, styles in self.ROLE_STYLES.items():
            css_content.append(f".role-{role} {{")
            for prop, value in styles.items():
                css_content.append(f"  {prop}: {value};")
            css_content.append("}\n")
        
        # Styles for dl/dt/dd if used
        css_content.append("dt[role=\"term\"] {")
        css_content.append("  font-weight: bold;")
        css_content.append("}\n")
        
        css_content.append("dd[role=\"definition\"] {")
        css_content.append("  margin-left: 2em;")
        css_content.append("}\n")
        
        style_elem.text = "\n".join(css_content)


def main():
    """Command-line interface."""
    if len(sys.argv) < 5:
        print("Usage: semantic_structure_transformer.py <input_html> <output_html> <report> <annex> [--use-dl]")
        print("Example: semantic_structure_transformer.py input.html output.html wg3 vi")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    report = sys.argv[3]
    annex = sys.argv[4]
    use_dl = "--use-dl" in sys.argv
    
    transformer = SemanticStructureTransformer(use_dl=use_dl)
    success = transformer.transform_html(input_path, output_path, report, annex)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

