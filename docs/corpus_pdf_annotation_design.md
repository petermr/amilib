# Corpus PDF Annotation Design Reference

**Date**: July 30, 2025 (system date of generation)

## Design Documentation

**Primary Design Document**: `docs/Corpus_design.md` - Contains the detailed design with decimal numbering structure (1.1, 1.1.1, 1.1.6, etc.)

This document provides a comprehensive design covering:
- Current AmiCorpus analysis and existing structure
- Transformation schema design (1.1.1)
- Corpus structure enhancement (1.1.2)
- Graphviz diagram plans (1.1.3)
- Test planning (1.1.4)
- Integration strategy (1.1.5)
- External configuration strategy (1.1.6)
- Multi-source corpus configuration
- Repository adapter interfaces

## Current Status

**Last Completed Work**: HTML Wordlist PDF Annotation Implementation
- Integrated into `amilib/ami_pdf_libs.py`
- Comprehensive test suite in `test/test_pdf_hyperlink_adder.py`
- Supports both CSV and HTML wordlists

**Current Task**: Finding HTML editing files (HTMLEditor) containing declarative instructions like `remove_empty_elements`

## Key Design Principles

1. **External Configuration**: All transformations defined in YAML/JSON/XML files
2. **Multi-Source Input**: Remote repositories + manual collections
3. **Transformation Tracking**: Schema for foo.xml → foo.xml.html mappings
4. **Non-Coder Accessibility**: Configuration files readable by business users

## Next Steps

1. Locate and analyze HTMLEditor declarative files
2. Continue with repository adapter design
3. Implement transformation pipeline configuration

**Reference**: See `docs/Corpus_design.md` for the complete decimal-numbered design structure. 