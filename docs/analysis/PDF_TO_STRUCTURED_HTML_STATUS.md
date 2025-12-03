# PDF to Structured HTML Conversion - Status Review

**Date:** Thursday, November 27, 2025  
**Branch:** `pmr202511`  
**Reviewer:** AI Assistant

## Executive Summary

The PDF to structured HTML conversion pipeline is **partially implemented** with a multi-step pipeline architecture in place. The core conversion functionality works, but several steps remain incomplete or need improvement. The pipeline follows a 10-step process from raw PDF to final structured HTML.

## Current Implementation Status

### ✅ Completed Components

#### 1. **PDF to Raw HTML Conversion** (Step 1)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.convert_pdf_to_html()`
- **Implementation:** Uses `HtmlGenerator.read_pdf_convert_to_html()` which calls `AmiPDFPlumber`
- **Output:** Raw HTML with absolute positioning from PDF coordinates
- **Notes:** Works with both pdfplumber and pdfminer backends

#### 2. **Style Normalization** (Steps 2-3)
- **Status:** ✅ **COMPLETE** (with minor bugs noted)
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step2_3()`
- **Implementation:** 
  - `HtmlStyle.extract_styles_and_normalize_classrefs()` - Extracts and normalizes CSS classes
  - Creates `normalized.html` output
- **Known Issues:** 
  - Comment in code: `# TODO has minor bugs in joining spans` (line 1157)
- **Output:** Normalized HTML with extracted styles

#### 3. **Section Tagging** (Step 4)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step_4_tag_sections()`
- **Implementation:** Uses `SpanMarker.markup_file_with_markup_dict()` to tag sections
- **Capabilities:**
  - Tags sections by style and content (Decision, Chapter, subchapter, numbered paragraphs, lists)
  - Adds IDs to sections
  - Uses regex-based markup dictionary
- **Output:** `sectiontag.html` with tagged sections

#### 4. **File Splitting** (Step 5)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step5_split_to_files()`
- **Implementation:** `SpanMarker.split_at_sections_and_write_split_files()`
- **Capabilities:**
  - Splits major sections into separate HTML files
  - Uses regex templates for file naming
  - Example: `CMA1_4` → `CMA1`, `CMA2`, etc.
- **Output:** Multiple HTML files, one per section

#### 5. **Inline Markup** (Step 8)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step8_inline_markup()`
- **Implementation:** `SpanMarker.split_spans_in_html()` with dictionary-based annotation
- **Capabilities:**
  - Searches for substrings in spans
  - Adds hyperlinks to dictionaries
  - Applies inline markup with styles
- **Output:** `marked.html` with inline annotations

#### 6. **HTML Cleaning** (Step 9)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step_9_clean()`
- **Implementation:** `HtmlCleaner.clean_elems()` with configurable options
- **Capabilities:**
  - Removes XY coordinates (`XY_LIST`)
  - Removes LRTB coordinates (`LRTB_LIST`)
  - Removes style attributes (`STYLE_LIST`)
- **Output:** `cleaned.html` with cleaned structure

#### 7. **Final Step** (Step 999)
- **Status:** ✅ **COMPLETE**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_final_step_999()`
- **Implementation:** Copies cleaned file to `final.html`
- **Output:** Final structured HTML file

### ⚠️ Incomplete Components

#### 1. **Hierarchical Nesting** (Step 7)
- **Status:** ❌ **NOT IMPLEMENTED**
- **Location:** `amilib/html_marker.py::HtmlPipeline.run_step7_make_nested_noop()` (line 1205-1210)
- **Current State:**
  ```python
  @classmethod
  def run_step7_make_nested_noop(cls, infile, outfile):
      logger.debug(f"nesting not yet written")
      return
      # Code below is unreachable:
      html_elem = HtmlLib.parse_html(infile)
      SpanMarker.move_implicit_children_to_parents(html_elem)
      HtmlLib.write_html_file(html_elem, outfile)
  ```
- **Required Functionality:**
  - Convert flat HTML structure to hierarchical nested structure
  - Move implicit children to their proper parent elements
  - Create semantic document structure (sections, subsections, etc.)
- **Impact:** High - This is a critical step for creating truly "structured" HTML
- **Priority:** **HIGH**

#### 2. **PDF to Raw HTML Tidy Process**
- **Status:** ⚠️ **PARTIAL** (marked as URGENT)
- **Location:** `amilib/pdf_args.py::pdf_to_raw_then_raw_to_tidy()` (line 444)
- **Current State:**
  - Comment: `# then make HtmlTidy and execute commands to clean`
  - Comment: `# URGENT`
- **Implementation:** Uses `HtmlTidy.tidy_flow()` but may need enhancement
- **Priority:** **HIGH**

