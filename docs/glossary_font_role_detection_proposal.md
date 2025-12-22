# Glossary Font Role Detection Tool - Proposal

**Date:** December 11, 2025  
**System Date:** Thu Dec 11 09:41:51 GMT 2025

---

## Overview

Create a tool that uses font information to identify semantic roles in glossary/acronym files (terms, definitions, cross-references) instead of hardcoding font names. The tool will leverage amilib's existing font extraction capabilities and use configuration files for font-to-role mapping.

---

## Current Font Patterns in AR6 Files

### WG3 Annex VI (Acronyms)
- `HPFPTY+FrutigerLTPro-BlackCn` (520 occurrences) - **Terms/Acronyms**
- `HPFPTY+FrutigerLTPro-Condensed` (522 occurrences) - **Definitions**
- `HPFPTY+FrutigerLTPro-CondensedIta` (5 occurrences) - **Cross-references (italics)**
- `HPFPTY+FrutigerLTPro-BoldCn` (11 occurrences) - **Section headings**
- `HPFPTY+FrutigerLTPro-LightCn` (2 occurrences) - **Metadata**

### WG1 Annex I (Glossary)
- `EYIDSA+FrutigerLTPro-Condensed` (2974 occurrences) - **Definitions**
- `YKGOMM+FrutigerLTPro-CondensedIta` (2174 occurrences) - **Cross-references (italics)**
- `TBNOEW+FrutigerLTPro-BlackCn` (657 occurrences) - **Terms**
- `GBHPUW+FrutigerLTPro-BoldCn` (35 occurrences) - **Section headings**
- `CVJRQE+FrutigerLTPro-LightCn` (2 occurrences) - **Metadata**

### SYR Annex I (Glossary)
- `TimesNewRomanPSMT` (117 occurrences) - **Definitions**
- `TimesNewRomanPS-BoldMT` (3 occurrences) - **Terms/Headings**

---

## Existing amilib Functionality

### 1. `AmiFont` Class (`amilib/ami_html.py`)

**Purpose:** Extracts font properties (weight, style, stretch) from font names.

**Key Methods:**
- `AmiFont.extract_name_weight_style_stretched_as_font(font_name)` - Extracts font properties
- `AmiFont.trim_pdf_prefix(font_name)` - **Removes PDF prefixes (e.g., "HPFPTY+")** - Already handles prefix truncation
- Properties: `is_bold`, `is_italic`, `weight`, `style`, `stretched`, `family`

**Example:**
```python
from amilib.ami_html import AmiFont

font_name = "HPFPTY+FrutigerLTPro-BlackCn"
ami_font = AmiFont.extract_name_weight_style_stretched_as_font(font_name)
# Returns: weight=BOLD, style=NORMAL, stretched=NARROW, family=FrutigerLTPro
```

### 2. `CSSStyle` Class (`amilib/ami_html.py`)

**Purpose:** Parses and manipulates CSS styles.

**Key Methods:**
- `CSSStyle.create_css_style_from_attribute_of_body_element(elem)` - Creates CSSStyle from element
- `CSSStyle.create_css_style_from_css_string(css_string)` - Parses CSS string
- Properties: `font_family`, `font_size`, `font_weight`, `font_style`, `is_bold`, `is_italic`

**Example:**
```python
from amilib.ami_html import CSSStyle

style_str = "font-family: HPFPTY+FrutigerLTPro-BlackCn; font-size: 9.5;"
css_style = CSSStyle.create_css_style_from_css_string(style_str)
# Access: css_style.font_family, css_style.font_size, css_style.is_bold
```

### 3. Font Normalization

**Method:** `CSSStyle.normalize_styles_in_fonts_in_html_head(html_elem)`

**Purpose:** Normalizes fonts in HTML head, extracting weight and style from font names.

### 4. Coordinate Extraction (`amilib/ami_html.py`)

**Purpose:** Extracts coordinates and analyzes positions for role detection.

**Key Methods:**
- `CSSStyle.get_coords(elem)` - Returns `(x0, y0, x1, y1)` tuple
- `CSSStyle.get_x0(elem)`, `get_y0(elem)`, `get_x1(elem)`, `get_y1(elem)` - Individual coordinate access
- `CSSStyle.extract_coords_and_font_properties(span)` - Extracts both coordinates and font properties
- `HtmlUtil.analyze_coordinates(elem)` - Analyzes coordinate patterns
- `HtmlUtil.get_lrtb(elem, direction)` - Clusters elements by x-coordinate (useful for column detection)

**Note:** Section headings can be identified by x-coordinate position (typically centered or left-aligned at specific x-coordinates).

### 5. Column Detection (`amilib/html_structure.py`)

**Class:** `ColumnDetector`

**Purpose:** Detects column layouts using x-coordinate clustering.

**Key Methods:**
- `ColumnDetector.detect_columns(elements)` - Detects 1, 2, or 3 column layouts
- Uses `CSSStyle.get_x0()` to cluster elements by x-coordinate
- Useful for identifying term/definition columns in acronym files

---

## Proposed Solution

### Architecture

