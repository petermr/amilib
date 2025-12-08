# IPCC HTML Processing Results Summary

**Date:** December 8, 2025  
**Script Run:** `scripts/process_ipcc_html_ids.py`  
**Status:** ⚠️ **PARTIAL SUCCESS** - Processing completed but significant issues identified

---

## Executive Summary

The processing script successfully ran on 63 files but revealed critical structural issues:

### Key Findings

1. **✅ Processing Pipeline Works**: Script successfully processed files and generated output
2. **⚠️ Coverage Issues**: Most files still have low paragraph ID coverage (0-85% vs 95% target)
3. **❌ PDF Files Failed**: PDF-converted annexes have 0 paragraphs detected (structure mismatch)
4. **⚠️ SPM/TS Issues**: Files processed but coverage remains very low (0-8%)

---

## Processing Statistics

| Metric | Count |
|--------|-------|
| **Total Files Found** | 63 |
| **Files Processed** | 63 |
| **Files with Good Coverage** | 2 (WG3 Chapter17, WG1 Chapter10) |
| **Files with Low Coverage** | ~47 chapters |
| **Files with Structure Issues** | 14 (PDF-converted annexes) |

---

## Coverage Results by Component Type

### SPM (Summary for Policymakers) - 8 files

| Report | Paragraph Coverage | Section Coverage | Status |
|--------|-------------------|------------------|--------|
| WG1 | 7.9% (15/189) | 45.2% (19/42) | ⚠️ Very Low |
| WG2 | Unknown | Unknown | ⚠️ Needs check |
| WG3 | Unknown | Unknown | ⚠️ Needs check |
| SYR | Unknown | Unknown | ⚠️ Needs check |

**Issue**: Files processed but paragraph IDs not being generated. Structure may not match expected format.

### TS (Technical Summary) - 7 files

| Report | Paragraph Coverage | Section Coverage | Status |
|--------|-------------------|------------------|--------|
| WG1 | 0% (0/569) | 73.7% (140/190) | ❌ No Paragraph IDs |
| WG2 | Unknown | Unknown | ⚠️ Needs check |
| WG3 | Unknown | Unknown | ⚠️ Needs check |
| SYR | Unknown | Unknown | ⚠️ Needs check |

**Issue**: No paragraph IDs generated despite 569 paragraphs present. Section IDs exist but paragraph IDs missing.

### Chapters - 47 files

**Coverage Range**: 49-98% paragraph coverage

| Coverage Range | File Count | Status |
|----------------|------------|--------|
| 95%+ | 2 files | ✅ Good |
| 80-95% | ~10 files | ⚠️ Acceptable |
| 60-80% | ~25 files | ⚠️ Needs improvement |
| <60% | ~10 files | ❌ Poor |

**Common Issues**:
- Missing IDs for FAQ paragraphs
- Missing IDs for box paragraphs  
- Missing IDs for reference paragraphs
- Some sections with spaces/special characters not matched

### PDF-Converted Annexes - 6 files

| File | Paragraphs Found | Status |
|------|------------------|--------|
| WG1 Annex I (Glossary) | 0 | ❌ Structure mismatch |
| WG1 Annex II (Acronyms) | Unknown | ⚠️ Needs check |
| WG3 Annex I (Glossary) | 0 | ❌ Structure mismatch |
| WG3 Annex II (Definitions) | 0 | ❌ Structure mismatch |
| WG3 Annex VI (Acronyms) | 0 | ❌ Structure mismatch |
| SYR Annex I (Glossary) | 0 | ❌ Structure mismatch |
| SYR Annex II (Acronyms) | Unknown | ⚠️ Needs check |

**Issue**: PDF-converted HTML files don't have the expected structure:
- No `<p>` tags detected (or different structure)
- Missing `h*-container` divs
- Missing `h*-siblings` divs
- Need pre-processing to add proper structure

---

## Root Cause Analysis

### Issue 1: PDF-Converted Files Structure Mismatch

**Problem**: PDF→HTML conversion creates different HTML structure than web-scraped HTML.

**Expected Structure** (from web scraping):
```html
<div class="h1-container" id="section-id">
  <h1>Title</h1>
  <div class="h1-siblings">
    <p>Paragraph content</p>
  </div>
</div>
```

**Actual Structure** (from PDF conversion):
- May use `<div>` elements instead of `<p>`
- May not have `h*-container` structure
- May have `page_*.raw.html` files instead of single combined file
- Structure varies by PDF conversion tool

**Solution Needed**: 
1. Analyze PDF-converted HTML structure
2. Create pre-processing script to add proper section containers
3. Convert content divs to paragraphs where appropriate
4. Add semantic IDs based on content (glossary terms, acronyms)

### Issue 2: SPM/TS Files Low Coverage

**Problem**: SPM/TS files have sections but paragraphs aren't getting IDs.

**Possible Causes**:
1. Section IDs don't match expected regex patterns
2. Paragraphs aren't in `h*-siblings` containers
3. ID generation logic doesn't handle SPM/TS format
4. Need `spm-*` and `ts-*` prefixes but current system uses numeric IDs

**Solution Needed**:
1. Check HTML structure of SPM/TS files
2. Verify section containers exist
3. Update ID generation to handle SPM/TS format
4. Ensure proper prefix application (`spm-*`, `ts-*`)

### Issue 3: Chapter Coverage Below Target

