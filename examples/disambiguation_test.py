#!/usr/bin/env python3
"""
Disambiguation Page Test

This script tests the Wikidata service with terms that should lead to disambiguation pages.
Based on the search results, "Delhi" should lead to a disambiguation page.

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import json
from pathlib import Path
from datetime import datetime

from amilib.wikidata_service import WikidataService


def main():
    """Test Wikidata service with disambiguation pages."""
    
    print("🔍 Disambiguation Page Test")
    print("=" * 50)
    
    # Initialize the service
    service = WikidataService()
    
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
        "example_type": "disambiguation_test",
        "disambiguation_tests": [],
        "successful_disambiguation_found": False
    }
    
    for term in disambiguation_terms:
        print(f"🔍 Term: {term}")
        print("-" * 40)
        
        # Search for the term
        search_results = service.search_entity(term, max_results=3)
        
        term_result = {
            "term": term,
            "search_results": search_results,
            "disambiguation_analysis": []
        }
        
        if search_results:
            print(f"✅ Found {len(search_results)} search results")
            
            for i, result in enumerate(search_results):
                qid = result['id']
                print(f"   {i+1}. {result.get('label', 'No label')} ({qid})")
                
                # Check if this entity leads to a disambiguation page
                is_disambig = service.is_wikipedia_disambiguation_page(qid)
                print(f"      Disambiguation page: {'Yes' if is_disambig else 'No'}")
                
                if is_disambig:
                    print("      🎯 DISAMBIGUATION PAGE FOUND!")
                    disambig_options = service.get_disambiguation_options(qid)
                    if disambig_options:
                        print(f"      📋 Disambiguation options (first 5):")
                        for j, option in enumerate(disambig_options[:5], 1):
                            print(f"         {j}. {option}")
                    
                    # Get comprehensive information about this disambiguation page
                    summary = service.get_entity_summary(qid)
                    print(f"      📊 Summary: {summary.get('label', 'No label')}")
                    print(f"      📝 Description: {summary.get('description', 'No description')}")
                    
                    disambig_analysis = {
                        "qid": qid,
                        "is_disambiguation_page": True,
                        "disambiguation_options": disambig_options,
                        "summary": summary
                    }
                    
                    all_results["successful_disambiguation_found"] = True
                else:
                    disambig_analysis = {
                        "qid": qid,
                        "is_disambiguation_page": False,
                        "disambiguation_options": None,
                        "summary": None
                    }
                
                term_result["disambiguation_analysis"].append(disambig_analysis)
                
                # Get Wikipedia links to see what page this leads to
                wikipedia_links = service.get_wikipedia_links(qid)
                if wikipedia_links.get('en'):
                    print(f"      🌐 Wikipedia: {wikipedia_links['en']}")
                    
                    # Check if the Wikipedia URL contains disambiguation indicators
                    url = wikipedia_links['en']
                    if 'disambiguation' in url.lower() or '(disambiguation)' in url:
                        print(f"      🔗 URL indicates disambiguation page!")
                
        else:
            print("❌ No search results found")
        
        all_results["disambiguation_tests"].append(term_result)
        print()
    
    # Test with a known disambiguation page URL
    print("🔗 Testing with known disambiguation page URL")
    print("=" * 50)
    
    # Based on the search results, Delhi should lead to a disambiguation page
    # Let's search for "Delhi" specifically and analyze the results
    delhi_results = service.search_entity("Delhi", max_results=5)
    
    if delhi_results:
        print(f"🏆 Delhi search results: {len(delhi_results)} found")
        
        for i, result in enumerate(delhi_results):
            qid = result['id']
            label = result.get('label', 'No label')
            description = result.get('description', 'No description')
            
            print(f"\n{i+1}. {label} ({qid})")
            print(f"   Description: {description}")
            
            # Check if this leads to a disambiguation page
            is_disambig = service.is_wikipedia_disambiguation_page(qid)
            print(f"   Disambiguation page: {'Yes' if is_disambig else 'No'}")
            
            if is_disambig:
                print("   🎯 DISAMBIGUATION PAGE DETECTED!")
                disambig_options = service.get_disambiguation_options(qid)
                if disambig_options:
                    print(f"   📋 Disambiguation options (first 10):")
                    for j, option in enumerate(disambig_options[:10], 1):
                        print(f"      {j}. {option}")
                
                # Get the Wikipedia URL
                wikipedia_links = service.get_wikipedia_links(qid)
                if wikipedia_links.get('en'):
                    print(f"   🌐 Wikipedia URL: {wikipedia_links['en']}")
                    
                    # Check if this matches the expected disambiguation URL
                    if 'Delhi' in wikipedia_links['en']:
                        print("   ✅ URL contains 'Delhi' - likely the correct disambiguation page")
                
                # Get comprehensive summary
                summary = service.get_entity_summary(qid)
                print(f"   📊 Comprehensive Summary:")
                print(f"      Label: {summary.get('label', 'N/A')}")
                print(f"      Description: {summary.get('description', 'N/A')}")
                print(f"      Type: {summary.get('type', 'N/A')}")
                
                # Store this successful disambiguation result
                all_results["successful_disambiguation_found"] = True
                all_results["primary_disambiguation_result"] = {
                    "term": "Delhi",
                    "qid": qid,
                    "label": label,
                    "description": description,
                    "wikipedia_url": wikipedia_links.get('en'),
                    "disambiguation_options": disambig_options,
                    "summary": summary
                }
                break
    
    # Export results to JSON
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    json_file = temp_dir / "wikimedia_examples.json"
    
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
        print("\n🎉 Successfully found and analyzed disambiguation pages!")
    else:
        print("\n⚠️  No disambiguation pages were detected. This may indicate an issue.")
    
    print("\n🎉 Disambiguation test completed!")


if __name__ == "__main__":
    main()

