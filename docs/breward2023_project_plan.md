# Breward2023 Repository Project Plan

**Date**: July 30, 2025 (system date of generation)

## Project Overview

**Current Project**: Create a repository system for breward2023 with PDF ingestion and term extraction capabilities.

## Project Requirements

### 1. Repository Creation
- **Repository Name**: `breward2023`
- **Purpose**: Store and manage 8 PDF files with extracted metadata

### 2. PDF Ingestion
- **Input**: 8 PDF files to be ingested into the repository
- **Processing**: Extract text and metadata from each PDF
- **Storage**: Organized storage with metadata tracking

### 3. Term Extraction & Indexing
- **Goal**: Extract significant words and phrases from each PDF
- **Output**: JSON index of terms with frequency and significance metrics
- **Scope**: Both individual document analysis and cross-document analysis

### 4. Repository Software/API
- **Requirements**: Software/API to support the above operations
- **Interface**: Programmatic access to repository contents
- **Query Capabilities**: Search and retrieval of documents and terms

## Development Approach

### Test-Driven Development (TDD)
- **Principle**: Write tests first, then implement functionality
- **Process**: Red-Green-Refactor cycle
- **Coverage**: Comprehensive test suite for all components

### DNWC Principle
- **Do Not Write Code** without explicit user approval
- **Design First**: Plan and discuss before implementation
- **User-Driven**: All major decisions require user approval

## Technical Foundation

### Existing Infrastructure
Based on our previous work, we have:

1. **PDF Processing**: `amilib/ami_pdf_libs.py` with PyMuPDF integration
2. **Corpus Management**: `corpus_module/` with `AmiCorpus` and `AmiCorpusContainer`
3. **HTML Processing**: `HtmlEditor` with declarative JSON configuration
4. **External Configuration**: YAML/JSON-based transformation definitions

### Design Principles
- **External Configuration**: Transformations and logic in external files
- **Non-Coder Accessibility**: Configuration files readable by business users
- **Modular Design**: Leverage existing code where possible
- **Output Location**: All output files to `temp/` directory

## Proposed Architecture

### 1. Repository Structure
```
breward2023/
├── documents/
│   ├── pdf/          # Original PDF files
│   ├── extracted/    # Extracted text and metadata
│   └── processed/    # Processed versions
├── indices/
│   ├── terms.json    # Term frequency and significance
│   ├── documents.json # Document metadata
│   └── cross_ref.json # Cross-document references
├── config/
│   ├── repository.yaml # Repository configuration
│   ├── extraction.yaml # Term extraction rules
│   └── processing.yaml # Document processing pipeline
└── api/
    └── repository.py # Repository API interface
```

### 2. Core Components

#### Repository Manager
- Document ingestion and storage (`ingest`, `remove`)
- Metadata management
- Version control for transformations
- File organization and tracking

#### Term Extractor
- Text extraction from PDFs (`extract`)
- Term frequency analysis
- TF-IDF calculation
- Cross-document correlation
- Index generation (`index`)

#### Repository API
- CRUD operations (`ingest`, `remove`, `extract`, `transform`, `index`)
- Search capabilities (`search`)
- Metadata retrieval
- Export functionality
- Visualization (tree and graphviz)

### 3. Configuration-Driven Design
Following our established pattern:
- **Repository Config**: Define source files, processing rules
- **Extraction Config**: Define term extraction criteria and significance metrics
- **Processing Config**: Define document transformation pipeline

## Test Strategy

### Unit Tests
- **Repository Operations**: Document ingestion, storage, retrieval
- **Term Extraction**: Text processing, frequency analysis, significance scoring
- **API Interface**: Query methods, error handling, validation

### Integration Tests
- **End-to-End Workflow**: Complete PDF ingestion to term extraction
- **Cross-Document Analysis**: Term correlation across multiple documents
- **API Integration**: Full API usage scenarios

### Test Data
- **Sample PDFs**: Representative documents for testing
- **Expected Outputs**: Known results for validation
- **Edge Cases**: Error conditions and boundary cases

## Implementation Phases

### Phase 1: Foundation
1. **Repository Structure**: Create directory structure and basic configuration
2. **Basic API**: Simple document storage and retrieval
3. **PDF Ingestion**: Basic PDF text extraction

### Phase 2: Term Extraction
1. **Text Processing**: Advanced text extraction and cleaning
2. **Term Analysis**: Frequency counting and significance scoring
3. **Index Generation**: JSON index creation and storage

### Phase 3: Advanced Features
1. **Cross-Document Analysis**: Term correlation across documents
2. **Advanced Queries**: Complex search and retrieval capabilities
3. **Export Features**: Data export in various formats

## Project Specifications

### PDF Source
- **Location**: `test/corpus/breward2023/` (to be created)
- **Source**: User's filestore (8 PDF files to be copied)
- **Processing**: Extract text and metadata from each PDF

### Term Significance
- **Method**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Process**: Automated calculation + manual editing
- **Output**: Significance scores for terms across documents

### Index Structure
```json
{
  "term": {
    "frequency": 10,
    "documents": ["doc1.pdf", "doc2.pdf"],
    "significance": 0.8,
    "tfidf_score": 0.65
  }
}
```

### Repository API Operations
**CRUD-like operations** (Create, Read, Delete - Update replaced by Delete/Create):

1. **ingest file/s** - Add PDF files to repository
2. **remove file/s** - Delete files from repository  
3. **extract file/s** - Extract text/metadata from files
4. **transform** - Apply transformations to documents
5. **index** - Generate term frequency and TF-IDF indices
6. **search** - Query documents and terms (with index support)

### Visualization
- **Content Tree**: Print hierarchical structure
- **Graphviz**: Generate visual diagrams of repository structure

## Next Steps

1. **Confirm Requirements**: Validate understanding of project scope
2. **Design Tests**: Create test specifications for each component
3. **Plan Implementation**: Break down into implementable units
4. **Begin TDD Cycle**: Start with first test case

## Dependencies

- **PyMuPDF**: PDF processing (already available)
- **lxml**: XML/HTML processing (already available)
- **JSON/YAML**: Configuration files (already available)
- **Existing amilib modules**: Leverage current infrastructure

## Notes

- **DNWC**: All implementation requires explicit user approval
- **TDD**: Tests must be written before implementation
- **External Config**: All logic should be configurable via external files
- **Documentation**: Comprehensive documentation for future reference 