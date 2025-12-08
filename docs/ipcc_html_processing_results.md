# IPCC HTML Processing Results

**Date:** December 8, 2025  
**Script:** `scripts/process_ipcc_html_ids.py`  
**Status:** ⚠️ **PARTIAL SUCCESS** - Processing completed but coverage issues remain

---

## Executive Summary

The processing script ran successfully but revealed significant issues:

### Key Findings

1. **Chapters**: Most chapters processed but coverage remains below target (60-85% vs 95% target)
2. **SPM/TS Files**: Not processed (likely missing cleaned files or structure issues)
3. **PDF Annexes**: Failed to process (0 paragraphs found - structure mismatch)
4. **Section Coverage**: Generally good (99%+ for most files)
5. **Paragraph Coverage**: Below target for most files

---

## Processing Statistics

### Overall Results

- **Files Processed**: 63 files found
- **Successfully Processed**: 2 files (with good coverage)
- **Processed but Low Coverage**: ~47 files
- **Failed**: 14 files (mostly PDF-converted annexes)

### Coverage by Document Type

| Document Type | Files | Avg Paragraph Coverage | Avg Section Coverage | Status |
|---------------|-------|------------------------|----------------------|--------|
| **Chapters** | 47 | 60-85% | 99%+ | ⚠️ Needs improvement |
| **SPM** | 8 | 0-8% | 45-73% | ❌ Not processed |
| **TS** | 7 | 0% | 73% | ❌ Not processed |
| **Glossary** | 4 | 0-9% | 0-42% | ❌ Structure issues |
| **Acronym** | 3 | 0% | 0% | ❌ Structure issues |
| **Definition** | 1 | 0% | 0% | ❌ Structure issues |

---

## Detailed Results by Component

### AR6 Working Groups

#### WG1
- **SPM**: 7.9% paragraph coverage - ⚠️ Needs processing
- **TS**: 0% paragraph coverage - ❌ Not processed
- **Chapters**: 49-96% coverage - ⚠️ Variable, some need improvement
- **Annexes**: PDF-converted files failed - ❌ Structure issues

#### WG2
- **SPM**: Not shown in results - ⚠️ May not have been processed
- **TS**: Not shown in results - ⚠️ May not have been processed
- **Chapters**: 60-84% coverage - ⚠️ Below target
- **Glossary**: 9.4% coverage - ⚠️ Needs improvement

#### WG3
- **SPM**: Not shown in results - ⚠️ May not have been processed
- **TS**: Not shown in results - ⚠️ May not have been processed
- **Chapters**: 56-98% coverage - ⚠️ Variable
- **Annexes**: PDF-converted files failed - ❌ Structure issues

#### SYR
- **SPM**: Not shown in results - ⚠️ May not have been processed
- **TS**: Not shown in results - ⚠️ May not have been processed
- **Annexes**: PDF-converted files failed - ❌ Structure issues

---

## Issues Identified

### Issue 1: PDF-Converted Files Lack Structure

**Problem**: PDF-converted HTML files (annexes) don't have the expected section structure:
- Missing `h*-container` divs
- Missing `h*-siblings` divs
- No paragraph elements detected (0 paragraphs found)

**Affected Files**:
- WG1 Annex I (Glossary)
- WG1 Annex II (Acronyms)
- WG3 Annex I (Glossary)
- WG3 Annex II (Definitions)
- WG3 Annex VI (Acronyms)
- SYR Annex I (Glossary)
- SYR Annex II (Acronyms)

**Solution Needed**: 
- Pre-process PDF-converted HTML to add proper section structure
- Or create custom ID generation for PDF-converted files

### Issue 2: SPM/TS Files Not Processing

**Problem**: SPM and TS files exist but weren't processed:
- Files have `html_with_ids.html` but low coverage
- May be missing cleaned files (`de_gatsby.html`)
- Or structure doesn't match expected format

**Affected Files**:
- All 8 SPM files (WG1, WG2, WG3, SYR × 2)
- All 7 TS files (WG1, WG2, WG3, SYR × 2)

**Solution Needed**:
- Ensure cleaned files exist
- Verify HTML structure matches expected format
- May need special ID generation for SPM/TS format

### Issue 3: Chapter Coverage Below Target

**Problem**: Most chapters have 60-85% paragraph coverage, below 95% target:
- Missing IDs for paragraphs in boxes, FAQs, references
- Some paragraphs in special sections not getting IDs

