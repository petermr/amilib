# HTML Structure Templating Strategy for PDF-Converted Documents

**Date:** 2025-12-08  
**Purpose:** Design a reusable templating system for structuring line-by-line HTML from PDF conversions

---

## Executive Summary

This document proposes a strategy for creating structured, nested HTML from PDF-converted line-by-line HTML using a template-driven approach. The system will detect document structure at both page and document levels, handle multi-column layouts, floating elements, and indentation through heuristics rather than machine learning.

---

## Current State Analysis

### Existing Capabilities in `amilib`

#### ✅ **HTML Grouping & Hierarchical Structure**
- **`HtmlGroup`** (`ami_html.py:578`): Groups siblings into hierarchical divs
  - `group_divs_into_tree()`: Creates tree structure from flat divs
  - `make_hierarchical_sections_KEY()`: Creates sections using regex patterns
  - `group_siblings_between_fenceposts()`: Groups elements between markers

#### ✅ **Coordinate & Geometric Operations**
- **`BBox`** (`bbox.py`): Bounding box operations with coordinate tracking
  - Intersection, union, containment checks
  - Coordinate range management
- **`HtmlUtil.analyze_coordinates()`**: Analyzes left/right/top positions
  - `get_lrtb()`: Detects common x-coordinates (potential columns)

#### ✅ **Floating Element Detection**
- **`FloatExtractor`** (`ami_html.py:5479`): Extracts floats using regex patterns
- **`FloatBoundary`** (`ami_html.py:5435`): Handles START/END markers for boxes/figures/tables
- Supports IPCC-style markers: `[START BOX.1 HERE]` / `[END BOX.1 HERE]`

#### ✅ **PDF Conversion with Coordinates**
- **`AmiPDFPlumber`** (`ami_pdf_libs.py`): Preserves coordinate information
  - Text elements have `x0`, `x1`, `y0`, `y1` attributes
  - Font size, weight, style information preserved
  - Table detection via `pdfplumber.find_tables()`

#### ✅ **Section Detection**
- **`HtmlTree`** (`ami_html.py:4977`): Builds trees from flat elements
  - `get_div_spans_with_decimals()`: Detects numbered sections (1.2, 1.2.3)
  - Uses font size, weight, and regex patterns

### Gaps Identified

1. **No unified column detection** - Coordinate analysis exists but not integrated
2. **No template system** - Structure detection is hardcoded
3. **Limited indentation detection** - No systematic left-margin analysis
4. **No page-level structure detection** - Document-level only
5. **No reusable configuration** - Patterns embedded in code

---

## Proposed Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│              Template Configuration (JSON/YAML)         │
│  - Column detection rules                                │
│  - Section detection patterns                            │
│  - Floating element markers                             │
│  - Indentation thresholds                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         HtmlStructureFormatter (Generic Engine)          │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Phase 1: Page-Level Analysis                   │   │
│  │  - Column detection (1/2/3 columns)              │   │
│  │  - Floating element detection                    │   │
│  │  - Table/image detection                         │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Phase 2: Document-Level Analysis                │   │
│  │  - Section hierarchy detection                    │   │
│  │  - Indentation-based grouping                    │   │
│  │  - Cross-page structure                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Phase 3: Structure Application                  │   │
│  │  - Apply nested containers                       │   │
│  │  - Group floating elements                       │   │
│  │  - Create semantic HTML structure                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Template System Design

### Template Format (JSON)

