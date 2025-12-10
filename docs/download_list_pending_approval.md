# Missing Files Download List - Pending Approval

**Date:** December 10, 2025  
**Status:** ⏳ **AWAITING AUTHORIZATION**

---

## Summary

**Total Files to Download:** 7 files
- **PDF Files:** 1
- **HTML Files:** 6

---

## Files to Download

### WG2 (Working Group II) - 7 files

#### 1. Annex III - Acronyms
- **Report:** WG2
- **Component:** Annex III - Acronyms
- **File Type:** PDF
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Annex-III.pdf`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/annex-iii-acronyms/IPCC_AR6_WGII_Annex-III.pdf`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** Unknown (typical PDF annex: 50-300 KB)

#### 2. Cross-Chapter Box 1 (ccp1)
- **Report:** WG2
- **Component:** Cross-Chapter Box 1
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp1/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp1/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

#### 3. Cross-Chapter Box 2 (ccp2)
- **Report:** WG2
- **Component:** Cross-Chapter Box 2
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp2/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp2/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

#### 4. Cross-Chapter Box 3 (ccp3)
- **Report:** WG2
- **Component:** Cross-Chapter Box 3
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp3/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp3/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

#### 5. Cross-Chapter Box 4 (ccp4)
- **Report:** WG2
- **Component:** Cross-Chapter Box 4
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp4/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp4/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

#### 6. Cross-Chapter Box 6 (ccp6)
- **Report:** WG2
- **Component:** Cross-Chapter Box 6
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp6/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp6/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

#### 7. Cross-Chapter Box 7 (ccp7)
- **Report:** WG2
- **Component:** Cross-Chapter Box 7
- **File Type:** HTML (Gatsby)
- **Download URL:** `https://www.ipcc.ch/report/ar6/wg2/chapter/ccp7/`
- **Target Location:** `test/resources/ipcc/cleaned_content/wg2/CrossChapters/ccp7/gatsby_raw.html`
- **Status:** ❌ **NOT DOWNLOADED**
- **Estimated Size:** ~500-800 KB (based on ccp5: 766,187 bytes)

---

## Already Downloaded (Not in this list)

The following files **already exist** and do not need downloading:

### WG1
- ✅ SPM - Already downloaded (574,217 bytes)
- ✅ TS - Already downloaded (1,086,948 bytes)
- ✅ Annex I (Glossary) PDF - Already downloaded (588,085 bytes)
- ⚠️ Annex II (Acronyms) - Has small HTML file (51,544 bytes), may need PDF download

### WG2
- ✅ SPM - Already downloaded (633,591 bytes)
- ✅ TS - Already downloaded (1,008,130 bytes)
- ✅ Annex II (Glossary) - Already downloaded (656,376 bytes)
- ✅ Cross-Chapter Box 5 (ccp5) - Already downloaded (766,187 bytes)

### WG3
- ✅ SPM - Already downloaded (924,120 bytes)
- ✅ TS - Already downloaded (1,440,850 bytes)
- ✅ Annex I (Glossary) PDF - Already downloaded (272,992 bytes)
- ✅ Annex VI (Acronyms) PDF - Already downloaded (133,924 bytes)

### SYR
- ✅ Longer Report - Already downloaded (~556 KB)
- ⚠️ SPM - Has small HTML file (51,576 bytes), may need PDF download
- ⚠️ TS - Has small HTML file (51,564 bytes), may need PDF download
- ⚠️ Annex I (Glossary) PDF - May already exist
- ⚠️ Annex II (Acronyms) PDF - May already exist
- ⚠️ Annexes and Index PDF - May already exist

---

## Download Strategy

### For PDF Files (1 file)
- Use direct PDF download via `requests` or `wget`
- Save to target directory
- Verify file size > 10 KB (to avoid navigation-only files)

### For HTML Files (6 files)
- Use headless browser (Selenium/Playwright) or `requests` with proper headers
- Save as `gatsby_raw.html` in target directory
- Verify file size > 100 KB (to avoid navigation-only files)
- Follow same pattern as existing ccp5 download

---

## Post-Download Processing

After downloading, these files will need:

1. **PDF Files:**
   - Convert PDF → HTML
   - Clean HTML
   - Add semantic IDs

2. **HTML Files:**
   - Clean HTML (remove navigation, tooltips)
   - Add semantic IDs

---

## Authorization

**Please review the above list and confirm:**

- [ ] ✅ **APPROVED** - Proceed with downloading all 7 files
- [ ] ❌ **REJECTED** - Do not download
- [ ] ⚠️ **MODIFIED** - Download only selected files (specify which)

**Total Estimated Download Size:** ~4-6 MB (1 PDF + 6 HTML files)

---

**Ready to proceed once authorized.**

