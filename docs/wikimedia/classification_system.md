# Wikipedia Page Classification System

## Overview

The Wikipedia page classification system identifies different types of Wikipedia pages to determine the appropriate parsing strategy. Different page types require different approaches to extract meaningful content.

## Page Types

### 1. Direct Article (`DIRECT_ARTICLE`)
**Description**: Standard Wikipedia article with main content directly accessible.

**Detection Method**: No special indicators found - standard article content.

**Parsing Strategy**: 
- Extract main content directly
- Parse first paragraph
- Extract links and references
- Process infoboxes and images

**Example**: "Climate change" - contains direct, comprehensive content about climate change.

### 2. Disambiguation Page (`DISAMBIGUATION`)
**Description**: Page with multiple options (e.g., "may refer to:").

**Detection Method**: `page.is_disambiguation_page()` returns True.

**Parsing Strategy**:
- Get disambiguation list
- Score options by relevance
- Select most relevant option
- May need to follow link to actual content

**Example**: "AGW" - offers 12 options including "Anthropogenic global warming".

### 3. Redirect Page (`REDIRECT`)
**Description**: Page that redirects to another page.

**Detection Method**: Redirect indicators in content or URL analysis.

**Parsing Strategy**:
- Follow redirect to target page
- Parse the target page content
- Handle redirect chains if necessary

**Example**: "Global warming" - redirects to the main climate change article.

### 4. Page with "See Also" Section (`SEE_ALSO_PAGE`)
**Description**: Page that has a "See also" section for related content.

**Detection Method**: Found 'See also' section in page content.

**Parsing Strategy**:
- Parse main content
- Analyze "see also" section for related concepts
- Extract relevant links and references
- May need to follow some "see also" links

**Example**: "Greenhouse effect", "IPCC", "CO2" - all have "See also" sections.

### 5. Not Found (`NOT_FOUND`)
**Description**: Page doesn't exist or can't be accessed.

**Detection Method**: `page.html_elem` is None or empty.

**Parsing Strategy**:
- Handle gracefully
- Return empty result
- Log the missing page for analysis

**Example**: Non-existent terms return this classification.

### 6. Other/Errors (`OTHER`)
**Description**: Errors or exceptions during processing.

**Detection Method**: Errors or exceptions during processing.

**Parsing Strategy**:
- Error handling
- Fallback to basic parsing
- Log errors for debugging

**Example**: "GHG" - currently has processing issues due to Wikipedia's internal redirect structure.

## Implementation

### Enum Definition

```python
from enum import Enum, auto

class WikipediaPageType(Enum):
    DIRECT_ARTICLE = auto()
    DISAMBIGUATION = auto()
    REDIRECT = auto()
    SEE_ALSO_PAGE = auto()
    NOT_FOUND = auto()
    OTHER = auto()
```

### Classification Method

```python
def classify_wikipedia_page(term):
    """
    Classify a Wikipedia page and return the appropriate enum value.
    """
    try:
        page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        
        if not page or not page.html_elem:
            return WikipediaPageType.NOT_FOUND
        
        if page.is_disambiguation_page():
            return WikipediaPageType.DISAMBIGUATION
        
        # ... additional classification logic ...
        
        return WikipediaPageType.DIRECT_ARTICLE
        
    except Exception as e:
        return WikipediaPageType.OTHER
```

### Parsing Strategy Selection

```python
def get_parsing_strategy(page_type):
    """
    Determine parsing strategy based on page type.
    """
    strategies = {
        WikipediaPageType.DIRECT_ARTICLE: "Parse main content directly",
        WikipediaPageType.DISAMBIGUATION: "Handle disambiguation, find most relevant option",
        WikipediaPageType.REDIRECT: "Follow redirect, parse target page",
        WikipediaPageType.SEE_ALSO_PAGE: "Parse main content + analyze 'see also' section",
        WikipediaPageType.NOT_FOUND: "Handle gracefully, return empty result",
        WikipediaPageType.OTHER: "Error handling, fallback to basic parsing"
    }
    return strategies.get(page_type, "Unknown strategy")
```

## Usage Examples

### Basic Classification

```python
page_type = classify_wikipedia_page("Climate change")
print(f"Page type: {page_type}")
# Output: Page type: Direct Article
```

### Conditional Parsing

```python
page_type = classify_wikipedia_page(term)

if page_type == WikipediaPageType.DISAMBIGUATION:
    # Handle disambiguation
    options = page.get_disambiguation_list()
    best_option = select_most_relevant_option(options)
elif page_type == WikipediaPageType.REDIRECT:
    # Follow redirect
    target_page = follow_redirect(page)
    parse_page(target_page)
elif page_type == WikipediaPageType.DIRECT_ARTICLE:
    # Parse directly
    content = extract_main_content(page)
```

## Known Issues

### GHG Classification Problem

The term "GHG" currently has classification issues due to Wikipedia's internal redirect structure:
- "GHG" points to "Ghg" 
- "Ghg" points back to "GHG"
- This creates a circular reference that breaks our parsing

**Workaround**: For now, "GHG" is classified as `OTHER` and requires special handling.

## Testing

The classification system is thoroughly tested with 20 climate-related terms:

- **Direct articles**: 1 term
- **Disambiguation pages**: 5 terms  
- **Redirect pages**: 1 term
- **"See also" pages**: 12 terms
- **Not found**: 0 terms
- **Other/Errors**: 1 term (GHG)

## Future Enhancements

1. **Relevance Scoring**: Implement scoring for disambiguation options to find the most relevant choice.
2. **Enhanced Redirect Detection**: Improve detection of subtle redirects and redirect chains.
3. **Error Recovery**: Better handling of problematic pages like GHG.
4. **Content Analysis**: Deeper analysis of page content to improve classification accuracy.

## Migration to amilib

When ready to move this system to the main amilib codebase:

1. Move the `WikipediaPageType` enum to `amilib/wikimedia.py`
2. Move classification methods to the `WikipediaPage` class
3. Update imports in test files
4. All existing logic will continue to work unchanged

The enum-based approach ensures type safety and makes the system easy to maintain and extend.




































