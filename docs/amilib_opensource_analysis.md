# Amilib Open Source Library Analysis

**Date**: 2025-01-27  
**Purpose**: Identify functionality in amilib that could be replaced by existing open source libraries

## Analysis Results

### 1. **PDF Processing** (`ami_pdf_libs.py`)

#### ✅ **Already Using Good Libraries**
- **pdfplumber**: Already used extensively (good!)
- **pdfminer**: Used for some conversions (acceptable)
- **PIL/Pillow**: Used for image processing (good!)

#### 🔍 **Potential Replacements**

**Custom PDF Parsing Logic**:
- Lines 1099-1222: `PDFParser` class with custom PDF conversion
- **Recommendation**: Could be simplified to use pdfplumber exclusively
- **Rationale**: pdfplumber already provides most of this functionality

**Custom Text Style Analysis**:
- Lines 990-1098: `TextStyle` class with font analysis
- **Recommendation**: Could use `fonttools` library for font analysis
- **Rationale**: fonttools is the standard for font processing

**Custom Coordinate Processing**:
- Lines 1280-1332: Custom curve and line processing
- **Recommendation**: Could use `shapely` for geometric operations
- **Rationale**: shapely is the standard for geometric processing

### 2. **HTML Processing** (`ami_html.py`)

#### ✅ **Already Using Good Libraries**
- **lxml**: Used extensively (good!)
- **sklearn**: Used for coordinate analysis (acceptable)

#### 🔍 **Potential Replacements**

**Custom CSS Processing**:
- Lines 5476-6108: `CSSStyle` class with extensive CSS parsing
- **Recommendation**: Could use `cssutils` or `tinycss2` for CSS parsing
- **Rationale**: These are dedicated CSS parsing libraries

**Custom Font Analysis**:
- Lines 6216-6437: `AmiFont` class with font normalization
- **Recommendation**: Could use `fonttools` for font analysis
- **Rationale**: fonttools is the standard for font processing

**Custom HTML Cleaning**:
- Lines 282-534: `HtmlTidy` class for cleaning HTML
- **Recommendation**: Could use `bleach` for HTML sanitization
- **Rationale**: bleach is specifically designed for HTML cleaning

**Custom Coordinate Analysis**:
- Lines 3931-3954: Custom coordinate analysis with sklearn
- **Recommendation**: Could use `scipy.spatial` for spatial analysis
- **Rationale**: scipy provides more robust spatial algorithms

### 3. **Wikimedia Integration** (`wikimedia.py`)

#### ✅ **Already Using Good Libraries**
- **requests**: Used for HTTP requests (good!)
- **SPARQLWrapper**: Used for SPARQL queries (good!)
- **lxml**: Used for HTML parsing (good!)

#### 🔍 **Potential Replacements**

**Custom HTML Parsing**:
- Lines 1170-1187: `ParserWrapper` class
- **Recommendation**: Could use `BeautifulSoup` for malformed HTML
- **Rationale**: BeautifulSoup is more forgiving with Wikipedia's HTML

**Custom URL Processing**:
- Lines 1445-1453: Custom URL construction
- **Recommendation**: Could use `urllib.parse` more extensively
- **Rationale**: urllib.parse is the standard for URL manipulation

### 4. **Core Utilities**

#### 🔍 **Potential Replacements**

**Custom File Operations** (`file_lib.py`):
- **Recommendation**: Could use `pathlib` more extensively
- **Rationale**: pathlib provides modern file operations

**Custom XML Processing** (`xml_lib.py`):
- **Recommendation**: Could use `lxml` more extensively
- **Rationale**: lxml provides better XML processing than custom code

**Custom Logging** (`util.py`):
- **Recommendation**: Could use `structlog` for structured logging
- **Rationale**: structlog provides better logging capabilities

## Specific Library Recommendations

### 1. **Font Processing**
```python
# Current: Custom AmiFont class (6216-6437 lines)
# Replace with: fonttools
from fonttools.ttLib import TTFont
from fonttools.fontTools import fontTools
```

### 2. **CSS Processing**
```python
# Current: Custom CSSStyle class (5476-6108 lines)
# Replace with: cssutils or tinycss2
import cssutils
import tinycss2
```

### 3. **HTML Sanitization**
```python
# Current: Custom HtmlTidy class (282-534 lines)
# Replace with: bleach
import bleach
```

### 4. **Geometric Operations**
```python
# Current: Custom coordinate processing (1280-1332 lines)
# Replace with: shapely
from shapely.geometry import Point, LineString, Polygon
```

### 5. **Spatial Analysis**
```python
# Current: Custom coordinate analysis with sklearn (3931-3954 lines)
# Replace with: scipy.spatial
from scipy.spatial import distance, KDTree
```

## Implementation Priority

### High Priority (Major Code Reduction)
1. **CSS Processing**: Replace custom CSS parsing with `cssutils` or `tinycss2`
2. **Font Analysis**: Replace custom font processing with `fonttools`
3. **HTML Sanitization**: Replace custom HTML cleaning with `bleach`

### Medium Priority (Significant Improvement)
1. **Geometric Operations**: Replace custom coordinate processing with `shapely`
2. **Spatial Analysis**: Replace custom analysis with `scipy.spatial`
3. **PDF Parsing**: Simplify to use pdfplumber exclusively

### Low Priority (Minor Improvements)
1. **URL Processing**: Use `urllib.parse` more extensively
2. **File Operations**: Use `pathlib` more extensively
3. **Logging**: Use `structlog` for better logging

## Estimated Code Reduction

- **CSS Processing**: ~632 lines (10% of ami_html.py)
- **Font Analysis**: ~221 lines (3% of ami_html.py)
- **HTML Sanitization**: ~252 lines (4% of ami_html.py)
- **Geometric Operations**: ~52 lines (2% of ami_pdf_libs.py)
- **Total Potential Reduction**: ~1,157 lines (significant!)

## Next Steps

1. **Evaluate each library** for compatibility and features
2. **Create proof-of-concept** implementations
3. **Test with existing functionality**
4. **Gradually replace** custom code with library calls
5. **Update dependencies** in requirements.txt

---
*This analysis will be updated as we evaluate specific libraries.* 