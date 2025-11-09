"""
AmiEncyclopediaClusterer - Clustering encyclopedia entries by description similarity

Based on work by Shaik Zainab (2015).
Provides functionality to:
- Extract text from HTML descriptions
- Generate sentence embeddings
- Cluster entries by similarity
- Evaluate clustering quality
- Assign cluster IDs to entries
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

import matplotlib
# Configure matplotlib to run in headless mode
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import cm

from lxml.html import fromstring

from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.util import Util

logger = Util.get_logger(__name__)


@dataclass
class ClusterConfig:
    """Configuration for clustering parameters"""
    method: str = "sentence_embeddings"  # "sentence_embeddings", "tfidf", "hybrid"
    embedding_model: str = "all-MiniLM-L6-v2"  # Model name for sentence-transformers
    clustering_algorithm: str = "kmeans"  # "kmeans", "agglomerative", "dbscan", "hdbscan"
    n_clusters: Optional[int] = None  # Number of clusters (None for auto)
    distance_metric: str = "cosine"  # "cosine", "euclidean"
    preprocessing_level: str = "basic"  # "basic", "advanced"
    min_cluster_size: int = 2  # For DBSCAN/HDBSCAN
    random_state: int = 42  # For reproducibility


class TextExtractor:
    """Utility class for extracting and preprocessing text from HTML descriptions"""
    
    def __init__(self, preprocessing_level: str = "basic"):
        """
        Initialize with preprocessing configuration
        
        Args:
            preprocessing_level: "basic" or "advanced"
        """
        self.preprocessing_level = preprocessing_level
    
    def extract_text(self, description_html: str) -> str:
        """
        Convert HTML to plain text, strip tags
        
        Args:
            description_html: HTML string containing description
            
        Returns:
            Plain text string
        """
        if not description_html:
            return ""
        plain_text = self._strip_html_tags(description_html)
        return self._normalize_whitespace(plain_text)
    
    def preprocess_text(self, text: str) -> str:
        """
        Apply preprocessing (lowercase, stopwords, lemmatization)
        
        Args:
            text: Plain text string
            
        Returns:
            Preprocessed text string
        """
        if not text:
            return ""
        # Convert to lowercase
        processed = text.lower()
        # Normalize whitespace
        processed = self._normalize_whitespace(processed)
        # Apply advanced preprocessing if enabled
        if self.preprocessing_level == "advanced":
            processed = self._apply_advanced_preprocessing(processed)
        return processed
    
    def batch_extract(self, entries: List[Dict]) -> List[Tuple[str, str]]:
        """
        Extract text from multiple entries efficiently
        
        Args:
            entries: List of entry dictionaries with 'term' and 'description_html'
            
        Returns:
            List of (term, text) tuples
        """
        results = []
        for entry in entries:
            term = entry.get('term', '')
            description_html = entry.get('description_html', '')
            if description_html:
                text = self.extract_text(description_html)
                if text:
                    results.append((term, text))
        return results
    
    def _strip_html_tags(self, html: str) -> str:
        """Remove HTML tags using lxml"""
        try:
            element = fromstring(html)
            return element.text_content()
        except Exception as e:
            logger.warning(f"Failed to parse HTML: {e}")
            # Fallback: simple regex-based tag removal
            text = re.sub(r'<[^>]+>', '', html)
            return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Clean up whitespace"""
        if not text:
            return ""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        return text.strip()
    
    def _apply_advanced_preprocessing(self, text: str) -> str:
        """Optional: lemmatization, POS tagging (if enabled)"""
        # For now, return text as-is
        # Future: can add NLTK/spaCy lemmatization here
        return text


