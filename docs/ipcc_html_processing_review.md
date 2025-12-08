# IPCC HTML Processing Review

**Date:** December 8, 2025  
**Objective:** Review HTML processing to ensure proper nested sections and semantic IDs for all components

---

## Executive Summary

**Current Status:** ⚠️ **INCOMPLETE** - Many components lack proper semantic IDs

### Key Findings

1. **ID Coverage Issues:**
   - WG1 SPM: Only 7.8% paragraph ID coverage (15/192 paragraphs)
   - Many files have navigation/tooltip IDs but lack semantic content IDs
   - Section IDs are missing or incomplete

2. **Processing Pipeline:**
   - ✅ Download pipeline works (creates `gatsby_raw.html` or `wordpress.html`)
   - ✅ Cleaning pipeline works (creates `de_gatsby.html` or `de_wordpress.html`)
   - ⚠️ ID generation incomplete (many files lack `html_with_ids.html` or have low coverage)

3. **Components Needing Processing:**
   - SPM/TS documents (8 files) - need semantic IDs
   - Annexes (8 files) - need semantic IDs with proper prefixes
   - PDF-converted HTML files - need section structure and IDs

---

## IPCC Semantic ID System

### ID Format Requirements

The IPCC system uses semantic IDs based on document structure:

#### For Chapters:
- **Section IDs**: `{number}` format (e.g., `3.1.2`, `4.5.1`)
- **Paragraph IDs**: `{section_id}_p{index}` (e.g., `3.1.2_p1`, `3.1.2_p2`)
- **Box IDs**: `box-{number}` (e.g., `box-3.1`, `box-4.2`)
- **Cross-Chapter Box IDs**: `cross-chapter-box-{number}`

#### For Special Documents:
- **SPM (Summary for Policymakers)**: `spm-{section}` or `spm_{number}`
- **TS (Technical Summary)**: `ts-{section}` or `ts_{number}`
- **FAQ**: `faq-{number}` or `FAQ {number}`
- **Executive Summary**: `executive-summary`
- **References**: `references`

#### For Annexes:
- **Glossary**: `gloss-{term}` or `glossary-{term}` or term-based IDs
- **Acronyms**: `acr-{acronym}` or `acronym-{acronym}` or acronym-based IDs
- **Definitions**: `def-{term}` or `definition-{term}`

### Nested Section Structure

Expected HTML structure:
```html
<div class="h1-container" id="spm-1">
  <h1>Section Title</h1>
  <div class="h1-siblings">
    <p id="spm-1_p1">Paragraph 1</p>
    <p id="spm-1_p2">Paragraph 2</p>
    <div class="h2-container" id="spm-1.1">
      <h2>Subsection Title</h2>
      <div class="h2-siblings">
        <p id="spm-1.1_p1">Subsection paragraph</p>
      </div>
    </div>
  </div>
</div>
```

---

## Current Processing Pipeline

### Step 1: Download
- **Input**: IPCC website URL
- **Output**: `gatsby_raw.html` or `wordpress.html`
- **Status**: ✅ Working

### Step 2: Clean
- **Input**: Raw HTML file
- **Output**: `de_gatsby.html` or `de_wordpress.html`
- **Process**: Removes navigation, tooltips, footers
- **Status**: ✅ Working

### Step 3: Add Semantic IDs
- **Input**: Cleaned HTML file (`de_gatsby.html`)
- **Output**: `html_with_ids.html`
- **Process**: 
  - Identifies section containers (`div.h*-container`)
  - Adds section IDs based on heading numbers
  - Adds paragraph IDs (`{section_id}_p{index}`)
- **Status**: ⚠️ **INCOMPLETE** - Many files missing or have low coverage

### Step 4: Generate ID Lists
- **Output**: `id_list.html`, `para_list.html`
- **Status**: ⚠️ **INCOMPLETE** - Not generated for all files

---

## Component-by-Component Review

### AR6 Working Groups (WG1, WG2, WG3)

#### SPM (Summary for Policymakers)
- **Files**: `{report}/summary-for-policymakers/html_with_ids.html`
- **Current Status**: ⚠️ Files exist but ID coverage is low (~7.8%)
- **Issues**:
  - Missing section IDs (should be `spm-{number}` format)
  - Missing paragraph IDs
  - Navigation IDs present but not semantic content IDs
- **Needs**: 
  - Add section containers with `spm-*` IDs
  - Add paragraph IDs: `spm-{section}_p{index}`
  - Ensure nested structure

