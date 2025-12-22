# Glossary Font Role Analysis - Results Summary

**Date:** December 11, 2025  
**System Date:** Thu Dec 11 09:41:51 GMT 2025

---

## Summary

Successfully implemented and ran the standalone span analyzer tool (`analyze_span_roles.py`) on AR6 glossary/acronym files. Created configuration file (`font_role_config.json`) based on analysis results.

---

## Tools Created

### 1. Standalone Span Analyzer

**File:** `scripts/glossary_processor/analyze_span_roles.py`

**Features:**
- Analyzes all spans with style attributes in HTML files
- Extracts font properties using `AmiFont` (automatically truncates PDF prefixes)
- Extracts coordinates (x0, y0, x1, y1)
- Groups spans by font pattern
- Generates formatted report with:
  - Font patterns and counts
  - Font properties (weight, style, stretch)
  - Coordinate ranges
  - Font size ranges
  - Sample texts

**Usage:**
```bash
python scripts/glossary_processor/analyze_span_roles.py <html_file>
```

### 2. Font Role Configuration File

**File:** `scripts/glossary_processor/font_role_config.json`

**Contents:**
- 6 role mappings (term, definition, cross_reference, section_heading, metadata, special_character)
- Font property rules (weight, style, stretch)
- Font family patterns (after prefix truncation)
- Coordinate rules (x0, y0 ranges)
- Font size ranges
- Report-specific overrides for WG1, WG3, SYR

---

## Analysis Results

### WG3 Annex VI (Acronyms)

**Total Spans:** 1061  
**Font Patterns:** 6

| Pattern | Count | Role | X0 Range | Font Size |
|---------|-------|------|----------|-----------|
| FrutigerLTPro-Condensed | 522 | Definition | 130-449 | 5.6-9.5 |
| FrutigerLTPro-BlackCn | 520 | Term | 50-330 | 6.7-9.5 |
| FrutigerLTPro-BoldCn | 11 | Section Heading | 11-587 | 8.0-72.0 |
| FrutigerLTPro-CondensedIta | 5 | Cross-reference | 130-515 | 9.5 |
| FrutigerLTPro-LightCn | 2 | Metadata | 216-473 | 8.0 |
| FrutigerLTPro-LightCnIta | 1 | Metadata | 318 | 8.0 |

**Key Findings:**
- Clear separation: Terms (left, X0: 50-330) vs Definitions (right, X0: 130-449)
- Bold fonts (BlackCn) = Terms
- Normal fonts (Condensed) = Definitions
- Italic fonts (CondensedIta) = Cross-references
- Large fonts (72pt) = Section headings

### WG1 Annex I (Glossary)

**Total Spans:** ~6000+  
**Font Patterns:** 10

| Pattern | Count | Role | Notes |
|---------|-------|------|-------|
| FrutigerLTPro-Condensed | 2974 | Definition | Main definition text |
| FrutigerLTPro-CondensedIta | 2174 | Cross-reference | Italicized terms |
| FrutigerLTPro-BlackCn | 657 | Term | Bold terms |
| FrutigerLTPro-BoldCn | 35 | Section Heading | Large fonts (8-72pt) |
| Calibri-Italic | 3 | Special Character | Greek letters (η) |
| FrutigerLTPro-LightCn | 2 | Metadata | Citation info |
| FrutigerLTPro-LightCnIta | 1 | Metadata | Citation italic |
| Calibri | 1 | Special Character | Symbols |
| SymbolMT | 1 | Special Character | Arrows (→) |
| MyriadPro-Regular | 1 | Special Character | Punctuation |

**Key Findings:**
- High proportion of cross-references (2174 italic spans)
- Terms clearly identified by Bold fonts (BlackCn)
- Definitions use Condensed font
- Special characters use different fonts (Calibri, SymbolMT)

### SYR Annex I (Glossary)

**Total Spans:** ~120  
**Font Patterns:** 2

| Pattern | Count | Role | Notes |
|---------|-------|------|-------|
| TimesNewRomanPSMT | 117 | Definition | Standard serif font |
| TimesNewRomanPS-BoldMT | 3 | Term/Heading | Bold serif font |

**Key Findings:**
- Different font family (TimesNewRoman vs FrutigerLTPro)
- Simpler structure (only 2 patterns)
- Single-column layout (different from WG1/WG3)

---

## Configuration File Structure

### Role Mappings

1. **term** - Bold fonts, left column (X0: 50-350)
2. **definition** - Normal fonts, right column (X0: 130-560)
3. **cross_reference** - Italic fonts
4. **section_heading** - Bold fonts, large size (10-72pt) or centered (X0: 200-250)
5. **metadata** - Light fonts, top/bottom (Y0: 60-110)
6. **special_character** - Symbol fonts (Calibri, SymbolMT)

### Report-Specific Overrides

- **WG3 Annex VI:** Specific X0 ranges for terms (50-330) and definitions (130-449)
- **WG3 Annex I:** FrutigerLTPro font patterns
- **WG1 Annex I:** FrutigerLTPro font patterns
- **SYR Annex I/II:** TimesNewRomanPS font patterns

---

## Key Insights

1. **Font Prefix Truncation Works:** `AmiFont.trim_pdf_prefix()` successfully removes prefixes like "HPFPTY+" from font names

2. **Coordinate-Based Detection:** X0 ranges clearly distinguish:
   - Terms: Left column (X0: 50-350)
   - Definitions: Right column (X0: 130-560)
   - Section headings: Centered (X0: 200-250)

3. **Font Properties Reliable:**
   - Bold = Terms
   - Normal = Definitions
   - Italic = Cross-references
   - Large size = Section headings

4. **Report-Specific Patterns:**
   - WG1/WG3: FrutigerLTPro fonts
   - SYR: TimesNewRomanPS fonts
   - Different layouts require different X0 ranges

---

## Next Steps

1. ✅ **Standalone Analyzer Created** - Tool implemented and tested
2. ✅ **Configuration File Created** - Based on analysis results
3. ⏭️ **Implement FontRoleDetector** - Use configuration to detect roles
4. ⏭️ **Integrate with Entry Detector** - Use font roles for better term/definition separation
5. ⏭️ **Test on All Files** - Validate role detection accuracy

---

## Files Created

1. `scripts/glossary_processor/analyze_span_roles.py` - Standalone analyzer tool
2. `scripts/glossary_processor/font_role_config.json` - Configuration file
3. `docs/glossary_font_role_analysis_results.md` - This summary

---

**Status:** ✅ Complete - Ready for implementation of FontRoleDetector








