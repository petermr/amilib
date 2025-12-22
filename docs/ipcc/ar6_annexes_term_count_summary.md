# AR6 Annexes Term Count Summary

**Date:** Saturday, December 6, 2025  
**Location:** `test/resources/ipcc/cleaned_content/`

---

## Critical Issue: Content Loss During Processing

⚠️ **WARNING:** Some annexes have lost ALL content during `de_gatsby` processing.

---

## Term Count Summary Table

| Report | Annex | Type | Raw Terms | Processed Terms | With IDs | Status |
|--------|-------|------|-----------|-----------------|----------|--------|
| WG1 | annex-i-glossary | Glossary | 5 | **0** | **0** | ❌ **LOST** |
| WG1 | annex-ii-acronyms | Acronyms | 0 | **0** | **0** | ⚠️ **EMPTY** |
| WG2 | annex-ii-glossary | Glossary | **106** | **106** | **106** | ✅ **PRESERVED** |
| WG3 | annex-i-glossary | Glossary | 5 | **0** | **0** | ❌ **LOST** |
| WG3 | annex-ii-acronyms | Acronyms | 0 | **0** | **0** | ⚠️ **EMPTY** |
| **TOTAL** | | | **116** | **106** | **106** | **91.4% preserved** |

---

## Detailed Analysis

### ✅ WG2 Annex II - Glossary (WORKING)

**Status:** ✅ **ALL TERMS PRESERVED**

- **Raw file:** 106 terms found
- **Processed (de_gatsby):** 106 terms preserved (100%)
- **With IDs:** 106 terms preserved (100%)
- **File size:** 656KB raw → 329KB processed
- **Structure:** 1,084 paragraphs containing glossary entries

**Conclusion:** Processing pipeline works correctly for WG2 glossary.

---

### ❌ WG1 Annex I - Glossary (CONTENT LOST)

**Status:** ❌ **ALL CONTENT LOST**

- **Raw file:** Only 5 terms found (likely navigation/menu items, not actual glossary)
- **Processed (de_gatsby):** 0 terms (100% loss)
- **With IDs:** 0 terms
- **File size:** 51KB raw → 39 bytes processed (essentially empty)
- **Issue:** Raw file appears to be navigation page, not actual glossary content

**Root Cause:** 
- Downloaded file is only 51KB (too small for a glossary)
- Contains mostly navigation/menu HTML
- Actual glossary content not present in download
- May be JavaScript-loaded content or wrong URL

**Action Required:** 
- Verify correct URL for WG1 Annex I
- Re-download using correct URL pattern
- May need different download method if content is JavaScript-loaded

---

### ❌ WG1 Annex II - Acronyms (EMPTY)

**Status:** ⚠️ **NO TERMS FOUND**

- **Raw file:** 0 acronyms found
- **Processed (de_gatsby):** 0 acronyms
- **With IDs:** 0 acronyms
- **File size:** 51KB raw → 39 bytes processed

**Root Cause:** Same as WG1 Annex I - wrong content downloaded

**Action Required:** Re-download with correct URL

---

### ❌ WG3 Annex I - Glossary (CONTENT LOST)

**Status:** ❌ **ALL CONTENT LOST**

- **Raw file:** Only 5 terms found (likely navigation/menu items)
- **Processed (de_gatsby):** 0 terms (100% loss)
- **With IDs:** 0 terms
- **File size:** 51KB raw → 39 bytes processed

**Root Cause:** Same as WG1 Annex I - wrong content downloaded

**Action Required:** Re-download with correct URL

---

### ❌ WG3 Annex II - Acronyms (EMPTY)

**Status:** ⚠️ **NO TERMS FOUND**

- **Raw file:** 0 acronyms found
- **Processed (de_gatsby):** 0 acronyms
- **With IDs:** 0 acronyms
- **File size:** 51KB raw → 39 bytes processed

**Root Cause:** Same as WG1 Annex I - wrong content downloaded

**Action Required:** Re-download with correct URL

---

## File Structure Comparison

### WG2 Glossary (Working Example)

```
Raw File (gatsby_raw.html):
- Size: 656,376 bytes
- Paragraphs: 1,084
- Text length: 231,688 chars
- Structure: Contains actual glossary content

Processed File (de_gatsby.html):
- Size: 329,334 bytes (50% reduction - navigation removed)
- Paragraphs: 1,084 (100% preserved)
- Text length: 181,226 chars (78% preserved - navigation removed)
- Structure: Content preserved, navigation removed ✅
```

