# Breward2023 Repository TDD Plan

**Date**: July 30, 2025 (system date of generation)

## TDD Approach

**Principle**: Write tests first, then implement functionality
**Cycle**: Red-Green-Refactor
**Scope**: Comprehensive test coverage for all components

## Test Structure

### Directory Structure
```
test/
├── corpus/
│   └── breward2023/           # PDF files (to be copied)
├── test_breward2023/
│   ├── __init__.py
│   ├── test_repository.py     # Repository operations
│   ├── test_extractor.py      # Term extraction
│   ├── test_api.py           # API interface
│   ├── test_tfidf.py         # TF-IDF calculations
│   └── test_visualization.py # Tree and graphviz
└── conftest.py               # Test configuration
```

## Test Categories

### 1. Repository Operations Tests
**File**: `test_repository.py`

#### Test Cases
1. **test_create_repository_structure**
   - Create directory structure
   - Verify all required directories exist
   - Check configuration files are created

2. **test_ingest_single_pdf**
   - Ingest one PDF file
   - Verify file is copied to repository
   - Check metadata is extracted and stored

3. **test_ingest_multiple_pdfs**
   - Ingest multiple PDF files
   - Verify all files are processed
   - Check metadata consistency

4. **test_remove_pdf**
   - Remove PDF from repository
   - Verify file is deleted
   - Check metadata is updated

5. **test_ingest_duplicate_pdf**
   - Attempt to ingest existing PDF
   - Verify appropriate error handling
   - Check no duplicate entries

### 2. Term Extraction Tests
**File**: `test_extractor.py`

#### Test Cases
1. **test_extract_text_from_pdf**
   - Extract text from single PDF
   - Verify text content is captured
   - Check text cleaning and normalization

2. **test_term_frequency_calculation**
   - Calculate term frequencies
   - Verify frequency counts are accurate
   - Check handling of case sensitivity

3. **test_tfidf_calculation**
   - Calculate TF-IDF scores
   - Verify mathematical accuracy
   - Check cross-document significance

4. **test_index_generation**
   - Generate JSON index
   - Verify index structure matches specification
   - Check all required fields are present

### 3. API Interface Tests
**File**: `test_api.py`

#### Test Cases
1. **test_api_ingest_operation**
   - Test ingest API call
   - Verify proper response format
   - Check error handling

2. **test_api_remove_operation**
   - Test remove API call
   - Verify file removal confirmation
   - Check error handling for missing files

3. **test_api_extract_operation**
   - Test extract API call
   - Verify extraction progress reporting
   - Check output validation

4. **test_api_transform_operation**
   - Test transform API call
   - Verify transformation pipeline execution
   - Check configuration loading

5. **test_api_index_operation**
   - Test index API call
   - Verify index generation
   - Check index file creation

6. **test_api_search_operation**
   - Test search API call
   - Verify search results
   - Check index-based search performance

### 4. TF-IDF Calculation Tests
**File**: `test_tfidf.py`

#### Test Cases
1. **test_tf_calculation**
   - Calculate term frequency
   - Verify mathematical accuracy
   - Test edge cases (empty documents, single terms)

2. **test_idf_calculation**
   - Calculate inverse document frequency
   - Verify cross-document significance
   - Test with varying document counts

3. **test_tfidf_combined**
   - Calculate combined TF-IDF scores
   - Verify score ranges and normalization
   - Test significance ranking

4. **test_tfidf_edge_cases**
   - Test with single document
   - Test with duplicate terms
   - Test with very large documents

### 5. Visualization Tests
**File**: `test_visualization.py`

#### Test Cases
1. **test_content_tree_generation**
   - Generate content tree
   - Verify tree structure
   - Check tree printing format

2. **test_graphviz_generation**
   - Generate graphviz diagram
   - Verify DOT file creation
   - Check diagram structure

## First Test Case (TDD Start)

### Test: `test_create_repository_structure`

**Purpose**: Verify repository directory structure creation

**Test Specification**:
```python
def test_create_repository_structure():
    """
    Test that repository creates proper directory structure
    """
    # Arrange
    repo_name = "breward2023"
    repo_path = Path("temp/breward2023")
    
    # Act
    repository = BrewardRepository(repo_name)
    repository.create_structure()
    
    # Assert
    assert repo_path.exists()
    assert (repo_path / "documents" / "pdf").exists()
    assert (repo_path / "documents" / "extracted").exists()
    assert (repo_path / "documents" / "processed").exists()
    assert (repo_path / "indices").exists()
    assert (repo_path / "config").exists()
    assert (repo_path / "api").exists()
    
    # Check configuration files
    assert (repo_path / "config" / "repository.yaml").exists()
    assert (repo_path / "config" / "extraction.yaml").exists()
    assert (repo_path / "config" / "processing.yaml").exists()
```

## Test Data Requirements

### Sample PDF Files
- **Location**: `test/corpus/breward2023/`
- **Quantity**: 8 PDF files (to be copied from user's filestore)
- **Characteristics**: Various sizes and content types for comprehensive testing

### Expected Outputs
- **Index Structure**: JSON files matching specified format
- **Metadata**: Document metadata in structured format
- **Visualizations**: Tree and graphviz output files

## Implementation Order

### Phase 1: Foundation (Red-Green-Refactor)
1. **test_create_repository_structure** → Repository class with structure creation
2. **test_ingest_single_pdf** → Basic PDF ingestion
3. **test_extract_text_from_pdf** → Text extraction from PDFs

### Phase 2: Core Functionality
4. **test_term_frequency_calculation** → Term frequency analysis
5. **test_tfidf_calculation** → TF-IDF implementation
6. **test_index_generation** → JSON index creation

### Phase 3: API and Integration
7. **test_api_ingest_operation** → API interface
8. **test_api_search_operation** → Search functionality
9. **test_visualization** → Tree and graphviz output

## Dependencies for Testing

### Test Framework
- **pytest**: Primary testing framework
- **pytest-mock**: Mocking capabilities
- **pytest-cov**: Coverage reporting

### Test Utilities
- **tempfile**: Temporary file management
- **pathlib**: Path operations
- **json**: JSON validation
- **yaml**: YAML configuration testing

## Notes

- **DNWC**: All implementation requires explicit user approval
- **Test-First**: Write failing test, implement minimal code, refactor
- **External Config**: Test configuration loading and validation
- **Error Handling**: Comprehensive error condition testing
- **Performance**: Include performance tests for large document sets 