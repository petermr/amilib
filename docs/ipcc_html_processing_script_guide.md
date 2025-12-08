# IPCC HTML Processing Script Guide

**Script:** `scripts/process_ipcc_html_ids.py`  
**Purpose:** Process all IPCC HTML components to add semantic IDs with proper nested section structure

---

## Overview

This script processes IPCC HTML files to ensure:
1. ✅ Proper nested section structure (`h*-container` divs)
2. ✅ Semantic IDs for all sections and paragraphs
3. ✅ Appropriate ID prefixes based on document type (spm, ts, gloss, acr, etc.)
4. ✅ Generation of `html_with_ids.html`, `id_list.html`, and `para_list.html`

---

## Usage

### Check Coverage Only (No Processing)

```bash
python scripts/process_ipcc_html_ids.py --check-only
```

Shows coverage statistics for all files without processing them.

### Process All Files

```bash
python scripts/process_ipcc_html_ids.py
```

Processes all files that need semantic IDs.

### Process Specific Report

```bash
python scripts/process_ipcc_html_ids.py --report wg1
python scripts/process_ipcc_html_ids.py --report syr
```

### Process Specific Component

```bash
python scripts/process_ipcc_html_ids.py --component summary-for-policymakers
python scripts/process_ipcc_html_ids.py --component technical-summary
python scripts/process_ipcc_html_ids.py --component annex-i-glossary
```

### Dry Run (Preview Changes)

```bash
python scripts/process_ipcc_html_ids.py --dry-run
```

Shows what would be processed without actually modifying files.

### Combined Options

```bash
# Process only WG1 SPM files in dry-run mode
python scripts/process_ipcc_html_ids.py --report wg1 --component summary-for-policymakers --dry-run
```

---

## What the Script Does

### 1. File Discovery

The script automatically finds:
- **SPM/TS documents**: `{report}/summary-for-policymakers/`, `{report}/technical-summary/`
- **Chapters**: `{report}/Chapter{NN}/`
- **Annexes**: `{report}/annex-*/`
- **Glossaries**: `{report}/glossary/` (for SR15, SROCC)

### 2. Document Type Identification

Automatically identifies document type from path:
- `spm` - Summary for Policymakers
- `ts` - Technical Summary
- `glossary` - Glossary annexes
- `acronym` - Acronym annexes
- `definition` - Definition annexes
- `chapter` - Regular chapters
- `faq` - Frequently Asked Questions
- `executive-summary` - Executive Summary
- `references` - References section

### 3. ID Generation

Uses existing IPCC processing pipeline:
- **Gatsby format** (WG1, WG2, WG3, SYR): Uses `IPCCGatsby.add_ids()`
- **WordPress format** (SR15, SROCC, SRCCL): Uses `IPCCWordpress.add_ids()`

### 4. Coverage Checking

Before processing, checks:
- Current paragraph ID coverage
- Current section ID coverage
- Skips files with 95%+ paragraph coverage and 99%+ section coverage

### 5. Output Files

For each processed file, creates:
- `html_with_ids.html` - Final HTML with semantic IDs
- `id_list.html` - List of all IDs
- `para_list.html` - List of paragraphs with IDs

---

## ID Prefix System

The script uses appropriate ID prefixes based on document type:

| Document Type | ID Prefix | Example |
|---------------|-----------|---------|
| **SPM** | `spm-` | `spm-1`, `spm-1.1`, `spm-1_p1` |
| **TS** | `ts-` | `ts-1`, `ts-1.1`, `ts-1_p1` |
| **Glossary** | `gloss-` | `gloss-term-name`, `gloss-term-name_p1` |
| **Acronyms** | `acr-` | `acr-AI`, `acr-AI_p1` |
| **Definitions** | `def-` | `def-term-name`, `def-term-name_p1` |
| **FAQ** | `faq-` | `faq-1`, `FAQ 1.1` |
| **Chapters** | (numeric) | `3.1.2`, `3.1.2_p1` |
| **Executive Summary** | `executive-summary` | `executive-summary_p1` |
| **References** | `references` | `references_p1` |

---

## Current Status

### Files Found by Type

Based on `--check-only` run:

