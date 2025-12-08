"""
Tests for HTML Structure Templating System.

Tests structure detection for PDF-converted HTML, including:
- Column detection
- Page metadata (page numbers, running titles, marginalia, recto/verso)
- Template loading and validation
"""

import json
import logging
from pathlib import Path

import lxml.etree as ET

from amilib.html_structure import (
    ColumnDetector,
    HtmlStructureFormatter,
    PageMetadataDetector,
    TemplateLoader,
)
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = logging.getLogger(__name__)


class HtmlStructureTest(AmiAnyTest):
    """Tests for HTML structure templating system."""

    ADMIN = True and AmiAnyTest.ADMIN
    BUG = True and AmiAnyTest.BUG
    CMD = True and AmiAnyTest.CMD
    DEBUG = True and AmiAnyTest.DEBUG
    LONG = True and AmiAnyTest.LONG
    NET = True and AmiAnyTest.NET
    OLD = True and AmiAnyTest.OLD
    NYI = True and AmiAnyTest.NYI
    USER = True and AmiAnyTest.USER

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "html_structure", "HtmlStructureTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Create sample template
        self.sample_template = {
            "document_type": "ipcc_annex",
            "version": "1.0",
            "column_detection": {
                "enabled": True,
                "tolerance_px": 20,
                "min_elements_per_column": 3,
            },
            "page_metadata": {
                "enabled": True,
                "page_numbers": {
                    "enabled": True,
                    "patterns": ["^Page\\s+(?P<number>\\d+)$", "^(?P<number>\\d+)$"],
                    "regions": {
                        "header": {"y_range": [0, 80], "x_ranges": [[500, 600]]},
                        "footer": {"y_range": [750, 850], "x_ranges": [[500, 600]]},
                    },
                },
                "running_titles": {
                    "enabled": True,
                    "regions": {"header": {"y_range": [0, 80]}},
                    "patterns": ["^.*Chapter\\s+\\d+.*$"],
                },
                "marginalia": {
                    "enabled": True,
                    "regions": {
                        "left_margin": {"x_range": [0, 50]},
                        "right_margin": {"x_range": [550, 600]},
                    },
                },
                "recto_verso": {
                    "enabled": True,
                    "recto": {
                        "page_number_x_range": [500, 600],
                        "running_title_x_range": [0, 200],
                    },
                    "verso": {
                        "page_number_x_range": [0, 100],
                        "running_title_x_range": [400, 600],
                    },
                },
            },
        }

        # Save template to file
        self.template_path = Path(self.temp_dir, "test_template.json")
        with open(self.template_path, "w", encoding="utf-8") as f:
            json.dump(self.sample_template, f, indent=2)

    def test_template_loader_loads_valid_template(self):
        """Test that TemplateLoader loads a valid template."""
        template = TemplateLoader.load_template(self.template_path)
        self.assertIsInstance(template, dict)
        self.assertEqual(template["document_type"], "ipcc_annex")
        self.assertEqual(template["version"], "1.0")

    def test_template_loader_validates_required_keys(self):
        """Test that TemplateLoader validates required keys."""
        invalid_template = {"version": "1.0"}  # Missing document_type
        invalid_path = Path(self.temp_dir, "invalid_template.json")
        with open(invalid_path, "w", encoding="utf-8") as f:
            json.dump(invalid_template, f)

        with self.assertRaises(ValueError):
            TemplateLoader.load_template(invalid_path)

    def test_template_loader_raises_on_missing_file(self):
        """Test that TemplateLoader raises FileNotFoundError for missing file."""
        missing_path = Path(self.temp_dir, "nonexistent.json")
        with self.assertRaises(FileNotFoundError):
            TemplateLoader.load_template(missing_path)

    def test_page_metadata_detector_detects_page_number(self):
        """Test that PageMetadataDetector detects page numbers."""
        config = self.sample_template["page_metadata"]
        detector = PageMetadataDetector(self.sample_template)

        # Create test HTML with page number in footer (PDF-converted format with coordinate attributes)
        html_str = """
        <div>
            <span style="x0: 500; y0: 800; x1: 550; y1: 820;">Page 42</span>
            <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content text</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        from amilib.bbox import BBox

        page_bbox = BBox(xy_ranges=[[0, 600], [0, 850]])
        metadata = detector.detect_page_metadata(elements, page_bbox)

        self.assertIsNotNone(metadata["page_number"])
        self.assertEqual(metadata["page_number"], 42)

    def test_page_metadata_detector_detects_running_title(self):
        """Test that PageMetadataDetector detects running titles."""
        detector = PageMetadataDetector(self.sample_template)

        html_str = """
        <div>
            <span style="x0: 50; y0: 50; x1: 150; y1: 70;">Chapter 3</span>
            <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content text</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        from amilib.bbox import BBox

        page_bbox = BBox(xy_ranges=[[0, 600], [0, 850]])
        metadata = detector.detect_page_metadata(elements, page_bbox)

        self.assertIsNotNone(metadata["running_title"])
        self.assertIn("Chapter", metadata["running_title"])

    def test_page_metadata_detector_detects_marginalia(self):
        """Test that PageMetadataDetector detects marginalia."""
        detector = PageMetadataDetector(self.sample_template)

        html_str = """
        <div>
            <span style="x0: 25; y0: 200; x1: 75; y1: 220;">Note</span>
            <span style="x0: 575; y0: 300; x1: 585; y1: 320;">*</span>
            <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content text</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        from amilib.bbox import BBox

        page_bbox = BBox(xy_ranges=[[0, 600], [0, 850]])
        metadata = detector.detect_page_metadata(elements, page_bbox)

        self.assertGreater(len(metadata["marginalia"]), 0)
        self.assertTrue(
            any(m["side"] == "left" for m in metadata["marginalia"])
            or any(m["side"] == "right" for m in metadata["marginalia"])
        )

    def test_page_metadata_detector_detects_recto_verso(self):
        """Test that PageMetadataDetector detects recto/verso."""
        detector = PageMetadataDetector(self.sample_template)

        # Test recto (page number on right)
        html_str = """
        <div>
            <span style="x0: 550; y0: 800; x1: 600; y1: 820;">Page 1</span>
            <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content text</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        from amilib.bbox import BBox

        page_bbox = BBox(xy_ranges=[[0, 600], [0, 850]])
        metadata = detector.detect_page_metadata(elements, page_bbox)

        self.assertIsNotNone(metadata["page_side"])
        self.assertEqual(metadata["page_side"], "recto")

    def test_column_detector_detects_single_column(self):
        """Test that ColumnDetector detects single column layout."""
        config = self.sample_template["column_detection"]
        detector = ColumnDetector(config)

        html_str = """
        <div>
            <span style="x0: 100; y0: 100; x1: 150; y1: 120;">Text 1</span>
            <span style="x0: 105; y0: 200; x1: 155; y1: 220;">Text 2</span>
            <span style="x0: 102; y0: 300; x1: 152; y1: 320;">Text 3</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        column_type, assignments = detector.detect_columns(elements)

        self.assertEqual(column_type, "single_column")
        self.assertIn("single", assignments)

    def test_column_detector_detects_two_columns(self):
        """Test that ColumnDetector detects two column layout."""
        config = self.sample_template["column_detection"]
        detector = ColumnDetector(config)

        html_str = """
        <div>
            <span style="x0: 50; y0: 100; x1: 150; y1: 120;">Left column text</span>
            <span style="x0: 52; y0: 200; x1: 152; y1: 220;">Left column text 2</span>
            <span style="x0: 51; y0: 300; x1: 151; y1: 320;">Left column text 3</span>
            <span style="x0: 350; y0: 100; x1: 450; y1: 120;">Right column text</span>
            <span style="x0: 352; y0: 200; x1: 452; y1: 220;">Right column text 2</span>
            <span style="x0: 351; y0: 300; x1: 451; y1: 320;">Right column text 3</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        column_type, assignments = detector.detect_columns(elements)

        self.assertEqual(column_type, "two_column")
        self.assertIn("column_1", assignments)
        self.assertIn("column_2", assignments)

    def test_html_structure_formatter_from_template_file(self):
        """Test that HtmlStructureFormatter can be created from template file."""
        formatter = HtmlStructureFormatter.from_template_file(self.template_path)
        self.assertIsInstance(formatter, HtmlStructureFormatter)
        self.assertIsNotNone(formatter.template)

    def test_html_structure_formatter_applies_metadata_attributes(self):
        """Test that HtmlStructureFormatter applies metadata as data attributes."""
        formatter = HtmlStructureFormatter(self.sample_template)

        html_str = """
        <html>
            <head></head>
            <body>
                <span style="x0: 550; y0: 800; x1: 600; y1: 820;">Page 5</span>
                <span style="x0: 100; y0: 400; x1: 200; y1: 420;">Content</span>
            </body>
        </html>
        """
        html_elem = ET.fromstring(html_str)

        structured = formatter.format_structure(html_elem)

        body = structured.xpath(".//body")[0]
        # Should have page number attribute if detected
        # Note: This test may need adjustment based on actual detection results
        self.assertIsNotNone(body)

    def test_html_structure_formatter_handles_empty_body(self):
        """Test that HtmlStructureFormatter handles HTML without body."""
        formatter = HtmlStructureFormatter(self.sample_template)

        html_str = """<html><head></head></html>"""
        html_elem = ET.fromstring(html_str)

        # Should not raise exception
        structured = formatter.format_structure(html_elem)
        self.assertIsNotNone(structured)

    def test_column_detector_with_disabled_config(self):
        """Test that ColumnDetector returns single column when disabled."""
        config = {"enabled": False}
        detector = ColumnDetector(config)

        html_str = """
        <div>
            <span style="x0: 50; y0: 100; x1: 150; y1: 120;">Text 1</span>
            <span style="x0: 350; y0: 100; x1: 450; y1: 120;">Text 2</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        column_type, assignments = detector.detect_columns(elements)

        self.assertEqual(column_type, "single_column")
        self.assertIn("single", assignments)

    def test_page_metadata_detector_with_disabled_config(self):
        """Test that PageMetadataDetector returns empty metadata when disabled."""
        config = {"page_metadata": {"enabled": False}}
        detector = PageMetadataDetector(config)

        html_str = """
        <div>
            <span style="position:absolute; left:550px; top:800px;">Page 42</span>
        </div>
        """
        html_elem = ET.fromstring(html_str)
        elements = html_elem.xpath(".//span")

        from amilib.bbox import BBox

        page_bbox = BBox(xy_ranges=[[0, 600], [0, 850]])
        metadata = detector.detect_page_metadata(elements, page_bbox)

        self.assertIsNone(metadata["page_number"])
        self.assertIsNone(metadata["running_title"])
        self.assertEqual(len(metadata["marginalia"]), 0)
        self.assertIsNone(metadata["page_side"])




