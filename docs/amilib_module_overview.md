# Amilib Module Overview

**Date**: 2025-01-27  
**Purpose**: Analysis of main amilib modules for refactoring to standalone libraries

## Core Modules Analysis

### 1. **PDF Processing** (`ami_pdf_libs.py` - 83KB, 2346 lines)

**Primary Purpose**: Convert PDF documents to HTML and SVG with detailed text extraction and formatting preservation.

**Key Classes**:
- `AmiPage`: Core container for PDF page transformation
- `PDFParser`: Main PDF parsing and conversion engine
- `AmiPlumberJson`: JSON-based PDF processing using pdfplumber
- `PDFDebug`: Debugging utilities for PDF analysis
- `TextStyle`: Font and style management for extracted text
- `CompositeLine`: Handles text lines with subscripts, superscripts, bold, italic

**Key Capabilities**:
- PDF to HTML conversion with preserved formatting
- Text extraction with coordinate information
- Font style preservation (bold, italic, size, family)
- Table extraction and conversion
- Image extraction and processing
- SVG generation for visual elements
- Debug utilities for PDF analysis

**Dependencies**:
- `pdfplumber`, `pdfminer` for PDF parsing
- `lxml` for XML/HTML processing
- `PIL` for image handling
- `amilib.ami_html` for HTML utilities
- `amilib.bbox` for coordinate handling

### 2. **HTML Processing** (`ami_html.py` - 234KB, 6627 lines)

**Primary Purpose**: Comprehensive HTML parsing, editing, markup, and restructuring capabilities.

**Key Classes**:
- `HtmlLib`: Core HTML manipulation utilities
- `HtmlTidy`: Cleans and restructures raw HTML from PDF/OCR
- `HtmlGroup`: Groups HTML elements into hierarchical structures
- `HtmlEditor`: Command-driven HTML editing
- `HtmlAnnotator`: Text annotation and markup
- `HtmlStyle`: CSS style management and normalization
- `HtmlTree`: Builds hierarchical trees from flat HTML elements
- `CSSStyle`: CSS property management
- `AmiFont`: Font normalization and conversion

**Key Capabilities**:
- HTML parsing and validation
- Text annotation and hyperlink creation
- Style extraction and normalization
- Hierarchical section building
- Table creation and manipulation
- DataTables integration
- Font family normalization
- Coordinate-based element positioning
- Footnote extraction and processing

**Dependencies**:
- `lxml` for HTML/XML processing
- `sklearn` for linear regression (coordinate analysis)
- `numpy` for numerical operations
- `amilib.bbox` for coordinate handling
- `amilib.xml_lib` for XML utilities

### 3. **Wikimedia Integration** (`wikimedia.py` - 122KB, 3033 lines)

**Primary Purpose**: Wikipedia, Wikidata, and Wiktionary lookup and data extraction.

**Key Classes**:
- `MediawikiParser`: Parses Wikipedia and Wiktionary pages
- `WikidataLookup`: Searches and retrieves Wikidata information
- `WikipediaPage`: Wikipedia page processing and content extraction
- `WiktionaryPage`: Wiktionary lookup and definition extraction
- `WikidataExtractor`: Wikidata API integration
- `WikidataSparql`: SPARQL query processing
- `WikipediaInfoBox`: Extracts information boxes from Wikipedia

**Key Capabilities**:
- Wikipedia page lookup and content extraction
- Wikidata entity search and property extraction
- Wiktionary definition lookup
- SPARQL query processing
- Information box extraction
- Disambiguation page handling
- Multi-language support
- HTML parsing of Wikimedia pages

**Dependencies**:
- `requests` for HTTP requests
- `SPARQLWrapper` for SPARQL queries
- `lxml` for HTML parsing
- `amilib.ami_html` for HTML utilities
- `amilib.file_lib` for file operations

## Supporting Modules

### 4. **Core Utilities**
- `util.py` (32KB): General utilities, logging, script execution
- `file_lib.py` (27KB): File operations and management
- `xml_lib.py` (69KB): XML processing utilities
- `bbox.py` (19KB): Bounding box and coordinate handling

### 5. **Specialized Processing**
- `ami_dict.py` (77KB): Dictionary creation and management
- `ami_corpus.py` (47KB): Corpus processing and analysis
- `html_marker.py` (47KB): HTML annotation and marking
- `headless_lib.py` (19KB): Headless browser operations

### 6. **Command Line Interface**
- `amix.py` (20KB): Main command-line interface and argument parsing
- `ami_args.py` (10KB): Base argument parsing classes
- `html_args.py` (5.5KB): HTML-specific command arguments
- `pdf_args.py` (26KB): PDF-specific command arguments
- `dict_args.py` (16KB): Dictionary-specific command arguments
- `search_args.py` (15KB): Search-specific command arguments

## Integration Points for Pygetpapers

### File-Based Communication Opportunities

1. **PDF Processing**:
   - Input: PDF files
   - Output: HTML files with preserved formatting
   - Intermediate: JSON metadata files

2. **HTML Restructuring**:
   - Input: Raw HTML files
   - Output: Cleaned, structured HTML files
   - Intermediate: Style extraction files

3. **Wikimedia Lookup**:
   - Input: Term lists or individual terms
   - Output: HTML files with extracted content
   - Intermediate: JSON response files

## Coupling Analysis

### High Coupling Areas
- `amix.py` imports all argument classes
- `ami_pdf_libs.py` imports `ami_html` utilities
- `wikimedia.py` imports `ami_html` utilities
- Multiple modules depend on `util.py` and `file_lib.py`

### Standalone Potential
- **PDF Processing**: Could be standalone with minimal dependencies
- **HTML Processing**: Core functionality could be extracted
- **Wikimedia**: Already relatively self-contained

## Refactoring Priorities

1. **Extract PDF Processing**: Create standalone PDF-to-HTML converter
2. **Extract HTML Core**: Create standalone HTML processing library
3. **Extract Wikimedia**: Create standalone Wikimedia lookup library
4. **Create File Interfaces**: Design file-based communication protocols
5. **Reduce Dependencies**: Minimize cross-module imports

---
*This overview will be updated as refactoring progresses.* 