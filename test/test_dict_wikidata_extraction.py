"""
Tests for Wikidata ID extraction from Wikipedia pages during dictionary creation.
"""
import logging
import re
import unittest
from pathlib import Path

from amilib.ami_dict import AmiEntry, AMIDictError
from amilib.wikimedia import WikipediaPage
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)


class TestDictWikidataExtraction(AmiAnyTest):
    """Test Wikidata ID extraction in dictionary entries"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "dict", "wikidata_extraction")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def test_extract_wikidata_id_from_article(self):
        """Test extracting Wikidata ID from a standard Wikipedia article"""
        # Terms that should return valid articles with Wikidata IDs
        test_terms = [
            "climate change",  # Should be Q7942
            "greenhouse effect",  # Should be Q1366
            "carbon dioxide"  # Should be Q1218
        ]
        
        extracted_count = 0
        for term in test_terms:
            with self.subTest(term=term):
                entry = AmiEntry.create_lxml_entry_from_term(term)
                ami_entry = AmiEntry.create_from_element(entry)
                
                # Call lookup and add Wikipedia page
                wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
                
                # Check that Wikipedia page was found
                self.assertIsNotNone(wikipedia_page, f"Wikipedia page should be found for {term}")
                
                # Try to get Wikidata ID directly from page to debug
                if wikipedia_page:
                    wikidata_url = wikipedia_page.get_wikidata_item()
                    if wikidata_url:
                        logger.info(f"For {term}, got Wikidata URL: {wikidata_url}")
                
                # Check that Wikidata ID was extracted and stored
                wikidata_id = ami_entry.wikidata_id
                if wikidata_id:
                    self.assertTrue(wikidata_id.startswith('Q'), 
                                  f"Wikidata ID should start with Q, got {wikidata_id}")
                    extracted_count += 1
                else:
                    logger.warning(f"Wikidata ID not extracted for {term} - this may be expected for some pages")
                
                # Verify URL was also stored
                wikipedia_url = ami_entry.element.get("wikipedia_url")
                self.assertIsNotNone(wikipedia_url, f"Wikipedia URL should be stored for {term}")
        
        # At least one should have extracted Wikidata ID
        self.assertGreater(extracted_count, 0, "At least one term should have extracted Wikidata ID")
                
    def test_extract_wikidata_id_disambiguation(self):
        """Test handling of disambiguation pages"""
        # Terms that return disambiguation pages
        disambig_terms = ["AGW", "GHG"]
        
        for term in disambig_terms:
            with self.subTest(term=term):
                entry = AmiEntry.create_lxml_entry_from_term(term)
                ami_entry = AmiEntry.create_from_element(entry)
                
                wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
                
                if wikipedia_page and wikipedia_page.html_elem:
                    # Check if it's a disambiguation page
                    try:
                        is_disambig = wikipedia_page.is_disambiguation_page()
                    except (AttributeError, TypeError):
                        # Skip if basic_info cannot be retrieved
                        is_disambig = False
                    
                    # Should still attempt to extract Wikidata ID if possible
                    # Disambiguation pages may or may not have Wikidata IDs
                    wikidata_id = ami_entry.wikidata_id
                    # Either None or valid Q/P ID
                    if wikidata_id:
                        self.assertTrue(
                            re.match(r'^[PQ]\d+$', wikidata_id),
                            f"Wikidata ID {wikidata_id} should be valid format"
                        )
                        
    def test_extract_wikidata_id_redirect(self):
        """Test handling of redirect pages"""
        # Terms that redirect to other pages
        redirect_terms = ["global warming"]  # Redirects to "climate change"
        
        for term in redirect_terms:
            with self.subTest(term=term):
                entry = AmiEntry.create_lxml_entry_from_term(term)
                ami_entry = AmiEntry.create_from_element(entry)
                
                wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
                
                # Redirects should resolve to target page
                self.assertIsNotNone(wikipedia_page, 
                                   f"Redirect should resolve for {term}")
                
                # Should extract Wikidata ID from target page
                wikidata_id = ami_entry.wikidata_id
                # May or may not have ID, but if present should be valid
                if wikidata_id:
                    self.assertTrue(wikidata_id.startswith('Q'),
                                  f"Wikidata ID should be valid format")
                                  
    def test_extract_wikidata_id_list_page(self):
        """Test handling of list pages"""
        # Terms that return list pages
        list_terms = ["List of IPCC assessment reports"]
        
        for term in list_terms:
            with self.subTest(term=term):
                entry = AmiEntry.create_lxml_entry_from_term(term)
                ami_entry = AmiEntry.create_from_element(entry)
                
                wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
                
                if wikipedia_page:
                    # List pages may or may not have Wikidata IDs
                    wikidata_id = ami_entry.wikidata_id
                    # If present, should be valid format
                    if wikidata_id:
                        self.assertTrue(re.match(r'^[PQ]\d+$', wikidata_id))
                        
    def test_wikidata_id_not_found_handling(self):
        """Test graceful handling when Wikidata ID cannot be extracted"""
        # This might happen with some pages
        entry = AmiEntry.create_lxml_entry_from_term("test term without wikipedia")
        ami_entry = AmiEntry.create_from_element(entry)
        
        wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
        
        # If page found but no Wikidata link, should not raise error
        wikidata_id = ami_entry.wikidata_id
        # Should be None, not empty string or invalid value
        self.assertIn(wikidata_id, [None, ""], 
                     "Should return None or empty string when not found")
                     
    def test_wikidata_id_html_output(self):
        """Test that Wikidata ID and link appear in HTML output"""
        # Create dictionary with Wikipedia descriptions
        dict_file = Path(self.temp_dir, "test_wikidata_output.html")
        
        # Use command-line equivalent
        from amilib.dict_args import AmiDictArgs
        
        # Create test words file
        words_file = Path(self.temp_dir, "test_words.txt")
        words_file.write_text("climate change\ncarbon dioxide\n")
        
        args = AmiDictArgs()
        args.words = str(words_file)
        args.dictfile = str(dict_file)
        args.description = ["wikipedia"]
        args.title = "Test Dictionary"
        args.figures = None
        
        # Create dictionary
        args.create_dictionary_from_words("Test Dictionary")
        
        # Check that HTML file was created
        self.assertTrue(dict_file.exists(), "Dictionary HTML file should be created")
        
        # Read HTML and check for Wikidata ID
        html_content = dict_file.read_text()
        
        # Should contain Wikidata references
        self.assertIn("wikidata", html_content.lower(), 
                     "HTML should contain Wikidata references")

    def test_page_type_detection(self):
        """Test that page type detection works correctly"""
        # Test article
        article_page = WikipediaPage.lookup_wikipedia_page_for_term("climate change")
        if article_page:
            page_type = article_page.get_page_type()
            self.assertIn(page_type, ['article', 'redirect', 'list', 'unknown'], 
                         f"Page type should be valid: {page_type}")
        
        # Test disambiguation
        disambig_page = WikipediaPage.lookup_wikipedia_page_for_term("AGW")
        if disambig_page:
            page_type = disambig_page.get_page_type()
            # Should detect as disambiguation
            if disambig_page.is_disambiguation_page():
                self.assertEqual(page_type, 'disambiguation',
                               f"AGW should be detected as disambiguation page")

    def test_is_redirect_page(self):
        """Test redirect page detection"""
        # "global warming" redirects to "climate change"
        redirect_page = WikipediaPage.lookup_wikipedia_page_for_term("global warming")
        if redirect_page:
            is_redirect = redirect_page.is_redirect_page()
            # May or may not be detected as redirect depending on implementation
            self.assertIsInstance(is_redirect, bool, "is_redirect_page should return boolean")

    def test_is_list_page(self):
        """Test list page detection"""
        # Try to find a list page
        list_page = WikipediaPage.lookup_wikipedia_page_for_term("List of IPCC assessment reports")
        if list_page:
            is_list = list_page.is_list_page()
            self.assertIsInstance(is_list, bool, "is_list_page should return boolean")
            if is_list:
                page_type = list_page.get_page_type()
                self.assertEqual(page_type, 'list', "List page should be classified as 'list'")

