# Wikidata ID Enhancement - Implementation Summary

## Overview

Implemented comprehensive Wikidata ID lookup functionality with staged strategy and SPARQL batch support.

## Implementation Date

2025-12-03

## Key Features Implemented

### 1. Automatic Wikidata ID Lookup

**Changed**: Removed `enable_auto_lookup` parameter - lookup is now always automatic.

**Rationale**: User requirement states "It is essential that all entries have wikidata_IDs"

**Behavior**: 
- If entry already has Wikidata ID → **Skip all lookups** (avoid unnecessary network calls)
- If entry missing Wikidata ID → Perform comprehensive lookup

### 2. Multi-Priority Lookup Strategy

**Priority 1**: From HTML attributes (existing)
- `wikidataID`, `wikidataid`, `wikidata_id` attributes

**Priority 2**: From Wikipedia URL
- Extract page title from URL
- Lookup Wikipedia page
- Extract Wikidata ID from Wikipedia page

**Priority 3**: From term via Wikipedia lookup
- Lookup Wikipedia page by term
- Extract Wikidata ID from Wikipedia page

**Priority 4**: Direct Wikidata lookup (fallback)
- Use `WikidataLookup.lookup_wikidata(term)`

### 3. Helper Methods

#### `_extract_qid_from_wikidata_url(wikidata_url: str) -> Optional[str]`
- Extracts Q/P ID from Wikidata EntityPage URL
- Handles URLs with fragments (e.g., `#sitelinks`)
- Returns None if no valid QID found

#### `_extract_wikidata_id_from_wikipedia_url(wikipedia_url: str) -> Optional[str]`
- Looks up Wikipedia page from URL
- Extracts Wikidata ID from Wikipedia page
- Returns None if lookup fails

#### `_lookup_wikidata_id_by_term(term: str) -> Optional[str]`
- Tries Wikipedia lookup first (more reliable)
- Falls back to direct Wikidata lookup
- Returns None if no match found

### 4. SPARQL Batch Lookup

#### `_lookup_wikidata_ids_batch_sparql(terms: List[str]) -> Dict[str, Optional[str]]`

**Purpose**: Lookup multiple Wikidata IDs in a single SPARQL query (faster than individual lookups)

**Implementation**:
- Constructs SPARQL query with VALUES clause for batch lookup
- Limits to 50 terms per query to avoid timeout
- Parses SPARQL XML results
- Returns dictionary mapping term -> Wikidata ID

**SPARQL Query Example**:
```sparql
SELECT ?item ?itemLabel ?term WHERE {
  VALUES ?term { "Climate change" "Greenhouse gas" "IPCC" }
  ?item rdfs:label ?itemLabel .
  FILTER(LANG(?itemLabel) = "en")
  FILTER(LCASE(?itemLabel) = LCASE(?term))
}
LIMIT 100
```

**Benefits**:
- Single network request for multiple terms
- Faster than individual lookups
- Respects Wikidata rate limits better

**Limitations**:
- May have rate limits (falls back to individual lookups)
- Requires exact label match (case-insensitive)

### 5. Staged Lookup Strategy

#### `ensure_all_entries_have_wikidata_ids(batch_size: int = 100, save_file: Optional[Path] = None) -> Dict[str, int]`

**Purpose**: Process entries in batches, saving after each batch

**Strategy**:
1. Identify entries missing Wikidata IDs
2. Process in batches of N entries (default: 100)
3. For each batch:
   - Try SPARQL batch lookup first (faster)
   - Fall back to individual lookups for remaining entries
   - Update entries with found Wikidata IDs
4. Save dictionary after each batch (if `save_file` provided)
5. Repeat until all entries processed

**Parameters**:
- `batch_size`: Number of entries per batch (default: 100)
- `save_file`: Optional file path to save after each batch

**Returns**: Statistics dictionary:
```python
{
    "total_entries": 866,
    "entries_with_wikidata_id_before": 0,
    "entries_with_wikidata_id_after": 750,
    "added_from_wikipedia_url": 400,
    "added_from_wikipedia_term": 300,
    "added_from_wikidata_lookup": 50,
    "added_from_sparql_batch": 0,  # If SPARQL used
    "entries_still_missing": 116,
    "batches_processed": 9
}
```