#### 3. **Parentheses Markup**
- **Status:** ❌ **NOT IMPLEMENTED** (marked as NYI)
- **Location:** `amilib/pdf_args.py::markup_parentheses()` (line 485-495)
- **Current State:**
  ```python
  def markup_parentheses(self, result_elem):
      """iterate over parenthesised fields
      iterates over HTML spans
      NYI
      should be in HTML
      """
      xpath = ".//span"
      spans = result_elem.xpath(xpath)
      for span in spans:
          # self.extract_brackets(span)
          pass
  ```
- **Required Functionality:**
  - Extract parenthesized citations: `(IPCC 2018a)`, `(Roy et al. 2018)`, etc.
  - Add hyperlinks for references
  - Handle multiple citations: `(Bertram et al. 2015; Riahi et al. 2015)`
- **Priority:** **MEDIUM**

#### 4. **Bracket Extraction**
- **Status:** ❌ **PARTIALLY IMPLEMENTED** (marked as NYI)
- **Location:** `amilib/pdf_args.py::extract_brackets()` (line 497-545)
- **Current State:** Code exists but incomplete, marked as NYI
- **Required Functionality:**
  - Extract citation patterns from spans
  - Create hyperlinks for references
  - Handle complex citation formats
- **Priority:** **MEDIUM**

## Pipeline Architecture

### Current Pipeline Steps (from `HtmlPipeline.stateless_pipeline()`)

```
STEP 1: PDF → Raw HTML
  ├─ Input: PDF file
  ├─ Process: HtmlGenerator.read_pdf_convert_to_html()
  └─ Output: raw.html

STEP 2-3: Style Normalization
  ├─ Input: raw.html
  ├─ Process: HtmlStyle.extract_styles_and_normalize_classrefs()
  └─ Output: normalized.html

STEP 4: Section Tagging
  ├─ Input: normalized.html
  ├─ Process: SpanMarker.markup_file_with_markup_dict()
  └─ Output: sectiontag.html

STEP 5: File Splitting
  ├─ Input: sectiontag.html
  ├─ Process: SpanMarker.split_at_sections_and_write_split_files()
  └─ Output: Multiple split HTML files

STEP 7: Hierarchical Nesting ⚠️ NOT IMPLEMENTED
  ├─ Input: split.html
  ├─ Process: Should create nested structure
  └─ Output: nested.html (currently skipped)

STEP 8: Inline Markup
  ├─ Input: split.html (should be nested.html)
  ├─ Process: SpanMarker.split_spans_in_html()
  └─ Output: marked.html

STEP 9: HTML Cleaning
  ├─ Input: marked.html
  ├─ Process: HtmlCleaner.clean_elems()
  └─ Output: cleaned.html

STEP 999: Final Copy
  ├─ Input: cleaned.html
  ├─ Process: File copy
  └─ Output: final.html
```

## Key Files and Classes

### Core Conversion Files
1. **`amilib/pdf_args.py`** (717 lines)
   - `PDFArgs` class - CLI argument handling and orchestration
   - `pdf_to_styled_html_CORE()` - Main conversion entry point
   - `pdf_to_raw_then_raw_to_tidy()` - PDF to HTML conversion
   - Contains TODOs and NYI markers

2. **`amilib/html_marker.py`** (1259+ lines)
   - `HtmlPipeline` class - Complete pipeline orchestration
   - `SpanMarker` class - Section tagging and markup
   - `HtmlCleaner` class - HTML cleaning utilities
   - Pipeline steps implementation

3. **`amilib/html_generator.py`**
   - `HtmlGenerator` class - PDF to HTML conversion
   - `read_pdf_convert_to_html()` - Main conversion method
   - `create_html_pages()` - Page-by-page conversion

4. **`amilib/ami_pdf_libs.py`** (2346 lines)
   - `PDFParser` class - Low-level PDF parsing
   - `AmiPage` class - Page-level processing
   - `AmiPDFPlumber` - pdfplumber integration

5. **`amilib/ami_html.py`** (6627 lines)
   - `HtmlTidy` class - HTML tidying and flow
   - `HtmlStyle` class - Style extraction and normalization
   - `HtmlGroup` class - Grouping and hierarchical structure
   - `CSSStyle` class - CSS management

## Remaining Tasks

### High Priority Tasks

1. **Implement Step 7: Hierarchical Nesting** ⚠️
   - **File:** `amilib/html_marker.py`
   - **Method:** `run_step7_make_nested_noop()` → rename and implement
   - **Requirements:**
     - Convert flat HTML structure to hierarchical nested structure
     - Implement `SpanMarker.move_implicit_children_to_parents()`
     - Create semantic document structure (sections, subsections, paragraphs)
     - Ensure proper parent-child relationships
   - **Estimated Effort:** Medium-High
   - **Dependencies:** `HtmlGroup` class may have relevant methods

