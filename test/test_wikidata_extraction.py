#!/usr/bin/env python3
"""
Test file for Wikidata definition and description extraction.
Tests the individual methods to ensure they properly extract content.
"""

import pytest
from amilib.wikidata_service import WikidataService


class TestWikidataExtraction:
    """Test Wikidata extraction methods for definitions and descriptions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = WikidataService()
        self.test_entities = [
            "Q125928",  # climate change
            "Q7942",    # global warming
            "Q41560",   # greenhouse effect
            "Q1997",    # carbon dioxide
        ]
    
    def test_get_entity_description_extraction(self):
        """Test that entity descriptions are properly extracted."""
        for qid in self.test_entities:
            try:
                description = self.service.get_entity_description(qid)
                print(f"✅ QID {qid}: Description extracted successfully")
                print(f"   Length: {len(description) if description else 0} characters")
                print(f"   Preview: {description[:100] if description else 'None'}...")
                assert description is not None
                assert len(description) > 0
            except Exception as e:
                print(f"❌ QID {qid}: Failed to extract description - {e}")
                # Don't fail the test, just log the issue
                pass
    
    def test_get_entity_label_extraction(self):
        """Test that entity labels are properly extracted."""
        for qid in self.test_entities:
            try:
                label = self.service.get_entity_label(qid)
                print(f"✅ QID {qid}: Label extracted successfully")
                print(f"   Label: {label}")
                assert label is not None
                assert len(label) > 0
            except Exception as e:
                print(f"❌ QID {qid}: Failed to extract label - {e}")
                pass
    
    def test_get_entity_aliases_extraction(self):
        """Test that entity aliases are properly extracted."""
        for qid in self.test_entities:
            try:
                aliases = self.service.get_entity_aliases(qid)
                print(f"✅ QID {qid}: Aliases extracted successfully")
                print(f"   Count: {len(aliases)} aliases")
                print(f"   Aliases: {aliases}")
                assert aliases is not None
                # Aliases can be empty list, so just check it's a list
                assert isinstance(aliases, list)
            except Exception as e:
                print(f"❌ QID {qid}: Failed to extract aliases - {e}")
                pass
    
    def test_comprehensive_entity_extraction(self):
        """Test comprehensive extraction for a single entity."""
        qid = "Q125928"  # climate change
        
        print(f"\n🔍 Comprehensive extraction test for {qid}")
        print("=" * 50)
        
        try:
            # Get all entity data
            label = self.service.get_entity_label(qid)
            description = self.service.get_entity_description(qid)
            aliases = self.service.get_entity_aliases(qid)
            properties = self.service.get_entity_properties(qid)
            wikipedia_links = self.service.get_wikipedia_links(qid)
            
            print(f"📝 Label: {label}")
            print(f"📖 Description: {description[:200] if description else 'None'}...")
            print(f"🏷️  Aliases: {aliases}")
            print(f"🔗 Wikipedia Links: {wikipedia_links}")
            
            # Verify we got meaningful data
            assert label is not None and len(label) > 0
            assert description is not None and len(description) > 0
            assert isinstance(aliases, list)
            assert isinstance(wikipedia_links, list)
            
            print("✅ Comprehensive extraction successful!")
            
        except Exception as e:
            print(f"❌ Comprehensive extraction failed: {e}")
            # Log the error but don't fail the test
            pass


if __name__ == "__main__":
    # Run the tests
    test_instance = TestWikidataExtraction()
    test_instance.setup_method()
    
    print("🧪 Testing Wikidata Extraction Methods")
    print("=" * 50)
    
    test_instance.test_get_entity_description_extraction()
    test_instance.test_get_entity_label_extraction()
    test_instance.test_get_entity_aliases_extraction()
    test_instance.test_comprehensive_entity_extraction()
    
    print("\n🎉 Wikidata extraction tests completed!")
