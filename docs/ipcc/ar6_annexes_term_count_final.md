# AR6 Annexes Term Count Summary - Final Report

**Date:** Saturday, December 6, 2025  
**Location:** `test/resources/ipcc/cleaned_content/`

---

## Executive Summary

⚠️ **CRITICAL ISSUE:** 4 out of 5 annexes have **lost all content** during `de_gatsby` processing. Only WG2 Annex II (Glossary) preserved content.

---

## Summary Table

| Report | Annex | Type | Raw File Size | Processed Size | Content Status | Terms Preserved |
|--------|-------|------|---------------|----------------|----------------|-----------------|
| WG1 | annex-i-glossary | Glossary | 51,544 bytes | **39 bytes** | ❌ **LOST** | 0% |
| WG1 | annex-ii-acronyms | Acronyms | 51,544 bytes | **39 bytes** | ❌ **LOST** | 0% |
| WG2 | annex-ii-glossary | Glossary | **656,376 bytes** | **329,334 bytes** | ✅ **PRESERVED** | ~100% |
| WG3 | annex-i-glossary | Glossary | 51,542 bytes | **39 bytes** | ❌ **LOST** | 0% |
| WG3 | annex-ii-acronyms | Acronyms | 51,544 bytes | **39 bytes** | ❌ **LOST** | 0% |

---

## Detailed Analysis

### ✅ WG2 Annex II - Glossary (SUCCESS)

**File Sizes:**
- Raw: 656,376 bytes (656 KB)
- Processed: 329,334 bytes (329 KB)
- Reduction: 50% (navigation removed, content preserved)

**Content Structure:**
- **Paragraphs:** 1,084 paragraphs
- **Text Content:** 181,226 characters preserved
- **Structure:** Contains actual glossary entries with terms and definitions

**Status:** ✅ **Content fully preserved** - Processing pipeline works correctly

**Estimated Terms:** ~100-200+ glossary terms (exact count requires parsing term-definition pairs)

---

### ❌ WG1 Annex I - Glossary (FAILED)

**File Sizes:**
- Raw: 51,544 bytes (51 KB) - **Too small for a glossary**
- Processed: 39 bytes - **Essentially empty**

**Content Analysis:**
- Raw file contains mostly navigation/menu HTML
- No actual glossary content present
- Only 13 paragraphs (all navigation)
- Text content: 12,996 chars (mostly navigation)

**Root Cause:** Wrong URL or wrong page downloaded - navigation page instead of glossary content

**Status:** ❌ **No content to preserve** - Wrong page downloaded

---

### ❌ WG1 Annex II - Acronyms (FAILED)

**File Sizes:**
- Raw: 51,544 bytes (51 KB) - **Too small for acronyms list**
- Processed: 39 bytes - **Essentially empty**

**Content Analysis:**
- Raw file contains navigation HTML
- 138 list items found, but these are navigation menu items, not acronyms
- No actual acronym content present

**Root Cause:** Wrong URL or wrong page downloaded

**Status:** ❌ **No content to preserve** - Wrong page downloaded

---

### ❌ WG3 Annex I - Glossary (FAILED)

**File Sizes:**
- Raw: 51,542 bytes (51 KB) - **Too small for a glossary**
- Processed: 39 bytes - **Essentially empty**

**Content Analysis:**
- Identical to WG1 Annex I
- Navigation page, not glossary content

**Root Cause:** Wrong URL or wrong page downloaded

**Status:** ❌ **No content to preserve** - Wrong page downloaded

---

### ❌ WG3 Annex II - Acronyms (FAILED)

**File Sizes:**
- Raw: 51,544 bytes (51 KB) - **Too small for acronyms list**
- Processed: 39 bytes - **Essentially empty**

**Content Analysis:**
- Identical to WG1 Annex II
- Navigation page, not acronyms content

**Root Cause:** Wrong URL or wrong page downloaded

**Status:** ❌ **No content to preserve** - Wrong page downloaded

---

## Root Cause Analysis

### Problem Identified

1. **Wrong URLs Used:**
   - Current pattern: `https://www.ipcc.ch/report/ar6/{report}/chapter/annex-{i|ii}`
   - These URLs return navigation pages, not actual annex content
   - File size (51KB) is identical for all failed downloads, confirming same wrong page

2. **WG2 Success:**
   - WG2 Annex II downloaded correctly (656KB file)
   - Content structure different - may use different URL pattern
   - Processing pipeline works when correct content is downloaded

3. **Content Loss:**
   - `de_gatsby` processing removes navigation (correct behavior)
   - When only navigation is present, result is empty file
   - This is expected behavior - issue is wrong content downloaded, not processing bug

---

## File Size Comparison