2. **Complete PDF Tidy Process** ⚠️
   - **File:** `amilib/pdf_args.py`
   - **Location:** `pdf_to_raw_then_raw_to_tidy()` (line 444)
   - **Requirements:**
     - Review and enhance `HtmlTidy.tidy_flow()` implementation
     - Ensure proper cleaning of raw HTML from PDF
     - Remove "URGENT" marker after completion
   - **Estimated Effort:** Medium
   - **Dependencies:** `HtmlTidy` class

3. **Fix Style Normalization Bugs**
   - **File:** `amilib/html_marker.py`
   - **Location:** `run_step2_3()` (line 1157)
   - **Issue:** `# TODO has minor bugs in joining spans`
   - **Requirements:**
     - Investigate and fix span joining issues
     - Test with various PDF formats
     - Remove TODO comment after fix
   - **Estimated Effort:** Low-Medium

### Medium Priority Tasks

4. **Implement Parentheses Markup**
   - **File:** `amilib/pdf_args.py`
   - **Method:** `markup_parentheses()` (line 485)
   - **Requirements:**
     - Iterate over HTML spans
     - Extract parenthesized citations
     - Add hyperlinks for references
     - Handle multiple citation formats
   - **Estimated Effort:** Medium
   - **Note:** Comment says "should be in HTML" - may need to move to `ami_html.py`

5. **Complete Bracket Extraction**
   - **File:** `amilib/pdf_args.py`
   - **Method:** `extract_brackets()` (line 497)
   - **Requirements:**
     - Complete regex pattern matching
     - Implement citation link creation
     - Handle complex citation formats
   - **Estimated Effort:** Medium
   - **Note:** Code partially exists but incomplete

6. **Improve Converter Tool**
   - **File:** `amilib/pdf_args.py`
   - **Location:** `pdf_to_styled_html_CORE()` (line 649)
   - **Comment:** `"uses a lot of defaults. will be better when we have a converter tool"`
   - **Requirements:**
     - Create configurable converter tool
     - Reduce hardcoded defaults
     - Improve flexibility
   - **Estimated Effort:** Medium-High

### Low Priority / Enhancement Tasks

7. **Documentation**
   - Create comprehensive documentation for the pipeline
   - Document each step's input/output format
   - Add examples and use cases
   - **Estimated Effort:** Low-Medium

8. **Testing**
   - Add comprehensive tests for each pipeline step
   - Test with various PDF formats
   - Test edge cases
   - **Estimated Effort:** Medium

9. **Error Handling**
   - Improve error messages throughout pipeline
   - Add validation at each step
   - Better handling of malformed PDFs
   - **Estimated Effort:** Medium

10. **Performance Optimization**
    - Profile pipeline performance
    - Optimize slow steps
    - Add caching where appropriate
    - **Estimated Effort:** Medium-High

## Technical Debt

### Code Quality Issues

1. **Hardcoded Values**
   - `Path(outdir, "tidied.html")` - hardcoded filename (line 467 in `pdf_args.py`)
   - Various default values scattered throughout

2. **Incomplete Methods**
   - `run_step7_make_nested_noop()` - returns immediately
   - `markup_parentheses()` - empty implementation
   - `extract_brackets()` - incomplete implementation

3. **Comments Indicating Issues**
   - "URGENT" markers
   - "NYI" (Not Yet Implemented) markers
   - "TODO" comments with bugs

4. **Method Naming**
   - `run_step7_make_nested_noop()` - "noop" in name suggests incomplete

## Recommendations

### Immediate Actions

1. **Implement Step 7 (Hierarchical Nesting)**
   - This is the most critical missing piece for "structured" HTML
   - Review `HtmlGroup` class for existing functionality
   - Implement proper nesting algorithm

2. **Address URGENT Items**
   - Complete PDF tidy process
   - Fix style normalization bugs

3. **Code Cleanup**
   - Remove or implement NYI methods
   - Rename `run_step7_make_nested_noop()` when implemented
   - Remove hardcoded values

### Short-term Improvements

4. **Complete Citation Markup**
   - Implement parentheses and bracket extraction
   - Move to appropriate module if needed

5. **Testing and Documentation**
   - Add tests for each pipeline step
   - Document expected input/output formats

### Long-term Enhancements

6. **Refactoring**
   - Create configurable converter tool
   - Reduce hardcoded defaults
   - Improve modularity

7. **Performance**
   - Profile and optimize
   - Add caching mechanisms

## Conclusion

The PDF to structured HTML conversion pipeline is **approximately 70-80% complete**. The core conversion functionality works well, but the critical **Step 7 (Hierarchical Nesting)** is missing, which prevents the output from being truly "structured" HTML. Several other features are marked as incomplete or need improvement.

**Priority Focus Areas:**
1. Implement hierarchical nesting (Step 7)
2. Complete PDF tidy process (URGENT)
3. Fix style normalization bugs
4. Complete citation markup features

Once these are completed, the pipeline should be production-ready for creating structured HTML from PDF documents.







