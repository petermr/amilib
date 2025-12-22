# Proposal: Add Paragraph IDs to SPM and TS Documents

**Date:** 2025-12-19  
**Focus:** WG1/2/3 SPM and TS documents  
**Current Status:** 0-8% paragraph ID coverage (target: 95%+)

---

## Problem Analysis

### Current Situation

All 6 SPM/TS documents have:
- ✅ Section IDs (95-100% coverage)
- ❌ Paragraph IDs (0-8% coverage)

### Root Cause

The existing `IPCCGatsby.create_and_add_id()` method (line 897-919) expects:
1. ✅ Paragraph parent with ID matching pattern `h\d-\d+-siblings` (e.g., `h1-1-siblings`) - **THIS MATCHES**
2. ❌ Grandparent container with numeric section ID matching pattern `\d+(\.\d+)*` (e.g., `3.1.2`) - **THIS FAILS**

**SPM/TS documents have:**
- Section containers with **non-numeric IDs** (e.g., `introduction`, `key-findings`)
- The structure is actually correct: paragraphs ARE in `h1-1-siblings` divs
- The grandparent container has ID `introduction` (non-numeric), which doesn't match the regex pattern `\d+(\.\d+)*`
- The regex on line 910-912 rejects non-numeric section IDs, so paragraph IDs are never created

### Evidence

From structure analysis:
- WG1 SPM has sections with IDs like `introduction` (not numeric)
- Paragraphs are inside `h1-siblings` divs
- Parent div IDs don't match the expected `h\d-\d+-siblings` pattern
- Section containers have IDs, but they're non-numeric

---

## Proposed Solution

### Approach: Enhanced Paragraph ID Generator for SPM/TS

Create a specialized method that handles SPM/TS document structure while maintaining compatibility with existing chapter processing.

### Key Design Decisions

1. **Detect Document Type** - Identify SPM/TS vs chapters
2. **Handle Non-Numeric Section IDs** - Support IDs like `introduction`, `key-findings`
3. **Incremental Processing** - Only add IDs to paragraphs that don't have them
4. **Preserve Existing IDs** - Don't overwrite existing paragraph IDs
5. **Reuse Existing Infrastructure** - Leverage `add_para_ids_and_make_id_list` framework

---

## Proposed Implementation

### Option 1: Modify Existing Method (Recommended - Simplest Fix)

**File:** `test/ipcc_classes.py`

**Method:** Modify `IPCCGatsby.create_and_add_id()` to accept non-numeric section IDs

**Current Code (line 910-912):**
```python
match = grandid is not None and re.match(
    "\\d+(\\.\\d+)*|(box|cross-chapter-box|cross-working-group-box)-\\d+(\\.\\d+)*|executive-summary|FAQ \\d+(\\.\\d+)*|references",
    grandid)
```

**Proposed Fix:**
```python
# Accept numeric section IDs, special sections, AND non-numeric alphanumeric IDs
match = grandid is not None and re.match(
    "\\d+(\\.\\d+)*|(box|cross-chapter-box|cross-working-group-box)-\\d+(\\.\\d+)*|executive-summary|FAQ \\d+(\\.\\d+)*|references|[a-z0-9\\-]+",
    grandid)
```

**Rationale:**
- Minimal change - just extend the regex pattern
- Maintains backward compatibility with chapters
- Handles SPM/TS non-numeric section IDs
- No new methods needed

### Option 2: Add Fallback Logic (More Robust)

**File:** `test/ipcc_classes.py`

**Method:** Modify `IPCCGatsby.create_and_add_id()` to handle non-numeric IDs as fallback

**Logic:**
```python
def create_and_add_id(self, id, p, parent, pindex, debug=False):
    pid = None
    match = re.match("h\\d-\\d+-siblings", id)
    if not match:
        if id.startswith("chapter-") or (id.startswith("_idContainer") or id.startswith("footnote")):
            pass
        else:
            if debug:
                print(f"cannot match {id}")
    else:
        grandparent = parent.getparent()
        grandid = grandparent.get("id")
        
        # Try numeric/special section pattern first (for chapters)
        match = grandid is not None and re.match(
            "\\d+(\\.\\d+)*|(box|cross-chapter-box|cross-working-group-box)-\\d+(\\.\\d+)*|executive-summary|FAQ \\d+(\\.\\d+)*|references",
            grandid)
        
        # If that fails, try non-numeric alphanumeric pattern (for SPM/TS)
        if not match and grandid:
            match = re.match(r'^[a-z0-9\-]+$', grandid)
        
        if not match:
            if debug:
                print(f"grandid does not match {grandid}")
        else:
            pid = f"{grandid}_p{pindex}"
            p.attrib["id"] = pid
    return pid
```

