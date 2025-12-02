# Encyclopedia Hide and Sort Requirements

**Date**: 2025-12-01  
**Status**: Requirements Document

## Overview

Enhance encyclopedia creation to support human interaction for:
1. Collapsing entries with same Wikidata ID but different case variants
2. Handling disambiguation pages (user selects target Wikipedia page)
3. Merging synonyms with same Wikidata ID into single HTML list
4. Hiding entries (missing Wikipedia pages, general terms, user-selected)
5. Saving list of user actions with system date
6. Recording metadata (creation, edits, actions)
7. Sorting entries (alphabetically and by importance)

## Requirements

### 1. Case-Insensitive Wikidata ID Collapse

**Requirement**: When terms vary in case but have the same Wikidata ID, collapse them into a single entry

**Implementation Details**:
- During synonym aggregation, treat terms with same Wikidata ID as synonyms regardless of case
- Example: "Greenhouse Gas" and "greenhouse gas" with same Wikidata ID → single entry
- Preserve all case variant terms as synonyms in the collapsed entry
- Use canonical term (preferably the most common or first encountered variant)

**Current Behavior**: 
- `aggregate_synonyms()` already groups by Wikidata ID in `normalize_by_wikidata_id()`
- Terms with same Wikidata ID are already collapsed
- Need to ensure case variants are properly preserved in synonyms list

**Implementation**:
- When aggregating synonyms, collect all case variants of terms
- Store all case variants in synonyms list (not just normalized versions)
- Choose canonical term using `_get_canonical_term()` method (prefers non-lowercase variants)
- Ensure `_normalize_terms()` preserves case variants for display
- Current `aggregate_synonyms()` already groups by Wikidata ID, but need to verify case variants are preserved

**Code Location**:
- `aggregate_synonyms()` in `amilib/ami_encyclopedia.py` (line 277)
- `_normalize_terms()` currently uses `set()` which may deduplicate case variants
- Need to ensure case variants are preserved in synonyms list

**Example**:
```python
# Input entries:
# Entry 1: term="Greenhouse Gas", wikidata_id="Q37836"
# Entry 2: term="greenhouse gas", wikidata_id="Q37836"
# Entry 3: term="GREENHOUSE GAS", wikidata_id="Q37836"

# Output: Single entry with:
# - canonical_term: "Greenhouse Gas" (first encountered or most common)
# - synonyms: ["Greenhouse Gas", "greenhouse gas", "GREENHOUSE GAS"]
# - wikidata_id: "Q37836"
```

### 2. Human Interaction - Entry Checkboxes

**Requirement**: Add checkboxes to each entry for user operations

**Checkbox Types** (each entry may have multiple checkboxes):

1. **Hide Entry Checkbox**:
   - Hide missing Wikipedia pages (entries without Wikipedia URL)
   - Hide general terms (user-determined)
   - Hide any entry (user-selected)

2. **Disambiguation Selection**:
   - For disambiguation pages, allow user to select target Wikipedia page
   - Dropdown or selection mechanism to choose from disambiguation options
   - Record selected page in metadata

3. **Merge Synonyms Checkbox**:
   - For synonyms with same Wikidata ID, checkbox to confirm/control merging
   - Display merged synonyms in single HTML list

**HTML Structure**:
```html
<div role="ami_entry" data-entry-id="entry_001" ...>
    <!-- Hide checkbox -->
    <input type="checkbox" class="entry-hide-checkbox" data-entry-id="entry_001" data-reason="missing_wikipedia">
    <label>Hide (missing Wikipedia)</label>
    
    <!-- Disambiguation selector (if applicable) -->
    <select class="disambiguation-selector" data-entry-id="entry_001">
        <option value="">Select Wikipedia page...</option>
        <option value="https://en.wikipedia.org/wiki/Page1">Page 1</option>
        <option value="https://en.wikipedia.org/wiki/Page2">Page 2</option>
    </select>
    
    <!-- Merge synonyms checkbox (if applicable) -->
    <input type="checkbox" class="merge-synonyms-checkbox" data-entry-id="entry_001" checked>
    <label>Merge synonyms</label>
    
    <!-- rest of entry content -->
</div>
```

### 3. Save Hidden Entries List

### 3. Save Actions and Metadata

**Requirement**: Save encyclopedia with list of user actions and system date

**Actions to Track**:
- Hide entry (with reason: missing_wikipedia, general_term, user_selected)
- Disambiguation page selection (selected Wikipedia URL)
- Merge synonyms (confirmed merge of synonyms with same Wikidata ID)
- Sort method applied (alphabetical, importance, original)

