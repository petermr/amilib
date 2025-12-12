#!/usr/bin/env python3
"""
Tests for IPCC Dictionary Template validation and transformation.

Tests cover:
- Template structure validation
- Entry detection and extraction
- Cross-reference handling
- Mixed content preservation
- Single vs. multi-column layouts
"""
import unittest
from pathlib import Path
import lxml.etree as ET

from amilib.ami_html import HtmlUtil, HtmlLib
from scripts.glossary_processor.dictionary_template_validator import DictionaryTemplateValidator
from scripts.glossary_processor.dictionary_template_constants import (
    CLASS_GLOSSARY, CLASS_ENTRY, ROLE_TERM, ROLE_DEFINITION,
    CLASS_ROLE_CROSS_REFERENCE, TAG_SUB, DATA_REPORT, REPORT_SYR,
    VALID_REPORTS, FILENAME_WG3_ANNEX_VI_SAMPLE, FILENAME_WG3_ANNEX_VI_CROSSREF,
    FILENAME_WG3_ANNEX_VI_MIXED_CONTENT, FILENAME_SYR_ANNEX_I_SAMPLE,
    FILENAME_WG3_ANNEX_VI_VALIDATED, FILENAME_WG3_ANNEX_VI_VALIDATION_REPORT,
    FILENAME_WG3_ANNEX_VI_EXTRACTED_ENTRIES, FILENAME_WG3_ANNEX_VI_MIXED_CONTENT_OUTPUT,
    OUTPUT_DIR_DICTIONARY_TEMPLATE, XPATH_HEAD, TAG_STYLE, FILENAME_WG3_ANNEX_VI_WITH_ITALICS,
    TAG_EM
)
from test.resources import Resources