```json
{
  "document_type": "ipcc_annex",
  "version": "1.0",
  
  "column_detection": {
    "enabled": true,
    "method": "coordinate_clustering",
    "tolerance_px": 20,
    "min_elements_per_column": 5,
    "column_count": {
      "auto_detect": true,
      "max_columns": 3,
      "preferred": [1, 2, 3]
    }
  },
  
  "section_detection": {
    "hierarchical": true,
    "patterns": [
      {
        "level": 1,
        "regex": "^\\s*(?P<id>\\d+)\\s+(?P<title>.*)$",
        "font_size_range": [12, 16],
        "font_weight": "bold",
        "class": "section_title"
      },
      {
        "level": 2,
        "regex": "^\\s*(?P<id>\\d+\\.\\d+)\\s+(?P<title>.*)$",
        "font_size_range": [11, 14],
        "font_weight": "bold",
        "class": "subsection_title"
      }
    ],
    "indentation_based": {
      "enabled": true,
      "thresholds": [0, 20, 40, 60],
      "min_indent_difference": 15
    }
  },
  
  "floating_elements": {
    "enabled": true,
    "markers": {
      "start_pattern": "\\[START\\s+(?P<type>BOX|FIGURE|TABLE)\\s+(?P<id>.*?)\\s+HERE\\]",
      "end_pattern": "\\[END\\s+(?P<type>BOX|FIGURE|TABLE)\\s+(?P<id>.*?)\\s+HERE\\]"
    },
    "bbox_detection": {
      "enabled": true,
      "min_width": 100,
      "min_height": 50,
      "isolation_threshold": 30
    }
  },
  
  "tables": {
    "detection": "pdfplumber",
    "wrap_in_figure": true,
    "caption_pattern": "^Table\\s+(?P<id>\\d+[.\\d]*)\\s*[:.]\\s*(?P<title>.*)$"
  },
  
  "images": {
    "detection": "coordinate",
    "wrap_in_figure": true,
    "caption_pattern": "^Figure\\s+(?P<id>\\d+[.\\d]*)\\s*[:.]\\s*(?P<title>.*)$",
    "min_width": 50,
    "min_height": 50
  },
  
  "indentation": {
    "enabled": true,
    "detection_method": "left_margin",
    "thresholds": {
      "level_0": [0, 10],
      "level_1": [15, 35],
      "level_2": [40, 60],
      "level_3": [65, 85]
    },
    "apply_to": ["paragraphs", "lists"]
  },
  
  "page_metadata": {
    "enabled": true,
    "page_numbers": {
      "detection": "coordinate_and_pattern",
      "patterns": [
        "^Page\\s+(?P<number>\\d+)$",
        "^(?P<number>\\d+)$"
      ],
      "regions": {
        "header": {"y_range": [0, 80], "x_ranges": [[0, 200], [400, 600]]},
        "footer": {"y_range": [800, 900], "x_ranges": [[0, 200], [400, 600]]}
      },
      "font_size_range": [8, 12],
      "extract": true,
      "store_as_attribute": "data-page-number"
    },
    "running_titles": {
      "detection": "coordinate_and_pattern",
      "regions": {
        "header": {"y_range": [0, 80]},
        "footer": {"y_range": [800, 900]}
      },
      "patterns": [
        "^.*Chapter\\s+\\d+.*$",
        "^.*Annex\\s+[IVX]+.*$"
      ],
      "font_size_range": [9, 12],
      "extract": true,
      "store_as_attribute": "data-running-title"
    },
    "marginalia": {
      "enabled": true,
      "detection": "coordinate",
      "regions": {
        "left_margin": {"x_range": [0, 50]},
        "right_margin": {"x_range": [550, 600]}
      },
      "extract": true,
      "store_as_attribute": "data-marginalia"
    },
    "recto_verso": {
      "enabled": true,
      "detection": "page_number_position",
      "recto": {
        "page_number_x_range": [500, 600],
        "running_title_x_range": [0, 200]
      },
      "verso": {
        "page_number_x_range": [0, 100],
        "running_title_x_range": [400, 600]
      },
      "store_as_attribute": "data-page-side"
    }
  },
  
  "output_structure": {
    "container_class": "section",
    "nested_containers": true,
    "semantic_tags": {
      "sections": "section",
      "floats": "aside",
      "tables": "figure",
      "images": "figure",
      "pages": "article",
      "page_metadata": "header"
    }
  }
}
```

---

## Detection Algorithms (Heuristics)

### A. Page-Level Structure Detection

#### 1. Column Detection

**Algorithm: Coordinate Clustering**

```python
def detect_columns(elements, tolerance=20):
    """
    Detect 1-, 2-, or 3-column layouts by clustering x-coordinates.
    
    Steps:
    1. Extract all left (x0) coordinates from elements
    2. Cluster coordinates within tolerance
    3. Count clusters - determines column count
    4. Assign elements to columns based on x0 position
    5. Sort elements within columns by y-coordinate
    """
    x_coords = [get_x0(elem) for elem in elements]
    clusters = cluster_coordinates(x_coords, tolerance)
    
    if len(clusters) == 1:
        return "single_column", assign_to_column(elements, clusters[0])
    elif len(clusters) == 2:
        return "two_column", assign_to_columns(elements, clusters)
    elif len(clusters) == 3:
        return "three_column", assign_to_columns(elements, clusters)
    else:
        # Fallback: use most common clusters
        return detect_dominant_columns(clusters, elements)
```

