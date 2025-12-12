"""
Constants for IPCC Dictionary Template.

Centralizes all dictionary template-related constants including:
- HTML roles and classes
- Data attributes
- XPath expressions
- File names
- Report values
"""

# ===== HTML ROLES =====
ROLE_IPCC_DICTIONARY = "ipcc_dictionary"
ROLE_DICTIONARY_ENTRY = "dictionary_entry"
ROLE_DICTIONARY_METADATA = "dictionary_metadata"
ROLE_TERM = "term"
ROLE_DEFINITION = "definition"
ROLE_DESCRIPTION = "description"
ROLE_CROSS_REFERENCES = "cross_references"
ROLE_ABBREVIATION = "abbreviation"
ROLE_SECTION_HEADING = "section_heading"
ROLE_SECTION = "dictionary_section"

# ===== HTML CLASSES =====
CLASS_GLOSSARY = "glossary"
CLASS_ENTRY = "entry"
CLASS_TERM = "term"
CLASS_DEFINITION = "definition"
CLASS_DESCRIPTION = "description"
CLASS_CROSS_REFERENCES = "cross-references"
CLASS_TERM_TEXT = "term-text"
CLASS_DEFINITION_TEXT = "definition-text"
CLASS_DESCRIPTION_PARAGRAPH = "description-paragraph"
CLASS_CROSS_REF_LINK = "cross-ref-link"
CLASS_CROSS_REF_LABEL = "cross-ref-label"
CLASS_ABBREVIATION = "abbreviation"
CLASS_INTERNAL_LINK = "internal-link"
CLASS_ROLE_TERM = "role-term"
CLASS_ROLE_DEFINITION = "role-definition"
CLASS_ROLE_CROSS_REFERENCE = "role-cross_reference"
CLASS_ROLE_SECTION_HEADING = "role-section_heading"
CLASS_ROLE_METADATA = "role-metadata"
CLASS_DICTIONARY_TITLE = "dictionary-title"
CLASS_METADATA_DETAILS = "metadata-details"
CLASS_METADATA_LIST = "metadata-list"
CLASS_DICTIONARY_SECTION = "dictionary-section"
CLASS_DICTIONARY_ENTRIES = "dictionary-entries"

# ===== HTML ELEMENTS =====
TAG_HTML = "html"
TAG_HEAD = "head"
TAG_BODY = "body"
TAG_DIV = "div"
TAG_DL = "dl"
TAG_DT = "dt"
TAG_DD = "dd"
TAG_SPAN = "span"
TAG_A = "a"
TAG_H1 = "h1"
TAG_H2 = "h2"
TAG_SECTION = "section"
TAG_P = "p"
TAG_SUB = "sub"
TAG_SUP = "sup"
TAG_EM = "em"
TAG_STRONG = "strong"
TAG_STYLE = "style"

# ===== DATA ATTRIBUTES =====
DATA_SCHEMA_VERSION = "data-schema-version"
DATA_REPORT = "data-report"
DATA_ANNEX = "data-annex"
DATA_ANNEX_TYPE = "data-annex-type"
DATA_SOURCE_PDF = "data-source-pdf"
DATA_CONVERSION_DATE = "data-conversion-date"
DATA_CONVERSION_TOOL = "data-conversion-tool"
DATA_ENTRY_NUMBER = "data-entry-number"
DATA_TERM = "data-term"
DATA_HAS_DEFINITION = "data-has-definition"
DATA_HAS_DESCRIPTION = "data-has-description"
DATA_HAS_ABBREVIATION = "data-has-abbreviation"
DATA_SECTION = "data-section"
DATA_SOURCE = "data-source"
DATA_DATE = "data-date"
DATA_ENTRY_COUNT = "data-entry-count"
DATA_LAYOUT = "data-layout"
DATA_VARIANT = "data-variant"

# ===== HTML ATTRIBUTES =====
ATTR_ID = "id"
ATTR_CLASS = "class"
ATTR_ROLE = "role"
ATTR_HREF = "href"
ATTR_TYPE = "type"
ATTR_LANG = "lang"

# ===== REPORT VALUES =====
REPORT_WG1 = "wg1"
REPORT_WG2 = "wg2"
REPORT_WG3 = "wg3"
REPORT_SYR = "syr"

VALID_REPORTS = [REPORT_WG1, REPORT_WG2, REPORT_WG3, REPORT_SYR]

# ===== ANNEX TYPES =====
ANNEX_TYPE_GLOSSARY = "glossary"
ANNEX_TYPE_ACRONYMS = "acronyms"

