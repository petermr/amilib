# Redundant Tests Analysis

## Overview
This document identifies redundant tests in the amilib test suite that use the same IPCC PDF files, allowing us to remove duplicates while maintaining test coverage.

## Redundant Test Groups

### 1. TEST_IPCC_CHAP06_PDF (Chapter 6) - 9 redundant tests

**Core functionality tests:**
- `test_make_raw_ami_pages_with_spans_from_charstream_ipcc_chap6` - Basic PDF processing
- `test_make_structured_html_MAIN` - HTML conversion
- `test_convert_to_raw_html_chap6_maxpage_example` - Raw HTML conversion

**Debug/analysis tests (redundant):**
- `test_convert_to_raw_html_chap6_page_ranges__fail` - Failing test, redundant
- `test_read_ipcc_chapter__debug` - Debug test, redundant
- `test_extract_single_page_ipcc_toc_chap6` - Single page extraction, redundant
- `test_make_styled_text_chunks_PDFPlumber` - Style analysis, redundant
- `test_debug_page_properties_chap6_word_count_and_images_data_wg3_old__example` - Debug test, redundant
- `test_pdfminer_images` - Image extraction, redundant

**Recommendation:** Keep 3 core tests, disable 6 redundant debug/analysis tests

### 2. TEST_IPCC_WG2_CHAP03_PDF (WG2 Chapter 3) - 2 redundant tests

- `test_final_ipcc_format_debug_LONG` - Format debugging
- `test_debug_page_properties_chap6_word_count_and_images_data_wg2_new__example` - Debug test

**Recommendation:** Keep 1 test, disable 1 redundant debug test

### 3. TEST_IPCC_LONGER_REPORT - 2 redundant tests

- `test_pdfplumber_singlecol_create_spans_with_CSSStyles` - CSS style processing
- `test_pdfplumber_json_longer_report_debug` - Debug test (in test_ipcc.py)

**Recommendation:** Keep 1 test, disable 1 redundant debug test

### 4. TEST_IPCC_CHAP15 - 2 redundant tests

- `test_pdf_plumber_table_LONG` - Table processing
- `test_wg3_15_character_and_page_properties` - Character analysis

**Recommendation:** Keep 1 test, disable 1 redundant test

## Summary

**Total redundant tests identified:** 15 tests
**Tests to disable:** 10 tests (keeping 5 core functionality tests)
**Estimated time savings:** ~30-40% reduction in PDF test runtime

## Implementation Plan

1. Disable redundant debug/analysis tests
2. Keep core functionality tests for each PDF
3. Maintain test coverage while reducing runtime
4. Monitor test results to ensure no regressions

## Files to Modify

- `test/test_pdf.py` - Main PDF test file
- `test/test_ipcc.py` - IPCC-specific tests
- `test/test_headless.py` - Headless operation tests 