**Open Source Libraries:**
- **`scikit-learn`** (already used): `DBSCAN` or `KMeans` for clustering
- **`numpy`**: Statistical analysis of coordinate distributions

#### 2. Floating Element Detection

**Algorithm: BBox Isolation + Marker Detection**

```python
def detect_floating_elements(elements, page_bbox):
    """
    Detect floating boxes, figures, tables.
    
    Steps:
    1. Find elements with START/END markers (regex)
    2. Find isolated bboxes (large gaps around element)
    3. Check if element spans multiple columns
    4. Check if element has caption pattern
    """
    floats = []
    
    # Method 1: Marker-based (IPCC style)
    marker_floats = extract_by_markers(elements, start_pattern, end_pattern)
    
    # Method 2: BBox isolation
    isolated = find_isolated_bboxes(elements, page_bbox, threshold=30)
    
    # Method 3: Caption detection
    captioned = find_captioned_elements(elements, caption_patterns)
    
    return combine_floats(marker_floats, isolated, captioned)
```

**Open Source Libraries:**
- **`shapely`**: Geometric operations (intersection, union, isolation)
- **`BBox`** (existing): Already provides bbox operations

#### 3. Table Detection

**Algorithm: Use pdfplumber + Coordinate Analysis**

```python
def detect_tables(page_elements, pdfplumber_page):
    """
    Detect tables using pdfplumber and coordinate analysis.
    
    Steps:
    1. Use pdfplumber.find_tables() for explicit tables
    2. Find table-like structures (grid of elements)
    3. Check for table captions
    4. Wrap in <figure> with <figcaption>
    """
    tables = []
    
    # Method 1: pdfplumber (already available)
    plumber_tables = pdfplumber_page.find_tables()
    
    # Method 2: Grid detection (for implicit tables)
    grid_tables = detect_grid_structure(page_elements)
    
    return combine_tables(plumber_tables, grid_tables)
```

**Open Source Libraries:**
- **`pdfplumber`** (already used): Table detection
- **`pandas`** (already used): Table structure analysis

#### 4. Page Metadata Detection

**Algorithm: Coordinate-Based Detection + Pattern Matching**

