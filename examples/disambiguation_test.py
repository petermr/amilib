#!/usr/bin/env python3
"""
Disambiguation Page Test

This script tests disambiguation page detection using existing amilib functionality.
Based on the search results, "Delhi" should lead to a disambiguation page.

Author: Dictionary Editor Team
Date: January 27, 2025
Rewritten to use existing amilib functionality
"""

import json
from pathlib import Path
from datetime import datetime

# Use existing amilib functionality instead of deleted WikidataService
from amilib.wikimedia import WikidataLookup, WikidataPage, WikipediaPage


def main():
    """Test disambiguation page detection using existing amilib functionality."""
    
    print("🔍 Disambiguation Page Test (using existing amilib)")
    print("=" * 60)
    
    # Initialize the existing amilib services
    wikidata_lookup = WikidataLookup()
    
    # Terms that should lead to disambiguation pages
    disambiguation_terms = [
        "Delhi",  # Should lead to disambiguation page based on search results
        "Delhi (disambiguation)",  # Explicit disambiguation page
        "Delhi disambiguation",  # Alternative search
        "Delhi may refer to",  # Common disambiguation phrase
        "Delhi places",  # Should find disambiguation
        "Delhi cities"  # Should find disambiguation
    ]
    
    print(f"\n📚 Testing {len(disambiguation_terms)} terms for disambiguation pages...\n")
    
    # Store all results for JSON export
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "example_type": "disambiguation_test_using_existing_amilib",
        "disambiguation_tests": [],
        "successful_disambiguation_found": False
    }
    
    for term in disambiguation_terms:
        print(f"🔍 Term: {term}")
        print("-" * 40)
        
        # Use existing amilib WikidataLookup to search for the term
        qid, description, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
        
        term_result = {
            "term": term,
            "wikidata_results": {
                "primary_qid": qid,
                "description": description,
                "all_hits": wikidata_hits
            },
            "disambiguation_analysis": []
        }
        
        if qid and wikidata_hits:
            print(f"✅ Found {len(wikidata_hits)} Wikidata results")
            print(f"   Primary: {qid} - {description}")
            
            # Analyze each Wikidata hit for disambiguation
            for i, hit_qid in enumerate(wikidata_hits[:3]):  # Check first 3
                print(f"   {i+1}. {hit_qid}")
                
                # Use existing amilib WikidataPage to get detailed info
                wikidata_page = WikidataPage(hit_qid)
                
                # Check if this entity leads to a disambiguation page
                # We'll check the Wikipedia page it links to
                wikipedia_links = wikidata_page.get_wikipedia_page_links(["en"])
                
                if wikipedia_links and 'en' in wikipedia_links:
                    wikipedia_url = wikipedia_links['en']
                    print(f"      🌐 Wikipedia: {wikipedia_url}")
                    
                    # Use existing amilib WikipediaPage to check if it's a disambiguation page
                    wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                    
                    if wikipedia_page and wikipedia_page.html_elem:
                        # Check if it's a disambiguation page by looking for disambiguation indicators
                        main_elem = wikipedia_page.get_main_element()
                        if main_elem is not None:
                            # Look for disambiguation indicators in the content
                            is_disambig = False
                            disambig_options = []
                            
                            # Check for common disambiguation patterns
                            text_content = main_elem.text_content() if hasattr(main_elem, 'text_content') else ""
                            if text_content:
                                # Look for disambiguation indicators
                                disambig_indicators = [
                                    "may refer to:",
                                    "may refer to",
                                    "disambiguation",
                                    "commonly refers to",
                                    "can refer to"
                                ]
                                
                                for indicator in disambig_indicators:
                                    if indicator.lower() in text_content.lower():
                                        is_disambig = True
                                        break
                                
                                if is_disambig:
                                    print("      🎯 DISAMBIGUATION PAGE DETECTED!")
                                    
                                    # Try to extract disambiguation options
                                    # Look for list items that might be disambiguation options
                                    list_items = main_elem.xpath(".//li")
                                    for li in list_items[:10]:  # First 10 list items
                                        li_text = li.text_content() if hasattr(li, 'text_content') else ""
                                        if li_text and len(li_text.strip()) > 3:
                                            disambig_options.append(li_text.strip())
                                    
                                    if disambig_options:
                                        print(f"      📋 Disambiguation options (first 5):")
                                        for j, option in enumerate(disambig_options[:5], 1):
                                            print(f"         {j}. {option}")
                                    
                                    disambig_analysis = {
                                        "qid": hit_qid,
                                        "is_disambiguation_page": True,
                                        "disambiguation_options": disambig_options,
                                        "wikipedia_url": wikipedia_url,
                                        "description": description
                                    }
                                    
                                    all_results["successful_disambiguation_found"] = True
                                else:
                                    print("      ❌ Not a disambiguation page")
                                    disambig_analysis = {
                                        "qid": hit_qid,
                                        "is_disambiguation_page": False,
                                        "disambiguation_options": None,
                                        "wikipedia_url": wikipedia_url,
                                        "description": description
                                    }
                                
                                term_result["disambiguation_analysis"].append(disambig_analysis)
                            else:
                                print("      ⚠️  Could not extract text content")
                        else:
                            print("      ⚠️  Could not get main element")
                    else:
                        print("      ⚠️  Could not load Wikipedia page")
                else:
                    print("      ❌ No Wikipedia link found")
        else:
            print("❌ No Wikidata results found")
        
        all_results["disambiguation_tests"].append(term_result)
        print()
    
    # Test with a known disambiguation page URL
    print("🔗 Testing with known disambiguation page URL")
    print("=" * 50)
    
    # Based on the search results, Delhi should lead to a disambiguation page
    # Let's search for "Delhi" specifically and analyze the results
    delhi_qid, delhi_desc, delhi_hits = wikidata_lookup.lookup_wikidata("Delhi")
    
    if delhi_qid and delhi_hits:
        print(f"🏆 Delhi search results: {len(delhi_hits)} found")
        
        for i, hit_qid in enumerate(delhi_hits[:3]):
            print(f"\n{i+1}. {hit_qid}")
            
            # Get detailed info using existing amilib WikidataPage
            wikidata_page = WikidataPage(hit_qid)
            description = wikidata_page.get_description()
            print(f"   Description: {description}")
            
            # Check Wikipedia links
            wikipedia_links = wikidata_page.get_wikipedia_page_links(["en"])
            if wikipedia_links and 'en' in wikipedia_links:
                wikipedia_url = wikipedia_links['en']
                print(f"   🌐 Wikipedia URL: {wikipedia_url}")
                
                # Check if this matches the expected disambiguation URL
                if 'Delhi' in wikipedia_url:
                    print("   ✅ URL contains 'Delhi' - likely the correct page")
                
                # Use existing amilib WikipediaPage to check content
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                
                if wikipedia_page and wikipedia_page.html_elem:
                    main_elem = wikipedia_page.get_main_element()
                    if main_elem is not None:
                        # Check for disambiguation indicators
                        text_content = main_elem.text_content() if hasattr(main_elem, 'text_content') else ""
                        is_disambig = False
                        
                        if text_content:
                            disambig_indicators = [
                                "may refer to:",
                                "may refer to",
                                "disambiguation",
                                "commonly refers to"
                            ]
                            
                            for indicator in disambig_indicators:
                                if indicator.lower() in text_content.lower():
                                    is_disambig = True
                                    break
                            
                            print(f"   Disambiguation page: {'Yes' if is_disambig else 'No'}")
                            
                            if is_disambig:
                                print("   🎯 DISAMBIGUATION PAGE DETECTED!")
                                
                                # Extract disambiguation options
                                list_items = main_elem.xpath(".//li")
                                disambig_options = []
                                for li in list_items[:10]:
                                    li_text = li.text_content() if hasattr(li, 'text_content') else ""
                                    if li_text and len(li_text.strip()) > 3:
                                        disambig_options.append(li_text.strip())
                                
                                if disambig_options:
                                    print(f"   📋 Disambiguation options (first 10):")
                                    for j, option in enumerate(disambig_options[:10], 1):
                                        print(f"      {j}. {option}")
                                
                                # Store this successful disambiguation result
                                all_results["successful_disambiguation_found"] = True
                                all_results["primary_disambiguation_result"] = {
                                    "term": "Delhi",
                                    "qid": hit_qid,
                                    "description": description,
                                    "wikipedia_url": wikipedia_url,
                                    "disambiguation_options": disambig_options,
                                    "is_disambiguation": True
                                }
                                break
                else:
                    print("   ⚠️  Could not load Wikipedia page")
            else:
                print("   ❌ No Wikipedia link found")
    
    # Export results to JSON
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    json_file = temp_dir / "wikimedia_examples_using_existing_amilib.json"
    
    # Load existing data if file exists
    existing_data = {}
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = {}
    
    # Add new results
    if "examples" not in existing_data:
        existing_data["examples"] = []
    
    existing_data["examples"].append(all_results)
    
    # Save to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results exported to: {json_file}")
    
    if all_results["successful_disambiguation_found"]:
        print("\n🎉 Successfully found and analyzed disambiguation pages using existing amilib!")
    else:
        print("\n⚠️  No disambiguation pages were detected. This may indicate an issue.")
    
    print("\n🎉 Disambiguation test completed using existing amilib functionality!")


if __name__ == "__main__":
    main()

