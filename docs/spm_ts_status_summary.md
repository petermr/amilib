# SPM and TS Status Summary for WG1/2/3

**Date:** 2025-12-19  
**Focus:** Summary for Policymakers (SPM) and Technical Summary (TS) from WG1, WG2, WG3

---

## Executive Summary

All 6 documents (SPM and TS for each of WG1, WG2, WG3) have been **downloaded, cleaned, and processed with semantic IDs**. However, there are concerns about ID coverage and HTML validity.

---

## Processing Timeline

### Download and Cleaning
- **Downloaded:** December 8, 2025 at 09:22
- **Cleaned:** December 8, 2025 at 09:22 (same time as download)
- All documents have `gatsby_raw.html` and `de_gatsby.html` files

### ID Addition
- **IDs Added:** December 8, 2025 at 10:45
- All documents have `html_with_ids.html` files created at this time
- ID list and paragraph list files also created (but appear to be minimal - only 48 bytes each)

---

## File Status by Document

### WG1 - Summary for Policymakers
- **Location:** `test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/`
- **Files:**
  - `gatsby_raw.html` - 561 KB (Dec 8 09:22)
  - `de_gatsby.html` - 551 KB (Dec 8 09:22)
  - `html_with_ids.html` - 551 KB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

### WG1 - Technical Summary
- **Location:** `test/resources/ipcc/cleaned_content/wg1/technical-summary/`
- **Files:**
  - `gatsby_raw.html` - 1.0 MB (Dec 8 09:22)
  - `de_gatsby.html` - 1.0 MB (Dec 8 09:22)
  - `html_with_ids.html` - 1.0 MB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

### WG2 - Summary for Policymakers
- **Location:** `test/resources/ipcc/cleaned_content/wg2/summary-for-policymakers/`
- **Files:**
  - `gatsby_raw.html` - 619 KB (Dec 8 09:22)
  - `de_gatsby.html` - 613 KB (Dec 8 09:22)
  - `html_with_ids.html` - 613 KB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

### WG2 - Technical Summary
- **Location:** `test/resources/ipcc/cleaned_content/wg2/technical-summary/`
- **Files:**
  - `gatsby_raw.html` - 985 KB (Dec 8 09:22)
  - `de_gatsby.html` - 983 KB (Dec 8 09:22)
  - `html_with_ids.html` - 983 KB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

### WG3 - Summary for Policymakers
- **Location:** `test/resources/ipcc/cleaned_content/wg3/summary-for-policymakers/`
- **Files:**
  - `gatsby_raw.html` - 902 KB (Dec 8 09:22)
  - `de_gatsby.html` - 895 KB (Dec 8 09:22)
  - `html_with_ids.html` - 895 KB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

