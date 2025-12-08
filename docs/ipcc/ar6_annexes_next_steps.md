# AR6 Annexes Processing - Next Steps Proposal

**Date:** Saturday, December 6, 2025  
**Based on:** Decisions in `docs/ipcc/ar6_annexes_decisions.json`

---

## Summary of Decisions

**Total Annexes Reviewed:** 16  
**Selected for Processing:** 8  
**Not Selected:** 8

### Selected Annexes (8)

| Report | Annex | Title | Status | Reason |
|--------|-------|-------|--------|--------|
| WG1 | Annex I | Glossary | Not Processed | High value for semantic linking |
| WG1 | Annex II | Acronyms | Not Processed | Useful for text processing |
| WG2 | Annex II | Glossary | Not Processed | High value for semantic linking |
| WG3 | Annex I | Glossary | Not Processed | High value for semantic linking |
| WG3 | Annex II | Acronyms | Not Processed | Useful for text processing |
| SYR | Annex I | Glossary | Partially Processed | Complete processing needed |
| SYR | Annex II | Acronyms | Partially Processed | Complete processing needed |
| SYR | Annexes and Index | Combined Annexes | Partially Processed | Needs cleaning |

### Not Selected (8)

- All Contributors annexes (WG1, WG3, SYR) - Lower priority
- All Reviewers annexes (WG1, WG3, SYR) - Lower priority
- WG2 Annex I (Global to Regional Atlas) - Lower priority
- SYR Annex V (List of Publications) - Lower priority

---

## Processing Plan

### Phase 1: Download and Initial Processing

#### 1.1 WG1 Annexes (2 annexes)

**Annex I - Glossary**
- **URL Pattern:** `https://www.ipcc.ch/report/ar6/wg1/annex/glossary/`
- **Download Location:** `test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/`
- **Expected Output:** `test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/html_with_ids.html`
- **Processing Steps:**
  1. Download raw HTML to IPCC directory
  2. Clean navigation, tooltips, etc.
  3. Add semantic IDs to all paragraphs and sections
  4. Add Wikimedia IDs (Wikidata first, then Wiktionary) to all glossary terms
  5. Generate id_list.html and para_list.html

**Annex II - Acronyms**
- **URL Pattern:** `https://www.ipcc.ch/report/ar6/wg1/annex/acronyms/`
- **Download Location:** `test/resources/ipcc/cleaned_content/wg1/annex-ii-acronyms/`
- **Expected Output:** `test/resources/ipcc/cleaned_content/wg1/annex-ii-acronyms/html_with_ids.html`
- **Processing Steps:** Same as Annex I, with Wikimedia IDs for acronyms

#### 1.2 WG2 Annexes (1 annex)

**Annex II - Glossary**
- **URL Pattern:** `https://www.ipcc.ch/report/ar6/wg2/annex/glossary/`
- **Download Location:** `test/resources/ipcc/cleaned_content/wg2/annex-ii-glossary/`
- **Expected Output:** `test/resources/ipcc/cleaned_content/wg2/annex-ii-glossary/html_with_ids.html`
- **Processing Steps:** Same as WG1 annexes, with Wikimedia IDs for glossary terms

#### 1.3 WG3 Annexes (2 annexes)

**Annex I - Glossary**
- **URL Pattern:** `https://www.ipcc.ch/report/ar6/wg3/annex/glossary/`
- **Download Location:** `test/resources/ipcc/cleaned_content/wg3/annex-i-glossary/`
- **Expected Output:** `test/resources/ipcc/cleaned_content/wg3/annex-i-glossary/html_with_ids.html`
- **Processing Steps:** Same as WG1 annexes, with Wikimedia IDs for glossary terms

**Annex II - Acronyms**
- **URL Pattern:** `https://www.ipcc.ch/report/ar6/wg3/annex/acronyms/`
- **Download Location:** `test/resources/ipcc/cleaned_content/wg3/annex-ii-acronyms/`
- **Expected Output:** `test/resources/ipcc/cleaned_content/wg3/annex-ii-acronyms/html_with_ids.html`
- **Processing Steps:** Same as WG1 annexes, with Wikimedia IDs for acronyms

