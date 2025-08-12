"""
Wikidata Service Module

This module provides clean, simple interfaces for Wikidata operations
using the existing amilib wikimedia functionality.

Author: Dictionary Editor Team
Date: January 27, 2025
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from urllib.error import HTTPError, URLError

from amilib.wikimedia import WikidataLookup, WikidataExtractor, WikidataPage
from amilib.util import Util

logger = Util.get_logger(__name__)


class WikidataService:
    """
    Service class for Wikidata operations.
    
    Provides clean interfaces for common Wikidata tasks like:
    - Searching for entities
    - Getting entity properties
    - Retrieving descriptions and aliases
    - Getting Wikipedia page links
    """
    
    def __init__(self, language: str = 'en'):
        """
        Initialize the Wikidata service.
        
        Args:
            language: Language code for Wikidata operations (default: 'en')
        """
        self.language = language
        self.wikidata_lookup = WikidataLookup()
        self.wikidata_extractor = WikidataExtractor(lang=language)
        self._cache = {}
        
    def search_entity(self, term: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for Wikidata entities by term.
        
        Args:
            term: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of entity dictionaries with id, description, and match info
        """
        try:
            logger.info(f"Searching Wikidata for term: {term}")
            
            # Use WikidataExtractor for API-based search
            entity_id = self.wikidata_extractor.search(term)
            
            if entity_id:
                # Get full entity data
                entity_data = self.wikidata_extractor.load(entity_id)
                if entity_data:
                    return [{
                        'id': entity_id,
                        'description': entity_data.get('descriptions', {}).get(self.language, ''),
                        'label': entity_data.get('labels', {}).get(self.language, ''),
                        'match_type': 'exact',
                        'confidence': 1.0
                    }]
            
            # Fallback to WikidataLookup for HTML-based search
            qitem, desc, qitems = self.wikidata_lookup.lookup_wikidata(term)
            
            results = []
            if qitem:
                results.append({
                    'id': qitem,
                    'description': desc or '',
                    'label': term,
                    'match_type': 'primary',
                    'confidence': 0.9
                })
            
            # Add additional results
            for qid in qitems[:max_results - len(results)]:
                if qid != qitem:
                    results.append({
                        'id': qid,
                        'description': '',
                        'label': term,
                        'match_type': 'secondary',
                        'confidence': 0.7
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Wikidata for term '{term}': {e}")
            return []
    
    def get_entity_properties(self, qid: str) -> Dict[str, Any]:
        """
        Get properties and values for a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID (e.g., 'Q12345')
            
        Returns:
            Dictionary containing entity properties and values
        """
        try:
            logger.info(f"Getting properties for Wikidata entity: {qid}")
            
            # Use WikidataExtractor for API-based property retrieval
            entity_data = self.wikidata_extractor.load(qid)
            
            if not entity_data:
                return {}
            
            properties = {}
            
            # Extract claims (statements)
            if 'claims' in entity_data:
                for prop_id, claims in entity_data['claims'].items():
                    if isinstance(claims, list) and claims:
                        # Get property label
                        prop_label = self._get_property_label(prop_id)
                        
                        # Extract values
                        values = []
                        for claim in claims:
                            if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                                datavalue = claim['mainsnak']['datavalue']
                                if 'value' in datavalue:
                                    value = datavalue['value']
                                    if isinstance(value, dict):
                                        if 'id' in value:
                                            # Entity reference
                                            values.append({
                                                'type': 'entity',
                                                'id': value['id'],
                                                'value': value.get('id', '')
                                            })
                                        elif 'amount' in value:
                                            # Quantity
                                            values.append({
                                                'type': 'quantity',
                                                'value': value.get('amount', ''),
                                                'unit': value.get('unit', '')
                                            })
                                        else:
                                            # String or other
                                            values.append({
                                                'type': 'string',
                                                'value': str(value)
                                            })
                        
                        if values:
                            properties[prop_label or prop_id] = values
            
            return properties
            
        except Exception as e:
            logger.error(f"Error getting properties for entity '{qid}': {e}")
            return {}
    
    def get_entity_description(self, qid: str) -> Optional[str]:
        """
        Get the description of a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID
            
        Returns:
            Entity description or None if not found
            
        Raises:
            Exception: If no definition/description found for the entity
        """
        try:
            logger.info(f"Getting description for Wikidata entity: {qid}")
            
            # Try WikidataExtractor first
            entity_data = self.wikidata_extractor.load(qid)
            if entity_data and 'descriptions' in entity_data:
                description = entity_data['descriptions'].get(self.language, '')
                if description:
                    return description
            
            # Fallback to WikidataPage
            wikidata_page = WikidataPage(pqitem=qid)
            if wikidata_page.root is not None:
                # Try to extract description from page content
                desc_elem = wikidata_page.root.find(".//div[@class='wikibase-entityview-description']")
                if desc_elem is not None:
                    return desc_elem.text.strip()
                
                # Try alternative description extraction methods
                description = wikidata_page.get_description()
                if description:
                    return description
            
            # No description found - raise exception
            raise Exception(f"No definition/description found for Wikidata entity: {qid}")
            
        except Exception as e:
            logger.error(f"Error getting description for entity '{qid}': {e}")
            raise
    
    def get_entity_label(self, qid: str) -> Optional[str]:
        """
        Get the label of a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID
            
        Returns:
            Entity label or None if not found
        """
        try:
            logger.info(f"Getting label for Wikidata entity: {qid}")
            
            # Try WikidataExtractor first
            entity_data = self.wikidata_extractor.load(qid)
            if entity_data and 'labels' in entity_data:
                label = entity_data['labels'].get(self.language, '')
                if label:
                    return label
            
            # Fallback to WikidataPage
            wikidata_page = WikidataPage(pqitem=qid)
            if wikidata_page.root is not None:
                # Try to extract label from page content
                label_elem = wikidata_page.root.find(".//div[@class='wikibase-title-label']")
                if label_elem is not None:
                    return label_elem.text.strip()
                
                # Try alternative label extraction methods
                label = wikidata_page.get_title()
                if label and label != "No title":
                    return label
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting label for entity '{qid}': {e}")
            return None
    
    def get_entity_aliases(self, qid: str) -> List[str]:
        """
        Get aliases (alternative names) for a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID
            
        Returns:
            List of aliases
        """
        try:
            logger.info(f"Getting aliases for Wikidata entity: {qid}")
            
            # Use WikidataExtractor
            entity_data = self.wikidata_extractor.load(qid)
            
            if entity_data and 'aliases' in entity_data:
                aliases = entity_data['aliases'].get(self.language, [])
                if isinstance(aliases, list):
                    result = [alias.get('value', '') for alias in aliases if isinstance(alias, dict)]
                    if result:
                        return result
            
            # Fallback to WikidataPage
            wikidata_page = WikidataPage(pqitem=qid)
            if wikidata_page.root is not None:
                try:
                    aliases = wikidata_page.get_aliases_from_wikidata_page()
                    if aliases is not None:
                        return aliases
                except:
                    pass
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting aliases for entity '{qid}': {e}")
            return []
    
    def get_wikipedia_links(self, qid: str, languages: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Get Wikipedia page links for a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID
            languages: List of language codes (default: ['en'])
            
        Returns:
            Dictionary mapping language codes to Wikipedia page titles
        """
        try:
            logger.info(f"Getting Wikipedia links for Wikidata entity: {qid}")
            
            if languages is None:
                languages = ['en']
            
            wikidata_page = WikidataPage(pqitem=qid)
            if wikidata_page.root is not None:
                return wikidata_page.get_wikipedia_page_links(languages)
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting Wikipedia links for entity '{qid}': {e}")
            return {}
    
    def is_wikipedia_disambiguation_page(self, qid: str, language: str = 'en') -> bool:
        """
        Check if a Wikipedia page is a disambiguation page using existing amilib logic.
        
        Args:
            qid: Wikidata entity ID
            language: Language code (default: 'en')
            
        Returns:
            True if the page is a disambiguation page, False otherwise
        """
        try:
            logger.info(f"Checking if Wikipedia page is disambiguation for entity: {qid}")
            
            # Get Wikipedia page links
            links = self.get_wikipedia_links(qid, [language])
            if not links or language not in links:
                return False
            
            # Import WikipediaPage here to avoid circular imports
            from amilib.wikimedia import WikipediaPage
            
            # Get the Wikipedia page URL
            wikipedia_url = links[language]
            if not wikipedia_url:
                return False
            
            # Create WikipediaPage object and check if it's a disambiguation page
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
            if wikipedia_page and wikipedia_page.html_elem is not None:
                return wikipedia_page.is_disambiguation_page()
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking disambiguation page for entity '{qid}': {e}")
            return False
    
    def get_disambiguation_options(self, qid: str, language: str = 'en') -> Optional[List[str]]:
        """
        Get disambiguation options if the Wikipedia page is a disambiguation page.
        
        Args:
            qid: Wikidata entity ID
            language: Language code (default: 'en')
            
        Returns:
            List of disambiguation options or None if not a disambiguation page
        """
        try:
            if not self.is_wikipedia_disambiguation_page(qid, language):
                return None
            
            # Get Wikipedia page links
            links = self.get_wikipedia_links(qid, [language])
            if not links or language not in links:
                return None
            
            # Import WikipediaPage here to avoid circular imports
            from amilib.wikimedia import WikipediaPage
            
            # Get the Wikipedia page URL
            wikipedia_url = links[language]
            if not wikipedia_url:
                return None
            
            # Create WikipediaPage object and get disambiguation list
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(wikipedia_url)
            if wikipedia_page and wikipedia_page.html_elem is not None:
                disambig_list = wikipedia_page.get_disambiguation_list()
                if disambig_list:
                    # Extract text from list items
                    options = []
                    for li in disambig_list:
                        text = li.text_content().strip() if hasattr(li, 'text_content') else li.text.strip()
                        if text:
                            options.append(text)
                    return options
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting disambiguation options for entity '{qid}': {e}")
            return None
    
    def get_entity_summary(self, qid: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a Wikidata entity.
        
        Args:
            qid: Wikidata entity ID
            
        Returns:
            Dictionary containing entity summary information
        """
        try:
            logger.info(f"Getting summary for Wikidata entity: {qid}")
            
            # Get basic entity data
            entity_data = self.wikidata_extractor.load(qid)
            
            if not entity_data:
                return {}
            
            # Get label and description using our improved methods
            label = self.get_entity_label(qid)
            description = self.get_entity_description(qid)
            
            # Extract key information
            summary = {
                'id': qid,
                'label': label or entity_data.get('labels', {}).get(self.language, ''),
                'description': description or entity_data.get('descriptions', {}).get(self.language, ''),
                'aliases': self.get_entity_aliases(qid),
                'properties': self.get_entity_properties(qid),
                'wikipedia_links': self.get_wikipedia_links(qid),
                'type': self._get_entity_type(qid, entity_data)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting summary for entity '{qid}': {e}")
            return {}
    
    def enrich_term(self, term: str) -> Dict[str, Any]:
        """
        Enrich a term with Wikidata information.
        
        Args:
            term: Term to enrich
            
        Returns:
            Dictionary containing enriched information
        """
        try:
            logger.info(f"Enriching term: {term}")
            
            # Search for entity
            entities = self.search_entity(term, max_results=1)
            
            if not entities:
                return {
                    'term': term,
                    'wikidata': None,
                    'enrichment_status': 'no_entity_found'
                }
            
            # Get primary entity
            primary_entity = entities[0]
            qid = primary_entity['id']
            
            # Get comprehensive data
            summary = self.get_entity_summary(qid)
            
            return {
                'term': term,
                'wikidata': {
                    'id': qid,
                    'description': primary_entity['description'],
                    'label': primary_entity['label'],
                    'confidence': primary_entity['confidence'],
                    'summary': summary
                },
                'enrichment_status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error enriching term '{term}': {e}")
            return {
                'term': term,
                'wikidata': None,
                'enrichment_status': f'error: {str(e)}'
            }
    
    def batch_enrich_terms(self, terms: List[str]) -> List[Dict[str, Any]]:
        """
        Enrich multiple terms in batch.
        
        Args:
            terms: List of terms to enrich
            
        Returns:
            List of enrichment results
        """
        results = []
        for term in terms:
            result = self.enrich_term(term)
            results.append(result)
        return results
    
    def validate_qid(self, qid: str) -> bool:
        """
        Validate if a string is a valid Wikidata QID.
        
        Args:
            qid: String to validate
            
        Returns:
            True if valid QID, False otherwise
        """
        if not qid:
            return False
        
        # QID format: Q followed by numbers
        import re
        qid_pattern = r'^Q\d+$'
        return bool(re.match(qid_pattern, qid))
    
    def _get_property_label(self, prop_id: str) -> Optional[str]:
        """
        Get the label for a Wikidata property.
        
        Args:
            prop_id: Property ID (e.g., 'P31')
            
        Returns:
            Property label or None if not found
        """
        try:
            # Try to get property label from Wikidata
            prop_data = self.wikidata_extractor.load(prop_id)
            if prop_data and 'labels' in prop_data:
                return prop_data['labels'].get(self.language, '')
        except:
            pass
        
        return None
    
    def _get_entity_type(self, qid: str, entity_data: Dict[str, Any]) -> Optional[str]:
        """
        Determine the type of a Wikidata entity.
        
        Args:
            qid: Entity ID
            entity_data: Entity data from Wikidata
            
        Returns:
            Entity type or None if not determined
        """
        try:
            # Look for instance of (P31) property
            if 'claims' in entity_data and 'P31' in entity_data['claims']:
                claims = entity_data['claims']['P31']
                if isinstance(claims, list) and claims:
                    claim = claims[0]
                    if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                        datavalue = claim['mainsnak']['datavalue']
                        if 'value' in datavalue and 'id' in datavalue['value']:
                            type_qid = datavalue['value']['id']
                            # Get label for the type
                            type_data = self.wikidata_extractor.load(type_qid)
                            if type_data and 'labels' in type_data:
                                return type_data['labels'].get(self.language, '')
        except:
            pass
        
        return None
    
    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
        logger.info("Wikidata service cache cleared")


# Convenience functions for backward compatibility
def search_wikidata_entity(term: str, language: str = 'en') -> List[Dict[str, Any]]:
    """
    Convenience function to search for Wikidata entities.
    
    Args:
        term: Search term
        language: Language code
        
    Returns:
        List of entity dictionaries
    """
    service = WikidataService(language)
    return service.search_entity(term)


def get_wikidata_entity_summary(qid: str, language: str = 'en') -> Dict[str, Any]:
    """
    Convenience function to get Wikidata entity summary.
    
    Args:
        qid: Wikidata entity ID
        language: Language code
        
    Returns:
        Entity summary dictionary
    """
    service = WikidataService(language)
    return service.get_entity_summary(qid)


def enrich_term_with_wikidata(term: str, language: str = 'en') -> Dict[str, Any]:
    """
    Convenience function to enrich a term with Wikidata data.
    
    Args:
        term: Term to enrich
        language: Language code
        
    Returns:
        Enrichment result dictionary
    """
    service = WikidataService(language)
    return service.enrich_term(term)
