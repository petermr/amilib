# Encyclopedia Checkbox Implementation Proposal

**Date**: 2025-12-02  
**Status**: Proposal - Business Logic Not Yet Implemented

## Overview

This document proposes the business logic implementation for checkbox functionality in encyclopedia entries. The tests have been written (TDD approach) and are ready to guide implementation.

## Requirements Summary

Each encyclopedia entry should have checkboxes for:
1. **Hide Entry** - Multiple reasons:
   - Missing Wikipedia (checked by default)
   - General term (unchecked by default)
   - User selected (unchecked by default)
2. **Merge Synonyms** - For entries with same Wikidata ID
3. **Disambiguation Selector** - For disambiguation pages (dropdown, not checkbox)

## Proposed Business Logic

### 1. Checkbox Generation in `create_wiki_normalized_html()`

**Location**: `amilib/ami_encyclopedia.py::create_wiki_normalized_html()`

**Proposed Changes**:

```python
# PSEUDOCODE - DO NOT IMPLEMENT YET

def create_wiki_normalized_html(self) -> str:
    # ... existing code ...
    
    for wikidata_id, group in synonym_groups.items():
        entry_div = ET.SubElement(encyclopedia_div, "div")
        entry_div.attrib["role"] = "ami_entry"
        
        # Generate entry ID
        entry_id = self._generate_entry_id(group)
        entry_div.attrib["data-entry-id"] = entry_id
        
        # Add checkboxes BEFORE other content
        self._add_entry_checkboxes(entry_div, group, entry_id)
        
        # ... rest of existing code ...
```

### 2. Entry ID Generation Method

**Proposed Method**: `_generate_entry_id(group: Dict) -> str`

**Logic**:
- Primary: Use `wikidata_id` if available (e.g., "Q37836")
- Secondary: Use `canonical_term` if no Wikidata ID
- Fallback: Generate unique ID (e.g., "entry_001", "entry_002")

**Implementation Notes**:
- Must be unique within the encyclopedia
- Should be stable (same entry always gets same ID)
- Used for checkbox `data-entry-id` attribute

### 3. Checkbox Addition Method

**Proposed Method**: `_add_entry_checkboxes(entry_div, group: Dict, entry_id: str) -> None`

**Logic**:

```python
# PSEUDOCODE - DO NOT IMPLEMENT YET

def _add_entry_checkboxes(self, entry_div, group: Dict, entry_id: str):
    # Create checkbox container div
    checkbox_container = ET.SubElement(entry_div, "div")
    checkbox_container.attrib["class"] = "entry-checkboxes"
    
    # 1. Missing Wikipedia checkbox
    if not group.get('wikipedia_url'):
        self._add_hide_checkbox(
            checkbox_container, 
            entry_id, 
            reason="missing_wikipedia",
            checked=True,  # Checked by default
            label="Hide (missing Wikipedia)"
        )
    
    # 2. General term checkbox (always present)
    self._add_hide_checkbox(
        checkbox_container,
        entry_id,
        reason="general_term",
        checked=False,  # Unchecked by default
        label="Hide (too general)"
    )
    
    # 3. Merge synonyms checkbox (if has synonyms)
    if len(group.get('synonyms', [])) > 1:
        self._add_merge_checkbox(
            checkbox_container,
            entry_id,
            group.get('wikidata_id'),
            checked=True  # Checked if synonyms should be merged
        )
    
    # 4. Disambiguation selector (if disambiguation page)
    if self._is_disambiguation_page(group.get('wikipedia_url', '')):
        self._add_disambiguation_selector(
            checkbox_container,
            entry_id,
            group.get('wikipedia_url', '')
        )
```

### 4. Individual Checkbox Creation Methods

#### 4.1 Hide Checkbox

**Proposed Method**: `_add_hide_checkbox(container, entry_id: str, reason: str, checked: bool, label: str) -> None`

**HTML Structure**:
```html
<div class="entry-checkbox-wrapper">
    <input 
        type="checkbox" 
        class="entry-hide-checkbox" 
        data-entry-id="Q37836"
        data-reason="missing_wikipedia"
        id="hide_Q37836_missing_wikipedia"
        checked
    />
    <label for="hide_Q37836_missing_wikipedia">Hide (missing Wikipedia)</label>
</div>
```

**Attributes**:
- `type="checkbox"` - Required
- `class="entry-hide-checkbox"` - Required for CSS/JS selection
- `data-entry-id` - Entry identifier (required)
- `data-reason` - One of: "missing_wikipedia", "general_term", "user_selected" (required)
- `id` - Unique ID for label association
- `checked` - Present if checked by default

#### 4.2 Merge Synonyms Checkbox

**Proposed Method**: `_add_merge_checkbox(container, entry_id: str, wikidata_id: str, checked: bool) -> None`

**HTML Structure**:
```html
<div class="entry-checkbox-wrapper">
    <input 
        type="checkbox" 
        class="merge-synonyms-checkbox" 
        data-entry-id="Q37836"
        data-wikidata-id="Q37836"
        id="merge_Q37836"
        checked
    />
    <label for="merge_Q37836">Merge synonyms</label>
</div>
```

**Attributes**:
- `type="checkbox"` - Required
- `class="merge-synonyms-checkbox"` - Required
- `data-entry-id` - Entry identifier
- `data-wikidata-id` - Wikidata ID for grouping
- `id` - Unique ID for label association
- `checked` - Present if synonyms should be merged

#### 4.3 Disambiguation Selector

**Proposed Method**: `_add_disambiguation_selector(container, entry_id: str, wikipedia_url: str) -> None`

