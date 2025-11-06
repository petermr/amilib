# Tests with Minimal Wikidata Lookup

## Overview

Tests that perform very small amounts of actual Wikidata lookup operations. These can be used to verify that auto-lookup functionality works without slowing down the test suite significantly.

## Tests Identified

### 1. `test/test_dict_wikidata_extraction.py::test_extract_wikidata_id_from_article`
- **Lookups:** 3 terms (climate change, greenhouse effect, carbon dioxide)
- **Purpose:** Tests extracting Wikidata IDs from Wikipedia articles
- **Time:** ~3-5 seconds (depends on network)
- **Use case:** Good for testing auto-lookup in encyclopedia when Wikidata ID is missing

### 2. `test/test_wikimedia.py::WikidataTest::test_lookup_wikidata_acetone`
- **Lookups:** 1 term (acetone)
- **Purpose:** Tests direct Wikidata lookup
- **Time:** ~1-2 seconds
- **Use case:** Minimal lookup for testing auto-lookup functionality

## Recommendation

Add a test in `test_encyclopedia.py` that:
1. Creates an entry WITHOUT `wikidataID` attribute
2. Has a Wikipedia URL
3. Enables auto-lookup
4. Verifies that Wikidata ID is extracted from Wikipedia page

This would be a minimal lookup test (1 lookup) that verifies the auto-lookup functionality works correctly.

## Implementation

Add an optional parameter to `create_from_html_content()` to enable auto-lookup:

```python
def create_from_html_content(self, html_content: str, enable_auto_lookup: bool = False) -> 'AmiEncyclopedia':
    """Create encyclopedia from HTML content
    :param enable_auto_lookup: If True, auto-lookup Wikidata IDs for entries without them (requires network)
    """
```

Then only enable it in specific tests that need it.






