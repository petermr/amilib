#!/usr/bin/env python3
"""
Wikidata Service Example

This script demonstrates how to use the WikidataService
for enriching terms with Wikidata information.

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import json
from pathlib import Path
from datetime import datetime


def main():
    """Demonstrate Wikidata service functionality."""
    
    print("🌍 Wikidata Service Example")
    print("=" * 50)
    
    
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
        
        # Enrich the term
        result = service.enrich_term(term)
        
        # Store result for JSON export
        all_results["terms_enriched"].append({
            "term": term,
            "result": result
        })
        
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
                
        elif result['enrichment_status'] == 'no_entity_found':
            print("❌ No Wikidata entity found")
        else:
            print(f"⚠️  Error: {result['enrichment_status']}")
        
        print()
    
    # Demonstrate batch enrichment
    print("🔄 Batch Enrichment Example")
    print("=" * 30)
    
    batch_results = service.batch_enrich_terms(terms[:2])  # Just first 2 terms
    
    # Store batch results for JSON export
    all_results["batch_results"] = batch_results
    
    for result in batch_results:
        status = "✅" if result['enrichment_status'] == 'success' else "❌"
        print(f"{status} {result['term']}: {result['enrichment_status']}")
    
    # Demonstrate individual service methods
    print("\n🔧 Individual Service Methods")
    print("=" * 40)
    
    # Test with a known entity (Q42 - Douglas Adams)
    qid = "Q42"
    
    print(f"\n📊 Entity Summary for {qid}:")
    summary = service.get_entity_summary(qid)
    if summary:
        print(f"   Label: {summary.get('label', 'N/A')}")
        print(f"   Description: {summary.get('description', 'N/A')}")
        print(f"   Type: {summary.get('type', 'N/A')}")
    
    # Store individual method results for JSON export
    all_results["individual_methods"]["entity_summary"] = {
        "qid": qid,
        "summary": summary
    }
    
    print(f"\n🔗 Wikipedia Links for {qid}:")
    links = service.get_wikipedia_links(qid)
    for lang, url in links.items():
        print(f"   {lang}: {url}")
    
    all_results["individual_methods"]["wikipedia_links"] = {
        "qid": qid,
        "links": links
    }
    
    print(f"\n🏷️  Properties for {qid}:")
    properties = service.get_entity_properties(qid)
    for prop_name, prop_values in list(properties.items())[:3]:  # Show first 3 properties
        print(f"   {prop_name}: {len(prop_values)} values")
    
    all_results["individual_methods"]["entity_properties"] = {
        "qid": qid,
        "properties": properties
    }
    
    # Demonstrate QID validation
    print(f"\n✅ QID Validation Examples:")
    test_qids = ["Q42", "P31", "invalid", "Q", "Q12345a"]
    for test_qid in test_qids:
        is_valid = service.validate_qid(test_qid)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {test_qid}")
        
        # Store validation results for JSON export
        all_results["qid_validation"][test_qid] = is_valid
    
    # Test language-specific functionality
    print("\n🌐 Language-Specific Functionality:")
    service_hi = WikidataService(language='hi')
    print(f"   Hindi service language: {service_hi.language}")
    
    # Test Hindi search
    hindi_results = service_hi.search_entity("जलवायु परिवर्तन", max_results=2)
    print(f"   Hindi search results: {len(hindi_results)} found")
    if hindi_results:
        print(f"   First result: {hindi_results[0]['label']} ({hindi_results[0]['id']})")
    
    # Store language-specific results for JSON export
    all_results["language_specific"] = {
        "language": "hi",
        "search_term": "जलवायु परिवर्तन",
        "results": hindi_results
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
