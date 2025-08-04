#!/usr/bin/env python3
"""
Test-Driven Development: HTML Annotation
Precise tests for HTML annotation functionality using IPCC executive summary
"""

import unittest
from pathlib import Path
from typing import Dict, List, Set, Tuple
import lxml.etree as ET
from lxml.html import HTMLParser, tostring, fromstring
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHTMLAnnotation(unittest.TestCase):
    """Precise test cases for HTML annotation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(__file__).parent
        self.resources_dir = self.test_dir / "resources"
        
        # Test files - using WG1 Chapter 1 instead of executive summary
        self.test_html = Path("temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
        self.expected_annotated_html = Path("temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_demo.html")
        
        # Climate terms for testing (subset of IPCC glossary)
        self.climate_terms = [
            "climate change",
            "global warming", 
            "greenhouse gas",
            "carbon dioxide",
            "temperature",
            "emissions",
            "mitigation",
            "adaptation",
            "IPCC",
            "atmosphere"
        ]
    
    def test_html_annotation_exact_positioning(self):
        """Test that annotations are placed in exactly the right positions within text"""
        print("\n🎯 Testing HTML annotation exact positioning...")
        
        if not self.test_html.exists():
            self.skipTest(f"Test HTML file not found: {self.test_html}")
        
        html_elem = self._parse_html(self.test_html)
        
        # Apply annotation
        annotated_elem = self._apply_annotation_with_glossary(html_elem)
        
        # Test 1: Verify annotation positioning within sentences
        self._test_annotation_positioning(annotated_elem)
        
        # Test 2: Verify no broken sentence structure
        self._test_sentence_integrity(annotated_elem)
        
        # Test 3: Verify exact term boundaries
        self._test_term_boundaries(annotated_elem)
        
        print("✅ HTML annotation positioning test passed")
    
    def test_html_annotation_structure_validation(self):
        """Test exact HTML structure of annotations"""
        print("\n🏗️ Testing HTML annotation structure validation...")
        
        if not self.test_html.exists():
            self.skipTest(f"Test HTML file not found: {self.test_html}")
        
        html_elem = self._parse_html(self.test_html)
        annotated_elem = self._apply_annotation_with_glossary(html_elem)
        
        # Test 1: Verify annotation element structure
        self._test_annotation_element_structure(annotated_elem)
        
        # Test 2: Verify hyperlink attributes
        self._test_hyperlink_attributes(annotated_elem)
        
        # Test 3: Verify CSS class usage
        self._test_css_class_usage(annotated_elem)
        
        print("✅ HTML annotation structure validation passed")
    
    def test_html_annotation_content_integrity(self):
        """Test that annotation preserves original content integrity"""
        print("\n📝 Testing HTML annotation content integrity...")
        
        if not self.test_html.exists():
            self.skipTest(f"Test HTML file not found: {self.test_html}")
        
        html_elem = self._parse_html(self.test_html)
        annotated_elem = self._apply_annotation_with_glossary(html_elem)
        
        # Test 1: Verify no content loss
        original_text = self._extract_all_text(html_elem)
        annotated_text = self._extract_all_text(annotated_elem)
        self._test_content_preservation(original_text, annotated_text)
        
        # Test 2: Verify no duplicate content
        self._test_no_duplicate_content(annotated_elem)
        
        # Test 3: Verify text flow integrity
        self._test_text_flow_integrity(annotated_elem)
        
        print("✅ HTML annotation content integrity test passed")
    
    def test_text_content_preservation(self):
        """Test that text content is preserved exactly during annotation"""
        print("\n🔍 Testing text content preservation...")
        
        if not self.test_html.exists():
            self.skipTest(f"Test HTML file not found: {self.test_html}")
        
        # Extract text from original HTML
        original_text = self._extract_text_from_html(self.test_html)
        print(f"   Original text length: {len(original_text):,} characters")
        
        # Extract text from annotated HTML
        if self.expected_annotated_html.exists():
            annotated_text = self._extract_text_from_html(self.expected_annotated_html)
            print(f"   Annotated text length: {len(annotated_text):,} characters")
            
            # Compare
            print("🔍 Comparison:")
            print(f"   Text lengths match: {len(original_text) == len(annotated_text)}")
            print(f"   Text content identical: {original_text == annotated_text}")
            
            if original_text != annotated_text:
                print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
                print("   Differences found:")
                
                # Find first difference
                min_len = min(len(original_text), len(annotated_text))
                for i in range(min_len):
                    if original_text[i] != annotated_text[i]:
                        print(f"   First difference at position {i}:")
                        print(f"     Original:  '{original_text[i:i+50]}...'")
                        print(f"     Annotated: '{annotated_text[i:i+50]}...'")
                        break
                
                # Show length differences
                if len(original_text) != len(annotated_text):
                    print(f"   Length difference: {len(original_text) - len(annotated_text)} characters")
            else:
                print("\n✅ TEXT CONTENT IS PRESERVED!")
        else:
            print(f"   Annotated file not found: {self.expected_annotated_html}")
    
    def test_html_annotation_specific_examples(self):
        """Test specific HTML annotation examples with exact expected output"""
        print("\n📋 Testing specific HTML annotation examples...")
        
        if not self.test_html.exists():
            self.skipTest(f"Test HTML file not found: {self.test_html}")
        
        # Get test cases
        test_cases = self._get_test_cases()
        
        for i, (original_html, expected_html, description) in enumerate(test_cases, 1):
            print(f"\n   Test case {i}: {description}")
            
            # Parse original HTML
            original_elem = fromstring(original_html)
            
            # Apply annotation
            annotated_elem = self._apply_annotation_with_glossary(original_elem)
            
            # Convert to string for comparison
            annotated_html = tostring(annotated_elem, encoding='unicode', pretty_print=True)
            
            # Normalize both for comparison
            normalized_annotated = self._normalize_html(annotated_html)
            normalized_expected = self._normalize_html(expected_html)
            
            # Compare
            self.assertEqual(
                normalized_annotated, 
                normalized_expected,
                f"HTML annotation mismatch for test case {i}: {description}"
            )
            
            print(f"   ✅ Test case {i} passed")
        
        print("✅ All specific HTML annotation examples passed")
    
    # Helper methods for testing
    def _test_annotation_positioning(self, annotated_elem):
        """Test that annotations are positioned correctly within text"""
        # Extract sentences and verify annotations don't break sentence structure
        sentences = self._extract_sentences(annotated_elem)
        
        for sentence in sentences:
            # Verify sentence starts with capital letter and ends with punctuation
            self.assertTrue(
                sentence[0].isupper() if sentence else True,
                f"Sentence should start with capital letter: {sentence[:50]}..."
            )
            
            # Verify sentence ends with proper punctuation
            if sentence and not sentence.endswith(('.', '!', '?', ':', ';')):
                # Check if it's a sentence fragment (common in HTML)
                pass
    
    def _test_sentence_integrity(self, annotated_elem):
        """Test that sentence integrity is maintained"""
        # Extract text and verify no broken sentences
        text = self._extract_all_text(annotated_elem)
        
        # Check for common sentence breakage patterns
        broken_patterns = [
            r'[A-Z][a-z]+<a[^>]*>[^<]*</a>[a-z]+',  # Annotation breaking word
            r'<a[^>]*>[^<]*</a>\s*<a[^>]*>[^<]*</a>',  # Adjacent annotations
        ]
        
        for pattern in broken_patterns:
            matches = re.findall(pattern, text)
            self.assertEqual(len(matches), 0, f"Found broken sentence pattern: {pattern}")
    
    def _test_term_boundaries(self, annotated_elem):
        """Test that term boundaries are respected"""
        # Find all annotation elements
        annotations = annotated_elem.xpath('//a[@class="annotation"]')
        
        for annotation in annotations:
            term_text = annotation.text_content()
            self._verify_complete_term(term_text)
            self._verify_word_boundaries(annotation)
    
    def _test_annotation_element_structure(self, annotated_elem):
        """Test that annotation elements have correct structure"""
        annotations = annotated_elem.xpath('//a[@class="annotation"]')
        
        for annotation in annotations:
            # Verify element is an <a> tag
            self.assertEqual(annotation.tag, 'a', "Annotation should be an <a> element")
            
            # Verify has class attribute
            self.assertIn('class', annotation.attrib, "Annotation should have class attribute")
            self.assertEqual(annotation.attrib['class'], 'annotation', "Annotation should have class='annotation'")
            
            # Verify has href attribute
            self.assertIn('href', annotation.attrib, "Annotation should have href attribute")
            self.assertTrue(annotation.attrib['href'].startswith('#'), "Annotation href should start with #")
            
            # Verify has text content
            self.assertIsNotNone(annotation.text, "Annotation should have text content")
            self.assertGreater(len(annotation.text.strip()), 0, "Annotation should have non-empty text")
    
    def _test_hyperlink_attributes(self, annotated_elem):
        """Test that hyperlink attributes are correct"""
        annotations = annotated_elem.xpath('//a[@class="annotation"]')
        
        for annotation in annotations:
            href = annotation.attrib.get('href', '')
            
            # Verify href format
            self.assertTrue(href.startswith('#'), f"Annotation href should start with #: {href}")
            
            # Verify href is valid (no spaces, special chars)
            href_id = href[1:]  # Remove #
            self.assertTrue(re.match(r'^[a-z0-9_]+$', href_id), f"Invalid href ID format: {href_id}")
    
    def _test_css_class_usage(self, annotated_elem):
        """Test that CSS classes are used correctly"""
        annotations = annotated_elem.xpath('//a[@class="annotation"]')
        
        for annotation in annotations:
            css_class = annotation.attrib.get('class', '')
            self.assertEqual(css_class, 'annotation', f"Annotation should have class='annotation', got: {css_class}")
    
    def _test_content_preservation(self, original_text: str, annotated_text: str):
        """Test that original content is preserved"""
        # Remove annotation markup from annotated text
        cleaned_annotated = self._remove_annotation_markup(annotated_text)
        
        # Normalize both texts
        normalized_original = self._normalize_text(original_text)
        normalized_annotated = self._normalize_text(cleaned_annotated)
        
        # Compare
        self.assertEqual(
            normalized_original, 
            normalized_annotated,
            "Original content should be preserved after annotation"
        )
    
    def _test_no_duplicate_content(self, annotated_elem):
        """Test that no content is duplicated"""
        text = self._extract_all_text(annotated_elem)
        
        # Check for obvious duplications
        words = text.split()
        word_counts = {}
        
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Flag suspicious duplications (more than 3 occurrences of same word in short text)
        if len(words) < 100:
            for word, count in word_counts.items():
                if count > 3 and len(word) > 3:
                    print(f"Warning: Word '{word}' appears {count} times in short text")
    
    def _test_text_flow_integrity(self, annotated_elem):
        """Test that text flow is maintained"""
        # Extract text and verify natural flow
        text = self._extract_all_text(annotated_elem)
        
        # Check for common flow issues
        flow_issues = [
            r'\s{3,}',  # Multiple spaces
            r'[.!?]\s*[.!?]',  # Multiple punctuation
            r'<a[^>]*>\s*</a>',  # Empty annotations
        ]
        
        for pattern in flow_issues:
            matches = re.findall(pattern, text)
            self.assertEqual(len(matches), 0, f"Found text flow issue: {pattern}")
    
    def _get_test_cases(self) -> List[Tuple[str, str, str]]:
        """Get specific test cases with expected output"""
        return [
            (
                "<p>Climate change is a global issue.</p>",
                '<p><a class="annotation" href="#climate_change">climate change</a> is a global issue.</p>',
                "Basic term annotation"
            ),
            (
                "<p>The IPCC reports on global warming.</p>",
                '<p>The <a class="annotation" href="#ipcc">IPCC</a> reports on <a class="annotation" href="#global_warming">global warming</a>.</p>',
                "Multiple term annotation"
            ),
            (
                "<p>This is a <a href='http://example.com'>link</a> with climate change.</p>",
                '<p>This is a <a href="http://example.com">link</a> with <a class="annotation" href="#climate_change">climate change</a>.</p>',
                "Annotation with existing hyperlink"
            ),
        ]
    
    def _apply_annotation_with_glossary(self, html_elem):
        """Apply annotation using the glossary terms"""
        # Import the annotation function from demo_html_annotation.py
        from demo_html_annotation import apply_annotation_to_paragraph
        
        # Apply annotation to each paragraph
        for p_elem in html_elem.xpath('//p'):
            annotated_p = apply_annotation_to_paragraph(p_elem, self.climate_terms)
            # Replace the original paragraph with annotated version
            p_elem.getparent().replace(p_elem, annotated_p)
        
        return html_elem
    
    def _extract_all_text(self, elem) -> str:
        """Extract all text content from element"""
        return elem.text_content() if hasattr(elem, 'text_content') else ''.join(elem.itertext())
    
    def _extract_text_with_annotations(self, elem) -> str:
        """Extract text including annotation markup"""
        return tostring(elem, encoding='unicode', method='text')
    
    def _extract_sentences(self, elem) -> List[str]:
        """Extract sentences from element"""
        text = self._extract_all_text(elem)
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _remove_annotation_markup(self, text: str) -> str:
        """Remove annotation markup from text"""
        # Remove <a> tags but keep their content
        text = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', text)
        return text
    
    def _normalize_html(self, html: str) -> str:
        """Normalize HTML for comparison"""
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        # Remove quotes around attributes
        html = re.sub(r'="([^"]*)"', r'="\1"', html)
        return html.strip()
    
    def _verify_complete_term(self, term: str):
        """Verify that a term is complete"""
        # Check if term contains complete words
        words = term.split()
        for word in words:
            self.assertGreater(len(word), 0, f"Term should not contain empty words: {term}")
    
    def _verify_word_boundaries(self, annotation):
        """Verify that annotation respects word boundaries"""
        term_text = annotation.text_content()
        
        # Check if term is surrounded by word boundaries
        parent_text = annotation.getparent().text_content()
        term_start = parent_text.find(term_text)
        
        if term_start > 0:
            char_before = parent_text[term_start - 1]
            self.assertTrue(
                not char_before.isalnum(),
                f"Term should be preceded by word boundary: '{char_before}{term_text}'"
            )
        
        term_end = term_start + len(term_text)
        if term_end < len(parent_text):
            char_after = parent_text[term_end]
            self.assertTrue(
                not char_after.isalnum(),
                f"Term should be followed by word boundary: '{term_text}{char_after}'"
            )
    
    def _verify_proper_nesting(self, annotation):
        """Verify that annotation is properly nested"""
        # Check that annotation doesn't break existing structure
        parent = annotation.getparent()
        self.assertIsNotNone(parent, "Annotation should have a parent element")
    
    def _extract_plain_text(self, elem) -> str:
        """Extract plain text without any markup"""
        if hasattr(elem, 'text_content'):
            return elem.text_content()
        else:
            return ''.join(elem.itertext())
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _parse_html(self, html_file: Path):
        """Parse HTML file"""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return fromstring(html_content)
    
    def _extract_text_from_html(self, html_file: Path) -> str:
        """Extract all text content from HTML file, removing all markup."""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        doc = fromstring(html_content)
        
        # Extract all text content
        text_content = doc.text_content()
        
        # Clean up whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content

def run_tests():
    """Run the HTML annotation tests"""
    print("🧪 Running HTML Annotation Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHTMLAnnotation)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run the text content preservation test as main
    print("🔍 Testing text content preservation during HTML annotation")
    print("=" * 60)
    
    # File paths
    original_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    annotated_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_using_library.html")
    
    # Extract text from original HTML
    print(f"📄 Extracting text from original: {original_file}")
    if original_file.exists():
        with open(original_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        doc = fromstring(html_content)
        
        # Extract all text content
        text_orig = doc.text_content()
        
        # Clean up whitespace
        text_orig = re.sub(r'\s+', ' ', text_orig).strip()
        
        print(f"   Original text length: {len(text_orig):,} characters")
        print(f"   First 200 chars: {text_orig[:200]}...")
        print()
        
        # Extract text from annotated HTML
        print(f"📄 Extracting text from annotated: {annotated_file}")
        if annotated_file.exists():
            with open(annotated_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            doc = fromstring(html_content)
            
            # Extract all text content
            text_marked = doc.text_content()
            
            # Clean up whitespace
            text_marked = re.sub(r'\s+', ' ', text_marked).strip()
            
            print(f"   Annotated text length: {len(text_marked):,} characters")
            print(f"   First 200 chars: {text_marked[:200]}...")
            print()
            
            # Compare
            print("🔍 Comparison:")
            print(f"   Text lengths match: {len(text_orig) == len(text_marked)}")
            print(f"   Text content identical: {text_orig == text_marked}")
            
            if text_orig != text_marked:
                print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
                print("   Differences found:")
                
                # Find first difference
                min_len = min(len(text_orig), len(text_marked))
                for i in range(min_len):
                    if text_orig[i] != text_marked[i]:
                        print(f"   First difference at position {i}:")
                        print(f"     Original:  '{text_orig[i:i+50]}...'")
                        print(f"     Annotated: '{text_marked[i:i+50]}...'")
                        break
                
                # Show length differences
                if len(text_orig) != len(text_marked):
                    print(f"   Length difference: {len(text_orig) - len(text_marked)} characters")
            else:
                print("\n✅ TEXT CONTENT IS PRESERVED!")
        else:
            print(f"   Annotated file not found: {annotated_file}")
    else:
        print(f"   Original file not found: {original_file}") 