1. **Font Role Mapper** - Maps font properties to semantic roles
2. **Configuration Files** - JSON/YAML files defining font-to-role mappings
3. **Role Detector** - Detects roles in HTML elements using font information
4. **Integration** - Works with existing glossary processor

### Configuration File Format

**File:** `scripts/glossary_processor/font_role_config.json`

```json
{
  "font_role_mappings": [
    {
      "role": "term",
      "description": "Glossary term or acronym",
      "font_properties": {
        "weight": ["bold", "black"],
        "style": ["normal"],
        "stretched": ["narrow", "condensed", "normal"]
      },
      "font_family_patterns": [
        "FrutigerLTPro-BlackCn",
        "FrutigerLTPro-BoldCn",
        "TimesNewRomanPS-BoldMT"
      ],
      "font_size_range": null
    },
    {
      "role": "definition",
      "description": "Definition text",
      "font_properties": {
        "weight": ["normal", "light"],
        "style": ["normal"],
        "stretched": ["condensed", "normal"]
      },
      "font_family_patterns": [
        "FrutigerLTPro-Condensed",
        "TimesNewRomanPSMT"
      ],
      "font_size_range": null
    },
    {
      "role": "cross_reference",
      "description": "Italicized cross-reference to other entries",
      "font_properties": {
        "weight": ["normal", "light"],
        "style": ["italic"],
        "stretched": ["condensed", "normal"]
      },
      "font_family_patterns": [
        "FrutigerLTPro-CondensedIta",
        "FrutigerLTPro-LightCnIta",
        "Calibri-Italic"
      ],
      "font_size_range": null
    },
    {
      "role": "section_heading",
      "description": "Section heading (A, B, C, etc.)",
      "font_properties": {
        "weight": ["bold"],
        "style": ["normal"],
        "stretched": ["normal", "narrow"]
      },
      "font_family_patterns": [
        "FrutigerLTPro-BoldCn"
      ],
      "font_size_range": {
        "min": 10.0,
        "max": 12.0
      },
      "coordinate_rules": {
        "x0_range": {
          "min": 200.0,
          "max": 250.0
        },
        "description": "Section headings typically centered or at specific x-coordinate"
      }
    },
    {
      "role": "metadata",
      "description": "Metadata (citation, editorial info)",
      "font_properties": {
        "weight": ["light", "normal"],
        "style": ["normal"],
        "stretched": ["normal"]
      },
      "font_family_patterns": [
        "FrutigerLTPro-LightCn"
      ],
      "font_size_range": {
        "min": 8.0,
        "max": 9.0
      }
    }
  ],
  "report_specific_overrides": {
    "wg3": {
      "annex-vi-acronyms": {
        "term": {
          "font_family_patterns": ["FrutigerLTPro-BlackCn"]
        }
      }
    },
    "syr": {
      "annex-i-glossary": {
        "term": {
          "font_family_patterns": ["TimesNewRomanPS-BoldMT"]
        },
        "definition": {
          "font_family_patterns": ["TimesNewRomanPSMT"]
        }
      }
    }
  }
}
```

### Implementation

#### Module: `scripts/glossary_processor/font_role_detector.py`

```python
"""
Font-based role detection for glossary/acronym entries.

Uses amilib's AmiFont and CSSStyle classes to extract font properties
and map them to semantic roles using configuration files.
"""
from pathlib import Path
from typing import Optional, Dict, List
import json
import re
import lxml.etree as ET

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
        # Extract font properties from element
        css_style = CSSStyle.create_css_style_from_attribute_of_body_element(elem)
        if css_style is None:
            return None
        
        font_family = css_style.font_family
        if not font_family:
            return None
        
        # Extract font properties using AmiFont
        ami_font = AmiFont.extract_name_weight_style_stretched_as_font(font_family)
        
        # Get report-specific overrides if available
        mappings = self._get_mappings_for_report(report, annex)
        
        # Match against role mappings
        for mapping in mappings:
            if self._matches_mapping(ami_font, css_style, mapping):
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
        
        return mappings
    
    def _matches_mapping(self, ami_font: AmiFont, css_style: CSSStyle, mapping: Dict) -> bool:
        """Check if font properties match a role mapping."""
        # Check font properties
        font_props = mapping.get("font_properties", {})
        
        # Check weight
        if "weight" in font_props:
            weight_str = str(ami_font.weight).lower()
            if weight_str not in [w.lower() for w in font_props["weight"]]:
                return False
        
        # Check style
        if "style" in font_props:
            style_str = str(ami_font.style).lower()
            if style_str not in [s.lower() for s in font_props["style"]]:
                return False
        
        # Check stretched
        if "stretched" in font_props:
            stretched_str = str(ami_font.stretched).lower()
            if stretched_str not in [st.lower() for st in font_props["stretched"]]:
                return False
        
        # Check font family patterns
        font_family_patterns = mapping.get("font_family_patterns", [])
        if font_family_patterns:
            font_family = ami_font.name or css_style.font_family
            matches_pattern = False
            for pattern in font_family_patterns:
                if pattern in font_family:
                    matches_pattern = True
                    break
            if not matches_pattern:
                return False
        
        # Check font size range
        font_size_range = mapping.get("font_size_range")
        if font_size_range and css_style.font_size:
            try:
                size = float(css_style.font_size)
                min_size = font_size_range.get("min")
                max_size = font_size_range.get("max")
                if min_size is not None and size < min_size:
                    return False
                if max_size is not None and size > max_size:
                    return False
            except (ValueError, TypeError):
                pass
        
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
```

