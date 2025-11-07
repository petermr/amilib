"""
AmiEncyclopedia - Encyclopedia management with Wikidata ID normalization

Provides functionality to:
- Extract entries from encyclopedia HTML
- Normalize entries by Wikidata ID
- Aggregate synonyms by Wikidata ID (canonical identifiers)
- Generate normalized encyclopedia output
"""

import re
import lxml.etree as ET
from pathlib import Path
from typing import Optional, Dict, List
from collections import defaultdict, Counter
from urllib.parse import urlparse, unquote

from amilib.ami_html import HtmlLib
from amilib.wikimedia import WikipediaPage
from amilib.ami_dict import AmiDictionary, AmiEntry
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.xml_lib import XmlLib


class AmiEncyclopedia:
    """Main encyclopedia class for managing entries and normalization"""
    
    def __init__(self, title: str = "Encyclopedia"):
        self.title = title
        self.dictionary = None  # AmiDictionary instance (composition)
        self.entries = []  # Processed entries as list of dicts
        self.normalized_entries = {}
        self.synonym_groups = {}  # Dict[str, Dict] - aggregated synonym groups by Wikidata ID
        
    def create_from_html_file(self, html_file: Path) -> 'AmiEncyclopedia':
        """Create encyclopedia from HTML file"""
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        html_content = html_file.read_text(encoding='utf-8')
        return self.create_from_html_content(html_content)
    
    def create_from_html_content(self, html_content: str, enable_auto_lookup: bool = False) -> 'AmiEncyclopedia':
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
                wikipedia_url = entry_element.get('wikipedia_url', '')
                
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
                # Only auto-lookup if explicitly enabled (disabled by default for performance)
                if not wikidata_id and wikipedia_url and enable_auto_lookup:
                    try:
                        # Extract page title from URL
                        if '/wiki/' in wikipedia_url:
                            page_title = wikipedia_url.split('/wiki/')[-1].split('#')[0].split('?')[0]
                            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(page_title)
                            if wikipedia_page:
                                wikidata_url = wikipedia_page.get_wikidata_item()
                                if wikidata_url:
                                    # Extract Q/P ID from URL
                                    match = re.search(r'[Ee]ntity[Pp]age/([QP]\d+)', wikidata_url)
                                    if not match:
                                        match = re.search(r'/([QP]\d+)(?:#|/|$)', wikidata_url)
                                    if match:
                                        wikidata_id = match.group(1)
                    except Exception as e:
                        logger = Util.get_logger(__name__)
                        logger.warning(f"Could not extract Wikidata ID from Wikipedia URL {wikipedia_url}: {e}")
                
                # Priority 3 for Wikidata ID: If still no Wikidata ID, try direct lookup from term
                # Only auto-lookup if explicitly enabled (disabled by default for performance)
                if not wikidata_id and term and enable_auto_lookup:
                    try:
                        from amilib.wikimedia import WikidataLookup
                        wikidata_lookup = WikidataLookup()
                        qitem, desc, qitems = wikidata_lookup.lookup_wikidata(term)
                        if qitem:
                            wikidata_id = qitem
                    except Exception as e:
                        logger = Util.get_logger(__name__)
                        logger.warning(f"Could not lookup Wikidata ID for term {term}: {e}")
                
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
                
                entry_dict = {
                    'term': term,
                    'search_term': search_term,
                    'wikidata_id': wikidata_id,  # PRIMARY identifier
                    'wikipedia_url': wikipedia_url,  # Secondary (for display)
                    'description_html': description_html,
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
        
        # Create encyclopedia container (not dictionary)
        encyclopedia_div = ET.SubElement(body, "div")
        encyclopedia_div.attrib["role"] = "ami_encyclopedia"
        encyclopedia_div.attrib["title"] = self.title
        
        # Get aggregated synonym groups if available
        if not self.synonym_groups or len(self.synonym_groups) == 0:
            synonym_groups = self.aggregate_synonyms()
        else:
            synonym_groups = self.synonym_groups
        
        # If no synonym groups were created (e.g., no Wikidata IDs), output raw entries
        if not synonym_groups or len(synonym_groups) == 0:
            # Output entries that couldn't be normalized
            for entry in self.entries:
                entry_div = ET.SubElement(encyclopedia_div, "div")
                entry_div.attrib["role"] = "ami_entry"
                
                # Add term
                term = entry.get('term', '')
                if term:
                    entry_div.attrib["term"] = term
                
                # Add search term
                search_term = entry.get('search_term', '')
                if search_term:
                    entry_div.attrib["name"] = search_term
                
                # Add Wikipedia URL if available
                wikipedia_url = entry.get('wikipedia_url', '')
                if wikipedia_url:
                    wiki_link = ET.SubElement(entry_div, "a")
                    wiki_link.attrib["href"] = wikipedia_url
                    wiki_link.text = search_term if search_term else term
                
                # Add Wikidata ID if available
                wikidata_id = entry.get('wikidata_id', '')
                if wikidata_id and wikidata_id not in ('no_wikidata_id', 'invalid_wikidata_id'):
                    entry_div.attrib["wikidataID"] = wikidata_id
                    wikidata_link = ET.SubElement(entry_div, "a")
                    wikidata_link.attrib["href"] = f"https://www.wikidata.org/wiki/{wikidata_id}"
                    wikidata_link.text = f"Wikidata: {wikidata_id}"
                
                # Add description if available
                description_html = entry.get('description_html', '')
                if description_html:
                    from lxml.html import fromstring
                    try:
                        desc_elem = fromstring(description_html)
                        entry_div.append(desc_elem)
                    except Exception:
                        desc_p = ET.SubElement(entry_div, "p")
                        desc_p.text = description_html
                
                # Add figure if available
                figure_html = entry.get('figure_html')
                if figure_html is not None:
                    entry_div.append(figure_html)
        else:
            # Add entry divs for each synonym group (normalized by Wikidata ID)
            for wikidata_id, group in synonym_groups.items():
                entry_div = ET.SubElement(encyclopedia_div, "div")
                entry_div.attrib["role"] = "ami_entry"
                
                # Add Wikidata ID as primary identifier
                entry_div.attrib["wikidataID"] = wikidata_id
                
                # Add canonical term
                canonical_term = group.get('canonical_term', '')
                if canonical_term:
                    entry_div.attrib["term"] = canonical_term
                
                # Add Wikipedia URL link (for display)
                wikipedia_url = group.get('wikipedia_url', '')
                if wikipedia_url:
                    wiki_link = ET.SubElement(entry_div, "a")
                    wiki_link.attrib["href"] = wikipedia_url
                    page_title = group.get('page_title', canonical_term)
                    wiki_link.text = page_title if page_title else wikipedia_url
                
                # Add Wikidata link
                wikidata_link = ET.SubElement(entry_div, "a")
                wikidata_link.attrib["href"] = f"https://www.wikidata.org/wiki/{wikidata_id}"
                wikidata_link.text = f"Wikidata: {wikidata_id}"
                
                # Add synonym list
                synonyms = group.get('synonyms', [])
                if synonyms:
                    synonym_ul = ET.SubElement(entry_div, "ul")
                    synonym_ul.attrib["class"] = "synonym_list"
                    for synonym in synonyms:
                        synonym_li = ET.SubElement(synonym_ul, "li")
                        synonym_li.text = synonym
                
                # Add description if available
                description_html = group.get('description_html', '')
                if description_html:
                    # Parse description HTML and append to entry
                    from lxml.html import fromstring
                    try:
                        desc_elem = fromstring(description_html)
                        entry_div.append(desc_elem)
                    except Exception:
                        # If parsing fails, add as text
                        desc_p = ET.SubElement(entry_div, "p")
                        desc_p.text = description_html
                
                # Add figure if available (from first entry in group)
                figure_html = group.get('figure_html')
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