class EmbeddingGenerator:
    """Generate sentence embeddings from text descriptions"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with sentence transformer model
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        self.dimensions = None
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            numpy array of embeddings (n_samples, n_dimensions)
        """
        if not texts:
            return np.array([])
        self._load_model()
        if self.model is None:
            raise ImportError("sentence-transformers is required for embedding generation")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return np.array(embeddings)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text
        
        Args:
            text: Text string
            
        Returns:
            numpy array of embedding (n_dimensions,)
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0]
    
    def get_model_info(self) -> Dict:
        """
        Return model metadata (dimensions, name, etc.)
        
        Returns:
            Dictionary with model information
        """
        self._load_model()
        return {
            'model_name': self.model_name,
            'dimensions': self.dimensions,
            'loaded': self.model is not None
        }
    
    def _load_model(self) -> None:
        """Lazy load the sentence transformer model"""
        if self.model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.dimensions = self.model.get_sentence_embedding_dimension()
        except ImportError:
            logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
            self.model = None
            self.dimensions = None
        except Exception as e:
            logger.warning(f"Error loading sentence transformer model: {e}")
            self.model = None
            self.dimensions = None
    
    def _batch_encode(self, texts: List[str]) -> np.ndarray:
        """Efficient batch encoding"""
        return self.generate_embeddings(texts)