**Metadata Structure**:
```json
{
    "created": "2025-12-01T10:00:00Z",
    "last_edited": "2025-12-01T15:30:00Z",
    "title": "Climate Change Encyclopedia",
    "version": "1.0.0",
    "actions": [
        {
            "action": "hide",
            "entry_id": "Q37836",
            "reason": "missing_wikipedia",
            "timestamp": "2025-12-01T10:15:00Z"
        },
        {
            "action": "disambiguation_select",
            "entry_id": "entry_001",
            "selected_url": "https://en.wikipedia.org/wiki/Selected_Page",
            "timestamp": "2025-12-01T10:20:00Z"
        },
        {
            "action": "merge_synonyms",
            "wikidata_id": "Q7942",
            "synonyms_merged": ["Climate Change", "climate change"],
            "timestamp": "2025-12-01T10:25:00Z"
        },
        {
            "action": "sort",
            "method": "alphabetical",
            "timestamp": "2025-12-01T10:30:00Z"
        }
    ],
    "hidden_entries": ["Q37836", "entry_002"],
    "statistics": {
        "total_entries": 100,
        "hidden_entries": 5,
        "merged_groups": 20,
        "disambiguation_selections": 3
    }
}
```

**Storage**:
- Metadata stored in `data-metadata` attribute on encyclopedia container
- Or separate JSON file: `{encyclopedia_name}_metadata.json`
- Include system date in all timestamps

### 4. Save Hidden Entries List

**Requirement**: Save the list of hidden entries persistently

**Implementation Options**:
1. **Data attribute on encyclopedia container**: Store as JSON in `data-hidden-entries` attribute
2. **Separate JSON file**: Save to `hidden_entries.json` alongside HTML file
3. **LocalStorage** (if browser-based): Use browser localStorage

**Recommended**: Data attribute on encyclopedia container for portability

**Format**:
```json
["entry_001", "entry_002", "entry_003"]
```

**Storage Location**:
- In HTML: `<div role="ami_encyclopedia" data-hidden-entries='["entry_001","entry_002"]' ...>`
- Or separate file: `{encyclopedia_name}_hidden_entries.json`

### 5. Sort Entries

**Requirement**: Sort entries in two ways:
- Alphabetically (by term)
- By importance

#### 3.1 Alphabetical Sorting

**Criteria**: Sort by entry term (case-insensitive)

**Implementation**:
- Sort entries by `term` attribute (or `name` attribute if term not available)
- Case-insensitive comparison
- Maintain entry order for entries with same term

#### 3.2 Importance Sorting

**Criteria**: Sort by importance score

**Importance Calculation** (proposed):
1. **Has Wikidata ID**: +10 points
2. **Has Wikipedia URL**: +5 points
3. **Has description**: +3 points
4. **Has figure/image**: +2 points
5. **Has synonyms**: +1 point per synonym

**Alternative**: Use frequency count if available in entry data

**Implementation**:
- Calculate importance score for each entry
- Sort by score (descending - most important first)
- Secondary sort: alphabetically by term

### 6. Disambiguation Pages

**Requirement**: Handle Wikipedia disambiguation pages - user selects target page by inspection

**Implementation Details**:
- Detect disambiguation pages (Wikipedia pages with "(disambiguation)" in title or disambiguation template)
- For disambiguation pages, provide dropdown/selector for user to choose target Wikipedia page
- Record selected page in metadata
- Update entry with selected Wikipedia URL and Wikidata ID

**Detection**:
- Check Wikipedia URL for "/wiki/.*\\(disambiguation\\)" pattern
- Check for disambiguation templates in page content
- Check for multiple Wikipedia links in entry

**HTML Structure**:
```html
<div role="ami_entry" data-entry-id="entry_001" data-is-disambiguation="true">
    <label>Select Wikipedia page:</label>
    <select class="disambiguation-selector" data-entry-id="entry_001">
        <option value="">-- Select --</option>
        <option value="https://en.wikipedia.org/wiki/Page1" data-wikidata="Q1">Page 1</option>
        <option value="https://en.wikipedia.org/wiki/Page2" data-wikidata="Q2">Page 2</option>
    </select>
    <!-- entry content -->
</div>
```

### 7. Missing Wikipedia Pages

**Requirement**: Entries without Wikipedia pages should be hideable by user

**Implementation Details**:
- Detect entries without `wikipedia_url` attribute
- Add checkbox labeled "Hide (missing Wikipedia)"
- By default, these entries may be hidden automatically or marked for review
- User can unhide if needed

**HTML Structure**:
```html
<div role="ami_entry" data-entry-id="entry_001" data-has-wikipedia="false">
    <input type="checkbox" class="entry-hide-checkbox" data-entry-id="entry_001" 
           data-reason="missing_wikipedia" checked>
    <label>Hide (missing Wikipedia)</label>
    <!-- entry content -->
</div>
```