**Rationale:**
- More explicit handling
- Easier to debug
- Clear separation of logic

### Option 2: Standalone Script (Alternative)

**File:** `scripts/add_spm_ts_paragraph_ids.py`

**Approach:** Create standalone script that:
1. Finds all SPM/TS `html_with_ids.html` files
2. Processes each file to add paragraph IDs
3. Uses specialized logic for SPM/TS structure
4. Regenerates `id_list.html` and `para_list.html`

---

## Detailed Algorithm

### Step 1: Find Section Containers

```python
# Find all section containers with IDs
section_containers = root.xpath('.//div[contains(@class, "h1-container")][@id] | '
                               './/div[contains(@class, "h2-container")][@id] | '
                               './/div[contains(@class, "h3-container")][@id]')
```

### Step 2: For Each Section Container

```python
for container in section_containers:
    section_id = container.get('id')
    
    # Find all paragraphs in this section
    # Look in siblings divs first, then directly in container
    paragraphs = container.xpath('.//div[contains(@class, "h1-siblings")]//p | '
                                 './/div[contains(@class, "h2-siblings")]//p | '
                                 './/div[contains(@class, "h3-siblings")]//p | '
                                 './/p[not(ancestor::div[contains(@class, "h1-siblings")] | '
                                         'ancestor::div[contains(@class, "h2-siblings")] | '
                                         'ancestor::div[contains(@class, "h3-siblings")])]')
    
    # Add IDs to paragraphs without IDs
    for pindex, p in enumerate(paragraphs, 1):
        if not p.get('id'):  # Only add if missing
            pid = f"{section_id}_p{pindex}"
            p.attrib["id"] = pid
```

### Step 3: Handle Edge Cases

1. **Paragraphs Outside Sections**
   - Use document-level prefix (e.g., `spm-`, `ts-`)
   - Sequential numbering: `spm-p1`, `spm-p2`, etc.

2. **Nested Sections**
   - Use most specific section ID (deepest container)
   - Handle subsections within sections

3. **Special Sections**
   - Handle non-standard section IDs
   - Preserve existing IDs

---

## Implementation Plan

### Phase 1: Fix Core Method (Day 1)

1. **Modify `create_and_add_id()` method** (Option 1 - Recommended)
   - Extend regex pattern to accept non-numeric section IDs
   - Test with WG1 SPM to verify fix works
   - Ensure backward compatibility with chapters

2. **Alternative: Add fallback logic** (Option 2)
   - Add fallback pattern matching for non-numeric IDs
   - More explicit but slightly more complex

### Phase 2: Testing and Validation (Week 1)

1. **Test on WG1 SPM**
   - Verify paragraph ID generation
   - Check ID format
   - Validate coverage

2. **Test on WG1 TS**
   - Verify with different structure
   - Check edge cases

3. **Validate ID Lists**
   - Regenerate `id_list.html`
   - Regenerate `para_list.html`
   - Verify completeness

### Phase 3: Batch Processing (Week 1)

1. **Process All SPM/TS Documents**
   - WG1, WG2, WG3 SPM
   - WG1, WG2, WG3 TS

2. **Verify Coverage**
   - Check all documents achieve 95%+ coverage
   - Validate ID uniqueness
   - Check ID format consistency

### Phase 4: Integration (Week 2)

1. **Integrate with AR6 Processor**
   - Add as stage processor
   - Support incremental processing
   - Update registry

2. **Documentation**
   - Document ID format
   - Document usage
   - Update processing guides

---

## ID Format Specification

### For SPM Documents

**Format:** `{section_id}_p{index}`

**Examples:**
- `introduction_p1`, `introduction_p2`
- `key-findings_p1`, `key-findings_p2`
- `A_p1`, `A_p2` (for lettered sections)
- `1_p1`, `1_p2` (for numbered sections)

### For TS Documents

**Format:** `{section_id}_p{index}`

**Examples:**
- `introduction_p1`, `introduction_p2`
- `1.1_p1`, `1.1_p2` (for numeric sections)
- `A.1_p1`, `A.1_p2` (for lettered sections)

### For Paragraphs Outside Sections

**Format:** `{doc_prefix}-p{index}`

**Examples:**
- `spm-p1`, `spm-p2` (for SPM)
- `ts-p1`, `ts-p2` (for TS)

---

## Script Structure

