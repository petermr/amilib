# Style Compliance Guide

## Overview

This document captures the style guide requirements that were established during the corpus development and how they were applied to ensure clean, maintainable code.

## Key Style Requirements

### 1. No Top-Level Files

**Requirement**: Do not create files in the top-level directory or external pipeline structures.

**❌ Wrong Approaches (What We Avoided)**:
```python
# Creating pipeline directories
mkdir -p pipeline/breward2023/00_input/pdfs
mkdir -p pipeline/breward2023/01_corpus/corpus

# Creating top-level scripts
edit_file("pipeline_runner.py")
edit_file("ingest_files.py")

# Using external pipeline structures
pipeline/
├── breward2023/
│   ├── 00_input/
│   ├── 01_corpus/
│   └── config/
```

**✅ Correct Approach**:
```python
# Use existing amilib structure
from corpus_module.corpus import AmiCorpus

# All functionality within amilib
corpus = AmiCorpus(topdir=Path("test", "resources", "corpus", "breward2023_corpus"))
```

### 2. No `cp` Commands

**Requirement**: Use AmiCorpus methods for all file operations, never use shell `cp` commands.

**❌ Wrong Approach**:
```bash
# Shell commands
cp test/resources/corpus/breward2025/*.pdf pipeline/breward2023/01_corpus/corpus/data/files/
```

**✅ Correct Approach**:
```python
# AmiCorpus methods
corpus.ingest_files(
    source_dir=Path("test", "resources", "corpus", "breward2025"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)
```

### 3. Proper Path Construction

**Requirement**: Use `Path("a") / "b" / "c"` instead of `Path("a/b/c")`.

**❌ Wrong Approach**:
```python
# Using / in Path construction
corpus_dir = Path("test/resources/corpus/breward2023_corpus")
source_dir = Path("test/resources/corpus/breward2025")
```

**✅ Correct Approach**:
```python
# Comma-separated Path construction
corpus_dir = Path("test", "resources", "corpus", "breward2023_corpus")
source_dir = Path("test", "resources", "corpus", "breward2025")
```

### 4. General Methods

**Requirement**: Methods should be general-purpose, not tied to specific file types.

**❌ Wrong Approach**:
```python
def ingest_pdf_files(self, source_dir):
    # Hardcoded for PDFs only
    pass
```

**✅ Correct Approach**:
```python
def ingest_files(self, source_dir, file_pattern="*", file_type="unknown"):
    # General purpose - works with any file type
    pass
```

### 5. User-Controlled Parameters

**Requirement**: Users should control file types and other parameters, not hardcoded values.

**❌ Wrong Approach**:
```python
# Hardcoded file type
corpus.ingest_files(source_dir=src)  # Assumes "unknown" type
```

**✅ Correct Approach**:
```python
# User specifies file type
corpus.ingest_files(
    source_dir=src,
    file_pattern="*.pdf",
    file_type="pdf"
)
```

## Style Violations and Corrections

### 1. Pipeline Directory Creation

**Violation**: Created `pipeline/` directory structure
```bash
mkdir -p pipeline/breward2023/{00_input/pdfs,01_corpus/corpus,02_extraction,03_indexing,04_annotation}
```

**Correction**: Removed entire pipeline structure
```bash
rm -rf pipeline/
```

**Rationale**: Pipeline directories violate "no top-level files" requirement.

### 2. Shell Commands for File Operations

**Violation**: Used `cp` commands
```bash
cp test/resources/corpus/breward2025/*.pdf pipeline/breward2023/01_corpus/corpus/data/files/
```

**Correction**: Used AmiCorpus methods
```python
corpus.ingest_files(
    source_dir=Path("test", "resources", "corpus", "breward2025"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)
```

**Rationale**: File operations should use AmiCorpus methods for consistency and error handling.

### 3. Top-Level Scripts

**Violation**: Created scripts in top-level directories
```python
edit_file("pipeline/shared/tools/pipeline_runner.py")
edit_file("pipeline/breward2023/ingest_files.py")
```

**Correction**: Moved to appropriate locations within amilib structure
```python
edit_file("scripts/ingest_breward2023.py")  # Within existing scripts directory
```

**Rationale**: Scripts should be within the existing project structure.

### 4. Hardcoded File Types

**Violation**: Methods assumed specific file types
```python
def ingest_pdfs(self, source_dir):
    # Only works with PDFs
    pass
```

**Correction**: General methods with user-controlled parameters
```python
def ingest_files(self, source_dir, file_pattern="*", file_type="unknown"):
    # Works with any file type
    pass
```

**Rationale**: General methods are more reusable and flexible.

## Style Compliance Checklist

### Before Implementation
- [ ] Will this create any top-level files or directories?
- [ ] Are there any shell commands (`cp`, `mv`, `mkdir`) that could be replaced with Python methods?
- [ ] Are all Path constructions using `Path("a") / "b" / "c"` format?
- [ ] Are methods general-purpose rather than specific to one file type?
- [ ] Do users control important parameters rather than having hardcoded values?

### During Implementation
- [ ] All file operations use AmiCorpus methods
- [ ] No external pipeline structures created
- [ ] Paths constructed properly without `/`
- [ ] Methods accept user parameters for customization
- [ ] Error handling follows amilib patterns

### After Implementation
- [ ] Code follows existing amilib patterns
- [ ] No top-level files or directories created
- [ ] All functionality contained within amilib structure
- [ ] Tests use temporary directories and clean up properly
- [ ] Documentation reflects style-compliant approach

## Benefits of Style Compliance

### 1. Maintainability
- Consistent code patterns across the project
- Easier to understand and modify
- Reduced coupling between components

### 2. Portability
- Cross-platform compatibility (proper Path handling)
- No external dependencies on specific directory structures
- Self-contained functionality

### 3. Reusability
- General methods work with different file types
- User-controlled parameters allow customization
- Consistent API across different use cases

### 4. Testability
- Isolated functionality easier to test
- Temporary directories prevent test interference
- Clear separation of concerns

## Style Guide Enforcement

### Code Review Process
1. Check for any top-level file creation
2. Verify no shell commands in Python code
3. Review Path construction patterns
4. Ensure methods are general-purpose
5. Confirm user control over parameters

### Automated Checks
- Linting tools can catch some style violations
- Unit tests verify style-compliant behavior
- Integration tests ensure no external dependencies

### Documentation
- Style requirements documented in this guide
- Examples of correct and incorrect approaches
- Rationale for each style requirement
- Checklist for implementation

## Conclusion

Following the style guide ensures:
- **Clean architecture**: No external dependencies or top-level files
- **Consistent patterns**: All code follows amilib conventions
- **Maintainable code**: Easy to understand and modify
- **Reusable components**: General methods work across different use cases

The style guide is not just about aesthetics—it's about creating robust, maintainable, and portable code that fits seamlessly into the existing amilib ecosystem. 