#!/usr/bin/env python3
"""
Test corpus ingestion using AmiCorpus methods.
Follows style guide: no top-level files, use AmiCorpus.ingest_files()
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from amilib.file_lib import FileLib
from corpus_module.corpus import AmiCorpus
from test.resources import Resources


class TestCorpusIngestion(unittest.TestCase):
    """Test corpus ingestion operations using AmiCorpus."""

    def setUp(self):
        """Set up test environment."""
        self.corpus_path = Path(Resources.TEMP_DIR, "breward2023_corpus")
        FileLib.force_mkdir(self.corpus_path)
        self.source_path = Path(Resources.TEST_RESOURCES_DIR, "corpus", "breward2025")
        
    def tearDown(self):
        """Clean up test environment."""
        # if self.test_dir.exists():
        #     shutil.rmtree(self.test_dir)
        pass

    def test_ami_corpus_ingestion(self):
        """Test ingesting files using AmiCorpus methods."""
        print("\n=== Test: AmiCorpus File Ingestion ===")
        
        # 1. Construct AmiCorpus (will create directory if needed)
        corpus = AmiCorpus(topdir=self.corpus_path, mkdir=True)
        print(f"Created AmiCorpus at: {self.corpus_path}")
        
        # 2. Set up directory structure
        self._setup_corpus_structure(corpus)
        
        # 3. Ingest files using the new AmiCorpus.ingest_files method
        ingested_files = corpus.ingest_files(
            source_dir=self.source_path,
            file_pattern="*.pdf",
            target_container="files",
            file_type="pdf"
        )
        
        print(f"Ingested {len(ingested_files)} files using AmiCorpus.ingest_files()")
        
        # 4. Verify ingestion
        files_dir = self.corpus_path / "data" / "files"
        files_in_dir = list(files_dir.glob("*.pdf"))
        
        self.assertEqual(len(files_in_dir), len(ingested_files), 
                        f"Expected {len(ingested_files)} files, got {len(files_in_dir)}")
        
        print(f"✅ Successfully ingested {len(ingested_files)} files using AmiCorpus.ingest_files()")

    def _setup_corpus_structure(self, corpus):
        """Set up the corpus directory structure."""
        # Create data directories
        data_container = corpus.ami_container.create_corpus_container(
            "data", bib_type="bagit_data", mkdir=True
        )
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
        config_container.create_corpus_container("transformations", bib_type="transforms", mkdir=True)




if __name__ == '__main__':
    unittest.main(verbosity=2) 