```python
def detect_page_metadata(elements, page_bbox, template):
    """
    Detect page numbers, running titles, marginalia, and recto/verso.
    
    Steps:
    1. Identify header/footer regions using y-coordinates
    2. Extract page numbers using patterns and coordinate regions
    3. Extract running titles from header regions
    4. Detect marginalia in left/right margins
    5. Determine recto/verso based on page number position
    6. Store metadata as data attributes
    """
    metadata = {
        "page_number": None,
        "running_title": None,
        "marginalia": [],
        "page_side": None  # "recto" or "verso"
    }
    
    # Page number detection
    if template.page_metadata.page_numbers.enabled:
        page_num = detect_page_number(elements, template.page_metadata.page_numbers)
        metadata["page_number"] = page_num
    
    # Running title detection
    if template.page_metadata.running_titles.enabled:
        running_title = detect_running_title(elements, template.page_metadata.running_titles)
        metadata["running_title"] = running_title
    
    # Marginalia detection
    if template.page_metadata.marginalia.enabled:
        marginalia = detect_marginalia(elements, template.page_metadata.marginalia)
        metadata["marginalia"] = marginalia
    
    # Recto/verso detection
    if template.page_metadata.recto_verso.enabled:
        page_side = detect_recto_verso(elements, metadata, template.page_metadata.recto_verso)
        metadata["page_side"] = page_side
    
    return metadata

def detect_page_number(elements, config):
    """
    Detect page number from header/footer regions.
    
    Steps:
    1. Filter elements in header/footer y-ranges
    2. Filter by x-ranges (left/right/center)
    3. Match against page number patterns
    4. Extract number from match
    5. Verify font size is in expected range
    """
    candidates = []
    
    for elem in elements:
        y0 = get_y0(elem)
        x0 = get_x0(elem)
        text = get_text(elem)
        
        # Check if in header/footer region
        in_header = config.regions.header.y_range[0] <= y0 <= config.regions.header.y_range[1]
        in_footer = config.regions.footer.y_range[0] <= y0 <= config.regions.footer.y_range[1]
        
        if in_header or in_footer:
            # Check x-position matches expected regions
            for x_range in config.regions.header.x_ranges + config.regions.footer.x_ranges:
                if x_range[0] <= x0 <= x_range[1]:
                    # Match against patterns
                    for pattern in config.patterns:
                        match = re.match(pattern, text)
                        if match:
                            page_num = match.group("number")
                            candidates.append((elem, int(page_num), y0))
                            break
    
    # Return most likely candidate (usually highest/lowest y)
    if candidates:
        # Sort by y-position (header = low y, footer = high y)
        candidates.sort(key=lambda x: x[2])
        return candidates[0][1]  # Return page number
    
    return None

def detect_running_title(elements, config):
    """
    Detect running title from header region.
    
    Steps:
    1. Filter elements in header y-range
    2. Match against running title patterns
    3. Extract title text
    4. Verify font size
    """
    candidates = []
    
    for elem in elements:
        y0 = get_y0(elem)
        text = get_text(elem).strip()
        
        if config.regions.header.y_range[0] <= y0 <= config.regions.header.y_range[1]:
            for pattern in config.patterns:
                match = re.match(pattern, text)
                if match:
                    candidates.append((elem, text, y0))
                    break
    
    if candidates:
        # Return most common or first candidate
        candidates.sort(key=lambda x: x[2])
        return candidates[0][1]
    
    return None

def detect_marginalia(elements, config):
    """
    Detect marginalia in left/right margins.
    
    Steps:
    1. Filter elements in margin x-ranges
    2. Extract text content
    3. Store as marginalia
    """
    marginalia = []
    
    for elem in elements:
        x0 = get_x0(elem)
        text = get_text(elem).strip()
        
        # Check left margin
        if (config.regions.left_margin.x_range[0] <= x0 <= 
            config.regions.left_margin.x_range[1]):
            marginalia.append({"side": "left", "text": text, "element": elem})
        
        # Check right margin
        elif (config.regions.right_margin.x_range[0] <= x0 <= 
              config.regions.right_margin.x_range[1]):
            marginalia.append({"side": "right", "text": text, "element": elem})
    
    return marginalia

def detect_recto_verso(elements, metadata, config):
    """
    Determine if page is recto (right) or verso (left).
    
    Steps:
    1. Use page number position if available
    2. Use running title position as fallback
    3. Default to recto if uncertain
    """
    if metadata.get("page_number"):
        # Check page number x-position
        page_num_elem = find_page_number_element(elements, metadata["page_number"])
        if page_num_elem:
            x0 = get_x0(page_num_elem)
            
            if config.recto.page_number_x_range[0] <= x0 <= config.recto.page_number_x_range[1]:
                return "recto"
            elif config.verso.page_number_x_range[0] <= x0 <= config.verso.page_number_x_range[1]:
                return "verso"
    
    # Fallback: use running title position
    if metadata.get("running_title"):
        running_title_elem = find_running_title_element(elements, metadata["running_title"])
        if running_title_elem:
            x0 = get_x0(running_title_elem)
            
            if config.recto.running_title_x_range[0] <= x0 <= config.recto.running_title_x_range[1]:
                return "recto"
            elif config.verso.running_title_x_range[0] <= x0 <= config.verso.running_title_x_range[1]:
                return "verso"
    
    # Default to recto (right page)
    return "recto"
```

**Open Source Libraries:**
- **`lxml`** (already used): Element manipulation and XPath
- **`regex`**: Pattern matching for page numbers and titles

### B. Document-Level Structure Detection

#### 1. Section Hierarchy Detection

**Algorithm: Multi-Pass Pattern Matching**

```python
def detect_section_hierarchy(elements, template):
    """
    Detect hierarchical sections using patterns and heuristics.
    
    Steps:
    1. Apply regex patterns from template (level 1, 2, 3...)
    2. Check font properties (size, weight)
    3. Check indentation levels
    4. Build parent-child relationships
    5. Group content under sections
    """
    sections = []
    
    for level, pattern in enumerate(template.section_patterns):
        matches = find_matching_elements(elements, pattern)
        for match in matches:
            section = create_section(match, level)
            sections.append(section)
    
    # Build hierarchy
    hierarchy = build_parent_child_tree(sections)
    
    # Assign content to sections
    assign_content_to_sections(elements, hierarchy)
    
    return hierarchy
```

**Open Source Libraries:**
- **`lxml`** (already used): XPath and element manipulation
- **`regex`**: Advanced pattern matching

#### 2. Indentation-Based Grouping

