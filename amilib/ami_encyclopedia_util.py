"""
AmiEncyclopedia utilities for link extraction and validation

Provides reusable components for encyclopedia analysis and processing
"""

import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from typing import Dict, List, Optional, Tuple
from collections import Counter

from amilib.ami_html import HtmlLib
from amilib.wikimedia import WikipediaPage
from amilib.xml_lib import XmlLib


class EncyclopediaLinkExtractor:
    """Extract and analyze links from encyclopedia HTML"""
    
    def __init__(self, base_url: str = "https://en.wikipedia.org/wiki/"):
        self.base_url = base_url
    
    def extract_entries_from_html(self, html_content: str) -> List[Dict]:
        """Extract all encyclopedia entries from HTML content"""
        html_root = HtmlLib.parse_html_string(html_content)
        dictionary_divs = html_root.xpath(".//div[@role='ami_dictionary']")
        
        if not dictionary_divs:
            raise ValueError("No dictionary container found")
        
        dictionary_div = dictionary_divs[0]
        entries = []
        
        entry_divs = dictionary_div.xpath(".//div[@role='ami_entry']")
        for entry_div in entry_divs:
            entry = self._extract_single_entry(entry_div)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _extract_single_entry(self, entry_div) -> Optional[Dict]:
        """Extract data from a single entry div"""
        try:
            term = entry_div.get('term', '')
            name = entry_div.get('name', '')
            wikipedia_url = entry_div.get('wikipedia_url', '')
            
            # Extract search term from paragraph
            search_term = term
            search_p = entry_div.xpath(".//p[contains(text(), 'search term:')]")
            if search_p:
                search_text = search_p[0].text or ''
                if 'search term:' in search_text:
                    search_term = search_text.split('search term:')[-1].strip()
            
            # Extract Wikipedia URL from link
            if not wikipedia_url:
                wiki_link = entry_div.xpath(".//a[contains(@href, 'wikipedia.org')]")
                if wiki_link:
                    wikipedia_url = wiki_link[0].get('href', '')
            
            # Extract description
            desc_p = entry_div.xpath(".//p[@class='wpage_first_para']")
            description_html = ""
            if desc_p:
                description_html = XmlLib.element_to_string(desc_p[0])
            
            # Extract links from description
            links = self._extract_description_links(desc_p[0] if desc_p else None)
            
            return {
                'term': term,
                'name': name,
                'search_term': search_term,
                'wikipedia_url': wikipedia_url,
                'description_html': description_html,
                'description_links': links,
                'element': entry_div
            }
        except Exception as e:
            print(f"Error extracting entry: {e}")
            return None
    
    def _extract_description_links(self, desc_element) -> List[Dict]:
        """Extract all links from description element"""
        links = []
        if not desc_element:
            return links
        
        link_elements = desc_element.xpath(".//a[@href]")
        for link_elem in link_elements:
            href = link_elem.get('href', '')
            text = link_elem.text or ''
            title = link_elem.get('title', '')
            
            # Skip citation links
            if href.startswith('#cite'):
                continue
            
            link_info = {
                'href': href,
                'text': text,
                'title': title,
                'type': self._classify_link_type(href)
            }
            links.append(link_info)
        
        return links
    
    def _classify_link_type(self, href: str) -> str:
        """Classify link type based on href pattern"""
        if href.startswith('/wiki/File:'):
            return 'file'
        elif href.startswith('/wiki/Help:'):
            return 'help'
        elif href.startswith('/wiki/'):
            return 'article'
        elif href.startswith('http'):
            return 'external'
        elif href.startswith('#'):
            return 'anchor'
        else:
            return 'unknown'
    
    def normalize_wikipedia_url(self, url: str) -> str:
        """Normalize Wikipedia URL to canonical format"""
        if not url:
            return url
        
        parsed = urlparse(url)
        if parsed.netloc == 'en.wikipedia.org':
            if parsed.path.startswith('/wiki/'):
                # Remove fragment and normalize
                normalized_path = parsed.path
                return f"https://en.wikipedia.org{normalized_path}"
        
        return url
    
    def extract_all_link_targets(self, entries: List[Dict]) -> Dict[str, List[str]]:
        """Extract all unique link targets from entries"""
        targets = {
            'search_urls': [],
            'article_links': [],
            'file_links': [],
            'help_links': [],
            'external_links': []
        }
        
        for entry in entries:
            # Search URLs
            if entry.get('wikipedia_url'):
                targets['search_urls'].append(entry['wikipedia_url'])
            
            # Description links
            for link in entry.get('description_links', []):
                link_type = link.get('type', 'unknown')
                href = link['href']
                
                if link_type == 'article':
                    targets['article_links'].append(href)
                elif link_type == 'file':
                    targets['file_links'].append(href)
                elif link_type == 'help':
                    targets['help_links'].append(href)
                elif link_type == 'external':
                    targets['external_links'].append(href)
        
        # Remove duplicates
        for key in targets:
            targets[key] = list(set(targets[key]))
        
        return targets
    
    def find_shared_article_links(self, entries: List[Dict], min_occurrences: int = 2) -> Dict:
        """Find article links that appear in multiple entries"""
        article_link_counter = Counter()
        link_to_entries = {}
        
        for entry in entries:
            entry_term = entry.get('term', '')
            for link in entry.get('description_links', []):
                if link.get('type') == 'article':
                    href = link.get('href', '')
                    # Normalize the link URL
                    normalized_href = self.normalize_wikipedia_url(
                        f"https://en.wikipedia.org{href}" if href.startswith('/wiki/') else href
                    )
                    
                    article_link_counter[normalized_href] += 1
                    
                    if normalized_href not in link_to_entries:
                        link_to_entries[normalized_href] = []
                    link_to_entries[normalized_href].append({
                        'term': entry_term,
                        'link_text': link.get('text', ''),
                        'title': link.get('title', '')
                    })
        
        # Find links that appear in multiple entries
        shared_links = {}
        for link_url, count in article_link_counter.items():
            if count >= min_occurrences:
                article_name = link_url.split('/wiki/')[-1] if '/wiki/' in link_url else link_url
                article_name = unquote(article_name.replace('_', ' '))
                
                shared_links[link_url] = {
                    'occurrence_count': count,
                    'entries': link_to_entries[link_url],
                    'article_name': article_name
                }
        
        return {
            'article_link_counts': dict(article_link_counter),
            'shared_article_links': shared_links,
            'total_shared_links': len(shared_links)
        }


