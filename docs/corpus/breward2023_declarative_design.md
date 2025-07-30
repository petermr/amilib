# Breward2023 Declarative Design (Revised)

**Date**: July 30, 2025 (system date of generation)

## Design Philosophy

- **No Subclassing**: Pure composition approach
- **Declarative**: All logic in configuration files
- **BagIt Core**: Standards-compliant foundation
- **Simple Search**: Brute force and file-based inverted indices
- **No Hidden Logic**: All transformations explicit in config

## Revised Corpus Configuration (YAML)

```yaml
# config/corpus.yaml
corpus:
  name: "breward2023"
  version: "1.0"
  bagit_compliant: true

structure:
  data:
    files: "data/files"
    metadata: "data/metadata"
    indices: "data/indices"
  non_bagit:
    search_results: "search_results"
    summaries: "summaries"
    temp: "temp"

pipeline:
  - type: "ingest"
    files: "test/resources/corpus/breward2025/*.pdf"
    destination: "data/files"
    rules:
      - type: "copy"
      - type: "extract_metadata"
      - type: "validate_pdf"
  
  - type: "extract"
    source: "data/files"
    output: "data/indices"
    method: "tfidf"
    config:
      min_frequency: 2
      significance_threshold: 0.1
  
  - type: "transform"
    transformation: "html_cleanup"
    source: "data/metadata"
    output: "data/processed"
    rules_file: "config/transformations/html_cleanup.yaml"

search:
  index_type: "file_based"
  config:
    inverted_index: "data/indices/inverted_index.json"
    brute_force: true
    search_log: "search_results/search_history.txt"
    max_results: 100
```

## Search Implementation Strategy

### **1. Brute Force Search**
```python
def brute_force_search(self, query, files=None):
    """
    Simple brute force search through text files
    """
    results = []
    search_files = files or self._get_all_text_files()
    
    for file_path in search_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append({
                    'file': file_path,
                    'matches': self._find_matches(content, query)
                })
    
    return results
```

### **2. File-Based Inverted Index**
```python
def build_inverted_index(self):
    """
    Build simple inverted index as JSON file
    """
    inverted_index = {}
    
    for file_path in self._get_all_text_files():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            words = self._tokenize(content)
            
            for word in words:
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append(str(file_path))
    
    # Save as JSON
    index_path = self.path / "data" / "indices" / "inverted_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=2)
    
    return inverted_index

def search_inverted_index(self, query):
    """
    Search using file-based inverted index
    """
    index_path = self.path / "data" / "indices" / "inverted_index.json"
    
    if not index_path.exists():
        self.build_inverted_index()
    
    with open(index_path, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    
    query_words = self._tokenize(query)
    results = {}
    
    for word in query_words:
        if word in inverted_index:
            for file_path in inverted_index[word]:
                if file_path not in results:
                    results[file_path] = 0
                results[file_path] += 1
    
    return sorted(results.items(), key=lambda x: x[1], reverse=True)
```

### **3. Search Logging**
```python
def log_search(self, query, results, search_type="brute_force"):
    """
    Log search queries and results
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'search_type': search_type,
        'result_count': len(results),
        'results': results[:10]  # Log first 10 results
    }
    
    log_path = self.path / "search_results" / "search_history.txt"
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')
```

## File Structure (Revised)

```
breward2023_corpus/
├── bag-info.txt
├── bagit.txt
├── manifest-md5.txt
├── data/
│   ├── files/                    # Original PDF files
│   ├── metadata/                 # Extracted metadata
│   ├── indices/                  # Search indices
│   │   ├── inverted_index.json   # File-based inverted index
│   │   ├── tfidf_index.json      # TF-IDF scores
│   │   └── term_frequency.json   # Term frequency data
│   └── processed/                # Processed text files
├── config/
│   ├── corpus.yaml               # Main configuration
│   ├── transformations/
│   │   ├── html_cleanup.yaml     # HTML transformation rules
│   │   └── term_extraction.yaml  # Term extraction rules
│   └── search.yaml               # Search configuration
├── search_results/               # Non-BagIt: Search results
│   ├── search_history.txt        # Search query log
│   ├── query_results.json        # Recent query results
│   └── search_index.json         # Search performance metrics
├── summaries/                    # Non-BagIt: Summary information
│   ├── corpus_summary.html       # HTML summary
│   ├── term_frequency.csv        # Term frequency data
│   └── analysis_report.pdf       # Analysis report
└── temp/                         # Non-BagIt: Temporary files
    ├── processing_log.txt        # Processing logs
    └── debug_output/             # Debug information
```

## Search Configuration (YAML)

```yaml
# config/search.yaml
search:
  methods:
    - name: "brute_force"
      enabled: true
      config:
        case_sensitive: false
        max_results: 100
    
    - name: "inverted_index"
      enabled: true
      config:
        index_file: "data/indices/inverted_index.json"
        rebuild_on_change: true
        max_results: 50
    
    - name: "tfidf_search"
      enabled: true
      config:
        index_file: "data/indices/tfidf_index.json"
        min_score: 0.1
        max_results: 25

logging:
  search_history: "search_results/search_history.txt"
  log_level: "INFO"
  max_log_size: "10MB"

performance:
  cache_results: true
  cache_size: 100
  timeout_seconds: 30
```

## Implementation Benefits

✅ **Simple and Reliable**: No external dependencies
✅ **File-Based**: All data in human-readable formats
✅ **Fast Development**: No complex search engine setup
✅ **Easy Debugging**: Can inspect index files directly
✅ **Portable**: No database or service dependencies
✅ **Extensible**: Easy to add more search methods later

## Future Integration Path

When ready to integrate search engines:

1. **Elasticsearch**: Add as optional search method
2. **Solr**: Alternative search engine option
3. **SQLite**: Lightweight database option
4. **PostgreSQL**: Full database option

All can be added as additional search methods while keeping the simple file-based approach as fallback.

## Usage Examples

```python
# Initialize corpus
corpus = BrewardCorpus("test/resources/corpus/breward2025_corpus")

# Brute force search
results = corpus.search("climate change", method="brute_force")

# Inverted index search
results = corpus.search("renewable energy", method="inverted_index")

# TF-IDF search
results = corpus.search("carbon emissions", method="tfidf")

# Search with logging
results = corpus.search_with_log("sustainability", method="inverted_index")
```

This approach gives us a solid foundation with simple, reliable search that can be enhanced later with more sophisticated search engines. 