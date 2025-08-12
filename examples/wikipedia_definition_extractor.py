#!/usr/bin/env python3
"""
Wikipedia Definition Extractor Test

This script uses amilib routines to:
1. Download Wikipedia pages for climate terms
2. Extract definitions from the first paragraph
3. Add the extracted definitions to dictionary entries

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

from amilib.wikimedia import WikipediaPage, WikipediaPara
from amilib.ami_html import HtmlUtil


class WikipediaDefinitionExtractor:
    """Extract definitions from Wikipedia pages using amilib routines."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.results = []
        
    def extract_definition_from_wikipedia(self, term):
        """
        Extract definition from Wikipedia page using amilib routines.
        
        Args:
            term: The term to look up
            
        Returns:
            dict: Contains extracted definition and metadata
        """
        print(f"\n🔍 Looking up '{term}' in Wikipedia...")
        print("-" * 50)
        
        result = {
            "term": term,
            "wikipedia_url": None,
            "definition": None,
            "full_paragraph": None,
            "success": False,
            "error": None
        }
        
        try:
            # Step 1: Use amilib to download Wikipedia page
            print(f"📥 Downloading Wikipedia page for '{term}'...")
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
            
            if wikipedia_page is None:
                result["error"] = "Could not find Wikipedia page"
                print(f"❌ No Wikipedia page found for '{term}'")
                return result
            
            # Step 2: Get the main content element
            print(f"📄 Processing Wikipedia page content...")
            main_element = wikipedia_page.get_main_element()
            
            if main_element is None:
                result["error"] = "Could not extract main content"
                print(f"❌ Could not extract main content for '{term}'")
                return result
            
            # Step 3: Create first paragraph wrapper
            print(f"📝 Extracting first paragraph...")
            first_para = wikipedia_page.create_first_wikipedia_para()
            
            if first_para is None:
                result["error"] = "Could not find first paragraph"
                print(f"❌ Could not find first paragraph for '{term}'")
                return result
            
            # Step 4: Extract definition from first paragraph
            print(f"🔍 Extracting definition from first paragraph...")
            
            # Get the paragraph element
            para_element = first_para.para_element
            
            # Extract text content
            full_text = HtmlUtil.get_text_content(para_element)
            result["full_paragraph"] = full_text
            
            # Extract first sentence (definition) using amilib's paragraph processing
            definition = self._extract_first_sentence_using_amilib(first_para)
            result["definition"] = definition
            
            # Get Wikipedia URL
            if wikipedia_page.search_url:
                result["wikipedia_url"] = wikipedia_page.search_url
            
            result["success"] = True
            
            print(f"✅ Successfully extracted definition for '{term}'")
            print(f"📝 Definition: {definition[:100]}...")
            print(f"📄 Full paragraph: {full_text[:150]}...")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error processing '{term}': {str(e)}")
        
        return result
    
    def _extract_first_sentence_using_amilib(self, first_para):
        """Use amilib's existing functionality to get first sentence."""
        if not first_para or not first_para.para_element:
            return ""
        
        # Just use amilib's HtmlUtil - no custom logic
        full_text = HtmlUtil.get_text_content(first_para.para_element)
        return full_text.split('.')[0] + '.' if '.' in full_text else full_text
    
    def process_climate_terms(self):
        """Process a list of climate terms to extract definitions."""
        climate_terms = [
            "climate change",
            "global warming",
            "greenhouse effect",
            "carbon dioxide",
            "methane",
            "ocean acidification",
            "sea level rise",
            "extreme weather",
            "renewable energy",
            "solar power"
        ]
        
        print("🌍 Wikipedia Definition Extractor Test")
        print("=" * 60)
        print(f"📚 Processing {len(climate_terms)} climate terms...")
        
        for term in climate_terms:
            result = self.extract_definition_from_wikipedia(term)
            self.results.append(result)
        
        return self.results
    
    def export_results(self):
        """Export results to JSON files."""
        # Create output directory
        output_dir = Path("temp")
        output_dir.mkdir(exist_ok=True)
        
        # Export detailed results
        detailed_file = output_dir / "wikipedia_definitions_detailed.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "wikipedia_definition_extraction",
                "total_terms": len(self.results),
                "successful_extractions": len([r for r in self.results if r["success"]]),
                "failed_extractions": len([r for r in self.results if not r["success"]]),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results exported to: {detailed_file}")
        
        # Export to main examples file
        main_output_file = Path("temp/wikimedia_examples.json")
        if main_output_file.exists():
            try:
                with open(main_output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = {}
        else:
            existing_data = {}
        
        # Add our results
        existing_data["wikipedia_definition_extraction"] = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "wikipedia_definition_extraction",
            "results": self.results
        }
        
        with open(main_output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results also added to: {main_output_file}")
    
    def print_summary(self):
        """Print a summary of the extraction results."""
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        print(f"✅ Successful extractions: {len(successful)}")
        print(f"❌ Failed extractions: {len(failed)}")
        print(f"📊 Success rate: {len(successful)/len(self.results)*100:.1f}%")
        
        if successful:
            print(f"\n📝 Sample definitions extracted:")
            for i, result in enumerate(successful[:3], 1):
                print(f"\n{i}. {result['term']}")
                print(f"   Definition: {result['definition'][:100]}...")
        
        if failed:
            print(f"\n❌ Failed extractions:")
            for result in failed:
                print(f"   - {result['term']}: {result['error']}")


def main():
    """Run the Wikipedia definition extraction test."""
    try:
        # Create and run the extractor
        extractor = WikipediaDefinitionExtractor()
        results = extractor.process_climate_terms()
        
        # Export results
        extractor.export_results()
        
        # Print summary
        extractor.print_summary()
        
        print(f"\n🎉 Wikipedia Definition Extraction Test Completed!")
        print(f"📊 Extracted definitions for {len([r for r in results if r['success']])} terms")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