### Main Script: `scripts/add_spm_ts_paragraph_ids.py`

```python
#!/usr/bin/env python3
"""
Add paragraph IDs to SPM and TS documents.

Processes all SPM/TS documents for WG1/2/3 and adds paragraph IDs
to achieve 95%+ coverage.

After fixing create_and_add_id() method, this script simply re-runs
the ID generation process on cleaned HTML files.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test.ipcc_classes import IPCCGatsby
from test.resources import Resources
from test.ipcc_constants import HTML_WITH_IDS, ID_LIST, PARA_LIST

# Target documents
SPM_TS_DOCUMENTS = [
    {"report": "wg1", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg1", "doc": "technical-summary", "type": "ts"},
    {"report": "wg2", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg2", "doc": "technical-summary", "type": "ts"},
    {"report": "wg3", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg3", "doc": "technical-summary", "type": "ts"},
]

def check_coverage(html_file):
    """Check paragraph ID coverage."""
    from lxml import html
    from lxml.html import HTMLParser
    
    parser = HTMLParser(recover=True)
    tree = html.parse(str(html_file), parser=parser)
    root = tree.getroot()
    
    total_paras = len(root.xpath('.//p'))
    paras_with_ids = len(root.xpath('.//p[@id]'))
    
    return {
        'total': total_paras,
        'with_ids': paras_with_ids,
        'coverage': paras_with_ids * 100 / total_paras if total_paras > 0 else 0
    }

def process_document(report, doc, doc_type, dry_run=False):
    """Process a single SPM/TS document."""
    base_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
    doc_dir = base_dir / report / doc
    
    # Find cleaned HTML file
    cleaned_file = doc_dir / "de_gatsby.html"
    if not cleaned_file.exists():
        print(f"⚠️  Skipping {report}/{doc}: de_gatsby.html not found")
        return False
    
    print(f"\n{'='*80}")
    print(f"Processing: {report.upper()} - {doc_type.upper()}")
    print(f"Directory: {doc_dir}")
    print(f"{'='*80}")
    
    # Check current coverage
    existing_ids_file = doc_dir / f"{HTML_WITH_IDS}.html"
    if existing_ids_file.exists():
        coverage = check_coverage(existing_ids_file)
        print(f"Current Coverage: {coverage['with_ids']}/{coverage['total']} ({coverage['coverage']:.1f}%)")
        
        if coverage['coverage'] >= 95:
            print(f"✅ Already has good coverage, skipping")
            return True
    
    if dry_run:
        print(f"DRY RUN: Would process {cleaned_file}")
        return True
    
    publisher = IPCCGatsby()
    
    # Add paragraph IDs (this will use the fixed create_and_add_id method)
    html_ids_file, idfile, parafile = publisher.add_para_ids_and_make_id_list(
        infile=str(cleaned_file),
        idfile=str(doc_dir / f"{ID_LIST}.html"),
        outfile=str(doc_dir / f"{HTML_WITH_IDS}.html"),
        parafile=str(doc_dir / f"{PARA_LIST}.html")
    )
    
    # Verify coverage
    coverage = check_coverage(html_ids_file)
    print(f"New Coverage: {coverage['with_ids']}/{coverage['total']} ({coverage['coverage']:.1f}%)")
    
    if coverage['coverage'] >= 95:
        print(f"✅ Success! Achieved {coverage['coverage']:.1f}% coverage")
        return True
    else:
        print(f"⚠️  Warning: Only {coverage['coverage']:.1f}% coverage (target: 95%+)")
        return False

def main():
    """Process all SPM/TS documents."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add paragraph IDs to SPM/TS documents')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without actually processing')
    parser.add_argument('--report', choices=['wg1', 'wg2', 'wg3'], help='Process specific report only')
    parser.add_argument('--doc-type', choices=['spm', 'ts'], help='Process specific document type only')
    
    args = parser.parse_args()
    
    documents = SPM_TS_DOCUMENTS
    
    if args.report:
        documents = [d for d in documents if d['report'] == args.report]
    
    if args.doc_type:
        documents = [d for d in documents if d['type'] == args.doc_type]
    
    print(f"\nProcessing {len(documents)} documents")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    results = []
    for doc_info in documents:
        success = process_document(
            report=doc_info["report"],
            doc=doc_info["doc"],
            doc_type=doc_info["type"],
            dry_run=args.dry_run
        )
        results.append({
            'doc': f"{doc_info['report']}/{doc_info['doc']}",
            'success': success
        })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"Summary")
    print(f"{'='*80}")
    successful = sum(1 for r in results if r['success'])
    print(f"Processed: {successful}/{len(results)} documents")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"  {status} {r['doc']}")

if __name__ == '__main__':
    main()
```

