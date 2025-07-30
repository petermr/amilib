# Corpus Design Discussion and Decisions

## Overview

This document captures the design discussion and decisions made during the development of the Breward2023 corpus system. It serves as a record of our thought process and the rationale behind key architectural choices.

## Key Design Principles

### 1. Style Compliance
- **No top-level files**: All functionality must be contained within the amilib structure
- **No pipeline directories**: Avoid creating external pipeline structures
- **No `cp` commands**: Use AmiCorpus methods for all file operations
- **Proper Path construction**: Use `Path("a") / "b" / "c"` instead of `Path("a/b/c")`

### 2. Declarative Configuration
- **External configuration**: Use YAML/JSON/XML files for logic definition
- **Non-coder accessible**: Configuration should be understandable by non-programmers
- **Composition over inheritance**: Use existing classes via composition rather than subclassing

### 3. Test-Driven Development (TDD)
- **Red-Green-Refactor cycle**: Write failing tests first, then implement
- **Incremental development**: Build functionality step by step
- **Comprehensive testing**: Cover CRUD operations, edge cases, and workflows

## Design Decisions

### 1. Corpus Structure

**Decision**: Use BagIt-compliant structure with AmiCorpus
- **Rationale**: BagIt is a mature, well-documented standard for digital preservation
- **Structure**:
  ```
  breward2023_corpus/
  ├── bag-info.txt              # BagIt metadata
  ├── bagit.txt                # BagIt version info
  ├── manifest-md5.txt         # BagIt checksums
  ├── data/                    # BagIt-managed content
  │   ├── files/               # PDF files
  │   ├── metadata/            # Extracted metadata
  │   ├── indices/             # Term indices
  │   └── processed/           # Processed files
  ├── search_results/          # Non-BagIt: Search results
  ├── summaries/               # Non-BagIt: Summary info
  └── temp/                    # Non-BagIt: Temporary files
  ```

### 2. File Ingestion Approach

**Initial Problem**: How to ingest files from source directory to corpus?

**Wrong Approaches Tried**:
- Creating pipeline directories with numbered steps
- Using `cp` commands to copy files
- Creating top-level scripts and configuration files

**Correct Approach**: Extend AmiCorpus with `ingest_files()` method
```python
corpus.ingest_files(
    source_dir=Path("test", "resources", "corpus", "breward2025"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)
```

**Benefits**:
- Style compliant (no top-level files)
- General purpose (works with any file type)
- User controls file type via parameter
- Uses existing AmiCorpus infrastructure

### 3. Directory Creation Responsibility

**Problem**: Who should be responsible for creating corpus directories?

**Initial Approach**: Caller creates directory, then initializes AmiCorpus
```python
corpus_dir.mkdir(parents=True, exist_ok=True)
corpus = AmiCorpus(topdir=corpus_dir)
```

**Better Approach**: AmiCorpus handles its own directory creation
```python
corpus = AmiCorpus(topdir=corpus_dir, mkdir=True)
```

**Rationale**: Better encapsulation - AmiCorpus manages its own resources

### 4. Test Strategy

**Comprehensive Test Plan**:
1. Ingest files 1-5 using glob pattern
2. Build indices and test search
3. Ingest files 6-8 incrementally
4. Test duplicate handling (file 4)
5. Delete file 3 and verify
6. Re-add file 3 and test

**Test Implementation**:
- Uses temporary directories for isolation
- Tests both individual operations and full workflows
- Validates CRUD operations and edge cases
- Follows TDD principles

## Technical Implementation

### 1. AmiCorpus Extensions

**New Method**: `ingest_files()`
```python
def ingest_files(self, source_dir: Union[str, Path], file_pattern: str = "*", 
                target_container: str = "files", file_type: str = "unknown") -> List[Path]:
```

**Features**:
- General purpose (any file type)
- Configurable target container
- User-defined file type
- Automatic container creation
- Error handling and logging

### 2. Directory Management

**Enhanced Constructor**:
```python
def __init__(self, topdir: Optional[Union[str, Path]] = None, mkdir: bool = False, ...):
    # ...
    if self.topdir and not self.topdir.is_dir():
        if mkdir:
            self.topdir.mkdir(parents=True, exist_ok=True)
        else:
            raise ValueError(f"AmiCorpus() requires valid directory {self.topdir}")
```

### 3. File Organization

**Source Files**: `test/resources/corpus/breward2025/*.pdf`
- 8 PDF files from Breward2023 Climate Change Seminar
- Raw input files for processing

**Corpus Files**: `test/resources/corpus/breward2023_corpus/data/files/`
- Ingested files using AmiCorpus methods
- BagIt-compliant structure
- Ready for processing pipeline

## Lessons Learned

### 1. Style Guide Importance
- Following the style guide prevents architectural mistakes
- No top-level files keeps the system clean and maintainable
- Proper Path construction prevents cross-platform issues

### 2. Incremental Development
- TDD helps catch issues early
- Small, focused tests are easier to debug
- Incremental functionality building reduces complexity

### 3. General vs Specific Design
- General methods (like `ingest_files()`) are more reusable
- User-controlled parameters (like `file_type`) provide flexibility
- Avoiding hardcoded assumptions makes the system more robust

### 4. Responsibility Assignment
- Classes should manage their own resources (like directory creation)
- Clear separation of concerns improves maintainability
- Encapsulation reduces coupling between components

## Future Considerations

### 1. Pipeline Integration
- How to integrate with text extraction, indexing, and annotation steps
- Maintaining BagIt compliance throughout the pipeline
- Handling intermediate results and temporary files

### 2. Search Implementation
- File-based search vs database search
- Index management and updates
- Search result presentation

### 3. Configuration Management
- YAML-based configuration for different corpus types
- Declarative transformation definitions
- User-friendly configuration interfaces

## Conclusion

The corpus design successfully balances:
- **Style compliance** with functionality
- **General purpose** design with specific use cases
- **Testability** with practical implementation
- **Standards compliance** (BagIt) with flexibility

The resulting system is clean, maintainable, and ready for the next phase of development. 