class IPCCDictionaryTemplateTest(unittest.TestCase):
    """Test cases for IPCC Dictionary Template."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_samples_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "dictionary_test_samples")
        cls.validator = DictionaryTemplateValidator()
        # Output dictionaries to temp/ for review
        cls.output_dir = Path(Resources.TEMP_DIR, "test", "ipcc_dictionary_template")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_wg3_annex_vi_basic_structure(self):
        """Test basic structure validation for WG3 Annex VI sample."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        is_valid, errors, warnings = self.validator.validate(html_path)
        
        # Should be valid (basic structure)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        
        # Check structure
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Should have dictionary container
        containers = html_elem.xpath(f'//div[@class="{CLASS_GLOSSARY}"]')
        self.assertEqual(len(containers), 1, "Should have exactly one glossary container")
        
        # Should have entries
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        self.assertGreaterEqual(len(entries), 3, "Should have at least 3 entries")
        
        # Each entry should have term and definition
        for entry in entries:
            terms = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
            definitions = entry.xpath(f'.//div[@role="{ROLE_DEFINITION}"]')
            self.assertGreater(len(terms), 0, f"Entry {entry.get('id')} should have a term")
            self.assertGreater(len(definitions), 0, f"Entry {entry.get('id')} should have a definition")
        
        # Output validated dictionary to temp/ for review
        output_path = Path(self.output_dir, FILENAME_WG3_ANNEX_VI_VALIDATED)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)
    
    def test_wg3_annex_vi_cross_references(self):
        """Test cross-reference handling."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_CROSSREF)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Should have cross-reference spans
        cross_refs = html_elem.xpath(f'.//span[@class="{CLASS_ROLE_CROSS_REFERENCE}"]')
        self.assertGreater(len(cross_refs), 0, "Should have cross-reference elements")
        
        # Check cross-reference content
        for ref in cross_refs:
            text = ''.join(ref.itertext()).strip()
            self.assertGreater(len(text), 0, "Cross-reference should have text content")
    
    def test_wg3_annex_vi_mixed_content(self):
        """Test mixed content (subscripts, superscripts) preservation."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_MIXED_CONTENT)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Should have subscript elements
        subscripts = html_elem.xpath(f'.//{TAG_SUB}')
        self.assertGreater(len(subscripts), 0, "Should have subscript elements")
        
        # Check that subscripts are preserved in terms
        entries_with_sub = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]//div[@role="{ROLE_TERM}"]//{TAG_SUB}')
        self.assertGreater(len(entries_with_sub), 0, "Should have subscripts in terms")
        
        # Check that subscripts are preserved in definitions
        defs_with_sub = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]//div[@role="{ROLE_DEFINITION}"]//{TAG_SUB}')
        self.assertGreater(len(defs_with_sub), 0, "Should have subscripts in definitions")
    
    def test_syr_annex_i_single_column(self):
        """Test single-column layout (SYR files)."""
        html_path = Path(self.test_samples_dir, FILENAME_SYR_ANNEX_I_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        is_valid, errors, warnings = self.validator.validate(html_path)
        
        # Should be valid
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        
        # Should have SYR-specific structure
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        containers = html_elem.xpath(f'//div[@class="{CLASS_GLOSSARY}"][@{DATA_REPORT}="{REPORT_SYR}"]')
        self.assertEqual(len(containers), 1, "Should have SYR glossary container")
    
    def test_entry_id_uniqueness(self):
        """Test that entry IDs are unique."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        entry_ids = [entry.get('id') for entry in entries if entry.get('id')]
        
        # All entries should have IDs
        self.assertEqual(len(entry_ids), len(entries), "All entries should have IDs")
        
        # IDs should be unique
        unique_ids = set(entry_ids)
        self.assertEqual(len(unique_ids), len(entry_ids), "Entry IDs should be unique")
    
    def test_required_data_attributes(self):
        """Test that required data attributes are present."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        containers = html_elem.xpath(f'//div[@class="{CLASS_GLOSSARY}"]')
        self.assertEqual(len(containers), 1, "Should have glossary container")
        
        container = containers[0]
        
        # Check required attributes
        self.assertIsNotNone(container.get(DATA_REPORT), f"Should have {DATA_REPORT} attribute")
        from scripts.glossary_processor.dictionary_template_constants import DATA_ANNEX
        self.assertIsNotNone(container.get(DATA_ANNEX), f"Should have {DATA_ANNEX} attribute")
        
        # Validate report value
        report = container.get(DATA_REPORT)
        self.assertIn(report, VALID_REPORTS, f"Report should be one of {VALID_REPORTS}, got {report}")
    
    def test_term_and_definition_content(self):
        """Test that terms and definitions have non-empty content."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        
        for entry in entries:
            # Check term content
            terms = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
            for term in terms:
                term_text = ''.join(term.itertext()).strip()
                self.assertGreater(len(term_text), 0, f"Term should have content in entry {entry.get('id')}")
            
            # Check definition content
            definitions = entry.xpath(f'.//div[@role="{ROLE_DEFINITION}"]')
            for definition in definitions:
                def_text = ''.join(definition.itertext()).strip()
                self.assertGreater(len(def_text), 0, f"Definition should have content in entry {entry.get('id')}")
    
    def test_css_styles_present(self):
        """Test that CSS styles are present in head."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Should have head element
        head = html_elem.xpath(XPATH_HEAD)
        self.assertGreater(len(head), 0, "Should have head element")
        
        # Should have style element
        styles = html_elem.xpath(f'{XPATH_HEAD}/{TAG_STYLE}')
        self.assertGreater(len(styles), 0, "Should have style element")
        
        # Style should have content
        style_text = styles[0].text or ''
        self.assertGreater(len(style_text), 0, "Style element should have CSS content")
        
        # Should have role-based styles
        self.assertIn(f'[role="{ROLE_TERM}"]', style_text, "Should have term role style")
        self.assertIn(f'[role="{ROLE_DEFINITION}"]', style_text, "Should have definition role style")
    
    def test_template_validation_detailed_report(self):
        """Test detailed validation report."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        result = self.validator.validate_template_structure(html_path)
        
        # Should have validation result
        self.assertIn('is_valid', result)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        self.assertIn('statistics', result)
        
        # Should be valid
        self.assertTrue(result['is_valid'], f"Should be valid, but got errors: {result['errors']}")
        
        # Should have statistics
        stats = result['statistics']
        self.assertGreater(stats.get('entries', 0), 0, "Should have entries")
        self.assertGreater(stats.get('terms', 0), 0, "Should have terms")
        self.assertGreater(stats.get('definitions', 0), 0, "Should have definitions")
        
        # Output validation report to temp/ for review
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        output_path = Path(self.output_dir, FILENAME_WG3_ANNEX_VI_VALIDATION_REPORT)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)
    
    def test_wg3_annex_vi_italics_hyperlinks(self):
        """Test entries with italicized text that might be hyperlinks."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_WITH_ITALICS)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Should have italicized cross-reference elements
        italic_refs = html_elem.xpath(f'.//{TAG_EM}[@class="{CLASS_ROLE_CROSS_REFERENCE}"]')
        self.assertGreater(len(italic_refs), 0, "Should have italicized cross-reference elements")
        
        # Check that italicized terms are in definitions
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        found_italics = False
        for entry in entries:
            def_italics = entry.xpath(f'.//div[@role="{ROLE_DEFINITION}"]//{TAG_EM}')
            if def_italics:
                found_italics = True
                # Check that italicized text could be converted to hyperlinks
                for italic in def_italics:
                    italic_text = ''.join(italic.itertext()).strip()
                    self.assertGreater(len(italic_text), 0, "Italicized cross-reference should have text")
        
        self.assertTrue(found_italics, "Should find italicized cross-references in definitions")
        
        # Output italics dictionary to temp/ for review
        output_path = Path(self.output_dir, FILENAME_WG3_ANNEX_VI_WITH_ITALICS)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)