class LinkValidator:
    """Validate extracted links and their targets"""
    
    def __init__(self):
        pass
    
    def validate_wikipedia_links(self, links: List[str]) -> Dict[str, Dict]:
        """Validate Wikipedia links using amilib WikipediaPage"""
        results = {}
        
        for link in links:
            try:
                if link.startswith('/wiki/'):
                    full_url = f"https://en.wikipedia.org{link}"
                else:
                    full_url = link
                
                # Use amilib WikipediaPage for validation
                wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(full_url)
                
                if wikipedia_page and wikipedia_page.html_elem is not None:
                    results[link] = {
                        'status_code': 200,
                        'final_url': wikipedia_page.url or full_url,
                        'accessible': True,
                        'page_title': self._extract_page_title(wikipedia_page)
                    }
                else:
                    results[link] = {
                        'status_code': 404,
                        'final_url': full_url,
                        'accessible': False
                    }
            except Exception as e:
                results[link] = {
                    'status_code': 0,
                    'final_url': link,
                    'accessible': False,
                    'error': str(e)
                }
        
        return results
    
    def _extract_page_title(self, wikipedia_page: WikipediaPage) -> str:
        """Extract page title from WikipediaPage"""
        if not wikipedia_page or not wikipedia_page.html_elem:
            return ""
        
        try:
            title_elements = wikipedia_page.html_elem.xpath(".//h1[@id='firstHeading']")
            if title_elements:
                return title_elements[0].text or ""
        except:
            pass
        
        return ""
    
    def check_link_consistency(self, search_url: str, canonical_url: str) -> bool:
        """Check if search URL resolves to expected canonical URL"""
        try:
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(search_url)
            if wikipedia_page and wikipedia_page.url:
                return wikipedia_page.url == canonical_url
        except:
            pass
        
        return False


class SynonymNormalizer:
    """Normalize terms for synonym detection"""
    
    def __init__(self):
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    def normalize_term(self, term: str) -> str:
        """Normalize a single term for comparison"""
        if not term:
            return ""
        
        # Basic normalization
        normalized = term.strip().lower()
        
        # Remove common suffixes
        normalized = re.sub(r'\s+(gas|gases)$', '', normalized)
        normalized = re.sub(r'\s+(effect|effects)$', '', normalized)
        normalized = re.sub(r'\s+(change|changes)$', '', normalized)
        
        # Handle plurals (basic)
        if normalized.endswith('s') and len(normalized) > 3:
            # Check if singular form exists
            singular = normalized[:-1]
            if len(singular) > 2:  # Avoid single letters
                return singular
        
        return normalized
    
    def are_synonyms(self, term1: str, term2: str) -> bool:
        """Check if two terms are synonyms"""
        norm1 = self.normalize_term(term1)
        norm2 = self.normalize_term(term2)
        
        if norm1 == norm2:
            return True
        
        # Check for common synonym patterns
        if self._is_plural_pair(norm1, norm2):
            return True
        
        if self._is_case_variant(term1, term2):
            return True
        
        return False
    
    def _is_plural_pair(self, term1: str, term2: str) -> bool:
        """Check if terms are singular/plural pairs"""
        if term1.endswith('s') and term1[:-1] == term2:
            return True
        if term2.endswith('s') and term2[:-1] == term1:
            return True
        return False
    
    def _is_case_variant(self, term1: str, term2: str) -> bool:
        """Check if terms differ only in case"""
        return term1.lower() == term2.lower() and term1 != term2
    
    def group_synonyms(self, terms: List[str]) -> List[List[str]]:
        """Group terms into synonym clusters"""
        groups = []
        used_terms = set()
        
        for term in terms:
            if term in used_terms:
                continue
            
            synonym_group = [term]
            used_terms.add(term)
            
            for other_term in terms:
                if other_term in used_terms:
                    continue
                
                if self.are_synonyms(term, other_term):
                    synonym_group.append(other_term)
                    used_terms.add(other_term)
            
            groups.append(synonym_group)
        
        return groups












