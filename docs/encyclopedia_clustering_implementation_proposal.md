# Encyclopedia Clustering Implementation Proposal

## Overview
This document proposes the implementation approach for each component to make the tests pass. All code should follow amilib style guide (absolute imports, Path construction, etc.).

---

## 1. TextExtractor Implementation

### Dependencies
- `lxml` (already in use in amilib)
- Optional: `nltk` or `spaCy` for advanced preprocessing

### Implementation Approach

#### `extract_text(description_html: str) -> str`
1. Use `lxml.html.fromstring()` to parse HTML
2. Use `.text_content()` or `.get_text()` to extract plain text
3. Call `_normalize_whitespace()` to clean up
4. Return cleaned text string

#### `preprocess_text(text: str) -> str`
1. Convert to lowercase using `.lower()`
2. Normalize whitespace using `_normalize_whitespace()`
3. If `preprocessing_level == "advanced"`:
   - Call `_apply_advanced_preprocessing()` for lemmatization
4. Return preprocessed text

#### `batch_extract(entries: List[Dict]) -> List[Tuple[str, str]]`
1. Iterate through entries
2. For each entry:
   - Extract `term` and `description_html`
   - Call `extract_text()` on `description_html`
   - Optionally call `preprocess_text()` if needed
   - Return tuple `(term, text)`
3. Return list of tuples

#### `_strip_html_tags(html: str) -> str`
1. Use `lxml.html.fromstring(html)`
2. Call `.text_content()` to get text without tags
3. Return plain text

#### `_normalize_whitespace(text: str) -> str`
1. Use `re.sub(r'\s+', ' ', text)` to replace multiple whitespace with single space
2. Strip leading/trailing whitespace
3. Return normalized text

#### `_apply_advanced_preprocessing(text: str) -> str`
1. For now, return text as-is (can be enhanced later with NLTK/spaCy)
2. Future: tokenize, lemmatize, remove stopwords

---

## 2. EmbeddingGenerator Implementation

### Dependencies
- `sentence-transformers` (v2.2.0+)
- `numpy` (for arrays)
- `torch` (dependency of sentence-transformers)

### Implementation Approach

#### `__init__(model_name: str = "all-MiniLM-L6-v2")`
1. Store `model_name`
2. Set `self.model = None` (lazy loading)
3. Set `self.dimensions = None` (will be set when model loads)

#### `_load_model() -> None`
1. Check if `self.model is None`
2. Import `SentenceTransformer` from `sentence_transformers`
3. Load model: `self.model = SentenceTransformer(self.model_name)`
4. Get dimensions from model: `self.dimensions = self.model.get_sentence_embedding_dimension()`
5. Handle ImportError gracefully (log warning if library not installed)

#### `generate_embeddings(texts: List[str]) -> np.ndarray`
1. Call `_load_model()` if model not loaded
2. Use `self.model.encode(texts)` to generate embeddings
3. Convert to numpy array: `np.array(embeddings)`
4. Return numpy array of shape `(n_samples, n_dimensions)`

#### `generate_embedding(text: str) -> np.ndarray`
1. Call `generate_embeddings([text])` with single-item list
2. Return first row: `embeddings[0]`

#### `get_model_info() -> Dict`
1. Call `_load_model()` if model not loaded
2. Return dictionary:
   ```python
   {
       'model_name': self.model_name,
       'dimensions': self.dimensions,
       'loaded': self.model is not None
   }
   ```

---

## 3. ClusterAlgorithm Implementations

### Dependencies
- `scikit-learn` (v1.0.0+)
- `numpy`

### Implementation Approach

#### Base Class: `ClusterAlgorithm`
- Store `n_clusters`, `model`, `labels_` as instance variables
- Abstract methods: `fit()`, `predict()`, `get_cluster_labels()`, `get_n_clusters()`

#### `KMeansClusterer`
1. Import `KMeans` from `sklearn.cluster`
2. `__init__()`: Store `n_clusters`, set `random_state` from config
3. `fit(embeddings)`:
   - Create `KMeans(n_clusters=self.n_clusters, random_state=42)`
   - Call `fit(embeddings)`
   - Store model in `self.model`
4. `predict(embeddings)`:
   - Call `self.model.predict(embeddings)`
   - Store in `self.labels_`
   - Return labels