### 8. General Terms

**Requirement**: User can hide terms that are too general

**Implementation Details**:
- Add checkbox for "Hide (too general)"
- User determines which terms are too general
- No automatic detection - purely user-driven
- Record in metadata with reason "general_term"

**HTML Structure**:
```html
<div role="ami_entry" data-entry-id="entry_001">
    <input type="checkbox" class="entry-hide-checkbox" data-entry-id="entry_001" 
           data-reason="general_term">
    <label>Hide (too general)</label>
    <!-- entry content -->
</div>
```

### 9. Metadata Recording

**Requirement**: Record all edits and creation details in metadata

**Metadata Fields**:
- `created`: System date when encyclopedia was first created
- `last_edited`: System date when last edited
- `title`: Encyclopedia title
- `version`: Version number (increment on edits)
- `actions`: List of all user actions with timestamps
- `hidden_entries`: List of hidden entry IDs with reasons
- `disambiguation_selections`: List of disambiguation page selections
- `merge_operations`: List of synonym merge operations
- `sort_history`: History of sort operations

**Storage**:
- Primary: `data-metadata` attribute on encyclopedia container (JSON string)
- Secondary: Separate JSON file `{encyclopedia_name}_metadata.json`
- Include system date in ISO 8601 format for all timestamps

**Example Metadata**:
```json
{
    "created": "2025-12-01T10:00:00Z",
    "last_edited": "2025-12-01T15:30:00Z",
    "title": "Climate Change Encyclopedia",
    "version": "1.0.1",
    "author": "User Name",
    "actions": [
        {
            "action": "hide",
            "entry_id": "Q37836",
            "reason": "missing_wikipedia",
            "timestamp": "2025-12-01T10:15:00Z"
        },
        {
            "action": "disambiguation_select",
            "entry_id": "entry_001",
            "original_url": "https://en.wikipedia.org/wiki/Term_(disambiguation)",
            "selected_url": "https://en.wikipedia.org/wiki/Specific_Term",
            "selected_wikidata": "Q123",
            "timestamp": "2025-12-01T10:20:00Z"
        },
        {
            "action": "merge_synonyms",
            "wikidata_id": "Q7942",
            "synonyms_merged": ["Climate Change", "climate change", "CLIMATE CHANGE"],
            "canonical_term": "Climate Change",
            "timestamp": "2025-12-01T10:25:00Z"
        },
        {
            "action": "sort",
            "method": "alphabetical",
            "timestamp": "2025-12-01T10:30:00Z"
        }
    ],
    "hidden_entries": [
        {"entry_id": "Q37836", "reason": "missing_wikipedia"},
        {"entry_id": "entry_002", "reason": "general_term"}
    ],
    "statistics": {
        "total_entries": 100,
        "visible_entries": 95,
        "hidden_entries": 5,
        "merged_groups": 20,
        "disambiguation_selections": 3
    }
}
```

## Implementation Plan

### Phase 1: HTML Structure Enhancement

1. **Add entry IDs**: Ensure each entry has a unique identifier
   - Use `wikidataID` if available
   - Fallback to `term` attribute
   - Generate unique ID if neither available

2. **Add checkboxes**: Insert checkboxes at start of each entry div
   - Hide checkbox (for missing Wikipedia, general terms, user-selected)
   - Disambiguation selector (for disambiguation pages)
   - Merge synonyms checkbox (for synonyms with same Wikidata ID)
   - Position: Before term/name
   - Classes: `entry-hide-checkbox`, `disambiguation-selector`, `merge-synonyms-checkbox`
   - Data attributes: `data-entry-id`, `data-reason`, `data-is-disambiguation`

3. **Add sorting controls**: Add UI controls for sorting
   - Dropdown or buttons for sort method selection
   - Options: "Alphabetical", "By Importance", "Original Order"

4. **Add metadata container**: Add metadata to encyclopedia container
   - `data-metadata` attribute with JSON string
   - Include creation date, last edited date, actions list

### Phase 2: JavaScript Functionality (if browser-based)

1. **Hide/show functionality**:
   - Event listener on checkboxes
   - Toggle CSS class or display property
   - Update hidden entries list

2. **Save hidden entries**:
   - Collect checked entry IDs
   - Save to data attribute or file
   - Load on page load

3. **Sorting functionality**:
   - Implement sort algorithms
   - Reorder DOM elements
   - Maintain hidden state during sort

### Phase 3: Python Backend Support

