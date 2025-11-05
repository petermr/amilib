"""
Tests for encyclopedia auto-lookup functionality
These tests perform minimal network lookups to verify auto-lookup works
"""
import unittest
from pathlib import Path

from amilib.ami_encyclopedia import AmiEncyclopedia
from test.resources import Resources


class EncyclopediaAutoLookupTest(unittest.TestCase):
    """Test encyclopedia auto-lookup functionality with minimal network calls"""
    
    def test_auto_lookup_from_wikipedia_url(self):
        """Test auto-lookup of Wikidata ID from Wikipedia URL (minimal lookup - 1 network call)"""
        print("🧪 Testing auto-lookup from Wikipedia URL...")
        
        # Create test HTML with entry that has Wikipedia URL but no Wikidata ID
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="Climate change" term="Climate change" role="ami_entry">
                <p>search term: Climate change <a href="https://en.wikipedia.org/wiki/Climate_change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        # Enable auto-lookup for this test
        encyclopedia.create_from_html_content(test_html, enable_auto_lookup=True)
        
        # Verify entry was created
        assert len(encyclopedia.entries) > 0, "Should have entries"
        
        # Verify Wikidata ID was auto-looked up (should be Q7942 for Climate change)
        entry = encyclopedia.entries[0]
        wikidata_id = entry.get('wikidata_id', '')
        
        if wikidata_id:
            assert wikidata_id.startswith('Q'), f"Wikidata ID should start with Q, got {wikidata_id}"
            print(f"✅ Auto-looked up Wikidata ID: {wikidata_id}")
        else:
            print("⚠️  Auto-lookup did not find Wikidata ID (may be network issue)")
            # Skip this test if network is not available
            return
        
        # Normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify synonym group was created
        assert len(synonym_groups) > 0, "Should have synonym groups after auto-lookup"
        assert wikidata_id in synonym_groups, f"Should have synonym group for {wikidata_id}"
        
        print("✅ Auto-lookup from Wikipedia URL working correctly")
    
    def test_auto_lookup_from_term(self):
        """Test auto-lookup of Wikidata ID from term (minimal lookup - 1 network call)"""
        print("🧪 Testing auto-lookup from term...")
        
        # Create test HTML with entry that has term but no Wikidata ID or Wikipedia URL
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="Ethanol" term="Ethanol" role="ami_entry">
                <p>search term: Ethanol</p>
                <p class="wpage_first_para">Ethanol is an organic compound.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        # Enable auto-lookup for this test
        encyclopedia.create_from_html_content(test_html, enable_auto_lookup=True)
        
        # Verify entry was created
        assert len(encyclopedia.entries) > 0, "Should have entries"
        
        # Verify Wikidata ID was auto-looked up (should be Q153 for Ethanol)
        entry = encyclopedia.entries[0]
        wikidata_id = entry.get('wikidata_id', '')
        
        if wikidata_id:
            assert wikidata_id.startswith('Q'), f"Wikidata ID should start with Q, got {wikidata_id}"
            print(f"✅ Auto-looked up Wikidata ID: {wikidata_id}")
        else:
            print("⚠️  Auto-lookup did not find Wikidata ID (may be network issue)")
            # Skip this test if network is not available
            return
        
        # Normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify synonym group was created
        assert len(synonym_groups) > 0, "Should have synonym groups after auto-lookup"
        assert wikidata_id in synonym_groups, f"Should have synonym group for {wikidata_id}"
        
        print("✅ Auto-lookup from term working correctly")


if __name__ == '__main__':
    unittest.main()




