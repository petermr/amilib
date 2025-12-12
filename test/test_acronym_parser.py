#!/usr/bin/env python3
"""
Tests for AcronymParser.

Tests parsing of acronym/abbreviation entries where definitions start with full terms.
"""
import unittest
from pathlib import Path
import lxml.etree as ET

from amilib.ami_html import HtmlUtil, HtmlLib
from scripts.glossary_processor.acronym_parser import AcronymParser
from scripts.glossary_processor.dictionary_template_constants import (
    ROLE_TERM, ROLE_DEFINITION, ROLE_ABBREVIATION, CLASS_ENTRY,
    DATA_TERM, DATA_HAS_ABBREVIATION, ANNEX_TYPE_ACRONYMS
)
from test.resources import Resources


class AcronymParserTest(unittest.TestCase):
    """Test cases for AcronymParser."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_samples_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "dictionary_test_samples")
        cls.output_dir = Path(Resources.TEMP_DIR, "test", "acronym_parser")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
    
    def test_simple_acronym_parsing(self):
        """Test parsing simple acronym where definition is just the full term."""
        # Create test entry
        entry = ET.Element("div", attrib={"class": "entry", "id": "test-entry-aum"})
        term_div = ET.SubElement(entry, "div", attrib={"role": ROLE_TERM})
        term_span = ET.SubElement(term_div, "span", attrib={"class": "role-term"})
        term_span.text = "AUM"
        
        def_div = ET.SubElement(entry, "div", attrib={"role": ROLE_DEFINITION})
        def_span = ET.SubElement(def_div, "span", attrib={"class": "role-definition"})
        def_span.text = "assets under management"
        
        # Parse entry
        modified = AcronymParser.parse_entry(entry, ANNEX_TYPE_ACRONYMS)
        
        self.assertTrue(modified, "Entry should be modified")
        
        # Check that term is now the full term
        from scripts.glossary_processor.dictionary_template_constants import CLASS_ROLE_TERM
        term_divs = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
        self.assertGreater(len(term_divs), 0, "Should have term div")
        term_spans = term_divs[0].xpath(f'.//span[@class="{CLASS_ROLE_TERM}"]')
        self.assertGreater(len(term_spans), 0, "Should have term span")
        term_text = term_spans[0].text or ''
        self.assertEqual(term_text.strip(), "assets under management", "Term should be full term")
        
        # Check that abbreviation exists
        abbrev = entry.xpath(f'.//span[@role="{ROLE_ABBREVIATION}"]')
        self.assertGreater(len(abbrev), 0, "Should have abbreviation element")
        self.assertEqual(abbrev[0].text, "AUM", "Abbreviation should be AUM")
        
        # Check data attributes
        self.assertEqual(entry.get(DATA_TERM), "assets under management")
        self.assertEqual(entry.get(DATA_HAS_ABBREVIATION), "true")
    
    def test_acronym_with_extended_definition(self):
        """Test parsing acronym with full term and additional definition text."""
        entry = ET.Element("div", attrib={"class": "entry", "id": "test-entry-ndc"})
        term_div = ET.SubElement(entry, "div", attrib={"role": ROLE_TERM})
        term_span = ET.SubElement(term_div, "span", attrib={"class": "role-term"})
        term_span.text = "NDC"
        
        def_div = ET.SubElement(entry, "div", attrib={"role": ROLE_DEFINITION})
        def_span = ET.SubElement(def_div, "span", attrib={"class": "role-definition"})
        def_span.text = "Nationally Determined Contribution. A climate action plan."
        
        # Parse entry
        modified = AcronymParser.parse_entry(entry, ANNEX_TYPE_ACRONYMS)
        
        self.assertTrue(modified, "Entry should be modified")
        
        # Check that term is the full term
        from scripts.glossary_processor.dictionary_template_constants import CLASS_ROLE_TERM, CLASS_ROLE_DEFINITION
        term_divs = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
        self.assertGreater(len(term_divs), 0, "Should have term div")
        term_spans = term_divs[0].xpath(f'.//span[@class="{CLASS_ROLE_TERM}"]')
        self.assertGreater(len(term_spans), 0, "Should have term span")
        term_text = term_spans[0].text or ''
        # Should extract full term up to sentence boundary
        # "Nationally Determined Contribution" (stops at period)
        self.assertIn("Nationally Determined Contribution", term_text, "Term should contain full term")
        # Should not include the sentence after the period
        self.assertNotIn("climate action plan", term_text, "Term should not include following sentence")
        
        # Check that definition has remaining text
        def_divs = entry.xpath(f'.//div[@role="{ROLE_DEFINITION}"]')
        if def_divs:
            def_spans = def_divs[0].xpath(f'.//span[@class="{CLASS_ROLE_DEFINITION}"]')
            if def_spans:
                def_text = def_spans[0].text or ''
                # Should have remaining definition text
                self.assertGreater(len(def_text.strip()), 0, "Should have remaining definition")
        
        # Check abbreviation
        abbrev = entry.xpath(f'.//span[@role="{ROLE_ABBREVIATION}"]')
        self.assertEqual(abbrev[0].text, "NDC")
    
    def test_ipcc_acronym(self):
        """Test parsing IPCC acronym."""
        entry = ET.Element("div", attrib={"class": "entry", "id": "test-entry-ipcc"})
        term_div = ET.SubElement(entry, "div", attrib={"role": ROLE_TERM})
        term_span = ET.SubElement(term_div, "span", attrib={"class": "role-term"})
        term_span.text = "IPCC"
        
        def_div = ET.SubElement(entry, "div", attrib={"role": ROLE_DEFINITION})
        def_span = ET.SubElement(def_div, "span", attrib={"class": "role-definition"})
        def_span.text = "Intergovernmental Panel on Climate Change"
        
        # Parse entry
        modified = AcronymParser.parse_entry(entry, ANNEX_TYPE_ACRONYMS)
        
        self.assertTrue(modified, "IPCC entry should be modified")
        
        # Check term
        from scripts.glossary_processor.dictionary_template_constants import CLASS_ROLE_TERM
        term_divs = entry.xpath(f'.//div[@role="{ROLE_TERM}"]')
        self.assertGreater(len(term_divs), 0, "Should have term div")
        term_spans = term_divs[0].xpath(f'.//span[@class="{CLASS_ROLE_TERM}"]')
        self.assertGreater(len(term_spans), 0, "Should have term span")
        term_text = term_spans[0].text or ''
        self.assertEqual(term_text.strip(), "Intergovernmental Panel on Climate Change", "Term should be full term")
        
        # Check abbreviation
        abbrev = entry.xpath(f'.//span[@role="{ROLE_ABBREVIATION}"]')
        self.assertEqual(abbrev[0].text, "IPCC")
    
    def test_parse_dictionary(self):
        """Test parsing entire dictionary."""
        html_path = Path(self.test_samples_dir, "wg3_annex_vi_acronym_examples.html")
        
        if not html_path.exists():
            self.skipTest(f"Test file not found: {html_path}")
        
        html_tree = HtmlUtil.parse_html_lxml(str(html_path))
        html_elem = html_tree.getroot()
        
        # Count entries before
        entries_before = html_elem.xpath(f'.//div[@class="{CLASS_ENTRY}"]')
        
        # Parse dictionary
        modified = AcronymParser.parse_dictionary(html_elem, ANNEX_TYPE_ACRONYMS)
        
        # Check that entries were modified
        self.assertGreater(modified, 0, "Should modify at least some entries")
        
        # Check that abbreviations were added
        abbrevs = html_elem.xpath(f'.//span[@role="{ROLE_ABBREVIATION}"]')
        self.assertGreater(len(abbrevs), 0, "Should have abbreviation elements")
        
        # Output parsed dictionary to temp/ for review
        output_path = Path(self.output_dir, "parsed_acronym_examples.html")
        HtmlLib.write_html_file(html_elem, output_path, debug=True)
    
    def test_is_acronym(self):
        """Test acronym detection."""
        self.assertTrue(AcronymParser._is_acronym("IPCC"))
        self.assertTrue(AcronymParser._is_acronym("AR6"))
        self.assertTrue(AcronymParser._is_acronym("NDC"))
        self.assertTrue(AcronymParser._is_acronym("CO2"))
        self.assertTrue(AcronymParser._is_acronym("U.S."))
        self.assertFalse(AcronymParser._is_acronym("climate"))
        self.assertFalse(AcronymParser._is_acronym("Intergovernmental Panel"))
    
    def test_could_be_full_term(self):
        """Test full term detection."""
        # Standard cases
        self.assertTrue(AcronymParser._could_be_full_term("IPCC", "Intergovernmental Panel on Climate Change"))
        self.assertTrue(AcronymParser._could_be_full_term("AUM", "assets under management"))
        self.assertTrue(AcronymParser._could_be_full_term("NDC", "Nationally Determined Contribution"))
        self.assertTrue(AcronymParser._could_be_full_term("GHG", "greenhouse gas"))
        
        # Should not match
        self.assertFalse(AcronymParser._could_be_full_term("IPCC", "International Climate Panel"))
        self.assertFalse(AcronymParser._could_be_full_term("ABC", "climate change"))


if __name__ == '__main__':
    unittest.main()

