# Wikimedia Module Overview

## Introduction

The Wikimedia module provides comprehensive functionality for interacting with Wikipedia, Wikidata, and Wiktionary. This document outlines the basic operations for Wikipedia lookup and the comprehensive test coverage for different types of Wikipedia pages.

## Wikipedia Lookup Basic Operations

### 1. Core Lookup Methods

#### `lookup_wikipedia_page_for_term(search_term)`
- **Purpose**: Gets Wikipedia page by searching for a term/phrase
- **Input**: Search term (string)
- **Output**: WikipediaPage object or None
- **Implementation**: 
  - Constructs search URL: `https://en.wikipedia.org/w/index.php?search={search_term}&title=Special%3ASearch&ns0=1`
  - Calls `lookup_wikipedia_page_for_url()` with the search URL
  - Sets the search_term on the returned page

#### `lookup_wikipedia_page_for_url(url)`
- **Purpose**: Downloads and parses Wikipedia page from URL
- **Input**: Wikipedia URL (can be search URL or direct page URL)
- **Output**: WikipediaPage object or None
- **Implementation**:
  - Makes HTTP GET request to the URL
  - Decodes content as UTF-8
  - Parses HTML content
  - Creates WikipediaPage object with parsed HTML

### 2. Content Extraction Methods

#### `get_main_element()`
- **Purpose**: Extracts main content from Wikipedia page
- **Output**: Cleaned main content element
- **Implementation**:
  - Finds `<main>` element using XPath
  - Removes navigation, noscript, and language button elements
  - Returns cleaned main content

#### `create_first_wikipedia_para()`
- **Purpose**: Gets first meaningful paragraph (usually contains definitions)
- **Output**: WikipediaPara wrapper object
- **Implementation**:
  - Gets main element
  - Finds first paragraph with sufficient length (> MIN_FIRST_PARA_LEN)
  - Returns WikipediaPara wrapper

### 3. Metadata Extraction Methods

#### `get_wikidata_item()`
- **Purpose**: Extracts Wikidata item ID from Wikipedia page
- **Output**: Wikidata URL or None
- **Implementation**:
  - Looks for Wikidata item link in page tools
  - Extracts href attribute from Wikidata item link

#### `get_infobox()`
- **Purpose**: Extracts infobox table from Wikipedia page
- **Output**: WikipediaInfoBox object or None
- **Implementation**:
  - Finds table with 'infobox' class
  - Returns WikipediaInfoBox wrapper

#### `get_basic_information()`
- **Purpose**: Extracts basic page information table
- **Output**: BasicInformation wrapper object
- **Implementation**:
  - Finds page info table with basic metadata

### 4. Batch Processing Methods

#### `lookup_pages_for_words_in_file(filestem, indir, suffix=".txt")`
- **Purpose**: Processes multiple words from a file
- **Input**: File stem, input directory, file suffix
- **Output**: Dictionary mapping words to Wikipedia pages

#### `create_page_dict_for_words_in_file(inpath)`
- **Purpose**: Creates dictionary of Wikipedia pages for words in file
- **Input**: File path
- **Output**: Dictionary {word: WikipediaPage}

### 5. Special Page Handling

#### `is_disambiguation_page()`
- **Purpose**: Detects if page is a disambiguation page
- **Output**: Boolean
- **Implementation**: Checks central description for "Wikimedia disambiguation page"

#### `get_disambiguation_list()`
- **Purpose**: Extracts disambiguation options from disambiguation page
- **Output**: List of disambiguation options
- **Implementation**: Finds list items following "may refer to:" text

### 6. Utility Methods

#### `get_default_wikipedia_url()`
- **Purpose**: Returns base Wikipedia URL
- **Output**: "https://en.wikipedia.org/"

#### `create_html_of_leading_wp_paragraphs(words, outfile=None, debug=True)`
- **Purpose**: Creates HTML file with leading paragraphs for multiple words
- **Input**: List of words, optional output file, debug flag
- **Output**: HTML content with paragraphs

## Test Coverage for Different Wikipedia Page Types

### 1. Basic Page Type Detection Tests

#### Direct Entry Pages
- **Test Method**: `test_wikipedia_lookup_direct_entry`
- **Test Term**: "climate change"
- **Expected Behavior**: 
  - Page exists (`page.exists()` = True)
  - Not disambiguation (`page.is_disambiguation()` = False)
  - Not redirect (`page.is_redirect()` = False)
  - Has content (title, first paragraph)

#### Disambiguation Pages
- **Test Method**: `test_wikipedia_lookup_disambiguation`
- **Test Term**: "greenhouse"
- **Expected Behavior**:
  - Page exists (`page.exists()` = True)
  - Is disambiguation (`page.is_disambiguation()` = True)
  - Not redirect (`page.is_redirect()` = False)
  - Has disambiguation options list

#### Redirect Pages
- **Test Method**: `test_wikipedia_lookup_redirect`
- **Test Term**: "global warming"
- **Expected Behavior**:
  - Page exists (`page.exists()` = True)
  - Not disambiguation (`page.is_disambiguation()` = False)
  - Is redirect (`page.is_redirect()` = True)
  - Has redirect target