---

## Testing Strategy

### Unit Tests

1. **Test `_normalize_section_id()`**
   - Numeric IDs: `"3.1.2"` → `"3.1.2"`
   - Non-numeric IDs: `"introduction"` → `"introduction"`
   - Edge cases: empty, None, invalid

2. **Test `create_and_add_id_spm_ts()`**
   - Paragraph ID generation
   - Index handling
   - ID uniqueness

### Integration Tests

1. **Test on WG1 SPM**
   - Process document
   - Verify paragraph ID coverage
   - Check ID format

2. **Test on WG1 TS**
   - Process document
   - Verify different structure handling
   - Check edge cases

### Validation Tests

1. **ID Coverage**
   - Verify 95%+ paragraph ID coverage
   - Check all sections have paragraph IDs

2. **ID Uniqueness**
   - No duplicate IDs
   - All IDs valid

3. **ID Lists**
   - `id_list.html` contains all IDs
   - `para_list.html` contains all paragraphs

---

## Expected Outcomes

### Before Processing

- WG1 SPM: 15/192 paragraphs with IDs (7%)
- WG1 TS: 0/587 paragraphs with IDs (0%)
- WG2 SPM: 17/192 paragraphs with IDs (8%)
- WG2 TS: 0/567 paragraphs with IDs (0%)
- WG3 SPM: 28/776 paragraphs with IDs (3%)
- WG3 TS: 0/1,726 paragraphs with IDs (0%)

### After Processing

- **All documents:** 95%+ paragraph ID coverage ✅
- **ID lists:** Complete and accurate ✅
- **ID format:** Consistent across all documents ✅

---

## Risks and Mitigation

### Risk 1: Breaking Existing Functionality

**Mitigation:**
- Add new method, don't modify existing
- Use feature detection (check document type)
- Maintain backward compatibility

### Risk 2: ID Conflicts

**Mitigation:**
- Check for existing IDs before adding
- Use section ID + index for uniqueness
- Validate uniqueness after processing

### Risk 3: Different Structures

**Mitigation:**
- Analyze structure first
- Handle multiple structure patterns
- Test on all 6 documents

---

## Questions for Review

1. **Fix Approach:** 
   - Option 1: Simple regex extension (minimal change, recommended)
   - Option 2: Fallback logic (more explicit, slightly more complex)
   - Which approach do you prefer?

2. **ID Format:** 
   - Current: `{section_id}_p{index}` (e.g., `introduction_p1`)
   - Is this format acceptable for SPM/TS?

3. **Incremental Processing:** 
   - Should we skip paragraphs that already have IDs?
   - Or regenerate all IDs (may change existing IDs)?

4. **Testing:** 
   - Test on single document first (WG1 SPM)?
   - Or process all 6 documents at once?

5. **Integration:** 
   - Should this be integrated into AR6 incremental processor?
   - Or keep as standalone script?

---

## Next Steps

1. **Review Proposal** - Get feedback on approach (Option 1 vs Option 2)
2. **Fix `create_and_add_id()` Method** - Extend regex or add fallback logic
3. **Test on Single Document** - Verify fix works with WG1 SPM
4. **Process All Documents** - Run script on all 6 documents
5. **Validate Results** - Verify 95%+ coverage achieved for all documents

## Estimated Effort

- **Fix Method:** 30 minutes (simple regex change)
- **Test on Single Document:** 15 minutes
- **Process All Documents:** 10 minutes
- **Validation:** 15 minutes
- **Total:** ~1.5 hours

---

## Appendix: Current Structure Analysis

### WG1 SPM Structure

```
<div class="h1-container" id="introduction">
  <h1>Introduction</h1>
  <div class="h1-siblings" id="h1-1-siblings">
    <p>Paragraph 1 (no ID)</p>
    <p>Paragraph 2 (no ID)</p>
    ...
  </div>
</div>
```

**Issue:** Parent div ID is `h1-1-siblings` (matches pattern), but grandparent ID is `introduction` (non-numeric, doesn't match expected pattern `\d+(\.\d+)*`).

### Solution

Modify `create_and_add_id()` to:
1. Accept non-numeric section IDs
2. Use section ID directly (don't require numeric pattern)
3. Generate paragraph IDs: `{section_id}_p{index}`

---

**Ready for Review**

This proposal addresses the paragraph ID coverage issue for SPM/TS documents. Please review and provide feedback before implementation.

