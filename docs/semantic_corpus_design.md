# SemanticCorpus: Design Rationale and Specification

## Executive Summary

SemanticCorpus is a software system for managing personal research corpora (100-10,000 articles) with semantic enrichment and content-based relationship discovery. It addresses the challenge of organizing, validating, and navigating large collections of academic papers, theses, and institutional reports through automated semantification and similarity analysis.

---

## 1. Academic Rationale

### 1.1 Problem Statement

Academic researchers face several challenges when managing personal research collections:

**Information Overload**: Researchers accumulate hundreds to thousands of papers over time, making manual organization and discovery increasingly difficult.

**Fragmented Knowledge**: Related papers are often discovered through different searches at different times, creating disconnected islands of knowledge that are hard to navigate.

**Quality Assurance**: Document conversion (PDF→HTML, XML→HTML) introduces errors that can corrupt downstream analysis. Researchers need validation tools to ensure conversion quality before investing time in reading or analysis.

**Semantic Gaps**: Raw text lacks explicit semantic structure. Researchers need tools to identify key concepts, link related terms, and discover content-based relationships between documents.

**Reproducibility**: Research workflows involving corpus creation, processing, and analysis need to be documented and reproducible for scientific rigor.

### 1.2 Academic Use Cases

**Literature Review Management**
- Organize papers from systematic searches (e.g., via pygetpapers)
- Identify papers with similar content for comparative analysis
- Track which papers have been read, annotated, or cited
- Build thematic clusters of related research

**Research Discovery**
- Find papers similar to a seed paper based on content similarity
- Discover connections between papers that weren't explicitly cited
- Identify gaps in research coverage
- Navigate related work through content-based links

**Quality Control**
- Validate PDF→HTML conversion quality before analysis
- Ensure metadata completeness (DOIs, titles, authors, abstracts)
- Detect and flag corrupted or incomplete documents
- Monitor processing pipeline health

**Semantic Annotation**
- Enrich documents with semantic IDs (paragraphs, sections, terms)
- Link terms to external knowledge bases (Wikipedia, Wikidata)
- Create navigable semantic structures within documents
- Enable semantic search and querying

**Personal Knowledge Management**
- Build a searchable, semantically-enriched personal library
- Create persistent links between related documents
- Maintain provenance of document sources (search queries, dates)
- Support long-term research project organization

### 1.3 Academic Value Proposition

**For Individual Researchers**
- Reduces time spent searching for related papers
- Improves organization of personal research collections
- Enables discovery of non-obvious connections between papers
- Provides quality assurance for document processing pipelines

**For Research Groups**
- Standardizes corpus management practices
- Enables sharing of semantically-enriched corpora
- Supports collaborative literature review workflows
- Facilitates reproducible research practices

**For the Research Community**
- Demonstrates best practices for personal corpus management
- Provides open-source tools for semantic document processing
- Contributes to reproducibility in computational research
- Supports FAIR principles (Findable, Accessible, Interoperable, Reusable)

---

## 2. System Overview

### 2.1 Core Concept

**SemanticCorpus** = **Documents** + **Semantification** + **Relations**

- **Documents**: A collection of articles (papers, theses, reports) with metadata
- **Semantification**: Enrichment with semantic IDs, term annotations, and structured markup
- **Relations**: Content-based similarity links between documents

### 2.2 Design Principles

1. **Personal Corpus Scale**: Optimized for 100-10,000 articles (not millions)
2. **Content-Based Relations**: Focus on semantic similarity, not citations
3. **Quality First**: Validation of conversions and metadata before processing
4. **Integration-Friendly**: Works with existing tools (pygetpapers, amilib)
5. **Reproducible**: Tracks provenance and processing history

---

## 3. Inputs

### 3.1 Search Results (Primary Input)

**Source**: pygetpapers (external tool)
**Format**: JSON metadata files (`eupmc_result.json`)

**Structure**:
```json
{
  "papers": [
    {
      "pmcid": "PMC123456",
      "doi": "10.1234/example",
      "title": "Example Paper Title",
      "authors": ["Author1", "Author2"],
      "journal": "Journal Name",
      "year": 2023,
      "abstract": "Abstract text...",
      "fulltext": "path/to/fulltext.xml"
    }
  ],
  "query": "climate change AND adaptation",
  "total_hits": 150,
  "date": "2024-01-15"
}
```

