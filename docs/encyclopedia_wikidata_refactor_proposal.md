# Encyclopedia Wikidata ID Refactor Proposal

## Overview
Refactor the encyclopedia module to use **Wikidata IDs** instead of Wikipedia URLs for synonym grouping. This provides a more reliable and canonical way to identify concepts, as Wikidata IDs are unique identifiers that don't change with URL case sensitivity or Wikipedia redirects.

## Current Architecture Issues

### Current Implementation (Wikipedia URL-based)
- **Normalization:** Groups entries by Wikipedia URL
- **Problem:** Wikipedia URLs are case-sensitive and can have variations
- **Problem:** Same concept can have different Wikipedia URLs (e.g., "Climate_change" vs "climate_change")
- **Problem:** Wikipedia redirects create ambiguity

### Proposed Implementation (Wikidata ID-based)
- **Normalization:** Groups entries by Wikidata ID (Q/P IDs)
- **Benefit:** Wikidata IDs are unique, canonical identifiers
- **Benefit:** No case sensitivity issues
- **Benefit:** One concept = one Wikidata ID, regardless of Wikipedia URL variations

---

## Proposed Changes

### 1. Update Entry Extraction to Extract Wikidata ID

**Location:** `amilib/ami_encyclopedia.py:44-118` (in `create_from_html_content`)

**Current Code:**
```python
# Extract wikipedia_url with priority: attribute > explicit link > description links
wikipedia_url = ''
# ... extracts Wikipedia URL ...
entry_dict = {
    'term': term,
    'search_term': search_term,
    'wikipedia_url': wikipedia_url,
    'description_html': description_html,
}
```

**Proposed Change:**
```python
# Extract wikidata_id with priority: attribute > from Wikipedia page > lookup
wikidata_id = ''
# Priority 1: Check if wikidata_id is stored as an attribute on the entry element
wikidata_id = entry_element.get('wikidataID', entry_element.get('wikidata_id', ''))

# Priority 2: If no attribute, check if entry has Wikipedia page and extract Wikidata ID
if not wikidata_id:
    # Check if entry has Wikipedia URL and can extract Wikidata ID from it
    wikipedia_url = entry_element.get('wikipedia_url', '')
    if wikipedia_url:
        # Try to extract Wikidata ID from Wikipedia page
        from amilib.wikimedia import WikipediaPage
        try:
            # Extract page title from URL
            if '/wiki/' in wikipedia_url:
                page_title = wikipedia_url.split('/wiki/')[-1].split('#')[0].split('?')[0]
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(page_title)
                if wikipedia_page:
                    wikidata_url = wikipedia_page.get_wikidata_item()
                    if wikidata_url:
                        # Extract Q/P ID from URL
                        import re
                        match = re.search(r'[Ee]ntity[Pp]age/([QP]\d+)', wikidata_url)
                        if not match:
                            match = re.search(r'/([QP]\d+)(?:#|/|$)', wikidata_url)
                        if match:
                            wikidata_id = match.group(1)
        except Exception as e:
            logger.warning(f"Could not extract Wikidata ID from Wikipedia URL {wikipedia_url}: {e}")

# Priority 3: If still no Wikidata ID, try direct lookup from term
if not wikidata_id and term:
    from amilib.wikimedia import WikidataLookup
    try:
        wikidata_lookup = WikidataLookup()
        qitem, desc, qitems = wikidata_lookup.lookup_wikidata(term)
        if qitem:
            wikidata_id = qitem
    except Exception as e:
        logger.warning(f"Could not lookup Wikidata ID for term {term}: {e}")

entry_dict = {
    'term': term,
    'search_term': search_term,
    'wikidata_id': wikidata_id,  # PRIMARY identifier
    'wikipedia_url': wikipedia_url,  # Secondary (for display)
    'description_html': description_html,
}
```

**Rationale:**
- Extract Wikidata ID as primary identifier
- Try multiple methods to get Wikidata ID
- Keep Wikipedia URL as secondary for display purposes
- Require Wikidata ID for entries (fail if not found)

---

### 2. Change Normalization to Use Wikidata ID

**Location:** `amilib/ami_encyclopedia.py:149-164` (method `normalize_by_wikipedia_url`)