**HTML Structure**:
```html
<div class="disambiguation-wrapper">
    <label for="disambiguation_Q37836">Select Wikipedia page:</label>
    <select 
        class="disambiguation-selector" 
        data-entry-id="Q37836"
        id="disambiguation_Q37836"
    >
        <option value="">-- Select --</option>
        <option value="https://en.wikipedia.org/wiki/Page1" data-wikidata="Q1">Page 1</option>
        <option value="https://en.wikipedia.org/wiki/Page2" data-wikidata="Q2">Page 2</option>
    </select>
</div>
```

**Note**: This is a `<select>` element, not a checkbox, but grouped with checkboxes for user interaction.

### 5. Detection Methods

#### 5.1 Missing Wikipedia Detection

**Proposed Method**: `_has_wikipedia_url(group: Dict) -> bool`

**Logic**:
- Return `True` if `group.get('wikipedia_url')` exists and is not empty
- Return `False` otherwise

#### 5.2 Disambiguation Page Detection

**Proposed Method**: `_is_disambiguation_page(wikipedia_url: str) -> bool`

**Logic**:
- Check if URL contains "(disambiguation)" (case-insensitive)
- Check if URL path ends with "_(disambiguation)"
- Return `True` if disambiguation page detected

**Implementation Notes**:
- May need to fetch page content to detect disambiguation template
- For initial implementation, URL pattern matching may suffice

### 6. Checkbox Container Structure

**Proposed HTML Structure**:
```html
<div role="ami_entry" data-entry-id="Q37836" ...>
    <!-- Checkbox container at the start -->
    <div class="entry-checkboxes">
        <div class="entry-checkbox-wrapper">
            <input type="checkbox" ... />
            <label>...</label>
        </div>
        <!-- More checkboxes as needed -->
    </div>
    
    <!-- Rest of entry content -->
    <a href="...">...</a>
    <ul class="synonym_list">...</ul>
    ...
</div>
```

### 7. Integration Points

#### 7.1 Entry ID Generation

**Location**: Called from `create_wiki_normalized_html()`

**Method**: `_generate_entry_id(group: Dict) -> str`

**Dependencies**: None

#### 7.2 Checkbox Addition

**Location**: Called from `create_wiki_normalized_html()` for each entry

**Method**: `_add_entry_checkboxes(entry_div, group: Dict, entry_id: str)`

**Dependencies**:
- `_generate_entry_id()` - For entry identification
- `_has_wikipedia_url()` - For missing Wikipedia detection
- `_is_disambiguation_page()` - For disambiguation detection
- `_add_hide_checkbox()` - For hide checkboxes
- `_add_merge_checkbox()` - For merge checkboxes
- `_add_disambiguation_selector()` - For disambiguation selector

### 8. Style Guide Compliance

**Requirements**:
- ✅ Use absolute imports: `from amilib.util import Util`
- ✅ No mocks in tests (already done)
- ✅ Use `Path()` constructor with multiple arguments
- ✅ Use `Resources.TEMP_DIR` for temporary files
- ✅ Empty `__init__.py` files
- ✅ No business logic in tests (tests only verify)

### 9. Implementation Order

1. **Entry ID Generation** (`_generate_entry_id`)
   - Simple method, no dependencies
   - Foundation for all checkbox functionality

2. **Detection Methods** (`_has_wikipedia_url`, `_is_disambiguation_page`)
   - Simple boolean checks
   - Used by checkbox addition logic

3. **Individual Checkbox Methods** (`_add_hide_checkbox`, `_add_merge_checkbox`, `_add_disambiguation_selector`)
   - Create HTML elements
   - Add attributes and labels
   - Can be tested independently

4. **Checkbox Container Method** (`_add_entry_checkboxes`)
   - Orchestrates checkbox addition
   - Calls individual checkbox methods
   - Determines which checkboxes to add

5. **Integration** (modify `create_wiki_normalized_html()`)
   - Add checkbox generation to HTML creation
   - Ensure checkboxes appear before entry content
   - Test with real encyclopedia data

### 10. Testing Strategy

**Tests Already Written**:
- ✅ `test_html_contains_hide_checkboxes` - Basic checkbox presence
- ✅ `test_checkbox_structure_and_attributes` - Structure verification
- ✅ `test_checkbox_data_entry_id_matches_entry` - ID matching
- ✅ `test_checkbox_labels_exist` - Label association
- ✅ `test_checkbox_reason_attributes` - Reason validation
- ✅ `test_checkbox_positioning_in_entry` - Position verification
- ✅ `test_multiple_checkbox_types_per_entry` - Multiple types
- ✅ `test_checkbox_initial_state` - Initial checked state

**Test Execution**:
- Run tests before implementation (should fail)
- Implement one method at a time
- Run tests after each method
- Make tests pass incrementally

### 11. Open Questions

1. **Disambiguation Options**: How to get list of disambiguation options?
   - Fetch from Wikipedia API?
   - Parse disambiguation page HTML?
   - User provides list?

2. **Checkbox Persistence**: How to save checkbox state?
   - JavaScript + localStorage?
   - Server-side save to metadata file?
   - Both?

3. **Merge Synonyms Logic**: When should merge checkbox be checked?
   - Always if synonyms exist?
   - User preference?
   - Based on similarity score?

4. **CSS Styling**: Where to add CSS for checkboxes?
   - Inline styles?
   - External CSS file?
   - Style tag in HTML head?

## Next Steps

1. ✅ Tests written and ready
2. ⏳ Review and approve proposal
3. ⏳ Implement entry ID generation
4. ⏳ Implement detection methods
5. ⏳ Implement individual checkbox methods
6. ⏳ Implement checkbox container method
7. ⏳ Integrate into HTML generation
8. ⏳ Run tests and verify
9. ⏳ Generate test HTML file for browser inspection

## Notes

- All proposed methods follow style guide requirements
- Methods are focused and testable
- Implementation can be done incrementally
- Tests will guide implementation and verify correctness

