# Scripts Directory

This directory contains organized scripts for the amilib project, categorized by functionality.

## Directory Structure

### 📚 **corpus/** - Corpus Management
Scripts for creating, managing, and analyzing document corpora.

- **`ingest_breward2023.py`** - Ingest PDF files into AmiCorpus structure
- **`extract_phrases_keybert_breward2023.py`** - Extract phrases using KeyBERT analysis
- **`extract_phrases_breward2023.py`** - Extract phrases using TF-IDF analysis

### 📄 **annotation/** - Document Annotation
Scripts for adding hyperlinks and annotations to PDFs and HTML documents.

- **`markup_climate_pdfs_with_glossary.py`** - Add IPCC glossary links to climate PDFs
- **`markup_ipcc_executive_summary.py`** - Add glossary links to IPCC HTML documents
- **`process_biorxiv_pdfs_simple.py`** - Simplified PDF annotation (alternative)
- **`process_remaining_biorxiv.py`** - Background processing of bioRxiv PDFs
- **`create_flat_glossary.py`** - Convert HTML glossary to flat text format

### 🛠️ **utils/** - System Utilities
Utility scripts for system maintenance and file operations.

- **`sanitize_filenames.py`** - Make filenames Windows-compatible
- **`clean_git_history.py`** - Clean git history of problematic filenames

## Usage

Each subdirectory contains its own README with specific usage instructions for the scripts in that category.

## Style Guide Compliance

All scripts should follow the established style guide:
- Use Python commands, not shell commands
- Avoid hardcoded strings and numbers
- Do not put business logic in main(); use parameterized methods
- Use absolute imports with module prefix
- Use clean Path construction with comma-separated arguments 