**Current Method:**
```python
def normalize_by_wikipedia_url(self) -> Dict[str, List[Dict]]:
    """Normalize entries by grouping by Wikipedia URL"""
    url_groups = defaultdict(list)
    
    for entry in self.entries:
        wikipedia_url = entry.get('wikipedia_url', '')
        if wikipedia_url:
            normalized_url = self._normalize_wikipedia_url(wikipedia_url)
            url_groups[normalized_url].append(entry)
        else:
            url_groups['no_wikipedia_url'].append(entry)
    
    self.normalized_entries = dict(url_groups)
    return self.normalized_entries
```

**Proposed Change:**
```python
def normalize_by_wikidata_id(self) -> Dict[str, List[Dict]]:
    """Normalize entries by grouping by Wikidata ID"""
    wikidata_groups = defaultdict(list)
    
    for entry in self.entries:
        wikidata_id = entry.get('wikidata_id', '')
        if wikidata_id:
            # Validate Wikidata ID format (Q or P followed by digits)
            import re
            if re.match(r'^[QP]\d+$', wikidata_id):
                wikidata_groups[wikidata_id].append(entry)
            else:
                logger.warning(f"Invalid Wikidata ID format: {wikidata_id}")
                wikidata_groups['invalid_wikidata_id'].append(entry)
        else:
            # Entries without Wikidata IDs cannot be grouped
            wikidata_groups['no_wikidata_id'].append(entry)
    
    self.normalized_entries = dict(wikidata_groups)
    return self.normalized_entries
```

**Rationale:**
- Group by Wikidata ID instead of Wikipedia URL
- Validate Wikidata ID format
- Handle entries without Wikidata IDs separately
- Rename method to reflect new behavior

**Deprecation:**
- Keep `normalize_by_wikipedia_url()` for backward compatibility but mark as deprecated
- Or remove it entirely if breaking changes are acceptable

---

### 3. Update Aggregate Synonyms to Use Wikidata ID

**Location:** `amilib/ami_encyclopedia.py:181-219` (method `aggregate_synonyms`)

**Current Method:**
```python
def aggregate_synonyms(self) -> Dict[str, Dict]:
    """Aggregate synonyms by Wikipedia URL and normalize terms"""
    # Ensure entries are normalized first
    if not self.normalized_entries:
        self.normalize_by_wikipedia_url()
    
    synonym_groups = {}
    
    for wikipedia_url, entries in self.normalized_entries.items():
        if wikipedia_url == 'no_wikipedia_url':
            continue
        # ... groups by Wikipedia URL ...
```

**Proposed Change:**
```python
def aggregate_synonyms(self) -> Dict[str, Dict]:
    """Aggregate synonyms by Wikidata ID and normalize terms"""
    # Ensure entries are normalized first
    if not self.normalized_entries:
        self.normalize_by_wikidata_id()
    
    synonym_groups = {}
    
    for wikidata_id, entries in self.normalized_entries.items():
        if wikidata_id in ('no_wikidata_id', 'invalid_wikidata_id'):
            continue
        
        # Extract all search terms
        search_terms = [entry.get('search_term', '') for entry in entries if entry.get('search_term')]
        
        # Normalize terms (using helper method)
        normalized_terms = self._normalize_terms(search_terms)
        
        # Get canonical term (using helper method)
        canonical_term = self._get_canonical_term(normalized_terms)
        
        # Get Wikipedia URL from first entry (for display)
        wikipedia_url = entries[0].get('wikipedia_url', '') if entries else ''
        
        # Get page title from Wikipedia URL (if available)
        page_title = self._extract_page_title_from_url(wikipedia_url) if wikipedia_url else canonical_term
        
        # Use the best available description (using helper method)
        best_description = self._get_best_description(entries)
        
        synonym_groups[wikidata_id] = {
            'wikidata_id': wikidata_id,  # PRIMARY identifier
            'canonical_term': canonical_term,
            'page_title': page_title,
            'wikipedia_url': wikipedia_url,  # Secondary (for display)
            'search_terms': search_terms,
            'synonyms': list(set(normalized_terms)),
            'description_html': best_description,
            'entry_count': len(entries),
            'source_entries': entries
        }
    
    # Store for later use
    self.synonym_groups = synonym_groups
    return synonym_groups
```

