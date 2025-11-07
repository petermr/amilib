# Test Optimization Analysis

## Overview

This document analyzes the slowest tests in the test suite and provides optimization suggestions. All optimizations maintain at least one real lookup (no mocks) while reducing redundant operations.

## Slowest Tests Analysis

### 1. `test_dictionary_annotation_workflow` (107.93s)

**Location:** `test/test_annotate.py::AnnotateTest::test_dictionary_annotation_workflow`

**Current Behavior:**
- Loads wordlist from external URL (290-310 terms)
- Creates CSV from all terms
- Processes entire IPCC PDF (~100+ pages)
- Adds hyperlinks to all matches

**Bottlenecks:**
1. Network call to GitHub for wordlist
2. Processing entire PDF (~100+ pages)
3. Word matching across all pages

**Optimization Suggestions:**

```python
def test_dictionary_annotation_workflow(self):
    """Test complete dictionary annotation workflow using external wordlist"""
    self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
    
    # OPTIMIZATION: Limit to first 5-10 terms instead of 290+
    temp_csv = self._create_word_csv_from_url(self.shaik_url, max_terms=5)
    
    # OPTIMIZATION: Process only first 10 pages instead of entire PDF
    output_pdf = Resources.TEMP_DIR / "IPCC_AR6_WGII_Chapter07_dictionary_annotated.pdf"
    
    try:
        adder = self._create_pdf_adder(self.ipcc_pdf, temp_csv, output_pdf)
        # OPTIMIZATION: Add max_pages parameter to PDFHyperlinkAdder
        adder.process_pdf(max_pages=10)
        
        self._assert_pdf_processed_successfully(output_pdf, adder)
    finally:
        if temp_csv.exists():
            temp_csv.unlink()
```

**Changes needed:**
1. Modify `_create_word_csv_from_url` to accept `max_terms` parameter
2. Add `max_pages` parameter to `PDFHyperlinkAdder.process_pdf()`
3. Keep at least 1 term (ensures at least one lookup)

**Expected Time Savings:** ~90% (from 108s to ~10s)

---

### 2. `test_wikidata_id_html_output` (29.56s)

**Location:** `test/test_dict_wikidata_extraction.py::TestDictWikidataExtraction::test_wikidata_id_html_output`

**Current Behavior:**
- Creates dictionary with 2 terms ("climate change", "carbon dioxide")
- Performs Wikipedia lookups for both terms
- Generates HTML output

**Bottlenecks:**
1. Two Wikipedia lookups (network calls)
2. HTML generation

**Optimization Suggestions:**

```python
def test_wikidata_id_html_output(self):
    """Test that Wikidata ID and link appear in HTML output"""
    dict_file = Path(self.temp_dir, "test_wikidata_output.html")
    
    from amilib.dict_args import AmiDictArgs
    
    # OPTIMIZATION: Use only 1 term instead of 2 (keep at least one lookup)
    words_file = Path(self.temp_dir, "test_words.txt")
    words_file.write_text("climate change\n")  # Only 1 term
    
    args = AmiDictArgs()
    args.words = str(words_file)
    args.dictfile = str(dict_file)
    args.description = ["wikipedia"]
    args.title = "Test Dictionary"
    args.figures = None
    
    args.create_dictionary_from_words("Test Dictionary")
    
    self.assertTrue(dict_file.exists(), "Dictionary HTML file should be created")
    
    html_content = dict_file.read_text()
    self.assertIn("wikidata", html_content.lower(), 
                 "HTML should contain Wikidata references")
```

**Expected Time Savings:** ~50% (from 30s to ~15s)

---

### 3. `test_search_with_dictionary_and_make_links_IMPORTANT` (10.66s)

**Location:** `test/test_dict.py::AmiDictionaryTest::test_search_with_dictionary_and_make_links_IMPORTANT`

**Current Behavior:**
- Extracts all paragraphs from chapter (~1000-1200 paragraphs)
- Loads dictionary with 11 terms
- Searches all paragraphs for all terms
- Generates HTML output

**Bottlenecks:**
1. Processing 1000+ paragraphs
2. Searching 11 terms across all paragraphs
3. HTML generation

**Optimization Suggestions:**

```python
def test_search_with_dictionary_and_make_links_IMPORTANT(self):
    """Test dictionary search with limited paragraphs"""
    
    chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", f"{self.HTML_WITH_IDS}.html")
    
    # OPTIMIZATION: Limit to first 100 paragraphs instead of all
    paras = HtmlLib._extract_paras_with_ids(chapter_file, count=100)
    assert len(paras) == 100, f"Expected 100 paragraphs, got {len(paras)}"
    
    xml_dict_path = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", "climate_words.xml")
    dictionary = AmiDictionary.create_from_xml_file(xml_dict_path)
    assert dictionary is not None
    
    phrases = dictionary.get_terms()
    assert len(phrases) == 11
    
    # OPTIMIZATION: Skip HTML generation if not needed for test
    # Only generate if we need to verify HTML structure
    html_path = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", "climate_words.html")
    if not html_path.exists():
        dictionary.create_html_write_to_file(html_path, debug=False)
    dictionary.location = html_path
    
    # OPTIMIZATION: Search only first 50 paragraphs
    para_phrase_dict = HtmlLib.search_phrases_in_paragraphs(paras[:50], phrases, markup=html_path)
    
    # Verify we found at least one match (one lookup)
    assert len(para_phrase_dict) > 0, "Should find at least one phrase match"
    
    chapter_elem = paras[0].xpath("/html")[0]
    chapter_outpath = Path(Resources.TEMP_DIR, "ipcc", "Chapter03", "marked_up.html")
    HtmlLib.write_html_file(chapter_elem, chapter_outpath, debug=False)
```

