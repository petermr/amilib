# Encyclopedia Clustering Architecture

## Class Structure Outline

### 1. `AmiEncyclopediaClusterer`
**Purpose**: Main orchestrator class for clustering encyclopedia entries based on description similarity.

**Methods**:
- `__init__(encyclopedia: AmiEncyclopedia, config: ClusterConfig = None)`
  - Initialize with encyclopedia and optional configuration
- `cluster_entries(method: str = "sentence_embeddings") -> Dict[int, List[str]]`
  - Main clustering method, returns cluster_id -> list of entry terms
- `assign_clusters_to_entries() -> AmiEncyclopedia`
  - Assigns cluster_id to each entry in the encyclopedia
- `get_cluster_statistics() -> Dict`
  - Returns statistics about clusters (sizes, silhouette score, etc.)
- `export_cluster_report(output_path: Path) -> None`
  - Exports clustering results to HTML/JSON report

**Internal Methods**:
- `_extract_descriptions() -> List[Tuple[str, str]]`
  - Extract (term, description_html) pairs from entries
- `_cluster_with_embeddings() -> Dict[int, List[str]]`
  - Clustering using sentence embeddings
- `_cluster_with_tfidf() -> Dict[int, List[str]]`
  - Clustering using TF-IDF (alternative method)
- `_evaluate_clusters(embeddings, labels) -> Dict`
  - Calculate clustering quality metrics

---

### 2. `TextExtractor`
**Purpose**: Utility class for extracting and preprocessing text from HTML descriptions.

**Methods**:
- `__init__(preprocessing_level: str = "basic")`
  - Initialize with preprocessing configuration
- `extract_text(description_html: str) -> str`
  - Convert HTML to plain text, strip tags
- `preprocess_text(text: str) -> str`
  - Apply preprocessing (lowercase, stopwords, lemmatization)
- `batch_extract(entries: List[Dict]) -> List[Tuple[str, str]]`
  - Extract text from multiple entries efficiently

**Internal Methods**:
- `_strip_html_tags(html: str) -> str`
  - Remove HTML tags using lxml
- `_normalize_whitespace(text: str) -> str`
  - Clean up whitespace
- `_apply_advanced_preprocessing(text: str) -> str`
  - Optional: lemmatization, POS tagging (if enabled)

---

### 3. `EmbeddingGenerator`
**Purpose**: Generate sentence embeddings from text descriptions.

**Methods**:
- `__init__(model_name: str = "all-MiniLM-L6-v2")`
  - Initialize with sentence transformer model
- `generate_embeddings(texts: List[str]) -> numpy.ndarray`
  - Generate embeddings for list of texts
- `generate_embedding(text: str) -> numpy.ndarray`
  - Generate embedding for single text
- `get_model_info() -> Dict`
  - Return model metadata (dimensions, name, etc.)

**Internal Methods**:
- `_load_model() -> None`
  - Lazy load the sentence transformer model
- `_batch_encode(texts: List[str]) -> numpy.ndarray`
  - Efficient batch encoding

---

### 4. `ClusterAlgorithm`
**Purpose**: Abstract base class for clustering algorithms.

**Subclasses**:
- `KMeansClusterer`
- `AgglomerativeClusterer`
- `DBSCANClusterer`
- `HDBSCANClusterer`

**Methods**:
- `__init__(n_clusters: Optional[int] = None, **kwargs)`
  - Initialize with clustering parameters
- `fit(embeddings: numpy.ndarray) -> None`
  - Fit the clustering model
- `predict(embeddings: numpy.ndarray) -> numpy.ndarray`
  - Predict cluster labels
- `get_cluster_labels() -> numpy.ndarray`
  - Get cluster assignments
- `get_n_clusters() -> int`
  - Get number of clusters (auto-determined or specified)

**Concrete Implementations**:
- `KMeansClusterer`: K-means clustering with optional elbow method
- `AgglomerativeClusterer`: Hierarchical clustering with linkage options
- `DBSCANClusterer`: Density-based clustering (no n_clusters needed)
- `HDBSCANClusterer`: Hierarchical DBSCAN (handles varying densities)

---

### 5. `ClusterEvaluator`
**Purpose**: Evaluate clustering quality.

**Methods**:
- `__init__()`
  - Initialize evaluator
- `evaluate(embeddings: numpy.ndarray, labels: numpy.ndarray) -> Dict`
  - Calculate multiple evaluation metrics
- `silhouette_score(embeddings, labels) -> float`
  - Calculate silhouette coefficient
- `calinski_harabasz_score(embeddings, labels) -> float`
  - Calculate Calinski-Harabasz index
- `davies_bouldin_score(embeddings, labels) -> float`
  - Calculate Davies-Bouldin index
- `cluster_size_distribution(labels) -> Dict`
  - Analyze cluster size distribution

---

### 6. `ClusterConfig`
**Purpose**: Configuration dataclass for clustering parameters.

**Attributes**:
- `method: str` - "sentence_embeddings", "tfidf", "hybrid"
- `embedding_model: str` - Model name for sentence-transformers
- `clustering_algorithm: str` - "kmeans", "agglomerative", "dbscan", "hdbscan"
- `n_clusters: Optional[int]` - Number of clusters (None for auto)
- `distance_metric: str` - "cosine", "euclidean"
- `preprocessing_level: str` - "basic", "advanced"
- `min_cluster_size: int` - For DBSCAN/HDBSCAN
- `random_state: int` - For reproducibility

---

## Workflow Overview

1. **Input**: `AmiEncyclopedia` with entries containing `description_html`
2. **Text Extraction**: Extract plain text from HTML descriptions
3. **Preprocessing**: Clean and normalize text (optional advanced preprocessing)
4. **Embedding Generation**: Convert texts to vector embeddings
5. **Clustering**: Apply clustering algorithm to embeddings
6. **Evaluation**: Calculate clustering quality metrics
7. **Assignment**: Assign cluster IDs to encyclopedia entries
8. **Output**: Updated `AmiEncyclopedia` with cluster assignments + statistics

---

## Integration Points

- **Input**: `AmiEncyclopedia.entries` (list of dicts with `description_html`)
- **Output**: 
  - Updated entries with `cluster_id` attribute
  - Cluster statistics dictionary
  - Optional: cluster report HTML/JSON
- **Storage**: Cluster assignments stored in entry dictionaries
- **Visualization**: Cluster IDs can be used to color-code nodes in knowledge graph
- **Export**: Cluster information included in GraphML output

---

## Dependencies

- `sentence-transformers` (v2.2.0+)
- `scikit-learn` (v1.0.0+)
- `numpy` (for embeddings)
- `lxml` or `BeautifulSoup4` (for HTML parsing - already in use)
- Optional: `nltk` or `spaCy` (for advanced preprocessing)

---

## Author Attribution

Based on clustering concepts and adapted for encyclopedia entry clustering.
Integration with `AmiEncyclopedia` follows amilib patterns and style guide.