---

## Integration with Glossary Processor

### Updated Entry Detector

Modify `scripts/glossary_processor/entry_detector.py` to use font role detection:

```python
from scripts.glossary_processor.font_role_detector import FontRoleDetector

class EntryDetector:
    def __init__(self):
        self.font_role_detector = FontRoleDetector()
    
    def detect_entries(self, html_elem, entry_type, report, annex):
        # Detect roles for all elements
        role_map = self.font_role_detector.detect_roles_in_html(html_elem, report, annex)
        
        # Use roles to identify terms and definitions
        # Terms: elements with role='term'
        # Definitions: elements with role='definition'
        # Cross-references: elements with role='cross_reference'
        
        # ... rest of entry detection logic
```

---

## Benefits

1. **No Hardcoded Font Names** - All font names in configuration files
2. **Report-Specific Overrides** - Different fonts for different reports
3. **Leverages Existing Code** - Uses amilib's `AmiFont` and `CSSStyle`
4. **Configurable** - Easy to add new fonts or adjust mappings
5. **Maintainable** - Changes don't require code modifications

---

## Configuration File Location

**Default:** `scripts/glossary_processor/font_role_config.json`

**Alternative:** Can be specified per-report:
- `scripts/glossary_processor/configs/wg3_font_config.json`
- `scripts/glossary_processor/configs/syr_font_config.json`

---

## Standalone Span Analyzer Tool

### Purpose

Create a standalone tool to analyze spans and their potential roles without processing the full glossary. This tool will:
1. Extract all spans from HTML
2. Analyze font properties (using `AmiFont`)
3. Analyze coordinates (using `CSSStyle.get_coords()`)
4. Generate a report showing font patterns and their potential roles
5. Help identify font-to-role mappings before creating configuration files

### Implementation: `scripts/glossary_processor/analyze_span_roles.py`

```python
"""
Standalone tool to analyze spans and their potential roles.

Analyzes font properties and coordinates to identify patterns
that can be used for role detection.
"""
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import lxml.etree as ET

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
        # Extract CSS style
        css_style = CSSStyle.create_css_style_from_attribute_of_body_element(span)
        if css_style is None:
            return
        
        font_family = css_style.font_family
        if not font_family:
            return
        
        # Extract font properties using AmiFont (truncates prefix automatically)
        ami_font = AmiFont.extract_name_weight_style_stretched_as_font(font_family)
        
        # Get coordinates
        coords = CSSStyle.get_coords(span)
        x0, y0, x1, y1 = coords
        
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
            
            if pattern['font_size_range']['min']:
                print(f"  Font Size: {pattern['font_size_range']['min']:.1f} - {pattern['font_size_range']['max']:.1f}")
            
            if pattern['x0_range']['min'] is not None:
                print(f"  X0 Range: {pattern['x0_range']['min']:.1f} - {pattern['x0_range']['max']:.1f}")
            
            print(f"  Sample texts:")
            for text in pattern['sample_texts']:
                print(f"    - {text}")


def main():
    """Command-line interface."""
    import sys
    
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
```

### Usage

```bash
# Analyze a glossary file
python scripts/glossary_processor/analyze_span_roles.py \
    test/resources/ipcc/cleaned_content/wg3/annex-vi-acronyms/annex-vi-acronyms.html

# Output shows:
# - Font patterns with counts
# - Font properties (weight, style, stretch)
# - Coordinate ranges (x0, y0)
# - Font size ranges
# - Sample texts for each pattern
```

## Next Steps

1. **Create Standalone Span Analyzer** - Implement `analyze_span_roles.py` tool
2. **Run Analysis** - Analyze all glossary/acronym files to identify font patterns
3. **Create Configuration File** - Define font-to-role mappings based on analysis
4. **Implement FontRoleDetector** - Create the detector module with coordinate support
5. **Update Entry Detector** - Integrate font role detection
6. **Test on Sample Files** - Validate on WG3 Annex VI, WG1 Annex I, SYR Annex I
7. **Refine Mappings** - Adjust based on test results

---

## Example Usage

```python
from scripts.glossary_processor.font_role_detector import FontRoleDetector
from amilib.ami_html import HtmlLib

# Initialize detector
detector = FontRoleDetector()

# Load HTML
html_elem = HtmlLib.parse_html("wg3/annex-vi-acronyms/annex-vi-acronyms.html")

# Detect roles
role_map = detector.detect_roles_in_html(html_elem, report="wg3", annex="vi")

# Use roles
for elem, role in role_map.items():
    if role == "term":
        # Process as term
        pass
    elif role == "definition":
        # Process as definition
        pass
    elif role == "cross_reference":
        # Process as cross-reference
        pass
```

---

**Status:** Proposal - Ready for Implementation