**Problem**: Most chapters have 60-85% coverage instead of 95%+.

**Missing ID Patterns**:
- `FAQ {number}_p*` - FAQ sections with question text
- `box-{number}_p*` - Box sections
- `references_p*` - Reference paragraphs
- Sections with spaces: `2.6.8 _p8` (space before `_p`)

**Solution Needed**:
1. Enhance regex patterns for FAQ, boxes, references
2. Handle spaces/special characters in section IDs
3. Add fallback ID generation for unmatched paragraphs
4. Fix spacing issues in ID generation

---

## What Needs to Be Done

### Priority 1: Fix PDF-Converted Annexes (CRITICAL)

**Files**: 6 annex files

**Steps**:
1. **Analyze Structure**: Examine PDF-converted HTML to understand structure
2. **Create Pre-processor**: Script to add proper section containers
3. **Add Semantic IDs**: Generate IDs based on content (terms, acronyms)
4. **Test**: Verify structure and IDs are correct

**Expected Output**: 
- Proper `h*-container` structure
- Paragraph elements with content
- Semantic IDs: `gloss-{term}`, `acr-{acronym}`, `def-{term}`

### Priority 2: Fix SPM/TS Processing (HIGH)

**Files**: 15 files (8 SPM + 7 TS)

**Steps**:
1. **Verify Structure**: Check if cleaned files have proper structure
2. **Analyze Format**: Understand SPM/TS HTML format
3. **Update ID Generation**: Ensure proper `spm-*` and `ts-*` prefixes
4. **Fix Paragraph IDs**: Ensure paragraphs get IDs based on section containers

**Expected Output**:
- Section IDs: `spm-1`, `spm-1.1`, `ts-1`, `ts-1.1`
- Paragraph IDs: `spm-1_p1`, `spm-1_p2`, `ts-1_p1`, etc.
- 95%+ paragraph coverage

### Priority 3: Improve Chapter Coverage (MEDIUM)

**Files**: 47 chapter files

**Steps**:
1. **Enhance Regex**: Update patterns for FAQ, boxes, references
2. **Fix Spacing**: Handle spaces in section IDs
3. **Add Fallbacks**: Generate IDs for unmatched paragraphs
4. **Target**: 95%+ coverage for all chapters

**Expected Output**:
- FAQ paragraphs get IDs: `FAQ 1.1_p1`, `FAQ 1.1_p2`
- Box paragraphs get IDs: `box-3.1_p1`, `box-3.1_p2`
- Reference paragraphs get IDs: `references_p1`, `references_p2`
- 95%+ paragraph coverage

### Priority 4: Process Special Reports (LOW)

**Files**: ~27 files (SR15, SROCC, SRCCL)

**Steps**:
1. Check if `html_with_ids.html` exists
2. Process if missing
3. Ensure WordPress format handled correctly

---

## Files Requiring Immediate Attention

### Critical (Structure Issues)

1. **WG1 Annex I (Glossary)** - 0 paragraphs detected
2. **WG3 Annex I (Glossary)** - 0 paragraphs detected
3. **WG3 Annex II (Definitions)** - 0 paragraphs detected
4. **WG3 Annex VI (Acronyms)** - 0 paragraphs detected
5. **SYR Annex I (Glossary)** - 0 paragraphs detected

### High Priority (Low Coverage)

1. **WG1 TS** - 0% paragraph coverage (569 paragraphs)
2. **WG1 SPM** - 7.9% paragraph coverage (189 paragraphs)
3. **All other SPM/TS files** - Need verification

### Medium Priority (Below Target)

1. **Chapters with <80% coverage** - ~35 files
2. **Focus areas**: FAQ sections, boxes, references

---

## Recommendations

### Immediate Actions

1. **Analyze PDF Structure**: 
   ```bash
   # Examine a PDF-converted file
   cat test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/annex-i-glossary.html | head -100
   ```

2. **Check SPM/TS Structure**:
   ```bash
   # Check cleaned file structure
   cat test/resources/ipcc/cleaned_content/wg1/summary-for-policymakers/de_gatsby.html | grep -E "(h1|h2|div.*container|p)" | head -50
   ```

3. **Create Pre-processing Script**: For PDF-converted files to add proper structure

### Short-term Actions

1. **Enhance ID Generation**: Update regex patterns and add fallbacks
2. **Fix SPM/TS Processing**: Ensure proper prefix application
3. **Re-run Processing**: After fixes, process all files again

### Long-term Actions

1. **Validation Script**: Create comprehensive ID validation
2. **Coverage Reporting**: Automated coverage reports
3. **Documentation**: ID naming convention guide

---

## Conclusion

**Status**: ⚠️ **IN PROGRESS**

The processing script successfully ran and identified critical issues:

1. **PDF-converted files** need structure pre-processing (6 files)
2. **SPM/TS files** need format-specific ID generation (15 files)
3. **Chapters** need enhanced ID generation for special sections (~35 files)

**Next Steps**:
1. Analyze PDF-converted file structure
2. Create pre-processing script for PDF files
3. Fix SPM/TS ID generation
4. Enhance chapter ID generation
5. Re-run processing script

**Target**: 95%+ paragraph coverage and 99%+ section coverage for all files.

---

**Last Updated:** December 8, 2025  
**Script:** `scripts/process_ipcc_html_ids.py`  
**Results File:** `/tmp/ipcc_processing_results.txt`

