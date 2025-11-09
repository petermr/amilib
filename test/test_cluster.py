"""
Tests for AmiEncyclopediaClusterer functionality

Tests clustering of encyclopedia entries based on description text similarity.
Uses TDD approach - tests written before implementation.
"""

import unittest
from pathlib import Path
from typing import Dict, List
import shutil

from amilib.ami_encyclopedia import AmiEncyclopedia
from test.resources import Resources
from test.test_all import AmiAnyTest
from amilib.util import Util

logger = Util.get_logger(__name__)


class ClusterTest(AmiAnyTest):
    """Test clustering functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "ClusterTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_clusterer_initialization(self):
        """Test that AmiEncyclopediaClusterer can be initialized"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        
        assert clusterer is not None, "Clusterer should be created"
        assert clusterer.encyclopedia == encyclopedia, "Clusterer should reference encyclopedia"
        print("✅ Clusterer initialization working")
    
    def test_clusterer_with_config(self):
        """Test that AmiEncyclopediaClusterer can be initialized with configuration"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer, ClusterConfig
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        config = ClusterConfig(
            method="sentence_embeddings",
            n_clusters=5,
            embedding_model="all-MiniLM-L6-v2"
        )
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia, config)
        
        assert clusterer.config == config, "Clusterer should store configuration"
        print("✅ Clusterer initialization with config working")
    
    def test_cluster_entries_basic(self):
        """Test basic clustering of entries"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        clusters = clusterer.cluster_entries()
        
        assert clusters is not None, "Should return clusters"
        assert isinstance(clusters, dict), "Clusters should be a dictionary"
        assert len(clusters) > 0, "Should have at least one cluster"
        
        # Check cluster structure: cluster_id -> list of entry terms
        for cluster_id, terms in clusters.items():
            assert isinstance(cluster_id, int), "Cluster ID should be integer"
            assert isinstance(terms, list), "Cluster should contain list of terms"
            assert len(terms) > 0, "Cluster should have at least one term"
        
        print(f"✅ Created {len(clusters)} clusters")
    
    def test_cluster_entries_with_method(self):
        """Test clustering with different methods"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        
        # Test sentence embeddings method
        clusters_emb = clusterer.cluster_entries(method="sentence_embeddings")
        assert len(clusters_emb) > 0, "Should create clusters with embeddings method"
        
        # Test TF-IDF method (if implemented)
        try:
            clusters_tfidf = clusterer.cluster_entries(method="tfidf")
            assert len(clusters_tfidf) > 0, "Should create clusters with TF-IDF method"
        except NotImplementedError:
            print("⚠️  TF-IDF method not yet implemented")
        
        print("✅ Clustering with different methods working")
    
    def test_assign_clusters_to_entries(self):
        """Test assigning cluster IDs to encyclopedia entries"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        updated_encyclopedia = clusterer.assign_clusters_to_entries()
        
        assert updated_encyclopedia is not None, "Should return updated encyclopedia"
        assert len(updated_encyclopedia.entries) > 0, "Should have entries"
        
        # Check that entries have cluster_id
        entries_with_cluster = [e for e in updated_encyclopedia.entries if 'cluster_id' in e]
        assert len(entries_with_cluster) > 0, "Should have entries with cluster_id"
        
        # Check cluster_id is integer
        for entry in entries_with_cluster:
            assert isinstance(entry['cluster_id'], int), "cluster_id should be integer"
        
        print(f"✅ Assigned clusters to {len(entries_with_cluster)} entries")
    
    def test_get_cluster_statistics(self):
        """Test getting cluster statistics"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        clusterer.cluster_entries()
        stats = clusterer.get_cluster_statistics()
        
        assert stats is not None, "Should return statistics"
        assert isinstance(stats, dict), "Statistics should be a dictionary"
        assert 'n_clusters' in stats, "Should have n_clusters"
        assert 'cluster_sizes' in stats, "Should have cluster_sizes"
        assert 'silhouette_score' in stats, "Should have silhouette_score"
        
        assert stats['n_clusters'] > 0, "Should have at least one cluster"
        assert len(stats['cluster_sizes']) == stats['n_clusters'], "Cluster sizes should match n_clusters"
        
        print(f"✅ Statistics: {stats['n_clusters']} clusters, silhouette={stats.get('silhouette_score', 'N/A')}")
    
    def test_export_cluster_report(self):
        """Test exporting cluster report"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        clusterer.cluster_entries()
        
        output_file = self.temp_dir / "cluster_report.html"
        clusterer.export_cluster_report(output_file)
        
        assert output_file.exists(), "Report file should be created"
        content = output_file.read_text(encoding='utf-8')
        assert len(content) > 0, "Report should not be empty"
        
        print(f"✅ Exported cluster report to {output_file}")


