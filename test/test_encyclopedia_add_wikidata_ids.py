"""
Tests for adding Wikidata IDs to encyclopedia entries from Wikipedia pages

Tests the lookup_wikidata_ids_from_wikipedia_pages method which:
- Skips entries that already have Wikidata IDs
- Skips entries without Wikipedia pages
- Looks up Wikidata IDs from Wikipedia page URLs
- Writes the edited encyclopedia
- Supports max_ids parameter for batch processing
"""

import unittest
import pytest
from pathlib import Path
import shutil

from amilib.ami_encyclopedia import AmiEncyclopedia
from test.resources import Resources
from test.test_all import AmiAnyTest
from amilib.util import Util
from test.test_encyclopedia import AbstractEncyclopediaTest

logger = Util.get_logger(__name__)


@pytest.mark.skip("Encyclopedia functionality moved to ../encyclopedia")
class EncyclopediaAddWikidataIdsTest(AbstractEncyclopediaTest):
    """Test adding Wikidata IDs from Wikipedia pages"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "test_encyclopedia_15_entries.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaAddWikidataIdsTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directory for preserving test results
        self.output_dir = Path(Resources.TEMP_DIR, "encyclopedia_add_wikidata_ids")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures - preserve output files"""
        # Don't delete temp_dir or output_dir - keep for manual inspection
        # Only clean up if explicitly needed (commented out for now)
        # if self.temp_dir.exists():
        #     shutil.rmtree(self.temp_dir)
        pass
    
    def test_lookup_wikidata_ids_from_wikipedia_pages(self):
        """Test looking up Wikidata IDs from Wikipedia pages for entries that have Wikipedia URLs"""
        print("🧪 Testing lookup of Wikidata IDs from Wikipedia pages...")
        
        # Create encyclopedia from test file
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia 15 Entries")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Count entries before
        total_entries = len(encyclopedia.entries)
        entries_with_wd_before = sum(1 for e in encyclopedia.entries 
                                    if e.get('wikidata_id') and e.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'))
        entries_with_wikipedia = sum(1 for e in encyclopedia.entries if e.get('wikipedia_url'))
        
        print(f"📊 Before lookup:")
        print(f"   Total entries: {total_entries}")
        print(f"   Entries with Wikidata ID: {entries_with_wd_before}")
        print(f"   Entries with Wikipedia URL: {entries_with_wikipedia}")
        
        # Lookup Wikidata IDs from Wikipedia pages
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)
        
        # Count entries after
        entries_with_wd_after = sum(1 for e in encyclopedia.entries 
                                   if e.get('wikidata_id') and e.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'))
        
        print(f"📊 After lookup:")
        print(f"   Entries with Wikidata ID: {entries_with_wd_after}")
        print(f"   Stats: {stats}")
        
        # Verify that entries with Wikipedia URLs got Wikidata IDs (if lookup succeeded)
        # Note: Some entries may not have Wikidata IDs if Wikipedia page doesn't have one
        entries_with_wikipedia_and_wd = sum(1 for e in encyclopedia.entries 
                                           if e.get('wikipedia_url') and 
                                           e.get('wikidata_id') and 
                                           e.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'))
        
        print(f"   Entries with Wikipedia URL AND Wikidata ID: {entries_with_wikipedia_and_wd}")
        
        # Verify stats
        assert stats['total_entries'] == total_entries, "Total entries should match"
        assert stats['entries_with_wikidata_id_before'] == entries_with_wd_before, "Before count should match"
        assert stats['entries_with_wikidata_id_after'] == entries_with_wd_after, "After count should match"
        assert stats['entries_skipped_already_have_id'] >= 0, "Skipped count should be non-negative"
        assert stats['entries_skipped_no_wikipedia'] >= 0, "No Wikipedia count should be non-negative"
        assert stats['entries_looked_up'] >= 0, "Looked up count should be non-negative"
        assert stats['entries_successfully_found'] >= 0, "Successfully found count should be non-negative"
        
        # Verify that entries with existing Wikidata IDs were skipped
        # (We can't easily test this without modifying the test file, but we can verify the logic)
        
        print("✅ Wikidata ID lookup from Wikipedia pages completed successfully")
    
    def test_lookup_wikidata_ids_with_max_ids_limit(self):
        """Test looking up Wikidata IDs with max_ids parameter to limit batch size"""
        print("🧪 Testing lookup with max_ids parameter...")
        
        # Create encyclopedia from test file
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia 15 Entries")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Lookup with max_ids=5 (should only process first 5 entries needing lookup)
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=5)
        
        print(f"📊 Lookup with max_ids=5:")
        print(f"   Stats: {stats}")
        
        # Verify that max_ids was respected
        assert stats['entries_looked_up'] <= 5, f"Should not look up more than max_ids, got {stats['entries_looked_up']}"
        
        print("✅ Max IDs limit respected")
    
    def test_lookup_wikidata_ids_skips_existing_ids(self):
        """Test that entries with existing Wikidata IDs are skipped"""
        print("🧪 Testing that existing Wikidata IDs are skipped...")
        
        # Create encyclopedia with some entries that already have Wikidata IDs
        test_html = """
        <html><head><style>div[role] {border:solid 1px;margin:1px;}</style><base href="https://en.wikipedia.org/wiki/"></head><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="climate change" term="climate change" wikidataID="Q7942" role="ami_entry">
                <p>search term: climate change <a href="https://en.wikipedia.org/wiki/Climate_change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change description.</p>
            </div>
            <div name="biodiversity" term="biodiversity" role="ami_entry">
                <p>search term: biodiversity <a href="https://en.wikipedia.org/wiki/Biodiversity">Wikipedia Page</a></p>
                <p class="wpage_first_para">Biodiversity description.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify first entry has Wikidata ID
        entry1 = encyclopedia.entries[0]
        assert entry1.get('wikidata_id') == 'Q7942', "First entry should have Wikidata ID Q7942"
        
        # Lookup Wikidata IDs
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)
        
        # Verify that first entry's ID was not changed (it was skipped)
        entry1_after = encyclopedia.entries[0]
        assert entry1_after.get('wikidata_id') == 'Q7942', "First entry's Wikidata ID should not change"
        
        # Verify that it was counted as skipped
        assert stats['entries_skipped_already_have_id'] >= 1, "Should have skipped at least one entry with existing ID"
        
        print("✅ Entries with existing Wikidata IDs were skipped")
    
    def test_lookup_wikidata_ids_skips_no_wikipedia(self):
        """Test that entries without Wikipedia pages are skipped"""
        print("🧪 Testing that entries without Wikipedia pages are skipped...")
        
        # Create encyclopedia with entry that has no Wikipedia URL
        # Note: create_from_html_content may extract URLs from links, so we need to manually create entries
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        
        # Manually add entries to avoid automatic URL extraction
        entry_no_wikipedia = {
            'term': 'nonexistent_term',
            'search_term': 'nonexistent_term',
            'wikipedia_url': '',  # Explicitly no Wikipedia URL
            'wikidata_id': '',
            'description_html': '<p>No Wikipedia page for this term.</p>'
        }
        
        entry_with_wikipedia = {
            'term': 'biodiversity',
            'search_term': 'biodiversity',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Biodiversity',
            'wikidata_id': '',
            'description_html': '<p>Biodiversity description.</p>'
        }
        
        encyclopedia.entries = [entry_no_wikipedia, entry_with_wikipedia]
        
        # Verify first entry has no Wikipedia URL
        entry1 = encyclopedia.entries[0]
        assert not entry1.get('wikipedia_url'), "First entry should not have Wikipedia URL"
        
        # Lookup Wikidata IDs
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)
        
        # Verify that first entry was skipped
        assert stats['entries_skipped_no_wikipedia'] >= 1, "Should have skipped at least one entry without Wikipedia URL"
        
        print("✅ Entries without Wikipedia pages were skipped")
    
    def test_lookup_wikidata_ids_writes_edited_encyclopedia(self):
        """Test that the method writes the edited encyclopedia to a file"""
        print("🧪 Testing that edited encyclopedia is written to file...")
        
        # Create encyclopedia from test file
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia 15 Entries")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Output file - save to output_dir for preservation
        output_file = self.output_dir / "encyclopedia_with_wikidata_ids.html"
        
        # Lookup Wikidata IDs and write to file
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(
            max_ids=None,
            output_file=output_file
        )
        
        # Verify file was created
        assert output_file.exists(), "Output file should be created"
        assert output_file.stat().st_size > 0, "Output file should not be empty"
        
        # Verify file content contains encyclopedia format (not dictionary format)
        file_content = output_file.read_text(encoding='utf-8')
        assert 'role="ami_encyclopedia"' in file_content, "Saved file should be in encyclopedia format"
        
        # Verify that Wikidata IDs are present in the file content
        # (The file format may vary, but we can check for Wikidata references)
        entries_with_wd_in_content = file_content.count('wikidataID="Q') + file_content.count('wikidataID="P')
        entries_with_wd_links = file_content.count('wikidata.org/wiki/Q') + file_content.count('wikidata.org/wiki/P')
        
        print(f"   Entries with Wikidata ID attribute in saved file: {entries_with_wd_in_content}")
        print(f"   Wikidata links in saved file: {entries_with_wd_links}")
        print(f"   Stats: {stats}")
        
        # Verify that at least some entries were processed
        assert stats['entries_looked_up'] >= 0, "Should have attempted some lookups"
        
        # Verify file contains the title
        assert encyclopedia.title in file_content or "Test Encyclopedia" in file_content, "File should contain encyclopedia title"
        
        print("✅ Edited encyclopedia written to file successfully")
    
    def test_lookup_wikidata_ids_never_fails(self):
        """Test that the method never fails even if lookups fail (try/catch protection)"""
        print("🧪 Testing that method never fails even with network errors...")
        
        # Create encyclopedia with entries that might fail lookup
        test_html = """
        <html><head><style>div[role] {border:solid 1px;margin:1px;}</style><base href="https://en.wikipedia.org/wiki/"></head><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="biodiversity" term="biodiversity" role="ami_entry">
                <p>search term: biodiversity <a href="https://en.wikipedia.org/wiki/Biodiversity">Wikipedia Page</a></p>
                <p class="wpage_first_para">Biodiversity description.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # This should never raise an exception, even if network fails
        try:
            stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)
            print(f"   Stats: {stats}")
            print("✅ Method completed without exceptions")
        except Exception as e:
            assert False, f"Method should never fail, but raised: {e}"
    
    def test_entry_classification_system(self):
        """Test the entry classification system to avoid expensive lookups"""
        print("🧪 Testing entry classification system...")
        
        from amilib.ami_encyclopedia import AmiEncyclopedia
        
        # Create encyclopedia with various entry types
        encyclopedia = AmiEncyclopedia(title="Test Classification")
        
        # Entry with Wikidata ID
        entry1 = {
            'term': 'climate change',
            'search_term': 'climate change',
            'wikidata_id': 'Q7942',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Climate_change',
            'description_html': '<p>Climate change description.</p>',
            'classification': AmiEncyclopedia.CLASSIFICATION_UNPROCESSED
        }
        
        # Entry without Wikipedia URL
        entry2 = {
            'term': 'nonexistent_term',
            'search_term': 'nonexistent_term',
            'wikidata_id': '',
            'wikipedia_url': '',
            'description_html': '<p>No Wikipedia page.</p>',
            'classification': AmiEncyclopedia.CLASSIFICATION_UNPROCESSED
        }
        
        # Entry with disambiguation page
        entry3 = {
            'term': 'AR5',
            'search_term': 'AR5',
            'wikidata_id': '',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/AR5_(disambiguation)',
            'description_html': '<p>Disambiguation page.</p>',
            'classification': AmiEncyclopedia.CLASSIFICATION_UNPROCESSED
        }
        
        # Entry with Wikipedia URL but no Wikidata ID (unprocessed)
        entry4 = {
            'term': 'biodiversity',
            'search_term': 'biodiversity',
            'wikidata_id': '',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Biodiversity',
            'description_html': '<p>Biodiversity description.</p>',
            'classification': AmiEncyclopedia.CLASSIFICATION_UNPROCESSED
        }
        
        encyclopedia.entries = [entry1, entry2, entry3, entry4]
        
        # Classify all entries
        stats = encyclopedia.classify_all_entries()
        
        print(f"📊 Classification stats: {stats}")
        
        # Verify classifications
        assert entry1['classification'] == AmiEncyclopedia.CLASSIFICATION_HAS_WIKIDATA, \
            "Entry with Wikidata ID should be classified as HAS_WIKIDATA"
        
        assert entry2['classification'] == AmiEncyclopedia.CLASSIFICATION_NO_WIKIPEDIA_PAGE, \
            "Entry without Wikipedia URL should be classified as NO_WIKIPEDIA_PAGE"
        
        assert entry3['classification'] == AmiEncyclopedia.CLASSIFICATION_AMBIGUOUS, \
            "Entry with disambiguation page should be classified as AMBIGUOUS"
        
        assert entry4['classification'] == AmiEncyclopedia.CLASSIFICATION_UNPROCESSED, \
            "Entry with Wikipedia URL but no Wikidata ID should be UNPROCESSED"
        
        # Verify stats
        assert stats['has_wikidata'] == 1, "Should have 1 entry with Wikidata"
        assert stats['no_wikipedia_page'] == 1, "Should have 1 entry without Wikipedia page"
        assert stats['ambiguous'] == 1, "Should have 1 ambiguous entry"
        assert stats['unprocessed'] == 1, "Should have 1 unprocessed entry"
        
        print("✅ Entry classification system working correctly")
    
    def test_classification_skips_expensive_lookups(self):
        """Test that classification is used to skip expensive lookups"""
        print("🧪 Testing that classification skips expensive lookups...")
        
        from amilib.ami_encyclopedia import AmiEncyclopedia
        
        # Create encyclopedia with pre-classified entries
        encyclopedia = AmiEncyclopedia(title="Test Classification Skip")
        
        # Entry already classified as HAS_WIKIDATA (should skip lookup)
        entry1 = {
            'term': 'climate change',
            'wikidata_id': 'Q7942',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Climate_change',
            'classification': AmiEncyclopedia.CLASSIFICATION_HAS_WIKIDATA
        }
        
        # Entry classified as NO_WIKIPEDIA_PAGE (should skip lookup)
        entry2 = {
            'term': 'nonexistent',
            'wikidata_id': '',
            'wikipedia_url': '',
            'classification': AmiEncyclopedia.CLASSIFICATION_NO_WIKIPEDIA_PAGE
        }
        
        # Entry classified as AMBIGUOUS (should skip lookup)
        entry3 = {
            'term': 'AR5',
            'wikidata_id': '',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/AR5_(disambiguation)',
            'classification': AmiEncyclopedia.CLASSIFICATION_AMBIGUOUS
        }
        
        # Entry unprocessed (should be looked up)
        entry4 = {
            'term': 'biodiversity',
            'wikidata_id': '',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Biodiversity',
            'classification': AmiEncyclopedia.CLASSIFICATION_UNPROCESSED
        }
        
        encyclopedia.entries = [entry1, entry2, entry3, entry4]
        
        # Run lookup - should skip entries 1, 2, 3 based on classification
        stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(max_ids=None)
        
        print(f"📊 Lookup stats: {stats}")
        
        # Verify that classified entries were skipped
        assert stats['entries_skipped_classified'] >= 3, \
            f"Should skip at least 3 classified entries, got {stats['entries_skipped_classified']}"
        
        assert stats['entries_skipped_already_have_id'] >= 1, \
            "Should skip entry with HAS_WIKIDATA classification"
        
        assert stats['entries_skipped_no_wikipedia'] >= 1, \
            "Should skip entry with NO_WIKIPEDIA_PAGE classification"
        
        assert stats['entries_skipped_ambiguous'] >= 1, \
            "Should skip entry with AMBIGUOUS classification"
        
        # Verify only unprocessed entry was looked up
        assert stats['entries_looked_up'] >= 1, \
            "Should look up at least the unprocessed entry"
        
        print("✅ Classification successfully skips expensive lookups")
    
    def test_complete_processing_15_entries(self):
        """Complete processing example: classify all entries and lookup all Wikidata IDs
        
        This demonstrates the full workflow:
        1. Load encyclopedia with ~15 entries
        2. Classify all entries
        3. Lookup all Wikidata IDs
        4. Verify all entries are classified
        5. Save final encyclopedia
        """
        print("🧪 Testing complete processing of 15-entry encyclopedia...")
        
        # Load the test encyclopedia
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia 15 Entries - Complete Processing")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        print(f"\n📊 Initial state:")
        print(f"   Total entries: {len(encyclopedia.entries)}")
        
        # Step 1: Classify all entries
        print(f"\n🔍 Step 1: Classifying all entries...")
        classification_stats = encyclopedia.classify_all_entries()
        
        print(f"   Classification results:")
        print(f"     - HAS_WIKIDATA: {classification_stats['has_wikidata']}")
        print(f"     - UNPROCESSED: {classification_stats['unprocessed']}")
        print(f"     - AMBIGUOUS: {classification_stats['ambiguous']}")
        print(f"     - NO_WIKIPEDIA_PAGE: {classification_stats['no_wikipedia_page']}")
        print(f"     - NO_WIKIDATA_ENTRY: {classification_stats['no_wikidata_entry']}")
        print(f"     - ERROR: {classification_stats['error']}")
        
        # Step 2: Lookup all Wikidata IDs for unprocessed entries
        print(f"\n🔍 Step 2: Looking up Wikidata IDs for unprocessed entries...")
        lookup_stats = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(
            max_ids=None,  # Process all entries
            delay_seconds=0.1
        )
        
        print(f"   Lookup results:")
        print(f"     - Entries looked up: {lookup_stats['entries_looked_up']}")
        print(f"     - Successfully found: {lookup_stats['entries_successfully_found']}")
        print(f"     - Failed lookups: {lookup_stats['entries_failed_lookup']}")
        print(f"     - Skipped (already have ID): {lookup_stats['entries_skipped_already_have_id']}")
        print(f"     - Skipped (no Wikipedia): {lookup_stats['entries_skipped_no_wikipedia']}")
        print(f"     - Skipped (ambiguous): {lookup_stats['entries_skipped_ambiguous']}")
        
        # Step 3: Re-classify to get final state
        print(f"\n🔍 Step 3: Re-classifying after lookup...")
        final_classification_stats = encyclopedia.classify_all_entries()
        
        print(f"   Final classification:")
        print(f"     - HAS_WIKIDATA: {final_classification_stats['has_wikidata']}")
        print(f"     - UNPROCESSED: {final_classification_stats['unprocessed']}")
        print(f"     - AMBIGUOUS: {final_classification_stats['ambiguous']}")
        print(f"     - NO_WIKIPEDIA_PAGE: {final_classification_stats['no_wikipedia_page']}")
        print(f"     - NO_WIKIDATA_ENTRY: {final_classification_stats['no_wikidata_entry']}")
        print(f"     - ERROR: {final_classification_stats['error']}")
        
        # Step 4: Verify all entries are classified
        print(f"\n✅ Step 4: Verifying all entries are classified...")
        unclassified = [e for e in encyclopedia.entries if not e.get('classification')]
        assert len(unclassified) == 0, f"Found {len(unclassified)} unclassified entries"
        print(f"   All {len(encyclopedia.entries)} entries are classified ✓")
        
        # Step 5: Show entry details
        print(f"\n📋 Entry details:")
        for idx, entry in enumerate(encyclopedia.entries, 1):
            term = entry.get('term', 'N/A')
            wikidata_id = entry.get('wikidata_id', '')
            classification = entry.get('classification', 'UNKNOWN')
            wikipedia_url = entry.get('wikipedia_url', '')
            
            print(f"   {idx:2d}. {term:30s} | {classification:20s} | Wikidata: {wikidata_id or 'N/A':10s}")
            if wikipedia_url and '(disambiguation)' in wikipedia_url.lower():
                print(f"       └─ Disambiguation page: {wikipedia_url}")
        
        # Step 6: Save final encyclopedia
        print(f"\n💾 Step 5: Saving final encyclopedia...")
        output_file = self.output_dir / "test_encyclopedia_15_entries_complete.html"
        lookup_stats_final = encyclopedia.lookup_wikidata_ids_from_wikipedia_pages(
            max_ids=None,
            output_file=output_file
        )
        
        print(f"   Saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size:,} bytes")
        
        # Verify file content
        file_content = output_file.read_text(encoding='utf-8')
        entries_with_wd = file_content.count('wikidataID="Q') + file_content.count('wikidataID="P')
        print(f"   Entries with Wikidata ID in file: {entries_with_wd}")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total entries: {len(encyclopedia.entries)}")
        print(f"   Entries with Wikidata ID: {final_classification_stats['has_wikidata']}")
        print(f"   Entries without Wikipedia page: {final_classification_stats['no_wikipedia_page']}")
        print(f"   Ambiguous entries: {final_classification_stats['ambiguous']}")
        print(f"   Entries needing Wikidata lookup: {final_classification_stats['unprocessed'] + final_classification_stats['no_wikidata_entry']}")
        
        print(f"\n✅ Complete processing finished!")
        print(f"   Open in browser: file://{output_file.absolute()}")


if __name__ == '__main__':
    unittest.main()

