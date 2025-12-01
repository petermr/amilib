# Planning Session Transcript Summary - Code and Integration Points

**Date**: 2025-11-10  
**Participants**: Peter Murray-Rust, Renu Kumari, Udita Agarwal  
**Focus**: Code integration and workflow improvements for the scientific document processing pipeline

## Overview

This document summarizes the code and integration discussions from a planning session focused on improving the workflow from PyGet Papers query through to knowledge graph creation.

## Key Integration Points

### 1. PyGet Papers - HTML Extraction

**Current State**:
- `--make-html` flag exists but only creates metadata tables, not actual HTML conversion
- GitHub V2 version has HTML extraction functionality

**Requirements**:
- Extract HTML format of papers if available from EPMC
- Update library to include this functionality
- HTML conversion should be handled in Corpus, not PyGet Papers

**Integration Notes**:
- Existing `AmiCorpus` class can handle HTML conversion
- Need to check if HTML extraction from EPMC is available in current PyGet Papers

### 2. Corpus - HTML Conversion and Ingestion

**Decision**: HTML conversion belongs in Corpus (not PyGet Papers)

**Requirements**:
- Ingest PyGet Papers output (XML, PDF, JSON)
- Support manual ingest (add files directly to corpus)
- Convert PDF to HTML (not PDF to text) to enable sectioning
- AmiLib already has hierarchical section functionality

**Integration Notes**:
- `AmiCorpus` class exists with `ingest_files()` method
- `HtmlGenerator.read_pdf_convert_to_html()` exists for PDF to HTML conversion
- Need to ensure HTML conversion is integrated into corpus workflow

### 3. Section Extraction

**Requirements**:
- Need XPath to extract sections
- Sections are valuable (similar to PubMed Central approach)
- Should use similar sections as PubMed Central

**Integration Notes**:
- `HtmlGenerator.create_sections()` exists
- `HtmlGroup.make_hierarchical_sections_KEY()` exists
- Need to ensure section extraction is part of corpus processing

### 4. txt2phrases - Key Phrase Extraction

**Current Input Options**:
- Corpus directory (PyGet Papers output)
- Single PDF file
- Directory of PDFs
- Directory of HTMLs
- Single TXT file

**Enhancement Required**:
- Support glob patterns (e.g., `**/*.pdf`) for more powerful file selection
- Argument `-i` should accept globs

**Integration Notes**:
- `AmiCorpus.extract_significant_phrases()` exists (TF-IDF based)
- `AmiCorpus.extract_significant_phrases_keybert()` exists (KeyBERT based)
- Need to add glob pattern support to file selection

### 5. Doc Analysis - Supervised NER

**Current State**:
- Uses pre-built libraries (plants, chemicals) for Named Entity Recognition
- Only works with Python 3.10 (needs update for 3.11/3.12)
- Supervised approach with dictionaries

**Workflow**:
1. Use txt2phrases (unsupervised) to extract key phrases
2. Manually review and build dictionary from key phrases
3. Use doc analysis with dictionary for supervised search

**Integration Notes**:
- `AmiDictionary` class exists
- `AmiSearch.markup_html_file_with_words_or_dictionary()` exists
- Need to update Python version compatibility
- Repository maintainer access available for updates

### 6. CSV Output Enhancements

**Current Columns**: word, count

**Required Enhancements**:
1. **Document References**: List of documents containing each term
   - Format: CSV with columns: word, count, list_of_documents
   - Enables building HTML lists of documents containing specific terms

2. **Case-Insensitive Extraction**: Avoid duplicates (e.g., "Lantana" vs "lantana")

3. **Annotation Column**: Fourth column for manual annotation
   - Mark false positives
   - Add comments
   - Mark for ignore
   - Enables iterative refinement

**Integration Notes**:
- Phrase extraction methods in `AmiCorpus` need to track document sources
- CSV generation needs to include document lists
- Case-insensitive matching needs to be implemented

### 7. Encyclopedia

**Requirements**:
- Glob support to select files for encyclopedia creation
- Remove false positives from encyclopedia
- Sorting capability
- Disambiguation (noted as problem, deferred)

**Integration Notes**:
- `AmiEncyclopedia` class exists
- Need to add glob pattern support
- Need filtering/removal capabilities

### 8. Knowledge Graph

**Requirements**:
- Node tooltips with URL and definition
- Edge descriptions
- Currently uses similarity by description (requires Wikipedia entry)
- Parent/child relationships
- Consider using existing tools (e.g., OpenAI embeddings) for document similarity

**Integration Notes**:
- `AmiGraph` class exists
- `AmiKnowledgeGraph` class exists (for encyclopedia knowledge graphs)
- Need to enhance with tooltip support
- Should leverage existing similarity tools rather than reinventing

### 9. Streamlit Integration

**Action Required**: Merge three Streamlit apps:
- Preeti's app (supervised/doc analysis)
- Shake's app (knowledge graph)
- Udita's app (unsupervised/txt2phrases)

**Structure**:
- Different tabs: supervised, unsupervised, knowledge graph
- Follow the pipeline workflow
- Include diagrams in the app

**Integration Notes**:
- All three apps are on GitHub
- Repository: semantic limiter repository
- Need to combine into unified interface

### 10. Testing

**Requirement**: Automated test suite for full chain:
- PyGet Papers → Doc Analysis → txt2phrases → Corpus

**Rationale**: Catch bugs early when components change

**Integration Notes**:
- Create integration tests in `test/` directory
- Test the complete workflow regularly
- Ensure components work together

### 11. Data Tables

**Note**: Small amount of JavaScript (generally don't edit)

**Integration Notes**:
- `datatables_module` exists
- Should be included in pipeline
- Proven technology used for many years

## Workflow Summary

The complete workflow discussed:

1. **Query** → PyGet Papers (EPMC, 100+ articles)
2. **Corpus** → Ingest PyGet Papers output, convert PDF to HTML, extract sections
3. **Key Phrases** → txt2phrases (unsupervised) or Doc Analysis (supervised with dictionaries)
4. **Encyclopedia** → Create from key phrases, remove false positives
5. **Knowledge Graph** → Create from encyclopedia and corpus
6. **Streamlit App** → Unified interface for all operations

## Integration Priorities

### High Priority
1. HTML extraction in PyGet Papers/Corpus
2. CSV enhancements (document references, case-insensitive, annotation column)
3. Glob pattern support in txt2phrases

### Medium Priority
4. Doc Analysis Python 3.11/3.12 compatibility
5. Knowledge Graph tooltips and edge descriptions
6. Streamlit app merging

### Low Priority
7. Automated test suite for full chain

## Technical Decisions

1. **HTML Conversion Location**: Corpus (not PyGet Papers)
2. **PDF Processing**: Convert to HTML (not text) to enable sectioning
3. **File Selection**: Use glob patterns for flexibility
4. **Language Preference**: Python over JavaScript for maintainability
5. **Tool Reuse**: Use existing tools/libraries rather than reinventing

## Notes

- All mentioned components already exist in the codebase
- Focus should be on enhancements and integration rather than new implementations
- Diagrams should be created for all workflows
- Streamlit app should follow the pipeline workflow
- Regular testing of the complete chain is essential

## Next Steps

1. Review existing code for each component
2. Identify specific integration points
3. Plan implementation for each enhancement
4. Create unified Streamlit interface
5. Develop comprehensive test suite