5. `get_n_clusters()`: Return `self.n_clusters` or `len(set(self.labels_))`

#### `AgglomerativeClusterer`
1. Import `AgglomerativeClustering` from `sklearn.cluster`
2. `__init__()`: Store `n_clusters`, set `linkage='ward'` (default)
3. `fit(embeddings)`:
   - Create `AgglomerativeClustering(n_clusters=self.n_clusters, linkage='ward')`
   - Call `fit_predict(embeddings)` (Agglomerative doesn't have separate fit/predict)
   - Store labels in `self.labels_`
4. `predict(embeddings)`:
   - Return `self.labels_` (already computed in fit)
5. `get_n_clusters()`: Return `self.n_clusters` or `len(set(self.labels_))`

#### `DBSCANClusterer`
1. Import `DBSCAN` from `sklearn.cluster`
2. `__init__()`: Store `min_cluster_size` (maps to `min_samples`), set `eps=0.5` (default)
3. `fit(embeddings)`:
   - Create `DBSCAN(min_samples=self.min_cluster_size, eps=0.5)`
   - Call `fit_predict(embeddings)`
   - Store labels in `self.labels_`
4. `predict(embeddings)`:
   - Return `self.labels_` (DBSCAN doesn't support new predictions)
5. `get_n_clusters()`: Count unique labels excluding -1 (noise): `len(set(self.labels_)) - (1 if -1 in self.labels_ else 0)`

---

## 4. ClusterEvaluator Implementation

### Dependencies
- `scikit-learn` (for metrics)
- `numpy`

### Implementation Approach

#### `evaluate(embeddings: np.ndarray, labels: np.ndarray) -> Dict`
1. Call all three metric methods
2. Call `cluster_size_distribution()`
3. Return dictionary:
   ```python
   {
       'silhouette_score': self.silhouette_score(embeddings, labels),
       'calinski_harabasz_score': self.calinski_harabasz_score(embeddings, labels),
       'davies_bouldin_score': self.davies_bouldin_score(embeddings, labels),
       'cluster_size_distribution': self.cluster_size_distribution(labels)
   }
   ```

#### `silhouette_score(embeddings, labels) -> float`
1. Import `silhouette_score` from `sklearn.metrics`
2. Call `silhouette_score(embeddings, labels, metric='cosine')` if using cosine distance
3. Return float value

#### `calinski_harabasz_score(embeddings, labels) -> float`
1. Import `calinski_harabasz_score` from `sklearn.metrics`
2. Call `calinski_harabasz_score(embeddings, labels)`
3. Return float value

#### `davies_bouldin_score(embeddings, labels) -> float`
1. Import `davies_bouldin_score` from `sklearn.metrics`
2. Call `davies_bouldin_score(embeddings, labels)`
3. Return float value

#### `cluster_size_distribution(labels) -> Dict`
1. Use `np.unique(labels, return_counts=True)` to get cluster sizes
2. Create dictionary mapping `cluster_id -> size`
3. Exclude noise points (-1) if present
4. Return dictionary

---

## 5. AmiEncyclopediaClusterer Implementation

### Dependencies
- All above components
- `AmiEncyclopedia` (already exists)

### Implementation Approach

#### `cluster_entries(method: Optional[str] = None) -> Dict[int, List[str]]`
1. Extract descriptions using `_extract_descriptions()`
2. Based on `method` or `self.config.method`:
   - If "sentence_embeddings": call `_cluster_with_embeddings()`
   - If "tfidf": call `_cluster_with_tfidf()`
3. Store clusters in `self.clusters`
4. Return `self.clusters`

#### `_extract_descriptions() -> List[Tuple[str, str]]`
1. Create `TextExtractor` instance
2. Extract `(term, description_html)` pairs from `self.encyclopedia.entries`
3. For each entry:
   - Get `term` and `description_html`
   - Skip if `description_html` is empty
4. Return list of tuples

#### `_cluster_with_embeddings() -> Dict[int, List[str]]`
1. Extract descriptions: `descriptions = self._extract_descriptions()`
2. Extract texts:
   - Create `TextExtractor`
   - For each `(term, html)`: call `extractor.extract_text(html)`
   - Store `(term, text)` pairs
3. Generate embeddings:
   - Create `EmbeddingGenerator` with `self.config.embedding_model`
   - Call `generate_embeddings([text for _, text in texts])`
   - Store in `self.embeddings`
4. Create clustering algorithm:
   - Based on `self.config.clustering_algorithm`:
     - "kmeans": `KMeansClusterer(n_clusters=self.config.n_clusters)`
     - "agglomerative": `AgglomerativeClusterer(n_clusters=self.config.n_clusters)`
     - "dbscan": `DBSCANClusterer(min_cluster_size=self.config.min_cluster_size)`
5. Fit and predict:
   - Call `clusterer.fit(self.embeddings)`
   - Call `clusterer.predict(self.embeddings)` to get labels
   - Store in `self.cluster_labels`
6. Build cluster dictionary:
   - Create `clusters = {}`
   - For each `(term, label)` pair:
     - If `label not in clusters`: `clusters[label] = []`
     - Append `term` to `clusters[label]`
   - Convert cluster IDs to integers (handle -1 for noise)
7. Evaluate clusters:
   - Create `ClusterEvaluator`
   - Call `evaluate(self.embeddings, self.cluster_labels)`
   - Store in `self.stats`
8. Return clusters dictionary

#### `assign_clusters_to_entries() -> AmiEncyclopedia`
1. Ensure clusters are computed: call `cluster_entries()` if `self.clusters` is empty
2. Create mapping from term to cluster_id:
   - `term_to_cluster = {}`
   - For each `cluster_id, terms` in `self.clusters.items()`:
     - For each `term` in `terms`:
       - `term_to_cluster[term] = cluster_id`
3. Assign cluster_id to entries:
   - For each entry in `self.encyclopedia.entries`:
     - Get `term` from entry
     - If `term in term_to_cluster`:
       - Set `entry['cluster_id'] = term_to_cluster[term]`
     - Else:
       - Set `entry['cluster_id'] = -1` (unclustered)
4. Return `self.encyclopedia`

#### `get_cluster_statistics() -> Dict`
1. Ensure clusters are computed
2. Ensure evaluation is done (call `_evaluate_clusters()` if needed)
3. Return dictionary:
   ```python
   {
       'n_clusters': len(self.clusters),
       'cluster_sizes': {cid: len(terms) for cid, terms in self.clusters.items()},
       'silhouette_score': self.stats.get('silhouette_score'),
       'calinski_harabasz_score': self.stats.get('calinski_harabasz_score'),
       'davies_bouldin_score': self.stats.get('davies_bouldin_score'),
       'cluster_size_distribution': self.stats.get('cluster_size_distribution', {})
   }
   ```

#### `export_cluster_report(output_path: Path) -> None`
1. Get statistics: `stats = self.get_cluster_statistics()`
2. Create simple HTML report:
   - Title: "Cluster Report"
   - Statistics section
   - Cluster details section (list clusters with their terms)
3. Write to `output_path`

#### `_evaluate_clusters(embeddings, labels) -> Dict`
1. Create `ClusterEvaluator`
2. Call `evaluator.evaluate(embeddings, labels)`
3. Return evaluation dictionary

---

## Implementation Order

1. **TextExtractor** (simplest, no external dependencies beyond lxml)
2. **ClusterEvaluator** (uses scikit-learn, straightforward)
3. **ClusterAlgorithm implementations** (KMeans, Agglomerative, DBSCAN)
4. **EmbeddingGenerator** (requires sentence-transformers installation)
5. **AmiEncyclopediaClusterer** (orchestrates everything)

---

## Error Handling

- **Missing dependencies**: Catch `ImportError` and log warnings
- **Empty descriptions**: Skip entries without `description_html`
- **No clusters found**: Return empty dictionary or handle gracefully
- **Model loading failures**: Log error and raise informative exception

---

## Testing Considerations

- Mock sentence-transformers for tests that don't require actual embeddings
- Use small test datasets to avoid long execution times
- Test with both valid and edge cases (empty descriptions, single entry, etc.)

---

## Style Guide Compliance

- Use absolute imports: `from amilib.ami_encyclopedia import AmiEncyclopedia`
- Use `Path` from `pathlib` for file paths
- Use `Resources.TEMP_DIR` for temporary files in tests
- Follow existing amilib patterns for logging and error handling