#### TS (Technical Summary)
- **Files**: `{report}/technical-summary/html_with_ids.html`
- **Current Status**: ⚠️ Files exist but ID coverage unknown
- **Needs**: 
  - Add section containers with `ts-{number}` IDs
  - Add paragraph IDs: `ts-{section}_p{index}`
  - Ensure nested structure

#### Chapters
- **Files**: `{report}/Chapter{NN}/html_with_ids.html`
- **Current Status**: ✅ Most chapters have good ID coverage
- **Format**: Uses numeric section IDs (`3.1.2`, etc.)

#### Annexes

**WG1 Annex I - Glossary:**
- **File**: `wg1/annex-i-glossary/annex-i-glossary.html`
- **Source**: PDF→HTML conversion
- **Current Status**: ⚠️ Needs semantic IDs
- **Needs**:
  - Add section containers for each glossary term
  - Use IDs like `gloss-{term}` or term-based IDs
  - Add paragraph IDs for definitions

**WG1 Annex II - Acronyms:**
- **File**: `wg1/annex-ii-acronyms/html_with_ids.html`
- **Current Status**: ⚠️ Needs review
- **Needs**:
  - Add section containers for each acronym
  - Use IDs like `acr-{acronym}` or acronym-based IDs

**WG2 Annex II - Glossary:**
- **File**: `wg2/annex-ii-glossary/html_with_ids.html`
- **Current Status**: ✅ Has `html_with_ids.html`
- **Needs**: Verify ID format and coverage

**WG3 Annexes:**
- **Files**: 
  - `wg3/annex-i-glossary/annex-i-glossary.html`
  - `wg3/annex-ii-definitions/annex-ii-definitions.html`
  - `wg3/annex-vi-acronyms/annex-vi-acronyms.html`
- **Current Status**: ⚠️ PDF-converted, need semantic IDs
- **Needs**: Add proper section structure and IDs

### SYR (Synthesis Report)

#### SPM
- **File**: `syr/summary-for-policymakers/html_with_ids.html`
- **Current Status**: ⚠️ Needs review
- **Needs**: Same as WG SPM files

#### TS
- **File**: `syr/technical-summary/html_with_ids.html`
- **Current Status**: ⚠️ Needs review
- **Needs**: Same as WG TS files

#### Annexes
- **Files**: 
  - `syr/annex-i-glossary/annex-i-glossary.html`
  - `syr/annex-ii-acronyms/annex-ii-acronyms.html`
- **Current Status**: ⚠️ PDF-converted, need semantic IDs
- **Needs**: Add proper section structure and IDs

### Special Reports (SR15, SROCC, SRCCL)

#### SPM/TS
- **Files**: `{report}/spm/de_wordpress_styles.html`, `{report}/ts/de_wordpress_styles.html`
- **Current Status**: ⚠️ May not have `html_with_ids.html` versions
- **Needs**: 
  - Process to create `html_with_ids.html`
  - Add semantic IDs with `spm-*` and `ts-*` prefixes

#### Chapters
- **Files**: `{report}/Chapter{NN}/de_wordpress_styles.html`
- **Current Status**: ⚠️ May not have `html_with_ids.html` versions
- **Needs**: Process to create `html_with_ids.html` with semantic IDs

#### Glossaries
- **Files**: `{report}/glossary/de_wordpress_styles.html`
- **Current Status**: ⚠️ May not have `html_with_ids.html` versions
- **Needs**: Process to create `html_with_ids.html` with `gloss-*` IDs

---

## What Needs to Be Done

### Priority 1: High Priority (Critical for Semantic Analysis)

1. **Process All SPM/TS Documents**
   - **Files**: 8 SPM + 8 TS = 16 files
   - **Action**: Run ID generation pipeline
   - **Expected Output**: `html_with_ids.html` with `spm-*` and `ts-*` IDs
   - **Target Coverage**: 95%+ paragraphs, 99%+ sections

2. **Process PDF-Converted Annexes**
   - **Files**: 6 annex files (WG1: 2, WG3: 3, SYR: 2)
   - **Action**: 
     - Ensure proper section structure (nested divs)
     - Add semantic IDs with appropriate prefixes (`gloss-*`, `acr-*`, `def-*`)
     - Add paragraph IDs
   - **Expected Output**: `html_with_ids.html` or properly named annex file

3. **Verify Existing `html_with_ids.html` Files**
   - **Action**: Check ID coverage for all existing files
   - **Target**: 95%+ paragraph coverage, 99%+ section coverage
   - **Fix**: Re-process files with low coverage

