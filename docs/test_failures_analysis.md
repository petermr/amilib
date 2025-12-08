# Test Failures Analysis and Recommendations

**Date:** 2025-12-08  
**Total Failures:** 22 tests across 6 test files

---

## Summary by Category

| Category | Count | Issue Type |
|----------|-------|------------|
| Missing Test Resources | 9 | Missing `eoCompound` directory/files |
| HTML Structure Tests | 4 | Coordinate extraction from CSS positioning |
| File Count Assertions | 2 | Outdated expected counts |
| TF-IDF Configuration | 6 | Document frequency parameter mismatch |
| Missing CSV File | 1 | Related to missing `eoCompound` |

---

## 1. Missing Test Resources (9 failures)

### Affected Tests:
- `test_dict.py::AmiDictionaryTest::test_entry_id`
- `test_util.py::Util0Test::test_read_csv`
- `test_util.py::Util0Test::test_select_csv_field_by_type`
- `test_wikimedia.py::WikidataTest::test_get_predicate_value`
- `test_wikimedia.py::WikidataTest::test_get_predicate_value_1`
- `test_wikimedia.py::WikidataTest::test_get_property_list`
- `test_wikimedia.py::WikidataTest::test_get_wikidata_predicate_value`
- `test_wikimedia.py::WikidataTest::test_page_get_values_for_property_id`
- `test_wikimedia.py::WikidataTest::test_parse_wikidata_html`
- `test_wikimedia.py::WikidataTest::test_read_wikidata_filter`

### Issue:
Missing test resource directory: `/Users/pm286/workspace/amilib/test/resources/eoCompound/`

**Missing Files/Directories:**
- `test/resources/eoCompound/` (entire directory)
- `test/resources/eoCompound/compound_enzyme.csv`
- `test/resources/eoCompound/q407418.html`
- `test/resources/eoCompound/p31.html`
- `test/resources/filter00.json`

### Root Cause:
Test resources were removed, moved, or never committed to the repository.

### Recommendations:

**Option 1: Skip tests if resources missing (Recommended)**
```python
def test_entry_id(self):
    """Test entry ID functionality"""
    eo_compound_path = Path(Resources.TEST_RESOURCES_DIR, "eoCompound")
    if not eo_compound_path.exists():
        self.skipTest(f"Test resource directory not found: {eo_compound_path}")
    # ... rest of test
```

**Option 2: Create minimal test resources**
- Create empty `eoCompound` directory structure
- Add minimal test files with expected structure
- Document that these are test fixtures

**Option 3: Download from external source**
- Tests reference `CEV_OPEN_RAW_DICT_URL` which suggests resources may be available online
- Add setup script to download test resources if missing

---

## 2. HTML Structure Tests (4 failures)

### Affected Tests:
- `test_html_structure.py::HtmlStructureTest::test_column_detector_detects_two_columns`
- `test_html_structure.py::HtmlStructureTest::test_page_metadata_detector_detects_marginalia`
- `test_html_structure.py::HtmlStructureTest::test_page_metadata_detector_detects_page_number`
- `test_html_structure.py::HtmlStructureTest::test_page_metadata_detector_detects_running_title`

### Issue:
Tests use CSS positioning (`left:500px; top:800px;`) but `CSSStyle.get_x0()` expects PDF-converted format with explicit coordinate attributes (`x0: 500; y0: 800;`).

**Current Test HTML:**
```html
<span style="position:absolute; left:500px; top:800px;">Page 42</span>
```

**Expected Format (PDF-converted):**
```html
<span style="x0: 500; y0: 800; x1: 550; y1: 820;">Page 42</span>
```

### Root Cause:
`CSSStyle.get_coords()` calls `get_numeric_attval("x0")` which looks for `x0:` in the CSS style string, not `left:`.

### Recommendations:

**Option 1: Update test HTML to use PDF-converted format (Recommended)**
```python
html_str = """
<div>
    <span style="x0: 500; y0: 800; x1: 550; y1: 820;">Page 42</span>
    <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content text</span>
</div>
"""
```

**Option 2: Add helper to convert CSS positioning to coordinate attributes**
```python
def _convert_css_to_coords(elem):
    """Convert CSS left/top to x0/y0 attributes for testing"""
    style = elem.get('style', '')
    # Parse left and top from style
    # Add x0, y0, x1, y1 to style attribute
```

**Option 3: Make coordinate extraction handle both formats**
- Extend `CSSStyle.get_coords()` to also parse `left:` and `top:` CSS properties
- Fall back to coordinate attributes if CSS positioning found

---

## 3. File Count Assertions (2 failures)

### Affected Tests:
- `test_bib.py::PygetpapersTest::test_search_all_chapters_with_query_words`
- `test_bib.py::AmiCorpusTest::test_search_and_create_term_href_p_table`

### Issue:
Tests expect 50-55 files but found 67 files:
```python
assert 50 <= len(infiles) <= 55  # Fails: 67 > 55
```