### WG3 - Technical Summary
- **Location:** `test/resources/ipcc/cleaned_content/wg3/technical-summary/`
- **Files:**
  - `gatsby_raw.html` - 1.4 MB (Dec 8 09:22)
  - `de_gatsby.html` - 1.4 MB (Dec 8 09:22)
  - `html_with_ids.html` - 1.4 MB (Dec 8 10:45) ✅
  - `id_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small
  - `para_list.html` - 48 bytes (Dec 8 10:45) ⚠️ Very small

---

## Completeness Assessment

### ✅ What's Complete

1. **Download Stage** ✅
   - All 6 documents downloaded
   - Raw HTML files present (`gatsby_raw.html`)

2. **Cleaning Stage** ✅
   - All documents cleaned
   - Cleaned HTML files present (`de_gatsby.html`)

3. **Section IDs** ✅
   - **Excellent coverage:** 95-100% of sections have IDs
   - All documents have proper section structure

### ❌ Critical Issues

1. **Paragraph ID Coverage** ❌
   - **WG1 SPM:** 15/192 paragraphs with IDs (7%) ❌
   - **WG1 TS:** 0/587 paragraphs with IDs (0%) ❌
   - **WG2 SPM:** 17/192 paragraphs with IDs (8%) ❌
   - **WG2 TS:** 0/567 paragraphs with IDs (0%) ❌
   - **WG3 SPM:** 28/776 paragraphs with IDs (3%) ❌
   - **WG3 TS:** 0/1726 paragraphs with IDs (0%) ❌
   - **Target:** 95%+ paragraph ID coverage
   - **Actual:** 0-8% coverage - **CRITICALLY LOW**

2. **ID List Files** ❌
   - `id_list.html` files are empty (only HTML structure, no IDs listed)
   - `para_list.html` files are empty (only HTML structure, no paragraphs listed)
   - Confirms that ID generation did not work correctly

3. **HTML Validity** ⚠️
   - HTML parsing errors detected (mismatched tags)
   - May affect ID extraction and validation

---

## Next Steps

1. **Verify ID Coverage**
   - Check actual number of paragraphs with IDs
   - Check actual number of sections with IDs
   - Verify ID format and structure

2. **Fix ID List Generation**
   - Investigate why id_list.html files are empty
   - Regenerate ID lists if needed

3. **Fix HTML Validity**
   - Address HTML parsing errors
   - Ensure valid HTML structure

4. **Validate Completeness**
   - Confirm all sections have IDs
   - Confirm all paragraphs have IDs (target: 95%+)
   - Confirm section structure is correct

---

## Detailed ID Coverage

| Report | Document | Paragraphs | Para IDs | Para % | Sections | Section IDs | Section % | Total IDs |
|--------|----------|------------|----------|--------|----------|-------------|-----------|-----------|
| WG1 | SPM | 192 | 15 | **7%** ❌ | 6 | 6 | **100%** ✅ | 208 |
| WG1 | TS | 587 | 0 | **0%** ❌ | 56 | 56 | **100%** ✅ | 267 |
| WG2 | SPM | 192 | 17 | **8%** ❌ | 24 | 23 | **95%** ✅ | 224 |
| WG2 | TS | 567 | 0 | **0%** ❌ | 39 | 39 | **100%** ✅ | 185 |
| WG3 | SPM | 776 | 28 | **3%** ❌ | 33 | 33 | **100%** ✅ | 334 |
| WG3 | TS | 1,726 | 0 | **0%** ❌ | 25 | 25 | **100%** ✅ | 229 |

## Summary Table

| Report | Document | Downloaded | Cleaned | Section IDs | Paragraph IDs | Status |
|--------|----------|------------|---------|-------------|---------------|--------|
| WG1 | SPM | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 100% | ❌ 7% | ⚠️ **Incomplete** |
| WG1 | TS | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 100% | ❌ 0% | ❌ **Failed** |
| WG2 | SPM | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 95% | ❌ 8% | ⚠️ **Incomplete** |
| WG2 | TS | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 100% | ❌ 0% | ❌ **Failed** |
| WG3 | SPM | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 100% | ❌ 3% | ⚠️ **Incomplete** |
| WG3 | TS | ✅ Dec 8 09:22 | ✅ Dec 8 09:22 | ✅ 100% | ❌ 0% | ❌ **Failed** |

**Legend:**
- ✅ Complete
- ⚠️ Needs verification
- ❌ Missing

---

## Conclusion

### Status: ⚠️ **INCOMPLETE - Paragraph IDs Missing**

All 6 SPM/TS documents have been:
- ✅ **Downloaded** (Dec 8, 2025 09:22)
- ✅ **Cleaned** (Dec 8, 2025 09:22)
- ✅ **Section IDs added** (95-100% coverage)
- ❌ **Paragraph IDs FAILED** (0-8% coverage, target: 95%+)

### Critical Findings

1. **Section IDs:** Excellent (95-100% coverage) ✅
2. **Paragraph IDs:** **CRITICALLY LOW** (0-8% coverage) ❌
   - Technical Summaries: **0%** paragraph ID coverage
   - SPMs: **3-8%** paragraph ID coverage
   - Target: **95%+** paragraph ID coverage

3. **ID List Files:** Empty (confirms ID generation failure)

### Root Cause

The ID generation process appears to have failed for paragraphs. While section IDs were successfully added (likely because sections have explicit container divs with IDs), paragraph IDs were not generated. This could be due to:
- Missing section container IDs that paragraphs depend on
- Different HTML structure in SPM/TS vs chapters
- ID generation logic not handling SPM/TS structure correctly

### Action Required

**All 6 documents need paragraph ID regeneration** to meet the 95%+ coverage target.

