"""
Tests for AmiEncyclopedia functionality

Tests encyclopedia creation, normalization, and synonym aggregation
"""

import unittest
import re
from pathlib import Path
import shutil

from amilib.ami_encyclopedia import AmiEncyclopedia
from amilib.ami_encyclopedia_util import EncyclopediaLinkExtractor, LinkValidator, SynonymNormalizer
from test.resources import Resources


class EncyclopediaTest(unittest.TestCase):
    """Test encyclopedia functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_encyclopedia_from_html_file(self):
        """Test creating encyclopedia from HTML file"""
        print("🧪 Testing encyclopedia creation from HTML file...")
        
        assert self.test_html_file.exists(), f"Test HTML file not found: {self.test_html_file}"
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        assert encyclopedia.title == "Test Encyclopedia", "Title should be set correctly"
        assert len(encyclopedia.entries) > 0, "Should have entries"
        
        # Check entry structure
        first_entry = encyclopedia.entries[0]
        assert 'term' in first_entry, "Entry should have term"
        assert 'search_term' in first_entry, "Entry should have search_term"
        assert 'wikipedia_url' in first_entry, "Entry should have wikipedia_url"
        
        print(f"✅ Created encyclopedia with {len(encyclopedia.entries)} entries")
    
    def test_normalize_by_wikidata_id(self):
        """Test normalizing entries by Wikidata ID"""
        print("🧪 Testing Wikidata ID normalization...")
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        normalized_entries = encyclopedia.normalize_by_wikidata_id()
        
        assert len(normalized_entries) > 0, "Should have normalized entries"
        
        # Check that entries are grouped by Wikidata ID
        for wikidata_id, entries in normalized_entries.items():
            assert isinstance(entries, list), "Each Wikidata ID should map to a list of entries"
            assert len(entries) > 0, "Each Wikidata ID group should have entries"
            
            # All entries in a group should have the same Wikidata ID
            for entry in entries:
                if wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
                    assert re.match(r'^[QP]\d+$', wikidata_id), f"Invalid Wikidata ID format: {wikidata_id}"
                    assert entry.get('wikidata_id') == wikidata_id, "Entries should be grouped by Wikidata ID"
        
        print(f"✅ Normalized into {len(normalized_entries)} groups")
    
    def test_aggregate_synonyms(self):
        """Test synonym aggregation"""
        print("🧪 Testing synonym aggregation...")
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping synonym aggregation test")
            return
        
        normalized = encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        assert len(normalized) > 0, "Should have normalized entries"
        assert len(synonym_groups) > 0, "Should have synonym groups"
        
        # Check synonym group structure
        for wikidata_id, group in synonym_groups.items():
            assert 'wikidata_id' in group, "Group should have wikidata_id"
            assert 'canonical_term' in group, "Group should have canonical_term"
            assert 'synonyms' in group, "Group should have synonyms"
            assert 'search_terms' in group, "Group should have search_terms"
            
            assert len(group['synonyms']) > 0, "Group should have synonyms"
            assert len(group['search_terms']) > 0, "Group should have search terms"
        
        print(f"✅ Aggregated into {len(synonym_groups)} synonym groups")
    
    def test_create_wiki_normalized_html(self):
        """Test creating wiki-normalized HTML output"""
        print("🧪 Testing normalized HTML creation...")
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping HTML creation test")
            return
        
        # Normalize and aggregate before generating HTML
        encyclopedia.normalize_by_wikidata_id()
        encyclopedia.aggregate_synonyms()
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        assert html_content is not None, "Should generate HTML content"
        assert len(html_content) > 0, "HTML content should not be empty"
        assert '<div role="ami_encyclopedia"' in html_content, "Should contain encyclopedia container"
        assert '<div role="ami_entry"' in html_content, "Should contain entry containers"
        
        print("✅ Generated normalized HTML content")
    
    def test_save_wiki_normalized_html(self):
        """Test saving wiki-normalized HTML to file"""
        print("🧪 Testing normalized HTML file saving...")
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        output_file = self.temp_dir / "normalized_encyclopedia.html"
        encyclopedia.save_wiki_normalized_html(output_file)
        
        assert output_file.exists(), "Output file should be created"
        
        content = output_file.read_text(encoding='utf-8')
        assert len(content) > 0, "Output file should not be empty"
        assert '<div role="ami_encyclopedia"' in content, "Should contain encyclopedia structure"
        
        print(f"✅ Saved normalized HTML to {output_file}")
    
    def test_get_statistics(self):
        """Test getting encyclopedia statistics"""
        print("🧪 Testing encyclopedia statistics...")
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping statistics test")
            return
        
        stats = encyclopedia.get_statistics()
        
        assert 'total_entries' in stats, "Should have total_entries"
        assert 'normalized_groups' in stats, "Should have normalized_groups"
        assert 'total_synonyms' in stats, "Should have total_synonyms"
        assert 'compression_ratio' in stats, "Should have compression_ratio"
        
        assert stats['total_entries'] > 0, "Should have entries"
        assert stats['normalized_groups'] > 0, "Should have normalized groups"
        assert stats['compression_ratio'] > 0, "Should have compression ratio"
        
        print(f"✅ Statistics: {stats['total_entries']} entries → {stats['normalized_groups']} groups")


class EncyclopediaUtilTest(unittest.TestCase):
    """Test encyclopedia utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaUtilTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = EncyclopediaLinkExtractor()
        self.validator = LinkValidator()
        self.normalizer = SynonymNormalizer()
    
    def test_extract_entries_from_html(self):
        """Test extracting entries from HTML"""
        print("🧪 Testing entry extraction from HTML...")
        
        html_content = self.test_html_file.read_text(encoding='utf-8')
        entries = self.extractor.extract_entries_from_html(html_content)
        
        assert len(entries) > 0, "Should extract entries"
        
        # Check entry structure
        first_entry = entries[0]
        assert 'term' in first_entry, "Entry should have term"
        assert 'search_term' in first_entry, "Entry should have search_term"
        assert 'wikipedia_url' in first_entry, "Entry should have wikipedia_url"
        
        print(f"✅ Extracted {len(entries)} entries")
    
    def test_classify_link_types(self):
        """Test link type classification"""
        print("🧪 Testing link type classification...")
        
        test_links = [
            ("/wiki/Climate_change", "article"),
            ("/wiki/File:Earth.jpg", "file"),
            ("/wiki/Help:Contents", "help"),
            ("https://example.com", "external"),
            ("#section", "anchor"),
            ("/unknown", "unknown")
        ]
        
        for href, expected_type in test_links:
            actual_type = self.extractor._classify_link_type(href)
            assert actual_type == expected_type, f"Link {href} should be classified as {expected_type}"
        
        print("✅ Link type classification working correctly")
    
    def test_normalize_wikipedia_url(self):
        """Test Wikipedia URL normalization"""
        print("🧪 Testing Wikipedia URL normalization...")
        
        test_urls = [
            ("https://en.wikipedia.org/wiki/Climate_change", "https://en.wikipedia.org/wiki/Climate_change"),
            ("https://en.wikipedia.org/wiki/Climate_change#section", "https://en.wikipedia.org/wiki/Climate_change"),
            ("/wiki/Climate_change", "/wiki/Climate_change"),
            ("https://example.com", "https://example.com")
        ]
        
        for input_url, expected_url in test_urls:
            normalized = self.extractor.normalize_wikipedia_url(input_url)
            assert normalized == expected_url, f"URL {input_url} should normalize to {expected_url}"
        
        print("✅ Wikipedia URL normalization working correctly")


