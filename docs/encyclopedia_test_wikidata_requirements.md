# Encyclopedia Test Wikidata ID Requirements

## Overview
All encyclopedia tests must be updated to require Wikidata IDs for entries. This document outlines the specific changes needed for each test.

## Test Requirements Summary

### Mandatory Changes for All Tests

1. **All test HTML entries must include `wikidataID` attribute**
2. **All test assertions must check for Wikidata IDs**
3. **All test methods must use `normalize_by_wikidata_id()` instead of `normalize_by_wikipedia_url()`**
4. **All test assertions must validate Wikidata ID format (Q or P followed by digits)**

---

## Test-by-Test Changes

### 1. `test_single_entry_synonym_list`

**Current Test HTML:**
```html
<div name="Climate change" term="Climate change" role="ami_entry">
    <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
    <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
</div>
```

**Required Change:**
```html
<div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
    <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
    <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
</div>
```

**Current Assertions:**
```python
assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change'
```

**Required Changes:**
```python
# Validate Wikidata ID is present and correct
assert 'wikidata_id' in group, "Synonym group must have Wikidata ID"
assert group['wikidata_id'] == 'Q7942', f"Wikidata ID should be Q7942, got {group['wikidata_id']}"
assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change'  # Secondary check
```

**Method Calls:**
```python
# Change from:
encyclopedia.normalize_by_wikipedia_url()

# To:
encyclopedia.normalize_by_wikidata_id()
```

---

### 2. `test_multiple_entries_same_wikipedia_url`

**Current Test HTML:**
```html
<div name="Climate change" term="Climate change" role="ami_entry">
    ...
</div>
<div name="climate change" term="climate change" role="ami_entry">
    ...
</div>
```

**Required Change:**
```html
<!-- Both entries must have the SAME Wikidata ID (they're the same concept) -->
<div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
    ...
</div>
<div name="climate change" term="climate change" role="ami_entry" wikidataID="Q7942">
    ...
</div>
```

**Current Assertions:**
```python
assert len(synonym_groups) == 1, f"Should have 1 synonym group (merged), got {len(synonym_groups)}"
```

**Required Changes:**
```python
assert len(synonym_groups) == 1, f"Should have 1 synonym group (merged by Wikidata ID), got {len(synonym_groups)}"
group = list(synonym_groups.values())[0]
assert group['wikidata_id'] == 'Q7942', f"Wikidata ID should be Q7942, got {group['wikidata_id']}"
assert len(group['synonyms']) == 2, f"Should have 2 synonyms (Climate change, climate change)"
```

---

### 3. `test_ethanol_single_entry`

**Required Change:**
```html
<div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
    ...
</div>
```

**Required Assertions:**
```python
assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153 (Ethanol), got {group['wikidata_id']}"
assert group['synonyms'] == ['ethanol'], f"Synonyms should be ['ethanol'], got {group['synonyms']}"
```

---

### 4. `test_hydroxyethane_single_entry`

**Required Change:**
```html
<div name="hydroxyethane" term="hydroxyethane" role="ami_entry" wikidataID="Q153">
    ...
</div>
```

**Note:** Hydroxyethane is the same compound as Ethanol, so they share Wikidata ID Q153.

**Required Assertions:**
```python
assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153 (Ethanol/Hydroxyethane), got {group['wikidata_id']}"
assert group['synonyms'] == ['hydroxyethane'], f"Synonyms should be ['hydroxyethane'], got {group['synonyms']}"
```

---

### 5. `test_ethanol_and_hydroxyethane_separate_entries`

**Current Expected Behavior:** Two separate entries with different Wikipedia URLs

**Required Change:**
```html
<!-- If they're truly different concepts, use different Wikidata IDs -->
<!-- But ethanol and hydroxyethane are the same, so they should have the same ID -->
<!-- This test may need to be updated to use different compounds -->
<div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
    ...
</div>
<div name="hydroxyethane" term="hydroxyethane" role="ami_entry" wikidataID="Q153">
    ...
</div>
```

**OR** (if test is meant to test different concepts):
```html
<!-- Use different compounds with different Wikidata IDs -->
<div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
    ...
</div>
<div name="methanol" term="methanol" role="ami_entry" wikidataID="Q14982">
    ...
</div>
```

**Required Assertions:**
```python
# If same Wikidata ID, they should be grouped together
# If different Wikidata IDs, they should be in separate groups
urls = set(group['wikidata_id'] for group in synonym_groups.values())
expected_ids = {'Q153', 'Q14982'}  # or {'Q153'} if same
assert urls == expected_ids, f"Wikidata IDs should be {expected_ids}, got {urls}"
```

---

### 6. `test_ethanol_and_hydroxyethane_with_merge`

**Required Change:** Same as above - ensure both entries have Wikidata IDs.

**Required Assertions:**
```python
# After merge, check Wikidata IDs
urls = set(group['wikidata_id'] for group in merged_groups.values())
expected_ids = {'Q153'}  # Same Wikidata ID means they're merged
assert urls == expected_ids, f"Wikidata IDs should be {expected_ids}, got {urls}"
```

---

### 7. `test_synonym_list_html_output`

**Required Change:**
```html
<div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
    ...
</div>
<div name="climate change" term="climate change" role="ami_entry" wikidataID="Q7942">
    ...
</div>
```

