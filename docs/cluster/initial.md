# Encyclopedia Clustering Implementation - Initial Summary

**Date**: 2025-01-09  
**Author**: Implementation based on work by Shaik Zainab (2015)  
**Status**: ✅ Complete - All tests passing

## Overview

The encyclopedia clustering facility provides functionality to cluster encyclopedia entries based on textual similarity of their descriptions. This enables identification of related concepts and grouping of semantically similar entries.

## Architecture

### Main Components

1. **`AmiEncyclopediaClusterer`** - Main orchestrator class
   - Coordinates the clustering pipeline
   - Extracts descriptions, generates embeddings, applies clustering
   - Assigns cluster IDs to entries
   - Generates statistics and reports
   - Creates 2D visualizations

2. **`TextExtractor`** - HTML to text conversion
   - Extracts plain text from HTML descriptions
   - Preprocesses text (lowercase, whitespace normalization)
   - Supports basic and advanced preprocessing levels

3. **`EmbeddingGenerator`** - Sentence embeddings
   - Uses sentence-transformers library
   - Default model: `all-MiniLM-L6-v2`
   - Generates vector representations for text descriptions
   - Lazy loading of models

4. **`ClusterAlgorithm`** - Abstract base class
   - **`KMeansClusterer`** - K-means clustering
   - **`AgglomerativeClusterer`** - Hierarchical clustering
   - **`DBSCANClusterer`** - Density-based clustering (handles noise)

5. **`ClusterEvaluator`** - Quality metrics
   - Silhouette score
   - Calinski-Harabasz index
   - Davies-Bouldin index
   - Cluster size distribution

6. **`ClusterConfig`** - Configuration dataclass
   - Method selection (sentence_embeddings, tfidf)
   - Clustering algorithm (kmeans, agglomerative, dbscan)
   - Number of clusters
   - Embedding model selection
   - Preprocessing options

## Key Features

### Clustering Methods

- **Sentence Embeddings** (default): Uses pre-trained sentence transformers to generate semantic embeddings
- **TF-IDF** (not yet implemented): Alternative method using term frequency-inverse document frequency

### Clustering Algorithms

- **K-Means**: Partition-based clustering with specified number of clusters
- **Agglomerative**: Hierarchical clustering with linkage options
- **DBSCAN**: Density-based clustering that automatically determines cluster count and handles noise

### Visualization

- **Automatic 2D plots**: Created automatically when clusters are generated
- **Dimensionality reduction**: PCA (default) or t-SNE
- **Color-coded clusters**: Each cluster gets distinct color
- **Labeled nodes**: Each point labeled with Wikipedia term
- **SVG output**: Scalable vector graphics saved to `temp/cluster_visualization.svg`
- **Noise visualization**: Noise points (from DBSCAN) shown in gray with 'x' markers

## Usage

### Basic Usage

```python
from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer

# Create encyclopedia
encyclopedia = AmiEncyclopedia(title="My Encyclopedia")
encyclopedia.create_from_html_file(html_file)

# Cluster entries (automatically creates visualization)
clusterer = AmiEncyclopediaClusterer(encyclopedia)
clusters = clusterer.cluster_entries()

# Get statistics
stats = clusterer.get_cluster_statistics()
print(f"Created {stats['n_clusters']} clusters")
print(f"Silhouette score: {stats['silhouette_score']}")

# Assign cluster IDs to entries
updated_encyclopedia = clusterer.assign_clusters_to_entries()
```

### Custom Configuration

```python
from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer, ClusterConfig

# Custom configuration
config = ClusterConfig(
    method="sentence_embeddings",
    clustering_algorithm="kmeans",
    n_clusters=5,
    embedding_model="all-MiniLM-L6-v2",
    preprocessing_level="basic"
)

clusterer = AmiEncyclopediaClusterer(encyclopedia, config)
clusters = clusterer.cluster_entries()
```

### Manual Visualization

```python
# Create visualization with custom path and method
output_path = Path("temp/my_clusters.svg")
clusterer.visualize_clusters(output_path, method="tsne")

# Disable automatic visualization
clusters = clusterer.cluster_entries(visualize=False)
```

### Export Cluster Report

```python
# Export HTML report with cluster details
report_path = Path("temp/cluster_report.html")
clusterer.export_cluster_report(report_path)
```

## Dependencies

### Required
- `numpy` - For array operations
- `lxml` - For HTML parsing (already in amilib)
- `scikit-learn` - For clustering algorithms and metrics
- `matplotlib` - For visualization (already in amilib)

### Optional
- `sentence-transformers` - For sentence embeddings (required for default method)
- `torch` - Dependency of sentence-transformers

## File Structure