**Metadata Fields**:
- **Identifiers**: PMCID, DOI, PMID
- **Bibliographic**: Title, Authors, Journal, Year
- **Content**: Abstract, Full-text paths
- **Provenance**: Query, Search date, Source API

### 3.2 Document Files

**Formats**:
- **PDF**: Original papers (from publishers or repositories)
- **XML**: Structured full-text (from EPMC, PubMed Central)
- **HTML**: Converted/processed documents (from PDF/XML conversion)

**Sources**:
- Downloaded via pygetpapers
- Manually added files
- Institutional repositories
- Preprint servers

### 3.3 Configuration Files

**Search Configuration** (`saved_config.ini`):
- Search queries
- API endpoints
- Date ranges
- Filter criteria

**Processing Configuration**:
- Conversion parameters
- Semantic annotation rules
- Quality thresholds
- Output formats

---

## 4. Uses

### 4.1 Corpus Ingestion

**Purpose**: Import search results into structured corpus

**Process**:
1. Read pygetpapers JSON output
2. Extract metadata for each paper
3. Locate corresponding document files (PDF/XML)
4. Create corpus entry with metadata
5. Validate file existence and accessibility
6. Generate corpus manifest

**Output**:
- Structured corpus directory
- Document metadata database
- Ingestion report (success/failure counts)

### 4.2 Document Conversion Validation

**Purpose**: Ensure quality of PDF→HTML and XML→HTML conversions

**Validation Checks**:
- **Completeness**: All pages/sections converted
- **Structure**: Headings, paragraphs, lists preserved
- **Content**: Text extraction quality (no garbled characters)
- **Metadata**: Document metadata present and correct
- **Links**: Internal links and references functional

**Metrics**:
- Conversion success rate (%)
- Page count consistency (PDF pages vs HTML pages)
- Text extraction quality (character encoding errors)
- Structural element preservation (headings, paragraphs)

**Output**:
- Validation report per document
- Quality scores
- Flagged documents requiring manual review

### 4.3 Metadata Validation

**Purpose**: Ensure per-document metadata completeness and correctness

**Required Metadata**:
- **Identifiers**: At least one of (DOI, PMCID, PMID)
- **Title**: Present and non-empty
- **Authors**: At least one author listed
- **Year**: Publication year present
- **Abstract**: Abstract text available (if applicable)

**Optional Metadata**:
- Journal name
- Keywords
- Subject categories
- License information

**Validation Rules**:
- Check for missing required fields
- Validate identifier formats (DOI regex, PMCID format)
- Detect duplicate entries
- Flag inconsistent metadata (e.g., year mismatch)

**Output**:
- Metadata completeness report
- Missing field summary
- Validation errors/warnings

### 4.4 Semantification

**Purpose**: Add semantic structure and annotations to documents

**Semantic Enhancements**:
- **Paragraph IDs**: Unique identifiers for each paragraph (`{doc_id}_p{index}`)
- **Section IDs**: Hierarchical section identifiers (`{doc_id}_s{section_number}`)
- **Term Annotation**: Link key terms to external knowledge bases
- **Semantic Markup**: Add RDFa/HTML5 semantic attributes

**Process**:
1. Parse document structure (headings, paragraphs)
2. Generate semantic IDs following naming conventions
3. Extract key terms/phrases
4. Link terms to Wikipedia/Wikidata (optional)
5. Add semantic markup to HTML

**Output**:
- Semantically-enriched HTML documents
- Term index
- Semantic ID mapping

### 4.5 Content Similarity Analysis

**Purpose**: Discover relationships between documents based on content similarity

**Similarity Metrics**:
- **TF-IDF Cosine Similarity**: Term frequency-based similarity
- **Semantic Term Overlap**: Shared semantic concepts/terms
- **Abstract Similarity**: Compare abstracts using text similarity
- **Topic Modeling**: LDA/topic-based similarity (future)

**Process**:
1. Extract text features from each document (abstract + full-text)
2. Compute similarity matrix (document × document)
3. Apply threshold to identify significant relationships
4. Generate similarity graph
5. Create navigable links between similar documents