**Rationale:**
- Group by Wikidata ID instead of Wikipedia URL
- Use Wikidata ID as primary identifier in synonym groups
- Keep Wikipedia URL for display purposes
- Handle entries without Wikidata IDs

---

### 4. Remove Wikipedia URL Normalization Method

**Location:** `amilib/ami_encyclopedia.py:166-179` (method `_normalize_wikipedia_url`)

**Action:** Remove or deprecate this method, as it's no longer needed for grouping.

**Rationale:**
- Wikidata IDs don't need normalization (they're already canonical)
- Wikipedia URL normalization was the source of case sensitivity issues

---

### 5. Update HTML Output Generation

**Location:** `amilib/ami_encyclopedia.py:262-318` (method `create_wiki_normalized_html`)

**Current Code:**
```python
# Add entry divs for each synonym group (normalized by Wikipedia URL)
for wikipedia_url, group in synonym_groups.items():
```

**Proposed Change:**
```python
# Add entry divs for each synonym group (normalized by Wikidata ID)
for wikidata_id, group in synonym_groups.items():
    entry_div = ET.SubElement(encyclopedia_div, "div")
    entry_div.attrib["role"] = "ami_entry"
    
    # Add Wikidata ID as primary identifier
    entry_div.attrib["wikidataID"] = wikidata_id
    
    # Add canonical term
    canonical_term = group.get('canonical_term', '')
    if canonical_term:
        entry_div.attrib["term"] = canonical_term
    
    # Add Wikipedia URL link (for display)
    wikipedia_url = group.get('wikipedia_url', '')
    if wikipedia_url:
        wiki_link = ET.SubElement(entry_div, "a")
        wiki_link.attrib["href"] = wikipedia_url
        page_title = group.get('page_title', canonical_term)
        wiki_link.text = page_title if page_title else wikipedia_url
    
    # Add Wikidata link
    wikidata_link = ET.SubElement(entry_div, "a")
    wikidata_link.attrib["href"] = f"https://www.wikidata.org/wiki/{wikidata_id}"
    wikidata_link.text = f"Wikidata: {wikidata_id}"
    
    # Add synonym list
    synonyms = group.get('synonyms', [])
    if synonyms:
        synonym_ul = ET.SubElement(entry_div, "ul")
        synonym_ul.attrib["class"] = "synonym_list"
        for synonym in synonyms:
            synonym_li = ET.SubElement(synonym_ul, "li")
            synonym_li.text = synonym
    
    # Add description if available
    description_html = group.get('description_html', '')
    if description_html:
        # Parse description HTML and append to entry
        from lxml.html import fromstring
        try:
            desc_elem = fromstring(description_html)
            entry_div.append(desc_elem)
        except Exception:
            # If parsing fails, add as text
            desc_p = ET.SubElement(entry_div, "p")
            desc_p.text = description_html
```

**Rationale:**
- Use Wikidata ID as primary identifier in HTML output
- Include both Wikipedia and Wikidata links
- Keep Wikipedia URL for display purposes

---

## Test Updates Required

### 1. All Tests Must Require Wikidata IDs

**Action:** Update all test HTML to include Wikidata IDs in entries.

**Example Test HTML Update:**
```html
<!-- BEFORE -->
<div name="Climate change" term="Climate change" role="ami_entry">
    <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
    <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
</div>

<!-- AFTER -->
<div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
    <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
    <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
</div>
```

### 2. Update Test Assertions

**Current:**
```python
assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change'
```

**Proposed:**
```python
assert group['wikidata_id'] == 'Q7942'  # PRIMARY
assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change'  # Secondary
```

### 3. Update Test Method Calls

**Current:**
```python
encyclopedia.normalize_by_wikipedia_url()
```

**Proposed:**
```python
encyclopedia.normalize_by_wikidata_id()
```

### 4. Add Wikidata ID Validation to Tests

