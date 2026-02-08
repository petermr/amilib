# DOI Schemes for Web Scraping

**Date:** 2025-12-19  
**Purpose:** Overview of schemes and standards for adding DOIs (Digital Object Identifiers) to web scraping workflows

---

## Table of Contents

1. [Introduction](#introduction)
2. [DOI Formats and Standards](#doi-formats-and-standards)
3. [HTML Metadata Schemes](#html-metadata-schemes)
4. [Extraction Methods](#extraction-methods)
5. [Implementation Approaches](#implementation-approaches)
6. [Current Implementation in amilib](#current-implementation-in-amilib)
7. [Recommendations](#recommendations)

---

## Introduction

DOIs (Digital Object Identifiers) are persistent identifiers for digital objects, commonly used for academic papers, reports, and other scholarly content. When web scraping, adding DOIs to extracted content provides:

- **Persistent linking** to original sources
- **Citation metadata** for academic references
- **Verification** of document authenticity
- **Interoperability** with citation management systems

---

## DOI Formats and Standards

### Standard DOI Format

DOIs follow the pattern: `10.XXXX/YYYY`

- **Prefix:** `10.XXXX` (assigned by DOI registration agency)
- **Suffix:** `YYYY` (assigned by publisher)

**Examples:**
- `10.1017/9781009157926.001`
- `10.1038/s41586-021-03821-8`
- `10.1080/14693062.2020.1763900`

### DOI URL Formats

DOIs can be represented in multiple URL formats:

1. **DOI Protocol:** `doi:10.1017/9781009157926.001`
2. **HTTPS:** `https://doi.org/10.1017/9781009157926.001`
3. **HTTP:** `http://dx.doi.org/10.1017/9781009157926.001`

**Best Practice:** Use `https://doi.org/` for all DOI links (most modern and secure).

---

## HTML Metadata Schemes

### 1. Schema.org (JSON-LD)

**Most Recommended:** Schema.org provides structured data markup that search engines and citation tools can parse.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "DOI",
    "value": "10.1017/9781009157926.001"
  },
  "name": "Summary for Policymakers",
  "publisher": {
    "@type": "Organization",
    "name": "Cambridge University Press"
  },
  "datePublished": "2022"
}
</script>
```

**Benefits:**
- Machine-readable
- Search engine friendly
- Citation tool compatible
- Standardized vocabulary

### 2. Dublin Core Metadata

```html
<meta name="DC.identifier" content="doi:10.1017/9781009157926.001">
<meta name="DC.relation.ispartof" content="IPCC AR6 WG3">
```

### 3. Highwire Press Tags

Commonly used by academic publishers:

```html
<meta name="citation_doi" content="10.1017/9781009157926.001">
<meta name="citation_title" content="Summary for Policymakers">
<meta name="citation_publication_date" content="2022">
```

### 4. HTML5 `<link>` Element

```html
<link rel="canonical" href="https://doi.org/10.1017/9781009157926.001">
<link rel="alternate" type="application/pdf" href="https://doi.org/10.1017/9781009157926.001">
```

### 5. HTML `<a>` Element with `data-doi` Attribute

```html
<a href="https://doi.org/10.1017/9781009157926.001" 
   data-doi="10.1017/9781009157926.001"
   class="doi-link">doi:10.1017/9781009157926.001</a>
```

---

## Extraction Methods

### 1. Text Pattern Matching

**Regex Pattern:**
```python
import re

DOI_PATTERN = re.compile(
    r'\b(?:doi:)?\s*(?:https?://(?:dx\.)?doi\.org/)?(10\.\d+/[^\s\)]+)',
    re.IGNORECASE
)

def extract_dois(text):
    """Extract DOIs from text."""
    matches = DOI_PATTERN.findall(text)
    return [match for match in matches]
```

**Common Text Patterns:**
- `doi: 10.1017/9781009157926.001`
- `doi:10.1017/9781009157926.001`
- `https://doi.org/10.1017/9781009157926.001`
- `http://dx.doi.org/10.1017/9781009157926.001`
- `(doi: 10.1017/9781009157926.001)`

### 2. HTML Element Extraction

**XPath Queries:**
```python
# Meta tags
dois = tree.xpath('//meta[@name="citation_doi"]/@content')
dois = tree.xpath('//meta[@name="DC.identifier" and contains(@content, "doi:")]/@content')

# Link elements
dois = tree.xpath('//link[@rel="canonical" and contains(@href, "doi.org")]/@href')
dois = tree.xpath('//a[contains(@href, "doi.org")]/@href')

# Data attributes
dois = tree.xpath('//*[@data-doi]/@data-doi')

# JSON-LD
import json
scripts = tree.xpath('//script[@type="application/ld+json"]')
for script in scripts:
    data = json.loads(script.text)
    # Extract DOI from structured data
```

### 3. Citation Section Parsing

DOIs often appear in reference/citation sections:

```python
def extract_dois_from_citations(html_tree):
    """Extract DOIs from citation paragraphs."""
    citations = html_tree.xpath('//p[contains(@class, "citation")] | '
                                '//div[contains(@class, "references")]//p')
    dois = []
    for citation in citations:
        text = ''.join(citation.itertext())
        dois.extend(DOI_PATTERN.findall(text))
    return dois
```

---

## Implementation Approaches

### Approach 1: Extract and Normalize

1. **Extract** DOIs from various sources (text, meta tags, links)
2. **Normalize** to standard format (`10.XXXX/YYYY`)
3. **Convert** to HTTPS URL (`https://doi.org/10.XXXX/YYYY`)
4. **Store** in structured format (JSON, database)

```python
def normalize_doi(doi_string):
    """Normalize DOI string to standard format."""
    # Remove protocol prefixes
    doi = re.sub(r'^(?:doi:|https?://(?:dx\.)?doi\.org/)', '', doi_string)
    # Remove trailing punctuation
    doi = doi.rstrip('.,;')
    # Validate format
    if re.match(r'^10\.\d+/', doi):
        return doi
    return None

def doi_to_url(doi):
    """Convert DOI to HTTPS URL."""
    return f"https://doi.org/{doi}"
```

### Approach 2: Add DOI Metadata During Scraping

1. **Detect** document type (article, report, chapter)
2. **Extract** existing DOI if present
3. **Lookup** DOI from external APIs if missing
4. **Inject** DOI into HTML as metadata

```python
def add_doi_metadata(html_tree, doi):
    """Add DOI metadata to HTML document."""
    head = html_tree.find('head')
    
    # Add meta tag
    meta = ET.SubElement(head, 'meta')
    meta.set('name', 'citation_doi')
    meta.set('content', doi)
    
    # Add JSON-LD
    script = ET.SubElement(head, 'script')
    script.set('type', 'application/ld+json')
    script.text = json.dumps({
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "DOI",
            "value": doi
        }
    })
    
    # Add link element
    link = ET.SubElement(head, 'link')
    link.set('rel', 'canonical')
    link.set('href', f"https://doi.org/{doi}")
```

### Approach 3: DOI Lookup Services

Use external APIs to resolve DOIs:

**Crossref API:**
```python
import requests

def lookup_doi_metadata(doi):
    """Lookup DOI metadata from Crossref."""
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['message']
    return None
```

**DataCite API:**
```python
def lookup_datacite_doi(doi):
    """Lookup DOI metadata from DataCite."""
    url = f"https://api.datacite.org/dois/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']
    return None
```

---

## Current Implementation in amilib

### Existing Code: `amilib/ami_bib.py`

The `Reference` class includes DOI handling:

```python
class Reference:
    DOI_REC = re.compile(r".*\s(doi:[^\s]*)\.")  # finds DOI string in running text
    DOI_PROTOCOL = "doi:"
    HTTPS_DOI_ORG = "https://doi.org/"
    
    def markup_dois_in_spans(self):
        """Iterates over contained spans until the doi-containing one is found."""
        for span in self.spans:
            text = span.text
            doi_match = self.DOI_REC.match(text)
            if doi_match:
                doi_txt = doi_match.group(1)
                if self.DOI_PROTOCOL in doi_txt:
                    doi_txt = doi_txt.replace("doi:https", "https")
                    doi_txt = doi_txt.replace(self.DOI_PROTOCOL, self.HTTPS_DOI_ORG)
                    if doi_txt.startswith(self.DOI_PROTOCOL):
                        doi_txt = "https://" + doi_txt
                    a = ET.SubElement(span.getparent(), "a")
                    a.attrib["href"] = doi_txt
                    a.text = doi_txt
                    break
```

### Current Limitations

1. **Regex Pattern:** Only matches `doi: ...` followed by period
2. **Single DOI:** Only extracts first DOI found
3. **No Metadata:** Doesn't add Schema.org or meta tags
4. **No Validation:** Doesn't validate DOI format
5. **No Lookup:** Doesn't resolve DOIs from external APIs

### HTML Structure: DOI Links

Current HTML includes empty DOI links:

```html
<a href="" id="doilink" target="_blank">doi</a>
```

These should be populated with actual DOI URLs.

---

## Recommendations

### 1. Enhanced DOI Extraction

**Improve regex pattern:**
```python
DOI_PATTERN = re.compile(
    r'\b(?:doi:)?\s*(?:https?://(?:dx\.)?doi\.org/)?(10\.\d+/[^\s\)\.,;]+)',
    re.IGNORECASE
)
```

**Extract from multiple sources:**
- Text content (paragraphs, citations)
- Meta tags (`citation_doi`, `DC.identifier`)
- Link elements (`href` attributes)
- JSON-LD structured data
- Data attributes (`data-doi`)

### 2. Add DOI Metadata During Processing

**Create `DOIEnricher` class:**
```python
class DOIEnricher:
    """Enriches HTML documents with DOI metadata."""
    
    def extract_dois(self, html_tree):
        """Extract all DOIs from document."""
        # Multiple extraction methods
        pass
    
    def add_metadata(self, html_tree, doi):
        """Add DOI metadata to HTML head."""
        # Schema.org JSON-LD
        # Meta tags
        # Link elements
        pass
    
    def populate_doi_links(self, html_tree, doi):
        """Populate empty DOI links with actual URLs."""
        # Find all <a id="doilink"> elements
        # Set href to https://doi.org/{doi}
        pass
```

### 3. Integration with Processing Pipeline

**Add to `dodo.py` tasks:**
```python
def task_add_doi_metadata():
    """Add DOI metadata to processed documents."""
    return {
        'actions': [
            'python scripts/doi_processor/add_doi_metadata.py'
        ],
        'file_dep': ['html_with_all_ids.html'],
        'targets': ['html_with_doi_metadata.html']
    }
```

### 4. DOI Validation and Resolution

**Validate DOI format:**
```python
def validate_doi(doi):
    """Validate DOI format."""
    pattern = re.compile(r'^10\.\d+/[^\s]+$')
    return bool(pattern.match(doi))
```

**Resolve DOI (optional):**
```python
def resolve_doi(doi):
    """Resolve DOI to get metadata."""
    # Use Crossref API
    # Use DataCite API
    # Fallback to DOI.org resolver
    pass
```

### 5. Schema.org Integration

**Add structured data:**
```python
def create_schema_org_doi(doi, title, publisher, date):
    """Create Schema.org JSON-LD for DOI."""
    return {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "DOI",
            "value": doi
        },
        "name": title,
        "publisher": {
            "@type": "Organization",
            "name": publisher
        },
        "datePublished": date
    }
```

---

## Summary

### Best Practices

1. **Extract DOIs** from multiple sources (text, meta tags, links)
2. **Normalize** to standard format (`10.XXXX/YYYY`)
3. **Convert** to HTTPS URLs (`https://doi.org/10.XXXX/YYYY`)
4. **Add metadata** using Schema.org JSON-LD
5. **Populate links** in HTML (`<a id="doilink">`)
6. **Validate** DOI format before use
7. **Store** DOIs in structured format for later use

### Priority Actions

1. ✅ **Enhance regex pattern** to match more DOI formats
2. ✅ **Extract DOIs** from citation sections
3. ✅ **Add Schema.org metadata** to HTML documents
4. ✅ **Populate empty DOI links** (`id="doilink"`)
5. ⏳ **Create `DOIEnricher` class** for reusable functionality
6. ⏳ **Integrate with processing pipeline** (`dodo.py`)

---

## References

- [DOI Handbook](https://www.doi.org/doi_handbook/)
- [Schema.org ScholarlyArticle](https://schema.org/ScholarlyArticle)
- [Crossref API](https://www.crossref.org/documentation/retrieve-metadata/)
- [DataCite API](https://support.datacite.org/docs/api)
- [Highwire Press Tags](https://scholar.google.com/intl/en/scholar/inclusion.html)

---

**Generated:** 2025-12-19  
**Status:** Proposal for implementation