**Output**:
- Similarity matrix (sparse, thresholded)
- Similarity graph (nodes=documents, edges=similarity scores)
- "Related papers" lists per document
- Clustering visualization

### 4.6 Corpus Navigation

**Purpose**: Enable discovery and navigation of related content

**Navigation Features**:
- **Similar Document Discovery**: "Find papers similar to this one"
- **Thematic Clustering**: Group papers by topic similarity
- **Semantic Search**: Search by semantic concepts, not just keywords
- **Relationship Visualization**: Graph view of document relationships

**Use Cases**:
- Starting from a seed paper, discover related papers
- Explore thematic clusters
- Navigate through content-based connections
- Identify papers that bridge different topics

---

## 5. Static Analysis Design

### 5.1 Analysis Scope

**Document-Level Analysis**:
- Conversion quality metrics
- Metadata completeness scores
- Semantic annotation coverage
- Structural integrity checks

**Corpus-Level Analysis**:
- Corpus statistics (size, coverage, diversity)
- Processing pipeline health
- Relationship graph metrics
- Quality distribution analysis

### 5.2 Analysis Components

#### 5.2.1 Conversion Quality Analysis

**Metrics**:
- **Page Count Match**: PDF pages vs HTML pages
- **Text Extraction Rate**: % of text successfully extracted
- **Structure Preservation**: Headings, paragraphs, lists detected
- **Encoding Errors**: Character encoding issues detected
- **Link Integrity**: Internal links functional

**Output**: Quality score per document (0-100)

#### 5.2.2 Metadata Completeness Analysis

**Metrics**:
- **Required Field Coverage**: % of documents with all required fields
- **Identifier Availability**: % with DOI/PMCID/PMID
- **Content Availability**: % with abstracts, full-text
- **Consistency Checks**: Duplicate detection, format validation

**Output**: Completeness report with missing field summary

#### 5.2.3 Semantic Annotation Analysis

**Metrics**:
- **ID Coverage**: % of paragraphs/sections with semantic IDs
- **Term Annotation Rate**: % of key terms annotated
- **Link Success Rate**: % of external links valid
- **Semantic Density**: Average annotations per document

**Output**: Annotation coverage report

#### 5.2.4 Relationship Graph Analysis

**Metrics**:
- **Graph Connectivity**: Average degree, clustering coefficient
- **Component Analysis**: Number of connected components
- **Similarity Distribution**: Histogram of similarity scores
- **Hub Detection**: Documents with many relationships

**Output**: Graph statistics and visualization

### 5.3 Analysis Workflow

1. **Ingest**: Load corpus and metadata
2. **Validate**: Run conversion and metadata checks
3. **Analyze**: Compute quality metrics and statistics
4. **Report**: Generate analysis reports (HTML, JSON)
5. **Visualize**: Create charts and graphs

---

## 6. Workflow Design

### 6.1 High-Level Workflow

```
┌─────────────────┐
│ 1. Ingestion    │  ← pygetpapers JSON results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Validation   │  ← Conversion quality, metadata checks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Conversion   │  ← PDF/XML → HTML (if needed)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Semantification │  ← Add semantic IDs, annotations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Similarity   │  ← Compute content similarity
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Analysis     │  ← Static analysis, reports
└─────────────────┘
```

### 6.2 Detailed Workflow Stages

#### Stage 1: Ingestion
- **Input**: pygetpapers JSON (`eupmc_result.json`)
- **Process**: 
  - Parse JSON metadata
  - Locate document files
  - Create corpus structure
  - Generate manifest
- **Output**: Corpus directory with metadata

#### Stage 2: Validation
- **Input**: Corpus with documents
- **Process**:
  - Check file existence
  - Validate conversion quality (if HTML exists)
  - Check metadata completeness
  - Generate validation report
- **Output**: Validation report, flagged documents

#### Stage 3: Conversion (if needed)
- **Input**: PDF/XML documents
- **Process**:
  - Convert PDF→HTML or XML→HTML
  - Preserve structure
  - Extract metadata
- **Output**: HTML documents

#### Stage 4: Semantification
- **Input**: HTML documents
- **Process**:
  - Detect structure (headings, paragraphs)
  - Generate semantic IDs
  - Extract key terms
  - Add semantic markup
- **Output**: Semantically-enriched HTML

