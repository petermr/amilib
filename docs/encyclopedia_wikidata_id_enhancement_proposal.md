# Proposal: Ensure All Encyclopedia Entries Have Wikidata IDs

## Overview

Currently, `AmiEncyclopedia` has optional Wikidata ID lookup via `enable_auto_lookup` parameter (defaults to `False`). We need to ensure **ALL entries have Wikidata IDs** by making lookup automatic and comprehensive.

## Current State

### Current Implementation

1. **Priority 1**: Extract Wikidata ID from HTML attributes (`wikidataID`, `wikidataid`, `wikidata_id`)
2. **Priority 2**: Extract from Wikipedia URL (only if `enable_auto_lookup=True`)
   - Uses `WikipediaPage.lookup_wikipedia_page_for_term()` to get Wikipedia page
   - Extracts Wikidata ID using `wikipedia_page.get_wikidata_item()`
3. **Priority 3**: Direct Wikidata lookup by term (only if `enable_auto_lookup=True`)
   - Uses `WikidataLookup.lookup_wikidata(term)`

### Problems

- `enable_auto_lookup` defaults to `False`, so most entries won't get Wikidata IDs
- Lookup is not comprehensive - doesn't try all methods systematically
- No statistics on how many entries got Wikidata IDs from each method
- No post-processing to ensure all entries have Wikidata IDs

## Proposed Solution

### 1. Make Wikidata ID Lookup Automatic

**Change**: Remove `enable_auto_lookup` parameter and make lookup automatic for all entries.

**Rationale**: User requirement states "It is essential that all entries have wikidata_IDs"

### 2. Comprehensive Lookup Strategy

Implement a systematic multi-priority lookup:

```
Priority 1: From HTML attributes (existing - already implemented)
  ├─ wikidataID attribute
  ├─ wikidataid attribute (lowercase from HTML parser)
  └─ wikidata_id attribute

Priority 2: From Wikipedia URL (if exists)
  ├─ Extract page title from URL
  ├─ Lookup Wikipedia page: WikipediaPage.lookup_wikipedia_page_for_term(page_title)
  ├─ Extract Wikidata ID: wikipedia_page.get_wikidata_item()
  └─ Parse Q/P ID from Wikidata URL

Priority 3: From term via Wikipedia lookup
  ├─ Lookup Wikipedia page: WikipediaPage.lookup_wikipedia_page_for_term(term)
  ├─ Extract Wikidata ID: wikipedia_page.get_wikidata_item()
  └─ Parse Q/P ID from Wikidata URL

Priority 4: Direct Wikidata lookup (if Wikipedia lookup fails)
  ├─ Use WikidataLookup.lookup_wikidata(term)
  └─ Extract QID from results
```

### 3. New Methods

#### `_extract_wikidata_id_from_wikipedia_url(wikipedia_url: str) -> Optional[str]`

Extract Wikidata ID from a Wikipedia URL by:
1. Extracting page title from URL
2. Looking up Wikipedia page
3. Getting Wikidata item URL
4. Parsing Q/P ID

**Returns**: Wikidata ID (Q/P format) or None

#### `_extract_wikidata_id_from_wikipedia_page(wikipedia_page: WikipediaPage) -> Optional[str]`

Extract Wikidata ID from a WikipediaPage object:
1. Call `wikipedia_page.get_wikidata_item()` to get Wikidata URL
2. Parse Q/P ID from URL using regex

**Returns**: Wikidata ID (Q/P format) or None

#### `_lookup_wikidata_id_by_term(term: str) -> Optional[str]`

Lookup Wikidata ID by term using multiple methods:
1. Try Wikipedia lookup first (more reliable)
2. Fall back to direct Wikidata lookup

**Returns**: Wikidata ID (Q/P format) or None

#### `ensure_all_entries_have_wikidata_ids() -> Dict[str, int]`

Post-processing method to ensure all entries have Wikidata IDs:
- Iterate through all entries
- For entries without Wikidata IDs, try all lookup methods
- Track statistics: how many got IDs from each method

