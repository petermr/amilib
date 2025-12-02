# Encyclopedia Revised Interaction Model

**Date**: 2025-12-02  
**Status**: Proposal - Under Review

## Overview

Revised interaction model for encyclopedia entries with automatic collapse and category-based interaction.

## Entry Categories

Each entry falls into one of these categories:

1. **True Wikipedia Entry**
   - Valid Wikipedia page found
   - Content matches the term
   - Appropriate for encyclopedia

2. **No Wikipedia Entry Found**
   - Wikipedia lookup returned no results
   - Term has no Wikipedia page

3. **False Wikipedia Entry**
   - Wikipedia page found but content doesn't match term
   - Wrong match (e.g., term "compensation" matches wrong page)
   - User needs to reject/correct

4. **Too General Wikipedia Entry**
   - Wikipedia page found but too broad/general
   - Not specific enough for encyclopedia context
   - User may want to hide or find more specific page

5. **Disambiguation Page Found**
   - Wikipedia disambiguation page detected
   - Multiple possible targets
   - User needs to select correct target

## Automatic Collapse

**Agreement**: ✅ **AGREE** - This is a good approach

**Implementation**:
- **Case variants**: Automatically collapse entries with same Wikidata ID but different case
  - Example: "Greenhouse Gas", "greenhouse gas", "GREENHOUSE GAS" → single entry
  - All case variants shown in synonym list

- **Synonyms**: Automatically collapse entries with same Wikidata ID
  - All synonyms shown in single HTML list
  - No checkbox needed - always merged

**Benefits**:
- Reduces clutter
- Shows all variants clearly
- User can see all related terms
- Cleaner interface

**Current Status**: 
- ✅ Already implemented in `aggregate_synonyms()`
- ✅ Case variants preserved in synonyms list
- ✅ Single entry per Wikidata ID

## Disambiguation Interaction

**Agreement**: ✅ **AGREE** - LISTBOX is the right approach

**Proposed Implementation**:

### Option 1: LISTBOX with Disambiguation Options from Target Page

**When**: Disambiguation page detected

**Display**:
```html
<select class="disambiguation-selector" data-entry-id="entry_001">
    <option value="">-- Select Wikipedia page --</option>
    <option value="https://en.wikipedia.org/wiki/Page1" data-wikidata="Q1">Page 1</option>
    <option value="https://en.wikipedia.org/wiki/Page2" data-wikidata="Q2">Page 2</option>
    <option value="https://en.wikipedia.org/wiki/Page3" data-wikidata="Q3">Page 3</option>
</select>
```

**Source**: Parse disambiguation page HTML to extract options
- Extract from "may refer to:" list
- Extract from disambiguation template
- Show page titles and Wikidata IDs

**Pros**:
- Shows actual options from Wikipedia
- User can see all possibilities
- Can select correct target

**Cons**:
- Requires parsing disambiguation page HTML
- May need to fetch page content

### Option 2: LISTBOX with Other Options (Alternative Pages)

**When**: User wants to see alternative Wikipedia pages

**Display**:
```html
<select class="alternative-pages-selector" data-entry-id="entry_001">
    <option value="">-- Select alternative page --</option>
    <option value="https://en.wikipedia.org/wiki/Alternative1">Alternative 1</option>
    <option value="https://en.wikipedia.org/wiki/Alternative2">Alternative 2</option>
</select>
```

**Source**: 
- Search results from Wikipedia
- Related pages
- User-suggested alternatives

**Use Case**: When current Wikipedia page is wrong or too general

## Questions for Clarification

### 1. Category Detection

**Q**: How do we detect "False Wikipedia Entry"?
- **Option A**: User marks as false (manual)
- **Option B**: Automatic detection (how? content similarity?)
- **Option C**: Both (auto-detect, user can override)

**Q**: How do we detect "Too General Wikipedia Entry"?
- **Option A**: User marks as too general (manual)
- **Option B**: Automatic detection (how? page size? content analysis?)
- **Option C**: Both (auto-detect, user can override)

### 2. Disambiguation LISTBOX

**Q**: Which approach for disambiguation?
- **Option 1**: LISTBOX with options from disambiguation page (parse "may refer to:" list)
- **Option 2**: LISTBOX with other options (alternative pages from search)
- **Option 3**: Both (disambiguation options + alternative pages)

**Q**: When should LISTBOX appear?
- **Option A**: Only when disambiguation page detected
- **Option B**: Always available (for finding alternatives)
- **Option C**: When disambiguation OR when user wants alternatives

### 3. User Actions per Category

**Q**: What actions should be available for each category?

| Category | Actions Needed |
|----------|----------------|
| True Wikipedia Entry | None? Or "Mark as false/general"? |
| No Wikipedia Entry Found | Hide? Search alternative? |
| False Wikipedia Entry | LISTBOX to select correct page? Hide? |
| Too General Wikipedia Entry | LISTBOX to select more specific page? Hide? |
| Disambiguation Page | LISTBOX to select target page |