1. **Entry ID generation**: Ensure all entries have unique IDs
2. **Disambiguation detection**: Detect disambiguation pages
3. **Missing Wikipedia detection**: Identify entries without Wikipedia URLs
4. **Hidden entries persistence**: Read/write hidden entries list with reasons
5. **Action tracking**: Record all user actions with timestamps
6. **Metadata management**: Create, update, and persist metadata
7. **Sorting methods**: Implement sort functions
8. **HTML generation**: Include checkboxes, selectors, and sorting controls in generated HTML
9. **System date integration**: Use system date for all timestamps

## Data Structure

### Entry Identification

Each entry should have a unique identifier:
- Primary: `wikidataID` attribute (e.g., "Q37836")
- Secondary: `term` attribute (e.g., "Greenhouse Gas")
- Fallback: Generated ID (e.g., "entry_001")

### Hidden Entries Storage

```python
hidden_entries = [
    {"entry_id": "Q37836", "reason": "missing_wikipedia"},
    {"entry_id": "Q12345", "reason": "general_term"},
    {"entry_id": "entry_001", "reason": "user_selected"}
]
```

### Action Tracking

```python
action = {
    "action": "hide",  # or "disambiguation_select", "merge_synonyms", "sort"
    "entry_id": "Q37836",
    "reason": "missing_wikipedia",  # for hide actions
    "selected_url": "https://...",  # for disambiguation_select
    "selected_wikidata": "Q123",  # for disambiguation_select
    "synonyms_merged": ["term1", "term2"],  # for merge_synonyms
    "method": "alphabetical",  # for sort actions
    "timestamp": "2025-12-01T10:15:00Z"  # system date
}
```

### Importance Score Calculation

```python
def calculate_importance(entry: Dict) -> int:
    score = 0
    if entry.get('wikidata_id'):
        score += 10
    if entry.get('wikipedia_url'):
        score += 5
    if entry.get('description_html'):
        score += 3
    if entry.get('figure_html'):
        score += 2
    synonyms = entry.get('synonyms', [])
    if synonyms:
        score += len(synonyms)
    return score
```

## Files to Modify

1. **`amilib/ami_encyclopedia.py`**:
   - `aggregate_synonyms()`: Ensure case variants are preserved in synonyms list
   - `_normalize_terms()`: Preserve case variants (don't deduplicate by case)
   - `_detect_disambiguation()`: Detect disambiguation pages
   - `_detect_missing_wikipedia()`: Identify entries without Wikipedia URLs
   - `create_wiki_normalized_html()`: Add checkboxes, selectors, entry IDs, sorting controls
   - `calculate_importance_score()`: Calculate importance score for entries
   - `sort_entries()`: Sort entries (alphabetical, importance)
   - `save_metadata()`: Save metadata with actions and system date
   - `load_metadata()`: Load metadata from file or HTML
   - `record_action()`: Record user action with timestamp
   - `get_system_date()`: Get current system date in ISO 8601 format

2. **`amilib/ami_encyclopedia_args.py`**:
   - Add command-line arguments for:
     - `--sort`: Sort method (alphabetical, importance, none)
     - `--hidden-entries`: Path to hidden entries file
     - `--metadata`: Path to metadata file
     - `--save-actions`: Save actions list with encyclopedia
     - `--auto-hide-missing-wikipedia`: Automatically hide entries without Wikipedia URLs

3. **CSS/HTML**:
   - Add styles for checkboxes
   - Add styles for hidden entries
   - Add styles for sorting controls

## Testing Requirements

1. **Hide functionality**:
   - Test checkbox appears on each entry
   - Test entry hides when checkbox checked
   - Test hidden entries list is saved
   - Test hidden entries persist on reload

2. **Case-insensitive collapse**:
   - Test entries with same Wikidata ID but different case are collapsed
   - Test all case variants appear in synonyms list
   - Test canonical term selection (prefers non-lowercase)

3. **Sort functionality**:
   - Test alphabetical sorting
   - Test importance sorting
   - Test sorting maintains hidden state
   - Test sorting with empty/null values

3. **Integration**:
   - Test with real encyclopedia files
   - Test with entries missing various fields
   - Test with large number of entries

## Style Guide Compliance

- Use absolute imports: `from amilib.util import Util`
- Use `Path()` constructor with comma-separated arguments
- Follow existing code patterns in `ami_encyclopedia.py`
- No mocks in tests
- Use `Resources.TEMP_DIR` for temporary files

## Next Steps

1. Review and approve requirements
2. Implement entry ID generation
3. Implement checkbox addition to HTML
4. Implement hidden entries persistence
5. Implement sorting algorithms
6. Add command-line arguments
7. Create tests
8. Update documentation

