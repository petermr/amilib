# Document Annotation Scripts

Scripts for adding hyperlinks and annotations to PDFs and HTML documents, particularly for glossary term linking.

## Scripts

### **`markup_climate_pdfs_with_glossary.py`** ⭐⭐⭐⭐⭐
**Purpose**: Add IPCC glossary hyperlinks to climate PDFs

**Current Status**:
- ✅ Excellent user-facing tool
- ✅ Uses argparse and parameterized methods
- ❌ Some hardcoded values
- ❌ Limited error handling

**Planned Improvements**:
- Better error handling and progress reporting
- Configuration for different glossaries
- Support for different PDF types
- Better output formatting

**Usage**:
```bash
python markup_climate_pdfs_with_glossary.py --single /path/to/file.pdf
python markup_climate_pdfs_with_glossary.py  # Process all PDFs
```

### **`markup_ipcc_executive_summary.py`** ⭐⭐⭐⭐
**Purpose**: Add glossary links to IPCC HTML documents

**Current Status**:
- ✅ Good user-facing tool
- ✅ Uses parameterized methods
- ❌ Hardcoded input/output files
- ❌ Limited error handling

**Planned Improvements**:
- Parameterize input/output files
- Support for different document types
- Better error handling
- Configuration file support

**Usage** (planned):
```bash
python markup_html.py --input /path/to/input.html --output /path/to/output.html --glossary /path/to/glossary.csv
```

### **`create_flat_glossary.py`** ⭐⭐⭐
**Purpose**: Convert HTML glossary to flat text format

**Current Status**:
- ✅ Useful utility
- ❌ Hardcoded file paths
- ❌ Business logic in main()
- ❌ Violates style guide

**Planned Improvements**:
- Add command-line arguments
- Better error handling
- Support for different input formats

**Usage** (planned):
```bash
python create_flat_glossary.py --input /path/to/input.csv --output /path/to/output.csv
```

### **`process_biorxiv_pdfs_simple.py`** ⭐⭐⭐
**Purpose**: Simplified PDF annotation (avoids pdfplumber dependency)

**Current Status**:
- ✅ Alternative to main annotation tool
- ❌ Redundant with main annotation tool
- ❌ Hardcoded parameters
- ❌ Business logic in main()

**Recommendation**: Merge functionality into main annotation tool

### **`process_remaining_biorxiv.py`** ⭐⭐
**Purpose**: Background processing of bioRxiv PDFs

**Current Status**:
- ❌ Very specific use case
- ❌ Too specific, violates style guide
- ❌ Shell commands in Python code
- ❌ Hardcoded paths

**Recommendation**: Integrate into main annotation tool as background option or remove

## Planned Unified Tool

The annotation scripts will be consolidated into a unified `annotate_documents.py` tool with:

- Support for both PDF and HTML documents
- Multiple glossary formats
- Background processing option
- Configuration file support
- Better error handling and progress reporting
- Multiple output formats

## Dependencies

- PyMuPDF (fitz) for PDF processing
- lxml for HTML processing
- BeautifulSoup for HTML parsing
- amilib for document processing utilities 