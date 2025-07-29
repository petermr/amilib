# Amilib Refactoring Context

## Project Overview

**Date**: 2025-01-27  
**Goal**: Refactor amilib to be a set of standalone libraries for pygetpapers integration

## Architecture Context

### Amilib Purpose
- Set of (moderately) standalone libraries for transforming semi-structured documents
- Will be used by pygetpapers with minimal coupling
- Primary storage: text files (except for images)
- Communication: file-based (write/read files) rather than direct code linking

### Pygetpapers Integration Requirements
Pygetpapers is mostly self-contained but may need:
1. **PDF read and convert to HTML**
2. **HTML restructure** 
3. **Wikimedia** (Wikipedia, Wikidata, and Wiktionary lookup)

### Design Principles
- **Minimal coupling** between amilib and pygetpapers
- **File-based communication** where possible
- **Standalone libraries** that can work independently
- **Text file storage** as primary data format

## Current Analysis Needed

### Files to Analyze
Based on the integration requirements, we need to examine:
1. **PDF processing**: `ami_pdf_libs.py` (83KB, 2346 lines)
2. **HTML restructuring**: `ami_html.py` (234KB, 6627 lines) 
3. **Wikimedia**: `wikimedia.py` (122KB, 3033 lines)

### Questions to Address
1. How are these libraries currently structured?
2. What dependencies exist between them?
3. How can we make them more standalone?
4. What file interfaces would work for pygetpapers integration?

## Next Steps
- Analyze current structure of key libraries
- Identify coupling points
- Design file-based interfaces
- Plan refactoring approach

---
*This document will be updated as we progress through the refactoring.* 