#### Page Not Found
- **Test Method**: `test_wikipedia_lookup_page_not_found`
- **Test Term**: "nonexistentclimateterm12345"
- **Expected Behavior**:
  - Page doesn't exist (`page.exists()` = False)
  - Not disambiguation (`page.is_disambiguation()` = False)
  - Not redirect (`page.is_redirect()` = False)

### 2. Acronym-Specific Page Type Tests

#### Acronym Direct Entry
- **Test Method**: `test_wikipedia_lookup_acronym_direct_entry`
- **Test Term**: "IPCC"
- **Expected Behavior**: Same as direct entry but for acronyms

#### Acronym Disambiguation
- **Test Method**: `test_wikipedia_lookup_acronym_disambiguation`
- **Test Term**: "CO2"
- **Expected Behavior**: Same as disambiguation but for acronyms

#### Acronym Redirect
- **Test Method**: `test_wikipedia_lookup_acronym_redirect`
- **Test Term**: "GHG"
- **Expected Behavior**: Same as redirect but for acronyms

#### Acronym Page Not Found
- **Test Method**: `test_wikipedia_lookup_acronym_page_not_found`
- **Test Term**: "NONEXISTENT123"
- **Expected Behavior**: Same as page not found but for acronyms

### 3. Content Extraction Tests

#### First Paragraph Extraction
- **Test Method**: `test_wikipedia_page_first_para`
- **Test Term**: "Greenhouse gas"
- **Purpose**: Tests extraction of first meaningful paragraph
- **Validation**: Ensures `create_first_wikipedia_para()` returns non-None

#### Bold Text and Links Extraction
- **Test Method**: `test_wikipedia_page_first_para_bold_ahrefs`
- **Test Term**: "Greenhouse gas"
- **Purpose**: Tests extraction of bold text and hyperlinks
- **Validation**: 
  - 2 bold elements (including "Greenhouse gas")
  - 9 hyperlinks (including "ocean current" → "/wiki/Ocean_current")

#### Text Processing and Formatting
- **Test Method**: `test_wikipedia_page_first_para_sentence_span_tails`
- **Purpose**: Tests wrapping of mixed content text in spans
- **Validation**: Complex HTML structure with proper formatting

### 4. Batch Processing Tests

#### Multiple Word Lookup
- **Test Method**: `test_wikipedia_lookup_climate_words_short`
- **Purpose**: Tests batch lookup of multiple climate terms
- **File**: "small_2.txt" wordlist
- **Output**: Dictionary of Wikipedia pages

#### Multiple Wordlist Processing
- **Test Method**: `test_wikipedia_lookup_several_word_lists`
- **Purpose**: Tests processing multiple wordlist files
- **Files**: Various climate-related wordlists
- **Output**: HTML files with extracted content

### 5. Service Connection Tests

All the main lookup tests include **connection validation**:
```python
connection_result = FileLib.check_service_connection(
    service_url=WIKIPEDIA_SERVICE_URL,
    service_name=WIKIPEDIA_SERVICE_NAME,
    timeout=10
)
self.assertTrue(connection_result['connected'])
```

### 6. Page Type Detection Methods Tested

The tests validate these key methods on WikipediaPage objects:

- **`page.exists()`** - Page availability
- **`page.is_disambiguation()`** - Disambiguation page detection
- **`page.is_redirect()`** - Redirect page detection
- **`page.get_title()`** - Page title extraction
- **`page.get_first_paragraph()`** - First paragraph content
- **`page.get_disambiguation_options()`** - Disambiguation choices
- **`page.get_redirect_target()`** - Redirect destination

## Climate Change Focus

All tests use **climate change terminology** as per the style guide:
- **Direct terms**: "climate change", "greenhouse gas"
- **Disambiguation**: "greenhouse", "CO2"
- **Redirects**: "global warming", "GHG"
- **Acronyms**: "IPCC", "CO2", "GHG"

## Test Coverage Summary

The test suite comprehensively covers:

1. **Page Existence** - All four states (exists, doesn't exist, disambiguation, redirect)
2. **Content Types** - Regular terms and acronyms
3. **Content Extraction** - Paragraphs, formatting, links
4. **Batch Processing** - Multiple terms and wordlists
5. **Service Reliability** - Connection validation
6. **Edge Cases** - Non-existent terms, complex formatting
7. **Climate Domain** - Relevant terminology for the project

## Implementation Notes

### Error Handling
- All methods include proper exception handling
- Graceful degradation when pages are not found
- Logging of errors for debugging

### Performance Considerations
- HTTP requests include timeout handling
- Batch processing for multiple terms
- Efficient HTML parsing using lxml

### Dependencies
- `requests` for HTTP operations
- `lxml` for HTML/XML parsing
- `pathlib` for file operations
- Custom HTML and XML utility libraries

## Future Enhancements

1. **Caching** - Implement page caching to reduce API calls
2. **Rate Limiting** - Add rate limiting for Wikipedia API compliance
3. **Internationalization** - Support for non-English Wikipedia pages
4. **Advanced Search** - Implement more sophisticated search algorithms
5. **Content Validation** - Add content quality assessment metrics

## Conclusion

The Wikimedia module provides a robust foundation for Wikipedia interaction, with comprehensive test coverage ensuring reliable operation across all page types. The focus on climate change terminology aligns with the project's domain expertise, while the modular design allows for easy extension and maintenance.

---

*This document was generated based on the comprehensive analysis of the Wikimedia module's Wikipedia lookup operations and test coverage.*




















