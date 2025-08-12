#!/usr/bin/env python3
"""
Wikipedia Description Extractor Test

This script uses amilib routines to:
1. Download Wikipedia pages for climate terms
2. Extract descriptions from the first paragraph and beyond
3. Use amilib's built-in paragraph processing capabilities

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

from amilib.wikimedia import WikipediaPage, WikipediaPara
from amilib.ami_html import HtmlUtil


class WikipediaDescriptionExtractor:
    """Extract descriptions from Wikipedia pages using amilib routines."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.results = []
        
    def extract_description_from_wikipedia(self, term):
        """
        Extract description from Wikipedia page using amilib routines.
        
        Args:
            term: The term to look up
            
        Returns:
            dict: Contains extracted description and metadata
        """
        print(f"\n🔍 Looking up '{term}' in Wikipedia...")
        print("-" * 50)
        
        result = {
            "term": term,
            "wikipedia_url": None,
            "short_description": None,  # First sentence
            "full_description": None,   # Full first paragraph
            "extended_description": None,  # Multiple paragraphs
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
            
            # Step 3: Create first paragraph wrapper using amilib
            print(f"📝 Extracting first paragraph using amilib...")
            first_para = wikipedia_page.create_first_wikipedia_para()
            
            if first_para is None:
                result["error"] = "Could not find first paragraph"
                print(f"❌ Could not find first paragraph for '{term}'")
                return result
            
            # Step 4: Extract descriptions using amilib's paragraph processing
            print(f"🔍 Extracting descriptions from paragraphs...")
            
            # Get the paragraph element
            para_element = first_para.para_element
            
            # Extract text content using amilib's HtmlUtil
            full_text = HtmlUtil.get_text_content(para_element)
            result["full_description"] = full_text
            
            # Extract short description (first sentence) using amilib's paragraph processing
            short_desc = self._extract_first_sentence_using_amilib(first_para)
            result["short_description"] = short_desc
            
            # Step 5: Extract extended description (multiple paragraphs)
            print(f"📖 Extracting extended description...")
            extended_desc = self._extract_extended_description(main_element)
            result["extended_description"] = extended_desc
            
            # Get Wikipedia URL
            if wikipedia_page.search_url:
                result["wikipedia_url"] = wikipedia_page.search_url
            
            result["success"] = True
            
            print(f"✅ Successfully extracted descriptions for '{term}'")
            print(f"📝 Short description: {short_desc[:80]}...")
            print(f"📄 Full description: {full_text[:100]}...")
            print(f"📖 Extended description: {extended_desc[:120]}...")
            
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
    
    def _extract_extended_description(self, main_element):
        """
        Extract extended description from multiple paragraphs using amilib.
        
        Args:
            main_element: The main content element
            
        Returns:
            str: Extended description from multiple paragraphs
        """
        if not main_element:
            return ""
        
        # Get first few paragraphs using amilib's xpath
        paragraphs = main_element.xpath(".//p")
        
        if not paragraphs:
            return ""
        
        # Use amilib's HtmlUtil to get clean text from first 3 paragraphs
        extended_texts = []
        for para in paragraphs[:3]:
            if para is not None:
                para_text = HtmlUtil.get_text_content(para).strip()
                if para_text:
                    extended_texts.append(para_text)
        
        # Simple join - let amilib handle the complexity
        return "\n\n".join(extended_texts)
    
    def process_climate_terms(self):
        """Process a list of climate terms to extract descriptions."""
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
        
        print("🌍 Wikipedia Description Extractor Test")
        print("=" * 60)
        print(f"📚 Processing {len(climate_terms)} climate terms...")
        print("🔍 This test extracts:")
        print("   - Short descriptions (first sentence)")
        print("   - Full descriptions (first paragraph)")
        print("   - Extended descriptions (multiple paragraphs)")
        
        for term in climate_terms:
            result = self.extract_description_from_wikipedia(term)
            self.results.append(result)
        
        return self.results
    
    def export_results(self):
        """Export results to JSON files."""
        # Create output directory
        output_dir = Path("temp")
        output_dir.mkdir(exist_ok=True)
        
        # Export detailed results
        detailed_file = output_dir / "wikipedia_descriptions_detailed.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "wikipedia_description_extraction",
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
        existing_data["wikipedia_description_extraction"] = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "wikipedia_description_extraction",
            "results": self.results
        }
        
        with open(main_output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results also added to: {main_output_file}")
    
    def print_summary(self):
        """Print a summary of the extraction results."""
        print("\n" + "=" * 60)
        print("📊 DESCRIPTION EXTRACTION SUMMARY")
        print("=" * 60)
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        print(f"✅ Successful extractions: {len(successful)}")
        print(f"❌ Failed extractions: {len(failed)}")
        print(f"📊 Success rate: {len(successful)/len(self.results)*100:.1f}%")
        
        if successful:
            print(f"\n📝 Sample descriptions extracted:")
            for i, result in enumerate(successful[:3], 1):
                print(f"\n{i}. {result['term']}")
                print(f"   Short: {result['short_description'][:80]}...")
                print(f"   Full: {result['full_description'][:100]}...")
                print(f"   Extended: {result['extended_description'][:120]}...")
        
        if failed:
            print(f"\n❌ Failed extractions:")
            for result in failed:
                print(f"   - {result['term']}: {result['error']}")


def main():
    """Run the Wikipedia description extraction test."""
    try:
        # Create and run the extractor
        extractor = WikipediaDescriptionExtractor()
        results = extractor.process_climate_terms()
        
        # Export results
        extractor.export_results()
        
        # Print summary
        extractor.print_summary()
        
        print(f"\n🎉 Wikipedia Description Extraction Test Completed!")
        print(f"📊 Extracted descriptions for {len([r for r in results if r['success']])} terms")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
