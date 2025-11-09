# Encyclopedia Knowledge Graph - Zainab's Script Review

**Date:** November 8, 2025 (system date of generation)  
**Author:** Shaik Zainab (2015)  
**Reviewer:** AI Assistant

## Overview

This document reviews Shaik Zainab's network generator script (`amilib/resources/scripts/zainab.py`) and proposes how to integrate it into the amilib codebase as a new `AmiKnowledgeGraph` class.

## 1. Review of `zainab.py`

### What the Script Does

The script (`amilib/resources/scripts/zainab.py`) performs the following operations:

#### Step 1: Package Installation
- Auto-installs required packages: `beautifulsoup4`, `networkx`, `pyvis`, `requests`

#### Step 2: HTML Cleaning & Sorting
- Reads encyclopedia HTML file (`wg2.html`)
- Removes citation references (`<sup>` tags with `cite_ref` or `reference`)
- Deduplicates entries by description/image combination
- Sorts entries alphabetically by term
- Fixes protocol-relative image URLs (`//` → `https://`)
- Outputs cleaned HTML (`wg2_cleaned_sorted.html`)

#### Step 3: PDF Generation (Vivliostyle)
- Uses Vivliostyle CLI to preview cleaned HTML
- Optionally generates PDF (`encyclopaedia_book.pdf`)

#### Step 4.5: Snippet Extraction
- Extracts text snippets and images from entries
- Stores in dictionary for tooltip generation

#### Step 5: Knowledge Graph Construction
- Parses cleaned HTML to find entries (`div[role="ami_entry"]` or `div[term]`)
- Extracts Wikipedia links from entry descriptions using regex pattern `/wiki/([^"#]+)`
- Creates NetworkX graph:
  - **Nodes**: Encyclopedia entry terms (with description and image attributes)
  - **Edges**: Only between entries that are both in the graph (not all wiki links)
- Removes isolated nodes (nodes with no connections)
- Exports to GraphML format (`output/data/graph/encyclopedia_kg.graphml`)

**Key Characteristic:** The script creates edges only between entries that exist in the graph. If entry A links to Wikipedia article B, and article B is also an entry in the encyclopedia, then an edge is created. If article B is not an entry, no edge is created.

#### Step 6: Visualization (Pyvis)
- Creates interactive HTML visualization using Pyvis
- Color-codes nodes by degree (connectivity):
  - **Green** (`#00ff99`): >25 connections (highly connected nodes)
  - **Blue** (`#66b2ff`): >10 connections (main topics)
  - **Orange** (`#ff9933`): >4 connections (subfields/categories)
  - **Red** (`#ff5555`): ≤4 connections (related concepts)
- Rich tooltips with images and descriptions (max 1200 chars)
- Node size based on degree

#### Step 7: Search & Legend
- Adds search functionality to visualization
- Adds legend explaining node colors
- Opens visualization in browser

### Key Features

1. **Entry-to-Entry Edges**: Creates edges only between entries that are both in the encyclopedia
2. **Degree-Based Coloring**: Visual importance based on connectivity
3. **Rich Tooltips**: Images and descriptions in hover tooltips
4. **Interactive Visualization**: Search and navigation capabilities
5. **GraphML Export**: Standard format for graph analysis tools

## 2. Integration Plan for amilib

### Proposed Structure

**New File:** `amilib/ami_encyclopedia_kg.py`

**Class:** `AmiKnowledgeGraph`

### Integration Approach

#### Use Existing amilib Utilities

Instead of raw HTML parsing, the integrated version should:

1. **Use `AmiEncyclopedia` as input** (instead of raw HTML file)
   - Leverage existing `AmiEncyclopedia` class
   - Use `AmiEncyclopedia.entries` list

2. **Use `EncyclopediaLinkExtractor`** (instead of BeautifulSoup regex)
   - Leverage existing link extraction utilities
   - Use `_extract_description_links()` method
   - Normalize Wikipedia URLs properly

3. **Use `HtmlLib` for HTML parsing** (instead of BeautifulSoup)
   - Follow amilib patterns
   - Use existing HTML utilities

4. **Follow Style Guide**:
   - Absolute imports: `from amilib.ami_encyclopedia import AmiEncyclopedia`
   - Path construction: `Path("a", "b", "c")` not `Path("a/b/c")`
   - Use `Resources.TEMP_DIR` for temporary files

#### Preserve Core Logic

The integrated version should preserve:

1. **Node Creation**: From encyclopedia entries
2. **Link Extraction**: From entry descriptions
3. **Edge Creation**: Configurable edge types
   - Entry-to-entry (current behavior)
   - Entry-to-wiki (new requirement)
4. **GraphML Export**: Standard format
5. **Visualization Capabilities**: Optional Pyvis integration

#### Enhancements

1. **Configurable Edge Types**:
   - `edge_type="entry_to_entry"`: Only edges between entries (current behavior)
   - `edge_type="entry_to_wiki"`: Edges from entries to all Wikipedia links (new requirement)

2. **Better Integration**:
   - Accept `AmiEncyclopedia` instance
   - Use amilib utilities throughout
   - Follow amilib patterns and conventions

3. **Extensibility**:
   - Support for future NER (SpaCy/NLTK)
   - Support for KeyPhrases
   - Support for Wikidata relationship types for edge labels

## 3. Proposed Implementation

### Class Structure

```python
class AmiKnowledgeGraph:
    """
    Knowledge graph builder for encyclopedias.
    
    Based on work by Shaik Zainab (2015).
    
    Creates knowledge graphs from encyclopedia entries by:
    - Creating nodes from entries
    - Extracting Wikipedia links from descriptions
    - Creating edges between nodes (configurable)
    - Exporting to GraphML format
    """
    
    def __init__(self, encyclopedia: AmiEncyclopedia):
        """Initialize from AmiEncyclopedia"""
        self.encyclopedia = encyclopedia
        self.graph = nx.Graph()
        self.entry_nodes = {}
        self.wiki_nodes = {}
        
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
2. **Edge Types**: Configurable (entry-to-entry or entry-to-wiki)
3. **Link Extraction**: Uses `EncyclopediaLinkExtractor`
4. **GraphML Export**: Standard format
5. **Visualization**: Optional Pyvis integration

### Dependencies

- **NetworkX**: Already in requirements.txt
- **Pyvis**: Optional (for visualization)
- **amilib utilities**: Use existing utilities

## 4. Author Attribution

**Original Work:** Shaik Zainab (2015)  
**Integration:** amilib team (2025)

The integrated version will:
- Preserve core graph-building logic from Zainab's script
- Honor the original author in documentation
- Document the evolution from script to class
- Maintain the spirit of the original implementation

## 5. Next Steps

1. **Review by Zainab**: This document should be reviewed by Shaik Zainab before proceeding
2. **Implementation**: After approval, create `amilib/ami_encyclopedia_kg.py`
3. **Testing**: Create tests for the new class
4. **Documentation**: Update main documentation

## Questions for Review

1. Should we preserve the entry-to-entry edge behavior, or switch to entry-to-wiki?
2. Should visualization be part of the core class or a separate utility?
3. Should we support both edge types simultaneously?
4. How should we handle Wikidata relationship types for edge labels?

---

**Note:** This document is for review by Shaik Zainab before proceeding with implementation.

