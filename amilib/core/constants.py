"""
Constants used across the amilib core module.
Extracted from xml_lib.py and util.py to avoid circular dependencies.
"""

# XML/HTML Namespaces
HTML_NS = "HTML_NS"
MATHML_NS = "MATHML_NS"
SVG_NS = "SVG_NS"
XMLNS_NS = "XMLNS_NS"
XML_NS = "XML_NS"
XLINK_NS = "XLINK_NS"

# Namespace mapping
NS_MAP = {
    HTML_NS: "http://www.w3.org/1999/xhtml",
    MATHML_NS: "http://www.w3.org/1998/Math/MathML",
    SVG_NS: "http://www.w3.org/2000/svg",
    XLINK_NS: "http://www.w3.org/1999/xlink",
    XML_NS: "http://www.w3.org/XML/1998/namespace",
    XMLNS_NS: "http://www.w3.org/2000/xmlns/",
}

# XML attributes
XML_LANG = "{" + XML_NS + "}" + 'lang'

# HTML tags
H_HTML = "html"
H_BODY = "body"
H_TBODY = "tbody"
H_DIV = "div"
H_TABLE = "table"
H_THEAD = "thead"
H_HEAD = "head"
H_TITLE = "title"
H_TD = "td"
H_TR = "tr"
H_TH = "th"

# Other HTML constants
LINK = "link"
UTF_8 = "UTF-8"
SCRIPT = "script"
STYLESHEET = "stylesheet"
TEXT_CSS = "text/css"
TEXT_JAVASCRIPT = "text/javascript"

# Section and content tags
RESULTS = "results"
SECTIONS = "sections"
TITLE = "title"

# Terminal elements for XML processing
TERMINAL_COPY = {
    "abstract", "aff", "article-id", "article-categories", "author-notes",
    "caption", "contrib-group", "fig", "history", "issue", "journal_id",
    "journal-title-group", "kwd-group", "name", "notes", "p", "permissions",
    "person-group", "pub-date", "publisher", "ref", "table", "title",
    "title-group", "volume",
}

TERMINALS = ["inline-formula"]

IGNORE_CHILDREN = {"disp-formula"}

HTML_TAGS = {
    "italic": "i",
    "p": "p",
    "sub": "sub",
    "sup": "sup",
    "tr": "tr",
}

SEC_TAGS = {"sec"}
LINK_TAGS = {"xref"}

# HTML decluttering patterns
DEFAULT_DECLUTTER = [
    ".//style", ".//script", ".//noscript", ".//meta", ".//link",
    ".//button", ".//picture", ".//svg", ".//textarea",
]

DECLUTTER_BASIC = [
    ".//style", ".//script", ".//noscript", ".//meta", ".//link", ".//textarea",
]

# Elements that cause display problems
BAD_DISPLAY = [
    "//i[not(node())]",
    "//a[@href and not(node())]",
    "//div[contains(@style, 'position:absolute')]"
]

# Util constants
GENERATE = "_GENERATE"  # should we generate IDREF? 