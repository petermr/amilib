#!/usr/bin/env python3
"""
Climate Wikidata Example

This script demonstrates how to use existing amilib components
for enriching climate-related terms with Wikidata information.

Author: Dictionary Editor Team  
Date: August 21, 2025
"""

import json
from pathlib import Path
from datetime import datetime
from amilib.wikimedia import WikidataLookup, WikipediaPage, WikidataPage


def main():
    """Demonstrate Wikidata functionality with climate terms using existing amilib."""
    
    print("🌍 Climate Wikidata Example")
    print("=" * 50)
    
    # Initialize the amilib components
    wikidata_lookup = WikidataLookup()
    print("✅ Using existing amilib WikidataLookup and WikipediaPage")
    
    # Climate-related terms to enrich
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
        "solar power",
        "atmospheric circulation",
        "ice sheet melting",
        "permafrost thaw",
        "biodiversity loss",
        "climate adaptation"
    ]
    
    print(f"\n📚 Enriching {len(climate_terms)} climate terms with Wikidata data...\n")
    
    # Store all results for JSON export
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "example_type": "climate_wikidata",
        "climate_terms_enriched": [],
        "detailed_analysis": {},
        "qid_validation": {},
        "batch_enrichment": {}
    }
    
    for term in climate_terms:
        print(f"🔍 Term: {term}")
        print("-" * 40)
        
        # Enrich the term using existing amilib
        try:
            # Look up entity using WikidataLookup
            hit0_id, hit0_description, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
            
            term_result = {
                "term": term,
                "result": {}
            }
            
            if hit0_id and hit0_description:
                qid = hit0_id
                description = hit0_description
                
                print(f"✅ Found Wikidata entity: {qid}")
                print(f"📝 Description: {description}")
                
                # Get additional information using existing methods
                try:
                    # Get WikidataPage for this QID to find Wikipedia URL
                    wikidata_page = WikidataPage(pqitem=qid)
                    wikipedia_url = wikidata_page.get_wikipedia_page_link(lang="en")
                    
                    if wikipedia_url:
                        print(f"🌐 Wikipedia: {wikipedia_url}")
                    
                    # If we have a Wikipedia URL, try to get the actual Wikipedia page for disambiguation check
                    is_disambig = False
                    disambig_options = []
                    if wikipedia_url:
                        try:
                            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                            if wikipedia_page:
                                is_disambig = wikipedia_page.is_disambiguation_page()
                                if is_disambig:
                                    print("⚠️  This is a disambiguation page!")
                                    disambig_options = wikipedia_page.get_disambiguation_options() or []
                                    if disambig_options:
                                        print(f"📋 Disambiguation options: {', '.join(disambig_options[:5])}")
                        except Exception as e:
                            print(f"⚠️  Could not check disambiguation: {e}")
                    
                    # Store result for JSON export
                    result_data = {
                        "enrichment_status": "success",
                        "wikidata": {
                            "id": qid,
                            "label": term,  # Use term as label
                            "description": description,
                            "wikipedia_url": wikipedia_url,
                            "is_disambiguation": is_disambig,
                            "disambiguation_options": disambig_options
                        }
                    }
                    term_result["result"] = result_data
                    
                except Exception as e:
                    print(f"⚠️  Error extracting details: {e}")
                    result_data = {
                        "enrichment_status": "partial_success",
                        "wikidata": {
                            "id": qid,
                            "label": term,
                            "description": description,
                            "wikipedia_url": "",
                            "error": str(e)
                        }
                    }
                    term_result["result"] = result_data
                    
            else:
                print("❌ No Wikidata entity found")
                term_result["result"] = {
                    "enrichment_status": "no_entity_found"
                }
                
        except Exception as e:
            print(f"❌ Error enriching '{term}': {e}")
            term_result["result"] = {
                "enrichment_status": "error",
                "error": str(e)
            }
        
        all_results["climate_terms_enriched"].append(term_result)
        print()
    
    # Demonstrate detailed analysis of a specific climate term
    print("🔬 Detailed Analysis: Climate Change")
    print("=" * 50)
    
    # Search for climate change specifically using existing amilib
    try:
        hit0_id, hit0_description, wikidata_hits = wikidata_lookup.lookup_wikidata("climate change")
        
        detailed_analysis = {
            "search_term": "climate change",
            "search_results": wikidata_hits if wikidata_hits else []
        }
        
        if hit0_id and hit0_description:
            qid = hit0_id
            label = "climate change"
            description = hit0_description
            
            print(f"🏆 Primary Result: {label} ({qid})")
            print(f"📝 Description: {description}")
            
            # Try to get Wikipedia page using WikidataPage
            try:
                wikidata_page = WikidataPage(pqitem=qid)
                wikipedia_url = wikidata_page.get_wikipedia_page_link(lang="en")
                
                is_disambig = False
                
                if wikipedia_url:
                    try:
                        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                        if wikipedia_page:
                            is_disambig = wikipedia_page.is_disambiguation_page()
                    except:
                        is_disambig = False
                
                print(f"🌐 Wikipedia URL: {wikipedia_url}")
                print(f"⚠️  Disambiguation Page: {'Yes' if is_disambig else 'No'}")
                
                detailed_analysis["primary_result"] = {
                    "qid": qid,
                    "label": label,
                    "description": description,
                    "wikipedia_url": wikipedia_url,
                    "is_disambiguation": is_disambig
                }
                
            except Exception as e:
                print(f"⚠️  Could not retrieve Wikipedia details: {e}")
                detailed_analysis["primary_result"] = {
                    "qid": qid,
                    "label": label,
                    "description": description,
                    "error": str(e)
                }
        else:
            print("❌ No results found for 'climate change'")
            detailed_analysis["primary_result"] = None
            
    except Exception as e:
        print(f"❌ Error in detailed analysis: {e}")
        detailed_analysis = {
            "search_term": "climate change",
            "error": str(e)
        }
    
    all_results["detailed_analysis"] = detailed_analysis
    
    # Demonstrate QID validation for climate-related entities
    print(f"\n✅ QID Validation Examples:")
    test_qids = ["Q7942", "Q125928", "Q12345", "invalid", "Q"]
    qid_validation_results = {}
    
    for test_qid in test_qids:
        # Simple QID validation - QIDs should start with Q and be followed by digits
        is_valid = test_qid.startswith('Q') and test_qid[1:].isdigit() and len(test_qid) > 1
        status = "✅" if is_valid else "❌"
        print(f"   {status} {test_qid}")
        
        qid_validation_results[test_qid] = is_valid
    
    all_results["qid_validation"] = qid_validation_results
    
    # Show summary of enrichment results
    print(f"\n📊 Enrichment Summary:")
    successful_terms = [result for result in all_results["climate_terms_enriched"] 
                       if result["result"].get("enrichment_status") == "success"]
    
    print(f"   Successfully enriched: {len(successful_terms)}/{len(climate_terms)} terms")
    
    batch_summary = {
        "total_terms": len(climate_terms),
        "successful_enrichments": len(successful_terms),
        "results": all_results["climate_terms_enriched"][:5]  # First 5 terms
    }
    
    for result in all_results["climate_terms_enriched"][:5]:
        status = "✅" if result["result"].get("enrichment_status") == "success" else "❌"
        enrichment_status = result["result"].get("enrichment_status", "unknown")
        print(f"   {status} {result['term']}: {enrichment_status}")
    
    all_results["batch_enrichment"] = batch_summary
    
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
    print("\n🎉 Climate Wikidata example completed successfully!")


if __name__ == "__main__":
    main()
