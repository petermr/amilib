# Wikipedia Classification System - User Guide

## Quick Start

The Wikipedia classification system helps you understand what type of Wikipedia page you're dealing with and how to parse it effectively.

## Basic Usage

### 1. Classify a Wikipedia Page

```python
from test_wikimedia import WikipediaPageType, WikipediaTest

# Create a test instance to access the classification method
wiki_test = WikipediaTest()

# Classify a term
term = "Climate change"
page_type = wiki_test.classify_wikipedia_page(term)
print(f"{term} is a {page_type}")
# Output: Climate change is a Direct Article
```

### 2. Handle Different Page Types

```python
page_type = wiki_test.classify_wikipedia_page(term)

if page_type == WikipediaPageType.DIRECT_ARTICLE:
    print("✅ Can parse content directly")
elif page_type == WikipediaPageType.DISAMBIGUATION:
    print("🔀 Need to handle multiple options")
elif page_type == WikipediaPageType.REDIRECT:
    print("🔄 Need to follow redirect")
elif page_type == WikipediaPageType.SEE_ALSO_PAGE:
    print("📚 Has related content in 'See also' section")
elif page_type == WikipediaPageType.NOT_FOUND:
    print("❌ Page doesn't exist")
else:
    print("⚠️  Error or unknown type")
```

## Page Type Examples

### Direct Articles
- **What they are**: Standard Wikipedia pages with main content
- **Examples**: "Climate change", "Carbon dioxide"
- **How to handle**: Parse content directly

### Disambiguation Pages
- **What they are**: Pages with multiple options ("may refer to:")
- **Examples**: "AGW", "GHG", "Emissions"
- **How to handle**: Get the list of options and select the most relevant

### Redirect Pages
- **What they are**: Pages that redirect to other pages
- **Examples**: "Global warming" → redirects to climate change article
- **How to handle**: Follow the redirect and parse the target page

### Pages with "See Also" Sections
- **What they are**: Pages that have related content sections
- **Examples**: "IPCC", "Greenhouse effect", "CO2"
- **How to handle**: Parse main content + analyze "see also" for related concepts

## Common Use Cases

### 1. Content Extraction

```python
def extract_content(term):
    page_type = wiki_test.classify_wikipedia_page(term)
    
    if page_type == WikipediaPageType.DIRECT_ARTICLE:
        # Extract main content directly
        return extract_main_content(term)
    elif page_type == WikipediaPageType.DISAMBIGUATION:
        # Handle disambiguation
        return handle_disambiguation(term)
    elif page_type == WikipediaPageType.REDIRECT:
        # Follow redirect
        return follow_redirect(term)
    else:
        return None
```

### 2. Related Content Discovery

```python
def find_related_content(term):
    page_type = wiki_test.classify_wikipedia_page(term)
    
    if page_type == WikipediaPageType.SEE_ALSO_PAGE:
        # Extract "see also" links
        return extract_see_also_links(term)
    elif page_type == WikipediaPageType.DISAMBIGUATION:
        # Get disambiguation options
        return get_disambiguation_options(term)
    else:
        return []
```

### 3. Error Handling

```python
def safe_parse(term):
    try:
        page_type = wiki_test.classify_wikipedia_page(term)
        
        if page_type == WikipediaPageType.OTHER:
            print(f"⚠️  Error processing {term}")
            return None
        elif page_type == WikipediaPageType.NOT_FOUND:
            print(f"❌ {term} not found")
            return None
        else:
            return parse_by_type(term, page_type)
            
    except Exception as e:
        print(f"❌ Unexpected error with {term}: {e}")
        return None
```

## Troubleshooting

### Common Issues

1. **GHG Classification Error**
   - **Problem**: "GHG" returns `OTHER` classification
   - **Cause**: Wikipedia has circular redirects (GHG → Ghg → GHG)
   - **Solution**: Handle as special case or use alternative terms

2. **Disambiguation Without Options**
   - **Problem**: Some disambiguation pages don't return options
   - **Cause**: Page structure variations
   - **Solution**: Fall back to content analysis

3. **Redirect Detection Failures**
   - **Problem**: Some redirects aren't detected
   - **Cause**: Subtle redirect mechanisms
   - **Solution**: Enhanced content analysis

### Best Practices

1. **Always check the page type** before attempting to parse
2. **Handle errors gracefully** - not all pages will classify perfectly
3. **Use fallback strategies** for problematic classifications
4. **Log classification results** for debugging and improvement

## Advanced Usage

### Custom Classification Logic

```python
def custom_classifier(term, keywords):
    """
    Custom classifier that considers specific keywords.
    """
    page_type = wiki_test.classify_wikipedia_page(term)
    
    if page_type == WikipediaPageType.DISAMBIGUATION:
        # Custom disambiguation handling
        return handle_custom_disambiguation(term, keywords)
    else:
        return page_type
```

### Batch Processing

```python
def classify_multiple_terms(terms):
    """
    Classify multiple terms and group by type.
    """
    results = {
        WikipediaPageType.DIRECT_ARTICLE: [],
        WikipediaPageType.DISAMBIGUATION: [],
        WikipediaPageType.REDIRECT: [],
        WikipediaPageType.SEE_ALSO_PAGE: [],
        WikipediaPageType.NOT_FOUND: [],
        WikipediaPageType.OTHER: []
    }
    
    for term in terms:
        page_type = wiki_test.classify_wikipedia_page(term)
        results[page_type].append(term)
    
    return results
```

## Performance Tips

1. **Cache classifications** for frequently accessed terms
2. **Batch requests** when processing multiple terms
3. **Handle errors asynchronously** for large datasets
4. **Use timeouts** for network requests

## Getting Help

- **Check the classification**: Always verify the page type first
- **Review the logs**: Look for error messages and warnings
- **Test with known terms**: Use "Climate change" as a reliable test case
- **Check Wikipedia directly**: Verify the page exists and structure

## Future Features

The classification system is actively being improved. Planned enhancements include:
- Better relevance scoring for disambiguation options
- Enhanced redirect detection
- Improved error recovery
- Content-based classification improvements















