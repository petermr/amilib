"""
AmiEncyclopedia - Encyclopedia management with Wikipedia URL normalization

Provides functionality to:
- Extract entries from encyclopedia HTML
- Normalize entries by Wikipedia URL
- Aggregate synonyms by canonical Wikipedia pages
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
        self.synonym_groups = defaultdict(list)
        
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
                
                # Extract wikipedia_url with priority: attribute > explicit link > description links
                wikipedia_url = ''
                
                # Priority 1: Check if wikipedia_url is stored as an attribute on the entry element
                wikipedia_url = entry_element.get('wikipedia_url', '')
                
                # Priority 2: If no attribute, check for Wikipedia link in the search term paragraph
                if not wikipedia_url:
                    wiki_links_in_para = entry_element.xpath(".//p[contains(text(), 'search term:')]//a[contains(@href, 'en.wikipedia.org/wiki/')]")
                    if wiki_links_in_para:
                        href = wiki_links_in_para[0].get('href', '')
                        if href.startswith('http'):
                            wikipedia_url = href
                
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
                
                # Extract description_html from <p class="wpage_first_para">
                description_html = ''
                desc_p = entry_element.xpath(".//p[@class='wpage_first_para']")
                if desc_p:
                    from amilib.xml_lib import XmlLib
                    description_html = XmlLib.element_to_string(desc_p[0])
                
                entry_dict = {
                    'term': term,
                    'search_term': search_term,
                    'wikipedia_url': wikipedia_url,
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
    
    def normalize_by_wikipedia_url(self) -> Dict[str, List[Dict]]:
        """Normalize entries by grouping by Wikipedia URL"""
        url_groups = defaultdict(list)
        
        for entry in self.entries:
            wikipedia_url = entry.get('wikipedia_url', '')
            if wikipedia_url:
                # Normalize URL
                normalized_url = self._normalize_wikipedia_url(wikipedia_url)
                url_groups[normalized_url].append(entry)
            else:
                # Entries without Wikipedia URLs go to a special group
                url_groups['no_wikipedia_url'].append(entry)
        
        self.normalized_entries = dict(url_groups)
        return self.normalized_entries
    
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
        """Aggregate synonyms by Wikipedia URL and normalize terms"""
        # Ensure entries are normalized first
        if not self.normalized_entries:
            self.normalize_by_wikipedia_url()
        
        synonym_groups = {}
        
        for wikipedia_url, entries in self.normalized_entries.items():
            if wikipedia_url == 'no_wikipedia_url':
                continue
            
            # Extract all search terms
            search_terms = [entry.get('search_term', '') for entry in entries if entry.get('search_term')]
            
            # Normalize terms (using helper method)
            normalized_terms = self._normalize_terms(search_terms)
            
            # Get canonical term (using helper method)
            canonical_term = self._get_canonical_term(normalized_terms)
            
            # Get page title from URL (using helper method)
            page_title = self._extract_page_title_from_url(wikipedia_url)
            
            # Use the best available description (using helper method)
            best_description = self._get_best_description(entries)
            
            synonym_groups[wikipedia_url] = {
                'canonical_term': canonical_term,
                'page_title': page_title,
                'wikipedia_url': wikipedia_url,
                'search_terms': search_terms,
                'synonyms': list(set(normalized_terms)),
                'description_html': best_description,
                'entry_count': len(entries),
                'source_entries': entries
            }
        
        return synonym_groups
    
    def merge(self) -> 'AmiEncyclopedia':
        """Merge entries with the same Wikipedia URL into single entries"""
        raise NotImplementedError("AmiEncyclopedia.merge not yet implemented")
    
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
        
        # Add entry divs for each entry
        for entry in self.entries:
            entry_div = ET.SubElement(encyclopedia_div, "div")
            entry_div.attrib["role"] = "ami_entry"
            if entry.get('term'):
                entry_div.attrib["term"] = entry['term']
        
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
        raise NotImplementedError("AmiEncyclopedia.get_statistics not yet implemented")
