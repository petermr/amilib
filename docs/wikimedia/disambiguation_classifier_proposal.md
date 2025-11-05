# Disambiguation Classifier Proposal

## Overview

We need to classify disambiguation options by their relevance to a given subject (e.g., climate change). For example, given the "GHG" disambiguation options, we want to identify that "Greenhouse gas" is climate-related while "General Healthcare Group" is not.

## Requirements

- **Lightweight**: No additional libraries beyond what we already have
- **Fast**: Should work quickly for real-time classification
- **Accurate**: Should correctly identify climate-related terms
- **Extensible**: Easy to add new subject domains

## Available Libraries

- **numpy**: For vector operations and similarity calculations
- **pandas**: For data manipulation and scoring
- **networkx**: For graph-based analysis (optional enhancement)

## Proposed Solution: Keyword-Based Classification

### Phase 1: Simple Keyword Matching (Immediate Implementation)

#### 1.1 Climate Domain Dictionary

Create a comprehensive dictionary of climate-related terms organized by categories:

```python
CLIMATE_KEYWORDS = {
    'core_climate': [
        'climate', 'warming', 'greenhouse', 'emissions', 'carbon', 'temperature',
        'atmosphere', 'ocean', 'biodiversity', 'sustainability', 'renewable',
        'fossil', 'fuel', 'energy', 'efficiency', 'pollution', 'air'
    ],
    'climate_science': [
        'ipcc', 'scientist', 'research', 'study', 'data', 'model', 'prediction',
        'trend', 'analysis', 'measurement', 'observation', 'satellite'
    ],
    'climate_impacts': [
        'extreme', 'weather', 'drought', 'flood', 'storm', 'hurricane', 'typhoon',
        'sea level', 'glacier', 'ice', 'melting', 'adaptation', 'mitigation'
    ],
    'climate_policy': [
        'unfccc', 'paris', 'agreement', 'protocol', 'kyoto', 'target', 'goal',
        'policy', 'regulation', 'tax', 'subsidy', 'incentive'
    ]
}
```

#### 1.2 Scoring Algorithm

```python
def score_disambiguation_option(option_text, domain_keywords):
    """
    Score a disambiguation option based on keyword matches.
    
    Args:
        option_text (str): The text description of the option
        domain_keywords (dict): Dictionary of keyword categories
    
    Returns:
        dict: Scoring results with category scores and total
    """
    option_text_lower = option_text.lower()
    
    scores = {}
    total_score = 0
    
    for category, keywords in domain_keywords.items():
        category_score = 0
        for keyword in keywords:
            if keyword.lower() in option_text_lower:
                # Weight by keyword importance and frequency
                if keyword.lower() in ['climate', 'greenhouse', 'warming']:
                    category_score += 3  # High weight for core terms
                elif keyword.lower() in ['emissions', 'carbon', 'temperature']:
                    category_score += 2  # Medium weight for important terms
                else:
                    category_score += 1  # Standard weight for other terms
        
        scores[category] = category_score
        total_score += category_score
    
    return {
        'scores': scores,
        'total_score': total_score,
        'primary_category': max(scores.items(), key=lambda x: x[1])[0] if scores else None
    }
```

#### 1.3 Classification Function

```python
def classify_disambiguation_options(disambiguation_list, domain_keywords):
    """
    Classify disambiguation options by relevance to a domain.
    
    Args:
        disambiguation_list (list): List of disambiguation options
        domain_keywords (dict): Domain-specific keywords
    
    Returns:
        list: Sorted options with scores and classifications
    """
    classified_options = []
    
    for option in disambiguation_list:
        option_text = option.text_content()
        scores = score_disambiguation_option(option_text, domain_keywords)
        
        # Determine classification
        if scores['total_score'] >= 3:
            classification = 'highly_relevant'
        elif scores['total_score'] >= 1:
            classification = 'moderately_relevant'
        else:
            classification = 'not_relevant'
        
        classified_options.append({
            'option': option,
            'text': option_text,
            'scores': scores,
            'classification': classification,
            'relevance': scores['total_score']
        })
    
    # Sort by relevance score (descending)
    classified_options.sort(key=lambda x: x['relevance'], reverse=True)
    
    return classified_options
```

### Phase 2: Enhanced Text Analysis (Next Iteration)

#### 2.1 TF-IDF Similarity

Use numpy to implement simple TF-IDF similarity:

```python
def calculate_tfidf_similarity(option_text, reference_texts):
    """
    Calculate TF-IDF similarity between option text and reference texts.
    
    Args:
        option_text (str): Text to classify
        reference_texts (list): List of reference texts for the domain
    
    Returns:
        float: Similarity score (0-1)
    """
    # Simple word frequency analysis
    option_words = set(option_text.lower().split())
    
    # Calculate word overlap with reference texts
    total_overlap = 0
    for ref_text in reference_texts:
        ref_words = set(ref_text.lower().split())
        overlap = len(option_words.intersection(ref_words))
        total_overlap += overlap
    
    # Normalize by text length and number of references
    avg_overlap = total_overlap / len(reference_texts)
    max_possible = len(option_words)
    
    return avg_overlap / max_possible if max_possible > 0 else 0
```

