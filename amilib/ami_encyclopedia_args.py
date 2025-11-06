"""
Command-line argument handling for AmiEncyclopedia

Provides argument parsing and processing for encyclopedia operations
"""

from pathlib import Path
from typing import Dict, Any, Optional

from amilib.ami_args import AbstractArgs
from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.util import Util


class EncyclopediaArgs(AbstractArgs):
    """Command-line arguments for encyclopedia operations"""
    
    def __init__(self):
        super().__init__()
        self.operation = "create"
        self.input_file = None
        self.output_file = None
        self.title = "Encyclopedia"
        self.normalize = True
        self.aggregate_synonyms = True
    
    def add_subparser_args(self, subparser):
        """Add encyclopedia-specific arguments to subparser"""
        encyclopedia_parser = subparser.add_parser("ENCYCLOPEDIA", help="Encyclopedia operations")
        
        encyclopedia_parser.add_argument(
            "--input", "-i",
            type=Path,
            help="Input HTML file containing encyclopedia entries"
        )
        
        encyclopedia_parser.add_argument(
            "--output", "-o", 
            type=Path,
            help="Output file for normalized encyclopedia"
        )
        
        encyclopedia_parser.add_argument(
            "--title", "-t",
            type=str,
            default="Encyclopedia",
            help="Title for the encyclopedia"
        )
        
        encyclopedia_parser.add_argument(
            "--no-normalize",
            action="store_true",
            help="Skip Wikipedia URL normalization"
        )
        
        encyclopedia_parser.add_argument(
            "--no-synonyms",
            action="store_true", 
            help="Skip synonym aggregation"
        )
        
        encyclopedia_parser.add_argument(
            "--stats",
            action="store_true",
            help="Show encyclopedia statistics"
        )
        
        return encyclopedia_parser
    
    def process_args(self):
        """Process encyclopedia arguments"""
        self.input_file = self.args.get("input")
        self.output_file = self.args.get("output")
        self.title = self.args.get("title", "Encyclopedia")
        self.normalize = not self.args.get("no_normalize", False)
        self.aggregate_synonyms = not self.args.get("no_synonyms", False)
        self.show_stats = self.args.get("stats", False)
        
        # Validate arguments
        if not self.input_file:
            raise ValueError("Input file is required")
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if not self.output_file:
            # Generate default output filename
            self.output_file = self.input_file.parent / f"{self.input_file.stem}_normalized.html"
    
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
            encyclopedia.save_normalized_html(self.output_file)
            print(f"Normalized encyclopedia saved to: {self.output_file}")
    
    def show_statistics(self, encyclopedia: AmiEncyclopedia) -> None:
        """Display encyclopedia statistics"""
        stats = encyclopedia.get_statistics()
        
        print("\n=== Encyclopedia Statistics ===")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Normalized groups: {stats['normalized_groups']}")
        print(f"Total synonyms: {stats['total_synonyms']}")
        print(f"Compression ratio: {stats['compression_ratio']:.2f}")
        print(f"Groups with Wikipedia URL: {stats['groups_with_wikipedia_url']}")
        print("===============================\n")
    
    def run_encyclopedia_operation(self) -> None:
        """Run the encyclopedia operation"""
        try:
            # Create encyclopedia
            encyclopedia = self.create_encyclopedia()
            
            # Normalize if requested
            if self.normalize or self.aggregate_synonyms:
                encyclopedia = self.normalize_encyclopedia(encyclopedia)
            
            # Save if output specified
            if self.output_file:
                self.save_encyclopedia(encyclopedia)
            
            # Show statistics if requested
            if self.show_stats:
                self.show_statistics(encyclopedia)
                
        except Exception as e:
            print(f"Error processing encyclopedia: {e}")
            raise
