```
amilib/
  └── ami_encyclopedia_cluster.py  # Main clustering module

test/
  └── test_cluster.py              # Comprehensive test suite (24 tests)

docs/
  ├── cluster/
  │   └── initial.md               # This summary
  ├── encyclopedia_clustering_architecture.md  # Detailed architecture
  ├── encyclopedia_clustering_implementation_proposal.md  # Implementation plan
  └── graphviz/
      └── encyclopedia_clustering_workflow.svg  # Workflow diagram
```

## Testing

### Test Coverage

- ✅ **ClusterTest** (7 tests): Main clustering functionality
- ✅ **TextExtractorTest** (4 tests): Text extraction and preprocessing
- ✅ **EmbeddingGeneratorTest** (4 tests): Embedding generation
- ✅ **ClusterAlgorithmTest** (3 tests): Clustering algorithms (KMeans, Agglomerative, DBSCAN)
- ✅ **ClusterEvaluatorTest** (4 tests): Evaluation metrics
- ✅ **ClusterIntegrationTest** (2 tests): End-to-end workflows

**Total**: 24 tests - All passing ✅

### Running Tests

```bash
# Run all clustering tests
python3 -m pytest test/test_cluster.py -v

# Run specific test class
python3 -m pytest test/test_cluster.py::ClusterTest -v
```

## Implementation Details

### Workflow

1. **Extract Descriptions**: Get HTML descriptions from encyclopedia entries
2. **Extract Text**: Convert HTML to plain text using `TextExtractor`
3. **Generate Embeddings**: Create sentence embeddings using `EmbeddingGenerator`
4. **Cluster**: Apply clustering algorithm (KMeans, Agglomerative, or DBSCAN)
5. **Evaluate**: Calculate quality metrics (silhouette, Calinski-Harabasz, Davies-Bouldin)
6. **Visualize**: Create 2D plot with PCA or t-SNE reduction
7. **Assign**: Add cluster IDs to encyclopedia entries
8. **Report**: Generate HTML report with cluster details

### Visualization Details

- **Figure size**: 16x12 inches for readability
- **Color scheme**: 'tab20' colormap (supports up to 20 clusters)
- **Labels**: Each point annotated with Wikipedia term
- **Format**: SVG for scalability
- **Location**: `temp/cluster_visualization.svg` by default
- **Dimensionality reduction**: PCA (fast) or t-SNE (better separation)

## Configuration Options

### ClusterConfig Parameters

- `method`: "sentence_embeddings" (default) or "tfidf"
- `embedding_model`: Model name for sentence-transformers (default: "all-MiniLM-L6-v2")
- `clustering_algorithm`: "kmeans" (default), "agglomerative", or "dbscan"
- `n_clusters`: Number of clusters (None for auto, default: None)
- `distance_metric`: "cosine" (default) or "euclidean"
- `preprocessing_level`: "basic" (default) or "advanced"
- `min_cluster_size`: For DBSCAN/HDBSCAN (default: 2)
- `random_state`: For reproducibility (default: 42)

## Output Files

### Visualization
- **Location**: `temp/cluster_visualization.svg`
- **Format**: SVG (scalable vector graphics)
- **Content**: 2D scatter plot with color-coded clusters and labeled nodes

### Cluster Report
- **Location**: Custom path (default: `temp/cluster_report.html`)
- **Format**: HTML
- **Content**: Statistics, cluster sizes, evaluation metrics, cluster details

## Integration Points

- **Input**: `AmiEncyclopedia` with entries containing `description_html`
- **Output**: 
  - Updated entries with `cluster_id` attribute
  - Cluster statistics dictionary
  - Visualization SVG file
  - Optional HTML report
- **Storage**: Cluster assignments stored in entry dictionaries
- **Visualization**: Cluster IDs can be used to color-code nodes in knowledge graph
- **Export**: Cluster information can be included in GraphML output

## Future Enhancements

1. **TF-IDF Clustering**: Implement alternative clustering method
2. **Advanced Preprocessing**: Add NLTK/spaCy lemmatization
3. **Interactive Visualization**: Web-based interactive plots
4. **Cluster Merging**: Automatic merging of similar clusters
5. **Hierarchical Visualization**: Tree view of cluster relationships
6. **Export to GraphML**: Include cluster information in knowledge graph

## Author Attribution

Based on clustering concepts and adapted for encyclopedia entry clustering.  
Integration with `AmiEncyclopedia` follows amilib patterns and style guide.

**Original Work**: Shaik Zainab (2015) - Network generator script (`amilib/resources/scripts/zainab.py`)

## References

- Architecture: `docs/encyclopedia_clustering_architecture.md`
- Implementation Plan: `docs/encyclopedia_clustering_implementation_proposal.md`
- Workflow Diagram: `docs/graphviz/encyclopedia_clustering_workflow.svg`
- Original Script: `amilib/resources/scripts/zainab.py`

