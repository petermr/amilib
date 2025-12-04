"""
AmiEncyclopedia - Encyclopedia management with Wikidata ID normalization

Provides functionality to:
- Extract entries from encyclopedia HTML
- Normalize entries by Wikidata ID
- Aggregate synonyms by Wikidata ID (canonical identifiers)
- Generate normalized encyclopedia output
"""

import re
import json
import lxml.etree as ET
from pathlib import Path
from typing import Optional, Dict, List
from collections import defaultdict, Counter
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone

from amilib.ami_html import HtmlLib
from amilib.wikimedia import WikipediaPage
from amilib.ami_dict import AmiDictionary, AmiEntry
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.xml_lib import XmlLib

logger = Util.get_logger(__name__)


class AmiEncyclopedia:
    """Main encyclopedia class for managing entries and normalization"""
    
    # Checkbox reason constants
    REASON_MISSING_WIKIPEDIA = "missing_wikipedia"
    REASON_GENERAL_TERM = "general_term"
    REASON_FALSE_WIKIPEDIA = "false_wikipedia"
    REASON_USER_SELECTED = "user_selected"
    
    # Entry category constants (for Wikipedia page type)
    CATEGORY_TRUE_WIKIPEDIA = "true_wikipedia"
    CATEGORY_NO_WIKIPEDIA = "no_wikipedia"
    CATEGORY_DISAMBIGUATION = "disambiguation"
    
    # Entry classification constants (for processing status - avoids expensive lookups)
    CLASSIFICATION_UNPROCESSED = "UNPROCESSED"
    CLASSIFICATION_HAS_WIKIDATA = "HAS_WIKIDATA"
    CLASSIFICATION_NO_WIKIDATA_ENTRY = "NO_WIKIDATA_ENTRY"
    CLASSIFICATION_AMBIGUOUS = "AMBIGUOUS"
    CLASSIFICATION_NO_WIKIPEDIA_PAGE = "NO_WIKIPEDIA_PAGE"
    CLASSIFICATION_ERROR = "ERROR"
    
    # Metadata field constants
    METADATA_CREATED = "created"
    METADATA_LAST_EDITED = "last_edited"
    METADATA_TITLE = "title"
    METADATA_VERSION = "version"
    METADATA_ACTIONS = "actions"
    METADATA_HIDDEN_ENTRIES = "hidden_entries"
    METADATA_DISAMBIGUATION_SELECTIONS = "disambiguation_selections"
    METADATA_MERGE_OPERATIONS = "merge_operations"
    METADATA_SORT_HISTORY = "sort_history"
    METADATA_STATISTICS = "statistics"
    
    # Action type constants
    ACTION_HIDE = "hide"
    ACTION_DISAMBIGUATION_SELECT = "disambiguation_select"
    ACTION_MERGE_SYNONYMS = "merge_synonyms"
    ACTION_SORT = "sort"
    
    def __init__(self, title: str = "Encyclopedia"):
        self.title = title
        self.dictionary = None  # AmiDictionary instance (composition)
        self.entries = []  # Processed entries as list of dicts
        self.normalized_entries = {}
        self.synonym_groups = {}  # Dict[str, Dict] - aggregated synonym groups by Wikidata ID
        self.metadata = self._create_metadata()
    
    @classmethod
    def get_valid_checkbox_reasons(cls) -> list:
        """Get list of valid checkbox reason values
        
        Returns:
            List of valid reason strings
        """
        return [
            cls.REASON_MISSING_WIKIPEDIA,
            cls.REASON_GENERAL_TERM,
            cls.REASON_FALSE_WIKIPEDIA,
            cls.REASON_USER_SELECTED,
        ]
    
    @classmethod
    def _get_system_date(cls) -> str:
        """Get current system date in ISO 8601 format with Z suffix (UTC)
        
        Returns:
            ISO 8601 formatted date string with Z suffix in UTC (e.g., "2025-12-03T09:40:12Z")
        """
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    
    def _create_metadata(self) -> Dict:
        """Create initial metadata dictionary with system dates
        
        Returns:
            Dictionary containing metadata with created and last_edited timestamps
        """
        return {
            self.METADATA_CREATED: self._get_system_date(),
            self.METADATA_LAST_EDITED: self._get_system_date(),
            self.METADATA_TITLE: self.title,
            self.METADATA_VERSION: "1.0.0",
            self.METADATA_ACTIONS: [],
            self.METADATA_HIDDEN_ENTRIES: [],
            self.METADATA_DISAMBIGUATION_SELECTIONS: [],
            self.METADATA_MERGE_OPERATIONS: [],
            self.METADATA_SORT_HISTORY: [],
            self.METADATA_STATISTICS: {}
        }
    
    def _update_last_edited(self) -> None:
        """Update last_edited timestamp in metadata to current system date"""
        self.metadata[self.METADATA_LAST_EDITED] = self._get_system_date()
        
    def create_from_html_file(self, html_file: Path) -> 'AmiEncyclopedia':
        """Create encyclopedia from HTML file"""
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        html_content = html_file.read_text(encoding='utf-8')
        return self.create_from_html_content(html_content)
    
    def create_from_html_content(self, html_content: str) -> 'AmiEncyclopedia':
        """Create encyclopedia from HTML content"""
        # Use AmiDictionary to parse HTML
        from io import StringIO
        from tempfile import NamedTemporaryFile
        import os
        
        # Create temporary file for AmiDictionary
        with NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_path = Path(temp_file.name)
        
        try:
            # Parse HTML first to get original elements with all attributes
            from amilib.ami_html import HtmlUtil
            self._original_html_root = HtmlUtil.parse_html_file_to_xml(temp_path)
            
            # Use AmiDictionary to parse (composition)
            self.dictionary = AmiDictionary.create_from_html_file(temp_path, ignorecase=False)
            
            # Convert AmiEntry objects from entry_by_term to dictionary format
            self.entries = []
            for ami_entry in self.dictionary.entry_by_term.values():
                term = ami_entry.get_term()
                entry_element = ami_entry.element
                
                # Extract search_term from <p>search term: ...</p>
                search_term = term
                search_p = entry_element.xpath(".//p[contains(text(), 'search term:')]")
                if search_p and search_p[0].text:
                    search_text = search_p[0].text
                    if 'search term:' in search_text:
                        search_term = search_text.split('search term:')[-1].strip()
                
                # Extract wikidata_id with priority: attribute > from Wikipedia page > lookup
                wikidata_id = ''
                wikipedia_url = ''
                
                # Priority 1: Check if wikidataID is stored as an attribute on the entry element
                # HTML parser lowercases attributes, so wikidataID becomes wikidataid
                # But AmiDictionary may strip it, so check the original HTML element before dictionary processing
                # Try to get it from the original parsed HTML before AmiDictionary processed it
                from amilib.ami_dict import WIKIDATA_ID
                
                # First try AmiEntry property (may not work if AmiDictionary stripped the attribute)
                wikidata_id = ami_entry.wikidata_id if hasattr(ami_entry, 'wikidata_id') else None
                
                # If not found, check element directly (with lowercase variant)
                if not wikidata_id:
                    wikidata_id = (
                        entry_element.get('wikidataID') or 
                        entry_element.get('wikidataid') or  # Lowercase version from HTML parser
                        entry_element.get('wikidata_id') or 
                        entry_element.get(WIKIDATA_ID) or
                        ''
                    )
                
                # If still not found, try to get from original HTML element before dictionary processing
                # AmiDictionary creates new entry elements and only copies term/id, so wikidataID is lost
                # Use the original HTML root we stored during parsing
                if not wikidata_id and hasattr(self, '_original_html_root'):
                    try:
                        # Find the original HTML entry element by term
                        original_entries = self._original_html_root.xpath(f".//div[@role='ami_entry' and @term='{term}']")
                        if not original_entries:
                            # Try by name attribute as fallback
                            original_entries = self._original_html_root.xpath(f".//div[@role='ami_entry' and @name='{term}']")
                        if original_entries:
                            orig_entry = original_entries[0]
                            wikidata_id = (
                                orig_entry.get('wikidataID') or 
                                orig_entry.get('wikidataid') or  # Lowercase from HTML parser
                                orig_entry.get('wikidata_id') or
                                ''
                            )
                    except Exception:
                        pass
                
                # Extract wikipedia_url for display purposes (also needed for Wikidata ID lookup)
                # Try from entry element first
                wikipedia_url = (
                    entry_element.get('wikipedia_url') or 
                    entry_element.get('wikipediaURL') or  # CamelCase variant
                    entry_element.get('wikipedia-url') or  # Kebab-case variant
                    ''
                )
                
                # If not found, try from original HTML element (AmiDictionary may strip attributes)
                if not wikipedia_url and hasattr(self, '_original_html_root'):
                    try:
                        original_entries = self._original_html_root.xpath(f".//div[@role='ami_entry' and @term='{term}']")
                        if not original_entries:
                            original_entries = self._original_html_root.xpath(f".//div[@role='ami_entry' and @name='{term}']")
                        if original_entries:
                            orig_entry = original_entries[0]
                            wikipedia_url = (
                                orig_entry.get('wikipedia_url') or 
                                orig_entry.get('wikipediaURL') or
                                orig_entry.get('wikipedia-url') or
                                ''
                            )
                    except Exception:
                        pass
                
                # Priority 2: If no Wikipedia URL attribute, check for Wikipedia link in the search term paragraph
                if not wikipedia_url:
                    # Check for direct /wiki/ links
                    wiki_links_in_para = entry_element.xpath(".//p[contains(text(), 'search term:')]//a[contains(@href, 'en.wikipedia.org/wiki/')]")
                    if wiki_links_in_para:
                        href = wiki_links_in_para[0].get('href', '')
                        if href.startswith('http'):
                            wikipedia_url = href
                    # Also check for search URLs and convert them to canonical URLs
                    if not wikipedia_url:
                        search_links = entry_element.xpath(".//p[contains(text(), 'search term:')]//a[contains(@href, 'wikipedia.org/w/index.php?search=')]")
                        if search_links:
                            href = search_links[0].get('href', '')
                            # Extract search term from URL
                            if 'search=' in href:
                                from urllib.parse import parse_qs, urlparse
                                parsed = urlparse(href)
                                params = parse_qs(parsed.query)
                                search_term_from_url = params.get('search', [''])[0]
                                if search_term_from_url:
                                    # Convert search term to canonical Wikipedia URL
                                    page_title = search_term_from_url.replace(' ', '_')
                                    wikipedia_url = f"https://en.wikipedia.org/wiki/{page_title}"
                
                # Priority 3: Fall back to finding any /wiki/ directive link in the description
                if not wikipedia_url:
                    wiki_links = entry_element.xpath(".//a[contains(@href, '/wiki/')]")
                    if wiki_links:
                        href = wiki_links[0].get('href', '')
                        # Make it an absolute URL if it's relative
                        if href.startswith('/wiki/'):
                            wikipedia_url = f"https://en.wikipedia.org{href}"
                        elif href.startswith('http'):
                            wikipedia_url = href
                
                # Priority 2 for Wikidata ID: If no attribute, try to extract from Wikipedia page
                # Skip lookup if Wikidata ID already exists (avoid unnecessary network calls)
                if not wikidata_id and wikipedia_url:
                    wikidata_id = self._extract_wikidata_id_from_wikipedia_url(wikipedia_url)
                
                # Priority 3 for Wikidata ID: If still no Wikidata ID, try direct lookup from term
                # Skip lookup if Wikidata ID already exists
                if not wikidata_id and term:
                    wikidata_id = self._lookup_wikidata_id_by_term(term)
                
                # Validate Wikidata ID format
                if wikidata_id:
                    if not re.match(r'^[QP]\d+$', wikidata_id):
                        logger = Util.get_logger(__name__)
                        logger.warning(f"Invalid Wikidata ID format: {wikidata_id} (must be Q or P followed by digits)")
                        wikidata_id = ''  # Treat as missing
                
                # Extract description_html from <p class="wpage_first_para">
                description_html = ''
                desc_p = entry_element.xpath(".//p[@class='wpage_first_para']")
                if desc_p:
                    from amilib.xml_lib import XmlLib
                    description_html = XmlLib.element_to_string(desc_p[0])
                
                # Get Wikidata category (label/title) if we have a Wikidata ID
                wikidata_category = ''
                if wikidata_id and wikidata_id not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                    if re.match(r'^[QP]\d+$', wikidata_id):
                        wikidata_category = self._get_wikidata_category(wikidata_id)
                
                entry_dict = {
                    'term': term,
                    'search_term': search_term,
                    'wikidata_id': wikidata_id,  # PRIMARY identifier
                    'wikipedia_url': wikipedia_url,  # Secondary (for display)
                    'description_html': description_html,
                    'classification': self.CLASSIFICATION_UNPROCESSED,  # Initial classification
                    'wikidata_category': wikidata_category,  # Wikidata label/title
                }
                self.entries.append(entry_dict)
        finally:
            # Clean up temp file
            if temp_path.exists():
                os.unlink(temp_path)
        
        return self
    
    def _extract_entry_from_div(self, entry_div) -> Optional[Dict]:
        """Extract entry data from HTML div element"""
        raise NotImplementedError("AmiEncyclopedia._extract_entry_from_div not yet implemented")
    
    def _extract_description_links(self, desc_element) -> List[Dict]:
        """Extract all links from description element"""
        raise NotImplementedError("AmiEncyclopedia._extract_description_links not yet implemented")
    
    def _classify_link_type(self, href: str) -> str:
        """Classify link type based on href pattern"""
        raise NotImplementedError("AmiEncyclopedia._classify_link_type not yet implemented")
    
    def normalize_by_wikidata_id(self) -> Dict[str, List[Dict]]:
        """Normalize entries by grouping by Wikidata ID"""
        wikidata_groups = defaultdict(list)
        
        for entry in self.entries:
            wikidata_id = entry.get('wikidata_id', '')
            if wikidata_id:
                # Validate Wikidata ID format (Q or P followed by digits)
                if re.match(r'^[QP]\d+$', wikidata_id):
                    wikidata_groups[wikidata_id].append(entry)
                else:
                    logger = Util.get_logger(__name__)
                    logger.warning(f"Invalid Wikidata ID format: {wikidata_id}")
                    wikidata_groups['invalid_wikidata_id'].append(entry)
            else:
                # Entries without Wikidata IDs cannot be grouped
                wikidata_groups['no_wikidata_id'].append(entry)
        
        self.normalized_entries = dict(wikidata_groups)
        return self.normalized_entries
    
    def normalize_by_wikipedia_url(self) -> Dict[str, List[Dict]]:
        """Normalize entries by grouping by Wikipedia URL (DEPRECATED - use normalize_by_wikidata_id)"""
        # For backward compatibility, delegate to Wikidata ID normalization
        # This assumes entries have Wikidata IDs derived from Wikipedia URLs
        return self.normalize_by_wikidata_id()
    
    def _normalize_wikipedia_url(self, url: str) -> str:
        """Normalize Wikipedia URL to canonical format - preserve case"""
        if not url:
            return url
        
        parsed = urlparse(url)
        if parsed.netloc == 'en.wikipedia.org':
            if parsed.path.startswith('/wiki/'):
                # Remove fragment and normalize
                normalized_path = parsed.path
                # DO NOT convert to lowercase - Wikipedia URLs are case-sensitive
                return f"https://en.wikipedia.org{normalized_path}"
        
        return url
    
    def aggregate_synonyms(self) -> Dict[str, Dict]:
        """Aggregate synonyms by Wikidata ID and normalize terms"""
        # Ensure entries are normalized first
        if not self.normalized_entries:
            self.normalize_by_wikidata_id()
        
        synonym_groups = {}
        
        for wikidata_id, entries in self.normalized_entries.items():
            if wikidata_id in ('no_wikidata_id', 'invalid_wikidata_id'):
                continue
            
            # Extract all search terms
            search_terms = [entry.get('search_term', '') for entry in entries if entry.get('search_term')]
            
            # Normalize terms (using helper method)
            normalized_terms = self._normalize_terms(search_terms)
            
            # Get canonical term (using helper method)
            canonical_term = self._get_canonical_term(normalized_terms)
            
            # Get Wikipedia URL from first entry (for display)
            wikipedia_url = entries[0].get('wikipedia_url', '') if entries else ''
            
            # Get page title from Wikipedia URL (if available)
            page_title = self._extract_page_title_from_url(wikipedia_url) if wikipedia_url else canonical_term
            
            # Use the best available description (using helper method)
            best_description = self._get_best_description(entries)
            
            # Get figure from first entry that has one
            figure_html = None
            for entry in entries:
                if entry.get('figure_html'):
                    figure_html = entry.get('figure_html')
                    break
            
            synonym_groups[wikidata_id] = {
                'wikidata_id': wikidata_id,  # PRIMARY identifier
                'canonical_term': canonical_term,
                'page_title': page_title,
                'wikipedia_url': wikipedia_url,  # Secondary (for display)
                'search_terms': search_terms,
                'synonyms': list(set(normalized_terms)),
                'description_html': best_description,
                'figure_html': figure_html,
                'entry_count': len(entries),
                'source_entries': entries
            }
        
        # Store for later use
        self.synonym_groups = synonym_groups
        return synonym_groups
    
    def _merge_synonymous_entries(self) -> List[Dict]:
        """Merge synonymous entries with identical Wikidata IDs
        
        Returns:
            List of merged entry dictionaries, each containing:
            - wikidata_id: Wikidata ID (primary identifier)
            - canonical_term: Primary term for the merged entry
            - synonyms: List of all synonym terms
            - wikipedia_url: Wikipedia URL
            - description_html: Best description from merged entries
            - figure_html: Figure from first entry that has one
            - And other merged entry data
        """
        # Normalize entries by Wikidata ID
        if not self.normalized_entries:
            self.normalize_by_wikidata_id()
        
        merged_entries = []
        
        # Process entries with Wikidata IDs (can be merged)
        for wikidata_id, entries in self.normalized_entries.items():
            if wikidata_id in ('no_wikidata_id', 'invalid_wikidata_id'):
                # Process entries without Wikidata IDs separately (cannot be merged)
                for entry in entries:
                    # Get Wikidata category if available
                    wikidata_category = entry.get('wikidata_category', '')
                    
                    merged_entries.append({
                        'wikidata_id': '',
                        'canonical_term': entry.get('term', entry.get('search_term', '')),
                        'synonyms': [entry.get('term', entry.get('search_term', ''))],
                        'wikipedia_url': entry.get('wikipedia_url', ''),
                        'page_title': entry.get('term', entry.get('search_term', '')),
                        'description_html': entry.get('description_html', ''),
                        'figure_html': entry.get('figure_html'),
                        'wikidata_category': wikidata_category,
                        'entry_count': 1,
                        'source_entries': [entry]
                    })
            else:
                # Merge entries with same Wikidata ID
                # Extract all search terms
                search_terms = [entry.get('search_term', '') for entry in entries if entry.get('search_term')]
                terms = [entry.get('term', '') for entry in entries if entry.get('term')]
                all_terms = list(set(search_terms + terms))
                
                # Normalize terms
                normalized_terms = self._normalize_terms(all_terms)
                
                # Get canonical term
                canonical_term = self._get_canonical_term(normalized_terms)
                
                # Get Wikipedia URL from first entry
                wikipedia_url = entries[0].get('wikipedia_url', '') if entries else ''
                
                # Get page title from Wikipedia URL
                page_title = self._extract_page_title_from_url(wikipedia_url) if wikipedia_url else canonical_term
                
                # Get best description
                best_description = self._get_best_description(entries)
                
                # Get figure from first entry that has one
                figure_html = None
                for entry in entries:
                    if entry.get('figure_html'):
                        figure_html = entry.get('figure_html')
                        break
                
                # Get Wikidata category from first entry that has one, or look it up
                wikidata_category = ''
                for entry in entries:
                    if entry.get('wikidata_category'):
                        wikidata_category = entry.get('wikidata_category')
                        break
                
                # If no category found but we have a Wikidata ID, look it up
                if not wikidata_category and wikidata_id:
                    wikidata_category = self._get_wikidata_category(wikidata_id)
                
                merged_entries.append({
                    'wikidata_id': wikidata_id,
                    'canonical_term': canonical_term,
                    'synonyms': list(set(normalized_terms)),
                    'wikipedia_url': wikipedia_url,
                    'page_title': page_title,
                    'description_html': best_description,
                    'figure_html': figure_html,
                    'wikidata_category': wikidata_category,
                    'entry_count': len(entries),
                    'source_entries': entries
                })
        
        return merged_entries
    
    def _generate_entry_id_from_merged_entry(self, merged_entry: Dict, idx: int) -> str:
        """Generate entry ID for merged entry
        
        Args:
            merged_entry: Merged entry dictionary
            idx: Index of entry
            
        Returns:
            Entry ID string
        """
        wikidata_id = merged_entry.get('wikidata_id', '')
        if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
            return wikidata_id
        
        # Fallback to canonical term
        canonical_term = merged_entry.get('canonical_term', '')
        if canonical_term:
            return canonical_term.replace(' ', '_').replace('/', '_')
        
        return f"entry_{idx}"
    
    def _add_entry_checkboxes_for_merged_entry(self, entry_div, merged_entry: Dict, entry_id: str) -> None:
        """Add checkboxes to entry div for merged entry
        
        Args:
            entry_div: Entry div element
            merged_entry: Merged entry dictionary
            entry_id: Entry identifier
        """
        # Classify merged entry (check if it's a disambiguation page)
        category = self._classify_merged_entry(merged_entry)
        
        # Track if we add any checkboxes
        has_checkboxes = False
        checkbox_container = None
        
        # Add checkboxes based on category
        if category == self.CATEGORY_NO_WIKIPEDIA:
            # Missing Wikipedia checkbox
            checkbox_container = ET.SubElement(entry_div, "div")
            checkbox_container.attrib["class"] = "entry-checkboxes"
            checkbox_container.attrib["data-category"] = category
            self._add_hide_checkbox(
                checkbox_container,
                entry_id,
                reason=self.REASON_MISSING_WIKIPEDIA,
                checked=True,
                label="Hide (missing Wikipedia)"
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_DISAMBIGUATION:
            # Stage 2: Label disambiguation pages and offer content with checkboxes
            checkbox_container = ET.SubElement(entry_div, "div")
            checkbox_container.attrib["class"] = "entry-checkboxes"
            checkbox_container.attrib["data-category"] = category
            wikipedia_url = merged_entry.get('wikipedia_url', '')
            wikidata_id = merged_entry.get('wikidata_id', '')
            self._add_disambiguation_selector(
                checkbox_container,
                entry_id,
                wikipedia_url,
                wikidata_id
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_TRUE_WIKIPEDIA:
            # True Wikipedia entries - no checkboxes for now (will revisit later)
            pass
        
        # Merge synonyms checkbox (if has multiple synonyms)
        synonyms = merged_entry.get('synonyms', [])
        if len(synonyms) > 1:
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            wikidata_id = merged_entry.get('wikidata_id', '')
            self._add_merge_checkbox(
                checkbox_container,
                entry_id,
                wikidata_id if wikidata_id and wikidata_id.startswith('Q') else '',
                checked=True  # Checked by default (already merged)
            )
            has_checkboxes = True
        
        # Remove empty checkbox container
        if checkbox_container is not None and not has_checkboxes and len(checkbox_container) == 0:
            entry_div.remove(checkbox_container)
    
    def _classify_merged_entry(self, merged_entry: Dict) -> str:
        """Classify merged entry into category
        
        Args:
            merged_entry: Merged entry dictionary
            
        Returns:
            Category string (CATEGORY_NO_WIKIPEDIA, CATEGORY_DISAMBIGUATION, or CATEGORY_TRUE_WIKIPEDIA)
        """
        wikipedia_url = merged_entry.get('wikipedia_url', '')
        wikidata_id = merged_entry.get('wikidata_id', '')
        
        if not wikipedia_url:
            return self.CATEGORY_NO_WIKIPEDIA
        
        # Check if it's a disambiguation page (check Wikidata first, then Wikipedia URL)
        if self._is_disambiguation_page(wikipedia_url=wikipedia_url, wikidata_id=wikidata_id):
            return self.CATEGORY_DISAMBIGUATION
        
        # Default to true_wikipedia (can be marked as false/too_general manually)
        return self.CATEGORY_TRUE_WIKIPEDIA
    
    def _is_disambiguation_page(self, wikipedia_url: str = None, wikidata_id: str = None) -> bool:
        """Check if entry is a disambiguation page by checking Wikidata
        
        First checks Wikidata for P31 (instance of) = Q4167410 (disambiguation page).
        Falls back to Wikipedia URL pattern check if Wikidata ID not available.
        
        Args:
            wikipedia_url: Wikipedia URL (optional, for fallback)
            wikidata_id: Wikidata ID (optional, preferred method)
            
        Returns:
            True if disambiguation page, False otherwise
        """
        # Priority 1: Check Wikidata for disambiguation label (most reliable)
        if wikidata_id and wikidata_id not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
            if re.match(r'^[QP]\d+$', wikidata_id):
                try:
                    from amilib.wikimedia import WikidataPage
                    wikidata_page = WikidataPage(wikidata_id)
                    if wikidata_page is not None and wikidata_page.root is not None:
                        # Check for P31 (instance of) = Q4167410 (disambiguation page)
                        # Use WikidataPage method to get Q items for property P31
                        p31_qitems = wikidata_page.get_qitems_for_property_id('P31')
                        if p31_qitems:
                            # Check if any of the P31 values is Q4167410 (disambiguation page)
                            for qitem in p31_qitems:
                                qitem_title = qitem.get('title', '')
                                if qitem_title == 'Q4167410':
                                    return True
                                # Also check href
                                qitem_href = qitem.get('href', '')
                                if '/wiki/Q4167410' in qitem_href:
                                    return True
                        
                        # Alternative: Check for "disambiguation page" text in property values
                        # Look for P31 property div and check its values
                        p31_divs = wikidata_page.root.xpath(".//div[@id='P31']")
                        if p31_divs:
                            p31_text = ET.tostring(p31_divs[0], method='text', encoding='unicode').lower()
                            if 'q4167410' in p31_text or 'disambiguation page' in p31_text:
                                return True
                except Exception as e:
                    logger.debug(f"Could not check Wikidata for disambiguation: {e}")
        
        # Priority 2: Check Wikipedia URL pattern (fallback)
        if wikipedia_url:
            if '(disambiguation)' in wikipedia_url.lower():
                return True
            
            # Also check by fetching the Wikipedia page
            try:
                from amilib.wikimedia import WikipediaPage
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
                if wikipedia_page and wikipedia_page.is_disambiguation_page():
                    return True
            except Exception:
                # If lookup fails, fall back to URL pattern check
                pass
        
        return False
    
    def merge(self) -> 'AmiEncyclopedia':
        """Merge entries with the same Wikidata ID into single entries"""
        # Ensure entries are normalized first
        if not self.normalized_entries:
            self.normalize_by_wikidata_id()
        
        # Merge operation: aggregate synonyms if not already done
        if not self.synonym_groups:
            self.aggregate_synonyms()
        
        # The merge operation is essentially already done by aggregate_synonyms()
        # This method ensures the merge state is consistent
        return self
    
    def _normalize_terms(self, terms: List[str]) -> List[str]:
        """Normalize terms - only handle underscores and URL escaping"""
        normalized = []
        
        for term in terms:
            if not term:
                continue
            
            # Only normalize URL-related formatting
            normalized_term = term.strip()
            
            # If term contains a Wikipedia URL, extract the canonical page title
            if '/wiki/' in normalized_term:
                title_part = normalized_term.split('/wiki/')[-1]
                # Remove URL fragments and query parameters
                title_part = title_part.split('#')[0].split('?')[0]
                # Only decode URL encoding and replace underscores with spaces
                # Preserve Wikipedia's canonical case and pluralization
                normalized_term = unquote(title_part.replace('_', ' '))
            
            normalized.append(normalized_term)
        
        return list(set(normalized))
    
    def _get_canonical_term(self, terms: List[str]) -> str:
        """Get canonical term from list of normalized terms"""
        if not terms:
            return ""
        
        # Prefer terms that are not just lowercase versions
        original_terms = [t for t in terms if t != t.lower()]
        if original_terms:
            return original_terms[0]
        
        # Otherwise use the first term
        return terms[0]
    
    def _extract_page_title_from_url(self, url: str) -> str:
        """Extract page title from Wikipedia URL"""
        if '/wiki/' in url:
            title_part = url.split('/wiki/')[-1]
            title = unquote(title_part.replace('_', ' '))
            return title
        return ""
    
    def _get_best_description(self, entries: List[Dict]) -> str:
        """Get the best description from multiple entries"""
        if not entries:
            return ""
        
        # Prefer entries with longer descriptions
        best_entry = max(entries, key=lambda e: len(e.get('description_html', '')))
        return best_entry.get('description_html', '')
    
    def create_wiki_normalized_html(self) -> str:
        """Create wiki-normalized HTML encyclopedia (normalized by Wikipedia URL)"""
        # Use AmiDictionary pattern for HTML creation
        html_root = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html_root)
        head = HtmlLib.get_head(html_root)
        
        # Add CSS stylesheet for entry boxes and checkboxes
        style_elem = ET.SubElement(head, "style")
        style_elem.text = """
        /* Entry box styling */
        div[role="ami_entry"] {
            border: 2px solid #ccc;
            border-radius: 5px;
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
        }
        
        /* Disambiguation entry styling - different background color */
        div[role="ami_entry"][data-category="disambiguation"] {
            background-color: #fff3cd;
            border-color: #ffc107;
        }
        
        /* Wikidata category styling */
        .wikidata-category {
            font-weight: bold;
            color: #666;
            margin: 5px 0;
            font-size: 0.9em;
        }
        
        /* Entry checkboxes container */
        .entry-checkboxes {
            margin-bottom: 10px;
            padding: 5px;
            background-color: #f0f0f0;
            border-radius: 3px;
        }
        
        /* Checkbox wrapper */
        .entry-checkbox-wrapper {
            margin: 5px 0;
        }
        
        /* Disambiguation wrapper */
        .disambiguation-wrapper {
            margin: 5px 0;
            padding: 10px;
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 3px;
        }
        
        /* Disambiguation label */
        .disambiguation-label {
            font-weight: bold;
            margin-bottom: 8px;
            color: #856404;
        }
        
        /* Disambiguation checkbox wrapper */
        .disambiguation-checkbox-wrapper {
            margin: 5px 0;
            padding: 3px 0;
        }
        
        /* Disambiguation checkbox */
        .disambiguation-checkbox {
            margin-right: 5px;
        }
        
        /* Disambiguation checkbox label */
        .disambiguation-checkbox-wrapper label {
            cursor: pointer;
            display: inline-block;
        }
        
        /* Disambiguation checkbox label link */
        .disambiguation-checkbox-wrapper label a {
            color: #0066cc;
            text-decoration: none;
        }
        
        .disambiguation-checkbox-wrapper label a:hover {
            text-decoration: underline;
        }
        """
        
        # Create encyclopedia container (not dictionary)
        encyclopedia_div = ET.SubElement(body, "div")
        encyclopedia_div.attrib["role"] = "ami_encyclopedia"
        encyclopedia_div.attrib["title"] = self.title
        
        # Update last_edited timestamp before generating HTML
        self._update_last_edited()
        
        # Add metadata as JSON string in data-metadata attribute
        metadata_json = json.dumps(self.metadata, indent=2)
        encyclopedia_div.attrib["data-metadata"] = metadata_json
        
        # Stage 1: Merge synonymous entries with identical Wikidata IDs
        merged_entries = self._merge_synonymous_entries()
        
        # Process merged entries sequentially
        for idx, merged_entry in enumerate(merged_entries):
            entry_div = ET.SubElement(encyclopedia_div, "div")
            entry_div.attrib["role"] = "ami_entry"
            entry_div.attrib["class"] = "encyclopedia-entry"
            
            # Generate entry ID
            entry_id = self._generate_entry_id_from_merged_entry(merged_entry, idx)
            entry_div.attrib["data-entry-id"] = entry_id
            
            # Add canonical term (primary term for this merged entry)
            canonical_term = merged_entry.get('canonical_term', '')
            if canonical_term:
                entry_div.attrib["term"] = canonical_term
            
            # Add Wikidata ID (primary identifier for merged entries)
            wikidata_id = merged_entry.get('wikidata_id', '')
            if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
                entry_div.attrib["wikidataID"] = wikidata_id
            
            # Add Wikidata category if available
            wikidata_category = merged_entry.get('wikidata_category', '')
            if wikidata_category:
                category_elem = ET.SubElement(entry_div, "div")
                category_elem.attrib["class"] = "wikidata-category"
                category_elem.text = f"Category: {wikidata_category}"
            
            # Add category attribute for CSS styling (especially for disambiguation)
            category = self._classify_merged_entry(merged_entry)
            entry_div.attrib["data-category"] = category
            
            # Add checkboxes
            self._add_entry_checkboxes_for_merged_entry(entry_div, merged_entry, entry_id)
            
            # Add Wikipedia URL if available
            wikipedia_url = merged_entry.get('wikipedia_url', '')
            if wikipedia_url:
                wiki_link = ET.SubElement(entry_div, "a")
                wiki_link.attrib["href"] = wikipedia_url
                page_title = merged_entry.get('page_title', canonical_term)
                wiki_link.text = page_title if page_title else wikipedia_url
            
            # Add Wikidata link if available
            if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
                wikidata_link = ET.SubElement(entry_div, "a")
                wikidata_link.attrib["href"] = f"https://www.wikidata.org/wiki/{wikidata_id}"
                wikidata_link.text = f"Wikidata: {wikidata_id}"
            
            # Add synonym list if there are multiple synonyms
            synonyms = merged_entry.get('synonyms', [])
            if len(synonyms) > 1:
                synonym_ul = ET.SubElement(entry_div, "ul")
                synonym_ul.attrib["class"] = "synonym_list"
                for synonym in synonyms:
                    synonym_li = ET.SubElement(synonym_ul, "li")
                    synonym_li.text = synonym
            
            # Add description if available
            description_html = merged_entry.get('description_html', '')
            if description_html:
                from lxml.html import fromstring
                try:
                    desc_elem = fromstring(description_html)
                    # If the root element is a div, extract its children instead
                    if desc_elem.tag == 'div':
                        # Copy children to avoid nested div structure
                        for child in desc_elem:
                            entry_div.append(child)
                    else:
                        # For p, span, etc., append directly
                        entry_div.append(desc_elem)
                except Exception:
                    desc_p = ET.SubElement(entry_div, "p")
                    desc_p.text = description_html
            
            # Add figure if available
            figure_html = merged_entry.get('figure_html')
            if figure_html is not None:
                entry_div.append(figure_html)
        
        return XmlLib.element_to_string(html_root, pretty_print=True)
    
    def _create_wiki_normalized_entry_div(self, group: Dict):
        """Create wiki-normalized entry div for HTML output"""
        raise NotImplementedError("AmiEncyclopedia._create_wiki_normalized_entry_div not yet implemented")
    
    def save_wiki_normalized_html(self, output_file: Path) -> None:
        """Save wiki-normalized encyclopedia as HTML file"""
        html_content = self.create_wiki_normalized_html()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
    
    def get_statistics(self) -> Dict:
        """Get encyclopedia statistics"""
        # Ensure we have aggregated synonym groups
        if not self.synonym_groups:
            self.aggregate_synonyms()
        
        total_entries = len(self.entries)
        normalized_groups = len(self.synonym_groups)
        
        # Count total synonyms across all groups
        total_synonyms = sum(len(group.get('synonyms', [])) for group in self.synonym_groups.values())
        
        # Calculate compression ratio (entries to groups)
        compression_ratio = total_entries / normalized_groups if normalized_groups > 0 else 0.0
        
        return {
            'total_entries': total_entries,
            'normalized_groups': normalized_groups,
            'total_synonyms': total_synonyms,
            'compression_ratio': compression_ratio
        }
    
    def _generate_entry_id(self, group: Dict, wikidata_id: str) -> str:
        """Generate unique entry ID for checkbox data-entry-id attribute
        
        Args:
            group: Synonym group dictionary
            wikidata_id: Wikidata ID (may be 'no_wikidata_id' or 'invalid_wikidata_id')
            
        Returns:
            Unique entry identifier string
        """
        # Primary: Use Wikidata ID if valid
        if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
            return wikidata_id
        
        # Secondary: Use canonical term
        canonical_term = group.get('canonical_term', '')
        if canonical_term:
            # Sanitize term for use as ID
            safe_term = re.sub(r'[^a-zA-Z0-9_]', '_', canonical_term)
            return safe_term
        
        # Fallback: Use first search term
        search_terms = group.get('search_terms', [])
        if search_terms:
            safe_term = re.sub(r'[^a-zA-Z0-9_]', '_', search_terms[0])
            return safe_term
        
        # Last resort: Generate ID
        return f"entry_{hash(str(group)) % 10000}"
    
    def _generate_entry_id_from_entry(self, entry: Dict, index: int) -> str:
        """Generate entry ID from raw entry dictionary
        
        Args:
            entry: Raw entry dictionary
            index: Entry index for fallback
            
        Returns:
            Unique entry identifier string
        """
        # Primary: Use Wikidata ID if available
        wikidata_id = entry.get('wikidata_id', '')
        if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
            return wikidata_id
        
        # Secondary: Use term
        term = entry.get('term', '')
        if term:
            safe_term = re.sub(r'[^a-zA-Z0-9_]', '_', term)
            return safe_term
        
        # Fallback: Use search term
        search_term = entry.get('search_term', '')
        if search_term:
            safe_term = re.sub(r'[^a-zA-Z0-9_]', '_', search_term)
            return safe_term
        
        # Last resort: Generate ID
        return f"entry_{index}"
    
    def _has_wikipedia_url(self, group_or_entry: Dict) -> bool:
        """Check if group/entry has Wikipedia URL
        
        Args:
            group_or_entry: Synonym group or entry dictionary
            
        Returns:
            True if has Wikipedia URL, False otherwise
        """
        wikipedia_url = group_or_entry.get('wikipedia_url', '')
        return bool(wikipedia_url and wikipedia_url.strip())
    
    
    def _classify_entry(self, entry_or_group: Dict) -> str:
        """Classify entry into category based on Wikipedia status
        
        Categories:
        - true_wikipedia: Valid Wikipedia page found (not disambiguation)
        - no_wikipedia: No Wikipedia page found
        - false_wikipedia: Wikipedia page found but wrong (user marks manually)
        - too_general: Wikipedia page found but too general (user marks manually)
        - disambiguation: Disambiguation page found
        
        Args:
            entry_or_group: Entry dictionary or synonym group dictionary
            
        Returns:
            Category string
        """
        wikipedia_url = entry_or_group.get('wikipedia_url', '')
        has_wikipedia = bool(wikipedia_url)
        
        if not has_wikipedia:
            return self.CATEGORY_NO_WIKIPEDIA
        
        # Check for Wikidata ID to use for disambiguation detection
        wikidata_id = entry_or_group.get('wikidata_id', '')
        if self._is_disambiguation_page(wikipedia_url=wikipedia_url, wikidata_id=wikidata_id):
            return self.CATEGORY_DISAMBIGUATION
        
        # Default to true_wikipedia (can be marked as false/too_general manually)
        return self.CATEGORY_TRUE_WIKIPEDIA
    
    def classify_entry_status(self, entry: Dict) -> str:
        """Classify entry processing status to avoid expensive lookups
        
        This classification is stored in the entry and used to skip expensive operations.
        Categories:
        - UNPROCESSED: Entry hasn't been classified yet (default)
        - HAS_WIKIDATA: Entry has a valid Wikidata ID
        - NO_WIKIDATA_ENTRY: Wikipedia page exists but no Wikidata entry found
        - AMBIGUOUS: Points to disambiguation page
        - NO_WIKIPEDIA_PAGE: No Wikipedia page found
        - ERROR: Error occurred during processing
        
        Args:
            entry: Entry dictionary
            
        Returns:
            Classification string
        """
        # Check if already classified
        existing_classification = entry.get('classification')
        if existing_classification and existing_classification != self.CLASSIFICATION_UNPROCESSED:
            return existing_classification
        
        # Check for Wikidata ID first (fastest check)
        wikidata_id = entry.get('wikidata_id', '')
        if wikidata_id and wikidata_id not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
            if re.match(r'^[QP]\d+$', wikidata_id):
                return self.CLASSIFICATION_HAS_WIKIDATA
        
        # Check for Wikipedia URL
        wikipedia_url = entry.get('wikipedia_url', '')
        if not wikipedia_url:
            return self.CLASSIFICATION_NO_WIKIPEDIA_PAGE
        
        # Check if disambiguation page
        if self._is_disambiguation_page(wikipedia_url):
            return self.CLASSIFICATION_AMBIGUOUS
        
        # If we have Wikipedia URL but no Wikidata ID, it needs lookup
        # But we don't do the lookup here - just mark as needing it
        # The actual lookup will set the classification
        return self.CLASSIFICATION_UNPROCESSED
    
    def classify_all_entries(self) -> Dict[str, int]:
        """Classify all entries and store classification in entry dictionaries
        
        This avoids expensive lookups by storing the classification status.
        
        Returns:
            Statistics dictionary with classification counts
        """
        stats = {
            "total_entries": len(self.entries),
            "unprocessed": 0,
            "has_wikidata": 0,
            "no_wikidata_entry": 0,
            "ambiguous": 0,
            "no_wikipedia_page": 0,
            "error": 0
        }
        
        for entry in self.entries:
            classification = self.classify_entry_status(entry)
            entry['classification'] = classification
            
            # Update stats
            if classification == self.CLASSIFICATION_UNPROCESSED:
                stats["unprocessed"] += 1
            elif classification == self.CLASSIFICATION_HAS_WIKIDATA:
                stats["has_wikidata"] += 1
            elif classification == self.CLASSIFICATION_NO_WIKIDATA_ENTRY:
                stats["no_wikidata_entry"] += 1
            elif classification == self.CLASSIFICATION_AMBIGUOUS:
                stats["ambiguous"] += 1
            elif classification == self.CLASSIFICATION_NO_WIKIPEDIA_PAGE:
                stats["no_wikipedia_page"] += 1
            elif classification == self.CLASSIFICATION_ERROR:
                stats["error"] += 1
        
        logger.info(f"Classified {stats['total_entries']} entries: "
                   f"{stats['has_wikidata']} with Wikidata, "
                   f"{stats['unprocessed']} unprocessed, "
                   f"{stats['ambiguous']} ambiguous, "
                   f"{stats['no_wikipedia_page']} no Wikipedia page")
        
        return stats
    
    def _add_entry_checkboxes(self, entry_div, group: Dict, entry_id: str, wikidata_id: str = '') -> None:
        """Add checkboxes to entry div for synonym groups based on category
        
        Args:
            entry_div: Entry div element
            group: Synonym group dictionary
            entry_id: Entry identifier
            wikidata_id: Wikidata ID for merge checkbox
        """
        # Classify entry
        category = self._classify_entry(group)
        
        # Track if we add any checkboxes
        has_checkboxes = False
        
        # Create checkbox container div (only if we have checkboxes to add)
        checkbox_container = None
        
        # Add checkboxes based on category
        if category == self.CATEGORY_NO_WIKIPEDIA:
            # Missing Wikipedia checkbox (checked by default)
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            self._add_hide_checkbox(
                checkbox_container,
                entry_id,
                reason=self.REASON_MISSING_WIKIPEDIA,
                checked=True,
                label="Hide (missing Wikipedia)"
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_DISAMBIGUATION:
            # Disambiguation selector
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            wikipedia_url = group.get('wikipedia_url', '')
            self._add_disambiguation_selector(
                checkbox_container,
                entry_id,
                wikipedia_url,
                wikidata_id
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_TRUE_WIKIPEDIA:
            # True Wikipedia entries - no checkboxes for now (will revisit later)
            pass
        
        # Merge synonyms checkbox (if has multiple synonyms)
        synonyms = group.get('synonyms', [])
        if len(synonyms) > 1:
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            self._add_merge_checkbox(
                checkbox_container,
                entry_id,
                wikidata_id if wikidata_id and wikidata_id.startswith('Q') else '',
                checked=True  # Checked by default (automatic collapse)
            )
            has_checkboxes = True
        
        # Remove empty checkbox container to avoid nested divs
        if checkbox_container is not None and not has_checkboxes and len(checkbox_container) == 0:
            entry_div.remove(checkbox_container)
    
    def _add_entry_checkboxes_for_raw_entry(self, entry_div, entry: Dict, entry_id: str) -> None:
        """Add checkboxes to entry div for raw entries (no synonym groups) based on category
        
        Args:
            entry_div: Entry div element
            entry: Raw entry dictionary
            entry_id: Entry identifier
        """
        # Classify entry
        category = self._classify_entry(entry)
        
        # Track if we add any checkboxes
        has_checkboxes = False
        
        # Create checkbox container div (only if we have checkboxes to add)
        checkbox_container = None
        
        # Add checkboxes based on category
        if category == self.CATEGORY_NO_WIKIPEDIA:
            # Missing Wikipedia checkbox (checked by default)
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            self._add_hide_checkbox(
                checkbox_container,
                entry_id,
                reason=self.REASON_MISSING_WIKIPEDIA,
                checked=True,
                label="Hide (missing Wikipedia)"
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_DISAMBIGUATION:
            # Disambiguation selector
            if checkbox_container is None:
                checkbox_container = ET.SubElement(entry_div, "div")
                checkbox_container.attrib["class"] = "entry-checkboxes"
                checkbox_container.attrib["data-category"] = category
            wikipedia_url = entry.get('wikipedia_url', '')
            self._add_disambiguation_selector(
                checkbox_container,
                entry_id,
                wikipedia_url,
                ''
            )
            has_checkboxes = True
        
        elif category == self.CATEGORY_TRUE_WIKIPEDIA:
            # True Wikipedia entries - no checkboxes for now (will revisit later)
            pass
        
        # Remove empty checkbox container to avoid nested divs
        if checkbox_container is not None and not has_checkboxes and len(checkbox_container) == 0:
            entry_div.remove(checkbox_container)
    
    def _add_hide_checkbox(self, container, entry_id: str, reason: str, checked: bool, label: str) -> None:
        """Add hide checkbox to container
        
        Args:
            container: Parent element to add checkbox to
            entry_id: Entry identifier
            reason: Reason for hiding (missing_wikipedia, general_term, user_selected)
            checked: Whether checkbox should be checked by default
            label: Label text for checkbox
        """
        # Create wrapper div
        wrapper = ET.SubElement(container, "div")
        wrapper.attrib["class"] = "entry-checkbox-wrapper"
        
        # Create checkbox ID
        checkbox_id = f"hide_{entry_id}_{reason}".replace(' ', '_').replace('/', '_')
        
        # Create checkbox input
        checkbox = ET.SubElement(wrapper, "input")
        checkbox.attrib["type"] = "checkbox"
        checkbox.attrib["class"] = "entry-hide-checkbox"
        checkbox.attrib["data-entry-id"] = entry_id
        checkbox.attrib["data-reason"] = reason
        checkbox.attrib["id"] = checkbox_id
        
        if checked:
            checkbox.attrib["checked"] = "checked"
        
        # Create label
        label_elem = ET.SubElement(wrapper, "label")
        label_elem.attrib["for"] = checkbox_id
        label_elem.text = label
    
    def _add_merge_checkbox(self, container, entry_id: str, wikidata_id: str, checked: bool) -> None:
        """Add merge synonyms checkbox to container
        
        Args:
            container: Parent element to add checkbox to
            entry_id: Entry identifier
            wikidata_id: Wikidata ID for grouping
            checked: Whether checkbox should be checked by default
        """
        # Create wrapper div
        wrapper = ET.SubElement(container, "div")
        wrapper.attrib["class"] = "entry-checkbox-wrapper"
        
        # Create checkbox ID
        checkbox_id = f"merge_{entry_id}".replace(' ', '_').replace('/', '_')
        
        # Create checkbox input
        checkbox = ET.SubElement(wrapper, "input")
        checkbox.attrib["type"] = "checkbox"
        checkbox.attrib["class"] = "merge-synonyms-checkbox"
        checkbox.attrib["data-entry-id"] = entry_id
        if wikidata_id:
            checkbox.attrib["data-wikidata-id"] = wikidata_id
        checkbox.attrib["id"] = checkbox_id
        
        if checked:
            checkbox.attrib["checked"] = "checked"
        
        # Create label
        label_elem = ET.SubElement(wrapper, "label")
        label_elem.attrib["for"] = checkbox_id
        label_elem.text = "Merge synonyms"
    
    def _add_disambiguation_selector(self, container, entry_id: str, wikipedia_url: str, wikidata_id: str = '') -> None:
        """Add disambiguation selector with checkboxes for each link option
        
        Allows user to select one or more options from disambiguation page links.
        Each link is presented as a checkbox.
        
        Args:
            container: Parent element to add selector to
            entry_id: Entry identifier
            wikipedia_url: Original disambiguation page URL
            wikidata_id: Wikidata ID (optional, for future use)
        """
        # Create wrapper div
        wrapper = ET.SubElement(container, "div")
        wrapper.attrib["class"] = "disambiguation-wrapper"
        
        # Create label for the disambiguation section
        label_elem = ET.SubElement(wrapper, "div")
        label_elem.attrib["class"] = "disambiguation-label"
        label_elem.text = "Select Wikipedia page(s) from disambiguation:"
        
        # Try to fetch disambiguation options from Wikipedia page
        disambiguation_options = self._get_disambiguation_options(wikipedia_url)
        
        if disambiguation_options:
            # Create checkbox for each option
            import hashlib
            for option_url, option_title in disambiguation_options:
                checkbox_wrapper = ET.SubElement(wrapper, "div")
                checkbox_wrapper.attrib["class"] = "disambiguation-checkbox-wrapper"
                
                # Create checkbox ID - use a hash of the URL to make ID unique
                url_hash = hashlib.md5(option_url.encode()).hexdigest()[:8]
                checkbox_id = f"disambig_{entry_id}_{url_hash}".replace(' ', '_').replace('/', '_')
                
                # Create checkbox input
                checkbox = ET.SubElement(checkbox_wrapper, "input")
                checkbox.attrib["type"] = "checkbox"
                checkbox.attrib["class"] = "disambiguation-checkbox"
                checkbox.attrib["data-entry-id"] = entry_id
                checkbox.attrib["data-wikipedia-url"] = option_url
                checkbox.attrib["id"] = checkbox_id
                if wikidata_id:
                    checkbox.attrib["data-wikidata-id"] = wikidata_id
                
                # Create label for checkbox
                label = ET.SubElement(checkbox_wrapper, "label")
                label.attrib["for"] = checkbox_id
                
                # Add link in label
                link = ET.SubElement(label, "a")
                link.attrib["href"] = option_url
                link.attrib["target"] = "_blank"
                link.text = option_title
        else:
            # Fallback: Add original URL as checkbox option
            if wikipedia_url:
                checkbox_wrapper = ET.SubElement(wrapper, "div")
                checkbox_wrapper.attrib["class"] = "disambiguation-checkbox-wrapper"
                
                checkbox_id = f"disambig_{entry_id}_fallback".replace(' ', '_').replace('/', '_')
                
                checkbox = ET.SubElement(checkbox_wrapper, "input")
                checkbox.attrib["type"] = "checkbox"
                checkbox.attrib["class"] = "disambiguation-checkbox"
                checkbox.attrib["data-entry-id"] = entry_id
                checkbox.attrib["data-wikipedia-url"] = wikipedia_url
                checkbox.attrib["id"] = checkbox_id
                if wikidata_id:
                    checkbox.attrib["data-wikidata-id"] = wikidata_id
                
                label = ET.SubElement(checkbox_wrapper, "label")
                label.attrib["for"] = checkbox_id
                
                link = ET.SubElement(label, "a")
                link.attrib["href"] = wikipedia_url
                link.attrib["target"] = "_blank"
                page_title = wikipedia_url.split('/wiki/')[-1].replace('_', ' ') if '/wiki/' in wikipedia_url else wikipedia_url
                link.text = page_title
    
    def _get_disambiguation_options(self, wikipedia_url: str) -> list:
        """Get disambiguation options from Wikipedia page
        
        Args:
            wikipedia_url: Disambiguation page URL
            
        Returns:
            List of tuples (url, title) for disambiguation options, or empty list
        """
        if not wikipedia_url:
            return []
        
        try:
            from amilib.wikimedia import WikipediaPage
            
            # Lookup Wikipedia page
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
            if not wikipedia_page or not wikipedia_page.html_elem:
                return []
            
            # Check if it's actually a disambiguation page
            if not wikipedia_page.is_disambiguation_page():
                return []
            
            # Get disambiguation list
            disambig_list = wikipedia_page.get_disambiguation_list()
            if not disambig_list:
                return []
            
            # Extract options from list items
            options = []
            base_url = "https://en.wikipedia.org"
            
            for li in disambig_list:
                # Find links in the list item
                links = li.xpath(".//a[@href]")
                if links:
                    for link in links:
                        href = link.get('href', '')
                        if href:
                            # Convert relative URLs to absolute
                            if href.startswith('/wiki/'):
                                full_url = base_url + href
                            elif href.startswith('//'):
                                full_url = 'https:' + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            # Get link text (title)
                            title = link.text_content().strip() if hasattr(link, 'text_content') else (link.text or '').strip()
                            if not title:
                                # Fallback: extract from URL
                                if '/wiki/' in full_url:
                                    title = full_url.split('/wiki/')[-1].replace('_', ' ')
                            
                            if title and full_url:
                                options.append((full_url, title))
                                break  # Use first link in each list item
                else:
                    # No links, use text content as title
                    text = li.text_content().strip() if hasattr(li, 'text_content') else (li.text or '').strip()
                    if text:
                        # Try to construct URL from text
                        url_term = text.replace(' ', '_')
                        full_url = f"{base_url}/wiki/{url_term}"
                        options.append((full_url, text))
            
            return options[:20]  # Limit to first 20 options
            
        except Exception as e:
            logger.warning(f"Could not fetch disambiguation options for {wikipedia_url}: {e}")
            return []
    
    @staticmethod
    def _extract_qid_from_wikidata_url(wikidata_url: str) -> Optional[str]:
        """Extract Q/P ID from Wikidata EntityPage URL
        
        Examples:
            https://www.wikidata.org/wiki/Special:EntityPage/Q7942 -> Q7942
            https://www.wikidata.org/wiki/Special:EntityPage/Q125928#sitelinks -> Q125928
        
        Args:
            wikidata_url: Wikidata EntityPage URL
            
        Returns:
            Wikidata ID (Q/P format) or None
        """
        if not wikidata_url:
            return None
        
        # Pattern 1: EntityPage/Q123 or EntityPage/P123
        match = re.search(r'[Ee]ntity[Pp]age/([QP]\d+)', wikidata_url)
        if match:
            return match.group(1)
        
        # Pattern 2: /Q123 or /P123 at end of URL
        match = re.search(r'/([QP]\d+)(?:#|/|$)', wikidata_url)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_wikidata_id_from_wikipedia_url(self, wikipedia_url: str) -> Optional[str]:
        """Extract Wikidata ID from Wikipedia URL by looking up the Wikipedia page
        
        Args:
            wikipedia_url: Wikipedia page URL
            
        Returns:
            Wikidata ID (Q/P format) or None
        """
        if not wikipedia_url:
            return None
        
        try:
            # Extract page title from URL
            if '/wiki/' in wikipedia_url:
                page_title = wikipedia_url.split('/wiki/')[-1].split('#')[0].split('?')[0]
                page_title = unquote(page_title)  # Decode URL encoding
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(page_title)
                if wikipedia_page:
                    wikidata_url = wikipedia_page.get_wikidata_item()
                    if wikidata_url:
                        return self._extract_qid_from_wikidata_url(wikidata_url)
        except Exception as e:
            logger.warning(f"Could not extract Wikidata ID from Wikipedia URL {wikipedia_url}: {e}")
        
        return None
    
    def _get_wikidata_category(self, wikidata_id: str) -> str:
        """Get Wikidata category (label/title) from Wikidata ID
        
        This is typically the first string/label shown on the Wikidata page.
        Can be a controlled vocabulary property or user-provided string.
        
        Args:
            wikidata_id: Wikidata ID (Q/P format)
            
        Returns:
            Wikidata category/label string, or empty string if not found
        """
        if not wikidata_id or wikidata_id in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
            return ''
        
        if not re.match(r'^[QP]\d+$', wikidata_id):
            return ''
        
        try:
            from amilib.wikimedia import WikidataPage
            wikidata_page = WikidataPage(wikidata_id)
            if wikidata_page is not None and wikidata_page.root is not None:
                # Get title/label from Wikidata page (first string)
                title = wikidata_page.get_title()
                if title and title != "No title":
                    return title
        except Exception as e:
            logger.debug(f"Could not get Wikidata category for {wikidata_id}: {e}")
        
        return ''
    
    def _lookup_wikidata_id_by_term(self, term: str) -> Optional[str]:
        """Lookup Wikidata ID by term using Wikipedia lookup first, then direct Wikidata lookup
        
        Args:
            term: Search term
            
        Returns:
            Wikidata ID (Q/P format) or None
        """
        if not term:
            return None
        
        # Try Wikipedia lookup first (more reliable)
        try:
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
            if wikipedia_page:
                wikidata_url = wikipedia_page.get_wikidata_item()
                if wikidata_url:
                    qid = self._extract_qid_from_wikidata_url(wikidata_url)
                    if qid:
                        return qid
        except Exception as e:
            logger.debug(f"Wikipedia lookup failed for term '{term}': {e}")
        
        # Fallback to direct Wikidata lookup
        try:
            from amilib.wikimedia import WikidataLookup
            wikidata_lookup = WikidataLookup()
            qitem, desc, qitems = wikidata_lookup.lookup_wikidata(term)
            if qitem:
                return qitem
        except Exception as e:
            logger.warning(f"Could not lookup Wikidata ID for term '{term}': {e}")
        
        return None
    
    def _lookup_wikidata_ids_batch_sparql(self, terms: List[str]) -> Dict[str, Optional[str]]:
        """Lookup multiple Wikidata IDs using SPARQL batch query (faster than individual lookups)
        
        Note: SPARQL batch lookup is more efficient but may have rate limits.
        Falls back to individual lookups if SPARQL fails.
        
        Args:
            terms: List of search terms
            
        Returns:
            Dictionary mapping term -> Wikidata ID (or None if not found)
        """
        if not terms:
            return {}
        
        results = {}
        
        try:
            from amilib.wikimedia import WikidataSparql, NS_MAP, SPQ_RESULTS, SPQ_RESULT, SPQ_BINDING, SPQ_URI, NS_LITERAL
            from amilib.ami_html import HtmlUtil
            import lxml.etree as ET
            
            # Construct SPARQL query to search for multiple terms
            # Use VALUES clause for batch lookup (limit to 50 terms per query to avoid timeout)
            terms_subset = terms[:50]
            terms_list = '", "'.join([term.replace('"', '\\"').replace('\n', ' ') for term in terms_subset])
            
            # SPARQL query: find items with labels matching our terms
            sparql_query = f'''
            SELECT ?item ?itemLabel ?term WHERE {{
              VALUES ?term {{ "{terms_list}" }}
              ?item rdfs:label ?itemLabel .
              FILTER(LANG(?itemLabel) = "en")
              FILTER(LCASE(?itemLabel) = LCASE(?term))
            }}
            LIMIT 100
            '''
            
            sparql = WikidataSparql(None)  # Dictionary not needed for query-only
            xml_string = sparql.get_results_xml(sparql_query)
            
            # Parse SPARQL XML results
            # SPARQL XML format: <results><result><binding name="item"><uri>...</uri></binding>...</result></results>
            try:
                # Parse XML string
                root = ET.fromstring(xml_string.encode('utf-8'))
                
                # Find all result elements
                result_elements = root.findall(f".//{SPQ_RESULT}", NS_MAP)
                
                for result_elem in result_elements:
                    # Extract item (Wikidata ID) and itemLabel (term)
                    item_binding = result_elem.find(f".//{SPQ_BINDING}[@name='item']/{SPQ_URI}", NS_MAP)
                    label_binding = result_elem.find(f".//{SPQ_BINDING}[@name='itemLabel']", NS_MAP)
                    
                    if item_binding is not None and label_binding is not None:
                        # Extract QID from URI (e.g., http://www.wikidata.org/entity/Q7942 -> Q7942)
                        item_uri = item_binding.text
                        if item_uri:
                            qid = item_uri.split('/')[-1] if '/' in item_uri else item_uri
                            
                            # Extract label text (from literal element)
                            label_text = None
                            literal_elem = label_binding.find(f".//{NS_LITERAL}", NS_MAP)
                            if literal_elem is not None:
                                label_text = literal_elem.text
                            
                            if qid and label_text:
                                # Match label to original term (case-insensitive)
                                label_lower = label_text.lower().strip()
                                for term in terms_subset:
                                    if term.lower().strip() == label_lower:
                                        results[term] = qid
                                        break
                
                if results:
                    logger.info(f"SPARQL batch lookup found {len(results)}/{len(terms_subset)} Wikidata IDs")
                else:
                    logger.debug(f"SPARQL batch lookup found no matches for {len(terms_subset)} terms")
                    
            except Exception as parse_error:
                logger.warning(f"Failed to parse SPARQL results: {parse_error}")
            
        except Exception as e:
            logger.debug(f"SPARQL batch lookup failed (will use individual lookups): {e}")
        
        return results
    
    def ensure_all_entries_have_wikidata_ids(self, batch_size: int = 100, save_file: Optional[Path] = None) -> Dict[str, int]:
        """Ensure all entries have Wikidata IDs using staged lookup strategy
        
        Process entries in batches:
        1. Lookup next N missing IDs
        2. Add to entries
        3. Save dictionary if save_file provided
        4. Repeat until all entries have IDs or no more can be found
        
        Args:
            batch_size: Number of entries to process in each batch (default: 100)
            save_file: Optional file path to save after each batch
            
        Returns:
            Statistics dictionary with lookup results
        """
        stats = {
            "total_entries": len(self.entries),
            "entries_with_wikidata_id_before": 0,
            "entries_with_wikidata_id_after": 0,
            "added_from_wikipedia_url": 0,
            "added_from_wikipedia_term": 0,
            "added_from_wikidata_lookup": 0,
            "added_from_sparql_batch": 0,
            "entries_still_missing": 0,
            "batches_processed": 0
        }
        
        # Count entries with Wikidata IDs before
        for entry in self.entries:
            if entry.get('wikidata_id') and entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                stats["entries_with_wikidata_id_before"] += 1
        
        # Get entries missing Wikidata IDs
        missing_entries = [
            (idx, entry) for idx, entry in enumerate(self.entries)
            if not entry.get('wikidata_id') or entry.get('wikidata_id') in ('', 'no_wikidata_id', 'invalid_wikidata_id')
        ]
        
        if not missing_entries:
            logger.info("All entries already have Wikidata IDs")
            stats["entries_with_wikidata_id_after"] = stats["entries_with_wikidata_id_before"]
            return stats
        
        logger.info(f"Found {len(missing_entries)} entries missing Wikidata IDs. Processing in batches of {batch_size}...")
        
        # Process in batches
        for batch_start in range(0, len(missing_entries), batch_size):
            batch_end = min(batch_start + batch_size, len(missing_entries))
            batch = missing_entries[batch_start:batch_end]
            
            logger.info(f"Processing batch {stats['batches_processed'] + 1}: entries {batch_start + 1}-{batch_end} of {len(missing_entries)}")
            
            # Try SPARQL batch lookup first (faster for multiple terms)
            batch_terms = [entry[1].get('term', '') for entry in batch if entry[1].get('term')]
            if batch_terms:
                sparql_results = self._lookup_wikidata_ids_batch_sparql(batch_terms)
                # Apply SPARQL results
                for idx, entry in batch:
                    term = entry.get('term', '')
                    if term and term in sparql_results and sparql_results[term]:
                        entry['wikidata_id'] = sparql_results[term]
                        # Get Wikidata category for newly added ID
                        if entry['wikidata_id']:
                            entry['wikidata_category'] = self._get_wikidata_category(entry['wikidata_id'])
                        stats["added_from_sparql_batch"] += 1
            
            # Individual lookups for remaining entries in batch
            for idx, entry in batch:
                # Skip if already got ID from SPARQL
                if entry.get('wikidata_id') and entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                    continue
                
                term = entry.get('term', '')
                wikipedia_url = entry.get('wikipedia_url', '')
                
                # Try Wikipedia URL lookup first
                if wikipedia_url:
                    wikidata_id = self._extract_wikidata_id_from_wikipedia_url(wikipedia_url)
                    if wikidata_id:
                        entry['wikidata_id'] = wikidata_id
                        # Get Wikidata category for newly added ID
                        entry['wikidata_category'] = self._get_wikidata_category(wikidata_id)
                        stats["added_from_wikipedia_url"] += 1
                        continue
                
                # Try term-based lookup
                if term:
                    wikidata_id = self._lookup_wikidata_id_by_term(term)
                    if wikidata_id:
                        entry['wikidata_id'] = wikidata_id
                        # Get Wikidata category for newly added ID
                        entry['wikidata_category'] = self._get_wikidata_category(wikidata_id)
                        stats["added_from_wikipedia_term"] += 1
            
            stats["batches_processed"] += 1
            
            # Save after each batch if save_file provided
            if save_file:
                try:
                    self.save_wiki_normalized_html(save_file)
                    logger.info(f"Saved dictionary to {save_file} after batch {stats['batches_processed']}")
                except Exception as e:
                    logger.warning(f"Failed to save dictionary after batch: {e}")
        
        # Count entries with Wikidata IDs after
        for entry in self.entries:
            if entry.get('wikidata_id') and entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                stats["entries_with_wikidata_id_after"] += 1
        
        stats["entries_still_missing"] = stats["total_entries"] - stats["entries_with_wikidata_id_after"]
        
        logger.info(f"Lookup complete: {stats['entries_with_wikidata_id_after']}/{stats['total_entries']} entries now have Wikidata IDs")
        
        return stats
    
    def lookup_wikidata_ids_from_wikipedia_pages(self, max_ids: Optional[int] = None, output_file: Optional[Path] = None, delay_seconds: float = 0.1) -> Dict[str, int]:
        """Lookup Wikidata IDs from Wikipedia page URLs for entries that have Wikipedia pages
        
        Uses classification to avoid expensive lookups:
        - Skips entries classified as HAS_WIKIDATA (already have ID)
        - Skips entries classified as NO_WIKIPEDIA_PAGE (no Wikipedia URL)
        - Skips entries classified as AMBIGUOUS (disambiguation pages - handled separately)
        - Only processes UNPROCESSED entries
        
        For each entry:
        - If Wikidata ID already present, skip
        - If no Wikipedia page, skip
        - Lookup Wikidata ID from Wikipedia page using amilib routines
        - Add wikidata_id to entry and update classification (with try/catch to never fail)
        - Write edited encyclopedia if output_file provided
        
        Args:
            max_ids: Maximum number of IDs to lookup (None = no limit, for batch processing)
            output_file: Optional file path to write the edited encyclopedia
            delay_seconds: Delay between requests in seconds (default: 0.1) to avoid rate limiting
            
        Returns:
            Statistics dictionary with lookup results
        """
        import time
        
        stats = {
            "total_entries": len(self.entries),
            "entries_with_wikidata_id_before": 0,
            "entries_with_wikidata_id_after": 0,
            "entries_skipped_already_have_id": 0,
            "entries_skipped_no_wikipedia": 0,
            "entries_skipped_ambiguous": 0,
            "entries_skipped_classified": 0,
            "entries_looked_up": 0,
            "entries_successfully_found": 0,
            "entries_failed_lookup": 0
        }
        
        # Count entries with Wikidata IDs before
        for entry in self.entries:
            if entry.get('wikidata_id') and entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                stats["entries_with_wikidata_id_before"] += 1
        
        # Process entries that need lookup (use classification to skip expensive checks)
        entries_to_process = []
        for entry in self.entries:
            # Get classification (will classify if not already classified)
            classification = self.classify_entry_status(entry)
            entry['classification'] = classification  # Store it
            
            # Skip based on classification (avoids expensive lookups)
            if classification == self.CLASSIFICATION_HAS_WIKIDATA:
                stats["entries_skipped_already_have_id"] += 1
                stats["entries_skipped_classified"] += 1
                continue
            
            if classification == self.CLASSIFICATION_NO_WIKIPEDIA_PAGE:
                stats["entries_skipped_no_wikipedia"] += 1
                stats["entries_skipped_classified"] += 1
                continue
            
            if classification == self.CLASSIFICATION_AMBIGUOUS:
                stats["entries_skipped_ambiguous"] += 1
                stats["entries_skipped_classified"] += 1
                continue
            
            # Only process UNPROCESSED entries (have Wikipedia URL but no Wikidata ID yet)
            if classification == self.CLASSIFICATION_UNPROCESSED:
                entries_to_process.append(entry)
        
        # Apply max_ids limit if specified
        if max_ids is not None and max_ids > 0:
            entries_to_process = entries_to_process[:max_ids]
        
        total_to_process = len(entries_to_process)
        logger.info(f"Processing {total_to_process} entries for Wikidata ID lookup from Wikipedia pages")
        
        # Lookup Wikidata IDs for each entry
        for idx, entry in enumerate(entries_to_process, 1):
            wikipedia_url = entry.get('wikipedia_url', '')
            term = entry.get('term', 'N/A')
            
            stats["entries_looked_up"] += 1
            
            # Progress logging for long-running batches
            if total_to_process > 10 and idx % max(1, total_to_process // 10) == 0:
                progress_pct = (idx / total_to_process) * 100
                logger.info(f"Progress: {idx}/{total_to_process} ({progress_pct:.1f}%) - "
                          f"Found: {stats['entries_successfully_found']}, "
                          f"Failed: {stats['entries_failed_lookup']}")
            
            try:
                # Lookup Wikidata ID from Wikipedia page URL
                wikidata_id = self._extract_wikidata_id_from_wikipedia_url(wikipedia_url)
                
                if wikidata_id:
                    # Validate Wikidata ID format
                    if re.match(r'^[QP]\d+$', wikidata_id):
                        entry['wikidata_id'] = wikidata_id
                        entry['classification'] = self.CLASSIFICATION_HAS_WIKIDATA  # Update classification
                        # Get Wikidata category for newly found ID
                        entry['wikidata_category'] = self._get_wikidata_category(wikidata_id)
                        stats["entries_successfully_found"] += 1
                        logger.debug(f"Found Wikidata ID {wikidata_id} for '{term}' from {wikipedia_url}")
                    else:
                        logger.warning(f"Invalid Wikidata ID format for '{term}': {wikidata_id}")
                        entry['classification'] = self.CLASSIFICATION_ERROR  # Mark as error
                        stats["entries_failed_lookup"] += 1
                else:
                    # No Wikidata ID found - update classification
                    entry['classification'] = self.CLASSIFICATION_NO_WIKIDATA_ENTRY
                    stats["entries_failed_lookup"] += 1
                    logger.debug(f"Could not find Wikidata ID for '{term}' from {wikipedia_url}")
                    
            except Exception as e:
                # Never fail - catch all exceptions
                entry['classification'] = self.CLASSIFICATION_ERROR  # Mark as error
                stats["entries_failed_lookup"] += 1
                logger.warning(f"Error looking up Wikidata ID for '{term}' from {wikipedia_url}: {e}")
                # Continue processing other entries
            
            # Rate limiting: add delay between requests to avoid rate limiting
            if delay_seconds > 0 and idx < total_to_process:
                time.sleep(delay_seconds)
        
        # Count entries with Wikidata IDs after
        for entry in self.entries:
            if entry.get('wikidata_id') and entry.get('wikidata_id') not in ('', 'no_wikidata_id', 'invalid_wikidata_id'):
                stats["entries_with_wikidata_id_after"] += 1
        
        logger.info(f"Lookup complete: {stats['entries_successfully_found']}/{stats['entries_looked_up']} lookups successful "
                   f"({stats['entries_with_wikidata_id_after']}/{stats['total_entries']} total entries now have Wikidata IDs)")
        
        # Write edited encyclopedia if output_file provided
        if output_file:
            try:
                self.save_wiki_normalized_html(output_file)
                logger.info(f"Saved edited encyclopedia to {output_file}")
            except Exception as e:
                logger.warning(f"Failed to save edited encyclopedia to {output_file}: {e}")
                # Don't fail - just log the warning
        
        return stats
