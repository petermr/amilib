# Workflow Diagram Development Session Summary
**Date: Monday, November 17, 2025**

## Overview
Created and refined a workflow diagram (pipeline_workflow_v3) for the scientific document processing pipeline presentation.

## Pipeline Workflow
The diagram illustrates the complete workflow from EPMC query to knowledge graph creation:

1. **pygetpapers** - Query EPMC API and download corpus (JSON, PDF, XML)
2. **ami_html** - Convert XML to HTML (within Corpus)
3. **datatables_module** - Filter & refine corpus using JQuery Datatables (within Corpus)
4. **txt2phrases OR docanalysis** - Unsupervised search with TF-IDF phrase extraction (within Encyclopedia)
5. **ami_encyclopedia** - Create encyclopedia with Wikipedia & authorities (within Encyclopedia)
6. **html_marker** - Supervised search with encyclopedia annotation (within Corpus)
7. **ami_graph** - Create knowledge graph (GraphML format) (within Encyclopedia)

## Key Design Decisions

### Structure
- **Corpus Container**: Contains file types (JSON/PDF/XML combined, HTML), Datatables, Annotated HTML, and programs (ami_html, datatables_module, html_marker)
- **Encyclopedia Container**: Contains Weighted Phrases, Entries, Knowledge Graph, and programs (txt2phrases/docanalysis, ami_encyclopedia, ami_graph)
- **Files Container**: Nested within Corpus, contains JSON/PDF/XML (combined), ami_html, and HTML, stacked vertically

### Visual Styling
- All programs use consistent rounded rectangle style with uniform color (#ffe9c6)
- Content/data nodes use ellipses (light blue for external, white for internal)
- Containers use distinct background colors for visual separation
- Programs labeled with simple names (removed "amilib." prefixes)

### Workflow Features
- Step 3 (HTML conversion) loops back to add HTML files to the corpus
- Step 3 (Datatables) branches to unsupervised search (step 4)
- Step 4 feeds into step 5 (encyclopedia creation)
- Step 6 uses the encyclopedia to create annotated HTML in the corpus
- Step 7 creates the knowledge graph from both annotated corpus and encyclopedia entries
- Feedback loop: Entries → pygetpapers (labeled "supervised search")

## Files Created
- `pipeline_workflow_v3.dot` - Final Graphviz source file
- `pipeline_workflow_v3.svg` - Rendered diagram for presentations
- `pipeline_workflow_v2.dot` - Intermediate version
- `pipeline_workflow_v2.svg` - Intermediate version
- `pipeline_workflow.dot` - Initial version
- `pipeline_workflow.svg` - Initial version
- `README.md` - Documentation

## Codebases Represented
- **pygetpapers** - EPMC query and download
- **amilib** - Core processing (ami_html, datatables_module, ami_encyclopedia, html_marker, ami_graph)
- **txt2phrases** - Unsupervised phrase extraction
- **docanalysis** - spaCy and keybert wrapper (shown as alternative to txt2phrases)

## Refinements Made
1. Merged steps 1 and 2 (pygetpapers UI and download)
2. Unified program styling (all programs same color/style)
3. Organized programs into Corpus and Encyclopedia containers
4. Created files container with combined JSON/PDF/XML node
5. Simplified labels (removed " files", "amilib." prefixes, descriptive text)
6. Combined txt2phrases and docanalysis into single "OR" box
7. Positioned ami_html between XML and HTML files
8. Added supervised search feedback loop from Entries to pygetpapers
9. Removed Encyclopedia B (ghost reference) after refinement
10. Used double-headed arrows for txt2phrases/docanalysis connections

## Usage
To regenerate the SVG:
```bash
dot -Tsvg workflow/pipeline_workflow_v3.dot -o workflow/pipeline_workflow_v3.svg
```

## Presentation Context
This diagram is designed for presentations about the scientific document processing pipeline, showing how different tools work together to process research papers from query to knowledge graph. The workflow demonstrates both unsupervised and supervised approaches to building domain-specific encyclopedias.

