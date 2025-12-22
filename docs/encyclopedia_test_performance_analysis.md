# Encyclopedia Test Performance Analysis

## Summary

The `*encyclopedia*.py` tests are long-running because they perform **extensive network operations** including:
1. **Downloading Wikipedia pages** from the internet
2. **Querying Wikidata** via HTTP requests
3. **Downloading test data** from GitHub
4. **Making multiple sequential API calls** with rate-limiting delays

## Test Files Analyzed

1. `test/test_encyclopedia.py` - Basic functionality tests (mostly fast)
2. `test/test_encyclopedia_auto_lookup.py` - **Makes network calls**
3. `test/test_encyclopedia_add_wikidata_ids.py` - **Makes many network calls**
4. `test/test_encyclopedia_hide_sort.py` - **Downloads from GitHub + makes many network calls**
5. `test/test_encyclopedia_args.py` - Command-line argument tests (fast)

## Network Operations Identified

### 1. Wikipedia Page Downloads

**Location**: `amilib/wikimedia.py` → `WikipediaPage.lookup_wikipedia_page_for_url()` and `lookup_wikipedia_page_for_term()`

**How it works**:
- Makes HTTP GET requests to `https://en.wikipedia.org/wiki/...`
- Downloads full HTML pages
- Parses HTML to extract content

**Called by**:
- `test_encyclopedia_auto_lookup.py::test_auto_lookup_from_wikipedia_url()` - 1 network call
- `test_encyclopedia_auto_lookup.py::test_auto_lookup_from_term()` - 1 network call
- `ami_encyclopedia.py::_extract_wikidata_id_from_wikipedia_url()` - called for each entry
- `ami_encyclopedia.py::_get_disambiguation_options()` - downloads disambiguation pages

### 2. Wikidata Lookups

**Location**: `amilib/wikimedia.py` → `WikidataLookup.lookup_wikidata()` and `WikipediaPage.get_wikidata_item()`

**How it works**:
- Makes HTTP GET requests to `https://www.wikidata.org/w/index.php?search=...`
- Queries Wikidata search API
- Extracts Wikidata IDs (Q/P numbers) from results

**Called by**:
- `ami_encyclopedia.py::_lookup_wikidata_id_by_term()` - for each term lookup
- `ami_encyclopedia.py::_extract_wikidata_id_from_wikipedia_url()` - extracts Wikidata ID from Wikipedia page

### 3. SPARQL Batch Queries

**Location**: `amilib/ami_encyclopedia.py::_lookup_wikidata_ids_batch_sparql()`

**How it works**:
- Constructs SPARQL queries to Wikidata Query Service
- Makes HTTP POST requests to `https://query.wikidata.org/sparql`
- Processes XML results

**Called by**:
- `ami_encyclopedia.py::ensure_all_entries_have_wikidata_ids()` - batch processing

### 4. GitHub Downloads

**Location**: `test/test_encyclopedia_hide_sort.py`

**Test methods**:
- `test_add_all_wikidata_ids_one_pass()` - Downloads HTML from GitHub:
  ```python
  url = "https://raw.githubusercontent.com/semanticClimate/internship_sC/nidhi/output_dict_path.html"
  response = requests.get(url, timeout=30)
  ```
- `test_add_wikidata_ids_staged_100()` - Same GitHub download

**Impact**: Downloads large HTML files before processing

## Slow Test Methods

### High Impact (Many Network Calls)

1. **`test_encyclopedia_add_wikidata_ids.py::test_complete_processing_15_entries()`**
   - Calls `lookup_wikidata_ids_from_wikipedia_pages()` with `max_ids=None`
   - Processes all 15 entries sequentially
   - Each entry makes 1-2 network calls (Wikipedia + Wikidata)
   - **Estimated**: 15-30 network calls × 0.1s delay = 1.5-3 seconds minimum

2. **`test_encyclopedia_add_wikidata_ids.py::test_lookup_wikidata_ids_from_wikipedia_pages()`**
   - Calls `lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)`
   - Processes all entries in test file
   - **Estimated**: 15+ network calls × 0.1s delay = 1.5+ seconds minimum