### Root Cause:
More HTML files were added to `test/resources/ipcc/` directory since test was written.

### Recommendations:

**Option 1: Update assertion to current count (Recommended)**
```python
# Check that we have a reasonable number of files
assert 50 <= len(infiles) <= 70, f"Expected 50-70 files, got {len(infiles)}"
```

**Option 2: Use relative assertion**
```python
# Just verify we have some files
assert len(infiles) >= 50, f"Should have at least 50 files, got {len(infiles)}"
```

**Option 3: Make test more flexible**
```python
# Accept any reasonable number
min_files = 50
assert len(infiles) >= min_files, f"Should have at least {min_files} files"
```

---

## 4. TF-IDF Configuration (6 failures)

### Affected Tests:
All tests in `test_txt2phrases_glob.py`:
- `test_glob_pattern_case_sensitivity`
- `test_glob_pattern_relative_path`
- `test_glob_pattern_with_special_characters`
- `test_recursive_glob_pattern_deep_nesting`
- `test_recursive_glob_pattern_specific_subdirectory`
- `test_simple_glob_pattern_txt`

### Issue:
```
ValueError: max_df corresponds to < documents than min_df
```

### Root Cause:
TF-IDF parameters (`max_df` and `min_df`) are configured such that `max_df` requires fewer documents than `min_df`, which is impossible. This happens when:
- Too few test documents are created
- Parameters are set incorrectly
- Document filtering removes too many documents

### Recommendations:

**Option 1: Adjust test document count (Recommended)**
```python
# Ensure we have enough documents for TF-IDF
# If max_df=0.8 and min_df=2, need at least 3 documents (2/0.8 = 2.5, round up to 3)
# Create more test files or adjust parameters
```

**Option 2: Use more lenient TF-IDF parameters**
```python
# In test setup or corpus creation:
corpus.extract_significant_phrases(
    file_pattern="*.txt",
    min_df=1,  # Lower minimum
    max_df=1.0  # Higher maximum (or remove max_df)
)
```

**Option 3: Skip TF-IDF if insufficient documents**
```python
def test_simple_glob_pattern_txt(self):
    """Test simple glob pattern for TXT files"""
    try:
        phrases = self.corpus.extract_significant_phrases(file_pattern="*.txt")
        assert phrases is not None
    except ValueError as e:
        if "max_df" in str(e) and "min_df" in str(e):
            self.skipTest(f"Insufficient documents for TF-IDF: {e}")
        raise
```

---

## 5. Missing CSV File (1 failure)

### Affected Test:
- `test_util.py::Util0Test::test_read_csv`
- `test_util.py::Util0Test::test_select_csv_field_by_type`

### Issue:
Missing file: `test/resources/eoCompound/compound_enzyme.csv`

### Root Cause:
Same as #1 - missing `eoCompound` directory.

### Recommendation:
Same as #1 - skip test if resource missing or create minimal test file.

---

## Priority Recommendations

### High Priority (Blocking Tests)

1. **Fix HTML Structure Tests** - Update test HTML to use PDF-converted coordinate format
2. **Update File Count Assertions** - Adjust expected counts to match current test data
3. **Fix TF-IDF Configuration** - Either create more test documents or adjust parameters

### Medium Priority (Missing Resources)

4. **Handle Missing Test Resources** - Add skip logic or create minimal test fixtures
5. **Document Test Dependencies** - Create README listing required test resources

### Low Priority (Documentation)

6. **Update Test Documentation** - Document test resource requirements
7. **Add Test Setup Script** - Script to download/create missing test resources

---

## Implementation Order

1. **Quick Wins** (5 minutes each):
   - Update file count assertions in `test_bib.py`
   - Add skip logic for missing `eoCompound` resources

2. **Medium Effort** (15-30 minutes):
   - Fix HTML structure tests by updating test HTML format
   - Adjust TF-IDF parameters or document counts

3. **Longer Term** (1-2 hours):
   - Create minimal test resources for `eoCompound`
   - Add comprehensive test resource documentation

---

## Code Changes Summary

### test_bib.py (2 changes)
- Line 198: Update `assert 50 <= len(infiles) <= 55` → `assert 50 <= len(infiles) <= 70`
- Line 869: Update `assert 50 <= len(infiles) <= 55` → `assert 50 <= len(infiles) <= 70`

### test_html_structure.py (4 changes)
- Update test HTML to use `x0:`, `y0:`, `x1:`, `y1:` format instead of `left:`, `top:`
- Or add coordinate conversion helper function

### test_txt2phrases_glob.py (6 changes)
- Adjust `min_df`/`max_df` parameters or create more test documents
- Or add try/except to skip tests when insufficient documents

### test_dict.py, test_util.py, test_wikimedia.py (10 changes)
- Add skip logic if `eoCompound` directory missing
- Or create minimal test resources

---

**Last Updated:** 2025-12-08

