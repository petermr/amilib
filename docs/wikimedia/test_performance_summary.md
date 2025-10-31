# Test Performance Summary

## Overview

This document summarizes the performance characteristics of tests in `test_wikimedia.py` and `test_dict_wikidata_extraction.py`, identifying long-running tests and their execution times.

**Total test suite time:** ~77 seconds (1 minute 17 seconds)

## Longest-Running Tests

### Critical (20+ seconds)

1. **23.03s** - `test_dict_wikidata_extraction.py::TestDictWikidataExtraction::test_wikidata_id_html_output`
   - **Reason:** Creates a full dictionary with Wikipedia descriptions, makes multiple Wikipedia API calls, and generates HTML output
   - **Action:** This test performs a complete end-to-end workflow and is expected to be slow

### Moderate (3-5 seconds)

2. **4.67s** - `test_wikimedia.py::WikipediaTest::test_edit_disambiguation_page`
   - **Reason:** Tests disambiguation page editing with Wikipedia API calls
   
3. **4.46s** - `test_wikimedia.py::WikipediaTest::test_create_semantic_html_split_sentences`
   - **Reason:** Tests semantic HTML creation with sentence splitting and Wikipedia lookups

4. **3.05s** - `test_dict_wikidata_extraction.py::TestDictWikidataExtraction::test_page_type_detection`
   - **Reason:** Tests page type detection for multiple page types (article, disambiguation, redirect, list) with multiple Wikipedia API calls

### Minor (1.5-3 seconds)

5. **2.45s** - `test_wikimedia.py::WikidataTest::test_lookup_multiple_terms_solvents`
   - **Reason:** Tests multiple term lookups in Wikidata

6. **2.10s** - `test_wikimedia.py::WikipediaTest::test_flat_disambiguation_page`
   - **Reason:** Tests flat disambiguation page handling

7. **1.77s** - `test_wikimedia.py::MWParserTest::test_create_html_dictionary_with_wikipedia_urls`
   - **Reason:** Creates HTML dictionary with Wikipedia URLs

8. **1.76s** - `test_dict_wikidata_extraction.py::TestDictWikidataExtraction::test_extract_wikidata_id_from_article`
   - **Reason:** Tests Wikidata ID extraction from multiple articles (climate change, greenhouse effect, carbon dioxide)

## Performance Characteristics

### Network-Dependent Tests
Tests that make external API calls (Wikipedia, Wikidata) are inherently slower:
- Wikipedia page lookups: ~1-2 seconds each
- Wikidata lookups: ~0.5-1 second each
- Multiple lookups in a single test compound the time

### Integration Tests
Tests that perform full workflows (dictionary creation, HTML generation) take longer:
- File I/O operations
- Multiple API calls
- HTML parsing and generation

### Tests with Multiple Iterations
Tests that iterate over multiple terms/items accumulate time:
- `test_extract_wikidata_id_from_article` tests 3 terms
- `test_lookup_multiple_terms_solvents` tests multiple solvents

## Recommendations

### For Development
- Run specific test files/modules during development rather than the full suite
- Use `-k` flag to run specific tests: `pytest -k "test_wikidata_id"`
- Use `--lf` (last failed) to rerun only failed tests

### For CI/CD
- Consider splitting long integration tests into separate test runs
- Use test parallelization with `pytest-xdist` if available
- Mark very slow tests with `@pytest.mark.slow` and run separately

### Test Optimization Opportunities
1. **Mock external API calls** for unit tests (keep integration tests separate)
2. **Cache Wikipedia/Wikidata responses** where possible for repeat runs
3. **Reduce iterations** in parameterized tests during quick development runs

## Test Suite Summary

- **Total tests:** 77 tests
- **Passed:** 69 tests
- **Failed:** 2 tests (pre-existing issues, unrelated to new functionality)
- **Skipped:** 6 tests
- **Average test time:** ~1 second per test
- **Longest single test:** 23.03 seconds

## Notes

- Execution times are approximate and may vary based on network conditions
- Times measured on macOS with Python 3.12.7
- Two failing tests are pre-existing issues (exact HTML content matching, test bug)
- All new Wikidata ID extraction functionality passes all tests