3. **`test_encyclopedia_hide_sort.py::test_add_all_wikidata_ids_one_pass()`**
   - Downloads HTML from GitHub (network call #1)
   - Calls `ensure_all_entries_have_wikidata_ids(batch_size=total_entries)`
   - Makes network calls for **every entry** that needs a Wikidata ID
   - **Estimated**: 1 download + N lookups (could be 100+ entries) × 0.1s delay = 10+ seconds

4. **`test_encyclopedia_hide_sort.py::test_add_wikidata_ids_staged_100()`**
   - Downloads HTML from GitHub (network call #1)
   - Processes entries in batches of 100
   - Makes network calls for each batch
   - **Estimated**: 1 download + multiple batches × 100 entries × 0.1s delay = 10+ seconds

### Medium Impact (Few Network Calls)

5. **`test_encyclopedia_auto_lookup.py::test_auto_lookup_from_wikipedia_url()`**
   - Makes 1 Wikipedia page download
   - **Estimated**: ~0.5-1 second

6. **`test_encyclopedia_auto_lookup.py::test_auto_lookup_from_term()`**
   - Makes 1 Wikipedia page download + 1 Wikidata lookup
   - **Estimated**: ~1-2 seconds

### Rate Limiting Delays

**Location**: `ami_encyclopedia.py::lookup_wikidata_ids_from_wikipedia_pages()`

```python
# Rate limiting: add delay between requests to avoid rate limiting
if delay_seconds > 0 and idx < total_to_process:
    time.sleep(delay_seconds)  # Default: 0.1 seconds
```

**Impact**: For 15 entries, adds 1.4 seconds of delays (14 × 0.1s)

## Code Flow for Slow Operations

### Example: `lookup_wikidata_ids_from_wikipedia_pages()`

```
1. For each entry:
   a. Check classification (fast - no network)
   b. If UNPROCESSED:
      c. Call _extract_wikidata_id_from_wikipedia_url()
         → WikipediaPage.lookup_wikipedia_page_for_term() [NETWORK CALL #1]
         → wikipedia_page.get_wikidata_item() [NETWORK CALL #2]
      d. Call _get_wikidata_category() [NETWORK CALL #3 - optional]
   e. Sleep 0.1 seconds (rate limiting)
```

**For 15 entries**: 15-45 network calls + 1.4 seconds of delays

### Example: `ensure_all_entries_have_wikidata_ids()`

```
1. Download HTML from GitHub [NETWORK CALL #1] (if using GitHub source)
2. For each batch:
   a. Try SPARQL batch lookup [NETWORK CALL #2]
   b. If SPARQL fails, fall back to individual lookups:
      → For each term: _lookup_wikidata_id_by_term()
         → WikipediaPage.lookup_wikipedia_page_for_term() [NETWORK CALL]
         → WikidataLookup.lookup_wikidata() [NETWORK CALL]
   c. Sleep between batches
```

**For 100 entries**: 1 download + 1 SPARQL query + potentially 100+ individual lookups

## Why Tests Are Slow

1. **Sequential Processing**: Tests process entries one-by-one, not in parallel
2. **Rate Limiting**: 0.1 second delay between each request
3. **Multiple Calls Per Entry**: Each entry may require 2-3 network calls (Wikipedia + Wikidata)
4. **No Caching**: Same Wikipedia pages/Wikidata IDs are looked up repeatedly
5. **Large Test Files**: Some tests download and process large HTML files from GitHub
6. **Network Latency**: Real network requests add unpredictable delays

## Recommendations

1. **Mock Network Calls**: Use `unittest.mock` to mock `WikipediaPage` and `WikidataLookup` classes
2. **Use Test Fixtures**: Pre-download and cache Wikipedia pages/Wikidata data for test files
3. **Skip Network Tests**: Mark network-dependent tests with `@pytest.mark.skipif` or `@unittest.skipUnless`
4. **Reduce Test Data**: Use smaller test files with fewer entries
5. **Parallel Processing**: Process entries in parallel (if API allows)
6. **Reduce Delays**: Lower `delay_seconds` for tests (but risk rate limiting)

## Estimated Total Test Time

Based on static analysis:

- **Fast tests** (no network): < 1 second total
- **Auto-lookup tests**: ~2-4 seconds (2 tests × 1-2 calls each)
- **Add Wikidata IDs tests**: ~5-15 seconds (multiple tests, 15+ entries each)
- **Hide/sort tests with GitHub**: ~20-60 seconds (downloads + many lookups)

**Total estimated time**: 30-80 seconds (depending on network conditions)

## Conclusion

The encyclopedia tests are slow because they perform **real network operations** to download Wikipedia pages and query Wikidata. The tests are designed to verify actual integration with external APIs, which requires internet connectivity and adds significant latency. To speed up tests, consider mocking network calls or using cached test data.












