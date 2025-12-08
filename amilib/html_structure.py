"""
HTML Structure Templating System for PDF-Converted Documents

Provides template-driven structuring of line-by-line HTML from PDF conversions.
Detects columns, sections, floating elements, indentation, and page metadata.
"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import lxml.etree as ET
from lxml.etree import _Element

from amilib.ami_html import CSSStyle, HtmlLib
from amilib.bbox import BBox
from amilib.util import Util

logger = Util.get_logger(__name__)


class TemplateLoader:
    """Loads and validates structure templates from JSON/YAML files."""

    @classmethod
    def load_template(cls, template_path: Path) -> Dict:
        """
        Load template from JSON file.
        
        :param template_path: Path to template JSON file
        :return: Template dictionary
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            template = json.load(f)
        
        cls.validate_template(template)
        return template

    @classmethod
    def validate_template(cls, template: Dict) -> None:
        """
        Validate template structure.
        
        :param template: Template dictionary
        :raises ValueError: If template is invalid
        """
        required_keys = ["document_type", "version"]
        for key in required_keys:
            if key not in template:
                raise ValueError(f"Template missing required key: {key}")


class PageMetadataDetector:
    """Detects page numbers, running titles, marginalia, and recto/verso."""

    PAGE_NUMBER_PATTERNS = [
        re.compile(r"^Page\s+(?P<number>\d+)$", re.IGNORECASE),
        re.compile(r"^(?P<number>\d+)$"),
    ]

    def __init__(self, config: Dict):
        """
        Initialize page metadata detector.
        
        :param config: Page metadata configuration from template
        """
        self.config = config
        self.page_metadata_config = config.get("page_metadata", {})

    def detect_page_metadata(self, page_elements: List[_Element], page_bbox: BBox) -> Dict:
        """
        Detect all page metadata for a page.
        
        :param page_elements: List of elements on the page
        :param page_bbox: Bounding box of the page
        :return: Dictionary with page_number, running_title, marginalia, page_side
        """
        metadata = {
            "page_number": None,
            "running_title": None,
            "marginalia": [],
            "page_side": None,
        }

        if not self.page_metadata_config.get("enabled", False):
            return metadata

        # Detect page number
        if self.page_metadata_config.get("page_numbers", {}).get("enabled", False):
            metadata["page_number"] = self._detect_page_number(
                page_elements, self.page_metadata_config["page_numbers"]
            )

        # Detect running title
        if self.page_metadata_config.get("running_titles", {}).get("enabled", False):
            metadata["running_title"] = self._detect_running_title(
                page_elements, self.page_metadata_config["running_titles"]
            )

        # Detect marginalia
        if self.page_metadata_config.get("marginalia", {}).get("enabled", False):
            metadata["marginalia"] = self._detect_marginalia(
                page_elements, self.page_metadata_config["marginalia"]
            )

        # Detect recto/verso
        if self.page_metadata_config.get("recto_verso", {}).get("enabled", False):
            metadata["page_side"] = self._detect_recto_verso(
                page_elements, metadata, self.page_metadata_config["recto_verso"]
            )

        return metadata

    def _detect_page_number(self, elements: List[_Element], config: Dict) -> Optional[int]:
        """
        Detect page number from header/footer regions.
        
        :param elements: Page elements
        :param config: Page number detection configuration
        :return: Page number or None
        """
        from amilib.xml_lib import XmlLib
        candidates = []
        regions = config.get("regions", {})
        patterns = config.get("patterns", [])

        # Compile patterns
        compiled_patterns = []
        for pattern_str in patterns:
            try:
                compiled_patterns.append(re.compile(pattern_str))
            except re.error as e:
                logger.warning(f"Invalid page number pattern: {pattern_str}, error: {e}")

        # Use default patterns if none provided
        if not compiled_patterns:
            compiled_patterns = self.PAGE_NUMBER_PATTERNS

        for elem in elements:
            y0 = CSSStyle.get_y0(elem)
            x0 = CSSStyle.get_x0(elem)
            text = XmlLib.get_text(elem).strip()

            if not text or y0 is None or x0 is None:
                continue

            # Check header region
            header_region = regions.get("header", {})
            if header_region:
                header_y_range = header_region.get("y_range", [])
                if len(header_y_range) == 2 and header_y_range[0] <= y0 <= header_y_range[1]:
                    header_x_ranges = header_region.get("x_ranges", [])
                    for x_range in header_x_ranges:
                        if len(x_range) == 2 and x_range[0] <= x0 <= x_range[1]:
                            for pattern in compiled_patterns:
                                match = pattern.match(text)
                                if match:
                                    try:
                                        page_num = int(match.group("number"))
                                        candidates.append((elem, page_num, y0))
                                        break
                                    except (ValueError, IndexError):
                                        continue

            # Check footer region
            footer_region = regions.get("footer", {})
            if footer_region:
                footer_y_range = footer_region.get("y_range", [])
                if len(footer_y_range) == 2 and y0 is not None and footer_y_range[0] <= y0 <= footer_y_range[1]:
                    footer_x_ranges = footer_region.get("x_ranges", [])
                    for x_range in footer_x_ranges:
                        if len(x_range) == 2 and x_range[0] <= x0 <= x_range[1]:
                            for pattern in compiled_patterns:
                                match = pattern.match(text)
                                if match:
                                    try:
                                        page_num = int(match.group("number"))
                                        candidates.append((elem, page_num, y0))
                                        break
                                    except (ValueError, IndexError):
                                        continue

        if candidates:
            # Sort by y-position and return first
            candidates.sort(key=lambda x: x[2])
            return candidates[0][1]

        return None

    def _detect_running_title(self, elements: List[_Element], config: Dict) -> Optional[str]:
        """
        Detect running title from header region.
        
        :param elements: Page elements
        :param config: Running title detection configuration
        :return: Running title text or None
        """
        candidates = []
        regions = config.get("regions", {})
        patterns = config.get("patterns", [])

        # Compile patterns
        compiled_patterns = []
        for pattern_str in patterns:
            try:
                compiled_patterns.append(re.compile(pattern_str))
            except re.error as e:
                logger.warning(f"Invalid running title pattern: {pattern_str}, error: {e}")

        header_region = regions.get("header", {})
        if not header_region:
            return None

        header_y_range = header_region.get("y_range", [])
        if len(header_y_range) != 2:
            return None

        from amilib.xml_lib import XmlLib
        for elem in elements:
            y0 = CSSStyle.get_y0(elem)
            text = XmlLib.get_text(elem).strip()

            if not text or y0 is None:
                continue

            if header_y_range[0] <= y0 <= header_y_range[1]:
                # If patterns provided, match against them
                if compiled_patterns:
                    for pattern in compiled_patterns:
                        if pattern.match(text):
                            candidates.append((elem, text, y0))
                            break
                else:
                    # No patterns, accept any text in header region
                    candidates.append((elem, text, y0))

        if candidates:
            # Return first candidate (sorted by y-position)
            candidates.sort(key=lambda x: x[2])
            return candidates[0][1]

        return None

    def _detect_marginalia(self, elements: List[_Element], config: Dict) -> List[Dict]:
        """
        Detect marginalia in left/right margins.
        
        :param elements: Page elements
        :param config: Marginalia detection configuration
        :return: List of marginalia dictionaries
        """
        marginalia = []
        regions = config.get("regions", {})

        left_margin = regions.get("left_margin", {})
        right_margin = regions.get("right_margin", {})

        from amilib.xml_lib import XmlLib
        for elem in elements:
            x0 = CSSStyle.get_x0(elem)
            text = XmlLib.get_text(elem).strip()

            if not text or x0 is None:
                continue

            # Check left margin
            if left_margin:
                left_x_range = left_margin.get("x_range", [])
                if len(left_x_range) == 2 and left_x_range[0] <= x0 <= left_x_range[1]:
                    marginalia.append({"side": "left", "text": text, "element": elem})

            # Check right margin
            if right_margin:
                right_x_range = right_margin.get("x_range", [])
                if len(right_x_range) == 2 and right_x_range[0] <= x0 <= right_x_range[1]:
                    marginalia.append({"side": "right", "text": text, "element": elem})

        return marginalia

    def _detect_recto_verso(
        self, elements: List[_Element], metadata: Dict, config: Dict
    ) -> str:
        """
        Determine if page is recto (right) or verso (left).
        
        :param elements: Page elements
        :param metadata: Already detected metadata
        :param config: Recto/verso detection configuration
        :return: "recto" or "verso"
        """
        recto_config = config.get("recto", {})
        verso_config = config.get("verso", {})

        # Try page number position first
        if metadata.get("page_number"):
            page_num_elem = self._find_page_number_element(elements, metadata["page_number"])
            if page_num_elem:
                x0 = CSSStyle.get_x0(page_num_elem)
                if x0 is not None:
                    recto_x_range = recto_config.get("page_number_x_range", [])
                    verso_x_range = verso_config.get("page_number_x_range", [])

                    if len(recto_x_range) == 2 and recto_x_range[0] <= x0 <= recto_x_range[1]:
                        return "recto"
                    if len(verso_x_range) == 2 and verso_x_range[0] <= x0 <= verso_x_range[1]:
                        return "verso"

        # Fallback: use running title position
        if metadata.get("running_title"):
            running_title_elem = self._find_running_title_element(
                elements, metadata["running_title"]
            )
            if running_title_elem:
                x0 = CSSStyle.get_x0(running_title_elem)
                if x0 is not None:
                    recto_x_range = recto_config.get("running_title_x_range", [])
                    verso_x_range = verso_config.get("running_title_x_range", [])

                    if len(recto_x_range) == 2 and recto_x_range[0] <= x0 <= recto_x_range[1]:
                        return "recto"
                    if len(verso_x_range) == 2 and verso_x_range[0] <= x0 <= verso_x_range[1]:
                        return "verso"

        # Default to recto (right page)
        return "recto"

    def _find_page_number_element(self, elements: List[_Element], page_number: int) -> Optional[_Element]:
        """Find element containing page number."""
        from amilib.xml_lib import XmlLib
        for elem in elements:
            text = XmlLib.get_text(elem).strip()
            if str(page_number) in text:
                for pattern in self.PAGE_NUMBER_PATTERNS:
                    if pattern.match(text):
                        return elem
        return None

    def _find_running_title_element(self, elements: List[_Element], running_title: str) -> Optional[_Element]:
        """Find element containing running title."""
        from amilib.xml_lib import XmlLib
        for elem in elements:
            text = XmlLib.get_text(elem).strip()
            if text == running_title:
                return elem
        return None