# ===== LAYOUT TYPES =====
LAYOUT_SINGLE_COLUMN = "single-column"
LAYOUT_TWO_COLUMN = "two-column"
LAYOUT_MULTI_COLUMN = "multi-column"

# ===== XPath EXPRESSIONS =====
XPATH_DICT_CONTAINER = f'//div[@role="{ROLE_IPCC_DICTIONARY}"] | //div[@class="{CLASS_GLOSSARY}"]'
XPATH_DICT_ENTRIES = f'.//div[@class="{CLASS_ENTRY}"] | .//div[@role="{ROLE_DICTIONARY_ENTRY}"]'
XPATH_TERMS = f'.//div[@role="{ROLE_TERM}"] | .//dt[@role="{ROLE_TERM}"]'
XPATH_DEFINITIONS = f'.//div[@role="{ROLE_DEFINITION}"] | .//dd[@role="{ROLE_DEFINITION}"]'
XPATH_METADATA = f'.//div[@role="{ROLE_DICTIONARY_METADATA}"] | .//h1'
XPATH_CROSS_REFS = './/a[@href]'
XPATH_HEAD = '/html/head'
XPATH_BODY = '/html/body'

# ===== FILE NAMES =====
FILENAME_WG3_ANNEX_VI_SAMPLE = "wg3_annex_vi_sample_3_entries.html"
FILENAME_WG3_ANNEX_VI_CROSSREF = "wg3_annex_vi_with_crossref.html"
FILENAME_WG3_ANNEX_VI_MIXED_CONTENT = "wg3_annex_vi_with_mixed_content.html"
FILENAME_SYR_ANNEX_I_SAMPLE = "syr_annex_i_sample_single_column.html"
FILENAME_WG3_ANNEX_VI_VALIDATED = "wg3_annex_vi_validated.html"
FILENAME_WG3_ANNEX_VI_VALIDATION_REPORT = "wg3_annex_vi_validation_report.html"
FILENAME_WG3_ANNEX_VI_EXTRACTED_ENTRIES = "wg3_annex_vi_extracted_entries.html"
FILENAME_WG3_ANNEX_VI_MIXED_CONTENT_OUTPUT = "wg3_annex_vi_mixed_content.html"
FILENAME_WG3_ANNEX_VI_WITH_ITALICS = "wg3_annex_vi_with_italics_hyperlinks.html"

# ===== OUTPUT DIRECTORY =====
OUTPUT_DIR_DICTIONARY_TEMPLATE = "ipcc_dictionary_template"

# ===== CSS CLASSES FOR ROLES =====
CSS_CLASS_ROLE_PREFIX = "role-"

# ===== VALIDATION MESSAGES =====
MSG_NO_DICT_CONTAINER = "No dictionary container found (expected div with role='ipcc_dictionary' or class='glossary')"
MSG_MULTIPLE_CONTAINERS = "Multiple dictionary containers found ({count}), using first"
MSG_MISSING_REQUIRED_ATTR = "Dictionary container missing required attribute: {attr}"
MSG_UNKNOWN_REPORT = "Unknown report value: {report}"
MSG_NO_METADATA = "No metadata section found (expected div[@role='dictionary_metadata'] or h1)"
MSG_NO_ENTRIES = "No dictionary entries found"
MSG_ENTRY_MISSING_ID = "Entry {num} missing required 'id' attribute"
MSG_DUPLICATE_ID = "Duplicate entry ID: {id}"
MSG_ENTRY_MISSING_TERM = "Entry {num} (id={id}) missing required term element"
MSG_ENTRY_MISSING_DATA_TERM = "Entry {num} (id={id}) missing optional 'data-term' attribute"
MSG_ENTRY_MISSING_DATA_NUMBER = "Entry {num} (id={id}) missing optional 'data-entry-number' attribute"
MSG_EMPTY_TERM = "Entry {num} (id={id}) has empty term"
MSG_NO_DEFINITION = "Entry {num} (id={id}) has no definition"
MSG_INVALID_CROSS_REF = "Entry {num} (id={id}) has cross-reference to non-existent entry: {target_id}"
MSG_ROOT_MUST_BE_HTML = "Root element must be <html>"
MSG_NO_HEAD = "No <head> element found"
MSG_NO_BODY = "No <body> element found"
MSG_ERROR_PARSING = "Error parsing HTML: {error}"
MSG_ERROR_ANALYZING = "Error analyzing structure: {error}"

