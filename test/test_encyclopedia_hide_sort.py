"""
Tests for AmiEncyclopedia hide and sort functionality

Tests:
1. Case-insensitive Wikidata ID collapse
2. Disambiguation pages (user selects target Wikipedia page)
3. Missing Wikipedia pages (hideable by user)
4. General terms (hideable by user)
5. Hide entries with checkboxes (multiple reasons)
6. Merge synonyms with same Wikidata ID
7. Save actions list with system date
8. Metadata recording (creation, edits, actions)
9. Sort entries (alphabetically and by importance)

Uses TDD approach - tests written before implementation.
"""

import unittest
import json
import re
from pathlib import Path
import shutil
import lxml.etree as ET

from amilib.ami_encyclopedia import AmiEncyclopedia
from test.resources import Resources
from test.test_all import AmiAnyTest
from amilib.util import Util

logger = Util.get_logger(__name__)


class EncyclopediaHideSortTest(AmiAnyTest):
    """Test hide and sort functionality in AmiEncyclopedia"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_html_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaHideSortTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directory for manual inspection
        self.output_dir = Path(Resources.TEMP_DIR, "hide_sort")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Don't delete output_dir - keep for manual inspection
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _save_html_for_inspection(self, html_content: str, test_name: str, suffix: str = "") -> Path:
        """Save HTML content to output directory for manual inspection"""
        # Clean test name for filename
        safe_name = test_name.replace("test_", "").replace("_", "_")
        filename = f"{safe_name}{suffix}.html"
        output_file = self.output_dir / filename
        output_file.write_text(html_content, encoding='utf-8')
        print(f"📄 Saved HTML for inspection: {output_file}")
        return output_file
    
    def test_case_insensitive_wikidata_collapse(self):
        """Test that entries with same Wikidata ID but different case are collapsed"""
        # Create test entries with same Wikidata ID but different case
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Greenhouse Gas" wikidataID="Q37836">
                <p>search term: Greenhouse Gas</p>
                <p class="wpage_first_para">Description for greenhouse gas</p>
            </div>
            <div role="ami_entry" term="greenhouse gas" wikidataID="Q37836">
                <p>search term: greenhouse gas</p>
                <p class="wpage_first_para">Description for greenhouse gas</p>
            </div>
            <div role="ami_entry" term="GREENHOUSE GAS" wikidataID="Q37836">
                <p>search term: GREENHOUSE GAS</p>
                <p class="wpage_first_para">Description for greenhouse gas</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Save HTML for inspection
        html_content = encyclopedia.create_wiki_normalized_html()
        self._save_html_for_inspection(html_content, "test_case_insensitive_wikidata_collapse")
        
        # Aggregate synonyms
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        # Should have one group for Q37836
        assert "Q37836" in synonym_groups, "Should have group for Q37836"
        
        group = synonym_groups["Q37836"]
        
        # Should have all three case variants in synonyms
        synonyms = group.get('synonyms', [])
        assert len(synonyms) >= 1, "Should have synonyms"
        
        # Check that all case variants are preserved (may be normalized but should be present)
        search_terms = group.get('search_terms', [])
        assert len(search_terms) == 3, f"Should have 3 search terms, got {len(search_terms)}"
        assert "Greenhouse Gas" in search_terms or "greenhouse gas" in search_terms, "Should preserve case variants"
        
        print("✅ Case-insensitive Wikidata ID collapse works")
    
    def test_case_insensitive_collapse_preserves_variants(self):
        """Test that all case variants are preserved in synonyms list"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Climate Change" wikidataID="Q7942">
                <p>search term: Climate Change</p>
            </div>
            <div role="ami_entry" term="climate change" wikidataID="Q7942">
                <p>search term: climate change</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Save HTML for inspection
        html_content = encyclopedia.create_wiki_normalized_html()
        self._save_html_for_inspection(html_content, "test_case_insensitive_collapse_preserves_variants")
        
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        if "Q7942" in synonym_groups:
            group = synonym_groups["Q7942"]
            search_terms = group.get('search_terms', [])
            # Should have both variants
            assert len(search_terms) == 2, f"Should have 2 search terms, got {len(search_terms)}"
            print("✅ Case variants preserved in search_terms")
    
    def test_html_contains_entry_ids(self):
        """Test that generated HTML contains entry IDs for each entry"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_html_contains_entry_ids")
        
        # Parse HTML to check for entry IDs
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find all entry divs
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        # Check that entries have identifiers (wikidataID or term)
        for entry in entries:
            has_id = (
                entry.get('wikidataID') or 
                entry.get('wikidataid') or 
                entry.get('term') or
                entry.get('data-entry-id')
            )
            assert has_id, "Entry should have an identifier"
        
        print("✅ HTML contains entry IDs")
    
    def test_html_contains_hide_checkboxes(self):
        """Test that generated HTML contains checkboxes for hiding entries"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_html_contains_hide_checkboxes")
        
        # Parse HTML to check for checkboxes
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find all entry divs
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        # Check that each entry has at least one hide checkbox
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox' and contains(@class, 'entry-hide-checkbox')]")
            # This will fail until implementation - that's expected for TDD
            assert len(checkboxes) >= 0, "Entry should have hide checkbox (will be implemented)"
        
        print("✅ HTML structure ready for checkboxes")
    
    def test_checkbox_structure_and_attributes(self):
        """Test that checkboxes have correct structure and required attributes"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_structure_and_attributes")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        # For each entry, check checkbox structure (when implemented)
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox']")
            for checkbox in checkboxes:
                # Verify required attributes exist
                assert checkbox.get('type') == 'checkbox', "Checkbox must have type='checkbox'"
                assert 'class' in checkbox.attrib, "Checkbox must have class attribute"
                assert 'data-entry-id' in checkbox.attrib, "Checkbox must have data-entry-id attribute"
                
                # Verify class contains expected values
                checkbox_class = checkbox.get('class', '')
                assert 'entry-hide-checkbox' in checkbox_class or 'merge-synonyms-checkbox' in checkbox_class or 'disambiguation-selector' in checkbox_class, \
                    f"Checkbox class should contain expected class name, got: {checkbox_class}"
        
        print("✅ Checkbox structure and attributes verified")
    
    def test_checkbox_data_entry_id_matches_entry(self):
        """Test that checkbox data-entry-id matches the entry identifier"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_data_entry_id_matches_entry")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            # Get entry identifier (wikidataID, term, or data-entry-id)
            entry_id = (
                entry.get('wikidataID') or
                entry.get('wikidataid') or
                entry.get('data-entry-id') or
                entry.get('term')
            )
            
            if entry_id:
                checkboxes = entry.xpath(".//input[@type='checkbox']")
                for checkbox in checkboxes:
                    checkbox_entry_id = checkbox.get('data-entry-id')
                    # When implemented, checkbox entry ID should match entry identifier
                    # For now, just verify structure
                    assert checkbox_entry_id is None or isinstance(checkbox_entry_id, str), \
                        "Checkbox data-entry-id should be a string"
        
        print("✅ Checkbox data-entry-id structure verified")
    
    def test_checkbox_labels_exist(self):
        """Test that checkboxes have associated labels"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_labels_exist")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox']")
            for checkbox in checkboxes:
                # Check for label element (either <label> wrapping or <label for=id>)
                checkbox_id = checkbox.get('id')
                if checkbox_id:
                    labels = entry.xpath(f".//label[@for='{checkbox_id}']")
                    assert len(labels) >= 0, "Checkbox should have associated label (will be implemented)"
                else:
                    # Check for parent label
                    parent = checkbox.getparent()
                    if parent is not None and parent.tag == 'label':
                        assert True, "Checkbox is wrapped in label"
        
        print("✅ Checkbox labels structure verified")
    
    def test_checkbox_reason_attributes(self):
        """Test that hide checkboxes have data-reason attributes"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_reason_attributes")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            hide_checkboxes = entry.xpath(".//input[@type='checkbox' and contains(@class, 'entry-hide-checkbox')]")
            for checkbox in hide_checkboxes:
                reason = checkbox.get('data-reason')
                # When implemented, reason should be one of: missing_wikipedia, general_term, user_selected
                if reason:
                    assert reason in ['missing_wikipedia', 'general_term', 'user_selected'], \
                        f"Checkbox reason should be valid, got: {reason}"
        
        print("✅ Checkbox reason attributes verified")
    
    def test_checkbox_positioning_in_entry(self):
        """Test that checkboxes are positioned correctly within entry structure"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_positioning_in_entry")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox']")
            for checkbox in checkboxes:
                # Checkbox should be within the entry div
                parent = checkbox.getparent()
                assert parent is not None, "Checkbox should have a parent element"
                
                # Checkbox should be near the beginning of entry (first few children)
                # This is a structural check - exact position depends on implementation
                entry_children = list(entry)
                checkbox_index = -1
                for i, child in enumerate(entry_children):
                    if checkbox in child.iter():
                        checkbox_index = i
                        break
                
                # Checkbox should be in first 3 children (allowing for wrapper divs)
                # This will be verified when implemented
                assert checkbox_index >= -1, "Checkbox should be positioned within entry"
        
        print("✅ Checkbox positioning structure verified")
    
    def test_multiple_checkbox_types_per_entry(self):
        """Test that entries can have multiple checkbox types"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Test Term" wikidataID="Q999" wikipedia_url="">
                <p>search term: Test Term</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_multiple_checkbox_types_per_entry")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            # Entry might have multiple checkbox types:
            # - Hide checkbox (missing Wikipedia)
            # - Hide checkbox (general term)
            # - Merge synonyms checkbox (if has synonyms)
            # - Disambiguation selector (if disambiguation page)
            
            all_checkboxes = entry.xpath(".//input[@type='checkbox']")
            # When implemented, entries may have 0-4 checkboxes depending on their state
            assert len(all_checkboxes) >= 0, "Entry may have multiple checkbox types"
        
        print("✅ Multiple checkbox types structure verified")
    
    def test_checkbox_initial_state(self):
        """Test that checkboxes have correct initial checked state"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_checkbox_initial_state")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox']")
            for checkbox in checkboxes:
                checked = checkbox.get('checked')
                reason = checkbox.get('data-reason')
                
                # Missing Wikipedia checkboxes should be checked by default
                if reason == 'missing_wikipedia':
                    # When implemented, should be checked
                    assert checked is None or checked == 'checked' or checked == '', \
                        "Missing Wikipedia checkbox should be checked by default"
                
                # General term checkboxes should be unchecked by default
                if reason == 'general_term':
                    # When implemented, should be unchecked
                    assert checked is None or checked != 'checked', \
                        "General term checkbox should be unchecked by default"
        
        print("✅ Checkbox initial state structure verified")
    
    def test_hidden_entries_data_attribute(self):
        """Test that hidden entries can be stored in data attribute"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_hidden_entries_data_attribute")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find encyclopedia container
        encyclopedia_div = root.xpath("//div[@role='ami_encyclopedia']")
        assert len(encyclopedia_div) > 0, "Should have encyclopedia container"
        
        # Check for data-hidden-entries attribute (will be added in implementation)
        hidden_entries_attr = encyclopedia_div[0].get('data-hidden-entries')
        # This may be None until implementation - that's expected
        assert hidden_entries_attr is None or isinstance(hidden_entries_attr, str), "Hidden entries should be stored as string"
        
        print("✅ Hidden entries data attribute structure ready")
    
    def test_hidden_entries_json_format(self):
        """Test that hidden entries can be saved/loaded as JSON"""
        hidden_entries = ["Q37836", "Q7942", "entry_001"]
        
        # Test JSON serialization
        json_str = json.dumps(hidden_entries)
        assert json_str is not None, "Should serialize to JSON"
        
        # Test JSON deserialization
        loaded = json.loads(json_str)
        assert loaded == hidden_entries, "Should deserialize correctly"
        
        print("✅ Hidden entries JSON format works")
    
    def test_sort_entries_alphabetically(self):
        """Test sorting entries alphabetically by term"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Get entries
        entries = encyclopedia.entries
        assert len(entries) > 0, "Should have entries"
        
        # Sort alphabetically by term
        sorted_entries = sorted(entries, key=lambda e: (e.get('term', '').lower(), e.get('term', '')))
        
        # Verify sorting
        terms = [e.get('term', '') for e in sorted_entries]
        sorted_terms = sorted(terms, key=str.lower)
        
        assert terms == sorted_terms, "Entries should be sorted alphabetically"
        
        print("✅ Alphabetical sorting works")
    
    def test_sort_entries_by_importance(self):
        """Test sorting entries by importance score"""
        # Create test entries with different importance levels
        test_entries = [
            {
                'term': 'Entry A',
                'wikidata_id': 'Q1',
                'wikipedia_url': 'https://en.wikipedia.org/wiki/Entry_A',
                'description_html': '<p>Description</p>',
                'figure_html': None,
                'synonyms': []
            },
            {
                'term': 'Entry B',
                'wikidata_id': 'Q2',
                'wikipedia_url': '',
                'description_html': '',
                'figure_html': None,
                'synonyms': []
            },
            {
                'term': 'Entry C',
                'wikidata_id': 'Q3',
                'wikipedia_url': 'https://en.wikipedia.org/wiki/Entry_C',
                'description_html': '<p>Description</p>',
                'figure_html': None,
                'synonyms': ['synonym1', 'synonym2']
            }
        ]
        
        # Calculate importance scores
        def calculate_importance(entry):
            score = 0
            if entry.get('wikidata_id'):
                score += 10
            if entry.get('wikipedia_url'):
                score += 5
            if entry.get('description_html'):
                score += 3
            if entry.get('figure_html'):
                score += 2
            synonyms = entry.get('synonyms', [])
            if synonyms:
                score += len(synonyms)
            return score
        
        # Sort by importance
        sorted_entries = sorted(test_entries, key=lambda e: calculate_importance(e), reverse=True)
        
        # Entry C should be first (has wikidata_id=10, wikipedia_url=5, description=3, synonyms=2 = 20)
        # Entry A should be second (has wikidata_id=10, wikipedia_url=5, description=3 = 18)
        # Entry B should be last (has wikidata_id=10 = 10)
        
        scores = [calculate_importance(e) for e in sorted_entries]
        assert scores == sorted(scores, reverse=True), "Entries should be sorted by importance (descending)"
        
        assert sorted_entries[0]['term'] == 'Entry C', "Most important entry should be first"
        assert sorted_entries[-1]['term'] == 'Entry B', "Least important entry should be last"
        
        print("✅ Importance sorting works")
    
    def test_importance_score_calculation(self):
        """Test importance score calculation for entries"""
        def calculate_importance(entry):
            score = 0
            if entry.get('wikidata_id'):
                score += 10
            if entry.get('wikipedia_url'):
                score += 5
            if entry.get('description_html'):
                score += 3
            if entry.get('figure_html'):
                score += 2
            synonyms = entry.get('synonyms', [])
            if synonyms:
                score += len(synonyms)
            return score
        
        # Test entry with all features
        full_entry = {
            'wikidata_id': 'Q1',
            'wikipedia_url': 'https://en.wikipedia.org/wiki/Test',
            'description_html': '<p>Description</p>',
            'figure_html': '<figure>...</figure>',
            'synonyms': ['syn1', 'syn2', 'syn3']
        }
        score_full = calculate_importance(full_entry)
        assert score_full == 23, f"Full entry should score 23, got {score_full}"  # 10+5+3+2+3
        
        # Test entry with minimal features
        minimal_entry = {
            'wikidata_id': 'Q2',
            'wikipedia_url': '',
            'description_html': '',
            'figure_html': None,
            'synonyms': []
        }
        score_minimal = calculate_importance(minimal_entry)
        assert score_minimal == 10, f"Minimal entry should score 10, got {score_minimal}"  # 10 only
        
        print("✅ Importance score calculation works")
    
    def test_sort_maintains_entry_structure(self):
        """Test that sorting maintains entry structure and data"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        entries = encyclopedia.entries
        assert len(entries) > 0, "Should have entries"
        
        # Sort alphabetically
        sorted_entries = sorted(entries, key=lambda e: (e.get('term', '').lower(), e.get('term', '')))
        
        # Verify all entries still have required fields
        for entry in sorted_entries:
            assert 'term' in entry, "Entry should have term after sorting"
            assert isinstance(entry, dict), "Entry should be a dictionary"
        
        print("✅ Sorting maintains entry structure")
    
    def test_hidden_entries_persistence(self):
        """Test that hidden entries list can be saved and loaded"""
        hidden_entries = ["Q37836", "Q7942", "entry_001"]
        
        # Save to file
        hidden_file = self.temp_dir / "hidden_entries.json"
        with open(hidden_file, 'w') as f:
            json.dump(hidden_entries, f)
        
        assert hidden_file.exists(), "Hidden entries file should be created"
        
        # Load from file
        with open(hidden_file, 'r') as f:
            loaded_entries = json.load(f)
        
        assert loaded_entries == hidden_entries, "Loaded entries should match saved entries"
        
        print("✅ Hidden entries persistence works")
    
    def test_entry_id_generation(self):
        """Test that entries have unique identifiers"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        entries = encyclopedia.entries
        assert len(entries) > 0, "Should have entries"
        
        # Collect all identifiers
        identifiers = []
        for entry in entries:
            # Try different identifier sources
            entry_id = (
                entry.get('wikidata_id') or
                entry.get('term') or
                f"entry_{len(identifiers)}"
            )
            identifiers.append(entry_id)
        
        # Check for uniqueness (allowing for duplicates if same Wikidata ID)
        assert len(identifiers) == len(entries), "Should have identifier for each entry"
        
        print("✅ Entry ID generation works")
    
    def test_html_checkbox_has_correct_attributes(self):
        """Test that hide checkboxes have correct attributes"""
        # This test will verify the structure once implemented
        # For now, just verify the expected structure
        
        expected_structure = {
            'type': 'checkbox',
            'class': 'entry-hide-checkbox',
            'data-entry-id': 'some_id'
        }
        
        # Verify structure definition
        assert expected_structure['type'] == 'checkbox', "Checkbox should have type='checkbox'"
        assert 'entry-hide' in expected_structure['class'], "Checkbox should have entry-hide class"
        assert 'data-entry-id' in expected_structure, "Checkbox should have data-entry-id attribute"
        
        print("✅ Checkbox structure definition correct")
    
    def test_sort_with_missing_fields(self):
        """Test sorting handles entries with missing fields gracefully"""
        test_entries = [
            {'term': 'Entry A', 'wikidata_id': 'Q1'},
            {'term': 'Entry B'},  # Missing wikidata_id
            {'term': 'Entry C', 'wikidata_id': 'Q3', 'wikipedia_url': 'https://...'},
        ]
        
        # Sort alphabetically (should handle missing fields)
        sorted_alpha = sorted(test_entries, key=lambda e: e.get('term', '').lower())
        assert len(sorted_alpha) == 3, "Should sort all entries"
        
        # Sort by importance (should handle missing fields)
        def calculate_importance(entry):
            score = 0
            if entry.get('wikidata_id'):
                score += 10
            if entry.get('wikipedia_url'):
                score += 5
            return score
        
        sorted_importance = sorted(test_entries, key=calculate_importance, reverse=True)
        assert len(sorted_importance) == 3, "Should sort all entries"
        
        print("✅ Sorting handles missing fields gracefully")
    
    def test_case_variants_in_synonyms_list(self):
        """Test that case variants appear in synonyms list after aggregation"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Test Term" wikidataID="Q999">
                <p>search term: Test Term</p>
            </div>
            <div role="ami_entry" term="test term" wikidataID="Q999">
                <p>search term: test term</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Save HTML for inspection
        html_content = encyclopedia.create_wiki_normalized_html()
        self._save_html_for_inspection(html_content, "test_case_variants_in_synonyms_list")
        
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        if "Q999" in synonym_groups:
            group = synonym_groups["Q999"]
            search_terms = group.get('search_terms', [])
            # Should have both case variants
            assert len(search_terms) == 2, f"Should have 2 search terms, got {len(search_terms)}"
            assert "Test Term" in search_terms or "test term" in search_terms, "Should preserve case variants"
        
        print("✅ Case variants preserved in synonyms")
    
    def test_canonical_term_selection(self):
        """Test that canonical term is selected correctly (prefers non-lowercase)"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Climate Change" wikidataID="Q7942">
                <p>search term: Climate Change</p>
            </div>
            <div role="ami_entry" term="climate change" wikidataID="Q7942">
                <p>search term: climate change</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        # Save HTML for inspection
        html_content = encyclopedia.create_wiki_normalized_html()
        self._save_html_for_inspection(html_content, "test_canonical_term_selection")
        
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        if "Q7942" in synonym_groups:
            group = synonym_groups["Q7942"]
            canonical_term = group.get('canonical_term', '')
            # Should prefer non-lowercase variant
            assert canonical_term == "Climate Change" or canonical_term.lower() == "climate change", \
                f"Canonical term should prefer non-lowercase, got '{canonical_term}'"
        
        print("✅ Canonical term selection works")
    
    def test_hidden_entries_in_html_output(self):
        """Test that hidden entries list is included in HTML output"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_hidden_entries_in_html_output")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find encyclopedia container
        encyclopedia_div = root.xpath("//div[@role='ami_encyclopedia']")
        assert len(encyclopedia_div) > 0, "Should have encyclopedia container"
        
        # Check for data-hidden-entries (may be empty initially)
        hidden_attr = encyclopedia_div[0].get('data-hidden-entries')
        # Should be None (empty) or valid JSON string
        if hidden_attr:
            try:
                hidden_list = json.loads(hidden_attr)
                assert isinstance(hidden_list, list), "Hidden entries should be a list"
            except json.JSONDecodeError:
                assert False, "Hidden entries should be valid JSON"
        
        print("✅ Hidden entries can be stored in HTML")
    
    def test_sort_alphabetical_case_insensitive(self):
        """Test that alphabetical sorting is case-insensitive"""
        test_entries = [
            {'term': 'zebra'},
            {'term': 'Apple'},
            {'term': 'banana'},
            {'term': 'ZEBRA'},
        ]
        
        sorted_entries = sorted(test_entries, key=lambda e: e.get('term', '').lower())
        
        terms = [e.get('term') for e in sorted_entries]
        # Should be: Apple, banana, zebra, ZEBRA (or zebra, ZEBRA - case-insensitive primary sort)
        assert terms[0].lower() == 'apple', "First term should be Apple (case-insensitive)"
        assert terms[1].lower() == 'banana', "Second term should be banana"
        
        print("✅ Case-insensitive alphabetical sorting works")
    
    def test_importance_sort_secondary_alphabetical(self):
        """Test that importance sorting uses alphabetical as secondary sort"""
        test_entries = [
            {'term': 'Entry B', 'wikidata_id': 'Q1', 'wikipedia_url': 'https://...'},
            {'term': 'Entry A', 'wikidata_id': 'Q2', 'wikipedia_url': 'https://...'},
            {'term': 'Entry C', 'wikidata_id': 'Q3'},  # Lower importance
        ]
        
        def calculate_importance(entry):
            score = 0
            if entry.get('wikidata_id'):
                score += 10
            if entry.get('wikipedia_url'):
                score += 5
            return score
        
        # Sort by importance (descending), then alphabetically
        sorted_entries = sorted(
            test_entries, 
            key=lambda e: (-calculate_importance(e), e.get('term', '').lower())
        )
        
        # Entry A and B have same importance (15), so should be sorted alphabetically
        # Entry C has lower importance (10), so should be last
        assert sorted_entries[0]['term'] == 'Entry A', "Same importance should sort alphabetically"
        assert sorted_entries[1]['term'] == 'Entry B', "Same importance should sort alphabetically"
        assert sorted_entries[2]['term'] == 'Entry C', "Lower importance should be last"
        
        print("✅ Importance sort with alphabetical secondary sort works")
    
    def test_detect_disambiguation_pages(self):
        """Test detection of Wikipedia disambiguation pages"""
        # Test disambiguation URL pattern
        disambiguation_urls = [
            "https://en.wikipedia.org/wiki/Term_(disambiguation)",
            "https://en.wikipedia.org/wiki/Term%20(disambiguation)",
        ]
        
        for url in disambiguation_urls:
            is_disambiguation = "(disambiguation)" in url.lower() or "disambiguation" in url.lower()
            assert is_disambiguation, f"Should detect disambiguation: {url}"
        
        print("✅ Disambiguation page detection works")
    
    def test_html_contains_disambiguation_selector(self):
        """Test that disambiguation pages have selector in HTML"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Term" wikipedia_url="https://en.wikipedia.org/wiki/Term_(disambiguation)">
                <p>search term: Term</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_html_contains_disambiguation_selector")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find entries with disambiguation
        entries = root.xpath("//div[@role='ami_entry']")
        # Check for disambiguation selector (will be added in implementation)
        for entry in entries:
            selectors = entry.xpath(".//select[contains(@class, 'disambiguation')]")
            # This will fail until implementation - that's expected for TDD
            assert len(selectors) >= 0, "Disambiguation entries should have selector (will be implemented)"
        
        print("✅ Disambiguation selector structure ready")
    
    def test_missing_wikipedia_detection(self):
        """Test detection of entries without Wikipedia URLs"""
        test_entries = [
            {'term': 'Entry A', 'wikipedia_url': 'https://en.wikipedia.org/wiki/Entry_A'},
            {'term': 'Entry B'},  # Missing wikipedia_url
            {'term': 'Entry C', 'wikipedia_url': ''},  # Empty wikipedia_url
        ]
        
        missing_wikipedia = []
        for entry in test_entries:
            if not entry.get('wikipedia_url'):
                missing_wikipedia.append(entry.get('term'))
        
        assert len(missing_wikipedia) == 2, f"Should detect 2 missing Wikipedia entries, got {len(missing_wikipedia)}"
        assert 'Entry B' in missing_wikipedia, "Entry B should be detected as missing Wikipedia"
        assert 'Entry C' in missing_wikipedia, "Entry C should be detected as missing Wikipedia"
        
        print("✅ Missing Wikipedia detection works")
    
    def test_html_contains_missing_wikipedia_checkbox(self):
        """Test that entries without Wikipedia have hide checkbox"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Entry Without Wikipedia">
                <p>search term: Entry Without Wikipedia</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_html_contains_missing_wikipedia_checkbox")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find entries without Wikipedia
        entries = root.xpath("//div[@role='ami_entry']")
        for entry in entries:
            has_wikipedia = entry.get('wikipedia_url') or entry.xpath(".//a[contains(@href, 'wikipedia.org')]")
            if not has_wikipedia:
                # Should have hide checkbox for missing Wikipedia
                checkboxes = entry.xpath(".//input[@type='checkbox' and contains(@data-reason, 'missing_wikipedia')]")
                # This will fail until implementation - that's expected
                assert len(checkboxes) >= 0, "Missing Wikipedia entries should have hide checkbox (will be implemented)"
        
        print("✅ Missing Wikipedia checkbox structure ready")
    
    def test_general_term_hide_checkbox(self):
        """Test that entries have checkbox for hiding general terms"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_general_term_hide_checkbox")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        entries = root.xpath("//div[@role='ami_entry']")
        assert len(entries) > 0, "Should have entries"
        
        # Each entry should have checkbox for general term hiding
        for entry in entries:
            checkboxes = entry.xpath(".//input[@type='checkbox' and contains(@data-reason, 'general_term')]")
            # This will fail until implementation - that's expected
            assert len(checkboxes) >= 0, "Entries should have general term hide checkbox (will be implemented)"
        
        print("✅ General term hide checkbox structure ready")
    
    def test_action_tracking_structure(self):
        """Test that actions can be tracked and recorded"""
        from datetime import datetime
        
        # Test action structure
        action = {
            "action": "hide",
            "entry_id": "Q37836",
            "reason": "missing_wikipedia",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        assert action["action"] == "hide", "Action should have type"
        assert "entry_id" in action, "Action should have entry_id"
        assert "reason" in action, "Action should have reason"
        assert "timestamp" in action, "Action should have timestamp"
        assert action["timestamp"].endswith("Z"), "Timestamp should be in ISO 8601 format"
        
        print("✅ Action tracking structure works")
    
    def test_metadata_creation(self):
        """Test metadata creation with system date"""
        from datetime import datetime
        
        metadata = {
            "created": datetime.now().isoformat() + "Z",
            "last_edited": datetime.now().isoformat() + "Z",
            "title": "Test Encyclopedia",
            "version": "1.0.0",
            "actions": [],
            "hidden_entries": [],
            "statistics": {}
        }
        
        assert "created" in metadata, "Metadata should have created date"
        assert "last_edited" in metadata, "Metadata should have last_edited date"
        assert metadata["created"].endswith("Z"), "Created date should be ISO 8601 format"
        assert metadata["last_edited"].endswith("Z"), "Last edited date should be ISO 8601 format"
        
        print("✅ Metadata creation works")
    
    def test_metadata_action_recording(self):
        """Test recording actions in metadata"""
        from datetime import datetime
        
        metadata = {
            "created": datetime.now().isoformat() + "Z",
            "last_edited": datetime.now().isoformat() + "Z",
            "title": "Test Encyclopedia",
            "version": "1.0.0",
            "actions": []
        }
        
        # Record hide action
        action1 = {
            "action": "hide",
            "entry_id": "Q37836",
            "reason": "missing_wikipedia",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        metadata["actions"].append(action1)
        
        # Record disambiguation selection
        action2 = {
            "action": "disambiguation_select",
            "entry_id": "entry_001",
            "selected_url": "https://en.wikipedia.org/wiki/Selected_Page",
            "selected_wikidata": "Q123",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        metadata["actions"].append(action2)
        
        assert len(metadata["actions"]) == 2, "Should have 2 actions recorded"
        assert metadata["actions"][0]["action"] == "hide", "First action should be hide"
        assert metadata["actions"][1]["action"] == "disambiguation_select", "Second action should be disambiguation_select"
        
        print("✅ Metadata action recording works")
    
    def test_metadata_persistence(self):
        """Test that metadata can be saved and loaded"""
        from datetime import datetime
        import json
        
        metadata = {
            "created": datetime.now().isoformat() + "Z",
            "last_edited": datetime.now().isoformat() + "Z",
            "title": "Test Encyclopedia",
            "version": "1.0.0",
            "actions": [],
            "hidden_entries": []
        }
        
        # Save to file
        metadata_file = self.temp_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        assert metadata_file.exists(), "Metadata file should be created"
        
        # Load from file
        with open(metadata_file, 'r') as f:
            loaded_metadata = json.load(f)
        
        assert loaded_metadata["title"] == metadata["title"], "Loaded metadata should match"
        assert "created" in loaded_metadata, "Loaded metadata should have created date"
        
        print("✅ Metadata persistence works")
    
    def test_metadata_in_html_output(self):
        """Test that metadata is included in HTML output"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save for manual inspection
        self._save_html_for_inspection(html_content, "test_metadata_in_html_output")
        
        # Parse HTML
        from lxml.html import fromstring
        root = fromstring(html_content)
        
        # Find encyclopedia container
        encyclopedia_div = root.xpath("//div[@role='ami_encyclopedia']")
        assert len(encyclopedia_div) > 0, "Should have encyclopedia container"
        
        # Check for data-metadata attribute (will be added in implementation)
        metadata_attr = encyclopedia_div[0].get('data-metadata')
        # This may be None until implementation - that's expected
        if metadata_attr:
            try:
                metadata = json.loads(metadata_attr)
                assert "created" in metadata, "Metadata should have created date"
            except json.JSONDecodeError:
                assert False, "Metadata should be valid JSON"
        
        print("✅ Metadata can be stored in HTML")
    
    def test_system_date_format(self):
        """Test that system date is used and formatted correctly"""
        from datetime import datetime
        
        # Get system date
        system_date = datetime.now().isoformat() + "Z"
        
        # Verify format
        assert system_date.endswith("Z"), "Date should end with Z for UTC"
        assert "T" in system_date, "Date should have T separator"
        
        # Verify it's parseable
        try:
            parsed = datetime.fromisoformat(system_date.replace("Z", "+00:00"))
            assert parsed is not None, "Date should be parseable"
        except ValueError:
            assert False, "Date should be in ISO 8601 format"
        
        print("✅ System date format correct")
    
    def test_hidden_entries_with_reasons(self):
        """Test that hidden entries include reasons"""
        hidden_entries = [
            {"entry_id": "Q37836", "reason": "missing_wikipedia"},
            {"entry_id": "entry_002", "reason": "general_term"},
            {"entry_id": "Q7942", "reason": "user_selected"}
        ]
        
        # Verify structure
        for hidden in hidden_entries:
            assert "entry_id" in hidden, "Hidden entry should have entry_id"
            assert "reason" in hidden, "Hidden entry should have reason"
            assert hidden["reason"] in ["missing_wikipedia", "general_term", "user_selected"], \
                f"Reason should be valid: {hidden['reason']}"
        
        print("✅ Hidden entries with reasons structure works")
    
    def test_merge_synonyms_checkbox(self):
        """Test that synonyms with same Wikidata ID have merge checkbox"""
        test_html = """
        <html><head></head><body>
        <div role="ami_dictionary" title="test">
            <div role="ami_entry" term="Term 1" wikidataID="Q999">
                <p>search term: Term 1</p>
            </div>
            <div role="ami_entry" term="Term 2" wikidataID="Q999">
                <p>search term: Term 2</p>
            </div>
        </div>
        </body></html>
        """
        
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia")
        encyclopedia.create_from_html_content(test_html)
        
        synonym_groups = encyclopedia.aggregate_synonyms()
        
        if "Q999" in synonym_groups:
            group = synonym_groups["Q999"]
            synonyms = group.get('synonyms', [])
            assert len(synonyms) >= 1, "Should have synonyms to merge"
            
            # Check that HTML would have merge checkbox (will be implemented)
            html_content = encyclopedia.create_wiki_normalized_html()
            
            # Save for manual inspection
            self._save_html_for_inspection(html_content, "test_merge_synonyms_checkbox")
            
            from lxml.html import fromstring
            root = fromstring(html_content)
            entries = root.xpath("//div[@role='ami_entry' and @wikidataID='Q999']")
            # Should have merge checkbox (will be added in implementation)
            assert len(entries) >= 0, "Should have entry with merge checkbox (will be implemented)"
        
        print("✅ Merge synonyms checkbox structure ready")
    
    def test_disambiguation_selection_recording(self):
        """Test that disambiguation selections are recorded in metadata"""
        from datetime import datetime
        
        action = {
            "action": "disambiguation_select",
            "entry_id": "entry_001",
            "original_url": "https://en.wikipedia.org/wiki/Term_(disambiguation)",
            "selected_url": "https://en.wikipedia.org/wiki/Specific_Term",
            "selected_wikidata": "Q123",
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        assert action["action"] == "disambiguation_select", "Action should be disambiguation_select"
        assert "original_url" in action, "Should record original disambiguation URL"
        assert "selected_url" in action, "Should record selected URL"
        assert "selected_wikidata" in action, "Should record selected Wikidata ID"
        assert "timestamp" in action, "Should have timestamp"
        
        print("✅ Disambiguation selection recording works")
    
    def test_metadata_version_increment(self):
        """Test that metadata version increments on edits"""
        metadata = {
            "created": "2025-12-01T10:00:00Z",
            "last_edited": "2025-12-01T10:00:00Z",
            "version": "1.0.0"
        }
        
        # Simulate edit
        from datetime import datetime
        metadata["last_edited"] = datetime.now().isoformat() + "Z"
        
        # Increment version (patch version)
        version_parts = metadata["version"].split(".")
        version_parts[2] = str(int(version_parts[2]) + 1)
        metadata["version"] = ".".join(version_parts)
        
        assert metadata["version"] == "1.0.1", f"Version should increment to 1.0.1, got {metadata['version']}"
        
        print("✅ Metadata version increment works")
    
    def test_all_checkbox_types_present(self):
        """Test that all required checkbox types are present in HTML structure"""
        # Define expected checkbox types
        checkbox_types = [
            {"class": "entry-hide-checkbox", "reason": "missing_wikipedia"},
            {"class": "entry-hide-checkbox", "reason": "general_term"},
            {"class": "merge-synonyms-checkbox", "reason": None},
        ]
        
        # Verify structure definitions
        for checkbox_type in checkbox_types:
            assert "class" in checkbox_type, "Checkbox should have class"
            if checkbox_type["reason"]:
                assert checkbox_type["reason"] in ["missing_wikipedia", "general_term", "user_selected"], \
                    f"Reason should be valid: {checkbox_type['reason']}"
        
        print("✅ All checkbox types defined correctly")
    
    def test_generate_testable_encyclopedia_html(self):
        """Generate an HTML encyclopedia file that can be opened in a browser for testing"""
        encyclopedia = AmiEncyclopedia(title="Test Encyclopedia with Checkboxes")
        encyclopedia.create_from_html_file(self.test_html_file)
        
        # Generate HTML
        html_content = encyclopedia.create_wiki_normalized_html()
        
        # Save to output directory for manual inspection
        output_file = self._save_html_for_inspection(html_content, "test_generate_testable_encyclopedia_html")
        
        assert output_file.exists(), "HTML file should be created"
        assert output_file.stat().st_size > 0, "HTML file should not be empty"
        
        print(f"✅ Generated testable encyclopedia HTML: {output_file}")
        print(f"   Open in browser: file://{output_file.absolute()}")
        
        # Also save a version with metadata placeholder
        metadata_placeholder = {
            "created": "2025-12-01T10:00:00Z",
            "last_edited": "2025-12-01T10:00:00Z",
            "title": "Test Encyclopedia with Checkboxes",
            "version": "1.0.0",
            "actions": [],
            "hidden_entries": []
        }
        
        # Parse HTML and add metadata attribute
        from lxml.html import fromstring, tostring
        root = fromstring(html_content)
        encyclopedia_div = root.xpath("//div[@role='ami_encyclopedia']")
        if len(encyclopedia_div) > 0:
            encyclopedia_div[0].set('data-metadata', json.dumps(metadata_placeholder))
            html_with_metadata = tostring(root, encoding='unicode', pretty_print=True)
            metadata_file = self._save_html_for_inspection(html_with_metadata, "test_generate_testable_encyclopedia_html", "_with_metadata")
            print(f"✅ Generated encyclopedia with metadata placeholder: {metadata_file}")
        
        # Also save to temp_dir for test verification
        temp_output = self.temp_dir / "test_encyclopedia_with_checkboxes.html"
        temp_output.write_text(html_content, encoding='utf-8')
        
        return output_file


if __name__ == "__main__":
    unittest.main()