class ColumnDetector:
    """Detects column layouts (1, 2, or 3 columns) using coordinate clustering."""

    def __init__(self, config: Dict):
        """
        Initialize column detector.
        
        :param config: Column detection configuration from template
        """
        self.config = config
        self.tolerance = config.get("tolerance_px", 20)
        self.min_elements = config.get("min_elements_per_column", 5)

    def detect_columns(self, elements: List[_Element]) -> Tuple[str, Dict]:
        """
        Detect column layout and assign elements to columns.
        
        :param elements: List of elements to analyze
        :return: Tuple of (column_type, column_assignments)
        """
        if not self.config.get("enabled", False):
            return "single_column", {"single": elements}

        x_coords = []
        for elem in elements:
            try:
                x0 = CSSStyle.get_x0(elem)
                if x0 is not None:
                    x_coords.append((elem, x0))
            except (AttributeError, TypeError):
                # Element doesn't have coordinates, skip
                continue

        if not x_coords:
            return "single_column", {"single": elements}

        # Cluster x-coordinates
        clusters = self._cluster_coordinates([x for _, x in x_coords], self.tolerance)

        if len(clusters) == 1:
            return "single_column", {"single": elements}
        elif len(clusters) == 2:
            return "two_column", self._assign_to_columns(x_coords, clusters)
        elif len(clusters) == 3:
            return "three_column", self._assign_to_columns(x_coords, clusters)
        else:
            # Use dominant clusters
            return self._detect_dominant_columns(x_coords, clusters)

    def _cluster_coordinates(self, coords: List[float], tolerance: float) -> List[List[float]]:
        """
        Cluster coordinates within tolerance.
        
        :param coords: List of x-coordinates
        :param tolerance: Tolerance for clustering
        :return: List of clusters (each cluster is a list of coordinates)
        """
        if not coords:
            return []

        sorted_coords = sorted(set(coords))
        clusters = [[sorted_coords[0]]]

        for coord in sorted_coords[1:]:
            last_cluster = clusters[-1]
            if coord - last_cluster[-1] <= tolerance:
                last_cluster.append(coord)
            else:
                clusters.append([coord])

        # Filter clusters by minimum size
        filtered_clusters = [
            cluster for cluster in clusters if len(cluster) >= self.min_elements
        ]

        return filtered_clusters

    def _assign_to_columns(
        self, x_coords: List[Tuple[_Element, float]], clusters: List[List[float]]
    ) -> Dict:
        """
        Assign elements to columns based on clusters.
        
        :param x_coords: List of (element, x-coordinate) tuples
        :param clusters: List of coordinate clusters
        :return: Dictionary mapping column names to element lists
        """
        column_assignments = {}
        cluster_centers = [sum(cluster) / len(cluster) for cluster in clusters]

        for i, cluster_center in enumerate(cluster_centers):
            column_name = f"column_{i+1}"
            column_assignments[column_name] = []

        for elem, x0 in x_coords:
            # Find closest cluster
            min_distance = float("inf")
            closest_column = None
            for i, cluster_center in enumerate(cluster_centers):
                distance = abs(x0 - cluster_center)
                if distance < min_distance:
                    min_distance = distance
                    closest_column = f"column_{i+1}"

            if closest_column:
                column_assignments[closest_column].append(elem)

        return column_assignments

    def _detect_dominant_columns(
        self, x_coords: List[Tuple[_Element, float]], clusters: List[List[float]]
    ) -> Tuple[str, Dict]:
        """
        Detect dominant columns when more than 3 clusters found.
        
        :param x_coords: List of (element, x-coordinate) tuples
        :param clusters: List of coordinate clusters
        :return: Tuple of (column_type, column_assignments)
        """
        # Sort clusters by size (number of coordinates)
        sorted_clusters = sorted(clusters, key=len, reverse=True)

        # Take top 3 clusters
        top_clusters = sorted_clusters[:3]

        if len(top_clusters) == 1:
            return "single_column", {"single": [elem for elem, _ in x_coords]}
        elif len(top_clusters) == 2:
            return "two_column", self._assign_to_columns(x_coords, top_clusters)
        else:
            return "three_column", self._assign_to_columns(x_coords, top_clusters)


