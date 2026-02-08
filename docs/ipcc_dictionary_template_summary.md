# IPCC Dictionary Template - Summary

## Purpose

This document summarizes the proposed template for converting IPCC glossary and acronym PDFs into structured, semantic HTML dictionaries.

## Key Documents

1. **Template Proposal**: `docs/ipcc_dictionary_template_proposal.md`
   - Complete specification of the template structure
   - Validation rules and requirements
   - Processing pipeline description
   - Testing requirements

2. **Example File**: `docs/ipcc_dictionary_template_example.html`
   - Concrete HTML example showing the template in use
   - Demonstrates all major features
   - Includes CSS styling

## Template Features

### 1. Semantic Structure
- Uses HTML5 semantic elements with `role` attributes
- Accessible and machine-readable
- Supports both `<div>` and `<dl>` structures

### 2. Metadata Section
- Dictionary-level metadata (report, annex, type, source)
- Conversion information (date, tool, entry count)
- Layout information (single/multi-column)

### 3. Entry Structure
- Term-based entries with optional components:
  - **Term** (required): The glossary term or acronym
  - **Definition** (optional): Short definition
  - **Description** (optional): Extended multi-paragraph content
  - **Abbreviation** (optional): Variant forms
  - **Cross-references** (optional): Links to related entries

### 4. Rich Content Support
- Mixed content: text, links, subscripts, superscripts
- Preserves formatting from PDF
- Handles nested HTML elements

### 5. Section Organization
- Optional section headings (A, B, C, etc.)
- Groups entries alphabetically
- Supports navigation

## Transformation Requirements

### Input Handling
- PDF-to-HTML conversion with font/coordinate preservation
- Page break handling
- Float/figure detection
- Column layout detection (single/multi-column)

### Processing Pipeline
1. Page joining
2. Layout detection
3. Section detection
4. Entry detection
5. Role assignment (font-based)
6. Structure creation
7. Validation

### Role Detection
- Uses `font_role_config.json` for font-to-role mapping
- Supports report-specific overrides
- Coordinate-based rules (x0, y0 ranges)
- Section heading detection

## Validation Rules

### Required Elements
- Root dictionary container
- Metadata section with title
- At least one entry
- Each entry must have a term

### Data Attributes
- `data-report`: "wg1", "wg2", "wg3", or "syr"
- `data-annex`: Annex identifier
- `data-annex-type`: "glossary" or "acronyms"
- `data-entry-number`: Unique integer per entry
- `data-term`: Normalized term text
- `id`: Unique entry identifier

### Content Rules
- Term text must be non-empty
- Entry IDs must be unique
- Cross-reference links must be valid
- Section letters must be A-Z

## Testing Strategy

### Test Cases
1. Single-column layout (SYR files)
2. Two-column layout (WG3 files)
3. Multi-paragraph definitions
4. Cross-references (italicized terms)
5. Section headings (alphabetical organization)
6. Mixed content (subscripts, superscripts, links)
7. Page breaks (entries spanning pages)
8. Floats/figures (inserted content)

### Validation Tests
- Structure validation
- ID uniqueness
- Cross-reference link validation
- Metadata completeness
- Content preservation

## Implementation Plan

### Phase 1: Template Review
- [ ] Review template proposal
- [ ] Approve structure and validation rules
- [ ] Identify any required changes

### Phase 2: Implementation
- [ ] Update `semantic_structure_transformer.py` to use template
- [ ] Add validation module
- [ ] Create test suite
- [ ] Update configuration files

### Phase 3: Testing
- [ ] Run tests on all 6 glossary/acronym files
- [ ] Validate output against template
- [ ] Fix any issues
- [ ] Performance testing

### Phase 4: Documentation
- [ ] Create user guide
- [ ] Document transformation process
- [ ] Provide examples
- [ ] Update existing documentation

## Benefits

1. **Standardization**: Consistent structure across all glossary/acronym files
2. **Semantic**: Machine-readable and accessible
3. **Flexible**: Supports various content types and layouts
4. **Validatable**: Clear validation rules
5. **Extensible**: Easy to add new features
6. **Maintainable**: Well-documented and tested

## Next Steps

1. **Review**: User reviews template proposal
2. **Feedback**: Incorporate any requested changes
3. **Implementation**: Begin implementation once approved
4. **Testing**: Comprehensive testing on all files
5. **Deployment**: Use template for all future conversions

## Questions for Review

1. Is the entry structure appropriate? (term, definition, description, cross-references)
2. Should we use `<dl>` or `<div>` structure? (or support both?)
3. Are the data attributes sufficient for metadata needs?
4. Are the validation rules appropriate?
5. Should we add any additional features?

## Related Files

- `scripts/glossary_processor/semantic_structure_transformer.py` - Current transformer
- `scripts/glossary_processor/font_role_config.json` - Role detection config
- `scripts/glossary_processor/entry_detector.py` - Entry detection logic
- `scripts/glossary_processor/page_joiner.py` - Page joining logic
- `docs/glossary_semantic_structure_transformation.md` - Current implementation docs