#### 2.2 Context-Aware Scoring

```python
def enhanced_scoring(option_text, domain_keywords, reference_texts):
    """
    Enhanced scoring combining keyword matching and TF-IDF similarity.
    """
    # Get keyword-based score
    keyword_scores = score_disambiguation_option(option_text, domain_keywords)
    
    # Get TF-IDF similarity score
    similarity_score = calculate_tfidf_similarity(option_text, reference_texts)
    
    # Combine scores (70% keywords, 30% similarity)
    combined_score = (keyword_scores['total_score'] * 0.7) + (similarity_score * 10 * 0.3)
    
    return {
        'keyword_score': keyword_scores['total_score'],
        'similarity_score': similarity_score,
        'combined_score': combined_score,
        'classification': classify_by_score(combined_score)
    }
```

### Phase 3: Page Content Analysis (Future Enhancement)

#### 3.1 Retrieve and Analyze Linked Pages

```python
def analyze_linked_page_content(option, max_content_length=1000):
    """
    Retrieve the linked page and analyze its content for domain relevance.
    
    Args:
        option: Disambiguation option element
        max_content_length (int): Maximum content to analyze
    
    Returns:
        dict: Content analysis results
    """
    try:
        # Extract link from disambiguation option
        link = option.xpath('.//a[@href]')[0]
        href = link.get('href')
        
        if href.startswith('/wiki/'):
            # Internal Wikipedia link
            page_title = href.replace('/wiki/', '')
            page = WikipediaPage.lookup_wikipedia_page_for_term(page_title)
            
            if page and page.html_elem:
                # Extract first paragraph content
                first_para = page.create_first_wikipedia_para()
                if first_para and first_para.para_element:
                    content = first_para.para_element.text_content()[:max_content_length]
                    return {
                        'content': content,
                        'length': len(content),
                        'success': True
                    }
        
        return {'success': False, 'error': 'Could not retrieve content'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

## Implementation Plan

### Week 1: Basic Keyword Classification
- [ ] Implement `CLIMATE_KEYWORDS` dictionary
- [ ] Create `score_disambiguation_option()` function
- [ ] Implement `classify_disambiguation_options()` function
- [ ] Add tests for basic functionality

### Week 2: Enhanced Scoring
- [ ] Implement TF-IDF similarity calculation
- [ ] Create `enhanced_scoring()` function
- [ ] Add reference text corpus for climate domain
- [ ] Test with real disambiguation examples

### Week 3: Content Analysis
- [ ] Implement `analyze_linked_page_content()` function
- [ ] Add content-based scoring
- [ ] Create fallback mechanisms for failed retrievals
- [ ] Performance optimization

### Week 4: Integration and Testing
- [ ] Integrate with existing Wikipedia classification system
- [ ] Add configuration options for different domains
- [ ] Comprehensive testing with various disambiguation pages
- [ ] Documentation and user guide updates

## Example Usage

```python
# Basic classification
options = page.get_disambiguation_list()
classified = classify_disambiguation_options(options, CLIMATE_KEYWORDS)

for option in classified:
    print(f"Option: {option['text'][:50]}...")
    print(f"Classification: {option['classification']}")
    print(f"Relevance Score: {option['relevance']}")
    print(f"Primary Category: {option['scores']['primary_category']}")
    print("---")

# Enhanced classification with content analysis
enhanced_results = []
for option in classified[:3]:  # Top 3 options
    content_analysis = analyze_linked_page_content(option['option'])
    if content_analysis['success']:
        enhanced_score = enhanced_scoring(
            content_analysis['content'], 
            CLIMATE_KEYWORDS, 
            CLIMATE_REFERENCE_TEXTS
        )
        enhanced_results.append({
            'option': option,
            'content_analysis': content_analysis,
            'enhanced_score': enhanced_score
        })
```

## Benefits

1. **No New Dependencies**: Uses only existing libraries
2. **Fast Performance**: Keyword matching is O(n) where n is text length
3. **Accurate Classification**: Multi-factor scoring reduces false positives
4. **Extensible**: Easy to add new domains (healthcare, technology, etc.)
5. **Fallback Support**: Multiple scoring methods ensure robustness

## Limitations

1. **Keyword Dependency**: Requires manual curation of domain keywords
2. **Language Specific**: Currently English-only
3. **Context Blind**: Doesn't understand semantic relationships
4. **Performance**: Content analysis adds network latency

## Future Enhancements

1. **Machine Learning**: Train models on labeled disambiguation data
2. **Semantic Analysis**: Use word embeddings for better similarity
3. **Multi-language Support**: Extend to other languages
4. **Domain Adaptation**: Learn domain-specific patterns automatically

## Conclusion

This lightweight approach provides immediate value with keyword-based classification while setting the foundation for more sophisticated analysis. The phased implementation allows for iterative improvement and validation of each approach before moving to the next phase.







