class HtmlStructureFormatter:
    """
    Main class for formatting HTML structure using templates.
    
    Orchestrates page-level and document-level structure detection.
    """

    def __init__(self, template: Dict):
        """
        Initialize HTML structure formatter.
        
        :param template: Template dictionary loaded from JSON
        """
        self.template = template
        self.page_metadata_detector = PageMetadataDetector(template)
        self.column_detector = ColumnDetector(template.get("column_detection", {}))

    @classmethod
    def from_template_file(cls, template_path: Path) -> "HtmlStructureFormatter":
        """
        Create formatter from template file.
        
        :param template_path: Path to template JSON file
        :return: HtmlStructureFormatter instance
        """
        template = TemplateLoader.load_template(template_path)
        return cls(template)

    def format_structure(self, html_elem: _Element) -> _Element:
        """
        Apply structure formatting to HTML element.
        
        :param html_elem: Input HTML element (should have body with page elements)
        :return: Structured HTML element
        """
        body = HtmlLib.get_body(html_elem)
        if body is None:
            logger.warning("No body element found in HTML")
            return html_elem

        # Phase 1: Page-level analysis
        page_structure = self._detect_page_structure(body)

        # Phase 2: Document-level analysis
        doc_structure = self._detect_document_structure(body, page_structure)

        # Phase 3: Apply structure
        structured_html = self._apply_structure(html_elem, page_structure, doc_structure)

        return structured_html

    def _detect_page_structure(self, body: _Element) -> Dict:
        """
        Detect page-level structure (columns, metadata, floating elements).
        
        :param body: Body element containing page elements
        :return: Page structure dictionary
        """
        # Get all page elements
        page_elements = body.xpath(".//div | .//span | .//p")

        # Detect columns
        column_type, column_assignments = self.column_detector.detect_columns(page_elements)

        # Detect page metadata
        # Create page bbox from elements
        page_bbox = self._create_page_bbox(page_elements)
        metadata = self.page_metadata_detector.detect_page_metadata(page_elements, page_bbox)

        return {
            "column_type": column_type,
            "column_assignments": column_assignments,
            "metadata": metadata,
        }

    def _detect_document_structure(self, body: _Element, page_structure: Dict) -> Dict:
        """
        Detect document-level structure (sections, hierarchy).
        
        :param body: Body element
        :param page_structure: Page-level structure
        :return: Document structure dictionary
        """
        # TODO: Implement section hierarchy detection
        # TODO: Implement indentation-based grouping
        return {}

    def _apply_structure(
        self, html_elem: _Element, page_structure: Dict, doc_structure: Dict
    ) -> _Element:
        """
        Apply detected structure to HTML element.
        
        :param html_elem: Original HTML element
        :param page_structure: Page-level structure
        :param doc_structure: Document-level structure
        :return: Structured HTML element
        """
        # TODO: Implement structure application
        # Add page metadata as data attributes
        metadata = page_structure.get("metadata", {})
        body = HtmlLib.get_body(html_elem)

        if body is not None and metadata:
            if metadata.get("page_number"):
                body.set("data-page-number", str(metadata["page_number"]))
            if metadata.get("running_title"):
                body.set("data-running-title", metadata["running_title"])
            if metadata.get("page_side"):
                body.set("data-page-side", metadata["page_side"])

        return html_elem

    def _create_page_bbox(self, elements: List[_Element]) -> BBox:
        """
        Create bounding box from elements.
        
        :param elements: List of elements
        :return: BBox representing page bounds
        """
        if not elements:
            return BBox(xy_ranges=[[0, 600], [0, 800]])

        x_coords = []
        y_coords = []

        for elem in elements:
            x0 = CSSStyle.get_x0(elem)
            x1 = CSSStyle.get_x1(elem)
            y0 = CSSStyle.get_y0(elem)
            y1 = CSSStyle.get_y1(elem)

            if x0 is not None:
                x_coords.append(x0)
            if x1 is not None:
                x_coords.append(x1)
            if y0 is not None:
                y_coords.append(y0)
            if y1 is not None:
                y_coords.append(y1)

        if x_coords and y_coords:
            x_range = [min(x_coords), max(x_coords)]
            y_range = [min(y_coords), max(y_coords)]
            return BBox(xy_ranges=[x_range, y_range])

        return BBox(xy_ranges=[[0, 600], [0, 800]])