### 4. Automatic Collapse Details

**Q**: Should automatic collapse happen:
- **Option A**: Always (no user control)
- **Option B**: By default, but user can expand
- **Option C**: User can toggle collapse/expand

**Q**: How to display collapsed synonyms?
- **Option A**: Always visible in list
- **Option B**: Collapsible section (expand/collapse)
- **Option C**: Tooltip/hover to see all

## Proposed Implementation

### 1. Entry Classification

Add method to classify each entry:
```python
def _classify_entry(self, entry: Dict) -> str:
    """Classify entry into category"""
    # Returns: "true_wikipedia", "no_wikipedia", "false_wikipedia", 
    #          "too_general", "disambiguation"
```

### 2. Automatic Collapse

Already implemented:
- ✅ `aggregate_synonyms()` groups by Wikidata ID
- ✅ Case variants preserved in synonyms list
- ✅ Single entry per Wikidata ID

**Enhancement needed**:
- Ensure case variants are always collapsed (currently done)
- Display all variants in synonym list (currently done)

### 3. Disambiguation LISTBOX

**Current**: Basic selector structure exists

**Enhancement needed**:
- Parse disambiguation page to extract options
- Populate LISTBOX with actual options
- Handle selection and update entry

### 4. Category-Based Checkboxes

**Proposed**: Different checkboxes/actions based on category

| Category | Checkboxes/Actions |
|----------|-------------------|
| True Wikipedia | None (or "Mark as false/general") |
| No Wikipedia | Hide checkbox |
| False Wikipedia | LISTBOX (select correct) + Hide checkbox |
| Too General | LISTBOX (select specific) + Hide checkbox |
| Disambiguation | LISTBOX (select target) |

## Recommendations

### ✅ Agree With

1. **Automatic collapse of case and synonyms**: ✅ **EXCELLENT IDEA**
   - Reduces clutter
   - Shows relationships clearly
   - Already mostly implemented in `aggregate_synonyms()`
   - Should be the default behavior

2. **LISTBOX for disambiguation**: ✅ **RIGHT APPROACH**
   - Better than checkbox
   - Allows selection of specific target
   - User can see all options
   - Can populate from `WikipediaPage.get_disambiguation_list()`

3. **Category-based interaction**: ✅ **GOOD STRUCTURE**
   - Clear separation of concerns
   - Different actions per category
   - Makes UI more intuitive

### 🤔 Need Clarification

1. **False Wikipedia Entry detection**: 
   - **Question**: Automatic detection or manual marking?
   - **Suggestion**: Start with manual (user marks as false), later add automatic (content similarity check)

2. **Too General detection**: 
   - **Question**: Automatic detection or manual marking?
   - **Suggestion**: Start with manual (user marks as too general), later add automatic (page size/content analysis)

3. **LISTBOX source**: 
   - **Question**: Disambiguation options vs. alternative pages?
   - **Recommendation**: 
     - **For disambiguation pages**: Use Option A (parse disambiguation list from page)
     - **For false/too general**: Use Option B (search for alternative pages)
     - **Implementation**: `WikipediaPage.get_disambiguation_list()` already exists

4. **User actions per category**: 
   - **Question**: What actions should be available?
   - **Proposed**:
     - True Wikipedia: None (or optional "Mark as false/general")
     - No Wikipedia: Hide checkbox
     - False Wikipedia: LISTBOX (select correct) + Hide checkbox
     - Too General: LISTBOX (select specific) + Hide checkbox
     - Disambiguation: LISTBOX (select target from disambiguation options)

### 💡 Suggestions

1. **Category indicator**: Add visual indicator for each category
   - Icon or badge showing category
   - Color coding

2. **LISTBOX enhancement**: 
   - Show page preview on hover
   - Show Wikidata ID
   - Show page description

3. **Automatic collapse UI**:
   - Show count of collapsed entries
   - Allow expand to see individual entries
   - Highlight when entries are collapsed

## Next Steps

1. **Clarify category detection**: How to detect false/too general automatically?
2. **Clarify LISTBOX source**: Disambiguation options or alternative pages?
3. **Design category-based UI**: What controls per category?
4. **Implement disambiguation parsing**: Extract options from disambiguation pages
5. **Update checkbox logic**: Category-based checkbox display

## Current Implementation Status

- ✅ Automatic collapse: **IMPLEMENTED** (aggregate_synonyms)
- ✅ Case variant preservation: **IMPLEMENTED**
- ✅ Disambiguation detection: **IMPLEMENTED** (_is_disambiguation_page)
- ⚠️ Disambiguation LISTBOX: **PARTIALLY IMPLEMENTED** (structure exists, needs option parsing)
- ❌ Category classification: **NOT IMPLEMENTED**
- ❌ False/Too General detection: **NOT IMPLEMENTED**