**Required Assertions:**
```python
# Check for Wikidata ID in HTML output
assert 'wikidataID="Q7942"' in html_content, "Should contain Wikidata ID attribute"
assert 'href="https://www.wikidata.org/wiki/Q7942"' in html_content, "Should contain Wikidata link"
assert 'href="https://en.wikipedia.org/wiki/Climate_change"' in html_content, "Should contain Wikipedia URL link"
```

---

### 8. `test_normalize_by_wikipedia_url`

**Action:** Rename to `test_normalize_by_wikidata_id` and update

**Required Changes:**
```python
def test_normalize_by_wikidata_id(self):
    """Test normalizing entries by Wikidata ID"""
    print("🧪 Testing Wikidata ID normalization...")
    
    encyclopedia = AmiEncyclopedia()
    encyclopedia.create_from_html_file(self.test_html_file)
    
    normalized_entries = encyclopedia.normalize_by_wikidata_id()
    
    assert len(normalized_entries) > 0, "Should have normalized entries"
    
    # Check that entries are grouped by Wikidata ID
    for wikidata_id, entries in normalized_entries.items():
        assert isinstance(entries, list), "Each Wikidata ID should map to a list of entries"
        assert len(entries) > 0, "Each Wikidata ID group should have entries"
        
        # Validate Wikidata ID format
        if wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
            assert re.match(r'^[QP]\d+$', wikidata_id), f"Invalid Wikidata ID format: {wikidata_id}"
            
            # All entries in a group should have the same Wikidata ID
            for entry in entries:
                assert entry.get('wikidata_id') == wikidata_id, "Entries should be grouped by Wikidata ID"
    
    print(f"✅ Normalized into {len(normalized_entries)} groups")
```

---

## Test Data Requirements

### Wikidata IDs to Use in Tests

| Term | Wikidata ID | Notes |
|------|-------------|-------|
| Climate change | Q7942 | Standard Wikipedia page |
| Ethanol | Q153 | Chemical compound |
| Hydroxyethane | Q153 | Same as Ethanol (same compound) |
| Methanol | Q14982 | Different compound (for testing separate entries) |
| Greenhouse gas | Q7942 | Same as Climate change (for testing) |

**Note:** Use actual Wikidata IDs from real data, not made-up IDs.

---

## Validation Checks to Add

### 1. Entry Validation

Add to `create_from_html_content()`:
```python
# Validate that entry has Wikidata ID
if not wikidata_id:
    raise ValueError(f"Entry '{term}' must have Wikidata ID (wikidataID attribute or lookup)")
    
# Validate Wikidata ID format
import re
if not re.match(r'^[QP]\d+$', wikidata_id):
    raise ValueError(f"Invalid Wikidata ID format: {wikidata_id} (must be Q or P followed by digits)")
```

### 2. Test Setup Validation

Add to test setup:
```python
def setUp(self):
    """Set up test fixtures"""
    self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
    # Verify test file has Wikidata IDs
    # (Add validation if needed)
```

### 3. Test Assertion Helpers

Create helper methods:
```python
def assert_has_wikidata_id(self, entry, wikidata_id=None):
    """Assert that entry has valid Wikidata ID"""
    assert 'wikidata_id' in entry, f"Entry {entry.get('term')} must have wikidata_id"
    assert re.match(r'^[QP]\d+$', entry['wikidata_id']), f"Invalid Wikidata ID format: {entry['wikidata_id']}"
    if wikidata_id:
        assert entry['wikidata_id'] == wikidata_id, f"Expected Wikidata ID {wikidata_id}, got {entry['wikidata_id']}"

def assert_synonym_group_has_wikidata_id(self, group, wikidata_id=None):
    """Assert that synonym group has valid Wikidata ID"""
    assert 'wikidata_id' in group, "Synonym group must have wikidata_id"
    assert re.match(r'^[QP]\d+$', group['wikidata_id']), f"Invalid Wikidata ID format: {group['wikidata_id']}"
    if wikidata_id:
        assert group['wikidata_id'] == wikidata_id, f"Expected Wikidata ID {wikidata_id}, got {group['wikidata_id']}"
```

---

## Implementation Checklist

### Test Updates
- [ ] Update all test HTML to include `wikidataID` attributes
- [ ] Update all test assertions to check Wikidata IDs
- [ ] Update all test method calls from `normalize_by_wikipedia_url()` to `normalize_by_wikidata_id()`
- [ ] Add Wikidata ID validation to all tests
- [ ] Update test expectations based on actual Wikidata IDs
- [ ] Add test helper methods for Wikidata ID validation
- [ ] Rename `test_normalize_by_wikipedia_url` to `test_normalize_by_wikidata_id`

### Code Updates (Separate)
- [ ] Update `create_from_html_content()` to extract Wikidata ID
- [ ] Update `normalize_by_wikipedia_url()` to `normalize_by_wikidata_id()`
- [ ] Update `aggregate_synonyms()` to use Wikidata ID
- [ ] Update `create_wiki_normalized_html()` to use Wikidata ID

---

## Testing Strategy

1. **Unit Tests:** Test Wikidata ID extraction and validation
2. **Integration Tests:** Test full workflow with Wikidata IDs
3. **Validation Tests:** Verify all entries have Wikidata IDs
4. **Edge Cases:** Test entries without Wikidata IDs, invalid IDs, etc.

---

## Notes

- **Breaking Change:** All tests must be updated before this refactor can be merged
- **Data Requirements:** Test HTML files must include Wikidata IDs
- **Validation:** Add strict validation to fail fast if Wikidata IDs are missing
- **Error Messages:** Provide clear error messages when Wikidata IDs are missing or invalid