**Algorithm: Left Margin Analysis**

```python
def detect_indentation_structure(elements, thresholds):
    """
    Group elements by indentation level.
    
    Steps:
    1. Extract left margin (x0) for each element
    2. Cluster margins into levels using thresholds
    3. Create nested structure based on indent levels
    4. Handle list items (bullets, numbers)
    """
    indent_levels = []
    
    for elem in elements:
        x0 = get_x0(elem)
        level = assign_indent_level(x0, thresholds)
        indent_levels.append((elem, level))
    
    # Build nested structure
    structure = build_nested_from_indents(indent_levels)
    
    return structure
```

**Open Source Libraries:**
- **`numpy`**: Statistical analysis of margins
- **`scipy.cluster`**: Clustering indent levels

### C. Iterative Refinement

**Algorithm: Multi-Pass Processing**

```python
def iterative_structure_detection(html_elem, template, max_iterations=3):
    """
    Iteratively refine structure detection.
    
    Steps:
    1. Initial pass: Detect obvious structures (markers, explicit patterns)
    2. Second pass: Use detected structures to refine (e.g., column boundaries)
    3. Third pass: Apply indentation and fine-tune
    4. Validation: Check consistency across pages
    """
    structure = {}
    
    for iteration in range(max_iterations):
        # Page-level detection
        page_structure = detect_page_structure(html_elem, template)
        
        # Document-level detection
        doc_structure = detect_document_structure(html_elem, template, page_structure)
        
        # Refine based on previous iteration
        if iteration > 0:
            structure = refine_structure(structure, page_structure, doc_structure)
        else:
            structure = combine_structures(page_structure, doc_structure)
    
    return structure
```

---

## Implementation Plan

### Phase 1: Core Infrastructure

1. **Create Template System**
   - Template parser (JSON/YAML)
   - Template validation
   - Default templates for common document types

2. **Create `HtmlStructureFormatter` Class**
   - Main orchestrator class
   - Template loading and application
   - Phase-based processing

### Phase 2: Page-Level Detection

1. **Column Detection Module**
   - Coordinate clustering implementation
   - Integration with existing `HtmlUtil.analyze_coordinates()`
   - Column assignment logic

2. **Floating Element Detection**
   - Enhance `FloatExtractor` with bbox analysis
   - Add isolation detection
   - Caption pattern matching

3. **Table/Image Detection**
   - Integrate pdfplumber table detection
   - Image detection via coordinates
   - Caption extraction

### Phase 3: Document-Level Detection

1. **Section Hierarchy**
   - Enhance `HtmlGroup.make_hierarchical_sections_KEY()`
   - Multi-level pattern matching
   - Cross-page section tracking

2. **Indentation Detection**
   - Left margin analysis
   - Threshold-based level assignment
   - Nested structure creation

### Phase 4: Structure Application

1. **HTML Generation**
   - Apply detected structure to HTML
   - Create semantic containers
   - Preserve original content

2. **Validation & Refinement**
   - Structure consistency checking
   - Iterative refinement
   - Error reporting

---

## Recommended Open Source Libraries

### Already in Use ✅
- **`lxml`**: HTML/XML processing
- **`pdfplumber`**: PDF parsing and table detection
- **`numpy`**: Numerical operations
- **`scikit-learn`**: Clustering (DBSCAN, KMeans)
- **`pandas`**: Data manipulation

### Additional Recommendations

1. **`shapely`** (Geometric Operations)
   - **Purpose**: BBox intersection, union, isolation detection
   - **Use Case**: Floating element detection, column boundary analysis
   - **License**: BSD-3-Clause
   - **Install**: `pip install shapely`

2. **`pyyaml`** (Template Parsing)
   - **Purpose**: YAML template parsing (alternative to JSON)
   - **Use Case**: More readable template format
   - **License**: MIT
   - **Install**: `pip install pyyaml`

3. **`jsonschema`** (Template Validation)
   - **Purpose**: Validate template structure
   - **Use Case**: Ensure templates are correct before processing
   - **License**: MIT
   - **Install**: `pip install jsonschema`

4. **`scipy`** (Advanced Clustering)
   - **Purpose**: Hierarchical clustering for indent levels
   - **Use Case**: Indentation-based structure detection
   - **License**: BSD-3-Clause
   - **Install**: `pip install scipy`

