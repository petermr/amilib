#!/usr/bin/env python3
"""
Climate Wikidata Example

This script demonstrates how to use the WikidataService
for enriching climate-related terms with Wikidata information.

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import json
from pathlib import Path
from datetime import datetime

from amilib.wikidata_service import WikidataService


def main():
    """Demonstrate Wikidata service functionality with climate terms."""
    
    print("🌍 Climate Wikidata Example")
    print("=" * 50)
    
    # Initialize the service
    service = WikidataService()
    
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
        
        # Enrich the term
        result = service.enrich_term(term)
        
        # Store result for JSON export
        term_result = {
            "term": term,
            "result": result
        }
        
        if result['enrichment_status'] == 'success':
            wikidata = result['wikidata']
            print(f"✅ Found Wikidata entity: {wikidata['id']}")
            print(f"📝 Description: {wikidata['description']}")
            print(f"🏷️  Label: {wikidata['label']}")
            print(f"🎯 Confidence: {wikidata['confidence']}")
            
            # Get additional details
            summary = wikidata['summary']
            if summary.get('aliases'):
                print(f"🔄 Aliases: {', '.join(summary['aliases'][:3])}")
            
            if summary.get('wikipedia_links', {}).get('en'):
                print(f"🌐 Wikipedia: {summary['wikipedia_links']['en']}")
            
            # Check if it's a disambiguation page
            is_disambig = service.is_wikipedia_disambiguation_page(wikidata['id'])
            if is_disambig:
                print("⚠️  This is a disambiguation page!")
                disambig_options = service.get_disambiguation_options(wikidata['id'])
                if disambig_options:
                    print(f"📋 Disambiguation options: {', '.join(disambig_options[:5])}")
            
            # Show entity type if available
            if summary.get('type'):
                print(f"🏷️  Entity Type: {summary['type']}")
            
            # Store disambiguation info for JSON export
            term_result["disambiguation"] = {
                "is_disambiguation_page": is_disambig,
                "disambiguation_options": disambig_options if is_disambig else None
            }
                
        elif result['enrichment_status'] == 'no_entity_found':
            print("❌ No Wikidata entity found")
        else:
            print(f"⚠️  Error: {result['enrichment_status']}")
        
        all_results["climate_terms_enriched"].append(term_result)
        print()
    
    # Demonstrate detailed analysis of a specific climate term
    print("🔬 Detailed Analysis: Climate Change")
    print("=" * 50)
    
    # Search for climate change specifically
    climate_change_results = service.search_entity("climate change", max_results=3)
    
    detailed_analysis = {
        "search_term": "climate change",
        "search_results": climate_change_results
    }
    
    if climate_change_results:
        primary_result = climate_change_results[0]
        qid = primary_result['id']
        
        print(f"🏆 Primary Result: {primary_result['label']} ({qid})")
        print(f"📝 Description: {primary_result['description']}")
        print(f"🎯 Confidence: {primary_result['confidence']}")
        
        # Get comprehensive summary
        print(f"\n📊 Comprehensive Summary:")
        summary = service.get_entity_summary(qid)
        
        detailed_analysis["primary_result"] = {
            "qid": qid,
            "label": primary_result['label'],
            "description": primary_result['description'],
            "confidence": primary_result['confidence'],
            "summary": summary
        }
        
        if summary:
            print(f"   Label: {summary.get('label', 'N/A')}")
            print(f"   Description: {summary.get('description', 'N/A')}")
            print(f"   Type: {summary.get('type', 'N/A')}")
            
            # Show properties
            properties = summary.get('properties', {})
            if properties:
                print(f"\n🏷️  Key Properties:")
                for prop_name, prop_values in list(properties.items())[:5]:
                    print(f"   {prop_name}: {len(prop_values)} values")
            
            # Show Wikipedia links
            wikipedia_links = summary.get('wikipedia_links', {})
            if wikipedia_links:
                print(f"\n🌐 Wikipedia Links:")
                for lang, url in list(wikipedia_links.items())[:5]:
                    print(f"   {lang}: {url}")
            
            # Check disambiguation status
            is_disambig = service.is_wikipedia_disambiguation_page(qid)
            print(f"\n⚠️  Disambiguation Page: {'Yes' if is_disambig else 'No'}")
            
            detailed_analysis["disambiguation_status"] = is_disambig
            
            if is_disambig:
                disambig_options = service.get_disambiguation_options(qid)
                if disambig_options:
                    print(f"📋 Disambiguation Options (first 10):")
                    for i, option in enumerate(disambig_options[:10], 1):
                        print(f"   {i}. {option}")
                    
                    detailed_analysis["disambiguation_options"] = disambig_options
    
    all_results["detailed_analysis"] = detailed_analysis
    
    # Demonstrate QID validation for climate-related entities
    print(f"\n✅ QID Validation Examples:")
    test_qids = ["Q7942", "Q125928", "Q12345", "invalid", "Q"]
    qid_validation_results = {}
    
    for test_qid in test_qids:
        is_valid = service.validate_qid(test_qid)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {test_qid}")
        
        qid_validation_results[test_qid] = is_valid
    
    all_results["qid_validation"] = qid_validation_results
    
    # Show batch enrichment results
    print(f"\n🔄 Batch Enrichment Summary:")
    batch_results = service.batch_enrich_terms(climate_terms[:5])  # First 5 terms
    
    success_count = sum(1 for r in batch_results if r['enrichment_status'] == 'success')
    print(f"   Successfully enriched: {success_count}/{len(batch_results)} terms")
    
    batch_summary = {
        "total_terms": len(batch_results),
        "successful_enrichments": success_count,
        "results": batch_results
    }
    
    for result in batch_results:
        status = "✅" if result['enrichment_status'] == 'success' else "❌"
        print(f"   {status} {result['term']}: {result['enrichment_status']}")
    
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