**Returns**: Statistics dictionary:
```python
{
    "total_entries": 100,
    "entries_with_wikidata_id_before": 60,
    "entries_with_wikidata_id_after": 95,
    "added_from_wikipedia_url": 20,
    "added_from_wikipedia_term": 10,
    "added_from_wikidata_lookup": 5,
    "entries_still_missing": 5
}
```

### 4. Updated `create_from_html_content()` Method

**Changes**:
1. Remove `enable_auto_lookup` parameter (always enabled)
2. Always try Priority 2 and Priority 3 lookups
3. Add comprehensive error handling and logging
4. Track lookup statistics

**New Signature**:
```python
def create_from_html_content(self, html_content: str) -> 'AmiEncyclopedia':
```

### 5. Statistics and Logging

Add metadata statistics:
- Track how many entries have Wikidata IDs
- Track lookup method used for each entry
- Log warnings for entries that couldn't get Wikidata IDs

Update metadata:
```python
metadata["statistics"]["wikidata_id_coverage"] = {
    "total_entries": 100,
    "entries_with_wikidata_id": 95,
    "coverage_percentage": 95.0,
    "lookup_methods": {
        "from_attribute": 60,
        "from_wikipedia_url": 20,
        "from_wikipedia_term": 10,
        "from_wikidata_lookup": 5
    }
}
```

## Implementation Details

### Helper Method: Extract Q/P ID from Wikidata URL

```python
@staticmethod
def _extract_qid_from_wikidata_url(wikidata_url: str) -> Optional[str]:
    """Extract Q/P ID from Wikidata EntityPage URL
    
    Examples:
        https://www.wikidata.org/wiki/Special:EntityPage/Q7942 -> Q7942
        https://www.wikidata.org/wiki/Special:EntityPage/Q125928#sitelinks -> Q125928
    """
    if not wikidata_url:
        return None
    
    # Pattern 1: EntityPage/Q123 or EntityPage/P123
    match = re.search(r'[Ee]ntity[Pp]age/([QP]\d+)', wikidata_url)
    if match:
        return match.group(1)
    
    # Pattern 2: /Q123 or /P123 at end of URL
    match = re.search(r'/([QP]\d+)(?:#|/|$)', wikidata_url)
    if match:
        return match.group(1)
    
    return None
```

### Updated Entry Processing

**Important**: If an entry already has a Wikidata ID, skip all lookups to avoid unnecessary network calls.

```python
# Priority 1: From attributes (existing code)
wikidata_id = self._extract_wikidata_id_from_attributes(entry_element, term)

# Only perform lookups if Wikidata ID is missing
if not wikidata_id:
    # Priority 2: From Wikipedia URL (if exists)
    if wikipedia_url:
        wikidata_id = self._extract_wikidata_id_from_wikipedia_url(wikipedia_url)
    
    # Priority 3: From term via Wikipedia lookup (if still no Wikidata ID)
    if not wikidata_id and term:
        wikidata_id = self._lookup_wikidata_id_by_term(term)
    
    # Priority 4: Direct Wikidata lookup (if still no Wikidata ID)
    if not wikidata_id and term:
        wikidata_id = self._lookup_wikidata_id_direct(term)
```

## Error Handling

- **Network errors**: Log warning, continue with next method
- **Invalid Wikidata IDs**: Validate format (Q/P followed by digits), log warning
- **Missing Wikipedia pages**: Try next lookup method
- **Rate limiting**: Add delays between lookups if needed

## Performance Considerations

- **Caching**: Cache Wikipedia page lookups to avoid duplicate requests
- **Batch processing**: Consider batch lookups if processing many entries
- **Progress tracking**: Log progress for large encyclopedias

## Testing

### Test Cases

