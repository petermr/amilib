# Wikipedia URL Feature Implementation

## Overview
Implemented a feature to include Wikipedia page URLs in HTML dictionary outputs, showing both the search term and the actual Wikipedia page address.

## Changes Made

### 1. Enhanced WikipediaPage Class (`amilib/wikimedia.py`)
- **Added `url` attribute**: `self.url = None` in `__init__()`
- **Set final URL**: `wikipedia_page.url = response.url` in `lookup_wikipedia_page_for_url()`
- This captures the actual Wikipedia page URL after any redirects

### 2. Updated AmiDictionary Methods (`amilib/ami_dict.py`)

#### `lookup_and_add_wikipedia_page()` method:
```python
# Store the Wikipedia page URL in the entry element
if wikipedia_page.url:
    self.element.attrib["wikipedia_url"] = wikipedia_page.url
```

#### `add_html_entries()` method:
```python
# Get Wikipedia URL from stored attribute or from current lookup
wikipedia_url = ami_entry.element.attrib.get("wikipedia_url")
if wikipedia_url is None and wikipedia_page is not None:
    wikipedia_url = wikipedia_page.url

# Create text showing search term and Wikipedia URL address
search_term = ami_entry.get_term()
p.text = f"search term: {search_term}"

if wikipedia_url is not None:
    # Add Wikipedia URL as clickable link with page title
    ET.SubElement(p, "br")  # Line break
    url_text = ET.SubElement(p, "span")
    url_text.text = "Wikipedia URL: "
    
    # Extract page title from URL for link text
    page_title = wikipedia_url.split("/wiki/")[-1] if "/wiki/" in wikipedia_url else search_term
    page_title = page_title.replace("_", " ")  # Convert underscores to spaces
    
    # Create clickable link with page title
    wiki_link = ET.SubElement(p, "a")
    wiki_link.attrib[A_HREF] = wikipedia_url
    wiki_link.text = page_title
```

### 3. Added Test Coverage (`test/test_wikimedia.py`)
- **New test**: `test_create_html_dictionary_with_wikipedia_urls()`
- Tests the complete workflow: wordlist → dictionary → Wikipedia lookup → HTML generation
- Verifies Wikipedia URLs are included in output
- Checks both visible URL text and clickable links

## HTML Output Structure

Each dictionary entry now includes:

```html
<div role="ami_entry" term="anthropogenic" wikipedia_url="https://en.wikipedia.org/wiki/Anthropogenic">
  <p>search term: anthropogenic<br>
     <span>Wikipedia URL: </span>
     <a href="https://en.wikipedia.org/wiki/Anthropogenic">Anthropogenic</a>
  </p>
  <p class="wpage_first_para"><!-- Wikipedia description --></p>
  <figure><!-- optional Wikipedia image --></figure>
</div>
```

## Features Delivered

1. **Search term display**: Shows the original search term
2. **Wikipedia URL link**: Displays "Wikipedia URL: " followed by a clickable link with the page title
3. **Page title extraction**: Automatically extracts page title from URL for link text
4. **Wikipedia content**: Includes definitions, descriptions, and figures
5. **URL storage**: Stores Wikipedia URL in entry attributes for reuse

## Test Results

- **60 tests passed**
- **6 tests skipped**
- **2 pre-existing failures** (unrelated to Wikipedia URL changes)
- **New test passes**: `test_create_html_dictionary_with_wikipedia_urls()`

## Example Output Files

Generated HTML files demonstrating the feature:
- `/Users/pm286/workspace/amilib/temp/words/html/small_2_with_wikipedia_urls.html`

## Usage

The feature works automatically when:
1. Creating dictionaries from wordlists with `--wikipedia` flag
2. Using `AmiDictionary.create_dictionary_from_wordfile()` with Wikipedia lookup
3. Generating HTML dictionaries with `create_html_dictionary()`

## Implementation Notes

- Uses existing `amilib` tools (no external dependencies)
- Follows project style guide
- Maintains backward compatibility
- Stores URLs for efficient reuse
- Handles redirects correctly via `response.url`