**Common Missing ID Patterns**:
- `FAQ {number}_p*` - FAQ paragraphs
- `box-{number}_p*` - Box paragraphs
- `references_p*` - Reference paragraphs
- Some numbered sections with spaces or special characters

**Solution Needed**:
- Enhance ID generation regex patterns
- Handle special sections (FAQ, boxes, references) better
- Fix spacing/special character issues in section IDs

---

## What Worked

### ✅ Section ID Coverage

Most files have excellent section coverage (99%+):
- Section containers (`h*-container` divs) are properly identified
- Section IDs are correctly assigned
- Nested structure is maintained

### ✅ Processing Pipeline

The script successfully:
- Found all files needing processing
- Identified document types correctly
- Used appropriate publisher classes (Gatsby/WordPress)
- Generated output files (`html_with_ids.html`, `id_list.html`, `para_list.html`)

### ✅ Files with Good Coverage

- WG3 Chapter17: 98% paragraph coverage ✅
- Some chapters have 85%+ coverage (acceptable but below target)

---

## Recommendations

### Priority 1: Fix PDF-Converted Files

**Action**: Create pre-processing step for PDF-converted HTML:
1. Analyze PDF-converted HTML structure
2. Add proper section containers (`h*-container`, `h*-siblings`)
3. Identify glossary terms/acronyms and create section structure
4. Then run ID generation

**Files Affected**: 6 annex files

### Priority 2: Process SPM/TS Files

**Action**: 
1. Verify cleaned files exist for all SPM/TS
2. Check HTML structure matches expected format
3. Ensure proper section containers exist
4. Run ID generation with appropriate prefixes (`spm-*`, `ts-*`)

**Files Affected**: 15 files (8 SPM + 7 TS)

### Priority 3: Improve Chapter Coverage

**Action**:
1. Enhance ID generation regex to handle:
   - FAQ sections with full question text
   - Box sections with titles
   - References sections
   - Sections with spaces/special characters
2. Add fallback ID generation for unmatched paragraphs
3. Target: 95%+ paragraph coverage

**Files Affected**: 47 chapter files

### Priority 4: Special Report Files

**Action**:
1. Check if Special Reports (SR15, SROCC, SRCCL) have `html_with_ids.html`
2. Process if missing
3. Ensure WordPress format is handled correctly

**Files Affected**: ~27 files

---

## Next Steps

1. **Analyze PDF-Converted Structure**
   - Examine sample PDF-converted HTML files
   - Identify how to add section structure
   - Create pre-processing script

2. **Fix SPM/TS Processing**
   - Check for cleaned files
   - Verify structure
   - Process with proper ID prefixes

3. **Enhance ID Generation**
   - Update regex patterns for FAQ, boxes, references
   - Add fallback ID generation
   - Handle edge cases

4. **Re-run Processing**
   - After fixes, re-run script
   - Target: 95%+ paragraph coverage for all files

---

## Files Requiring Special Attention

### PDF-Converted Annexes (Need Structure Pre-processing)
- `wg1/annex-i-glossary/annex-i-glossary.html`
- `wg1/annex-ii-acronyms/` (needs processing)
- `wg3/annex-i-glossary/annex-i-glossary.html`
- `wg3/annex-ii-definitions/annex-ii-definitions.html`
- `wg3/annex-vi-acronyms/annex-vi-acronyms.html`
- `syr/annex-i-glossary/` (needs processing)
- `syr/annex-ii-acronyms/` (needs processing)

### SPM/TS Files (Need Verification)
- All `{report}/summary-for-policymakers/` directories
- All `{report}/technical-summary/` directories

### Chapters Needing Improvement
- Chapters with <80% paragraph coverage (many WG2/WG3 chapters)
- Focus on FAQ, box, and reference sections

---

## Conclusion

The processing script successfully ran but revealed that:

1. **PDF-converted files** need special handling (structure pre-processing)
2. **SPM/TS files** need verification and proper processing
3. **Chapter files** need enhanced ID generation for special sections

**Overall Status**: ⚠️ **IN PROGRESS** - Foundation is good but improvements needed

**Next Action**: Fix PDF-converted file structure and SPM/TS processing, then re-run.

---

**Last Updated:** December 8, 2025  
**Script:** `scripts/process_ipcc_html_ids.py`

