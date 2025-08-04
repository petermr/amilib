# Corpus Management Scripts

Scripts for creating, managing, and analyzing document corpora using the AmiCorpus framework.

## Scripts

### **`ingest_breward2023.py`** ⭐⭐⭐⭐⭐
**Purpose**: Ingest PDF files into AmiCorpus structure

**Current Status**: 
- ✅ Functional but needs parameterization
- ❌ Hardcoded paths and business logic in main()
- ❌ Violates style guide

**Planned Improvements**:
- Add command-line arguments for source/target directories
- Support for different file types (PDF, TXT, HTML)
- Better error handling and validation
- Move business logic to parameterized methods

**Usage** (planned):
```bash
python ingest_files.py --source /path/to/source --target /path/to/corpus --file-type pdf
```

### **`extract_phrases_keybert_breward2023.py`** ⭐⭐⭐⭐
**Purpose**: Extract significant phrases using KeyBERT analysis

**Current Status**:
- ✅ Functional with advanced NLP capabilities
- ❌ Hardcoded magic numbers and paths
- ❌ Business logic in main()
- ❌ Violates style guide

**Planned Improvements**:
- Parameterize all hardcoded values
- Add configuration file support
- Better output formatting and options
- Merge with TF-IDF version into unified tool

**Usage** (planned):
```bash
python extract_phrases.py --method keybert --corpus /path/to/corpus --output /path/to/output --max-phrases 200
```

### **`extract_phrases_breward2023.py`** ⭐⭐⭐⭐
**Purpose**: Extract significant phrases using TF-IDF analysis

**Current Status**:
- ✅ Functional with standard NLP analysis
- ❌ Hardcoded magic numbers and paths
- ❌ Business logic in main()
- ❌ Violates style guide

**Planned Improvements**:
- Same as KeyBERT version
- Consider merging with KeyBERT version into single tool with method selection

## Planned Unified Tool

The phrase extraction scripts will be merged into a single `extract_phrases.py` tool with:

- Method selection (TF-IDF, KeyBERT, or both)
- Configuration file support
- Parameterized inputs and outputs
- Better error handling and progress reporting
- Multiple output formats (JSON, CSV, TXT)

## Dependencies

- amilib (AmiCorpus framework)
- keybert (for KeyBERT analysis)
- scikit-learn (for TF-IDF analysis)
- pandas (for data manipulation) 