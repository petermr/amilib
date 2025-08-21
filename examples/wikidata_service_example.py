#!/usr/bin/env python3
"""
Wikidata Service Example

This script demonstrates how to use existing amilib components
for enriching terms with Wikidata information.

Author: Dictionary Editor Team
Date: August 21, 2025
"""

import json
from pathlib import Path
from datetime import datetime
from amilib.wikimedia import WikidataLookup, WikipediaPage, WikidataPage


def main():
    """Demonstrate Wikidata functionality using existing amilib."""
    
    print("🌍 Wikidata Service Example")
    print("=" * 50)
    
    # Initialize the amilib components
    wikidata_lookup = WikidataLookup()
    print("✅ Using existing amilib WikidataLookup and WikipediaPage")
    
    # Example terms to enrich
    terms = [
        "Douglas Adams",
        "climate change",
        "acetone",
        "nonexistent_term_xyz123"
    ]
    
    print(f"\n📚 Enriching {len(terms)} terms with Wikidata data...\n")
    
    # Store all results for JSON export
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "example_type": "wikidata_service_basic",
        "terms_enriched": [],
        "batch_results": [],
        "individual_methods": {},
        "qid_validation": {},
        "language_specific": {}
    }
    
    for term in terms:
        print(f"🔍 Term: {term}")
        print("-" * 30)
        
        # Enrich the term using existing amilib
        try:
            hit0_id, hit0_description, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
            
            if hit0_id and hit0_description:
                qid = hit0_id
                label = term  # Use term as label
                description = hit0_description
                
                print(f"✅ Found Wikidata entity: {qid}")
                print(f"📝 Description: {description}")
                print(f"🏷️  Label: {label}")
                
                # Try to get Wikipedia page
                try:
                    wikidata_page = WikidataPage(pqitem=qid)
                    wikipedia_url = wikidata_page.get_wikipedia_page_link(lang="en")
                    if wikipedia_url:
                        print(f"🌐 Wikipedia: {wikipedia_url}")
                except Exception as e:
                    print(f"⚠️  Could not get Wikipedia page: {e}")
                
                # Store result for JSON export
                result_data = {
                    "enrichment_status": "success",
                    "wikidata": {
                        "id": qid,
                        "label": label,
                        "description": description
                    }
                }
                
            else:
                print("❌ No Wikidata entity found")
                result_data = {
                    "enrichment_status": "no_entity_found"
                }
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
            result_data = {
                "enrichment_status": "error",
                "error": str(e)
            }
        
        # Store result for JSON export
        all_results["terms_enriched"].append({
            "term": term,
            "result": result_data
        })
        
        print()
    
    # Demonstrate batch enrichment summary
    print("🔄 Enrichment Summary")
    print("=" * 30)
    
    successful_results = [result for result in all_results["terms_enriched"] 
                         if result["result"].get("enrichment_status") == "success"]
    
    # Store batch results for JSON export
    all_results["batch_results"] = all_results["terms_enriched"][:2]  # Just first 2 terms
    
    for result in all_results["terms_enriched"]:
        status = "✅" if result["result"].get("enrichment_status") == "success" else "❌"
        enrichment_status = result["result"].get("enrichment_status", "unknown")
        print(f"{status} {result['term']}: {enrichment_status}")
    
    # Demonstrate individual methods with a known entity
    print("\n🔧 Individual Method Examples")
    print("=" * 40)
    
    # Test with climate change if we found it, otherwise use a fallback
    test_qid = "Q7942"  # Climate change QID
    
    print(f"\n📊 Testing with QID: {test_qid}")
    
    try:
        # Try to get Wikipedia page for this QID using WikidataPage
        wikidata_page = WikidataPage(pqitem=test_qid)
        wikipedia_url = wikidata_page.get_wikipedia_page_link(lang="en")
        
        if wikipedia_url:
            print(f"🌐 Wikipedia URL: {wikipedia_url}")
            
            # Check if it's a disambiguation page
            try:
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                if wikipedia_page:
                    is_disambig = wikipedia_page.is_disambiguation_page()
                    print(f"⚠️  Disambiguation: {'Yes' if is_disambig else 'No'}")
                else:
                    print("⚠️  Could not load Wikipedia page")
            except:
                print("⚠️  Could not check disambiguation status")
                
        else:
            print("❌ Could not retrieve Wikipedia URL")
            
        # Store individual method results for JSON export
        all_results["individual_methods"]["qid_test"] = {
            "qid": test_qid,
            "wikipedia_url": wikipedia_url if 'wikipedia_url' in locals() else "",
            "success": wikipedia_page is not None
        }
        
    except Exception as e:
        print(f"❌ Error testing QID {test_qid}: {e}")
        all_results["individual_methods"]["qid_test"] = {
            "qid": test_qid,
            "error": str(e)
        }
    
    # Demonstrate QID validation
    print(f"\n✅ QID Validation Examples:")
    test_qids = ["Q42", "P31", "invalid", "Q", "Q12345a"]
    for test_qid in test_qids:
        # Simple QID validation - QIDs should start with Q and be followed by digits
        is_valid = test_qid.startswith('Q') and test_qid[1:].isdigit() and len(test_qid) > 1
        status = "✅" if is_valid else "❌"
        print(f"   {status} {test_qid}")
        
        # Store validation results for JSON export
        all_results["qid_validation"][test_qid] = is_valid
    
    # Test language-specific functionality
    print("\n🌐 Language-Specific Search Example:")
    print("   Testing search with Hindi term...")
    
    try:
        # Test Hindi search using existing amilib
        hindi_term = "जलवायु परिवर्तन"  # Climate change in Hindi
        hit0_id, hit0_description, wikidata_hits = wikidata_lookup.lookup_wikidata(hindi_term)
        
        hindi_results_data = []
        if hit0_id and hit0_description:
            print(f"   Hindi search results: 1 found")
            print(f"   Result 1: {hindi_term} ({hit0_id})")
            
            hindi_results_data.append({
                "qid": hit0_id,
                "label": hindi_term,
                "description": hit0_description
            })
        else:
            print(f"   Hindi search results: 0 found")
        
        # Store language-specific results for JSON export
        all_results["language_specific"] = {
            "language": "hi",
            "search_term": hindi_term,
            "results_count": len(hindi_results_data),
            "results": hindi_results_data
        }
        
    except Exception as e:
        print(f"   ❌ Error with Hindi search: {e}")
        all_results["language_specific"] = {
            "language": "hi",
            "search_term": "जलवायु परिवर्तन",
            "error": str(e)
        }
    
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
    print("\n🎉 Example completed successfully!")


if __name__ == "__main__":
    main()
