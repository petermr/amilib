# AR6 IPCC Annexes Processing Decision Table

**Date:** Saturday, December 6, 2025  
**Purpose:** Decision table for selecting which AR6 annexes need processing with semantic IDs

---

## Instructions

1. Review each annex listed below
2. Check the box (☑) if the annex needs processing
3. Add your reason for the decision in the "Reason" column
4. Use the interactive HTML version (`ar6_annexes_decision_table.html`) for easier editing

---

## Decision Table

### Working Group I (WGI) - Physical Science Basis

| Process? | Report | Annex | Title | Description | Current Status | Reason |
|----------|--------|-------|-------|-------------|----------------|--------|
| ☐ | WG1 | Annex I | Glossary | Definitions of key terms used in the report | Not Processed | |
| ☐ | WG1 | Annex II | Acronyms | List of acronyms and abbreviations | Not Processed | |
| ☐ | WG1 | Annex III | Contributors | List of authors and contributors | Not Processed | |
| ☐ | WG1 | Annex IV | Reviewers | List of expert reviewers | Not Processed | |

---

### Working Group II (WGII) - Impacts, Adaptation and Vulnerability

| Process? | Report | Annex | Title | Description | Current Status | Reason |
|----------|--------|-------|-------|-------------|----------------|--------|
| ☐ | WG2 | Annex I | Global to Regional Atlas | Visualizations of climate change impacts across regions | Not Processed | |
| ☐ | WG2 | Annex II | Glossary | Definitions of key terms used in the report | Not Processed | |

---

### Working Group III (WGIII) - Mitigation of Climate Change

| Process? | Report | Annex | Title | Description | Current Status | Reason |
|----------|--------|-------|-------|-------------|----------------|--------|
| ☐ | WG3 | Annex I | Glossary | Definitions of key terms used in the report | Not Processed | |
| ☐ | WG3 | Annex II | Acronyms | List of acronyms and abbreviations | Not Processed | |
| ☐ | WG3 | Annex III | Contributors | List of authors and contributors | Not Processed | |
| ☐ | WG3 | Annex IV | Reviewers | List of expert reviewers | Not Processed | |

---

### Synthesis Report (SYR)

| Process? | Report | Annex | Title | Description | Current Status | Reason |
|----------|--------|-------|-------|-------------|----------------|--------|
| ☐ | SYR | Annex I | Glossary | Definitions of key terms used in the report | Partially Processed | |
| ☐ | SYR | Annex II | Acronyms | List of acronyms and abbreviations | Partially Processed | |
| ☐ | SYR | Annex III | Contributors | List of authors and contributors | Not Processed | |
| ☐ | SYR | Annex IV | Reviewers | List of expert reviewers | Not Processed | |
| ☐ | SYR | Annex V | List of Publications | Comprehensive list of IPCC publications | Not Processed | |
| ☐ | SYR | Annexes and Index | Combined Annexes | Combined annexes and index section (may include multiple annexes) | Partially Processed | |

---

## Notes

### Current Processing Status

- **SYR Glossary:** Partially processed - files exist in `test/resources/ipcc/syr/annexes/html/glossary/`
- **SYR Acronyms:** Partially processed - files exist in `test/resources/ipcc/syr/annexes/html/acronyms/`
- **SYR Annexes and Index:** Has `content.html` file but may need full processing

### Considerations

1. **Glossaries:** High value for semantic linking and dictionary creation
2. **Acronyms:** Useful for text processing and disambiguation
3. **Contributors/Reviewers:** Lower priority unless needed for author analysis
4. **Global to Regional Atlas (WG2):** May require special handling for visualizations
5. **List of Publications:** May be useful for citation tracking

### Processing Requirements

If selected for processing, each annex should:
- Have semantic IDs for all paragraphs, sections, and divs
- Follow the same ID generation pattern as chapters
- Be processed through the same pipeline (download → clean → add IDs)

---

## Summary

**Total Annexes:** 15  
**Selected for Processing:** _[To be filled]_  
**Not Selected:** _[To be filled]_

---

## Next Steps

After making decisions:

1. Export decisions using the HTML version (`ar6_annexes_decision_table.html`)
2. Process selected annexes using the same pipeline as chapters
3. Validate semantic IDs using `scripts/ar6_validate_ids.py`
4. Update processing status documentation

---

## Files

- **Interactive HTML:** `docs/ar6_annexes_decision_table.html` (open in browser)
- **Markdown Version:** `docs/ar6_annexes_decision_table.md` (this file)





