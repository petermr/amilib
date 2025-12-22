# IPCC Dictionary Template Tests

## Overview

Comprehensive test suite for validating IPCC dictionary template structure and transformation logic.

## Test Structure

### Test Files

1. **`test/test_ipcc_dictionary_template.py`**
   - Template validation tests
   - Transformation tests
   - Content preservation tests

2. **`scripts/glossary_processor/dictionary_template_validator.py`**
   - Standalone validator tool
   - Detailed validation reports
   - Command-line interface

### Test Samples

Located in `test/resources/ipcc/dictionary_test_samples/`:

- `wg3_annex_vi_sample_3_entries.html` - Basic structure
- `wg3_annex_vi_with_crossref.html` - Cross-references
- `wg3_annex_vi_with_mixed_content.html` - Mixed content
- `syr_annex_i_sample_single_column.html` - Single-column layout

## Test Categories

### 1. Structure Validation Tests

#### `test_wg3_annex_vi_basic_structure`
- Validates basic dictionary structure
- Checks for dictionary container
- Verifies entry structure
- Ensures terms and definitions are present

#### `test_entry_id_uniqueness`
- Validates entry IDs are unique
- Checks all entries have IDs
- Prevents duplicate IDs

#### `test_required_data_attributes`
- Validates required data attributes
- Checks `data-report` and `data-annex`
- Validates report values (wg1/wg2/wg3/syr)

### 2. Content Validation Tests

#### `test_term_and_definition_content`
- Ensures terms have non-empty content
- Ensures definitions have non-empty content
- Validates text extraction

#### `test_wg3_annex_vi_cross_references`
- Tests cross-reference detection
- Validates cross-reference spans
- Checks cross-reference content

#### `test_wg3_annex_vi_mixed_content`
- Tests subscript preservation
- Tests superscript preservation
- Validates mixed content in terms and definitions

### 3. Layout Tests

#### `test_syr_annex_i_single_column`
- Tests single-column layout handling
- Validates SYR-specific structure
- Ensures compatibility with different layouts

### 4. CSS/Styling Tests

#### `test_css_styles_present`
- Validates CSS stylesheet presence
- Checks role-based styles
- Ensures proper styling structure

### 5. Transformation Tests

#### `test_entry_extraction`
- Tests entry extraction from HTML
- Validates term/definition extraction
- Checks text content preservation

#### `test_mixed_content_preservation`
- Tests preservation of HTML elements (sub, sup, etc.)
- Validates nested content structure
- Ensures no data loss

## Running Tests

### Run All Tests
```bash
python -m pytest test/test_ipcc_dictionary_template.py -v
```

### Run Specific Test
```bash
python -m pytest test/test_ipcc_dictionary_template.py::IPCCDictionaryTemplateTest::test_wg3_annex_vi_basic_structure -v
```

### Run Validator Tool
```bash
python scripts/glossary_processor/dictionary_template_validator.py test/resources/ipcc/dictionary_test_samples/wg3_annex_vi_sample_3_entries.html
```

## Validation Rules

### Required Elements
- Root `<html>` element
- Dictionary container (`div[@class="glossary"]` or `div[@role="ipcc_dictionary"]`)
- At least one entry (`div[@class="entry"]`)
- Each entry must have a term (`div[@role="term"]`)

### Required Attributes
- Dictionary container: `data-report`, `data-annex`
- Entry: `id` (unique)

### Optional Attributes
- Entry: `data-term`, `data-entry-number`, `data-has-definition`, etc.

### Content Rules
- Terms must have non-empty text content
- Definitions should have non-empty text content (warning if missing)
- Entry IDs must be unique
- Cross-reference links should reference valid entry IDs

## Test Results

All 11 tests currently pass:
- ✅ Basic structure validation
- ✅ Entry ID uniqueness
- ✅ Required data attributes
- ✅ Term and definition content
- ✅ Cross-reference handling
- ✅ Mixed content preservation
- ✅ Single-column layout
- ✅ CSS stylesheet presence
- ✅ Detailed validation report
- ✅ Entry extraction
- ✅ Mixed content preservation

## Adding New Tests

When adding new tests:

1. **Create test sample** in `test/resources/ipcc/dictionary_test_samples/`
2. **Add test method** to `IPCCDictionaryTemplateTest` or `IPCCDictionaryTransformationTest`
3. **Document test** in this file
4. **Run tests** to ensure they pass
5. **Update README** in test_samples directory if needed

## Future Test Cases

Potential additional test cases:

1. **Page break handling**
   - Test entries spanning multiple pages
   - Validate page break removal

2. **Float/figure handling**
   - Test entries with inserted figures
   - Validate float detection

3. **Section headings**
   - Test alphabetical section organization
   - Validate section heading detection

4. **Multi-paragraph definitions**
   - Test extended descriptions
   - Validate paragraph structure

5. **Abbreviation variants**
   - Test multiple abbreviation forms
   - Validate variant handling

6. **Cross-reference link validation**
   - Test internal link resolution
   - Validate broken link detection

7. **Performance tests**
   - Test with large files (500+ entries)
   - Validate processing time

8. **Edge cases**
   - Empty entries
   - Missing terms
   - Special characters
   - Unicode content







