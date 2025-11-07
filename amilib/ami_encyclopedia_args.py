"""
Command-line argument handling for AmiEncyclopedia

Provides argument parsing and processing for encyclopedia operations
"""

import argparse
import copy
import logging
import lxml.etree as ET
from pathlib import Path
from typing import Dict, Any, Optional

from amilib.ami_args import AbstractArgs
from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.util import Util
from amilib.wikimedia import WikipediaPage

logger = Util.get_logger(__name__)

# Constants for figures
FIGURES = "figures"
WIKIPEDIA = "wikipedia"
WIKIDATA = "wikidata"


class EncyclopediaArgs(AbstractArgs):
    """Command-line arguments for encyclopedia operations"""
    
    def __init__(self):
        super().__init__()
        self.subparser_arg = "ENCYCLOPEDIA"
        self.operation = "create"
        self.input_file = None
        self.output_file = None
        self.title = "Encyclopedia"
        self.normalize = True
        self.aggregate_synonyms = True
        self.figures = None
    
    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        arg_dict = dict()
        arg_dict["inpath"] = None
        arg_dict["outpath"] = None
        arg_dict["title"] = "Encyclopedia"
        arg_dict["no_normalize"] = False
        arg_dict["no_synonyms"] = False
        arg_dict["stats"] = False
        arg_dict[FIGURES] = None
        return arg_dict
    
    def add_arguments(self):
        """Add encyclopedia-specific arguments"""
        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        
        self.parser.description = 'Encyclopedia operations'
        
        self.parser.add_argument(
            "--inpath", "-i",
            type=str,
            help="Input HTML file containing encyclopedia entries"
        )
        
        self.parser.add_argument(
            "--outpath", "-o", 
            type=str,
            help="Output file for normalized encyclopedia"
        )
        
        self.parser.add_argument(
            "--title", "-t",
            type=str,
            default="Encyclopedia",
            help="Title for the encyclopedia"
        )
        
        self.parser.add_argument(
            "--no-normalize",
            action="store_true",
            help="Skip Wikidata ID normalization"
        )
        
        self.parser.add_argument(
            "--no-synonyms",
            action="store_true", 
            help="Skip synonym aggregation"
        )
        
        self.parser.add_argument(
            "--stats",
            action="store_true",
            help="Show encyclopedia statistics"
        )
        
        self.parser.add_argument(
            f"--{FIGURES}",
            type=str,
            nargs="*",
            default="None",
            choices=["None", WIKIPEDIA, WIKIDATA],
            help=f"sources for figures: "
                 f"'{WIKIPEDIA}' uses infobox or first thumbnail, {WIKIDATA} uses first figure"
        )
    
    def process_args(self):
        """Process encyclopedia arguments"""
        logger.debug(f"ENCYCLOPEDIA process_args {self.arg_dict}")
        if not self.arg_dict:
            logger.debug(f"no arg_dict given, no action")
            return
        
        self.input_file = self.arg_dict.get("inpath")
        self.output_file = self.arg_dict.get("outpath")
        self.title = self.arg_dict.get("title", "Encyclopedia")
        self.normalize = not self.arg_dict.get("no_normalize", False)
        self.aggregate_synonyms = not self.arg_dict.get("no_synonyms", False)
        self.show_stats = self.arg_dict.get("stats", False)
        self.figures = self.arg_dict.get(FIGURES)
        if self.figures == "None":
            self.figures = None
        
        # Convert string paths to Path objects
        if self.input_file:
            self.input_file = Path(self.input_file)
        if self.output_file:
            self.output_file = Path(self.output_file)
        
        # Validate arguments
        if not self.input_file:
            raise ValueError("Input file (--inpath) is required")
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if not self.output_file:
            # Generate default output filename
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_normalized.html"
        
        # Run the encyclopedia operation
        self.run_encyclopedia_operation()
    
    def create_encyclopedia(self) -> AmiEncyclopedia:
        """Create encyclopedia from input file"""
        encyclopedia = AmiEncyclopedia(title=self.title)
        encyclopedia.create_from_html_file(self.input_file)
        return encyclopedia
    
    def normalize_encyclopedia(self, encyclopedia: AmiEncyclopedia) -> AmiEncyclopedia:
        """Normalize encyclopedia by Wikipedia URL"""
        if self.normalize:
            encyclopedia.normalize_by_wikipedia_url()
        
        if self.aggregate_synonyms:
            encyclopedia.aggregate_synonyms()
        
        return encyclopedia
    
    def save_encyclopedia(self, encyclopedia: AmiEncyclopedia) -> None:
        """Save normalized encyclopedia to output file"""
        if self.output_file:
            encyclopedia.save_wiki_normalized_html(self.output_file)
            print(f"Normalized encyclopedia saved to: {self.output_file}")
    
    def add_figures(self, encyclopedia: AmiEncyclopedia) -> None:
        """Add figures to encyclopedia entries from Wikipedia or Wikidata"""
        if encyclopedia.entries is None or len(encyclopedia.entries) == 0:
            logger.warning("No entries to add figures to")
            return
        
        # Determine figure source
        figure_source = None
        if isinstance(self.figures, list) and len(self.figures) > 0:
            figure_source = self.figures[0]
        elif isinstance(self.figures, str):
            figure_source = self.figures
        
        if figure_source not in (WIKIPEDIA, WIKIDATA):
            logger.warning(f"Unknown figure source: {figure_source}, skipping figures")
            return
        
        logger.info(f"Adding figures from {figure_source} to {len(encyclopedia.entries)} entries")
        
        # Add figures to entries
        for entry in encyclopedia.entries:
            term = entry.get('term') or entry.get('search_term', '')
            if not term:
                continue
            
            try:
                if figure_source == WIKIPEDIA:
                    # Look up Wikipedia page
                    wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
                    if wikipedia_page is not None:
                        # Extract figure from Wikipedia page
                        figure_elem = self._extract_figure_from_wikipedia(wikipedia_page)
                        if figure_elem is not None:
                            entry['figure_html'] = figure_elem
                            logger.debug(f"Added figure for {term}")
                elif figure_source == WIKIDATA:
                    # TODO: Implement Wikidata figure extraction
                    logger.warning(f"Wikidata figure extraction not yet implemented")
            except Exception as e:
                logger.warning(f"Error adding figure for {term}: {e}")
    
    def _extract_figure_from_wikipedia(self, wikipedia_page: WikipediaPage):
        """Extract figure from Wikipedia page (infobox or first thumbnail)"""
        # Try to get figure from infobox first
        a_elem = wikipedia_page.extract_a_elem_with_image_from_infobox()
        if a_elem is not None:
            figure_div = ET.Element("div")
            figure_div.attrib["title"] = "figure"
            copied_elem = copy.deepcopy(a_elem)
            self._fix_image_urls(copied_elem)
            figure_div.append(copied_elem)
            return figure_div
        
        # Try to get first figure element
        figures = wikipedia_page.html_elem.xpath(".//figure")
        if len(figures) > 0:
            figure_div = ET.Element("div")
            figure_div.attrib["title"] = "figure"
            copied_figure = copy.deepcopy(figures[0])
            self._fix_image_urls(copied_figure)
            figure_div.append(copied_figure)
            return figure_div
        
        return None
    
    def _fix_image_urls(self, element):
        """Fix relative image URLs to absolute URLs"""
        wikipedia_base = "https://en.wikipedia.org"
        
        # Fix img src attributes
        img_elements = element.xpath(".//img[@src]")
        for img in img_elements:
            src = img.get('src', '')
            if src:
                # Convert protocol-relative URL (//upload.wikimedia.org/...) to https://
                if src.startswith('//'):
                    img.set('src', f"https:{src}")
                # Convert relative URL to absolute
                elif not src.startswith('http'):
                    if src.startswith('/'):
                        # Absolute path on Wikipedia
                        img.set('src', f"{wikipedia_base}{src}")
                    else:
                        # Relative path - prepend Wikipedia base
                        img.set('src', f"{wikipedia_base}/{src}")
        
        # Fix a href attributes that point to image files or Wikipedia pages
        a_elements = element.xpath(".//a[@href]")
        for a in a_elements:
            href = a.get('href', '')
            if href and not href.startswith('http'):
                # Convert protocol-relative URL
                if href.startswith('//'):
                    a.set('href', f"https:{href}")
                # Convert relative Wikipedia URLs
                elif href.startswith('/'):
                    a.set('href', f"{wikipedia_base}{href}")
                # Convert relative paths
                elif href.startswith('wiki/') or 'File:' in href or 'Special:FilePath' in href:
                    a.set('href', f"{wikipedia_base}/{href}")
    
    def show_statistics(self, encyclopedia: AmiEncyclopedia) -> None:
        """Display encyclopedia statistics"""
        stats = encyclopedia.get_statistics()
        
        print("\n=== Encyclopedia Statistics ===")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Normalized groups: {stats['normalized_groups']}")
        print(f"Total synonyms: {stats['total_synonyms']}")
        print(f"Compression ratio: {stats['compression_ratio']:.2f}")
        print("===============================\n")
    
    def run_encyclopedia_operation(self) -> None:
        """Run the encyclopedia operation"""
        try:
            # Create encyclopedia
            encyclopedia = self.create_encyclopedia()
            
            # Normalize if requested
            if self.normalize or self.aggregate_synonyms:
                encyclopedia = self.normalize_encyclopedia(encyclopedia)
            
            # Add figures if requested
            if self.figures is not None:
                self.add_figures(encyclopedia)
            
            # Save if output specified
            if self.output_file:
                self.save_encyclopedia(encyclopedia)
            
            # Show statistics if requested
            if self.show_stats:
                self.show_statistics(encyclopedia)
                
        except Exception as e:
            print(f"Error processing encyclopedia: {e}")
            raise


















