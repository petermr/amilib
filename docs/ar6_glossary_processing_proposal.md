# AR6 Glossary/Acronym Processing Proposal

**Date:** December 10, 2025  
**System Date:** Wed Dec 10 09:43:02 GMT 2025

## Overview

Create semantic dictionaries from PDF Glossaries/Acronyms for all AR6 reports. The raw HTML has been created from PDFs, but needs processing to:
1. Detect sections and paragraphs
2. Join pages seamlessly
3. Detect section headings
4. Detect italics (create as hyperlinks to other entries)

## Current State

### Files Available
Based on `ar6_manifest.md`, the following PDF glossaries/acronyms need processing:

| Report | Component | File Type | Size | Status |
|--------|-----------|-----------|------|--------|
| WG1 | Annex I (Glossary) | PDF | 588,085 bytes | ⚠️ Needs processing |
| WG1 | Annex II (Acronyms) | PDF | 72,098 bytes | ⚠️ Needs processing |
| WG2 | Annex III (Acronyms) | PDF | 82,128 bytes | ✅ Downloaded (needs processing) |
| WG3 | Annex I (Glossary) | PDF | 272,992 bytes | ⚠️ Needs processing |
| WG3 | Annex VI (Acronyms) | PDF | 133,924 bytes | ⚠️ Needs processing |
| SYR | Annex I (Glossary) | PDF | 82,984 bytes | ⚠️ Needs processing |
| SYR | Annex II (Acronyms) | PDF | 82,984 bytes | ⚠️ Needs processing |

### Raw HTML Structure

From examining `wg3/annex-vi-acronyms/annex-vi-acronyms.html`, the converted HTML has:

1. **Position-based layout:**
   - Each text element is in a `<div>` with `left`, `right`, `top` attributes
   - Absolute positioning from PDF coordinates
   - Example: `<div left="309.26" right="330.91" top="625.45">`

2. **Font information in spans:**
   - Font family indicates style: `HPFPTY+FrutigerLTPro-BlackCn` (bold), `HPFPTY+FrutigerLTPro-CondensedIta` (italic)
   - Font size: `font-size: 9.5`
   - Fill color: `fill: [0.339]` (darker = bold/acronym), `fill: [0]` (normal text)

3. **Entry structure:**
   - Acronym entries: Bold acronym (left column) + definition (right column)
   - Glossary entries: Term (bold) + definition (normal)
   - Multi-line entries span multiple divs

4. **Page boundaries:**
   - Pages are separated but need seamless joining
   - Page breaks may interrupt entries

## Proposed Processing Pipeline

### Stage 1: Page Joining and Structure Detection

**Goal:** Convert position-based HTML to semantic structure

#### 1.1 Remove Page Boundaries
- **Input:** Raw HTML with page-separated divs
- **Process:**
  - Remove page break markers
  - Merge consecutive divs that belong to same entry
  - Detect when an entry spans page boundaries
- **Output:** Continuous HTML without page breaks

#### 1.2 Detect Entry Boundaries
- **Input:** Continuous HTML
- **Process:**
  - **Acronyms:** Detect bold text at left margin (x0 ~309-340) followed by definition at right margin (x0 ~388+)
  - **Glossary:** Detect bold term followed by definition
  - Use vertical spacing (`top` attribute) to detect new entries
  - Entry gap threshold: >15-20px vertical spacing
- **Output:** Identified entry boundaries

#### 1.3 Group Entry Components
- **Input:** Entry boundaries
- **Process:**
  - Group all divs belonging to same entry
  - Handle multi-line definitions
  - Preserve formatting within entries
- **Output:** Structured entries as HTML elements

### Stage 2: Section Detection

**Goal:** Identify section headings (e.g., "A", "B", "C" sections)

#### 2.1 Detect Section Headings
- **Input:** Structured entries
- **Process:**
  - Look for large, bold text at top of page/section
  - Common patterns: Single letter (A-Z), "Numbers", "Special Characters"
  - Font size typically larger than entries (10-12pt vs 9.5pt)
  - Position: Usually centered or left-aligned at page top
- **Output:** Section headings identified

#### 2.2 Create Section Hierarchy
- **Input:** Section headings + entries
- **Process:**
  - Wrap entries in section containers (`<section>` or `<div class="section">`)
  - Add section heading as `<h2>` or `<h3>`
  - Maintain alphabetical ordering
