# Acronym Parser Implementation

## Summary

Implemented business logic to parse acronym/abbreviation entries where the definition often starts with the non-abbreviated term. The parser extracts the full term from the definition and reorganizes entries so that:
- The **full term** becomes the main term
- The **acronym/abbreviation** becomes an abbreviation field

## Implementation

### File: `scripts/glossary_processor/acronym_parser.py`

**Key Features:**
1. **Acronym Detection**: Identifies acronyms/abbreviations (e.g., "IPCC", "AUM", "NDC", "GHG")
2. **Full Term Extraction**: Extracts full terms from definitions using first-letter matching
3. **Entry Reorganization**: Restructures entries to have full term as term and acronym as abbreviation
4. **Sentence Boundary Detection**: Attempts to stop at sentence boundaries (periods, exclamation marks)

**Main Methods:**
- `parse_entry()`: Parses a single entry
- `parse_dictionary()`: Parses all entries in a dictionary
- `_extract_full_term()`: Extracts full term from definition
- `_could_be_full_term()`: Checks if a phrase could be the full term for an acronym
- `_is_acronym()`: Detects if text looks like an acronym
- `_reorganize_entry()`: Reorganizes entry structure

**Example Transformations:**

**Before:**
```html
<div class="entry">
  <div role="term">AUM</div>
  <div role="definition">assets under management</div>
</div>
```

**After:**
```html
<div class="entry" data-term="assets under management" data-has-abbreviation="true">
  <div role="term">
    <span class="role-term">assets under management</span>
    <span role="abbreviation" class="abbreviation" data-variant="AUM">AUM</span>
  </div>
  <div role="definition"></div>
</div>
```

## Integration

The parser is integrated into `semantic_structure_transformer.py`:
- Automatically runs for acronym entries (`entry_type == 'acronyms'`)
- Processes entries after semantic structure is created
- Preserves role attributes and CSS classes

## Test Coverage

**File**: `test/test_acronym_parser.py`

**Test Cases:**
1. ✅ Simple acronym parsing (AUM -> "assets under management")
2. ✅ Acronym with extended definition (NDC with additional text)
3. ✅ IPCC acronym (Intergovernmental Panel on Climate Change)
4. ✅ Full term detection logic
5. ✅ Acronym detection logic
6. ✅ Dictionary-wide parsing

**Test Sample**: `test/resources/ipcc/dictionary_test_samples/wg3_annex_vi_acronym_examples.html`

## Known Limitations

1. **Sentence Boundary Detection**: Currently extracts full terms but may include text beyond sentence boundaries in some cases (e.g., "Nationally Determined Contribution. A climate action" instead of stopping at the period)
2. **Special Cases**: Handles common patterns like "GHG" -> "greenhouse gas" but may need additional special cases for edge cases
3. **Stop Words**: Uses a predefined list of stop words; may need expansion for domain-specific terms

## Usage

### Standalone
```bash
python scripts/glossary_processor/acronym_parser.py input.html output.html
```

### Integrated
The parser is automatically called by `SemanticStructureTransformer` when processing acronym entries.

## Output

Parsed dictionaries are saved to `temp/test/acronym_parser/` for review.

## Future Improvements

1. Improve sentence boundary detection to stop more accurately at periods
2. Add more special case handling for common acronym patterns
3. Support for multi-word acronyms with complex patterns
4. Configuration file for custom acronym patterns