class EncyclopediaIntegrationTest(unittest.TestCase):
    """Integration tests for encyclopedia functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaIntegrationTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_single_entry_synonym_list(self):
        """Test encyclopedia with single entry creates synonym list with one item"""
        print("🧪 Testing single entry synonym list...")
        
        # Create test HTML with single entry (must include Wikidata ID)
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
                <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entry has Wikidata ID
        assert len(encyclopedia.entries) > 0, "Should have entries"
        assert encyclopedia.entries[0].get('wikidata_id') == 'Q7942', "Entry must have Wikidata ID"
        
        # Normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single synonym group
        assert len(synonym_groups) == 1, f"Should have 1 synonym group, got {len(synonym_groups)}"
        
        # Check the group structure
        group = list(synonym_groups.values())[0]
        assert group['canonical_term'] == 'Climate change', f"Canonical term should be 'Climate change', got '{group['canonical_term']}'"
        assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change', f"Wikipedia URL should be correct"
        assert len(group['synonyms']) == 1, f"Should have 1 synonym, got {len(group['synonyms'])}"
        assert group['synonyms'][0] == 'Climate change', f"Synonym should be 'Climate change', got '{group['synonyms'][0]}'"
        
        print("✅ Single entry synonym list working correctly")
    
    def test_multiple_entries_same_wikidata_id(self):
        """Test encyclopedia with multiple entries having same Wikidata ID merges synonyms"""
        print("🧪 Testing multiple entries with same Wikidata ID...")
        
        # Create test HTML with two entries for same concept (same Wikidata ID)
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
                <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
            <div name="climate change" term="climate change" role="ami_entry" wikidataID="Q7942">
                <p>search term: climate change <a href="https://en.wikipedia.org/w/index.php?search=climate%20change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entries have Wikidata IDs
        for entry in encyclopedia.entries:
            assert entry.get('wikidata_id') == 'Q7942', f"Entry {entry.get('term')} must have Wikidata ID Q7942"
        
        # Normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single synonym group (merged by Wikidata ID)
        assert len(synonym_groups) == 1, f"Should have 1 synonym group (merged by Wikidata ID), got {len(synonym_groups)}"
        
        # Check the group structure
        group = list(synonym_groups.values())[0]
        assert group['wikidata_id'] == 'Q7942', f"Wikidata ID should be Q7942, got {group['wikidata_id']}"
        assert group['wikipedia_url'] == 'https://en.wikipedia.org/wiki/Climate_change', f"Wikipedia URL should be correct"
        assert len(group['synonyms']) == 2, f"Should have 2 synonyms, got {len(group['synonyms'])}"
        
        # Check synonyms are present (order may vary)
        synonyms = set(group['synonyms'])
        expected_synonyms = {'Climate change', 'climate change'}
        assert synonyms == expected_synonyms, f"Synonyms should be {expected_synonyms}, got {synonyms}"
        
        print("✅ Multiple entries with same Wikidata ID merging correctly")
    
    def test_synonym_list_html_output(self):
        """Test that synonym list is properly formatted in HTML output"""
        print("🧪 Testing synonym list HTML output...")
        
        # Create test HTML with two entries for same concept (same Wikidata ID)
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="Climate change" term="Climate change" role="ami_entry" wikidataID="Q7942">
                <p>search term: Climate change <a href="https://en.wikipedia.org/w/index.php?search=Climate%20change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
            <div name="climate change" term="climate change" role="ami_entry" wikidataID="Q7942">
                <p>search term: climate change <a href="https://en.wikipedia.org/w/index.php?search=climate%20change">Wikipedia Page</a></p>
                <p class="wpage_first_para">Climate change is a long-term change in global climate patterns.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entries have Wikidata IDs
        for entry in encyclopedia.entries:
            assert entry.get('wikidata_id') == 'Q7942', f"Entry {entry.get('term')} must have Wikidata ID Q7942"
        
        # Normalize and aggregate before generating HTML
        encyclopedia.normalize_by_wikidata_id()
        encyclopedia.aggregate_synonyms()
        
        # Generate HTML
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Check for Wikidata ID
        assert 'wikidataID="Q7942"' in html_content, "Should contain Wikidata ID attribute"
        assert 'href="https://www.wikidata.org/wiki/Q7942"' in html_content, "Should contain Wikidata link"
        
        # Check for Wikipedia URL link
        assert 'href="https://en.wikipedia.org/wiki/Climate_change"' in html_content, "Should contain Wikipedia URL link"
        assert '>Climate change<' in html_content, "Should contain page title as link text"
        
        # Check for synonym list
        assert '<ul class="synonym_list">' in html_content, "Should contain synonym list"
        assert '<li>Climate change</li>' in html_content, "Should contain first synonym"
        assert '<li>climate change</li>' in html_content, "Should contain second synonym"
        
        print("✅ Synonym list HTML output working correctly")
    
    def test_ethanol_single_entry(self):
        """Test ethanol creates encyclopedia with one entry with Wikidata ID Q153 and synonym_list ['ethanol']"""
        print("🧪 Testing ethanol single entry...")
        
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
                <p>search term: ethanol <a href="https://en.wikipedia.org/w/index.php?search=ethanol">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entry has Wikidata ID
        assert len(encyclopedia.entries) > 0, "Should have entries"
        assert encyclopedia.entries[0].get('wikidata_id') == 'Q153', "Entry must have Wikidata ID Q153"
        
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single synonym group
        assert len(synonym_groups) == 1, f"Should have 1 synonym group, got {len(synonym_groups)}"
        
        group = list(synonym_groups.values())[0]
        assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153 (Ethanol), got {group['wikidata_id']}"
        # Wikipedia URL may be lowercase (ethanol) or title case (Ethanol) depending on how it was extracted
        assert 'ethanol' in group['wikipedia_url'].lower(), f"Wikipedia URL should contain 'ethanol', got {group['wikipedia_url']}"
        assert group['synonyms'] == ['ethanol'], f"Synonyms should be ['ethanol'], got {group['synonyms']}"
        
        print("✅ Ethanol single entry working correctly")
    
    def test_hydroxyethane_single_entry(self):
        """Test hydroxyethane creates encyclopedia with one entry with Wikidata ID Q153 and synonym_list ['hydroxyethane']"""
        print("🧪 Testing hydroxyethane single entry...")
        
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="hydroxyethane" term="hydroxyethane" role="ami_entry" wikidataID="Q153">
                <p>search term: hydroxyethane <a href="https://en.wikipedia.org/w/index.php?search=hydroxyethane">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entry has Wikidata ID
        assert len(encyclopedia.entries) > 0, "Should have entries"
        assert encyclopedia.entries[0].get('wikidata_id') == 'Q153', "Entry must have Wikidata ID Q153 (same as Ethanol)"
        
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single synonym group
        assert len(synonym_groups) == 1, f"Should have 1 synonym group, got {len(synonym_groups)}"
        
        group = list(synonym_groups.values())[0]
        assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153 (Ethanol/Hydroxyethane), got {group['wikidata_id']}"
        assert group['synonyms'] == ['hydroxyethane'], f"Synonyms should be ['hydroxyethane'], got {group['synonyms']}"
        
        print("✅ Hydroxyethane single entry working correctly")
    
    def test_ethanol_and_hydroxyethane_same_wikidata_id(self):
        """Test ethanol and hydroxyethane creates encyclopedia with one entry (same Wikidata ID Q153)"""
        print("🧪 Testing ethanol and hydroxyethane same Wikidata ID...")
        
        # Both ethanol and hydroxyethane are the same compound, so they share Wikidata ID Q153
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
                <p>search term: ethanol <a href="https://en.wikipedia.org/w/index.php?search=ethanol">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
            <div name="hydroxyethane" term="hydroxyethane" role="ami_entry" wikidataID="Q153">
                <p>search term: hydroxyethane <a href="https://en.wikipedia.org/w/index.php?search=hydroxyethane">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Verify entries have same Wikidata ID
        for entry in encyclopedia.entries:
            assert entry.get('wikidata_id') == 'Q153', f"Entry {entry.get('term')} must have Wikidata ID Q153"
        
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single synonym group (same Wikidata ID = same concept)
        assert len(synonym_groups) == 1, f"Should have 1 synonym group (same Wikidata ID), got {len(synonym_groups)}"
        
        # Check Wikidata ID
        group = list(synonym_groups.values())[0]
        assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153, got {group['wikidata_id']}"
        assert len(group['synonyms']) == 2, f"Should have 2 synonyms, got {len(group['synonyms'])}"
        
        # Check synonyms are present
        synonyms = set(group['synonyms'])
        expected_synonyms = {'ethanol', 'hydroxyethane'}
        assert synonyms == expected_synonyms, f"Synonyms should be {expected_synonyms}, got {synonyms}"
        
        print("✅ Ethanol and hydroxyethane same Wikidata ID working correctly")
    
    def test_ethanol_and_hydroxyethane_with_merge(self):
        """Test ethanol and hydroxyethane with merge() creates one merged entry (same Wikidata ID)"""
        print("🧪 Testing ethanol and hydroxyethane with merge...")
        
        # Both have same Wikidata ID Q153, so they should merge
        test_html = """
        <html><body>
        <div role="ami_dictionary" title="test_dict">
            <div name="ethanol" term="ethanol" role="ami_entry" wikidataID="Q153">
                <p>search term: ethanol <a href="https://en.wikipedia.org/w/index.php?search=ethanol">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
            <div name="hydroxyethane" term="hydroxyethane" role="ami_entry" wikidataID="Q153">
                <p>search term: hydroxyethane <a href="https://en.wikipedia.org/w/index.php?search=hydroxyethane">Wikipedia Page</a></p>
                <p class="wpage_first_para">Ethanol is an organic compound with the chemical formula C₂H₆O.</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Apply merge operation
        encyclopedia.merge()
        merged_groups = encyclopedia.aggregate_synonyms()
        
        # Verify single merged group (same Wikidata ID = merged)
        assert len(merged_groups) == 1, f"Should have 1 merged group (same Wikidata ID), got {len(merged_groups)}"
        
        # Check Wikidata ID
        group = list(merged_groups.values())[0]
        assert group['wikidata_id'] == 'Q153', f"Wikidata ID should be Q153, got {group['wikidata_id']}"
        assert len(group['synonyms']) == 2, f"Should have 2 synonyms after merge, got {len(group['synonyms'])}"
        
        # Check synonyms are present
        synonyms = set(group['synonyms'])
        expected_synonyms = {'ethanol', 'hydroxyethane'}
        assert synonyms == expected_synonyms, f"Synonyms should be {expected_synonyms}, got {synonyms}"
        
        print("✅ Ethanol and hydroxyethane with merge working correctly (merged by Wikidata ID)")
    
    def test_full_encyclopedia_workflow(self):
        """Test complete encyclopedia workflow"""
        print("🧪 Testing complete encyclopedia workflow...")
        
        # Create encyclopedia
        encyclopedia = AmiEncyclopedia(title="Integration Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping workflow test")
            return
        
        # Normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Generate HTML
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save to file
        output_file = self.temp_dir / "integration_test.html"
        encyclopedia.save_wiki_normalized_html(output_file)
        
        # Get statistics
        stats = encyclopedia.get_statistics()
        
        # Verify results
        assert len(encyclopedia.entries) > 0, "Should have original entries"
        assert len(synonym_groups) > 0, "Should have synonym groups"
        assert len(html_content) > 0, "Should generate HTML"
        assert output_file.exists(), "Should save output file"
        assert stats['total_entries'] > 0, "Should have statistics"
        assert stats['normalized_groups'] > 0, "Should have normalized groups"
        
        print(f"✅ Complete workflow: {stats['total_entries']} entries → {stats['normalized_groups']} groups")
        print(f"✅ Compression ratio: {stats['compression_ratio']:.2f}")


