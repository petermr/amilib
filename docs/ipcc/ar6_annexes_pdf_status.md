# AR6 Annexes PDF Download Status

**Date:** December 6, 2025  
**Status:** Ready for PDF download and conversion

---

## Current Status

Based on the analysis of existing files, the following annexes appear to be PDF-only (failed HTML downloads with only navigation content):

### PDF-Only Annexes (Need Download)

1. **WG1 Annex I - Glossary**
   - Current HTML: 50 B (navigation only)
   - Status: ❌ Needs PDF download

2. **WG1 Annex II - Acronyms**
   - Current HTML: 50 B (navigation only)
   - Status: ❌ Needs PDF download

3. **WG3 Annex I - Glossary**
   - Current HTML: 50 B (navigation only)
   - Status: ❌ Needs PDF download

4. **WG3 Annex II - Acronyms**
   - Current HTML: 50 B (navigation only)
   - Status: ❌ Needs PDF download

### Successfully Downloaded (HTML)

5. **WG2 Annex II - Glossary**
   - Current HTML: 323.7 KB (with content)
   - Status: ✅ Complete

### Missing/Not Processed

6. **SYR Annex I - Glossary**
   - Status: ❌ Not downloaded

7. **SYR Annex II - Acronyms**
   - Status: ❌ Not downloaded

8. **SYR Annexes and Index**
   - Status: ❌ Not downloaded

---

## Next Steps

### Option 1: Manual PDF URL Input

If you have the PDF URLs for the annexes, you can provide them and the script will download and convert them.

### Option 2: Find PDF URLs Automatically

The script attempts to find PDF URLs by:
1. Trying common URL patterns
2. Checking the annex HTML pages for PDF download links
3. Using headless browser to extract PDF links (if needed)

### Option 3: Extract from Full Report PDFs

If annexes are part of the full report PDFs, we can extract them using PDF page ranges.

---

## Scripts Available

1. **`scripts/download_pdf_annexes.py`**
   - Downloads PDF annexes and converts to HTML
   - Tries multiple URL patterns
   - Saves to: `test/resources/ipcc/cleaned_content/<wg>/annex-<roman>-<type>.html`

2. **`scripts/annex_status_table.py`**
   - Generates status table showing file sizes and types
   - Run to see current status

---

## Expected Output Structure

After PDF download and conversion:

```
test/resources/ipcc/cleaned_content/
├── wg1/
│   ├── annex-i-glossary/
│   │   ├── annex-i-glossary.html  (converted from PDF)
│   │   └── [PDF file if kept]
│   └── annex-ii-acronyms/
│       ├── annex-ii-acronyms.html  (converted from PDF)
│       └── [PDF file if kept]
├── wg3/
│   ├── annex-i-glossary/
│   │   ├── annex-i-glossary.html  (converted from PDF)
│   │   └── [PDF file if kept]
│   └── annex-ii-acronyms/
│       ├── annex-ii-acronyms.html  (converted from PDF)
│       └── [PDF file if kept]
└── ...
```

---

## Usage

To download and convert PDF annexes:

```bash
python scripts/download_pdf_annexes.py
```

To view current status:

```bash
python scripts/annex_status_table.py
```

---

## Notes

- PDF URLs may need to be provided manually if automatic detection fails
- Conversion uses the existing PDF-to-HTML pipeline (`HtmlGenerator.read_pdf_convert_to_html`)
- Converted HTML files will need semantic IDs added using `IPCCGatsby.add_ids()`