- **SPM**: 8 files (WG1, WG2, WG3, SYR × 2 each)
- **TS**: 7 files (WG1, WG2, WG3, SYR × 2 each, some may be missing)
- **Chapters**: 47 files
- **Glossary**: 4 files
- **Acronym**: 3 files
- **Definition**: 1 file

**Total**: ~63 files

### Coverage Issues Found

- **SPM files**: 0-8% paragraph coverage (needs processing)
- **TS files**: 0% paragraph coverage (needs processing)
- **Chapters**: Variable coverage (49-96%, some need reprocessing)
- **Annexes**: Many lack `html_with_ids.html` (need processing)

---

## Processing Pipeline

### Step 1: Find Files
- Scans `test/resources/ipcc/cleaned_content/`
- Identifies files needing processing
- Groups by document type

### Step 2: Check Coverage
- Parses existing `html_with_ids.html` if present
- Calculates paragraph and section ID coverage
- Skips files with good coverage (95%+ paragraphs, 99%+ sections)

### Step 3: Process Files
- Uses `IPCCGatsby.add_ids()` or `IPCCWordpress.add_ids()`
- Processes cleaned HTML file (`de_gatsby.html` or `de_wordpress.html`)
- Generates `html_with_ids.html` with semantic IDs

### Step 4: Validate
- Checks new coverage after processing
- Reports success/failure
- Generates summary statistics

---

## Expected Output Structure

After processing, each component directory should contain:

```
{component}/
├── gatsby_raw.html (or wordpress.html)      # Raw downloaded HTML
├── de_gatsby.html (or de_wordpress.html)    # Cleaned HTML
├── html_with_ids.html                       # ✅ Final HTML with semantic IDs
├── id_list.html                             # ✅ List of all IDs
└── para_list.html                           # ✅ List of paragraphs with IDs
```

---

## Troubleshooting

### Issue: "No cleaned file found"

**Solution**: The script needs either:
- `de_gatsby.html` or `de_wordpress.html` file, OR
- A source HTML file to process

If missing, you may need to run the cleaning step first.

### Issue: Low Coverage After Processing

**Possible Causes**:
1. Source HTML lacks proper section structure
2. Document type not recognized correctly
3. ID generation regex doesn't match document format

**Solution**: Check the source HTML structure and adjust ID generation logic if needed.

### Issue: PDF-Converted Files Not Processing

**Solution**: PDF-converted files may need special handling:
- Ensure they have proper section structure
- May need manual section container creation
- Check if `total_pages.html` or `annex-*.html` files exist

---

## Next Steps

1. **Run Coverage Check**:
   ```bash
   python scripts/process_ipcc_html_ids.py --check-only
   ```

2. **Process High-Priority Files** (SPM/TS):
   ```bash
   python scripts/process_ipcc_html_ids.py --component summary-for-policymakers
   python scripts/process_ipcc_html_ids.py --component technical-summary
   ```

3. **Process Annexes**:
   ```bash
   python scripts/process_ipcc_html_ids.py --component annex-i-glossary
   python scripts/process_ipcc_html_ids.py --component annex-ii-acronyms
   ```

4. **Process All Files**:
   ```bash
   python scripts/process_ipcc_html_ids.py
   ```

5. **Validate Results**:
   ```bash
   python scripts/ar6_validate_ids.py  # If available
   ```

---

## Integration with Existing Pipeline

This script integrates with the existing IPCC processing pipeline:

1. **Download**: `IPCCGatsby.download_save_chapter()` → `gatsby_raw.html`
2. **Clean**: `IPCCGatsby.remove_unnecessary_markup()` → `de_gatsby.html`
3. **Add IDs**: `IPCCGatsby.add_ids()` → `html_with_ids.html` ✅ **This script**
4. **Validate**: Check coverage and quality

---

## Notes

- The script uses existing `IPCCGatsby` and `IPCCWordpress` classes
- ID generation follows IPCC conventions from `test/ipcc_classes.py`
- Files with good coverage (95%+ paragraphs) are automatically skipped
- Dry-run mode allows previewing changes without modification

---

**Last Updated:** December 8, 2025  
**Script Location:** `scripts/process_ipcc_html_ids.py`