class ClusterAlgorithm:
    """Abstract base class for clustering algorithms"""
    
    def __init__(self, n_clusters: Optional[int] = None, **kwargs):
        """
        Initialize with clustering parameters
        
        Args:
            n_clusters: Number of clusters (None for auto)
            **kwargs: Additional algorithm-specific parameters
        """
        self.n_clusters = n_clusters
        self.model = None
        self.labels_ = None
    
    def fit(self, embeddings: np.ndarray) -> None:
        """
        Fit the clustering model
        
        Args:
            embeddings: numpy array of embeddings (n_samples, n_dimensions)
        """
        raise NotImplementedError("ClusterAlgorithm.fit not yet implemented")
    
    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels
        
        Args:
            embeddings: numpy array of embeddings (n_samples, n_dimensions)
            
        Returns:
            numpy array of cluster labels (n_samples,)
        """
        raise NotImplementedError("ClusterAlgorithm.predict not yet implemented")
    
    def get_cluster_labels(self) -> np.ndarray:
        """
        Get cluster assignments
        
        Returns:
            numpy array of cluster labels (n_samples,)
        """
        raise NotImplementedError("ClusterAlgorithm.get_cluster_labels not yet implemented")
    
    def get_n_clusters(self) -> int:
        """
        Get number of clusters (auto-determined or specified)
        
        Returns:
            Number of clusters
        """
        raise NotImplementedError("ClusterAlgorithm.get_n_clusters not yet implemented")


class KMeansClusterer(ClusterAlgorithm):
    """K-means clustering with optional elbow method"""
    
    def __init__(self, n_clusters: Optional[int] = None, **kwargs):
        super().__init__(n_clusters=n_clusters, **kwargs)
        self.random_state = kwargs.get('random_state', 42)
    
    def fit(self, embeddings: np.ndarray) -> None:
        """Fit the KMeans model"""
        try:
            from sklearn.cluster import KMeans
            if self.n_clusters is None:
                # Default to 3 if not specified
                self.n_clusters = 3
            self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
            self.model.fit(embeddings)
        except ImportError:
            raise ImportError("scikit-learn is required for KMeans clustering")
    
    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """Predict cluster labels"""
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        self.labels_ = self.model.predict(embeddings)
        return self.labels_
    
    def get_cluster_labels(self) -> np.ndarray:
        """Get cluster labels"""
        if self.labels_ is None:
            raise ValueError("Labels not available. Call fit() and predict() first.")
        return self.labels_
    
    def get_n_clusters(self) -> int:
        """Get number of clusters"""
        if self.n_clusters is not None:
            return self.n_clusters
        if self.labels_ is not None:
            return len(set(self.labels_))
        return 0


class AgglomerativeClusterer(ClusterAlgorithm):
    """Hierarchical clustering with linkage options"""
    
    def __init__(self, n_clusters: Optional[int] = None, **kwargs):
        super().__init__(n_clusters=n_clusters, **kwargs)
        self.linkage = kwargs.get('linkage', 'ward')
    
    def fit(self, embeddings: np.ndarray) -> None:
        """Fit the AgglomerativeClustering model"""
        try:
            from sklearn.cluster import AgglomerativeClustering
            if self.n_clusters is None:
                # Default to 3 if not specified
                self.n_clusters = 3
            self.model = AgglomerativeClustering(n_clusters=self.n_clusters, linkage=self.linkage)
            # AgglomerativeClustering uses fit_predict, not separate fit/predict
            self.labels_ = self.model.fit_predict(embeddings)
        except ImportError:
            raise ImportError("scikit-learn is required for AgglomerativeClustering")
    
    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """Predict cluster labels (returns labels from fit)"""
        if self.labels_ is None:
            raise ValueError("Model must be fitted before prediction")
        # AgglomerativeClustering doesn't support new predictions, return existing labels
        return self.labels_
    
    def get_cluster_labels(self) -> np.ndarray:
        """Get cluster labels"""
        if self.labels_ is None:
            raise ValueError("Labels not available. Call fit() first.")
        return self.labels_
    
    def get_n_clusters(self) -> int:
        """Get number of clusters"""
        if self.n_clusters is not None:
            return self.n_clusters
        if self.labels_ is not None:
            return len(set(self.labels_))
        return 0


class DBSCANClusterer(ClusterAlgorithm):
    """Density-based clustering (no n_clusters needed)"""
    
    def __init__(self, min_cluster_size: int = 2, **kwargs):
        super().__init__(n_clusters=None, **kwargs)
        self.min_cluster_size = min_cluster_size
        self.eps = kwargs.get('eps', 0.5)
    
    def fit(self, embeddings: np.ndarray) -> None:
        """Fit the DBSCAN model"""
        try:
            from sklearn.cluster import DBSCAN
            self.model = DBSCAN(min_samples=self.min_cluster_size, eps=self.eps)
            # DBSCAN uses fit_predict, not separate fit/predict
            self.labels_ = self.model.fit_predict(embeddings)
        except ImportError:
            raise ImportError("scikit-learn is required for DBSCAN clustering")
    
    def predict(self, embeddings: np.ndarray) -> np.ndarray:
        """Predict cluster labels (returns labels from fit)"""
        if self.labels_ is None:
            raise ValueError("Model must be fitted before prediction")
        # DBSCAN doesn't support new predictions, return existing labels
        return self.labels_
    
    def get_cluster_labels(self) -> np.ndarray:
        """Get cluster labels"""
        if self.labels_ is None:
            raise ValueError("Labels not available. Call fit() first.")
        return self.labels_
    
    def get_n_clusters(self) -> int:
        """Get number of clusters (excluding noise points)"""
        if self.labels_ is not None:
            unique_labels = set(self.labels_)
            # Exclude -1 (noise points)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
            return n_clusters
        return 0


class ClusterEvaluator:
    """Evaluate clustering quality"""
    
    def __init__(self):
        """Initialize evaluator"""
        pass
    
    def evaluate(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict:
        """
        Calculate multiple evaluation metrics
        
        Args:
            embeddings: numpy array of embeddings (n_samples, n_dimensions)
            labels: numpy array of cluster labels (n_samples,)
            
        Returns:
            Dictionary with evaluation metrics
        """
        return {
            'silhouette_score': self.silhouette_score(embeddings, labels),
            'calinski_harabasz_score': self.calinski_harabasz_score(embeddings, labels),
            'davies_bouldin_score': self.davies_bouldin_score(embeddings, labels),
            'cluster_size_distribution': self.cluster_size_distribution(labels)
        }
    
    def silhouette_score(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """
        Calculate silhouette coefficient
        
        Args:
            embeddings: numpy array of embeddings
            labels: numpy array of cluster labels
            
        Returns:
            Silhouette score (between -1 and 1)
        """
        try:
            from sklearn.metrics import silhouette_score
            # Use cosine distance for embeddings
            return float(silhouette_score(embeddings, labels, metric='cosine'))
        except ImportError:
            logger.warning("scikit-learn not available for silhouette_score")
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating silhouette score: {e}")
            return 0.0
    
    def calinski_harabasz_score(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """
        Calculate Calinski-Harabasz index
        
        Args:
            embeddings: numpy array of embeddings
            labels: numpy array of cluster labels
            
        Returns:
            Calinski-Harabasz score
        """
        try:
            from sklearn.metrics import calinski_harabasz_score
            return float(calinski_harabasz_score(embeddings, labels))
        except ImportError:
            logger.warning("scikit-learn not available for calinski_harabasz_score")
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating Calinski-Harabasz score: {e}")
            return 0.0
    
    def davies_bouldin_score(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """
        Calculate Davies-Bouldin index
        
        Args:
            embeddings: numpy array of embeddings
            labels: numpy array of cluster labels
            
        Returns:
            Davies-Bouldin score
        """
        try:
            from sklearn.metrics import davies_bouldin_score
            return float(davies_bouldin_score(embeddings, labels))
        except ImportError:
            logger.warning("scikit-learn not available for davies_bouldin_score")
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating Davies-Bouldin score: {e}")
            return 0.0
    
    def cluster_size_distribution(self, labels: np.ndarray) -> Dict:
        """
        Analyze cluster size distribution
        
        Args:
            labels: numpy array of cluster labels
            
        Returns:
            Dictionary mapping cluster_id to size
        """
        unique_labels, counts = np.unique(labels, return_counts=True)
        distribution = {}
        for label, count in zip(unique_labels, counts):
            # Exclude noise points (-1) from distribution
            if label != -1:
                distribution[int(label)] = int(count)
        return distribution


class AmiEncyclopediaClusterer:
    """
    Main orchestrator class for clustering encyclopedia entries based on description similarity.
    
    Based on work by Shaik Zainab (2015).
    """
    
    def __init__(self, encyclopedia: AmiEncyclopedia, config: Optional[ClusterConfig] = None):
        """
        Initialize with encyclopedia and optional configuration
        
        Args:
            encyclopedia: AmiEncyclopedia instance with entries
            config: Optional ClusterConfig (uses defaults if None)
        """
        self.encyclopedia = encyclopedia
        self.config = config or ClusterConfig()
        self.clusters = {}  # Dict[int, List[str]] - cluster_id -> list of entry terms
        self.cluster_labels = None  # numpy array of cluster labels
        self.embeddings = None  # numpy array of embeddings
        self.texts = []  # List of extracted texts
        self.terms = []  # List of terms matching embeddings order
        self.stats = {}  # Dictionary of cluster statistics
    
    def cluster_entries(self, method: Optional[str] = None, visualize: bool = True) -> Dict[int, List[str]]:
        """
        Main clustering method, returns cluster_id -> list of entry terms
        
        Args:
            method: Optional method override ("sentence_embeddings", "tfidf")
            visualize: If True, automatically create 2D visualization (default: True)
            
        Returns:
            Dictionary mapping cluster_id to list of entry terms
        """
        clustering_method = method or self.config.method
        
        if clustering_method == "sentence_embeddings":
            self.clusters = self._cluster_with_embeddings()
        elif clustering_method == "tfidf":
            self.clusters = self._cluster_with_tfidf()
        else:
            raise ValueError(f"Unknown clustering method: {clustering_method}")
        
        # Automatically create visualization if clusters were created
        if visualize and self.clusters and len(self.clusters) > 0:
            try:
                self.visualize_clusters()
            except Exception as e:
                logger.warning(f"Failed to create cluster visualization: {e}")
        
        return self.clusters
    
    def assign_clusters_to_entries(self) -> AmiEncyclopedia:
        """
        Assigns cluster_id to each entry in the encyclopedia
        
        Returns:
            Updated AmiEncyclopedia with cluster_id in each entry
        """
        # Ensure clusters are computed
        if not self.clusters:
            self.cluster_entries()
        
        # Create mapping from term to cluster_id
        term_to_cluster = {}
        for cluster_id, terms in self.clusters.items():
            for term in terms:
                term_to_cluster[term] = cluster_id
        
        # Assign cluster_id to entries
        for entry in self.encyclopedia.entries:
            term = entry.get('term', '')
            if term in term_to_cluster:
                entry['cluster_id'] = term_to_cluster[term]
            else:
                entry['cluster_id'] = -1  # Unclustered
        
        return self.encyclopedia
    
    def get_cluster_statistics(self) -> Dict:
        """
        Returns statistics about clusters (sizes, silhouette score, etc.)
        
        Returns:
            Dictionary with cluster statistics
        """
        # Ensure clusters are computed
        if not self.clusters:
            self.cluster_entries()
        
        # Ensure evaluation is done
        if not self.stats and self.embeddings is not None and self.cluster_labels is not None:
            self.stats = self._evaluate_clusters(self.embeddings, self.cluster_labels)
        
        # Build cluster sizes dictionary
        cluster_sizes = {}
        for cluster_id, terms in self.clusters.items():
            cluster_sizes[cluster_id] = len(terms)
        
        return {
            'n_clusters': len(self.clusters),
            'cluster_sizes': cluster_sizes,
            'silhouette_score': self.stats.get('silhouette_score'),
            'calinski_harabasz_score': self.stats.get('calinski_harabasz_score'),
            'davies_bouldin_score': self.stats.get('davies_bouldin_score'),
            'cluster_size_distribution': self.stats.get('cluster_size_distribution', {})
        }
    
    def export_cluster_report(self, output_path: Path) -> None:
        """
        Exports clustering results to HTML/JSON report
        
        Args:
            output_path: Path to output file
        """
        stats = self.get_cluster_statistics()
        
        # Create simple HTML report
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Cluster Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .cluster {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .cluster-id {{ font-weight: bold; color: #0066cc; }}
        .terms {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <h1>Cluster Report</h1>
    <div class="stats">
        <h2>Statistics</h2>
        <p><strong>Number of clusters:</strong> {stats['n_clusters']}</p>
        <p><strong>Silhouette score:</strong> {stats.get('silhouette_score', 'N/A')}</p>
        <p><strong>Calinski-Harabasz score:</strong> {stats.get('calinski_harabasz_score', 'N/A')}</p>
        <p><strong>Davies-Bouldin score:</strong> {stats.get('davies_bouldin_score', 'N/A')}</p>
    </div>
    <h2>Clusters</h2>
"""
        
        for cluster_id, terms in sorted(self.clusters.items()):
            html_content += f"""
    <div class="cluster">
        <div class="cluster-id">Cluster {cluster_id} ({len(terms)} entries)</div>
        <div class="terms">
            <ul>
"""
            for term in terms:
                html_content += f"                <li>{term}</li>\n"
            html_content += """            </ul>
        </div>
    </div>
"""
        
        html_content += """</body>
</html>"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
    
    def _extract_descriptions(self) -> List[Tuple[str, str]]:
        """
        Extract (term, description_html) pairs from entries
        
        Returns:
            List of (term, description_html) tuples
        """
        descriptions = []
        for entry in self.encyclopedia.entries:
            term = entry.get('term', '')
            description_html = entry.get('description_html', '')
            if description_html:
                descriptions.append((term, description_html))
        return descriptions
    
    def _cluster_with_embeddings(self) -> Dict[int, List[str]]:
        """
        Clustering using sentence embeddings
        
        Returns:
            Dictionary mapping cluster_id to list of entry terms
        """
        # Extract descriptions
        descriptions = self._extract_descriptions()
        if not descriptions:
            logger.warning("No descriptions found in encyclopedia entries")
            return {}
        
        # Extract texts
        extractor = TextExtractor(preprocessing_level=self.config.preprocessing_level)
        texts = []
        terms = []
        for term, html in descriptions:
            text = extractor.extract_text(html)
            if text:
                texts.append(text)
                terms.append(term)
        
        if not texts:
            logger.warning("No text extracted from descriptions")
            return {}
        
        # Generate embeddings
        generator = EmbeddingGenerator(model_name=self.config.embedding_model)
        embeddings = generator.generate_embeddings(texts)
        self.embeddings = embeddings
        self.texts = texts
        self.terms = terms  # Store terms in same order as embeddings
        
        # Create clustering algorithm
        if self.config.clustering_algorithm == "kmeans":
            clusterer = KMeansClusterer(
                n_clusters=self.config.n_clusters or 3,
                random_state=self.config.random_state
            )
        elif self.config.clustering_algorithm == "agglomerative":
            clusterer = AgglomerativeClusterer(n_clusters=self.config.n_clusters or 3)
        elif self.config.clustering_algorithm == "dbscan":
            clusterer = DBSCANClusterer(min_cluster_size=self.config.min_cluster_size)
        else:
            raise ValueError(f"Unknown clustering algorithm: {self.config.clustering_algorithm}")
        
        # Fit and predict
        clusterer.fit(embeddings)
        labels = clusterer.predict(embeddings)
        self.cluster_labels = labels
        
        # Build cluster dictionary
        clusters = {}
        for term, label in zip(terms, labels):
            # Convert label to integer (handle -1 for noise)
            cluster_id = int(label)
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(term)
        
        # Evaluate clusters
        self.stats = self._evaluate_clusters(embeddings, labels)
        
        return clusters
    
    def _cluster_with_tfidf(self) -> Dict[int, List[str]]:
        """
        Clustering using TF-IDF (alternative method)
        
        Returns:
            Dictionary mapping cluster_id to list of entry terms
        """
        # For now, raise NotImplementedError
        # Can be implemented later if needed
        raise NotImplementedError("TF-IDF clustering not yet implemented")
    
    def _evaluate_clusters(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict:
        """
        Calculate clustering quality metrics
        
        Args:
            embeddings: numpy array of embeddings
            labels: numpy array of cluster labels
            
        Returns:
            Dictionary with evaluation metrics
        """
        evaluator = ClusterEvaluator()
        return evaluator.evaluate(embeddings, labels)
    
    def visualize_clusters(self, output_path: Optional[Path] = None, method: str = "pca") -> Path:
        """
        Create a 2D visualization of clusters with labeled nodes
        
        Args:
            output_path: Optional path to save SVG file (defaults to temp/cluster_visualization.svg)
            method: Dimensionality reduction method ("pca" or "tsne")
            
        Returns:
            Path to saved SVG file
        """
        # Ensure clusters are computed
        if not self.clusters or self.embeddings is None or self.cluster_labels is None:
            self.cluster_entries()
        
        if self.embeddings is None or len(self.embeddings) == 0:
            logger.warning("No embeddings available for visualization")
            raise ValueError("No embeddings available. Run cluster_entries() first.")
        
        # Use stored terms list (matches embeddings order)
        if self.terms and len(self.terms) == len(self.embeddings):
            terms = self.terms
        else:
            # Fallback: reconstruct terms list to match embeddings
            descriptions = self._extract_descriptions()
            extractor = TextExtractor(preprocessing_level=self.config.preprocessing_level)
            terms = []
            for term, html in descriptions:
                text = extractor.extract_text(html)
                if text:  # Only include terms that have text (same filter as in _cluster_with_embeddings)
                    terms.append(term)
            
            if len(terms) != len(self.embeddings):
                logger.warning(f"Terms count ({len(terms)}) doesn't match embeddings count ({len(self.embeddings)})")
                # Use cluster mapping to get terms
                terms = []
                for cluster_id, cluster_terms in self.clusters.items():
                    terms.extend(cluster_terms)
                # Remove duplicates while preserving order
                seen = set()
                terms = [t for t in terms if not (t in seen or seen.add(t))]
        
        # Reduce to 2D
        if method == "pca":
            try:
                from sklearn.decomposition import PCA
                reducer = PCA(n_components=2, random_state=self.config.random_state)
                coords_2d = reducer.fit_transform(self.embeddings)
            except ImportError:
                raise ImportError("scikit-learn is required for PCA dimensionality reduction")
        elif method == "tsne":
            try:
                from sklearn.manifold import TSNE
                perplexity = min(30, len(self.embeddings) - 1)
                if perplexity < 1:
                    perplexity = 1
                reducer = TSNE(n_components=2, random_state=self.config.random_state, perplexity=perplexity)
                coords_2d = reducer.fit_transform(self.embeddings)
            except ImportError:
                raise ImportError("scikit-learn is required for t-SNE dimensionality reduction")
        else:
            raise ValueError(f"Unknown reduction method: {method}. Use 'pca' or 'tsne'")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # Get unique cluster labels (excluding noise -1)
        unique_labels = sorted([l for l in set(self.cluster_labels) if l != -1])
        
        # Generate colors for clusters
        n_clusters = len(unique_labels)
        if n_clusters > 0:
            colormap = cm.get_cmap('tab20', n_clusters) if n_clusters <= 20 else cm.get_cmap('tab20')
        else:
            colormap = cm.get_cmap('tab20')
        
        # Plot each cluster
        for i, cluster_id in enumerate(unique_labels):
            mask = self.cluster_labels == cluster_id
            cluster_coords = coords_2d[mask]
            cluster_terms = [terms[j] for j in range(len(terms)) if j < len(mask) and mask[j]]
            
            if len(cluster_coords) == 0:
                continue
                
            color = colormap(i / max(1, n_clusters - 1)) if n_clusters > 1 else colormap(0)
            ax.scatter(cluster_coords[:, 0], cluster_coords[:, 1], 
                      c=[color], label=f'Cluster {cluster_id}', 
                      s=100, alpha=0.6, edgecolors='black', linewidths=0.5)
            
            # Add labels for each point
            for coord, term in zip(cluster_coords, cluster_terms):
                ax.annotate(term, (coord[0], coord[1]), 
                           fontsize=8, alpha=0.7,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none'))
        
        # Plot noise points if any
        if -1 in self.cluster_labels:
            noise_mask = self.cluster_labels == -1
            noise_coords = coords_2d[noise_mask]
            noise_terms = [terms[j] for j in range(len(terms)) if j < len(noise_mask) and noise_mask[j]]
            
            if len(noise_coords) > 0:
                ax.scatter(noise_coords[:, 0], noise_coords[:, 1], 
                          c='gray', label='Noise', 
                          s=50, alpha=0.4, marker='x', edgecolors='black', linewidths=0.5)
                
                for coord, term in zip(noise_coords, noise_terms):
                    ax.annotate(term, (coord[0], coord[1]), 
                               fontsize=7, alpha=0.5, style='italic',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.5, edgecolor='none'))
        
        # Set labels and title
        ax.set_xlabel(f'{method.upper()} Component 1', fontsize=12)
        ax.set_ylabel(f'{method.upper()} Component 2', fontsize=12)
        ax.set_title(f'Cluster Visualization ({method.upper()}) - {self.encyclopedia.title}', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Save to SVG
        if output_path is None:
            from test.resources import Resources
            output_path = Path(Resources.TEMP_DIR, "cluster_visualization.svg")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=150)
        plt.close(fig)
        
        logger.info(f"Cluster visualization saved to: {output_path}")
        return output_path