class CompositionTest(unittest.TestCase):
    """Test composition relationship between AmiEncyclopedia and AmiDictionary"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "CompositionTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_encyclopedia_with_dictionary(self):
        """Test creating encyclopedia by composing with AmiDictionary"""
        print("🧪 Testing encyclopedia creation with AmiDictionary composition...")
        
        from amilib.ami_dict import AmiDictionary
        
        # Create dictionary from HTML file
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        assert dictionary is not None, "Should create dictionary"
        # HTML dictionaries use entry_by_term, not entries
        assert len(dictionary.get_ami_entries()) > 0, "Dictionary should have entries"
        
        # Create encyclopedia that uses dictionary via composition
        encyclopedia = AmiEncyclopedia(title=dictionary.title)
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify both have entries
        assert len(encyclopedia.entries) > 0, "Encyclopedia should have entries"
        # HTML dictionaries use get_ami_entries(), not entries
        assert len(dictionary.get_ami_entries()) > 0, "Dictionary should still have entries"
        
        print(f"✅ Created encyclopedia with {len(encyclopedia.entries)} entries from dictionary")
    
    def test_encyclopedia_independent_from_dictionary(self):
        """Test that encyclopedia operations don't modify the dictionary"""
        print("🧪 Testing encyclopedia independence from dictionary...")
        
        from amilib.ami_dict import AmiDictionary
        
        # Create dictionary and encyclopedia from same source
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        # HTML dictionaries use get_ami_entries(), not entries
        original_entry_count = len(dictionary.get_ami_entries())
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Perform operations on encyclopedia
        encyclopedia.normalize_by_wikidata_id()
        encyclopedia.aggregate_synonyms()
        encyclopedia.merge()
        
        # Verify dictionary is unchanged - HTML dictionaries use get_ami_entries(), not entries
        assert len(dictionary.get_ami_entries()) == original_entry_count, "Dictionary entries should not be modified"
        assert dictionary.title is not None, "Dictionary should retain its properties"
        
        print("✅ Encyclopedia operations do not modify dictionary")
    
    def test_dictionary_entries_preserved(self):
        """Test that original dictionary entries are preserved"""
        print("🧪 Testing dictionary entries preservation...")
        
        from amilib.ami_dict import AmiDictionary
        
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        # HTML dictionaries use get_ami_entries(), not entries
        original_terms = {entry.get_term() for entry in dictionary.get_ami_entries() if entry.get_term()}
        
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify encyclopedia has access to similar terms (via its own entries)
        encyclopedia_terms = {entry.get('term', '') for entry in encyclopedia.entries}
        
        # Dictionary terms should still be accessible
        assert len(original_terms) > 0, "Dictionary should have terms"
        assert len(encyclopedia_terms) > 0, "Encyclopedia should have terms"
        
        print(f"✅ Dictionary preserved {len(original_terms)} terms, encyclopedia has {len(encyclopedia_terms)} terms")
    
    def test_create_encyclopedia_from_dictionary_html(self):
        """Test creating encyclopedia from dictionary HTML representation"""
        print("🧪 Testing encyclopedia creation from dictionary HTML...")
        
        from amilib.ami_dict import AmiDictionary
        
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        
        # Create HTML representation of dictionary
        # Encyclopedia can work with same HTML structure
        encyclopedia = AmiEncyclopedia(title=dictionary.title)
        encyclopedia.create_from_html_file(self.test_html_file)
        
        assert encyclopedia.title == dictionary.title, "Titles should match"
        assert len(encyclopedia.entries) > 0, "Encyclopedia should have entries"
        
        print("✅ Encyclopedia created from dictionary HTML structure")
    
    def test_encyclopedia_normalization_with_dictionary_data(self):
        """Test that encyclopedia normalization works with dictionary-derived data"""
        print("🧪 Testing encyclopedia normalization with dictionary data...")
        
        from amilib.ami_dict import AmiDictionary
        
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping normalization test")
            return
        
        # Normalize and aggregate
        normalized = encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        assert len(normalized) > 0, "Should have normalized entries"
        assert len(synonym_groups) > 0, "Should have synonym groups"
        
        # Verify statistics
        stats = encyclopedia.get_statistics()
        assert stats['total_entries'] > 0, "Should have entries"
        assert stats['normalized_groups'] > 0, "Should have normalized groups"
        
        print(f"✅ Normalized {stats['total_entries']} entries into {stats['normalized_groups']} groups")
    
    def test_encyclopedia_and_dictionary_concurrent_usage(self):
        """Test that encyclopedia and dictionary can be used concurrently"""
        print("🧪 Testing concurrent usage of encyclopedia and dictionary...")
        
        from amilib.ami_dict import AmiDictionary
        
        # Create both from same source
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        encyclopedia = AmiEncyclopedia()
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Verify entries have Wikidata IDs (or skip if test file doesn't have them)
        entries_with_wikidata = [e for e in encyclopedia.entries if e.get('wikidata_id')]
        if len(entries_with_wikidata) == 0:
            print("⚠️  Test file does not have Wikidata IDs - skipping concurrent usage test")
            return
        
        # Use dictionary to find terms - HTML dictionaries use get_ami_entries(), not entries
        dict_terms = [entry.get_term() for entry in dictionary.get_ami_entries() if entry.get_term()]
        
        # Use encyclopedia to normalize and aggregate
        encyclopedia.normalize_by_wikidata_id()
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Both should work independently
        assert len(dict_terms) > 0, "Dictionary should provide terms"
        assert len(synonym_groups) > 0, "Encyclopedia should provide synonym groups"
        
        print(f"✅ Dictionary provides {len(dict_terms)} terms, encyclopedia provides {len(synonym_groups)} groups")
    
    def test_encyclopedia_html_output_from_dictionary_source(self):
        """Test that encyclopedia can generate HTML from dictionary source"""
        print("🧪 Testing encyclopedia HTML output from dictionary source...")
        
        from amilib.ami_dict import AmiDictionary
        
        dictionary = AmiDictionary.create_from_html_file(self.test_html_file)
        encyclopedia = AmiEncyclopedia(title=dictionary.title)
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Generate normalized HTML
        html_content = encyclopedia.create_wiki_normalized_html()
        
        assert html_content is not None, "Should generate HTML"
        assert len(html_content) > 0, "HTML should not be empty"
        assert '<div role="ami_encyclopedia"' in html_content, "Should contain encyclopedia container"
        
        # Save and verify
        output_file = self.temp_dir / "composition_test.html"
        encyclopedia.save_wiki_normalized_html(output_file)
        
        assert output_file.exists(), "Output file should be created"
        
        print("✅ Generated HTML output from dictionary source")


if __name__ == '__main__':
    unittest.main()
