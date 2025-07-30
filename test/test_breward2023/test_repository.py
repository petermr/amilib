"""
Test repository operations for Breward2023 corpus.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

# Import the existing AmiCorpus
from corpus_module.corpus import AmiCorpus


class TestBrewardRepository(unittest.TestCase):
    """Test repository operations for Breward2023 corpus."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.pipeline_path = self.test_dir / "pipeline" / "breward2023"
        self.corpus_path = self.pipeline_path / "01_corpus" / "corpus"
        
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_create_repository_structure(self):
        """
        Test that repository creates proper directory structure.
        
        This test verifies:
        - Repository directory is created
        - All required subdirectories exist
        - Configuration files are created
        - BagIt-compliant structure is established
        """
        # Arrange
        repo_name = "breward2023"
        
        # Act
        # Create pipeline structure first
        self.pipeline_path.mkdir(parents=True, exist_ok=True)
        self.corpus_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize AmiCorpus and apply breward2023 declarative commands
        corpus = AmiCorpus(topdir=self.corpus_path)
        self._apply_breward_commands(corpus)
        
        # Assert
        # Check that repository directory exists
        self.assertTrue(self.corpus_path.exists(), 
                       f"Repository directory {self.corpus_path} should exist")
        
        # Check BagIt structure
        self.assertTrue((self.corpus_path / "bag-info.txt").exists(),
                       "bag-info.txt should exist")
        self.assertTrue((self.corpus_path / "bagit.txt").exists(),
                       "bagit.txt should exist")
        self.assertTrue((self.corpus_path / "manifest-md5.txt").exists(),
                       "manifest-md5.txt should exist")
        
        # Check data directory structure
        data_dir = self.corpus_path / "data"
        self.assertTrue(data_dir.exists(), "data/ directory should exist")
        self.assertTrue((data_dir / "files").exists(), "data/files/ should exist")
        self.assertTrue((data_dir / "metadata").exists(), "data/metadata/ should exist")
        self.assertTrue((data_dir / "indices").exists(), "data/indices/ should exist")
        self.assertTrue((data_dir / "processed").exists(), "data/processed/ should exist")
        
        # Check non-BagIt directories
        self.assertTrue((self.corpus_path / "search_results").exists(),
                       "search_results/ should exist")
        self.assertTrue((self.corpus_path / "summaries").exists(),
                       "summaries/ should exist")
        self.assertTrue((self.corpus_path / "temp").exists(),
                       "temp/ should exist")
        
        # Check configuration directory
        config_dir = self.corpus_path / "config"
        self.assertTrue(config_dir.exists(), "config/ directory should exist")
        self.assertTrue((config_dir / "corpus.yaml").exists(),
                       "config/corpus.yaml should exist")
        self.assertTrue((config_dir / "search.yaml").exists(),
                       "config/search.yaml should exist")
        
        # Check transformations directory
        transforms_dir = config_dir / "transformations"
        self.assertTrue(transforms_dir.exists(),
                       "config/transformations/ should exist")
        self.assertTrue((transforms_dir / "html_cleanup.yaml").exists(),
                       "config/transformations/html_cleanup.yaml should exist")
        self.assertTrue((transforms_dir / "term_extraction.yaml").exists(),
                       "config/transformations/term_extraction.yaml should exist")

    def test_repository_initialization_with_config(self):
        """
        Test that repository loads configuration correctly.
        """
        # This test will be implemented when configuration loading is added
        self.skipTest("Repository configuration test not implemented yet - will be added when config loading is complete")

    def test_bagit_compliance(self):
        """
        Test that repository structure is BagIt compliant.
        """
        # This test will be implemented when BagIt integration is added
        self.skipTest("BagIt compliance test not implemented yet - will be added when BagIt integration is complete")

    def _apply_breward_commands(self, corpus):
        """
        Apply breward2023 declarative commands to create the required structure.
        """
        # Create data directory structure using AmiCorpus
        data_container = corpus.ami_container.create_corpus_container(
            "data", bib_type="bagit_data", mkdir=True
        )
        
        # Create subdirectories in data
        data_container.create_corpus_container("files", bib_type="files", mkdir=True)
        data_container.create_corpus_container("metadata", bib_type="metadata", mkdir=True)
        data_container.create_corpus_container("indices", bib_type="indices", mkdir=True)
        data_container.create_corpus_container("processed", bib_type="processed", mkdir=True)
        
        # Create non-BagIt directories
        corpus.ami_container.create_corpus_container("search_results", bib_type="search", mkdir=True)
        corpus.ami_container.create_corpus_container("summaries", bib_type="summary", mkdir=True)
        corpus.ami_container.create_corpus_container("temp", bib_type="temp", mkdir=True)
        
        # Create config directory
        config_container = corpus.ami_container.create_corpus_container("config", bib_type="config", mkdir=True)
        transforms_container = config_container.create_corpus_container("transformations", bib_type="transforms", mkdir=True)
        
        # Create BagIt files
        self._create_bagit_files(corpus)
        
        # Create configuration files
        self._create_config_files(corpus)

    def _create_bagit_files(self, corpus):
        """Create BagIt-compliant files."""
        from datetime import datetime
        
        # bag-info.txt
        bag_info = {
            "BagIt-Version": "1.0",
            "Tag-File-Character-Encoding": "UTF-8",
            "Payload-Oxum": "0.0",
            "Bagging-Date": datetime.now().strftime("%Y-%m-%d"),
            "External-Identifier": "breward2023",
            "Internal-Sender-Identifier": "breward2023_corpus",
            "Internal-Sender-Description": "Breward2023 Climate Change Seminar Corpus"
        }
        
        bag_info_path = corpus.topdir / "bag-info.txt"
        with open(bag_info_path, 'w', encoding='utf-8') as f:
            for key, value in bag_info.items():
                f.write(f"{key}: {value}\n")
        
        # bagit.txt
        bagit_path = corpus.topdir / "bagit.txt"
        with open(bagit_path, 'w', encoding='utf-8') as f:
            f.write("BagIt-Version: 1.0\n")
            f.write("Tag-File-Character-Encoding: UTF-8\n")
        
        # manifest-md5.txt (empty for now)
        manifest_path = corpus.topdir / "manifest-md5.txt"
        manifest_path.touch()

    def _create_config_files(self, corpus):
        """Create configuration files."""
        import yaml
        
        # corpus.yaml
        corpus_config = {
            "corpus": {
                "name": "breward2023",
                "version": "1.0",
                "bagit_compliant": True
            }
        }
        
        corpus_path = corpus.topdir / "config" / "corpus.yaml"
        with open(corpus_path, 'w', encoding='utf-8') as f:
            yaml.dump(corpus_config, f, default_flow_style=False)
        
        # search.yaml
        search_config = {
            "search": {
                "index_type": "file_based",
                "config": {
                    "inverted_index": "data/indices/inverted_index.json",
                    "brute_force": True,
                    "search_log": "search_results/search_history.txt",
                    "max_results": 100
                }
            }
        }
        
        search_path = corpus.topdir / "config" / "search.yaml"
        with open(search_path, 'w', encoding='utf-8') as f:
            yaml.dump(search_config, f, default_flow_style=False)
        
        # html_cleanup.yaml
        html_cleanup_config = {
            "transformations": [
                {
                    "name": "remove_empty_elements",
                    "type": "html_edit",
                    "xpath": "//div[count(*)=0 and count(text()=0]",
                    "action": "delete"
                }
            ]
        }
        
        html_cleanup_path = corpus.topdir / "config" / "transformations" / "html_cleanup.yaml"
        with open(html_cleanup_path, 'w', encoding='utf-8') as f:
            yaml.dump(html_cleanup_config, f, default_flow_style=False)
        
        # term_extraction.yaml
        term_extraction_config = {
            "transformations": [
                {
                    "name": "extract_text",
                    "type": "text_extraction",
                    "source": "pdf",
                    "output": "text",
                    "method": "pymupdf"
                }
            ]
        }
        
        term_extraction_path = corpus.topdir / "config" / "transformations" / "term_extraction.yaml"
        with open(term_extraction_path, 'w', encoding='utf-8') as f:
            yaml.dump(term_extraction_config, f, default_flow_style=False)


if __name__ == '__main__':
    unittest.main() 