5. **`regex`** (Advanced Pattern Matching)
   - **Purpose**: Better regex support than `re`
   - **Use Case**: Complex section detection patterns
   - **License**: Apache 2.0
   - **Install**: `pip install regex`

---

## Example Template: IPCC Annex

```json
{
  "document_type": "ipcc_annex",
  "version": "1.0",
  
  "column_detection": {
    "enabled": true,
    "tolerance_px": 25,
    "min_elements_per_column": 3
  },
  
  "section_detection": {
    "patterns": [
      {
        "level": 1,
        "regex": "^\\s*(?P<id>[A-Z]\\d+)\\s+(?P<title>.*)$",
        "font_size_range": [12, 16],
        "font_weight": "bold"
      }
    ],
    "indentation_based": {
      "enabled": true,
      "thresholds": [0, 25, 50]
    }
  },
  
  "floating_elements": {
    "markers": {
      "start_pattern": "\\[START\\s+(?P<type>BOX|FIGURE|TABLE)\\s+(?P<id>.*?)\\s+HERE\\]",
      "end_pattern": "\\[END\\s+(?P<type>BOX|FIGURE|TABLE)\\s+(?P<id>.*?)\\s+HERE\\]"
    }
  },
  
  "output_structure": {
    "container_class": "section",
    "semantic_tags": {
      "sections": "section",
      "floats": "aside"
    }
  }
}
```

---

## Integration with Existing Code

### Leverage Existing Classes

1. **`HtmlGroup`**: Extend for template-driven grouping
2. **`FloatExtractor`**: Enhance with template patterns
3. **`HtmlTree`**: Use for hierarchical structure building
4. **`BBox`**: Use for all geometric operations
5. **`HtmlUtil.analyze_coordinates()`**: Extend for column detection

### New Classes to Create

1. **`HtmlStructureFormatter`**: Main orchestrator
2. **`ColumnDetector`**: Column detection logic
3. **`IndentationAnalyzer`**: Indentation-based grouping
4. **`TemplateLoader`**: Template parsing and validation
5. **`StructureValidator`**: Consistency checking

---

## Testing Strategy

1. **Unit Tests**: Each detection algorithm
2. **Integration Tests**: End-to-end structure detection
3. **Template Tests**: Template validation and application
4. **Regression Tests**: Ensure existing functionality preserved

---

## Next Steps

1. **Review & Approve Strategy**: Get feedback on approach
2. **Create Proof of Concept**: Implement column detection first
3. **Develop Template Format**: Finalize JSON schema
4. **Implement Core Classes**: Start with `HtmlStructureFormatter`
5. **Iterate**: Test on real IPCC annex files

---

## References

- Existing code: `amilib/ami_html.py`, `amilib/ami_pdf_libs.py`
- PDF processing: `amilib/ami_pdf_libs.py:AmiPDFPlumber`
- HTML grouping: `amilib/ami_html.py:HtmlGroup`
- Float extraction: `amilib/ami_html.py:FloatExtractor`
- Coordinate analysis: `amilib/ami_html.py:HtmlUtil.analyze_coordinates()`

---

**Last Updated:** 2025-12-08  
**Author:** Strategy Document  
**Status:** Implementation Started - Class Structure Created

## Implementation Status

### ✅ Completed

1. **Class Structure Created** (`amilib/html_structure.py`):
   - `TemplateLoader`: Loads and validates templates from JSON
   - `PageMetadataDetector`: Detects page numbers, running titles, marginalia, recto/verso
   - `ColumnDetector`: Detects 1-, 2-, or 3-column layouts
   - `HtmlStructureFormatter`: Main orchestrator class

2. **Tests Created** (`test/test_html_structure.py`):
   - Template loading and validation tests
   - Page metadata detection tests
   - Column detection tests
   - Structure formatter tests

3. **Sample Template** (`amilib/resources/templates/ar6_annex_template.json`):
   - Template for IPCC AR6 Annexes (Glossaries and Acronyms)
   - Includes all page metadata detection configurations

### 🚧 In Progress

1. **Section Hierarchy Detection**: To be implemented
2. **Indentation-Based Grouping**: To be implemented
3. **Floating Element Detection**: Integration with existing `FloatExtractor`
4. **Structure Application**: Complete implementation of structure application

### 📋 Next Steps

1. Test with real AR6 annex HTML files
2. Implement section hierarchy detection
3. Implement indentation-based grouping
4. Integrate with existing `HtmlGroup` and `FloatExtractor` classes
5. Complete structure application logic

