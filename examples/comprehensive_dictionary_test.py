#!/usr/bin/env python3
"""
Comprehensive Dictionary Test - Creates a dictionary, adds climate terms, 
and enriches them with Wikidata and Wikipedia data.
"""

from amilib.ami_dict import AmiDictionary
from amilib.wikidata_service import WikidataService
from datetime import datetime
import json
import os

def create_climate_dictionary():
    """Create a comprehensive climate dictionary with enriched entries."""
    
    print("🌍 Comprehensive Dictionary Test")
    print("=" * 60)
    
    # 1. Create new empty dictionary
    print("1️⃣ Creating new empty dictionary...")
    dictionary = AmiDictionary.create_minimal_json_dictionary()
    print(f"📁 Dictionary ID: {dictionary.id}")
    
    # 2. Name the dictionary
    print("\n2️⃣ Naming the dictionary...")
    dictionary.title = "Climate Change Dictionary"
    dictionary.description = "A comprehensive dictionary of climate change terms enriched with Wikipedia and Wikidata data"
    print(f"✅ Dictionary named: '{dictionary.title}'")
    print(f"📝 Description: {dictionary.description}")
    
    # 3. Add creation date
    print("\n3️⃣ Adding creation date...")
    current_date = datetime.now().isoformat()
    dictionary.created_date = current_date
    dictionary.modified_date = current_date
    print(f"📅 Date added: {current_date}")
    
    # 4. Add climate terms and create entries
    print("\n4️⃣ Adding climate terms and creating entries...")
    climate_terms = [
        "climate change", "global warming", "greenhouse effect", "carbon dioxide", "methane",
        "ocean acidification", "sea level rise", "extreme weather", "renewable energy", "solar power"
    ]
    
    # Initialize Wikidata service
    wikidata_service = WikidataService()
    
    for term in climate_terms:
        print(f"📝 Entry created for term: '{term}'")
        
        # 5. & 6. Look up in Wikipedia/Wikidata and enrich
        print(f"\n5️⃣ & 6️⃣ Looking up '{term}' in Wikipedia/Wikidata...")
        print(f"\n🔍 Enriching term: '{term}'")
        print("-" * 50)
        
        try:
            # Search for the entity
            entities = wikidata_service.search_entity(term, max_results=1)
            
            if entities:
                primary_entity = entities[0]
                qid = primary_entity['id']
                
                # Get detailed information using individual methods
                try:
                    label = wikidata_service.get_entity_label(qid)
                    description = wikidata_service.get_entity_description(qid)
                    aliases = wikidata_service.get_entity_aliases(qid)
                    wikipedia_links = wikidata_service.get_wikipedia_links(qid)
                    
                    # Get Wikipedia URL
                    wikipedia_url = ""
                    if wikipedia_links and 'en' in wikipedia_links:
                        wikipedia_url = wikipedia_links['en']
                    
                    print(f"✅ Wikidata ID: {qid}")
                    print(f"🌐 Wikipedia URL: {wikipedia_url}")
                    
                    # Create enriched entry
                    entry_data = {
                        "term": term,
                        "definition": description if description else "",
                        "description": description if description else "",
                        "wikidata_id": qid,
                        "wikipedia_url": wikipedia_url,
                        "aliases": aliases if aliases else [],
                        "label": label if label else term,  # Use term as fallback if label is None
                        "enrichment_status": "success"
                    }
                    
                    # Add entry to dictionary
                    dictionary.add_entry_with_term(term, entry_data)
                    print("✅ Entry enriched successfully!")
                    
                except Exception as e:
                    print(f"⚠️  Partial enrichment failed: {e}")
                    # Still add the entry with basic info
                    entry_data = {
                        "term": term,
                        "definition": "",
                        "description": "",
                        "wikidata_id": qid if 'qid' in locals() else "",
                        "wikipedia_url": "",
                        "aliases": [],
                        "label": term,
                        "enrichment_status": f"partial: {str(e)}"
                    }
                    dictionary.add_entry_with_term(term, entry_data)
                    
            else:
                print(f"❌ No Wikidata entity found for '{term}'")
                # Add entry without enrichment
                entry_data = {
                    "term": term,
                    "definition": "",
                    "description": "",
                    "wikidata_id": "",
                    "wikipedia_url": "",
                    "aliases": [],
                    "label": term,
                    "enrichment_status": "no_entity_found"
                }
                dictionary.add_entry_with_term(term, entry_data)
                
        except Exception as e:
            print(f"❌ Error enriching '{term}': {e}")
            # Add entry with error status
            entry_data = {
                "term": term,
                "definition": "",
                "description": "",
                "wikidata_id": "",
                "wikipedia_url": "",
                "aliases": [],
                "label": term,
                "enrichment_status": f"error: {str(e)}"
            }
            dictionary.add_entry_with_term(term, entry_data)
    
    # 7. Final results
    print("\n" + "=" * 60)
    print("7️⃣ Final Dictionary Results")
    print("=" * 60)
    print(f"📚 Dictionary: {dictionary.title}")
    print(f"📅 Created: {dictionary.created_date}")
    print(f"📝 Total Entries: {len(dictionary.entries)}")
    
    print("\n📋 Enriched Entries:")
    for i, entry in enumerate(dictionary.entries, 1):
        print(f"\n{i}. {entry.term}")
        if entry.wikidata_id:
            print(f"   Wikidata ID: {entry.wikidata_id}")
        if entry.wikipedia_url:
            print(f"   Wikipedia: {entry.wikipedia_url}")
        if entry.definition:
            print(f"   Definition: {entry.definition[:100]}...")
        if entry.description:
            print(f"   Description: {entry.description[:100]}...")
        if entry.aliases:
            print(f"   Aliases: {entry.aliases}")
    
    # Save results
    output_file = "temp/comprehensive_dictionary_test.json"
    os.makedirs("temp", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary.to_json(), f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results exported to: {output_file}")
    
    # Also add to consolidated examples file
    consolidated_file = "temp/wikimedia_examples.json"
    try:
        if os.path.exists(consolidated_file):
            with open(consolidated_file, 'r', encoding='utf-8') as f:
                consolidated_data = json.load(f)
        else:
            consolidated_data = {}
        
        consolidated_data['comprehensive_dictionary_test'] = {
            'timestamp': datetime.now().isoformat(),
            'dictionary': dictionary.to_json()
        }
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results also added to: {consolidated_file}")
        
    except Exception as e:
        print(f"⚠️  Could not update consolidated file: {e}")
    
    print(f"\n🎉 Comprehensive Dictionary Test Completed Successfully!")
    print(f"📊 Final dictionary contains {len(dictionary.entries)} enriched entries")
    
    return dictionary

if __name__ == "__main__":
    create_climate_dictionary()