#### Stage 5: Similarity Analysis
- **Input**: Semantically-enriched documents
- **Process**:
  - Extract text features
  - Compute similarity matrix
  - Build relationship graph
  - Apply thresholds
- **Output**: Similarity graph, related document lists

#### Stage 6: Static Analysis
- **Input**: Complete corpus
- **Process**:
  - Compute quality metrics
  - Analyze relationship graph
  - Generate statistics
  - Create visualizations
- **Output**: Analysis reports, visualizations

---

## 7. Software Package Components

### 7.1 Core Modules

**Corpus Management** (`corpus_module`):
- `AmiCorpus`: Main corpus class
- `AmiCorpusContainer`: Hierarchical organization
- File ingestion and organization

**Ingestion** (`ingestion_module`):
- Parse pygetpapers JSON
- Extract metadata
- Locate document files
- Create corpus structure

**Validation** (`validation_module`):
- Conversion quality checks
- Metadata completeness validation
- File integrity checks
- Report generation

**Semantification** (`semantification_module`):
- Structure detection
- Semantic ID generation
- Term extraction
- Annotation addition

**Similarity** (`similarity_module`):
- Feature extraction
- Similarity computation
- Graph construction
- Relationship discovery

**Analysis** (`analysis_module`):
- Static analysis
- Metric computation
- Report generation
- Visualization

### 7.2 Integration Points

**pygetpapers**:
- Reads `eupmc_result.json` output
- Uses `saved_config.ini` for query provenance
- Compatible with pygetpapers directory structure

**amilib**:
- Uses `ami_html` for HTML processing
- Uses `ami_dict` for term management
- Uses `ami_encyclopedia` for semantic enrichment
- Uses `ami_graph` for graph operations

---

## 8. Outputs

### 8.1 Corpus Structure

```
corpus_name/
├── bag-info.txt              # BagIt metadata
├── manifest-md5.txt          # File checksums
├── data/
│   ├── documents/            # Document files (PDF, XML, HTML)
│   ├── metadata/             # Per-document metadata (JSON)
│   ├── semantic/             # Semantically-enriched HTML
│   └── indices/              # Search indices
├── relations/
│   ├── similarity_matrix.json
│   ├── similarity_graph.graphml
│   └── related_documents.json
├── analysis/
│   ├── validation_report.html
│   ├── quality_metrics.json
│   └── corpus_statistics.json
└── provenance/
    ├── ingestion_log.json
    └── processing_history.json
```

### 8.2 Reports

**Validation Report**:
- Conversion quality scores
- Metadata completeness
- Flagged documents
- Summary statistics

**Analysis Report**:
- Corpus statistics
- Relationship graph metrics
- Quality distribution
- Recommendations

**Similarity Report**:
- Similarity matrix summary
- Top similar document pairs
- Clustering results
- Relationship visualization

---

## 9. Limitations and Future Work

### 9.1 Current Limitations

- **No Citation Analysis**: Citations are excluded from relations (too broad/complex)
- **No Versioning**: Document versions not tracked (future enhancement)
- **Personal Corpus Scale**: Optimized for 100-10K articles, not millions
- **Manual Quality Review**: Some quality issues require manual intervention

### 9.2 Future Enhancements

- **Citation Integration**: Add citation-based relations (separate from content similarity)
- **Version Control**: Track document versions and updates
- **Advanced Topic Modeling**: LDA, BERT-based topic extraction
- **Interactive Visualization**: Web-based corpus explorer
- **Export Formats**: Export to standard formats (BibTeX, RIS, etc.)

---

## 10. Conclusion

SemanticCorpus addresses a real need in academic research: managing personal research collections with semantic enrichment and content-based discovery. By focusing on quality validation, semantic annotation, and similarity-based relations, it provides researchers with tools to organize, navigate, and discover connections in their personal research libraries.

The system's integration with existing tools (pygetpapers, amilib) and focus on reproducibility make it suitable for academic use and publication in JOSS.

---

## References

- pygetpapers: https://github.com/petermr/pygetpapers
- amilib: https://github.com/petermr/amilib
- BagIt Specification: https://datatracker.ietf.org/doc/html/rfc8493
- FAIR Principles: https://www.go-fair.org/fair-principles/