### Priority 2: Medium Priority

4. **Process Special Report Files**
   - **Files**: SR15, SROCC, SRCCL components
   - **Action**: Convert `de_wordpress_styles.html` → `html_with_ids.html`
   - **Expected Output**: All components have `html_with_ids.html` with semantic IDs

5. **Generate ID Lists**
   - **Action**: Create `id_list.html` and `para_list.html` for all components
   - **Purpose**: Enable easy navigation and validation

### Priority 3: Low Priority

6. **Validate All IDs**
   - **Action**: Run validation script to check for duplicates, missing IDs
   - **Tool**: `scripts/ar6_validate_ids.py`

7. **Document ID Naming Conventions**
   - **Action**: Create reference guide for ID formats
   - **Purpose**: Ensure consistency across all files

---

## Implementation Plan

### Step 1: Create Processing Script

Create a script that:
1. Finds all HTML files that need processing
2. Identifies document type (SPM, TS, Chapter, Glossary, Acronym, etc.)
3. Applies appropriate ID generation based on document type
4. Ensures nested section structure
5. Generates `html_with_ids.html` files

### Step 2: ID Generation by Document Type

#### For SPM Documents:
```python
# Section IDs: spm-1, spm-1.1, spm-1.1.1, etc.
# Paragraph IDs: spm-1_p1, spm-1_p2, spm-1.1_p1, etc.
```

#### For TS Documents:
```python
# Section IDs: ts-1, ts-1.1, ts-1.1.1, etc.
# Paragraph IDs: ts-1_p1, ts-1_p2, ts-1.1_p1, etc.
```

#### For Glossary Annexes:
```python
# Section IDs: gloss-{term} or glossary-{term-id}
# Paragraph IDs: gloss-{term}_p1, gloss-{term}_p2, etc.
```

#### For Acronym Annexes:
```python
# Section IDs: acr-{acronym} or acronym-{acronym}
# Paragraph IDs: acr-{acronym}_p1, acr-{acronym}_p2, etc.
```

### Step 3: Section Structure Enhancement

Ensure all files have proper nested structure:
```html
<div class="h1-container" id="{prefix}-{section-number}">
  <h1>Section Title</h1>
  <div class="h1-siblings">
    <p id="{prefix}-{section-number}_p1">Content</p>
    <div class="h2-container" id="{prefix}-{section-number}.1">
      <h2>Subsection</h2>
      <div class="h2-siblings">
        <p id="{prefix}-{section-number}.1_p1">Content</p>
      </div>
    </div>
  </div>
</div>
```

---

## Files Requiring Processing

### Summary by Type

| Document Type | Count | Status | Priority |
|---------------|-------|--------|----------|
| **SPM** | 7 | ⚠️ Low ID coverage | HIGH |
| **TS** | 7 | ⚠️ Low ID coverage | HIGH |
| **PDF Annexes** | 6 | ⚠️ Missing IDs | HIGH |
| **SR Chapters** | 18 | ⚠️ May lack html_with_ids | MEDIUM |
| **SR SPM/TS** | 6 | ⚠️ May lack html_with_ids | MEDIUM |
| **SR Glossaries** | 3 | ⚠️ May lack html_with_ids | MEDIUM |

**Total Files Needing Processing:** ~47 files

---

## Validation Criteria

### ID Coverage Targets

- **Paragraphs**: 95%+ should have semantic IDs
- **Sections**: 99%+ should have semantic IDs
- **No Duplicates**: Zero duplicate IDs per file
- **Proper Format**: All IDs follow IPCC naming conventions

### Structure Requirements

- **Nested Sections**: Proper `h*-container` structure
- **Sibling Containers**: `h*-siblings` divs for content
- **Heading Hierarchy**: Proper h1 → h2 → h3 nesting

---

## Next Steps

1. **Immediate**: Create comprehensive processing script
2. **Short-term**: Process all SPM/TS documents
3. **Medium-term**: Process all PDF-converted annexes
4. **Long-term**: Validate and document all ID systems

---

## Tools and Scripts

### Existing Tools
- `test/ipcc_classes.py` - Contains `IPCCGatsby.add_ids()` method
- `scripts/ar6_validate_ids.py` - Validation script (needs enhancement)

### Needed Tools
- Comprehensive processing script for all document types
- ID format validation script
- Coverage reporting script

---

**Last Updated:** December 8, 2025

