# AR6 Annexes Download Status

**Date:** Saturday, December 6, 2025  
**Status:** Phase 1 Complete - Downloads Successful

---

## Download Summary

✅ **Successfully Downloaded:** 5 annexes  
📁 **Location:** `test/resources/ipcc/cleaned_content/{report}/{annex-name}/`

---

## Downloaded Annexes

### WG1 (Working Group I)

1. ✅ **Annex I - Glossary**
   - Location: `test/resources/ipcc/cleaned_content/wg1/annex-i-glossary/`
   - Files: `gatsby_raw.html`, `de_gatsby.html`
   - Status: Downloaded, needs semantic IDs and Wikimedia IDs

2. ✅ **Annex II - Acronyms**
   - Location: `test/resources/ipcc/cleaned_content/wg1/annex-ii-acronyms/`
   - Files: `gatsby_raw.html`, `de_gatsby.html`
   - Status: Downloaded, needs semantic IDs and Wikimedia IDs

### WG2 (Working Group II)

3. ✅ **Annex II - Glossary**
   - Location: `test/resources/ipcc/cleaned_content/wg2/annex-ii-glossary/`
   - Files: `gatsby_raw.html`, `de_gatsby.html`
   - Status: Downloaded, needs semantic IDs and Wikimedia IDs

### WG3 (Working Group III)

4. ✅ **Annex I - Glossary**
   - Location: `test/resources/ipcc/cleaned_content/wg3/annex-i-glossary/`
   - Files: `gatsby_raw.html`, `de_gatsby.html`
   - Status: Downloaded, needs semantic IDs and Wikimedia IDs

5. ✅ **Annex II - Acronyms**
   - Location: `test/resources/ipcc/cleaned_content/wg3/annex-ii-acronyms/`
   - Files: `gatsby_raw.html`, `de_gatsby.html`
   - Status: Downloaded, needs semantic IDs and Wikimedia IDs

---

## SYR Annexes (Partially Processed)

### SYR Annex I - Glossary
- **Current Location:** `test/resources/ipcc/syr/annexes/html/glossary/`
- **Target Location:** `test/resources/ipcc/cleaned_content/syr/annex-i-glossary/`
- **Status:** Needs processing from existing files

### SYR Annex II - Acronyms
- **Current Location:** `test/resources/ipcc/syr/annexes/html/acronyms/`
- **Target Location:** `test/resources/ipcc/cleaned_content/syr/annex-ii-acronyms/`
- **Status:** Needs processing from existing files

### SYR Annexes and Index
- **Current Location:** `test/resources/ipcc/cleaned_content/syr/annexes-and-index/`
- **Status:** Has `content.html`, needs cleaning and processing

---

## Next Steps

### Phase 2: Add Semantic IDs ✅ IN PROGRESS

For each downloaded annex:
1. ✅ Run `IPCCGatsby.add_ids()` to add paragraph and section IDs
2. ⏳ Generate `html_with_ids.html`
3. ⏳ Generate `id_list.html` and `para_list.html`

### Phase 3: Add Wikimedia IDs ⏳ PENDING

For glossaries and acronyms:
1. Extract all terms/acronyms from HTML
2. Lookup Wikidata ID for each term (primary)
3. If Wikidata ID missing, lookup Wiktionary ID (fallback)
4. Add `data-wikidata-id` or `data-wiktionary-id` attributes to term elements

### Phase 4: Validation ⏳ PENDING

1. Run validation script: `python scripts/ar6_validate_ids.py`
2. Check ID coverage (target: 95%+ paragraphs)
3. Verify Wikimedia IDs added correctly
4. Check for duplicate IDs

---

## Files Created

- ✅ `scripts/process_ar6_annexes.py` - Download script
- ✅ `docs/ipcc/ar6_annexes_download_status.md` - This status document

---

## Notes

- All downloads saved to definitive repository: `test/resources/ipcc/cleaned_content/`
- Files follow naming convention: `{report}/annex-{number}-{type}/`
- Processing pipeline: Download → Clean → Add Semantic IDs → Add Wikimedia IDs → Validate





