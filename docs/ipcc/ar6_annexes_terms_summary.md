# AR6 Annexes - Glossary and Acronyms Term Count Summary

**Date:** Saturday, December 6, 2025  
**Location:** `test/resources/ipcc/cleaned_content/`

---

## Summary Table

| Report | Annex | Type | Raw File Size | Processed Size | Paragraphs | Content Status | Terms Status |
|--------|-------|------|---------------|----------------|-------------|----------------|--------------|
| WG1 | annex-i-glossary | Glossary | 51,544 bytes | **39 bytes** | 0 | ❌ **LOST** | **0 terms** |
| WG1 | annex-ii-acronyms | Acronyms | 51,544 bytes | **39 bytes** | 0 | ❌ **LOST** | **0 terms** |
| WG2 | annex-ii-glossary | Glossary | **656,376 bytes** | **329,334 bytes** | **1,084** | ✅ **PRESERVED** | **~100-200+ terms** |
| WG3 | annex-i-glossary | Glossary | 51,542 bytes | **39 bytes** | 0 | ❌ **LOST** | **0 terms** |
| WG3 | annex-ii-acronyms | Acronyms | 51,544 bytes | **39 bytes** | 0 | ❌ **LOST** | **0 terms** |

---

## Key Findings

### ✅ WG2 Annex II - Glossary

**Status:** ✅ **Content Preserved Successfully**

- **File Size:** 656 KB → 329 KB (50% reduction = navigation removed)
- **Paragraphs:** 1,084 paragraphs preserved
- **Text Content:** 181,226 characters preserved
- **Structure:** Contains actual glossary entries
- **Estimated Terms:** 100-200+ glossary terms (exact count requires parsing)

**Conclusion:** Processing pipeline works correctly when correct content is downloaded.

---

### ❌ WG1/WG3 Annexes

**Status:** ❌ **All Content Lost**

**Common Pattern:**
- All failed annexes: **51 KB raw files** (too small)
- All processed to: **39 bytes** (essentially empty)
- All contain: Navigation/menu HTML only
- All missing: Actual glossary/acronyms content

**Root Cause:** Wrong URLs used for download - getting navigation pages instead of actual content.

**Evidence:**
- Identical file sizes (51KB) for all failed downloads
- Same navigation structure in all files
- No actual glossary/acronyms content present

---

## Content Preservation Analysis

### Processing Pipeline (de_gatsby)

**What it does:**
1. Removes navigation elements
2. Removes tooltips and buttons
3. Removes style attributes
4. Preserves content paragraphs and structure

**Result:**
- ✅ **WG2:** Content preserved (navigation removed, content kept)
- ❌ **WG1/WG3:** Nothing preserved (only navigation was present)

**Conclusion:** Processing is working correctly. Issue is **wrong content downloaded**.

---

## Term Count Methodology

### Glossary Terms

Counted by identifying:
1. Paragraphs starting with bold text (term: definition pattern)
2. Definition list terms (`<dt>` elements)
3. Table structures (term | definition columns)
4. Pattern: `Term: Definition` or `Term—Definition`

### Acronyms

Counted by identifying:
1. Table rows with acronym | expansion
2. List items: `ACRONYM - Expansion`
3. Definition lists with acronym as term

### Current Counts

| Annex | Raw Terms Found | Processed Terms | Notes |
|-------|----------------|-----------------|-------|
| WG1 Glossary | 5 | 0 | Navigation items, not actual terms |
| WG1 Acronyms | 138 | 0 | Navigation menu items, not acronyms |
| WG2 Glossary | ~100-200+ | ~100-200+ | Actual glossary terms (exact count needs parsing) |
| WG3 Glossary | 5 | 0 | Navigation items, not actual terms |
| WG3 Acronyms | 138 | 0 | Navigation menu items, not acronyms |

**Note:** Exact term counts for WG2 require parsing term-definition pairs from the 1,084 paragraphs.

---

## Critical Issues Identified

### Issue 1: Wrong URLs

**Problem:** Download URLs return navigation pages, not actual content

**Evidence:**
- All failed downloads: 51KB files (navigation only)
- WG2 success: 656KB file (actual content)
- Identical file sizes suggest same wrong page downloaded

**Solution:** Investigate and fix URL patterns

### Issue 2: Content Loss

**Problem:** When wrong content is downloaded, processing removes everything

**Evidence:**
- Raw files contain only navigation
- Processing removes navigation (correct behavior)
- Result: Empty files

**Solution:** Fix downloads first, then processing will work

---

## Recommended Actions

### Priority 1: Fix Downloads

1. **Investigate Correct URLs:**
   - Check IPCC website for actual annex URLs
   - Test URLs manually in browser
   - Compare with WG2 successful download

2. **Update Download Script:**
   - Fix URL patterns in `scripts/process_ar6_annexes.py`
   - Test with one annex first
   - Verify file size >100KB before proceeding

3. **Re-download Failed Annexes:**
   - WG1 Annex I (Glossary)
   - WG1 Annex II (Acronyms)
   - WG3 Annex I (Glossary)
   - WG3 Annex II (Acronyms)

### Priority 2: Verify Content

1. **Check File Sizes:**
   - Glossaries should be >100KB
   - Acronyms should be >50KB
   - Files <100KB likely wrong content

2. **Count Terms:**
   - Parse actual glossary terms from paragraphs
   - Count acronyms from lists/tables
   - Verify preservation rate = 100%

3. **Add Wikimedia IDs:**
   - Only proceed after content is verified
   - Add Wikidata IDs first
   - Add Wiktionary IDs as fallback

---

## Files Created

- ✅ `docs/ipcc/ar6_annexes_term_count_final.md` - Detailed analysis
- ✅ `docs/ipcc/ar6_annexes_terms_summary.md` - This summary
- ✅ `scripts/summarize_ipcc_downloads.py` - Download summary script

---

## Conclusion

**Current Status:** ⚠️ **CRITICAL ISSUE**

- **4 out of 5 annexes** have wrong content (navigation pages)
- **Only WG2 Annex II** has correct content
- **Processing pipeline works** when correct content is downloaded
- **Issue is download URLs**, not processing

**Next Step:** Fix download URLs and re-download failed annexes.

---

**Generated:** Saturday, December 6, 2025






















