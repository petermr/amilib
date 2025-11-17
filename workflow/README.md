# Pipeline Workflow Diagram

## Overview

This directory contains the workflow diagram for the scientific document processing pipeline. The diagram illustrates the complete workflow from querying the EPMC API through to knowledge graph creation.

## Files

- `pipeline_workflow_v2.dot` - Graphviz source file for the workflow diagram
- `pipeline_workflow_v2.svg` - Rendered SVG diagram for presentations

## Pipeline Steps

1. **pygetpapers** - Query EPMC API and download corpus (XML, PDF, JSON)
2. **amilib.ami_html** - Convert XML to HTML
3. **amilib.datatables_module** - Filter & refine corpus using JQuery Datatables
4. **txt2phrases + docanalysis** - Unsupervised search with TF-IDF phrase extraction
5. **amilib.ami_encyclopedia** - Create encyclopedia with Wikipedia & authorities
6. **amilib.html_marker + docanalysis** - Supervised search with encyclopedia annotation
7. **amilib.ami_graph** - Create knowledge graph (GraphML format)

## Program Color Coding

The diagram uses distinct colors to identify different codebases:

- **Orange** - pygetpapers
- **Light Green** - amilib
- **Yellow** - txt2phrases
- **Light Blue** - docanalysis

## Data Containers

- **Corpus** - Contains XML, PDF, JSON, HTML files, Datatables, and Annotated HTML
- **Encyclopedia** - Contains Wikipedia-enhanced terms and Knowledge Graph

## Workflow Features

- Step 3 (HTML conversion) loops back to add HTML files to the corpus
- Step 3 (Datatables) branches to both unsupervised (step 4) and supervised (step 6) search
- Step 4 feeds into step 5 (encyclopedia creation)
- Step 6 uses the encyclopedia to create annotated HTML in the corpus
- Step 7 creates the knowledge graph from both annotated corpus and encyclopedia terms

## Usage

To regenerate the SVG from the DOT file:

```bash
dot -Tsvg pipeline_workflow_v2.dot -o pipeline_workflow_v2.svg
```

## Presentation Context

This diagram is designed for presentations about the scientific document processing pipeline, showing how different tools (pygetpapers, amilib, txt2phrases, docanalysis) work together to process research papers from query to knowledge graph.

