#!/usr/bin/env python3
"""
Test suite for PDF annotation functionality
"""
import csv

import requests
import fitz  # PyMuPDF
import tempfile
import shutil
import unittest
from pathlib import Path
from lxml.html import fromstring
from lxml.etree import tostring
from test.test_all import AmiAnyTest
from test.resources import Resources
from amilib.ami_pdf_libs import PDFHyperlinkAdder, create_sample_word_list
import logging

logger = logging.getLogger(__name__)
class AnnotateTest(AmiAnyTest):
    """Test class for PDF annotation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_terms = ["climate change", "IPCC", "global warming"]
        self.shaik_url = "https://raw.githubusercontent.com/semanticClimate/internship_sC/refs/heads/Shaik-Zainab/IPCC_WG2_Chapter07/ch7_wordlist.txt"
        self.shaik_html_url = "https://github.com/semanticClimate/internship_sC/blob/Shaik-Zainab/IPCC_WG2_Chapter07/ch7_dict.html"
        self.ipcc_pdf = Resources.TEST_PDFS_DIR / "IPCC_AR6_WGII_Chapter07.pdf"
    
    def test_read_shaik_wordlist(self):
        """Test reading wordlist from Shaik's GitHub repository
        
        Input: External URL (GitHub raw content)
        Operations: HTTP GET request, parse text lines, verify specific terms
        Output: List of terms from wordlist, verification of 3 test terms
        """
        print("🧪 Testing Shaik wordlist access...")
        
        terms = self._load_wordlist_from_url(self.shaik_url)
        assert 290 <= len(terms) <= 310
        
        # Verify 3 specific terms
        test_terms = ["Aedes aegypti", "developing countries", "green infrastructure"]
        
        for term in test_terms:
            if term in terms:
                print(f"✅ Found term: {term}")
            else:
                print(f"❌ Missing term: {term}")
                assert False, f"Missing term: {term}"
        
        print("✅ All 3 test terms found in wordlist")
    
    def test_read_html_dictionary(self):
        """Test reading HTML dictionary from Shaik's GitHub repository
        
        Input: External HTML URL (GitHub raw content)
        Operations: HTTP GET request, parse HTML content, extract terms
        Output: List of terms from HTML dictionary
        """
        print("🧪 Testing HTML dictionary access...")
        
        terms = self._load_html_wordlist_from_url(self.shaik_html_url)
        
        # Verify we got some terms
        assert len(terms) > 0, "Should load at least one term from HTML dictionary"
        
        # Print first 10 terms as sample
        print(f"📋 First 10 terms from HTML dictionary:")
        for i, term in enumerate(terms[:10]):
            print(f"   {i+1}. {term}")
        
        if len(terms) > 10:
            print(f"   ... and {len(terms) - 10} more terms")
        
        print(f"✅ Successfully loaded {len(terms)} terms from HTML dictionary")
    
    def test_read_ipcc_wg2_chapter07_pdf(self):
        """Test reading IPCC WG2 Chapter 7 PDF
        
        Input: IPCC_AR6_WGII_Chapter07.pdf
        Operations: Open PDF, extract first page text, search for expected terms
        Output: PDF page count, verification of expected terms found
        """
        print("🧪 Testing IPCC WG2 Chapter 7 PDF access...")
        
        self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
        
        doc = None
        try:
            doc = fitz.open(str(self.ipcc_pdf))
            print(f"✅ Successfully opened PDF: {self.ipcc_pdf}")
            print(f"📄 Pages: {len(doc)}")
            
            # Get first page text to verify content
            first_page = doc[0]
            text = first_page.get_text()
            
            # Check for expected content
            expected_terms = ["climate", "health", "adaptation"]
            found_terms = []
            
            for term in expected_terms:
                if term.lower() in text.lower():
                    found_terms.append(term)
                    print(f"✅ Found term: {term}")
                else:
                    print(f"❌ Missing term: {term}")
            
            # Verify we found at least one expected term
            assert len(found_terms) > 0, f"Should find at least one of {expected_terms}"
            print(f"✅ PDF reading test completed - found {len(found_terms)} expected terms")
            
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            raise RuntimeError(f"Failed to read IPCC PDF: {e}") from e
        finally:
            if doc and not doc.is_closed:
                doc.close()

    def test_create_word_csv_from_url(self):
        temp_csv = self._create_word_csv_from_url(self.shaik_url)
        print(f"csv {temp_csv}")
        csvreader = csv.reader(str(temp_csv))
        for row in csvreader:
            print(f">> {','.join(row)}")


    @unittest.skip("only annotates a few single words, needs mending")
    def test_annotate_pdf_with_shaik_wordlist(self):
        """VERY LONG - 35 mins on my laptop"""
        """Test annotating PDF with words from Shaik wordlist using PDFHyperlinkAdder
        
        Input: IPCC_AR6_WGII_Chapter07.pdf, external GitHub wordlist URL
        Operations: Load wordlist from URL, create temp CSV, process PDF with PDFHyperlinkAdder
        Output: Annotated PDF with hyperlinks and visual indicators
        """
        print("🧪 Testing PDF annotation with Shaik wordlist...")
        
        self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
        
        # Create temp CSV from URL wordlist
        temp_csv = self._create_word_csv_from_url(self.shaik_url)
        logger.info(f"wrote {temp_csv} as CSV file")
        
        # Create output PDF path
        output_pdf = Resources.TEMP_DIR / "IPCC_AR6_WGII_Chapter07_annotated.pdf"
        
        try:
            # Use existing PDFHyperlinkAdder
            adder = self._create_pdf_adder(self.ipcc_pdf, temp_csv, output_pdf)
            adder.process_pdf()
            
            # Verify results
            self._assert_pdf_processed_successfully(output_pdf, adder)
            
            print(f"💾 Saved annotated PDF: {output_pdf}")
            
        finally:
            # Clean up temp file
            if temp_csv.exists():
                temp_csv.unlink()
    
    def test_dictionary_annotation_workflow(self):
        """Test complete dictionary annotation workflow using external wordlist
        
        Input: IPCC_AR6_WGII_Chapter07.pdf, external GitHub wordlist URL
        Operations: Load wordlist from URL, create temp CSV, process PDF with PDFHyperlinkAdder
        Output: Annotated PDF with dictionary-based hyperlinks and visual indicators
        
        OPTIMIZATION: Limited to 5 terms and 10 pages for faster testing while maintaining at least one lookup
        """
        print("🧪 Testing complete dictionary annotation workflow...")
        
        self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
        
        # OPTIMIZATION: Limit to 5 terms instead of 290+ for faster testing
        temp_csv = self._create_word_csv_from_url(self.shaik_url, max_terms=5)
        
        # Create output PDF path
        output_pdf = Resources.TEMP_DIR / "IPCC_AR6_WGII_Chapter07_dictionary_annotated.pdf"
        
        try:
            # Use existing PDFHyperlinkAdder
            adder = self._create_pdf_adder(self.ipcc_pdf, temp_csv, output_pdf)
            # OPTIMIZATION: Process only first 10 pages instead of entire PDF
            adder.process_pdf(max_pages=10)
            
            # Verify results
            self._assert_pdf_processed_successfully(output_pdf, adder)
            
            print(f"✅ Dictionary annotation workflow completed!")
            print(f"💾 Saved annotated PDF: {output_pdf}")
            
        finally:
            # Clean up temp file
            if temp_csv.exists():
                temp_csv.unlink()
    
    def test_create_sample_word_list(self):
        """Test creating a sample word list
        
        Input: None (creates temporary directory)
        Operations: Create temporary directory, generate sample CSV with test words
        Output: Sample word list CSV file with predefined terms and URLs
        """
        print("🔧 Testing sample word list creation...")
        
        temp_dir = Path(tempfile.mkdtemp())
        sample_word_list = temp_dir / "sample_word_list.csv"
        
        try:
            create_sample_word_list(str(sample_word_list))
            
            # Verify file was created
            assert sample_word_list.exists()
            
            # Verify content
            with open(sample_word_list, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "python" in content
                assert "https://python.org" in content
                assert "machine learning" in content
            
            print(f"✅ Sample word list created: {sample_word_list}")
            
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def test_load_word_list(self):
        """Test loading word list from CSV
        
        Input: climate_words.csv, test PDF file
        Operations: Create PDFHyperlinkAdder, load word list from CSV, verify loaded terms
        Output: PDFHyperlinkAdder with loaded word_links dictionary
        """
        print("📖 Testing word list loading...")
        
        climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
        
        self._verify_file_exists(climate_words, "Climate words file")
        
        test_pdf = Resources.TEST_PDFS_DIR / "1758-2946-3-44.pdf"
        output_pdf = Resources.TEMP_DIR / "test_output.pdf"
        
        adder = PDFHyperlinkAdder(
            input_pdf=str(test_pdf),
            word_list_file=str(climate_words),
            output_pdf=str(output_pdf)
        )
        
        adder.load_word_list()
        
        # Verify words were loaded
        assert len(adder.word_links) > 0
        assert "climate" in adder.word_links
        assert "climate change" in adder.word_links
        assert "co2" in adder.word_links  # Note: converted to lowercase
        
        print(f"✅ Loaded {len(adder.word_links)} words from word list")
    
    def test_pdf_hyperlink_adder_basic(self):
        """Test basic PDF hyperlink adder functionality
        
        Input: 1758-2946-3-44.pdf, climate_words.csv
        Operations: Create PDFHyperlinkAdder, process PDF with word list
        Output: Annotated PDF with hyperlinks and visual indicators
        """
        print("🔗 Testing basic PDF hyperlink adder...")
        
        test_pdf = Resources.TEST_PDFS_DIR / "1758-2946-3-44.pdf"
        climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
        
        self._verify_file_exists(test_pdf, "Test PDF")
        
        self._verify_file_exists(climate_words, "Climate words file")
        
        output_pdf = Resources.TEMP_DIR / "basic_output.pdf"
        
        # Use helper methods
        adder = self._create_pdf_adder(test_pdf, climate_words, output_pdf)
        adder.process_pdf()
        
        # Verify results
        self._assert_pdf_processed_successfully(output_pdf, adder)
        print(f"   Input: {test_pdf}")
        print(f"   Output: {output_pdf}")
    
    def test_pdf_hyperlink_adder_breward(self):
        """Test PDF hyperlink adder with Breward PDF
        
        Input: breward_1.pdf, breward_words.csv
        Operations: Create PDFHyperlinkAdder, process PDF with word list
        Output: Annotated PDF with hyperlinks and visual indicators
        """
        print("📄 Testing PDF hyperlink adder with Breward PDF...")
        
        breward_pdf = Resources.TEST_PDFS_DIR / "breward_1.pdf"
        breward_words = Resources.TEST_PDFS_DIR / "breward_words.csv"
        
        self._verify_file_exists(breward_pdf, "Breward PDF")
        
        self._verify_file_exists(breward_words, "Breward words file")
        
        output_pdf = Resources.TEMP_DIR / "breward_with_links.pdf"
        
        # Use helper methods
        adder = self._create_pdf_adder(breward_pdf, breward_words, output_pdf)
        adder.process_pdf()
        
        # Verify results
        self._assert_pdf_processed_successfully(output_pdf, adder)
        print(f"   Input: {breward_pdf}")
        print(f"   Output: {output_pdf}")
    
    def test_pdf_hyperlink_adder_ipcc(self):
        """Test PDF hyperlink adder with IPCC PDF
        
        Input: IPCC_AR6_WGII_Chapter07.pdf, climate_words.csv
        Operations: Create PDFHyperlinkAdder, process PDF with word list
        Output: Annotated PDF with hyperlinks and visual indicators
        
        OPTIMIZATION: Limited to 10 pages for faster testing
        """
        print("🌍 Testing PDF hyperlink adder with IPCC PDF...")
        
        climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
        
        self._verify_file_exists(self.ipcc_pdf, "IPCC PDF")
        self._verify_file_exists(climate_words, "Climate words file")
        
        output_pdf = Resources.TEMP_DIR / "ipcc_with_links.pdf"
        
        # Use helper methods
        adder = self._create_pdf_adder(self.ipcc_pdf, climate_words, output_pdf)
        # OPTIMIZATION: Process only first 10 pages instead of entire PDF
        adder.process_pdf(max_pages=10)
        
        # Verify results
        self._assert_pdf_processed_successfully(output_pdf, adder)
        print(f"   Input: {self.ipcc_pdf}")
        print(f"   Output: {output_pdf}")
    
    def test_word_matching_accuracy(self):
        """Test accuracy of word matching using PDFHyperlinkAdder
        
        Input: 1758-2946-3-44.pdf, climate_words.csv
        Operations: Create PDFHyperlinkAdder, load word list, find word instances
        Output: Verification of word matching accuracy and instance validation
        """
        print("🎯 Testing word matching accuracy...")
        
        test_pdf = Resources.TEST_PDFS_DIR / "1758-2946-3-44.pdf"
        climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
        
        self._verify_file_exists(test_pdf, "Test PDF")
        
        self._verify_file_exists(climate_words, "Climate words file")
        
        output_pdf = Resources.TEMP_DIR / "accuracy_test.pdf"
        
        # Use helper methods
        adder = self._create_pdf_adder(test_pdf, climate_words, output_pdf)
        adder.load_word_list()
        
        # Find word instances using existing method
        doc = fitz.open(str(test_pdf))
        word_instances = adder.find_word_instances(doc)
        doc.close()
        
        # Verify we found some matches
        assert len(word_instances) > 0, "Should find at least one word instance"
        
        # Check that matches are valid
        for page_num, word, bbox, link in word_instances:
            assert isinstance(page_num, int)
            assert isinstance(word, str)
            assert isinstance(bbox, fitz.Rect)
            assert isinstance(link, str)
            assert word.lower() in adder.word_links
        
        print(f"✅ Word matching accuracy verified")
        print(f"   Found {len(word_instances)} word instances")
        print(f"   Unique words found: {len(set(word for _, word, _, _ in word_instances))}")
    
    def test_error_handling(self):
        """Test error handling for missing files
        
        Input: Non-existent PDF file, climate_words.csv
        Operations: Attempt to process PDF with missing input file
        Output: FileNotFoundError exception raised, no output file created
        """
        print("⚠️  Testing error handling...")
        
        climate_words = Resources.TEST_PDFS_DIR / "climate_words.csv"
        non_existent_pdf = Resources.TEMP_DIR / "non_existent.pdf"
        output_pdf = Resources.TEMP_DIR / "error_test_output.pdf"
        
        if climate_words.exists():
            # Use helper method
            adder = self._create_pdf_adder(non_existent_pdf, climate_words, output_pdf)
            
            # This should handle the error gracefully
            try:
                adder.process_pdf()
                assert False, "Should have raised an exception"
            except (FileNotFoundError, fitz.FileNotFoundError):
                pass  # Expected
        
        # Output should not be created
        assert not output_pdf.exists()
        
        print("✅ Error handling tested")
    
    def test_annotate_single_term_in_paragraph(self):
        """Test basic single term annotation in a paragraph
        
        Input: HTML paragraph element with text content
        Operations: Apply annotation to single term using _apply_annotation method
        Output: HTML element with annotated term wrapped in <a> tag
        """
        print("🧪 Testing single term annotation...")
        
        # Arrange
        original_elem = fromstring("<p>Climate change is a global issue.</p>")
        expected_elem = fromstring('<p><a class="annotation" href="#climate_change">Climate change</a> is a global issue.</p>')
        
        # Act
        result_elem = self._apply_annotation(original_elem, ["climate change"])
        
        # Assert using complete DOM comparison
        assert tostring(result_elem) == tostring(expected_elem), "DOM structure does not match expected annotation"
    
    def test_skip_annotation_inside_existing_links(self):
        """Test that annotation is skipped inside existing <a> tags
        
        Input: HTML paragraph with existing <a> tag containing target term
        Operations: Apply annotation to paragraph with existing links
        Output: HTML element unchanged (annotation skipped inside existing links)
        """
        print("🧪 Testing annotation skip inside existing links...")
        
        # Arrange
        original_elem = fromstring('<p>This is a <a href="http://example.com">climate change</a> example.</p>')
        expected_elem = fromstring('<p>This is a <a href="http://example.com">climate change</a> example.</p>')
        
        # Act
        result_elem = self._apply_annotation(original_elem, ["climate change"])
        
        # Assert using complete DOM comparison
        assert tostring(result_elem) == tostring(expected_elem), "DOM structure should remain unchanged when term is inside existing link"
    
    def test_text_content_identical_before_and_after_annotation(self):
        """Test that text content is exactly preserved after annotation
        
        Input: HTML paragraph with multiple terms to annotate
        Operations: Apply annotation to multiple terms in paragraph
        Output: HTML element with annotations, text content unchanged
        """
        print("🧪 Testing text content preservation...")
        
        # Arrange
        original_elem = fromstring("<p>Climate change is a global issue. The IPCC reports on global warming.</p>")
        
        # Act
        result_elem = self._apply_annotation(original_elem, self.test_terms)
        
        # Assert using complete DOM comparison of text content
        original_text = original_elem.text_content().strip()
        result_text = result_elem.text_content().strip()
        assert original_text == result_text, "Text content should be identical before and after annotation"
    
    def test_annotation_has_correct_html_structure(self):
        """Test that annotations have the correct HTML structure
        
        Input: HTML paragraph with single term to annotate
        Operations: Apply annotation to term using _apply_annotation method
        Output: HTML element with properly structured <a> tag annotation
        """
        print("🧪 Testing HTML structure...")
        
        # Arrange
        original_elem = fromstring("<p>Climate change is important.</p>")
        expected_elem = fromstring('<p><a class="annotation" href="#climate_change">Climate change</a> is important.</p>')
        
        # Act
        result_elem = self._apply_annotation(original_elem, ["climate change"])
        
        # Assert using complete DOM comparison
        assert tostring(result_elem) == tostring(expected_elem), "DOM structure should match expected annotation structure"
    
    def _load_wordlist_from_url(self, url: str) -> list:
        """Load wordlist from external URL and return as list"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            terms = [line.strip() for line in response.text.split('\n') if line.strip()]
            print(f"✅ Loaded {len(terms)} terms from URL")
            return terms
        except Exception as e:
            print(f"❌ Error loading wordlist from URL: {e}")
            raise RuntimeError(f"Failed to load wordlist from URL {url}: {e}") from e
    
    def _load_html_wordlist_from_url(self, url: str) -> list:
        """Load HTML wordlist from external URL and return as list of terms"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            from lxml.html import fromstring
            html_content = response.text
            root = fromstring(html_content)
            
            # Extract terms from HTML (assuming they're in specific elements)
            # This is a basic implementation - may need adjustment based on actual HTML structure
            terms = []
            
            # Look for terms in various HTML elements
            for element in root.xpath('//*[text()]'):
                text = element.text_content().strip()
                if text and len(text) > 2 and not text.startswith('<'):
                    # Filter out common HTML noise
                    if not any(skip in text.lower() for skip in ['html', 'body', 'head', 'title', 'div', 'span', 'p', 'br']):
                        terms.append(text)
            
            # Remove duplicates and sort
            terms = sorted(list(set(terms)))
            print(f"✅ Loaded {len(terms)} terms from HTML wordlist")
            return terms
            
        except Exception as e:
            print(f"❌ Error loading HTML wordlist from URL: {e}")
            raise RuntimeError(f"Failed to load HTML wordlist from URL {url}: {e}") from e
    
    def _create_word_csv_from_url(self, url: str, max_terms: int = None) -> Path:
        """Create temporary CSV file from URL wordlist for PDFHyperlinkAdder
        
        Args:
            url: URL to load wordlist from
            max_terms: Maximum number of terms to include (None = all)
        """
        terms = self._load_wordlist_from_url(url)
        if max_terms is not None and len(terms) > max_terms:
            terms = terms[:max_terms]
            print(f"⚠️  Limited to first {max_terms} terms for faster testing")
        print(f"terms {len(terms)}")
        temp_csv = Path(Resources.TEMP_DIR, "words", "pdf_annotate_wordlist.csv")
        temp_csv.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_csv, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(["word", "hyperlink"])
            for term in terms:
                # Create simple hash-based links for external wordlist
                link = f"#{term.lower().replace(' ', '_')}"
                writer.writerow([term, link])
        
        print(f"✅ Created temp CSV: {temp_csv}")
        return temp_csv
    
    def _verify_file_exists(self, file_path: Path, file_type: str) -> None:
        """Verify file exists and raise FileNotFoundError if missing"""
        if not file_path.exists():
            print(f"⚠️  {file_type} not found: {file_path}")
            raise FileNotFoundError(f"{file_type} not found: {file_path}")
    
    def _create_pdf_adder(self, input_pdf: Path, word_list: Path, output_pdf: Path) -> PDFHyperlinkAdder:
        """Create PDFHyperlinkAdder instance with common setup"""
        return PDFHyperlinkAdder(
            input_pdf=str(input_pdf),
            word_list_file=str(word_list),
            output_pdf=str(output_pdf)
        )
    
    def _assert_pdf_processed_successfully(self, output_pdf: Path, adder: PDFHyperlinkAdder) -> None:
        """Common assertions for PDF processing success"""
        assert output_pdf.exists(), "Output PDF should be created"
        assert output_pdf.stat().st_size > 0, "Output PDF should not be empty"
        assert adder.processed_words > 0, "Should process at least one word"
        print(f"✅ PDF processed successfully")
        print(f"   Words processed: {adder.processed_words}")
        print(f"   Total matches: {adder.total_matches}")
    
    def _apply_annotation(self, html_elem, terms):
        """Apply annotation to lxml Element - TEMPORARY IMPLEMENTATION - needs proper amilib integration"""
        from lxml.etree import SubElement
        import re
        
        # Find all text nodes that are not inside existing <a> tags
        text_nodes = html_elem.xpath('.//text()[not(ancestor::a)]')
        
        for text_node in text_nodes:
            if text_node.is_text:  # Direct text content of an element
                parent = text_node.getparent()
                if parent is not None:
                    text_content = text_node
                    
                    # Collect all matches from all terms
                    all_matches = []
                    for term in terms:
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        matches = list(pattern.finditer(text_content))
                        for match in matches:
                            all_matches.append((match.start(), match.end(), term))
                    
                    # Sort matches by start position (not reverse - we want natural order)
                    all_matches.sort(key=lambda x: x[0])
                    
                    if all_matches:
                        # Clear parent content once
                        parent.clear()
                        
                        # Process matches in natural order
                        current_text = text_content
                        last_end = 0
                        
                        for i, (start, end, term) in enumerate(all_matches):
                            # Add text before this match
                            if start > last_end:
                                if parent.text is None:
                                    parent.text = current_text[last_end:start]
                                else:
                                    parent.text += current_text[last_end:start]
                            
                            # Create annotation element
                            annotation = SubElement(parent, 'a')
                            annotation.attrib['class'] = 'annotation'
                            annotation.attrib['href'] = f'#{term.lower().replace(" ", "_")}'
                            annotation.text = current_text[start:end]  # Use original case
                            
                            # Set the tail to the text after this match
                            if i < len(all_matches) - 1:
                                # There's another match coming, so set tail to text up to next match
                                next_start = all_matches[i + 1][0]
                                annotation.tail = current_text[end:next_start]
                            else:
                                # This is the last match, so set tail to remaining text
                                annotation.tail = current_text[end:]
                            
                            last_end = end
        
        return html_elem