class TextExtractorTest(AmiAnyTest):
    """Test TextExtractor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "TextExtractorTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_text_extractor_initialization(self):
        """Test TextExtractor initialization"""
        from amilib.ami_encyclopedia_cluster import TextExtractor
        
        extractor = TextExtractor()
        assert extractor is not None, "TextExtractor should be created"
        
        extractor_advanced = TextExtractor(preprocessing_level="advanced")
        assert extractor_advanced.preprocessing_level == "advanced", "Should set preprocessing level"
        
        print("✅ TextExtractor initialization working")
    
    def test_extract_text_from_html(self):
        """Test extracting plain text from HTML"""
        from amilib.ami_encyclopedia_cluster import TextExtractor
        
        extractor = TextExtractor()
        
        html = '<p class="wpage_first_para">Climate change is a <b>long-term</b> change in global climate patterns.</p>'
        text = extractor.extract_text(html)
        
        assert text is not None, "Should extract text"
        assert isinstance(text, str), "Should return string"
        assert "Climate change" in text, "Should contain content"
        assert "<b>" not in text, "Should remove HTML tags"
        assert "<p>" not in text, "Should remove HTML tags"
        
        print("✅ HTML to text extraction working")
    
    def test_preprocess_text_basic(self):
        """Test basic text preprocessing"""
        from amilib.ami_encyclopedia_cluster import TextExtractor
        
        extractor = TextExtractor(preprocessing_level="basic")
        
        text = "Climate Change is a LONG-TERM change in Global Climate Patterns."
        processed = extractor.preprocess_text(text)
        
        assert processed is not None, "Should preprocess text"
        assert isinstance(processed, str), "Should return string"
        # Basic preprocessing should lowercase
        assert "climate" in processed.lower(), "Should lowercase text"
        
        print("✅ Basic text preprocessing working")
    
    def test_batch_extract(self):
        """Test batch extraction from multiple entries"""
        from amilib.ami_encyclopedia_cluster import TextExtractor
        
        extractor = TextExtractor()
        
        entries = [
            {'term': 'climate change', 'description_html': '<p>Climate change is a long-term change.</p>'},
            {'term': 'global warming', 'description_html': '<p>Global warming is the increase in temperature.</p>'}
        ]
        
        results = extractor.batch_extract(entries)
        
        assert results is not None, "Should return results"
        assert isinstance(results, list), "Should return list"
        assert len(results) == len(entries), "Should process all entries"
        
        for term, text in results:
            assert isinstance(term, str), "Should return term"
            assert isinstance(text, str), "Should return text"
            assert len(text) > 0, "Text should not be empty"
        
        print(f"✅ Batch extracted {len(results)} entries")


class EmbeddingGeneratorTest(AmiAnyTest):
    """Test EmbeddingGenerator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "EmbeddingGeneratorTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_embedding_generator_initialization(self):
        """Test EmbeddingGenerator initialization"""
        from amilib.ami_encyclopedia_cluster import EmbeddingGenerator
        
        generator = EmbeddingGenerator()
        assert generator is not None, "EmbeddingGenerator should be created"
        
        generator_custom = EmbeddingGenerator(model_name="all-mpnet-base-v2")
        assert generator_custom.model_name == "all-mpnet-base-v2", "Should set model name"
        
        print("✅ EmbeddingGenerator initialization working")
    
    def test_generate_embedding_single(self):
        """Test generating embedding for single text"""
        from amilib.ami_encyclopedia_cluster import EmbeddingGenerator
        
        generator = EmbeddingGenerator()
        text = "Climate change is a long-term change in global climate patterns."
        
        embedding = generator.generate_embedding(text)
        
        assert embedding is not None, "Should generate embedding"
        # Should return numpy array (will be checked when implemented)
        assert hasattr(embedding, 'shape') or isinstance(embedding, list), "Should return array-like"
        
        print("✅ Single text embedding generation working")
    
    def test_generate_embeddings_batch(self):
        """Test generating embeddings for multiple texts"""
        from amilib.ami_encyclopedia_cluster import EmbeddingGenerator
        
        generator = EmbeddingGenerator()
        texts = [
            "Climate change is a long-term change in global climate patterns.",
            "Global warming is the increase in Earth's average surface temperature."
        ]
        
        embeddings = generator.generate_embeddings(texts)
        
        assert embeddings is not None, "Should generate embeddings"
        assert len(embeddings) == len(texts), "Should generate embedding for each text"
        
        print(f"✅ Batch embedding generation working for {len(texts)} texts")
    
    def test_get_model_info(self):
        """Test getting model information"""
        from amilib.ami_encyclopedia_cluster import EmbeddingGenerator
        
        generator = EmbeddingGenerator()
        info = generator.get_model_info()
        
        assert info is not None, "Should return model info"
        assert isinstance(info, dict), "Should return dictionary"
        assert 'model_name' in info, "Should have model_name"
        assert 'dimensions' in info, "Should have dimensions"
        
        print(f"✅ Model info: {info.get('model_name')}, dimensions: {info.get('dimensions')}")