1. **Entry with Wikidata ID in attribute**: Should use it (Priority 1) - **Skip all lookups**
2. **Entry with Wikipedia URL but no Wikidata ID**: Should extract from Wikipedia page (Priority 2)
3. **Entry with term but no Wikipedia URL**: Should lookup Wikipedia page and extract Wikidata ID (Priority 3)
4. **Entry with term but no Wikipedia page**: Should use direct Wikidata lookup (Priority 4)
5. **Entry with no Wikidata ID found**: Should log warning, entry remains without Wikidata ID
6. **Invalid Wikidata ID format**: Should log warning, treat as missing

### Test Data

#### Small Test Files (for unit tests)
Create test HTML with:
- Entry with `wikidataID="Q123"` attribute (should skip lookups)
- Entry with `wikipedia_url="https://en.wikipedia.org/wiki/Climate_change"` but no Wikidata ID
- Entry with only `term="Greenhouse Gas"` (no Wikipedia URL, no Wikidata ID)
- Entry with invalid Wikidata ID format

#### Medium-Size Test Files (for integration tests)

**Available test files with Wikidata IDs:**

1. **`test/resources/plant/eoplant_part.xml`**
   - **Size**: ~112 entries, all with Wikidata IDs (100% coverage)
   - **Format**: XML (needs conversion to HTML for AmiEncyclopedia)
   - **Use case**: Test with entries that already have Wikidata IDs (should skip lookups)
   - **Sample entries**: apical (Q66571835), cone (Q22710), leaf (Q33971), root (Q41500)

2. **`test/resources/amidicts/mini_plant_part.xml`**
   - **Size**: 4 entries, all with Wikidata IDs (100% coverage)
   - **Format**: XML
   - **Use case**: Small test file for quick validation

**Test files without Wikidata IDs (for testing lookup functionality):**

1. **`test/resources/encyclopedia/wg1chap03_dict.html`**
   - **Size**: 866 entries, 0% have Wikidata IDs
   - **Format**: HTML (ready for AmiEncyclopedia)
   - **Use case**: Test comprehensive lookup on large file

2. **`test/resources/dictionary/html/ch7_dict.html`**
   - **Size**: 296 entries, 0% have Wikidata IDs
   - **Format**: HTML (ready for AmiEncyclopedia)
   - **Use case**: Test lookup on medium-size file

### Recommended Test Strategy

1. **Unit tests**: Use small HTML with mixed scenarios (has Wikidata ID, missing Wikidata ID)
2. **Integration test 1**: Use `eoplant_part.xml` (convert to HTML) to verify entries with existing Wikidata IDs skip lookups
3. **Integration test 2**: Use `ch7_dict.html` (296 entries) to test lookup functionality on medium-size file
4. **Performance test**: Use `wg1chap03_dict.html` (866 entries) to test lookup on large file (with rate limiting)

## Migration

### Backward Compatibility

- Existing code that calls `create_from_html_content(html_content, enable_auto_lookup=False)` will need to be updated
- However, since the requirement is that ALL entries must have Wikidata IDs, this is a breaking change that's necessary

### Deprecation

- Mark `enable_auto_lookup` parameter as deprecated (if we keep it temporarily)
- Remove in next major version

## Benefits

1. **Comprehensive coverage**: All entries will have Wikidata IDs when possible
2. **Automatic**: No need to manually enable lookup
3. **Robust**: Multiple fallback methods ensure maximum coverage
4. **Trackable**: Statistics show how many entries got IDs from each method
5. **Maintainable**: Clear priority system makes code easy to understand

## Risks

1. **Performance**: Multiple lookups per entry could be slow for large encyclopedias
   - **Mitigation**: Add caching, batch processing, progress logging
2. **Rate limiting**: Wikipedia/Wikidata APIs may rate limit
   - **Mitigation**: Add delays, respect rate limits, cache results
3. **Network failures**: Lookups may fail due to network issues
   - **Mitigation**: Comprehensive error handling, continue with next method

## Next Steps

1. Implement helper methods for Wikidata ID extraction
2. Update `create_from_html_content()` to always perform lookups
3. Add `ensure_all_entries_have_wikidata_ids()` method
4. Add statistics tracking
5. Update tests
6. Update documentation

