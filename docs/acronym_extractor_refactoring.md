# Acronym Extractor Refactoring

## Summary

Extracted reusable business logic from `AcronymParser` into a standalone `AcronymExtractor` class in `amilib`. This separation allows the business logic to be used independently of HTML/XML processing.

## Architecture

### Before
- All logic (business + HTML manipulation) in `AcronymParser`
- Tightly coupled to HTML/XML structures
- Not reusable outside of HTML context

### After
- **Pure Business Logic**: `AcronymExtractor` in `amilib/acronym_extractor.py`
  - No HTML/XML dependencies
  - Can be used with any text processing pipeline
  - Fully testable independently
  
- **HTML-Specific Logic**: `AcronymParser` in `scripts/glossary_processor/acronym_parser.py`
  - Uses `AcronymExtractor` for business logic
  - Handles HTML structure manipulation
  - Thin wrapper around extractor

## Classes

### `AcronymExtractor` (amilib)

**Location**: `amilib/acronym_extractor.py`

**Purpose**: Pure business logic for acronym extraction

**Key Methods**:
- `is_acronym(text: str) -> bool`: Detect if text is an acronym
- `extract_full_term(acronym: str, definition: str) -> Tuple[Optional[str], str]`: Extract full term from definition
- `normalize_term(term: str) -> str`: Normalize term for identifiers
- `extract_acronym_info(acronym: str, definition: str) -> Optional[dict]`: Convenience method returning structured data
- `_could_be_full_term(acronym: str, potential_full_term: str) -> bool`: Internal method for matching logic

**Dependencies**: None (pure Python, uses only `re` and `typing`)

**Usage Example**:
```python
from amilib.acronym_extractor import AcronymExtractor

# Detect acronym
if AcronymExtractor.is_acronym("IPCC"):
    # Extract full term
    full_term, remaining = AcronymExtractor.extract_full_term(
        "IPCC", "Intergovernmental Panel on Climate Change"
    )
    print(f"Full term: {full_term}")
```

### `AcronymParser` (scripts)

**Location**: `scripts/glossary_processor/acronym_parser.py`

**Purpose**: HTML-specific acronym parsing

**Key Methods**:
- `parse_entry(entry_elem: ET.Element, entry_type: str) -> bool`: Parse HTML entry
- `parse_dictionary(html_elem: ET.Element, entry_type: str) -> int`: Parse all entries in dictionary
- `_reorganize_entry(...)`: HTML structure manipulation

**Dependencies**: 
- `AcronymExtractor` (for business logic)
- `lxml.etree` (for HTML manipulation)
- Dictionary template constants

## Benefits

1. **Reusability**: `AcronymExtractor` can be used in any context, not just HTML processing
2. **Testability**: Business logic can be tested independently without HTML fixtures
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new extractors or parsers using the same business logic
5. **Library Integration**: `AcronymExtractor` is ready to be added to amilib's core utilities

## Test Coverage

### `test/test_acronym_extractor.py`
- 8 tests covering pure business logic
- No HTML dependencies
- Fast execution

### `test/test_acronym_parser.py`
- 6 tests covering HTML integration
- Uses `AcronymExtractor` internally
- Tests HTML structure manipulation

## Migration Path

The refactoring maintains backward compatibility:
- `AcronymParser` API unchanged
- Existing code continues to work
- Internal implementation uses `AcronymExtractor`

## Future Enhancements

1. Add `AcronymExtractor` to amilib's public API
2. Create additional extractors (e.g., for different languages)
3. Add configuration options (custom stop words, patterns)
4. Support for multi-word acronyms with complex patterns