### WG1/WG3 Annexes (Broken)

```
Raw File (gatsby_raw.html):
- Size: ~51,544 bytes (too small)
- Paragraphs: 13 (mostly navigation)
- Text length: 12,996 chars (mostly navigation)
- Structure: Navigation/menu HTML, no actual content ❌

Processed File (de_gatsby.html):
- Size: 39 bytes (essentially empty)
- Paragraphs: 0 (all removed)
- Text length: 0 chars
- Structure: Empty - all content lost ❌
```

---

## Root Cause Analysis

### Problem Identified

1. **Wrong URLs Used:** 
   - Current downloads use: `https://www.ipcc.ch/report/ar6/{report}/chapter/annex-{i|ii}`
   - These URLs may redirect or load navigation pages instead of actual content

2. **JavaScript-Loaded Content:**
   - Annexes may use JavaScript to load content dynamically
   - Headless browser may not be executing JavaScript properly
   - Content may require waiting for page load

3. **Different URL Structure:**
   - Annexes may have different URL patterns than chapters
   - May need: `/annex/glossary/` or `/annex/acronyms/` instead of `/chapter/annex-i`

### Evidence

- WG2 Annex II works because it was downloaded correctly (larger file, actual content)
- WG1/WG3 annexes are identical small files (51KB) suggesting same wrong page
- All show same navigation structure, not glossary/acronyms content

---

## Recommended Actions

### Immediate Actions

1. **Verify Correct URLs:**
   - Check IPCC website for actual annex URLs
   - Test URLs manually in browser
   - Verify content loads correctly

2. **Fix Download URLs:**
   - Update URL patterns in download script
   - May need: `{report}/annex/glossary/` instead of `{report}/chapter/annex-i`
   - Or: `{report}/annex/annex-i/` with different structure

3. **Re-download Failed Annexes:**
   - WG1 Annex I (Glossary)
   - WG1 Annex II (Acronyms)
   - WG3 Annex I (Glossary)
   - WG3 Annex II (Acronyms)

4. **Verify Content After Re-download:**
   - Check file sizes (should be >100KB for glossaries)
   - Count terms before and after processing
   - Ensure 100% preservation

### URL Patterns to Test

```
Current (may be wrong):
- https://www.ipcc.ch/report/ar6/wg1/chapter/annex-i
- https://www.ipcc.ch/report/ar6/wg1/chapter/annex-ii

Possible correct patterns:
- https://www.ipcc.ch/report/ar6/wg1/annex/glossary/
- https://www.ipcc.ch/report/ar6/wg1/annex/acronyms/
- https://www.ipcc.ch/report/ar6/wg1/annex/annex-i/
- https://www.ipcc.ch/report/ar6/wg1/annex/annex-ii/
```

---

## Term Count Methodology

### Glossary Terms Counted As:
1. Paragraphs starting with bold text (term: definition)
2. Definition list terms (`<dt>` elements)
3. Table first column entries (if structured as table)
4. Text matching pattern: `Term: Definition` or `Term—Definition`

### Acronyms Counted As:
1. Table rows with acronym | expansion
2. List items matching: `ACRONYM - Expansion`
3. Definition lists with acronym as term

---

## Preservation Rate

- **Total terms in raw files:** 116
- **Total terms preserved:** 106
- **Preservation rate:** 91.4%

**Note:** Low rate due to WG1/WG3 annexes having wrong content downloaded. If we exclude those:
- **WG2 only:** 106/106 = 100% preservation ✅

---

## Next Steps

1. ✅ **Document issue** (this document)
2. ⏳ **Verify correct URLs** for annexes
3. ⏳ **Fix download script** with correct URLs
4. ⏳ **Re-download failed annexes**
5. ⏳ **Verify term counts** after re-download
6. ⏳ **Add Wikimedia IDs** to all terms (once content is correct)

---

## Files Created

- ✅ `docs/ipcc/ar6_annexes_term_count_summary.md` - This document
- ✅ `scripts/summarize_ipcc_downloads.py` - Download summary script

---

**Status:** ⚠️ **CRITICAL ISSUE IDENTIFIED** - 4 out of 5 annexes have wrong content or lost content during processing.





