- **Output:** Hierarchical structure with sections

### Stage 3: Paragraph and Entry Structure

**Goal:** Create semantic paragraph structure

#### 3.1 Create Entry Elements
- **Input:** Grouped entry components
- **Process:**
  - Create `<div class="entry">` for each entry
  - Extract term/acronym: Bold text from left column
  - Extract definition: Normal text from right column
  - Structure as:
    ```html
    <div class="entry" id="entry-{term}">
      <span class="term">{term}</span>
      <span class="definition">{definition}</span>
    </div>
    ```
- **Output:** Structured entry elements

#### 3.2 Detect Paragraphs within Definitions
- **Input:** Entry definitions
- **Process:**
  - Detect paragraph breaks within multi-paragraph definitions
  - Use vertical spacing or explicit paragraph markers
  - Wrap in `<p>` tags
- **Output:** Paragraph-structured definitions

### Stage 4: Italic Detection and Hyperlink Creation

**Goal:** Convert italicized terms to hyperlinks

#### 4.1 Detect Italics
- **Input:** Entry definitions
- **Process:**
  - Identify spans with italic font-family: `*CondensedIta*`, `*Italic*`
  - Extract italic text content
  - Normalize text (remove punctuation, lowercase for matching)
- **Output:** List of italicized terms per entry

#### 4.2 Match Italics to Entries
- **Input:** Italicized terms + all entries
- **Process:**
  - For each italic term:
    - Normalize: lowercase, remove punctuation
    - Search for matching entry term (fuzzy matching)
    - Handle variations: plural/singular, case differences
    - Create hyperlink: `<a href="#entry-{matched-term}">{italic-text}</a>`
  - Replace italic spans with hyperlinks
- **Output:** Definitions with hyperlinked cross-references

#### 4.3 Handle Ambiguous Matches
- **Input:** Multiple potential matches
- **Process:**
  - Prefer exact matches
  - Use context (surrounding text) to disambiguate
  - Log ambiguous cases for manual review
- **Output:** Best-match hyperlinks

### Stage 5: Semantic Enhancement

**Goal:** Add semantic IDs and metadata

#### 5.1 Add Semantic IDs
- **Input:** Structured entries
- **Process:**
  - Generate unique IDs: `{report}-{annex}-entry-{normalized-term}`
  - Example: `wg3-annex-vi-entry-ndc`
  - Add `id` attribute to entry divs
- **Output:** Entries with semantic IDs

#### 5.2 Add Metadata
- **Input:** Entries with IDs
- **Process:**
  - Add `data-report`, `data-annex`, `data-type` attributes
  - Add `data-section` for section grouping
  - Add `data-entry-number` for ordering
- **Output:** Rich metadata on entries

#### 5.3 Create Dictionary Index
- **Input:** All entries
- **Process:**
  - Generate alphabetical index
  - Link to entry IDs
  - Group by first letter
- **Output:** Navigation index

## Implementation Approach

### Phase 1: Core Processing (Stages 1-3)
1. **Page Joining Module**
   - Function: `join_pages(html_elem)` → continuous HTML
   - Uses: Vertical position analysis, gap detection

2. **Entry Detection Module**
   - Function: `detect_entries(html_elem, entry_type='acronym')` → list of entries
   - Uses: Position analysis, font-weight detection, spacing

3. **Section Detection Module**
   - Function: `detect_sections(html_elem)` → section boundaries
   - Uses: Font size, position, pattern matching

4. **Structure Creation Module**
   - Function: `create_entry_structure(entries)` → structured HTML
   - Uses: DOM manipulation, element grouping

### Phase 2: Cross-Reference Processing (Stage 4)
1. **Italic Detection Module**
   - Function: `detect_italics(html_elem)` → list of italic spans
   - Uses: Font-family analysis, CSS parsing

2. **Term Matching Module**
   - Function: `match_terms(italic_text, all_entries)` → best match
   - Uses: String normalization, fuzzy matching, Levenshtein distance

3. **Hyperlink Creation Module**
   - Function: `create_hyperlinks(html_elem, matches)` → updated HTML
   - Uses: DOM manipulation, link insertion

### Phase 3: Semantic Enhancement (Stage 5)
1. **ID Generation Module**
   - Function: `add_semantic_ids(html_elem, report, annex)` → HTML with IDs
   - Uses: Term normalization, ID generation