class ClusterAlgorithmTest(AmiAnyTest):
    """Test ClusterAlgorithm implementations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "ClusterAlgorithmTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_kmeans_clusterer(self):
        """Test KMeansClusterer"""
        from amilib.ami_encyclopedia_cluster import KMeansClusterer
        import numpy as np
        
        # Create dummy embeddings (2D for testing)
        embeddings = np.random.rand(10, 5)  # 10 samples, 5 dimensions
        
        clusterer = KMeansClusterer(n_clusters=3)
        clusterer.fit(embeddings)
        labels = clusterer.predict(embeddings)
        
        assert labels is not None, "Should return labels"
        assert len(labels) == len(embeddings), "Should have label for each embedding"
        assert clusterer.get_n_clusters() == 3, "Should have 3 clusters"
        
        print("✅ KMeansClusterer working")
    
    def test_agglomerative_clusterer(self):
        """Test AgglomerativeClusterer"""
        from amilib.ami_encyclopedia_cluster import AgglomerativeClusterer
        import numpy as np
        
        embeddings = np.random.rand(10, 5)
        
        clusterer = AgglomerativeClusterer(n_clusters=3)
        clusterer.fit(embeddings)
        labels = clusterer.predict(embeddings)
        
        assert labels is not None, "Should return labels"
        assert len(labels) == len(embeddings), "Should have label for each embedding"
        
        print("✅ AgglomerativeClusterer working")
    
    def test_dbscan_clusterer(self):
        """Test DBSCANClusterer"""
        from amilib.ami_encyclopedia_cluster import DBSCANClusterer
        import numpy as np
        
        embeddings = np.random.rand(10, 5)
        
        clusterer = DBSCANClusterer(min_cluster_size=2)
        clusterer.fit(embeddings)
        labels = clusterer.predict(embeddings)
        
        assert labels is not None, "Should return labels"
        assert len(labels) == len(embeddings), "Should have label for each embedding"
        # DBSCAN may have -1 for noise points
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        assert n_clusters >= 0, "Should have valid number of clusters"
        
        print(f"✅ DBSCANClusterer working, found {n_clusters} clusters")


class ClusterEvaluatorTest(AmiAnyTest):
    """Test ClusterEvaluator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "ClusterEvaluatorTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_cluster_evaluator_initialization(self):
        """Test ClusterEvaluator initialization"""
        from amilib.ami_encyclopedia_cluster import ClusterEvaluator
        
        evaluator = ClusterEvaluator()
        assert evaluator is not None, "ClusterEvaluator should be created"
        
        print("✅ ClusterEvaluator initialization working")
    
    def test_evaluate_clusters(self):
        """Test cluster evaluation"""
        from amilib.ami_encyclopedia_cluster import ClusterEvaluator
        import numpy as np
        
        evaluator = ClusterEvaluator()
        
        # Create dummy data
        embeddings = np.random.rand(20, 5)  # 20 samples, 5 dimensions
        labels = np.random.randint(0, 3, 20)  # 3 clusters
        
        results = evaluator.evaluate(embeddings, labels)
        
        assert results is not None, "Should return evaluation results"
        assert isinstance(results, dict), "Should return dictionary"
        assert 'silhouette_score' in results, "Should have silhouette_score"
        assert 'calinski_harabasz_score' in results, "Should have calinski_harabasz_score"
        assert 'davies_bouldin_score' in results, "Should have davies_bouldin_score"
        
        print(f"✅ Cluster evaluation: silhouette={results.get('silhouette_score', 'N/A')}")
    
    def test_silhouette_score(self):
        """Test silhouette score calculation"""
        from amilib.ami_encyclopedia_cluster import ClusterEvaluator
        import numpy as np
        
        evaluator = ClusterEvaluator()
        embeddings = np.random.rand(20, 5)
        labels = np.random.randint(0, 3, 20)
        
        score = evaluator.silhouette_score(embeddings, labels)
        
        assert score is not None, "Should return score"
        assert isinstance(score, (int, float)), "Should return number"
        assert -1 <= score <= 1, "Silhouette score should be between -1 and 1"
        
        print(f"✅ Silhouette score: {score:.3f}")
    
    def test_cluster_size_distribution(self):
        """Test cluster size distribution analysis"""
        from amilib.ami_encyclopedia_cluster import ClusterEvaluator
        import numpy as np
        
        evaluator = ClusterEvaluator()
        labels = np.array([0, 0, 1, 1, 1, 2, 2])
        
        distribution = evaluator.cluster_size_distribution(labels)
        
        assert distribution is not None, "Should return distribution"
        assert isinstance(distribution, dict), "Should return dictionary"
        assert len(distribution) == 3, "Should have 3 clusters"
        
        print(f"✅ Cluster size distribution: {distribution}")


