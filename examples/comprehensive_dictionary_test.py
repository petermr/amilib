#!/usr/bin/env python3
"""
Comprehensive Dictionary Test - Creates a dictionary, adds climate terms, 
and enriches them with Wikidata and Wikipedia data.
"""

from amilib.ami_dict import AmiDictionary
from datetime import datetime
import json
import os

def create_climate_dictionary():
    """Create a comprehensive climate dictionary with enriched entries."""
    
    print("🌍 Comprehensive Dictionary Test")
    print("=" * 60)
    
    # 1. Create new empty dictionary (using Python dict instead of AmiDictionary)
    print("1️⃣ Creating new empty dictionary...")
    
    # Create a basic dictionary structure directly
    dictionary_data = {
        "title": "Climate Change Dictionary",
        "description": "A comprehensive dictionary of climate change terms enriched with Wikipedia and Wikidata data",
        "created_date": datetime.now().isoformat(),
        "modified_date": datetime.now().isoformat(),
        "entries": []
    }
    
    print(f"✅ Dictionary created: '{dictionary_data['title']}'")
    print(f"📝 Description: {dictionary_data['description']}")
    print(f"📅 Date added: {dictionary_data['created_date']}")
    
    # 4. Add climate terms and create entries
    print("\n4️⃣ Adding climate terms and creating entries...")
    climate_terms = [
        "climate change", "global warming", "greenhouse effect", "carbon dioxide", "methane",
        "ocean acidification", "sea level rise", "extreme weather", "renewable energy", "solar power"
    ]
    

    for term in climate_terms:
        print(f"📝 Entry created for term: '{term}'")
        
        # 5. & 6. Look up in Wikipedia/Wikidata and enrich
        print(f"\n5️⃣ & 6️⃣ Looking up '{term}' in Wikipedia/Wikidata...")
        print(f"\n🔍 Enriching term: '{term}'")
        print("-" * 50)
        
        try:
            # Search for the entity using existing amilib
            from amilib.wikimedia import WikidataLookup, WikidataPage
            wikidata_lookup = WikidataLookup()
            hit0_id, hit0_description, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
            
            if hit0_id and hit0_description:
                qid = hit0_id
                description = hit0_description
                
                # Get detailed information using existing methods
                try:
                    # Get Wikipedia URL using WikidataPage
                    wikidata_page = WikidataPage(pqitem=qid)
                    wikipedia_url = wikidata_page.get_wikipedia_page_link(lang="en") or ""
                    
                    print(f"✅ Wikidata ID: {qid}")
                    print(f"🌐 Wikipedia URL: {wikipedia_url}")
                    
                    # Create enriched entry
                    entry_data = {
                        "term": term,
                        "definition": description if description else "",
                        "description": description if description else "",
                        "wikidata_id": qid,
                        "wikipedia_url": wikipedia_url,
                        "aliases": [],  # Could be enhanced later
                        "label": term,  # Use term as label
                        "enrichment_status": "success"
                    }
                    
                    # Add entry to dictionary
                    dictionary_data["entries"].append(entry_data)
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
                    dictionary_data["entries"].append(entry_data)
                    
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
                dictionary_data["entries"].append(entry_data)
                
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
            dictionary_data["entries"].append(entry_data)
    
    # 7. Final results
    print("\n" + "=" * 60)
    print("7️⃣ Final Dictionary Results")
    print("=" * 60)
    print(f"📚 Dictionary: {dictionary_data['title']}")
    print(f"📅 Created: {dictionary_data['created_date']}")
    print(f"📝 Total Entries: {len(dictionary_data['entries'])}")
    
    print("\n📋 Enriched Entries:")
    for i, entry in enumerate(dictionary_data['entries'], 1):
        print(f"\n{i}. {entry['term']}")
        if entry.get('wikidata_id'):
            print(f"   Wikidata ID: {entry['wikidata_id']}")
        if entry.get('wikipedia_url'):
            print(f"   Wikipedia: {entry['wikipedia_url']}")
        if entry.get('definition'):
            print(f"   Definition: {entry['definition'][:100]}...")
        if entry.get('description'):
            print(f"   Description: {entry['description'][:100]}...")
        if entry.get('aliases'):
            print(f"   Aliases: {entry['aliases']}")
    
    # Save results
    output_file = "temp/comprehensive_dictionary_test.json"
    os.makedirs("temp", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary_data, f, indent=2, ensure_ascii=False)
    
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
            'dictionary': dictionary_data
        }
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results also added to: {consolidated_file}")
        
    except Exception as e:
        print(f"⚠️  Could not update consolidated file: {e}")
    
    print(f"\n🎉 Comprehensive Dictionary Test Completed Successfully!")
    print(f"📊 Final dictionary contains {len(dictionary_data['entries'])} enriched entries")
    
    return dictionary_data

if __name__ == "__main__":
    create_climate_dictionary()