**Proposed:**
```python
# Verify all entries have Wikidata IDs
for entry in encyclopedia.entries:
    assert entry.get('wikidata_id'), f"Entry {entry.get('term')} must have Wikidata ID"
    assert entry['wikidata_id'].startswith(('Q', 'P')), f"Invalid Wikidata ID format: {entry['wikidata_id']}"
```

---

## Test Files to Update

### 1. `test/test_encyclopedia.py`

**Tests to Update:**
- `test_single_entry_synonym_list` - Add wikidataID="Q7942" to entry
- `test_multiple_entries_same_wikipedia_url` - Add same wikidataID to both entries
- `test_ethanol_single_entry` - Add wikidataID="Q153" (Ethanol)
- `test_hydroxyethane_single_entry` - Add wikidataID="Q153" (same as Ethanol - they're synonyms)
- `test_ethanol_and_hydroxyethane_separate_entries` - Add different Wikidata IDs if they're truly different
- `test_ethanol_and_hydroxyethane_with_merge` - Add Wikidata IDs
- `test_synonym_list_html_output` - Add wikidataID to entries
- `test_normalize_by_wikipedia_url` - Rename to `test_normalize_by_wikidata_id` and update
- All other tests that create entries

**Wikidata IDs to Use:**
- Climate change: Q7942
- Ethanol: Q153
- Hydroxyethane: Q153 (same as Ethanol - they're the same compound)
- (Add more as needed)

---

## Implementation Checklist

### Phase 1: Core Implementation
- [ ] Update `create_from_html_content()` to extract Wikidata ID
- [ ] Rename `normalize_by_wikipedia_url()` to `normalize_by_wikidata_id()`
- [ ] Update `aggregate_synonyms()` to use Wikidata ID
- [ ] Remove or deprecate `_normalize_wikipedia_url()`
- [ ] Update `create_wiki_normalized_html()` to use Wikidata ID

### Phase 2: Test Updates
- [ ] Update all test HTML to include `wikidataID` attributes
- [ ] Update all test assertions to check Wikidata IDs
- [ ] Update all test method calls to use `normalize_by_wikidata_id()`
- [ ] Add Wikidata ID validation to tests
- [ ] Remove skip decorators from synonym tests

### Phase 3: Validation
- [ ] Verify all tests pass
- [ ] Verify Wikidata ID extraction works correctly
- [ ] Verify synonym grouping works with Wikidata IDs
- [ ] Verify HTML output includes Wikidata IDs

---

## Benefits of This Approach

1. **Canonical Identification:** Wikidata IDs are unique identifiers, not URLs
2. **No Case Sensitivity:** Wikidata IDs don't have case sensitivity issues
3. **Better Synonym Grouping:** Entries with same Wikidata ID are guaranteed to be the same concept
4. **More Reliable:** Wikidata IDs are stable identifiers that don't change with URL redirects
5. **Better Integration:** Wikidata IDs can be used for additional data lookup and linking

---

## Migration Notes

- **Breaking Change:** This is a breaking change - existing code using Wikipedia URL normalization will need updates
- **Backward Compatibility:** Consider keeping `normalize_by_wikipedia_url()` as deprecated method that calls `normalize_by_wikidata_id()` internally
- **Data Migration:** Existing encyclopedia entries without Wikidata IDs will need to be enriched

---

## Additional Considerations

### Handling Missing Wikidata IDs

**Option 1: Require Wikidata IDs (Fail Fast)**
- Raise exception if entry doesn't have Wikidata ID
- Force enrichment before processing

**Option 2: Auto-Lookup Missing IDs**
- Automatically lookup Wikidata ID for entries without one
- Use Wikipedia URL or term for lookup

**Option 3: Skip Entries Without IDs**
- Process only entries with Wikidata IDs
- Log warnings for entries without IDs

**Recommendation:** Use Option 2 (Auto-Lookup) with Option 1 as fallback (fail if lookup fails)

---

## Testing Strategy

1. **Unit Tests:** Test Wikidata ID extraction, normalization, and aggregation
2. **Integration Tests:** Test full workflow with Wikidata IDs
3. **Validation Tests:** Verify Wikidata ID format and uniqueness
4. **Edge Cases:** Test entries without Wikidata IDs, invalid IDs, etc.





