# Corpus Documentation

## Overview

This directory contains comprehensive documentation for the Breward2023 corpus system, including design decisions, implementation guides, and style compliance requirements.

## Documentation Structure

### 📋 [Design Discussion](design_discussion.md)
Comprehensive record of our design discussion and decisions made during corpus development. Includes:
- Key design principles and rationale
- Technical implementation details
- Lessons learned and future considerations
- Architectural choices and their benefits

### 🛠️ [Implementation Guide](implementation_guide.md)
Practical guide for using the corpus system. Includes:
- Quick start examples
- API reference
- Best practices
- Troubleshooting guide
- Next steps for development

### 📏 [Style Compliance](style_compliance.md)
Detailed guide on style requirements and how to follow them. Includes:
- Key style requirements with examples
- Common violations and corrections
- Compliance checklist
- Benefits of style compliance

## Quick Reference

### Basic Usage
```python
from corpus_module.corpus import AmiCorpus
from pathlib import Path

# Create corpus
corpus = AmiCorpus(
    topdir=Path("test", "resources", "corpus", "breward2023_corpus"),
    mkdir=True
)

# Ingest files
files = corpus.ingest_files(
    source_dir=Path("test", "resources", "corpus", "breward2025"),
    file_pattern="*.pdf",
    target_container="files",
    file_type="pdf"
)
```

### Key Principles
1. **No top-level files**: All functionality within amilib structure
2. **No `cp` commands**: Use AmiCorpus methods for file operations
3. **Proper Path construction**: Use `Path("a") / "b" / "c"` format
4. **General methods**: Not tied to specific file types
5. **User-controlled parameters**: Users specify file types and patterns

### File Organization
- **Source**: `test/resources/corpus/breward2025/*.pdf` (8 PDF files)
- **Corpus**: `test/resources/corpus/breward2023_corpus/data/files/` (ingested files)
- **Scripts**: `scripts/ingest_breward2023.py` (ingestion script)
- **Tests**: `test/test_breward2023/test_corpus_ingestion.py` (test suite)

## Development Status

### ✅ Completed
- [x] AmiCorpus extension with `ingest_files()` method
- [x] BagIt-compliant corpus structure
- [x] Style-compliant implementation
- [x] Comprehensive test suite
- [x] Documentation and guides

### 🔄 In Progress
- [ ] Text extraction from PDFs
- [ ] Term indexing and search
- [ ] PDF annotation with hyperlinks

### 📋 Planned
- [ ] Configuration management (YAML)
- [ ] Advanced search functionality
- [ ] Pipeline integration
- [ ] Performance optimization

## Getting Started

1. **Read the Design Discussion** to understand the rationale behind our approach
2. **Follow the Implementation Guide** for practical usage examples
3. **Review Style Compliance** to ensure your code follows the established patterns
4. **Run the tests** to verify everything works correctly

## Contributing

When contributing to the corpus system:
1. Follow the style guide requirements
2. Use TDD approach (Red-Green-Refactor)
3. Keep methods general-purpose
4. Document design decisions
5. Test thoroughly with temporary directories

## Related Files

- **Implementation**: `corpus_module/corpus.py` (AmiCorpus with `ingest_files()`)
- **Script**: `scripts/ingest_breward2023.py` (Ingestion script)
- **Test**: `test/test_breward2023/test_corpus_ingestion.py` (Test suite)
- **Corpus**: `test/resources/corpus/breward2023_corpus/` (BagIt corpus)
- **Source**: `test/resources/corpus/breward2025/` (Raw PDF files) 