**Benefits**:
- Progress saved after each batch (resume if interrupted)
- Reduces risk of data loss
- Allows monitoring progress
- Respects rate limits by processing in smaller batches

### 6. Save Functionality

**Existing Method**: `save_wiki_normalized_html(output_file: Path)`

**Usage in Staged Lookup**:
- Automatically called after each batch if `save_file` provided
- Saves updated HTML with new Wikidata IDs
- Creates parent directories if needed

## Code Changes

### Modified Methods

1. **`create_from_html_content()`**
   - Removed `enable_auto_lookup` parameter
   - Always performs lookup (skips if Wikidata ID already exists)
   - Uses new helper methods

### New Methods

1. `_extract_qid_from_wikidata_url()` - Static helper
2. `_extract_wikidata_id_from_wikipedia_url()` - Instance method
3. `_lookup_wikidata_id_by_term()` - Instance method
4. `_lookup_wikidata_ids_batch_sparql()` - Instance method
5. `ensure_all_entries_have_wikidata_ids()` - Public method

## Usage Examples

### Basic Usage (Automatic Lookup)

```python
from amilib.ami_encyclopedia import AmiEncyclopedia
from pathlib import Path

# Create encyclopedia - lookup happens automatically
encyclopedia = AmiEncyclopedia(title="Climate Encyclopedia")
encyclopedia.create_from_html_file(Path("input.html"))

# Entries with existing Wikidata IDs are skipped
# Entries without Wikidata IDs are looked up automatically
```

### Staged Lookup with Save

```python
# Process in batches of 100, save after each batch
stats = encyclopedia.ensure_all_entries_have_wikidata_ids(
    batch_size=100,
    save_file=Path("output_with_wikidata_ids.html")
)

print(f"Processed {stats['batches_processed']} batches")
print(f"Added {stats['entries_with_wikidata_id_after'] - stats['entries_with_wikidata_id_before']} Wikidata IDs")
print(f"{stats['entries_still_missing']} entries still missing Wikidata IDs")
```

### Manual Save

```python
# Save updated encyclopedia
encyclopedia.save_wiki_normalized_html(Path("output.html"))
```

## Performance Considerations

### SPARQL vs Individual Lookups

- **SPARQL batch**: ~50 terms per query, 1 network request
- **Individual lookups**: 1 network request per term
- **Recommendation**: Use SPARQL for batches of 10+ terms

### Rate Limiting

- Wikidata SPARQL endpoint: ~60 requests/minute
- Wikipedia API: ~200 requests/minute
- **Staged strategy**: Processes 100 entries at a time, saves progress

### Caching

- No caching implemented yet
- Future enhancement: Cache Wikipedia page lookups

## Testing

### Test Files Available

1. **`test/resources/plant/eoplant_part.xml`**
   - 112 entries, 100% have Wikidata IDs
   - Use to test: Entries with existing IDs skip lookups

2. **`test/resources/encyclopedia/wg1chap03_dict.html`**
   - 866 entries, 0% have Wikidata IDs
   - Use to test: Staged lookup on large file

3. **`test/resources/dictionary/html/ch7_dict.html`**
   - 296 entries, 0% have Wikidata IDs
   - Use to test: Medium-size lookup

## Future Enhancements

1. **SPARQL Result Parsing**: Improve parsing of SPARQL XML results
2. **Caching**: Cache Wikipedia page lookups to avoid duplicate requests
3. **Progress Tracking**: Add progress bar for staged lookup
4. **Resume Capability**: Resume staged lookup from last saved batch
5. **Parallel Processing**: Process multiple batches in parallel (with rate limit respect)

## Notes

- **Skip if exists**: Entries with existing Wikidata IDs skip all lookups (performance optimization)
- **Error handling**: All lookup methods handle errors gracefully, continue with next method
- **Validation**: Wikidata IDs are validated (must be Q/P followed by digits)
- **Logging**: Comprehensive logging for debugging and monitoring