| Annex | Raw Size | Expected Size | Status |
|-------|----------|---------------|--------|
| WG1 Annex I | 51 KB | **>100 KB** | ❌ Too small |
| WG1 Annex II | 51 KB | **>50 KB** | ❌ Too small |
| WG2 Annex II | **656 KB** | >100 KB | ✅ Correct |
| WG3 Annex I | 51 KB | **>100 KB** | ❌ Too small |
| WG3 Annex II | 51 KB | **>50 KB** | ❌ Too small |

**Conclusion:** Files <100KB are likely navigation pages, not actual content.

---

## Content Preservation Analysis

### WG2 Glossary (Working Example)

```
Processing Pipeline:
1. Download: 656 KB (contains navigation + content)
2. Clean (de_gatsby): 329 KB (navigation removed, content preserved)
3. Add IDs: 331 KB (IDs added, content preserved)

Content Preservation: ✅ 100%
- Paragraphs: 1,084 → 1,084 (100%)
- Text: 231,688 → 181,226 chars (78% - navigation removed)
```

### WG1/WG3 Annexes (Failed)

```
Processing Pipeline:
1. Download: 51 KB (navigation only, no content)
2. Clean (de_gatsby): 39 bytes (navigation removed, nothing left)
3. Add IDs: 50 bytes (empty file)

Content Preservation: ❌ 0%
- No actual content to preserve
- Issue is download, not processing
```

---

## Recommended Actions

### Immediate Actions

1. **Verify Correct URLs:**
   ```bash
   # Test these URLs manually:
   https://www.ipcc.ch/report/ar6/wg1/annex/glossary/
   https://www.ipcc.ch/report/ar6/wg1/annex/acronyms/
   https://www.ipcc.ch/report/ar6/wg3/annex/glossary/
   https://www.ipcc.ch/report/ar6/wg3/annex/acronyms/
   ```

2. **Fix Download Script:**
   - Update URL patterns in `scripts/process_ar6_annexes.py`
   - Use `/annex/glossary/` instead of `/chapter/annex-i`
   - Use `/annex/acronyms/` instead of `/chapter/annex-ii`

3. **Re-download Failed Annexes:**
   - WG1 Annex I (Glossary)
   - WG1 Annex II (Acronyms)
   - WG3 Annex I (Glossary)
   - WG3 Annex II (Acronyms)

4. **Verify After Re-download:**
   - Check file sizes (should be >100KB for glossaries)
   - Verify content structure
   - Count terms before and after processing
   - Ensure 100% preservation

### URL Pattern Investigation

**Current (Wrong):**
- `{report}/chapter/annex-i` → Returns navigation page (51KB)

**Possible Correct Patterns:**
- `{report}/annex/glossary/` → May return actual glossary
- `{report}/annex/acronyms/` → May return actual acronyms
- `{report}/annex/annex-i/` → May work with different structure

**WG2 Success Pattern:**
- Need to investigate why WG2 worked
- May have different URL structure
- Or may have been downloaded manually/correctly

---

## Term Counting Methodology

### Glossary Terms

Terms are identified by:
1. Paragraphs starting with bold text (term: definition)
2. Definition lists (`<dt>` elements)
3. Table structures (term | definition)
4. Pattern matching: `Term: Definition` or `Term—Definition`

### Acronyms

Acronyms are identified by:
1. Table rows (acronym | expansion)
2. List items: `ACRONYM - Expansion`
3. Definition lists with acronym as term

### Current Limitations

- Exact term counts require parsing term-definition pairs
- WG2 glossary has 1,084 paragraphs but exact term count needs manual parsing
- Some paragraphs may be citations/references, not terms
- Need to identify actual glossary section vs. references section

---

## Next Steps

1. ✅ **Document issue** (this document)
2. ⏳ **Investigate correct URLs** for WG1/WG3 annexes
3. ⏳ **Fix download script** with correct URL patterns
4. ⏳ **Re-download failed annexes**
5. ⏳ **Verify term counts** after re-download
6. ⏳ **Parse actual glossary terms** from WG2 (to get exact count)
7. ⏳ **Add Wikimedia IDs** to all terms (once content is correct)

---

## Files Created

- ✅ `docs/ipcc/ar6_annexes_term_count_summary.md` - Initial analysis
- ✅ `docs/ipcc/ar6_annexes_term_count_final.md` - This final summary
- ✅ `scripts/summarize_ipcc_downloads.py` - Download summary script

---

## Conclusion

**Status:** ⚠️ **CRITICAL ISSUE**

- **4 out of 5 annexes** have wrong content downloaded (navigation pages)
- **Only WG2 Annex II** has correct content and preserved it
- **Processing pipeline works correctly** when right content is downloaded
- **Issue is download URLs**, not processing logic

**Action Required:** Fix download URLs and re-download failed annexes before proceeding with Wikimedia ID addition.

---

**Generated:** Saturday, December 6, 2025




