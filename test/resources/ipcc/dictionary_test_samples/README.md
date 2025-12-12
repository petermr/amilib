# IPCC Dictionary Test Samples

This directory contains small test HTML files extracted from actual PDF-to-HTML conversions. These samples are used to test the dictionary template validation and transformation logic.

## Test Files

### 1. `wg3_annex_vi_sample_3_entries.html`
- **Source**: WG3 Annex VI (Acronyms)
- **Layout**: Two-column
- **Content**: 3 simple acronym entries
- **Features**: Basic term/definition structure
- **Use Case**: Basic structure validation

### 2. `wg3_annex_vi_with_crossref.html`
- **Source**: WG3 Annex VI (Acronyms)
- **Layout**: Two-column
- **Content**: 2 entries with cross-references
- **Features**: Cross-reference spans (italicized terms)
- **Use Case**: Cross-reference handling

### 3. `wg3_annex_vi_with_mixed_content.html`
- **Source**: WG3 Annex VI (Acronyms)
- **Layout**: Two-column
- **Content**: 3 entries with mixed content
- **Features**: Subscripts (CO₂, N₂O), extended definitions
- **Use Case**: Mixed content preservation

### 4. `syr_annex_i_sample_single_column.html`
- **Source**: SYR Annex I (Glossary)
- **Layout**: Single-column
- **Content**: 2 entries (metadata-like)
- **Features**: Single-column layout, different structure
- **Use Case**: Single-column layout handling

### 5. `wg3_annex_vi_with_italics_hyperlinks.html`
- **Source**: WG3 Annex VI (Acronyms)
- **Layout**: Two-column
- **Content**: 4 entries with italicized cross-references
- **Features**: Italicized terms (`<em>`) that might be converted to hyperlinks, mixed content with text/italic/text patterns
- **Use Case**: Testing italicized cross-reference handling and potential hyperlink conversion

## Test Coverage

These samples cover:
- ✅ Basic structure validation
- ✅ Entry ID uniqueness
- ✅ Required data attributes
- ✅ Term and definition content
- ✅ Cross-reference handling
- ✅ Mixed content (subscripts, superscripts)
- ✅ Single vs. multi-column layouts
- ✅ CSS stylesheet presence
- ✅ Italicized cross-references (potential hyperlinks)

## Usage

These test files are used by:
- `test/test_ipcc_dictionary_template.py` - Template validation tests
- `scripts/glossary_processor/dictionary_template_validator.py` - Validator tool

## Adding New Test Samples

When adding new test samples:
1. Extract small subsets (3-5 entries) from actual conversions
2. Include representative examples of different features
3. Document the source and features in this README
4. Ensure the file validates against the template