#### 1.4 SYR Annexes (3 annexes)

**Annex I - Glossary** (Partially Processed)
- **Current Status:** Files exist in `test/resources/ipcc/syr/annexes/html/glossary/`
- **Action:** Complete processing with semantic IDs
- **Expected Output:** `test/resources/ipcc/cleaned_content/syr/annex-i-glossary/html_with_ids.html`

**Annex II - Acronyms** (Partially Processed)
- **Current Status:** Files exist in `test/resources/ipcc/syr/annexes/html/acronyms/`
- **Action:** Complete processing with semantic IDs
- **Expected Output:** `test/resources/ipcc/cleaned_content/syr/annex-ii-acronyms/html_with_ids.html`

**Annexes and Index** (Partially Processed)
- **Current Status:** Has `content.html` file
- **Action:** Clean and add semantic IDs
- **Expected Output:** `test/resources/ipcc/cleaned_content/syr/annexes-and-index/html_with_ids.html`
- **Note:** User requested "please clean" - may need special handling

---

### Phase 2: Add Semantic IDs

For each annex, ensure:

1. **Paragraph IDs:**
   - Format: `{section_id}_p{index}` (e.g., `glossary-term-1_p1`)
   - All paragraphs must have IDs
   - Target: 95%+ coverage

2. **Section IDs:**
   - Glossary terms: Use term identifier (e.g., `glossary-term-1`)
   - Acronym entries: Use acronym identifier (e.g., `acronym-AI`)
   - Sections: Use hierarchical numbering

3. **Validation:**
   - No duplicate IDs
   - All semantic elements have IDs
   - ID format consistency

---

### Phase 3: Quality Assurance

1. **Run Validation Script:**
   ```bash
   python scripts/ar6_validate_ids.py
   ```

2. **Check ID Coverage:**
   - Paragraphs: Target 95%+
   - Sections: Target 99%+
   - No duplicates

3. **Content Verification:**
   - All glossary terms present
   - All acronyms present
   - Proper semantic structure

---

## Implementation Script

```python
from test.ipcc_classes import IPCCGatsby
from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL
from pathlib import Path
from test.resources import Resources

def process_selected_annexes():
    """Process all selected AR6 annexes"""
    publisher = IPCCGatsby()
    outdir = Path(Resources.TEMP_DIR, "ipcc", "ar6")
    
    # Selected annexes mapping
    # Format: (report, annex_slug, annex_name)
    selected_annexes = [
        # WG1
        ("wg1", "annex-i-glossary", "Annex I - Glossary"),
        ("wg1", "annex-ii-acronyms", "Annex II - Acronyms"),
        
        # WG2
        ("wg2", "annex-ii-glossary", "Annex II - Glossary"),
        
        # WG3
        ("wg3", "annex-i-glossary", "Annex I - Glossary"),
        ("wg3", "annex-ii-acronyms", "Annex II - Acronyms"),
        
        # SYR - Note: These may need different handling
        # ("syr", "annex-i-glossary", "Annex I - Glossary"),
        # ("syr", "annex-ii-acronyms", "Annex II - Acronyms"),
        # ("syr", "annexes-and-index", "Annexes and Index"),
    ]
    
    report_urls = {
        "wg1": WG1_URL,
        "wg2": WG2_URL,
        "wg3": WG3_URL,
        "syr": SYR_URL
    }
    
    for report, annex_slug, annex_name in selected_annexes:
        print(f"\n{'='*80}")
        print(f"Processing: {report.upper()} - {annex_name}")
        print(f"{'='*80}")
        
        wg_url = report_urls.get(report)
        if not wg_url:
            print(f"ERROR: No URL found for {report}")
            continue
        
        try:
            publisher.download_clean_chapter(
                annex_slug, 
                minsize=50000,  # Lower threshold for annexes
                outdir=outdir, 
                report=report,
                wg_url=wg_url
            )
            print(f"✅ Successfully processed {annex_name}")
        except Exception as e:
            print(f"❌ Error processing {annex_name}: {e}")

def process_syr_annexes():
    """Process SYR annexes that are partially processed"""
    # SYR annexes may need special handling since they're partially processed
    # Check existing files and complete processing
    
    syr_base = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "syr", "annexes")
    
    # Glossary
    glossary_dir = syr_base / "html" / "glossary"
    if glossary_dir.exists():
        print("Processing SYR Glossary from existing files...")
        # Use existing HTML files and add IDs
    
    # Acronyms
    acronyms_dir = syr_base / "html" / "acronyms"
    if acronyms_dir.exists():
        print("Processing SYR Acronyms from existing files...")
        # Use existing HTML files and add IDs
    
    # Annexes and Index
    annexes_index = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "syr", "annexes-and-index")
    if annexes_index.exists():
        print("Cleaning SYR Annexes and Index...")
        # Clean existing content.html and add IDs

if __name__ == "__main__":
    process_selected_annexes()
    process_syr_annexes()
```