**Expected Time Savings:** ~70% (from 11s to ~3s)

---

### 4. `test_pdf_hyperlink_adder_ipcc` (10.23s)

**Location:** `test/test_annotate.py::AnnotateTest::test_pdf_hyperlink_adder_ipcc`

**Current Behavior:**
- Processes entire IPCC PDF (~100+ pages)
- Matches words from CSV across all pages

**Bottlenecks:**
1. Processing entire PDF
2. Word matching across all pages

**Optimization Suggestions:**

```python
def test_pdf_hyperlink_adder_ipcc(self):
    """Test PDF hyperlink adder with IPCC PDF (limited pages)"""
    
    climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
    
    self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
    self._verify_file_exists(climate_words, "Climate words file")
    
    output_pdf = Resources.TEMP_DIR / "ipcc_with_links.pdf"
    
    # OPTIMIZATION: Add max_pages parameter
    adder = self._create_pdf_adder(self.ipcc_pdf, climate_words, output_pdf)
    adder.process_pdf(max_pages=10)  # Process only first 10 pages
    
    self._assert_pdf_processed_successfully(output_pdf, adder)
```

**Changes needed:**
- Add `max_pages` parameter to `PDFHyperlinkAdder.process_pdf()`

**Expected Time Savings:** ~80% (from 10s to ~2s)

---

### 5. `test_edit_disambiguation_page` (7.40s)

**Location:** `test/test_wikimedia.py::WikipediaTest::test_edit_disambiguation_page`

**Bottlenecks:**
- Wikipedia API calls for disambiguation pages
- Multiple lookups

**Optimization Suggestions:**
- Limit to 1 disambiguation term instead of multiple
- Cache results if same term is looked up multiple times

---

### 6. `test_download_wg2_cross_chapters` (7.29s)

**Location:** `test/test_headless.py::DriverTest::test_download_wg2_cross_chapters`

**Bottlenecks:**
- Headless browser operations
- Multiple chapter downloads

**Optimization Suggestions:**
- Download only 1 chapter instead of multiple
- Use shorter timeout for headless operations

---

### 7. Dictionary Entry Creation Tests (5-7s each)

**Locations:**
- `test/test_dictionary_entry_creation.py::TestDictionaryEntryCreation::test_multiword_wikipedia_success`
- `test/test_dictionary_entry_creation.py::TestDictionaryEntryCreation::test_single_word_disambiguation_handling`
- `test/test_dictionary_entry_creation.py::TestDictionaryEntryCreation::test_single_word_wikipedia_success`

**Common Bottlenecks:**
- Wikipedia lookups for each term
- Wikidata lookups
- HTML generation

**Optimization Suggestions:**
- Use only 1 term per test (keep at least one lookup)
- Skip HTML generation if not needed
- Reuse dictionary objects where possible

---

## General Optimization Strategies

### 1. Limit Data Volume
- **Paragraphs:** Limit to 10-100 instead of 1000+
- **Pages:** Limit to 5-10 pages instead of entire documents
- **Terms:** Limit to 1-5 terms instead of 10+

### 2. Skip Non-Essential Operations
- Skip HTML file generation if test only checks structure
- Skip file writing if only testing in-memory operations
- Use `debug=False` to reduce logging overhead

### 3. Cache Results
- Reuse dictionary objects across tests in same class
- Check if files already exist before regenerating
- Use class-level fixtures for expensive setup

### 4. Reduce Network Calls
- Use only 1 term for lookup tests (maintains at least one lookup)
- Batch operations where possible
- Use shorter timeouts

### 5. File Operations
- Use smaller test files where possible
- Skip full file processing if testing specific features
- Reuse temporary files across tests

## Implementation Priority

1. **High Priority (Biggest Impact):**
   - `test_dictionary_annotation_workflow` (108s → ~10s)
   - `test_wikidata_id_html_output` (30s → ~15s)
   - `test_search_with_dictionary_and_make_links_IMPORTANT` (11s → ~3s)

2. **Medium Priority:**
   - `test_pdf_hyperlink_adder_ipcc` (10s → ~2s)
   - Dictionary entry creation tests (6s → ~2s each)

3. **Low Priority:**
   - Headless browser tests (requires driver changes)
   - Disambiguation tests (already relatively fast)

## Testing Principles Maintained

✅ **At least one real lookup per test** - All optimizations maintain at least one network call or real operation  
✅ **No mocks** - All tests use real implementations  
✅ **Real behavior verification** - Tests still verify actual functionality  
✅ **Reduced redundancy** - Eliminate unnecessary operations while keeping essential ones

## Expected Overall Impact

**Current total slowest 20 tests:** ~250 seconds  
**After optimizations:** ~50 seconds  
**Savings:** ~80% reduction in test time

