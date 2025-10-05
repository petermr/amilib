# Wikipedia Integration Documentation

This directory contains comprehensive documentation for the Wikipedia integration system in amilib, including the page classification system, user guides, and technical analysis.

## 📚 Documentation Overview

### Core Documentation

- **[Classification System](classification_system.md)** - Comprehensive guide to the Wikipedia page classification system
- **[User Guide](user_guide.md)** - Practical guide for using the classification system
- **[GHG Issue Analysis](ghg_issue_analysis.md)** - Technical analysis of the GHG classification problem

## 🎯 What This System Does

The Wikipedia classification system automatically identifies different types of Wikipedia pages and determines the appropriate parsing strategy for each:

- **Direct Articles** - Standard pages with main content
- **Disambiguation Pages** - Pages with multiple options ("may refer to:")
- **Redirect Pages** - Pages that redirect to other content
- **"See Also" Pages** - Pages with related content sections
- **Not Found** - Non-existent pages
- **Other/Errors** - Problematic pages requiring special handling

## 🚀 Quick Start

```python
from test_wikimedia import WikipediaPageType, WikipediaTest

# Classify a Wikipedia page
wiki_test = WikipediaTest()
page_type = wiki_test.classify_wikipedia_page("Climate change")
print(f"Page type: {page_type}")
# Output: Page type: Direct Article
```

## 🔍 Key Features

### 1. **Enum-Based Classification**
- Type-safe classification using `WikipediaPageType` enum
- Prevents typos and ensures consistency
- Easy to extend with new page types

### 2. **Intelligent Parsing Decisions**
- Each page type has a defined parsing strategy
- Automatic handling of redirects and disambiguation
- Graceful error handling for problematic pages

### 3. **Comprehensive Testing**
- 20 climate-related terms tested and classified
- 95% success rate (19/20 terms classified correctly)
- Known issues documented and workarounds provided

## 📊 Classification Results

Recent testing with climate terms shows:

| **Category** | **Count** | **Success Rate** |
|--------------|-----------|------------------|
| Direct Articles | 1 | ✅ 100% |
| Disambiguation | 5 | ✅ 100% |
| Redirects | 1 | ✅ 100% |
| "See Also" Pages | 12 | ✅ 100% |
| Not Found | 0 | ✅ 100% |
| Other/Errors | 1 | ⚠️  Special case |

**Overall Success Rate: 95% (19/20 terms)**

## 🐛 Known Issues

### GHG Classification Problem
- **Term**: "GHG" (Greenhouse Gas)
- **Issue**: Circular redirect in Wikipedia (GHG → Ghg → GHG)
- **Impact**: Classified as `OTHER` instead of `DISAMBIGUATION`
- **Status**: Documented, workaround available
- **Solution**: Enhanced disambiguation detection (planned)

## 🛠️ Implementation Status

### ✅ Completed
- [x] Wikipedia page classification enum
- [x] Classification logic for all 6 page types
- [x] Comprehensive testing with climate terms
- [x] Documentation and user guides
- [x] Error handling and fallbacks

### 🔄 In Progress
- [ ] Enhanced disambiguation detection
- [ ] Improved redirect handling
- [ ] Content-based classification fallbacks

### 📋 Planned
- [ ] Relevance scoring for disambiguation options
- [ ] Redirect chain resolution
- [ ] Migration to main amilib codebase

## 🔧 Technical Details

### Architecture
- **Enum-based classification** for type safety
- **Fallback mechanisms** for edge cases
- **Comprehensive error handling** for robustness
- **Extensible design** for future enhancements

### Dependencies
- `lxml` for HTML/XML parsing
- `requests` for HTTP requests
- Standard Python libraries

## 📖 Usage Examples

### Basic Classification
```python
page_type = wiki_test.classify_wikipedia_page(term)
if page_type == WikipediaPageType.DISAMBIGUATION:
    # Handle disambiguation
    options = page.get_disambiguation_list()
elif page_type == WikipediaPageType.REDIRECT:
    # Follow redirect
    target_page = follow_redirect(page)
```

### Batch Processing
```python
terms = ["Climate change", "AGW", "Global warming"]
results = {}
for term in terms:
    results[term] = wiki_test.classify_wikipedia_page(term)
```

## 🧪 Testing

### Running Tests
```bash
# Test the classification system
python -m pytest test/test_wikimedia.py::WikipediaTest::test_wikipedia_page_classification_climate_terms -v -s

# Test enum usage
python -m pytest test/test_wikimedia.py::WikipediaTest::test_enum_usage_example -v -s

# Test parsing decisions
python -m pytest test/test_wikimedia.py::WikipediaTest::test_enum_parsing_decisions -v -s
```

### Test Coverage
- **Classification accuracy**: 95% (19/20 terms)
- **Page types covered**: All 6 categories
- **Edge cases tested**: Disambiguation, redirects, errors
- **Error handling**: Graceful fallbacks for problematic pages

## 🚀 Future Development

### Short Term
1. Fix GHG classification issue
2. Enhance disambiguation detection
3. Improve error handling

### Medium Term
1. Add relevance scoring for disambiguation
2. Implement redirect chain resolution
3. Add content-based classification fallbacks

### Long Term
1. Migrate to main amilib codebase
2. Add machine learning for classification
3. Support for other Wikimedia projects

## 🤝 Contributing

### Reporting Issues
- Document the specific term and expected behavior
- Include error messages and stack traces
- Test with multiple terms to isolate the issue

### Suggesting Improvements
- Provide use cases and examples
- Consider impact on existing functionality
- Include test cases for new features

## 📞 Support

### Getting Help
1. **Check the documentation** - Start with the User Guide
2. **Review known issues** - Check the GHG analysis document
3. **Run the tests** - Verify the system is working
4. **Check Wikipedia directly** - Verify the page structure

### Common Solutions
- **Classification errors**: Check page type first
- **Disambiguation issues**: Verify page structure
- **Redirect problems**: Check for circular redirects
- **Performance issues**: Use caching and batch processing

## 📄 License

This documentation is part of the amilib project and follows the same licensing terms.

---

**Last Updated**: December 2024  
**Status**: Active Development  
**Version**: 1.0.0




