2. **Metadata Module**
   - Function: `add_metadata(html_elem, metadata_dict)` → enriched HTML
   - Uses: Attribute addition

3. **Index Generation Module**
   - Function: `create_index(entries)` → index HTML
   - Uses: Sorting, grouping, link generation

## Technical Details

### Entry Detection Algorithm

```python
def detect_entry_boundaries(divs, entry_type='acronym'):
    """
    Detect entry boundaries based on:
    - Vertical spacing (gap > threshold)
    - Font weight (bold = term/acronym)
    - Horizontal position (left column = term, right = definition)
    """
    entries = []
    current_entry = []
    
    for i, div in enumerate(divs):
        # Calculate vertical gap from previous div
        if i > 0:
            gap = div.top - divs[i-1].bottom
        
        # New entry if:
        # 1. Large vertical gap (>20px)
        # 2. Bold text at left margin (term/acronym)
        if gap > ENTRY_GAP_THRESHOLD or is_term_start(div):
            if current_entry:
                entries.append(current_entry)
            current_entry = [div]
        else:
            current_entry.append(div)
    
    return entries
```

### Italic Detection Algorithm

```python
def detect_italics(html_elem):
    """
    Find all italic spans by checking font-family attribute
    """
    italics = []
    for span in html_elem.xpath('//span[@style]'):
        style = span.get('style', '')
        if 'Ita' in style or 'Italic' in style:
            text = ''.join(span.itertext())
            italics.append({
                'element': span,
                'text': text,
                'normalized': normalize_term(text)
            })
    return italics
```

### Term Matching Algorithm

```python
def match_term(italic_text, all_entries, threshold=0.8):
    """
    Match italicized term to entry using fuzzy matching
    """
    normalized_italic = normalize_term(italic_text)
    best_match = None
    best_score = 0
    
    for entry in all_entries:
        entry_term = normalize_term(entry.term)
        score = similarity(normalized_italic, entry_term)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = entry
    
    return best_match
```

## File Structure

```
scripts/
  glossary_processor/
    __init__.py
    page_joiner.py          # Stage 1.1
    entry_detector.py        # Stage 1.2-1.3
    section_detector.py     # Stage 2
    structure_creator.py     # Stage 3
    italic_detector.py      # Stage 4.1
    term_matcher.py          # Stage 4.2-4.3
    hyperlink_creator.py     # Stage 4.2
    semantic_enhancer.py     # Stage 5
    glossary_processor.py    # Main orchestrator
```

## Testing Strategy

1. **Unit Tests:** Each module tested independently
2. **Integration Tests:** Full pipeline on sample files
3. **Validation Tests:** 
   - Verify all entries detected
   - Verify all italics converted to links
   - Verify links point to valid entries
   - Manual review of ambiguous cases

## Output Format

### Structured HTML Output

```html
<div class="glossary" data-report="wg3" data-annex="vi" data-type="acronyms">
  <h1>Annex VI: Acronyms</h1>
  
  <section class="section" data-letter="A">
    <h2>A</h2>
    
    <div class="entry" id="wg3-annex-vi-entry-aviation">
      <span class="term">AVI</span>
      <span class="definition">
        <p>Aviation sector abbreviation</p>
      </span>
    </div>
    
    <div class="entry" id="wg3-annex-vi-entry-ndc">
      <span class="term">NDC</span>
      <span class="definition">
        <p>Nationally Determined Contribution. See also <a href="#wg3-annex-vi-entry-ndc">NDC</a>.</p>
      </span>
    </div>
  </section>
  
  <!-- More sections... -->
</div>
```

## Next Steps

1. **Review and Approve:** This proposal
2. **Implement Phase 1:** Core processing modules
3. **Test on Sample:** WG3 Annex VI (Acronyms) - smallest file
4. **Iterate:** Refine algorithms based on results
5. **Scale:** Process all 7 glossary/acronym files
6. **Validate:** Manual review of cross-references

## Questions for Discussion

1. **Entry Detection:** Should we use machine learning for better entry boundary detection?
2. **Italic Matching:** How strict should fuzzy matching be? (threshold)
3. **Cross-References:** Should we link to entries in other reports/annexes?
4. **Output Format:** Prefer HTML, JSON, or both?
5. **Validation:** What level of manual review is acceptable?

---

**Status:** Proposal - Awaiting Approval  
**Author:** AI Assistant  
**Date:** December 10, 2025

