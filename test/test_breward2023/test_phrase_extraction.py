#!/usr/bin/env python3
"""
Test script for TF-IDF phrase extraction functionality
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os

# Note: amilib should be installed with 'pip install -e .' for tests to work properly

from corpus_module.corpus import AmiCorpus


class TestPhraseExtraction(unittest.TestCase):
    """Test cases for TF-IDF phrase extraction functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.corpus_path = self.test_dir / "test_corpus"
        self.source_path = Path("test", "resources", "corpus", "breward2025")
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @unittest.skip("not yet implemented")
    def test_extract_significant_phrases(self):
        """Test extracting significant phrases using TF-IDF analysis."""
        print("\n=== Test: TF-IDF Phrase Extraction ===")
        
        # 1. Use existing corpus with files already ingested
        existing_corpus_path = Path("test", "resources", "corpus", "breward2023_corpus")
        if existing_corpus_path.exists():
            corpus = AmiCorpus(topdir=existing_corpus_path)
            print(f"Using existing corpus at: {existing_corpus_path}")
        else:
            # Fallback: create new corpus and ingest files
            corpus = AmiCorpus(topdir=self.corpus_path, mkdir=True)
            print(f"Created new corpus at: {self.corpus_path}")
            self._setup_corpus_structure(corpus)
            ingested_files = corpus.ingest_files(
                source_dir=self.source_path,
                file_pattern="*.pdf",
                target_container="files",
                file_type="pdf"
            )
            print(f"Ingested {len(ingested_files)} files")
        
        # 2. Extract significant phrases
        phrases = corpus.extract_significant_phrases(
            file_pattern="*.pdf",
            min_tfidf_score=0.05,  # Lower threshold for testing
            max_phrases=20,
            min_word_length=3
        )
        
        # 3. Validate results
        self.assertIsInstance(phrases, list)
        self.assertGreater(len(phrases), 0, "Should extract at least some phrases")
        
        print(f"✅ Extracted {len(phrases)} significant phrases")
        
        # 4. Validate phrase structure
        for phrase_data in phrases:
            self.assertIn("phrase", phrase_data)
            self.assertIn("tfidf_score", phrase_data)
            self.assertIn("frequency", phrase_data)
            self.assertIn("documents", phrase_data)
            self.assertIn("wikipedia_url", phrase_data)
            self.assertIn("definition", phrase_data)
            
            # Validate data types
            self.assertIsInstance(phrase_data["phrase"], str)
            self.assertIsInstance(phrase_data["tfidf_score"], float)
            self.assertIsInstance(phrase_data["frequency"], int)
            self.assertIsInstance(phrase_data["documents"], list)
            
            # Validate TF-IDF score range
            self.assertGreaterEqual(phrase_data["tfidf_score"], 0.0)
            self.assertLessEqual(phrase_data["tfidf_score"], 1.0)
            
            # Validate frequency
            self.assertGreaterEqual(phrase_data["frequency"], 1)
            
            # Validate documents list
            self.assertGreater(len(phrase_data["documents"]), 0)
        
        # 5. Check that we have meaningful phrases
        print(f"Sample phrases extracted: {[p['phrase'] for p in phrases[:5]]}")
        self.assertGreater(len(phrases), 0, "Should extract at least some phrases")
        
        # 6. Save results for inspection
        output_file = self.test_dir / "extracted_phrases.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(phrases, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(phrases)} phrases to {output_file}")
        print("✅ TF-IDF phrase extraction test passed")
    
    def test_phrase_extraction_with_different_patterns(self):
        """Test phrase extraction with different file patterns."""
        print("\n=== Test: Phrase Extraction with Different Patterns ===")
        
        # Create corpus and ingest files
        corpus = AmiCorpus(topdir=self.corpus_path, mkdir=True)
        self._setup_corpus_structure(corpus)
        
        # Ingest files
        corpus.ingest_files(
            source_dir=self.source_path,
            file_pattern="*.pdf",
            target_container="files",
            file_type="pdf"
        )
        
        # Test with different patterns
        patterns = ["*.pdf", "SCE-24-2023-*.pdf"]
        
        for pattern in patterns:
            phrases = corpus.extract_significant_phrases(
                file_pattern=pattern,
                min_tfidf_score=0.05,
                max_phrases=10
            )
            
            print(f"Pattern '{pattern}': extracted {len(phrases)} phrases")
            self.assertIsInstance(phrases, list)
    
    def test_phrase_extraction_parameters(self):
        """Test phrase extraction with different parameters."""
        print("\n=== Test: Phrase Extraction Parameters ===")
        
        # Create corpus and ingest files
        corpus = AmiCorpus(topdir=self.corpus_path, mkdir=True)
        self._setup_corpus_structure(corpus)
        
        corpus.ingest_files(
            source_dir=self.source_path,
            file_pattern="*.pdf",
            target_container="files",
            file_type="pdf"
        )
        
        # Test different parameter combinations
        test_cases = [
            {"min_tfidf_score": 0.1, "max_phrases": 5, "min_word_length": 4},
            {"min_tfidf_score": 0.05, "max_phrases": 10, "min_word_length": 3},
            {"min_tfidf_score": 0.2, "max_phrases": 3, "min_word_length": 5},
        ]
        
        for i, params in enumerate(test_cases):
            phrases = corpus.extract_significant_phrases(
                file_pattern="*.pdf",
                **params
            )
            
            print(f"Test case {i+1}: {len(phrases)} phrases with params {params}")
            
            # Validate parameter constraints
            if params["min_tfidf_score"] > 0.1:
                self.assertLessEqual(len(phrases), params["max_phrases"])
            
            # Validate minimum word length
            for phrase_data in phrases:
                words = phrase_data["phrase"].split()
                for word in words:
                    self.assertGreaterEqual(len(word), params["min_word_length"])
    
    def _setup_corpus_structure(self, corpus):
        """Set up the corpus directory structure."""
        # Create data directory structure
        data_container = corpus.ami_container.create_corpus_container(
            "data", bib_type="bagit_data", mkdir=True
        )
        
        # Create subdirectories
        data_container.create_corpus_container("files", bib_type="files", mkdir=True)
        data_container.create_corpus_container("indices", bib_type="indices", mkdir=True)
        data_container.create_corpus_container("metadata", bib_type="metadata", mkdir=True)


def run_tests():
    """Run the phrase extraction tests."""
    print("🧪 Running TF-IDF Phrase Extraction Tests")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPhraseExtraction))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        print("\n✅ All phrase extraction tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} tests failed")
        for test, traceback in result.failures:
            print(f"Failed: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 