#!/usr/bin/env python3
"""
IPCC Chapter Annotation with Keywords
Processes IPCC HTML chapters and adds hyperlinks to keyphrase dictionary entries.

This script reads IPCC chapter HTML files and annotates them with hyperlinks
to keyphrases from CSV files or AmiDictionary format. It supports both
individual chapter processing and batch processing of multiple chapters.

Usage:
    python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv
    python markup_ipcc_chapters_with_keywords.py --chapter 1,2,3 --keywords csv
    python markup_ipcc_chapters_with_keywords.py --all-chapters --keywords dictionary
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from lxml import html, etree

from amilib.ami_html import HtmlLib
from amilib.ami_dict import AmiDictionary
from amilib.core.util import Util
from amilib.search_args import AmiSearch

logger = Util.get_logger(__name__)

# Constants
IPCC_BASE_URL = "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/"
DEFAULT_CHAPTER_DIR = Path("test", "resources", "ipcc", "cleaned_content", "wg1")
DEFAULT_OUTPUT_DIR = Path("temp", "annotate", "keyphrases")
DEFAULT_DICT_BASE_URL = "https://en.wikipedia.org/wiki/"

# Chapter mapping with explicit names and URLs
CHAPTER_INFO = {
    1: {
        "name": "Framing, Context and Methods",
        "filename": "Chapter_1_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_1_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    2: {
        "name": "Changing State of the Climate System", 
        "filename": "Chapter_2_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_2_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    3: {
        "name": "Human Influence on the Climate System",
        "filename": "Chapter_3_keywords.csv", 
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_3_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    4: {
        "name": "Future Global Climate: Scenario-based Projections and Near-term Information",
        "filename": "Chapter_4_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_4_keywords.csv", 
        "html_file": "html_with_ids.html"
    },
    5: {
        "name": "Global Carbon and other Biogeochemical Cycles and Feedbacks",
        "filename": "Chapter_5_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_5_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    6: {
        "name": "Short-lived Climate Forcers",
        "filename": "Chapter_6_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_6_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    7: {
        "name": "The Earth's Energy Budget, Climate Feedbacks, and Climate Sensitivity",
        "filename": "Chapter_7_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_7_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    8: {
        "name": "Water Cycle Changes",
        "filename": "Chapter_8_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_8_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    9: {
        "name": "Ocean, Cryosphere and Sea Level Change",
        "filename": "Chapter_9_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_9_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    10: {
        "name": "Linking Global to Regional Climate Change",
        "filename": "Chapter_10_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_10_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    11: {
        "name": "Weather and Climate Extreme Events in a Changing Climate",
        "filename": "Chapter_11_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_11_keywords.csv",
        "html_file": "html_with_ids.html"
    },
    12: {
        "name": "Climate Change Information for Regional Impact and for Risk Assessment",
        "filename": "Chapter_12_keywords.csv",
        "url": "https://raw.githubusercontent.com/semanticClimate/encyclopedia/udita/Dictionary/ipcc/ipcc_wg1/ipcc_wg1_files/Chapter_12_keywords.csv",
        "html_file": "html_with_ids.html"
    }
}


class IPCCChapterAnnotator:
    """Annotates IPCC chapters with keyphrase hyperlinks."""
    
    def __init__(self, 
                 chapter_dir: Path = DEFAULT_CHAPTER_DIR,
                 output_dir: Path = DEFAULT_OUTPUT_DIR,
                 dict_base_url: str = DEFAULT_DICT_BASE_URL):
        """
        Initialize the IPCC chapter annotator.
        
        Args:
            chapter_dir: Directory containing IPCC chapter HTML files
            output_dir: Directory for annotated output files
            dict_base_url: Base URL for dictionary entries
        """
        self.chapter_dir = Path(chapter_dir)
        self.output_dir = Path(output_dir)
        self.dict_base_url = dict_base_url
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different annotation types
        self.csv_output_dir = self.output_dir / "csv_annotated"
        self.dict_output_dir = self.output_dir / "dict_annotated"
        self.csv_output_dir.mkdir(exist_ok=True)
        self.dict_output_dir.mkdir(exist_ok=True)
        
    def load_keywords_from_csv(self, chapter_num: int) -> Dict[str, Dict[str, str]]:
        """
        Load keywords from CSV file for a specific chapter.
        
        Args:
            chapter_num: Chapter number (1-12)
            
        Returns:
            Dictionary mapping lowercase terms to term info
        """
        try:
            # Get chapter information
            if chapter_num not in CHAPTER_INFO:
                logger.error(f"Chapter {chapter_num} not found in CHAPTER_INFO mapping")
                return {}
            
            chapter_info = CHAPTER_INFO[chapter_num]
            chapter_name = chapter_info["name"]
            csv_filename = chapter_info["filename"]
            csv_url = chapter_info["url"]
            
            logger.info(f"Loading keywords for Chapter {chapter_num}: {chapter_name}")
            logger.info(f"CSV filename: {csv_filename}")
            logger.info(f"CSV URL: {csv_url}")
            
            # Try to load from local file first
            local_file = self.chapter_dir / f"Chapter{chapter_num:02d}" / "marked" / "kw_counter.txt"
            if local_file.exists():
                logger.info(f"Loading keywords from local file: {local_file}")
                return self._load_from_local_counter(local_file)
            
            # Fallback to GitHub repository
            logger.info(f"Loading keywords from GitHub: {csv_url}")
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV content
            csv_content = response.text
            reader = csv.DictReader(csv_content.splitlines())
            
            keywords = {}
            for row in reader:
                term = row.get('term', '').strip()
                if term:
                    # Create dictionary entry with Wikipedia link
                    term_lower = term.lower()
                    keywords[term_lower] = {
                        'term': term,
                        'link': urljoin(self.dict_base_url, term.replace(' ', '_')),
                        'definition': f"Definition for {term}",
                        'source': 'csv'
                    }
            
            logger.info(f"Loaded {len(keywords)} keywords from CSV for Chapter {chapter_num}")
            return keywords
            
        except Exception as e:
            logger.error(f"Error loading keywords for Chapter {chapter_num}: {e}")
            return {}
    
    def _load_from_local_counter(self, counter_file: Path) -> Dict[str, Dict[str, str]]:
        """Load keywords from local Counter file."""
        try:
            with open(counter_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse Counter format: Counter({'term1': 1, 'term2': 2, ...})
            if content.startswith("Counter({") and content.endswith("})"):
                # Extract the dictionary part
                dict_str = content[9:-2]  # Remove "Counter({" and "})"
                
                # Simple parsing - this is basic but works for the format
                keywords = {}
                # Split by comma, but be careful with nested quotes
                terms = []
                current_term = ""
                in_quotes = False
                
                for char in dict_str:
                    if char == "'" and not in_quotes:
                        in_quotes = True
                    elif char == "'" and in_quotes:
                        in_quotes = False
                        if current_term.strip():
                            terms.append(current_term.strip())
                            current_term = ""
                    elif in_quotes:
                        current_term += char
                
                # Create keyword entries
                for term in terms:
                    if term and len(term) > 2:  # Filter out very short terms
                        term_lower = term.lower()
                        keywords[term_lower] = {
                            'term': term,
                            'link': urljoin(self.dict_base_url, term.replace(' ', '_')),
                            'definition': f"Definition for {term}",
                            'source': 'local_counter'
                        }
                
                logger.info(f"Loaded {len(keywords)} keywords from local counter file")
                return keywords
                
        except Exception as e:
            logger.error(f"Error parsing local counter file {counter_file}: {e}")
            return {}
    
    def load_keywords_from_dictionary(self, dict_path: Union[str, Path]) -> Dict[str, Dict[str, str]]:
        """
        Load keywords from AmiDictionary format.
        
        Args:
            dict_path: Path to dictionary file
            
        Returns:
            Dictionary mapping lowercase terms to term info
        """
        try:
            dict_path = Path(dict_path)
            if not dict_path.exists():
                logger.error(f"Dictionary file not found: {dict_path}")
                return {}
            
            # Load AmiDictionary
            ami_dict = AmiDictionary.read_dictionary(str(dict_path))
            if not ami_dict:
                logger.error(f"Failed to load dictionary from {dict_path}")
                return {}
            
            keywords = {}
            terms = ami_dict.get_terms()
            
            for term in terms:
                term_lower = term.lower()
                # Get entry info
                entry = ami_dict.get_lxml_entry(term)
                if entry is not None:
                    # Extract definition and other info
                    definition = entry.get('definition', f"Definition for {term}")
                    wikidata_id = entry.get('wikidataID', '')
                    
                    keywords[term_lower] = {
                        'term': term,
                        'link': urljoin(self.dict_base_url, term.replace(' ', '_')),
                        'definition': definition,
                        'wikidata_id': wikidata_id,
                        'source': 'dictionary'
                    }
            
            logger.info(f"Loaded {len(keywords)} keywords from dictionary")
            return keywords
            
        except Exception as e:
            logger.error(f"Error loading dictionary from {dict_path}: {e}")
            return {}
    
    def annotate_html_with_keywords(self, 
                                  html_file: Path, 
                                  keywords: Dict[str, Dict[str, str]], 
                                  output_file: Path) -> bool:
        """
        Annotate HTML file with keyword hyperlinks using amilib functionality.
        
        Args:
            html_file: Input HTML file path
            keywords: Dictionary of keywords to annotate
            output_file: Output HTML file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not html_file.exists():
                logger.error(f"HTML file not found: {html_file}")
                return False
            
            # Extract phrases from keywords for amilib
            phrases = [term_info['term'] for term_info in keywords.values()]
            
            # Use amilib's markup functionality
            logger.info(f"Using amilib to annotate {len(phrases)} phrases")
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use AmiSearch.markup_html_file_with_words_or_dictionary
            # This method expects phrases as a list of strings
            html_elem = AmiSearch.markup_html_file_with_words_or_dictionary(
                inpath=str(html_file),
                outpath=str(output_file),
                phrases=phrases,
                remove_styles=False,
                make_counter=True,
                reportpath=str(output_file.parent / f"{output_file.stem}_counter.txt")
            )
            
            if html_elem is not None:
                logger.info(f"Successfully annotated HTML file: {output_file}")
                return True
            else:
                logger.error(f"Failed to annotate HTML file: {html_file}")
                return False
            
        except Exception as e:
            logger.error(f"Error annotating HTML file {html_file}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def process_chapter(self, 
                       chapter_num: int, 
                       keyword_source: str = 'csv',
                       dict_path: Optional[Path] = None) -> bool:
        """
        Process a single chapter with keyword annotation.
        
        Args:
            chapter_num: Chapter number (1-12)
            keyword_source: Source type ('csv' or 'dictionary')
            dict_path: Path to dictionary file (if using dictionary source)
            
        Returns:
            True if successful, False otherwise
        """
        # Get chapter information
        if chapter_num not in CHAPTER_INFO:
            logger.error(f"Chapter {chapter_num} not found in CHAPTER_INFO mapping")
            return False
        
        chapter_info = CHAPTER_INFO[chapter_num]
        chapter_name = chapter_info["name"]
        html_filename = chapter_info["html_file"]
        
        logger.info(f"Processing Chapter {chapter_num}: {chapter_name}")
        logger.info(f"Using {keyword_source} keywords")
        
        # Find HTML file using explicit filename
        chapter_dir = self.chapter_dir / f"Chapter{chapter_num:02d}"
        html_file = chapter_dir / html_filename
        
        logger.info(f"Looking for HTML file: {html_file}")
        if not html_file.exists():
            logger.error(f"HTML file not found: {html_file}")
            return False
        
        # Load keywords
        if keyword_source == 'csv':
            keywords = self.load_keywords_from_csv(chapter_num)
            output_dir = self.csv_output_dir
        elif keyword_source == 'dictionary':
            if not dict_path:
                logger.error("Dictionary path required for dictionary source")
                return False
            keywords = self.load_keywords_from_dictionary(dict_path)
            output_dir = self.dict_output_dir
        else:
            logger.error(f"Unknown keyword source: {keyword_source}")
            return False
        
        if not keywords:
            logger.warning(f"No keywords loaded for Chapter {chapter_num}")
            return False
        
        # Create output file with explicit naming
        safe_chapter_name = chapter_name.replace(" ", "_").replace(":", "").replace(",", "").replace("(", "").replace(")", "")
        output_filename = f"Chapter{chapter_num:02d}_{safe_chapter_name}_annotated.html"
        output_file = output_dir / output_filename
        
        logger.info(f"Output file: {output_file}")
        
        # Annotate HTML
        success = self.annotate_html_with_keywords(html_file, keywords, output_file)
        
        if success:
            # Save keyword statistics using amilib counter
            stats_filename = f"Chapter{chapter_num:02d}_{safe_chapter_name}_stats.json"
            stats_file = output_dir / stats_filename
            
            # Get counter from amilib output
            counter_file = output_file.parent / f"{output_file.stem}_counter.txt"
            annotated_count = 0
            if counter_file.exists():
                try:
                    counter = AmiSearch.add_counts_from_outpath(str(output_file))
                    annotated_count = len(counter) if counter else 0
                except Exception as e:
                    logger.warning(f"Could not read counter file: {e}")
            
            stats = {
                'chapter': chapter_num,
                'chapter_name': chapter_name,
                'keyword_source': keyword_source,
                'csv_filename': chapter_info.get("filename", ""),
                'csv_url': chapter_info.get("url", ""),
                'html_filename': html_filename,
                'total_keywords': len(keywords),
                'annotated_terms': annotated_count,
                'input_file': str(html_file),
                'output_file': str(output_file),
                'counter_file': str(counter_file)
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
        
        return success
    
    def process_all_chapters(self, 
                           keyword_source: str = 'csv',
                           dict_path: Optional[Path] = None) -> Dict[int, bool]:
        """
        Process all available chapters.
        
        Args:
            keyword_source: Source type ('csv' or 'dictionary')
            dict_path: Path to dictionary file (if using dictionary source)
            
        Returns:
            Dictionary mapping chapter numbers to success status
        """
        logger.info(f"Processing all chapters with {keyword_source} keywords")
        
        results = {}
        chapter_dirs = [d for d in self.chapter_dir.iterdir() 
                       if d.is_dir() and d.name.startswith('Chapter')]
        
        for chapter_dir in sorted(chapter_dirs):
            # Extract chapter number
            match = re.match(r'Chapter(\d+)', chapter_dir.name)
            if match:
                chapter_num = int(match.group(1))
                results[chapter_num] = self.process_chapter(chapter_num, keyword_source, dict_path)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"Processed {successful}/{total} chapters successfully")
        
        return results


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Annotate IPCC chapters with keyphrase hyperlinks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process Chapter 1 with CSV keywords
  python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv
  
  # Process multiple chapters with CSV keywords
  python markup_ipcc_chapters_with_keywords.py --chapter 1,2,3 --keywords csv
  
  # Process all chapters with dictionary
  python markup_ipcc_chapters_with_keywords.py --all-chapters --keywords dictionary --dict-path /path/to/dict.xml
  
  # Process with custom directories
  python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv --chapter-dir /path/to/chapters --output-dir /path/to/output
  
  # Process Chapter 1 with explicit output to temp/annotate/keyphrases
  python markup_ipcc_chapters_with_keywords.py --chapter 1 --keywords csv --output-dir temp/annotate/keyphrases
        """
    )
    
    # Chapter selection
    chapter_group = parser.add_mutually_exclusive_group(required=True)
    chapter_group.add_argument(
        '--chapter', 
        type=str,
        help='Chapter number(s) to process (e.g., "1" or "1,2,3")'
    )
    chapter_group.add_argument(
        '--all-chapters', 
        action='store_true',
        help='Process all available chapters'
    )
    
    # Keyword source
    parser.add_argument(
        '--keywords',
        choices=['csv', 'dictionary'],
        default='csv',
        help='Keyword source type (default: csv)'
    )
    
    # File paths
    parser.add_argument(
        '--chapter-dir',
        type=Path,
        default=DEFAULT_CHAPTER_DIR,
        help=f'Directory containing chapter HTML files (default: {DEFAULT_CHAPTER_DIR})'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory for annotated files (default: {DEFAULT_OUTPUT_DIR})'
    )
    parser.add_argument(
        '--dict-path',
        type=Path,
        help='Path to dictionary file (required for dictionary source)'
    )
    parser.add_argument(
        '--dict-base-url',
        default=DEFAULT_DICT_BASE_URL,
        help=f'Base URL for dictionary entries (default: {DEFAULT_DICT_BASE_URL})'
    )
    
    # Processing options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.setLevel('DEBUG')
    
    # Validate arguments
    if args.keywords == 'dictionary' and not args.dict_path:
        parser.error("--dict-path is required when using dictionary source")
    
    if args.dict_path and not args.dict_path.exists():
        parser.error(f"Dictionary file not found: {args.dict_path}")
    
    # Create annotator
    annotator = IPCCChapterAnnotator(
        chapter_dir=args.chapter_dir,
        output_dir=args.output_dir,
        dict_base_url=args.dict_base_url
    )
    
    # Process chapters
    if args.all_chapters:
        results = annotator.process_all_chapters(
            keyword_source=args.keywords,
            dict_path=args.dict_path
        )
        
        # Print summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\n✅ Processing complete: {successful}/{total} chapters successful")
        
        for chapter_num, success in results.items():
            status = "✅" if success else "❌"
            print(f"  Chapter {chapter_num}: {status}")
    
    else:
        # Parse chapter numbers
        try:
            chapter_nums = [int(x.strip()) for x in args.chapter.split(',')]
        except ValueError:
            parser.error("Invalid chapter numbers. Use format like '1' or '1,2,3'")
        
        # Process each chapter
        results = {}
        for chapter_num in chapter_nums:
            success = annotator.process_chapter(
                chapter_num=chapter_num,
                keyword_source=args.keywords,
                dict_path=args.dict_path
            )
            results[chapter_num] = success
            
            status = "✅" if success else "❌"
            print(f"Chapter {chapter_num}: {status}")
        
        # Print summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\n✅ Processing complete: {successful}/{total} chapters successful")


if __name__ == "__main__":
    main()