---

## URL Patterns to Verify

Before processing, verify the actual URLs for annexes. The patterns may vary:

- **WG1 Glossary:** `https://www.ipcc.ch/report/ar6/wg1/annex/glossary/` or `/annex-i/`
- **WG1 Acronyms:** `https://www.ipcc.ch/report/ar6/wg1/annex/acronyms/` or `/annex-ii/`
- **WG2 Glossary:** `https://www.ipcc.ch/report/ar6/wg2/annex/glossary/` or `/annex-ii/`
- **WG3 Glossary:** `https://www.ipcc.ch/report/ar6/wg3/annex/glossary/` or `/annex-i/`
- **WG3 Acronyms:** `https://www.ipcc.ch/report/ar6/wg3/annex/acronyms/` or `/annex-ii/`

**Note:** The actual URL structure may need to be verified by checking the IPCC website or existing chapter URLs.

---

## Special Considerations

### SYR Annexes

1. **Partially Processed Files:**
   - Glossary and Acronyms have existing HTML files
   - May need to use existing files rather than re-downloading
   - Focus on adding semantic IDs to existing content

2. **Annexes and Index:**
   - User requested "please clean"
   - May contain multiple annexes combined
   - May need special parsing logic

### Glossary Structure

Glossaries typically have:
- Term entries (term name + definition)
- Cross-references
- May be in definition lists (`<dl>`, `<dt>`, `<dd>`)
- Need semantic IDs for each term entry

### Acronyms Structure

Acronyms typically have:
- Acronym + expansion pairs
- May be in tables or lists
- Need semantic IDs for each acronym entry

---

## Estimated Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Download & Clean (5 new annexes) | 2-3 hours |
| Phase 1 | Complete SYR processing (3 annexes) | 1-2 hours |
| Phase 2 | Add Semantic IDs (8 annexes) | 4-6 hours |
| Phase 3 | Validation & QA | 1-2 hours |
| **Total** | | **8-13 hours** |

---

## Next Actions

1. ✅ **Verify URL patterns** for annexes on IPCC website
2. ✅ **Create processing script** (see above)
3. ✅ **Test with one annex** (e.g., WG1 Glossary) before batch processing
4. ✅ **Process new annexes** (WG1, WG2, WG3)
5. ✅ **Complete SYR annexes** (use existing files, add IDs)
6. ✅ **Run validation** on all processed annexes
7. ✅ **Update documentation** with processing status

---

## Questions to Resolve

1. **URL Structure:** What are the exact URLs for annexes? (Need to verify)
2. **SYR Processing:** Should we use existing files or re-download?
3. **ID Format:** What ID format for glossary terms? (e.g., `glossary-term-{term-id}`)
4. **Acronym IDs:** What ID format for acronyms? (e.g., `acronym-{acronym}`)
5. **Annexes and Index:** How to handle combined annexes? (May need special parsing)

---

## Files Created

- ✅ `docs/ipcc/ar6_annexes_decisions.json` - Your decisions
- ✅ `docs/ipcc/ar6_annexes_decisions.md` - Markdown summary
- ✅ `docs/ipcc/ar6_annexes_next_steps.md` - This document

---

**Ready to proceed with implementation!**

