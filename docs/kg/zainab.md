# Encyclopedia Knowledge Graph - Review and Integration Plan

**Author:** Shaik Zainab (2015)  
**Review Date:** November 8, 2025 (system date)  
**Status:** Awaiting Review

## Overview

This document reviews the original knowledge graph generator script (`amilib/resources/scripts/zainab.py`) by Shaik Zainab (2015) and proposes an integration plan to incorporate this functionality into the amilib codebase as a formal module.

## 1. Review of Original Script (`zainab.py`)

### Purpose

The script processes encyclopedia HTML files to:
1. Clean and sort entries
2. Generate PDF books
3. Build knowledge graphs from encyclopedia entries
4. Create interactive visualizations

### Functionality Breakdown

#### Step 1: HTML Cleaning & Sorting
- Reads encyclopedia HTML file (`wg2.html`)
- Removes citation references (`<sup>` tags with cite_ref)
- Deduplicates entries by description/image combination
- Sorts entries alphabetically by term
- Fixes protocol-relative image URLs (`//` → `https://`)
- Outputs cleaned HTML (`wg2_cleaned_sorted.html`)

#### Step 2: PDF Generation (Vivliostyle)
- Uses Vivliostyle CLI to preview HTML in browser
- Generates PDF book (`encyclopaedia_book.pdf`) from cleaned HTML
- Optional step with user confirmation

#### Step 3: Snippet Extraction
- Extracts text snippets (first 500 chars) and images from entries
- Stores in dictionary for use in tooltips
- Handles protocol-relative image URLs

#### Step 4: Knowledge Graph Construction
- Parses cleaned HTML to find entries (`div[role="ami_entry"]`)
- Extracts Wikipedia links from entry descriptions using regex pattern `/wiki/([^"#]+)`
- Creates NetworkX graph:
  - **Nodes**: Encyclopedia entry terms (lowercase)
  - **Edges**: Only between entries that are both in the graph
    - Links to Wikipedia pages that match other entry terms
    - Case-insensitive matching
- Removes isolated nodes (nodes with no connections)
- Exports to GraphML format (`output/data/graph/encyclopedia_kg.graphml`)

**Key Insight**: The original script creates edges only between entries that exist in the graph (entry-to-entry), not between entries and all Wikipedia links they mention.

#### Step 5: Interactive Visualization (Pyvis)
- Creates interactive HTML visualization using Pyvis
- Color-codes nodes by degree (connectivity):
  - **Green** (`#00ff99`): >25 connections (highly connected nodes)
  - **Blue** (`#66b2ff`): >10 connections (main topics)
  - **Orange** (`#ff9933`): >4 connections (subfields/categories)
  - **Red** (`#ff5555`): ≤4 connections (related concepts)
- Rich tooltips with images and descriptions
- Search functionality to find and focus on nodes
- Legend explaining node colors
- Opens visualization in browser

### Key Characteristics

1. **Entry-to-Entry Edges**: Creates edges only between entries that are both in the graph
2. **Degree-Based Coloring**: Visual importance based on connectivity
3. **Interactive Features**: Search, tooltips, and visual legend
4. **Deduplication**: Removes duplicate entries and isolated nodes

## 2. Integration Plan for amilib

### Proposed Structure

**New File:** `amilib/ami_encyclopedia_kg.py`

**Class:** `AmiKnowledgeGraph`

### Integration Approach

#### 2.1 Use Existing amilib Utilities

Instead of raw HTML parsing, use:
- `AmiEncyclopedia` as input (instead of raw HTML file)
- `EncyclopediaLinkExtractor` for link extraction (instead of BeautifulSoup regex)
- `HtmlLib` for HTML parsing (instead of BeautifulSoup)
- Follow amilib style guide (absolute imports, Path construction, etc.)

#### 2.2 Preserve Core Logic

Maintain the essential graph-building logic:
- Node creation from encyclopedia entries
- Link extraction from descriptions
- Edge creation (configurable: entry-to-entry vs entry-to-wiki)
- GraphML export
- Optional visualization capabilities

#### 2.3 Enhancements

1. **Input**: Accept `AmiEncyclopedia` instance instead of HTML file
2. **Edge Types**: Support both:
   - **Entry-to-Entry** (current behavior): Edges only between entries in the graph
   - **Entry-to-Wiki** (new requirement): Edges from entries to all Wikipedia links they mention
3. **Configurability**: Make edge creation type configurable
4. **Utilities**: Use amilib's `EncyclopediaLinkExtractor` for link extraction
5. **Style Compliance**: Follow amilib style guide conventions

### Proposed Class Structure

```python
class AmiKnowledgeGraph:
    """
    Knowledge graph builder for encyclopedias.
    
    Based on work by Shaik Zainab (2015).
    
    Creates knowledge graphs from encyclopedia entries by:
    - Extracting Wikipedia links from entry descriptions
    - Creating nodes for entries and optionally wiki pages
    - Creating edges based on configurable relationship types
    - Exporting to GraphML format for visualization
    """
    
    def __init__(self, encyclopedia: AmiEncyclopedia):
        """Initialize from AmiEncyclopedia instance"""
        
    def build_graph(self, edge_type="entry_to_entry"):
        """
        Build graph with configurable edge types.
        
        Args:
            edge_type: "entry_to_entry" or "entry_to_wiki"
        """
        
    def export_graphml(self, output_path: Path):
        """Export to GraphML format"""
        
    def visualize(self, output_path: Path):
        """Create interactive visualization (optional, requires pyvis)"""
```

### Features

1. **Input**: `AmiEncyclopedia` instance
2. **Edge Types**: 
   - `entry_to_entry`: Edges only between entries (original behavior)
   - `entry_to_wiki`: Edges from entries to all Wikipedia links (new requirement)
3. **Link Extraction**: Use `EncyclopediaLinkExtractor` utility
4. **GraphML Export**: Standard format for Cytoscape/NetworkX
5. **Optional Visualization**: Pyvis-based interactive HTML (if available)

## 3. Requirements

### Dependencies

- **NetworkX**: Already in requirements.txt (`networkx~=3.4.2`)
- **amilib utilities**: Use existing `EncyclopediaLinkExtractor`, `HtmlLib`, etc.
- **Optional**: Pyvis for visualization (can be added if needed)

### Integration Points

1. **Input**: `AmiEncyclopedia` class (already exists)
2. **Link Extraction**: `EncyclopediaLinkExtractor` (already exists)
3. **HTML Parsing**: `HtmlLib` (already exists)
4. **Graph Operations**: NetworkX (already in dependencies)

## 4. Author Attribution

**Original Work**: Shaik Zainab (2015)  
**Integration**: amilib team (2025)

The new `AmiKnowledgeGraph` class will:
- Preserve the core graph-building logic from the original script
- Attribute the original work to Shaik Zainab (2015)
- Document the evolution from script to module
- Maintain compatibility with the original approach while adding new features

## 5. Next Steps

1. **Review**: Awaiting review from Shaik Zainab
2. **Implementation**: After approval, create `amilib/ami_encyclopedia_kg.py`
3. **Testing**: Create tests for graph building and export
4. **Documentation**: Update module documentation

## 6. Questions for Review

1. Should we preserve the entry-to-entry edge behavior as default, or make entry-to-wiki the default?
2. Should visualization be a core feature or optional?
3. Should we support both edge types simultaneously (hybrid graph)?
4. Any specific requirements for node/edge attributes in GraphML?

---

**Status**: Awaiting review from Shaik Zainab before proceeding with implementation.
