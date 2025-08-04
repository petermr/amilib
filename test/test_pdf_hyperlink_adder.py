#!/usr/bin/env python3
"""
Test script for PDF hyperlink adder functionality
Tests markup/annotation of PDFs with wordlists
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os
import pymupdf

# Note: amilib should be installed with 'pip install -e .' for tests to work properly

from amilib.ami_pdf_libs import PDFHyperlinkAdder, create_sample_word_list
from amilib.core.util import Util

class TestPDFHyperlinkAdder(unittest.TestCase):
    """Test cases for PDF hyperlink adder functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.resources_dir = Path(__file__).parent / "resources" / "pdf"
        
        # Test files
        self.test_pdf = self.resources_dir / "1758-2946-3-44.pdf"
        self.breward_pdf = self.resources_dir / "breward_1.pdf"
        self.climate_words = self.resources_dir / "climate_words.csv"
        self.breward_words = self.resources_dir / "breward_words.csv"
        
        # Output files
        self.output_pdf = self.test_dir / "output_with_links.pdf"
        self.sample_word_list = self.test_dir / "sample_word_list.csv"
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_create_sample_word_list(self):
        """Test creating a sample word list"""
        print("\n🔧 Testing sample word list creation...")
        
        create_sample_word_list(str(self.sample_word_list))
        
        # Verify file was created
        self.assertTrue(self.sample_word_list.exists())
        
        # Verify content
        with open(self.sample_word_list, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("python", content)
            self.assertIn("https://python.org", content)
            self.assertIn("machine learning", content)
        
        print(f"✅ Sample word list created: {self.sample_word_list}")
    
    def test_load_word_list(self):
        """Test loading word list from CSV"""
        print("\n📖 Testing word list loading...")
        
        if not self.climate_words.exists():
            print(f"⚠️  Climate words file not found: {self.climate_words}")
            return
        
        adder = PDFHyperlinkAdder(
            input_pdf=str(self.test_pdf),
            word_list_file=str(self.climate_words),
            output_pdf=str(self.output_pdf)
        )
        
        adder.load_word_list()
        
        # Verify words were loaded
        self.assertGreater(len(adder.word_links), 0)
        self.assertIn("climate", adder.word_links)
        self.assertIn("climate change", adder.word_links)
        self.assertIn("co2", adder.word_links)  # Note: converted to lowercase
        
        print(f"✅ Loaded {len(adder.word_links)} words from word list")
    
    def test_pdf_hyperlink_adder_basic(self):
        """Test basic PDF hyperlink adder functionality"""
        print("\n🔗 Testing basic PDF hyperlink adder...")
        
        if not self.test_pdf.exists():
            print(f"⚠️  Test PDF not found: {self.test_pdf}")
            return
        
        if not self.climate_words.exists():
            print(f"⚠️  Climate words file not found: {self.climate_words}")
            return
        
        # Create adder instance
        adder = PDFHyperlinkAdder(
            input_pdf=str(self.test_pdf),
            word_list_file=str(self.climate_words),
            output_pdf=str(self.output_pdf)
        )
        
        # Process the PDF
        adder.process_pdf()
        
        # Verify output was created
        self.assertTrue(self.output_pdf.exists())
        self.assertGreater(self.output_pdf.stat().st_size, 0)
        
        print(f"✅ PDF processed successfully")
        print(f"   Input: {self.test_pdf}")
        print(f"   Output: {self.output_pdf}")
        print(f"   Words processed: {adder.processed_words}")
        print(f"   Total matches: {adder.total_matches}")
    
    def test_pdf_hyperlink_adder_breward(self):
        """Test PDF hyperlink adder with Breward PDF"""
        print("\n📄 Testing PDF hyperlink adder with Breward PDF...")
        
        if not self.breward_pdf.exists():
            print(f"⚠️  Breward PDF not found: {self.breward_pdf}")
            return
        
        if not self.breward_words.exists():
            print(f"⚠️  Breward words file not found: {self.breward_words}")
            return
        
        output_pdf = self.test_dir / "breward_with_links.pdf"
        
        # Create adder instance
        adder = PDFHyperlinkAdder(
            input_pdf=str(self.breward_pdf),
            word_list_file=str(self.breward_words),
            output_pdf=str(output_pdf)
        )
        
        # Process the PDF
        adder.process_pdf()
        
        # Verify output was created
        self.assertTrue(output_pdf.exists())
        self.assertGreater(output_pdf.stat().st_size, 0)
        
        print(f"✅ Breward PDF processed successfully")
        print(f"   Input: {self.breward_pdf}")
        print(f"   Output: {output_pdf}")
        print(f"   Words processed: {adder.processed_words}")
        print(f"   Total matches: {adder.total_matches}")
    
    def test_pdf_hyperlink_adder_ipcc(self):
        """Test PDF hyperlink adder with IPCC PDF"""
        print("\n🌍 Testing PDF hyperlink adder with IPCC PDF...")
        
        ipcc_pdf = self.resources_dir / "IPCC_AR6_WGII_Chapter07.pdf"
        
        if not ipcc_pdf.exists():
            print(f"⚠️  IPCC PDF not found: {ipcc_pdf}")
            return
        
        if not self.climate_words.exists():
            print(f"⚠️  Climate words file not found: {self.climate_words}")
            return
        
        output_pdf = self.test_dir / "ipcc_with_links.pdf"
        
        # Create adder instance
        adder = PDFHyperlinkAdder(
            input_pdf=str(ipcc_pdf),
            word_list_file=str(self.climate_words),
            output_pdf=str(output_pdf)
        )
        
        # Process the PDF
        adder.process_pdf()
        
        # Verify output was created
        self.assertTrue(output_pdf.exists())
        self.assertGreater(output_pdf.stat().st_size, 0)
        
        print(f"✅ IPCC PDF processed successfully")
        print(f"   Input: {ipcc_pdf}")
        print(f"   Output: {output_pdf}")
        print(f"   Words processed: {adder.processed_words}")
        print(f"   Total matches: {adder.total_matches}")
    
    def test_word_matching_accuracy(self):
        """Test accuracy of word matching"""
        print("\n🎯 Testing word matching accuracy...")
        
        if not self.test_pdf.exists():
            print(f"⚠️  Test PDF not found: {self.test_pdf}")
            return
        
        if not self.climate_words.exists():
            print(f"⚠️  Climate words file not found: {self.climate_words}")
            return
        
        # Create adder instance
        adder = PDFHyperlinkAdder(
            input_pdf=str(self.test_pdf),
            word_list_file=str(self.climate_words),
            output_pdf=str(self.output_pdf)
        )
        
        # Load word list
        adder.load_word_list()
        
        # Find word instances
        import fitz
        doc = fitz.open(str(self.test_pdf))
        word_instances = adder.find_word_instances(doc)
        doc.close()
        
        # Verify we found some matches
        self.assertGreater(len(word_instances), 0)
        
        # Check that matches are valid
        for page_num, word, bbox, link in word_instances:
            self.assertIsInstance(page_num, int)
            self.assertIsInstance(word, str)
            self.assertIsInstance(bbox, fitz.Rect)
            self.assertIsInstance(link, str)
            self.assertIn(word.lower(), adder.word_links)
        
        print(f"✅ Word matching accuracy verified")
        print(f"   Found {len(word_instances)} word instances")
        print(f"   Unique words found: {len(set(word for _, word, _, _ in word_instances))}")
    
    def test_error_handling(self):
        """Test error handling for missing files"""
        print("\n⚠️  Testing error handling...")
        
        # Test with non-existent PDF
        non_existent_pdf = self.test_dir / "non_existent.pdf"
        output_pdf = self.test_dir / "output.pdf"
        
        if self.climate_words.exists():
            adder = PDFHyperlinkAdder(
                input_pdf=str(non_existent_pdf),
                word_list_file=str(self.climate_words),
                output_pdf=str(output_pdf)
            )
            
                    # This should handle the error gracefully
        with self.assertRaises((FileNotFoundError, pymupdf.FileNotFoundError)):
            adder.process_pdf()
        
        # Output should not be created
        self.assertFalse(output_pdf.exists())
        
        print("✅ Error handling tested")

def run_tests():
    """Run all tests"""
    print("🧪 Running PDF Hyperlink Adder Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPDFHyperlinkAdder)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 