class IPCCDictionaryTransformationTest(unittest.TestCase):
    """Test cases for dictionary transformation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_samples_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "dictionary_test_samples")
        # Output dictionaries to temp/ for review
        cls.output_dir = Path(Resources.TEMP_DIR, "test", OUTPUT_DIR_DICTIONARY_TEMPLATE)
        cls.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_entry_extraction(self):
        """Test that entries can be extracted from HTML."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_SAMPLE)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        self.assertGreaterEqual(len(entries), 3, "Should extract at least 3 entries")
        
        # Extract term and definition for each entry
        for entry in entries:
            term_elem = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
            def_elem = entry.xpath(f'.//div[@role="{ROLE_DEFINITION}"]')
            
            self.assertGreater(len(term_elem), 0, "Entry should have term")
            self.assertGreater(len(def_elem), 0, "Entry should have definition")
            
            term_text = ''.join(term_elem[0].itertext()).strip()
            def_text = ''.join(def_elem[0].itertext()).strip()
            
            self.assertGreater(len(term_text), 0, "Term should have text")
            self.assertGreater(len(def_text), 0, "Definition should have text")
        
        # Output extracted entries to temp/ for review
        output_path = Path(self.output_dir, FILENAME_WG3_ANNEX_VI_EXTRACTED_ENTRIES)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)
    
    def test_mixed_content_preservation(self):
        """Test that mixed content (sub, sup, etc.) is preserved."""
        html_path = Path(self.test_samples_dir, FILENAME_WG3_ANNEX_VI_MIXED_CONTENT)
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Find entry with subscript
        entries = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        
        found_sub = False
        for entry in entries:
            subs = entry.xpath(f'.//{TAG_SUB}')
            if subs:
                found_sub = True
                # Check that subscript text is preserved
                for sub in subs:
                    sub_text = ''.join(sub.itertext()).strip()
                    self.assertGreater(len(sub_text), 0, "Subscript should have text")
        
        self.assertTrue(found_sub, "Should find at least one entry with subscript")
        
        # Output mixed content dictionary to temp/ for review
        output_path = Path(self.output_dir, FILENAME_WG3_ANNEX_VI_MIXED_CONTENT_OUTPUT)
        HtmlLib.write_html_file(html_elem, output_path, debug=True)


if __name__ == '__main__':
    unittest.main()