class ClusterIntegrationTest(AmiAnyTest):
    """Integration tests for clustering workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "cluster", "ClusterIntegrationTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_clustering_workflow(self):
        """Test complete clustering workflow"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer
        
        # Create encyclopedia
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Cluster entries
        clusterer = AmiEncyclopediaClusterer(encyclopedia)
        clusters = clusterer.cluster_entries()
        
        # Assign clusters to entries
        updated_encyclopedia = clusterer.assign_clusters_to_entries()
        
        # Get statistics
        stats = clusterer.get_cluster_statistics()
        
        # Export report
        report_file = self.temp_dir / "cluster_report.html"
        clusterer.export_cluster_report(report_file)
        
        # Verify results
        assert len(clusters) > 0, "Should have clusters"
        assert len(updated_encyclopedia.entries) > 0, "Should have entries"
        assert stats['n_clusters'] > 0, "Should have cluster statistics"
        assert report_file.exists(), "Should export report"
        
        print(f"✅ Full workflow: {stats['n_clusters']} clusters, {len(updated_encyclopedia.entries)} entries")
    
    def test_clustering_with_different_n_clusters(self):
        """Test clustering with different numbers of clusters"""
        from amilib.ami_encyclopedia_cluster import AmiEncyclopediaClusterer, ClusterConfig
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Test with 3 clusters
        config_3 = ClusterConfig(n_clusters=3)
        clusterer_3 = AmiEncyclopediaClusterer(encyclopedia, config_3)
        clusters_3 = clusterer_3.cluster_entries()
        stats_3 = clusterer_3.get_cluster_statistics()
        
        # Test with 5 clusters
        config_5 = ClusterConfig(n_clusters=5)
        clusterer_5 = AmiEncyclopediaClusterer(encyclopedia, config_5)
        clusters_5 = clusterer_5.cluster_entries()
        stats_5 = clusterer_5.get_cluster_statistics()
        
        assert stats_3['n_clusters'] == 3, "Should have 3 clusters"
        assert stats_5['n_clusters'] == 5, "Should have 5 clusters"
        
        print(f"✅ Clustering with different n_clusters: 3={stats_3['n_clusters']}, 5={stats_5['n_clusters']}")


if __name__ == '__main__':
    unittest.main()

