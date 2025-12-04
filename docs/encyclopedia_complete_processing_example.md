# Complete Processing Example - 15 Entry Encyclopedia

## Overview

This document points to a complete example of processing an encyclopedia where:
1. **All entries are classified** (using the classification system)
2. **All Wikidata IDs are looked up** (for entries that need them)

## Test File Location

**Test File**: `test/test_encyclopedia_add_wikidata_ids.py`  
**Test Method**: `test_complete_processing_15_entries()`

**Input Encyclopedia**: `test/resources/encyclopedia/test_encyclopedia_15_entries.html`

**Output Encyclopedia**: `temp/encyclopedia_add_wikidata_ids/test_encyclopedia_15_entries_complete.html`

## Running the Example

```bash
cd /Users/pm286/workspace/amilib
pytest test/test_encyclopedia_add_wikidata_ids.py::EncyclopediaAddWikidataIdsTest::test_complete_processing_15_entries -v -s
```

## Processing Steps

### Step 1: Classify All Entries

The system classifies all 15 entries into categories:
- **HAS_WIKIDATA**: 13 entries (already have Wikidata IDs)
- **UNPROCESSED**: 2 entries (need Wikidata ID lookup)
- **AMBIGUOUS**: 0 entries
- **NO_WIKIPEDIA_PAGE**: 0 entries
- **NO_WIKIDATA_ENTRY**: 0 entries (initially)
- **ERROR**: 0 entries

### Step 2: Lookup Wikidata IDs

The system looks up Wikidata IDs for unprocessed entries:
- **Entries looked up**: 2
- **Successfully found**: 0 (these were fake entries that don't exist)
- **Failed lookups**: 2 (expected - these are test entries without real Wikipedia pages)
- **Skipped (already have ID)**: 13 (classified entries skipped)

### Step 3: Final Classification

After lookup, all entries are re-classified:
- **HAS_WIKIDATA**: 13 entries
- **NO_WIKIDATA_ENTRY**: 2 entries (Wikipedia page exists but no Wikidata entry found)
- **UNPROCESSED**: 0 entries (all processed)
- **All entries classified**: ✓

## Entry Details

The 15 entries in the test encyclopedia:

| # | Term | Classification | Wikidata ID |
|---|------|----------------|-------------|
| 1 | climate change | HAS_WIKIDATA | Q125928 |
| 2 | biodiversity | HAS_WIKIDATA | Q47041 |
| 3 | ecosystem services | HAS_WIKIDATA | Q295865 |
| 4 | drought | HAS_WIKIDATA | Q43059 |
| 5 | wildfire | HAS_WIKIDATA | Q169950 |
| 6 | precipitation | HAS_WIKIDATA | Q25257 |
| 7 | deforestation | HAS_WIKIDATA | Q169940 |
| 8 | AR5 | HAS_WIKIDATA | Q4653985 |
| 9 | adaptation | HAS_WIKIDATA | Q483921 |
| 10 | climate warming | HAS_WIKIDATA | Q125928 |
| 11 | global warming | HAS_WIKIDATA | Q125928 |
| 12 | nonexistent_term_xyz123 | NO_WIKIDATA_ENTRY | N/A |
| 13 | fake_entry_abc456 | NO_WIKIDATA_ENTRY | N/A |
| 14 | fire | HAS_WIKIDATA | Q3196 |
| 15 | birds | HAS_WIKIDATA | Q5113 |

### Notes

- **Entries 1, 10, 11** (climate change, climate warming, global warming) all share the same Wikidata ID (Q125928) - these are synonyms that should be collapsed
- **Entries 12, 13** are test entries without real Wikipedia pages - correctly classified as NO_WIKIDATA_ENTRY
- **Entry 8** (AR5) is a disambiguation page but was successfully resolved to a Wikidata ID

## Output File

The complete processed encyclopedia is saved to:
```
temp/encyclopedia_add_wikidata_ids/test_encyclopedia_15_entries_complete.html
```

**File size**: ~25 KB  
**Format**: HTML with `role="ami_encyclopedia"`  
**Contains**: All entries with classifications and Wikidata IDs

## Code Example

```python
from amilib.ami_encyclopedia import AmiEncyclopedia
from pathlib import Path

# Load encyclopedia
encyclopedia = AmiEncyclopedia(title="Test Encyclopedia 15 Entries")
encyclopedia.create_from_html_file(
    Path("test/resources/encyclopedia/test_encyclopedia_15_entries.html")
)

# Step 1: Classify all entries
classification_stats = encyclopedia.classify_all_entries()
print(f"Classified: {classification_stats}")

# Step 2: Lookup all Wikidata IDs
lookup_stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(
    max_ids=None,  # Process all entries
    output_file=Path("output_complete.html")
)
print(f"Lookup results: {lookup_stats}")

# Step 3: Verify all entries are classified
for entry in encyclopedia.entries:
    assert entry.get('classification'), "All entries should be classified"
    print(f"{entry['term']}: {entry['classification']} - {entry.get('wikidata_id', 'N/A')}")
```

## Classification System Benefits

1. **Performance**: Skips expensive lookups for already-classified entries
2. **Efficiency**: Fast classification using in-memory checks
3. **Persistence**: Classification stored in entry dictionaries
4. **Statistics**: Track classification distribution
5. **Smart Processing**: Only processes entries that need lookup

## Summary

✅ **All 15 entries classified**  
✅ **All Wikidata IDs looked up** (where possible)  
✅ **Complete encyclopedia saved**  
✅ **Ready for further processing** (synonym aggregation, normalization, etc.)

The processed encyclopedia can be opened in a browser for inspection:
```
file:///Users/pm286/workspace/amilib/temp/encyclopedia_add_wikidata_ids/test_encyclopedia_15_entries_complete.html
```


