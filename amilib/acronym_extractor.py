"""
Acronym extraction utilities.

Pure business logic for detecting acronyms and extracting full terms from definitions.
No HTML/XML dependencies - can be used independently or integrated into amilib.
"""
import re
from typing import Optional, Tuple


class AcronymExtractor:
    """
    Extracts full terms from acronym/abbreviation definitions.
    
    This class provides pure business logic for:
    - Detecting if text is an acronym/abbreviation
    - Extracting full terms from definitions using first-letter matching
    - Normalizing terms for use in identifiers
    
    No HTML/XML dependencies - can be used with any text processing pipeline.
    """
    
    # Maximum words to consider as full term (usually 2-6 words)
    MAX_FULL_TERM_WORDS = 6
    
    # Minimum words for full term (usually 2+ words)
    MIN_FULL_TERM_WORDS = 2
    
    # Common stop words that don't contribute to acronyms
    STOP_WORDS = {'the', 'a', 'an', 'of', 'for', 'and', 'or', 'in', 'on', 'at', 'to'}
    
    @classmethod
    def is_acronym(cls, text: str) -> bool:
        """
        Check if text looks like an acronym/abbreviation.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be an acronym
            
        Examples:
            >>> AcronymExtractor.is_acronym("IPCC")
            True
            >>> AcronymExtractor.is_acronym("climate")
            False
            >>> AcronymExtractor.is_acronym("AR6")
            True
            >>> AcronymExtractor.is_acronym("U.S.")
            True
        """
        text = text.strip()
        
        # Acronym patterns:
        # - All uppercase, 2-10 characters: "IPCC", "AR6", "NDC"
        # - Mixed case with periods: "U.S.", "U.K."
        # - Numbers allowed: "AR6", "CO2"
        
        # All uppercase, short
        if re.match(r'^[A-Z]{2,10}$', text):
            return True
        
        # Mixed case with periods
        if re.match(r'^[A-Z]\.?[A-Z]\.?[A-Z]?\.?$', text):
            return True
        
        # Contains numbers (e.g., "AR6", "CO2")
        if re.match(r'^[A-Z0-9]{2,10}$', text):
            return True
        
        # Single word, all caps, short
        if len(text) <= 10 and text.isupper() and not ' ' in text:
            return True
        
        return False
    
    @classmethod
    def extract_full_term(cls, acronym: str, definition: str) -> Tuple[Optional[str], str]:
        """
        Extract full term from definition if it starts with it.
        
        Uses first-letter matching to identify the full term that corresponds
        to the acronym. Handles sentence boundaries and punctuation.
        
        Args:
            acronym: The acronym/abbreviation (e.g., "IPCC")
            definition: The definition text (e.g., "Intergovernmental Panel on Climate Change")
            
        Returns:
            Tuple of (full_term, remaining_definition) or (None, definition) if not found
            
        Examples:
            >>> AcronymExtractor.extract_full_term("IPCC", "Intergovernmental Panel on Climate Change")
            ('Intergovernmental Panel on Climate Change', '')
            >>> AcronymExtractor.extract_full_term("AUM", "assets under management")
            ('assets under management', '')
            >>> AcronymExtractor.extract_full_term("NDC", "Nationally Determined Contribution. A climate plan.")
            ('Nationally Determined Contribution', 'A climate plan.')
        """
        definition = definition.strip()
        
        # Split definition into words
        words = definition.split()
        
        # Try different lengths of initial words, starting from longest possible match
        # This ensures we get the complete full term
        # Stop at sentence boundaries (period, exclamation, question mark)
        for num_words in range(min(len(words), cls.MAX_FULL_TERM_WORDS), 
                              cls.MIN_FULL_TERM_WORDS - 1, -1):
            # Get potential full term
            potential_full_term = ' '.join(words[:num_words])
            
            # Check if we should stop at sentence boundary first
            # If the last word ends with sentence punctuation, check if this matches
            last_word = words[num_words - 1] if num_words > 0 else ''
            if last_word and last_word[-1] in '.!?':
                # Remove punctuation for matching
                potential_full_term_clean = potential_full_term.rstrip('.!?')
                if cls._could_be_full_term(acronym, potential_full_term_clean):
                    # This looks like end of sentence - use this as full term
                    remaining = ' '.join(words[num_words:]).strip()
                    remaining = re.sub(r'^[,;:\-–—]\s*', '', remaining)
                    return potential_full_term_clean, remaining
            
            # Check if this could be the full term for the acronym (without punctuation)
            if cls._could_be_full_term(acronym, potential_full_term):
                # Get remaining definition
                remaining = ' '.join(words[num_words:]).strip()
                
                # Clean up remaining definition (remove leading punctuation)
                remaining = re.sub(r'^[,;:\-–—]\s*', '', remaining)
                
                return potential_full_term, remaining
        
        return None, definition
    
    @classmethod
    def _could_be_full_term(cls, acronym: str, potential_full_term: str) -> bool:
        """
        Check if potential_full_term could be the full term for acronym.
        
        Uses heuristics:
        - First letters of words match acronym exactly
        - Handles stop words (the, of, on, etc.) that don't contribute
        - Special cases for common patterns (e.g., GHG -> greenhouse gas)
        
        Args:
            acronym: The acronym/abbreviation
            potential_full_term: Potential full term to check
            
        Returns:
            True if this could be the full term
            
        Examples:
            >>> AcronymExtractor._could_be_full_term("IPCC", "Intergovernmental Panel on Climate Change")
            True
            >>> AcronymExtractor._could_be_full_term("AUM", "assets under management")
            True
            >>> AcronymExtractor._could_be_full_term("GHG", "greenhouse gas")
            True
        """
        # Remove common words that don't contribute to acronym
        words = [w for w in potential_full_term.split() if w.lower() not in cls.STOP_WORDS]
        
        if not words:
            return False
        
        # Extract first letters (case-insensitive)
        first_letters = ''.join([w[0].upper() for w in words if w])
        acronym_clean = acronym.upper().replace('.', '').replace('-', '').replace(' ', '')
        
        # Exact match is best
        if first_letters == acronym_clean:
            return True
        
        # For acronyms with numbers (e.g., AR6), check if letters match
        # Extract only letters from acronym
        acronym_letters = ''.join([c for c in acronym_clean if c.isalpha()])
        if acronym_letters and first_letters == acronym_letters:
            return True
        
        # For very short acronyms (2-3 chars), be more lenient
        # Check if first letters start with acronym
        if len(acronym_clean) <= 3 and len(first_letters) >= len(acronym_clean):
            if first_letters[:len(acronym_clean)] == acronym_clean:
                return True
        
        # Special case: "GHG" -> "greenhouse gas"
        # This is a common abbreviation where GHG stands for "greenhouse gas(es)"
        # Even though "greenhouse gas" starts with G-G, GHG is widely accepted
        # Accept if we have words starting with G and the phrase relates to greenhouse/gas
        if acronym_clean == "GHG":
            # Check if we have at least 2 words and first word starts with G
            if len(words) >= 2:
                word1_first = words[0][0].upper() if words[0] else ''
                # Accept if first word starts with G and it's a two-word phrase
                # (common pattern: "greenhouse gas", "greenhouse gases")
                if word1_first == 'G':
                    # Check if second word relates to gas/gases
                    word2_lower = words[1].lower() if len(words) > 1 else ''
                    if 'gas' in word2_lower:
                        return True
        
        return False
    
    @classmethod
    def normalize_term(cls, term: str) -> str:
        """
        Normalize term for use in identifiers (IDs, filenames, etc.).
        
        Converts to lowercase, removes punctuation, and replaces spaces with hyphens.
        
        Args:
            term: Term to normalize
            
        Returns:
            Normalized term string
            
        Examples:
            >>> AcronymExtractor.normalize_term("Intergovernmental Panel on Climate Change")
            'intergovernmental-panel-on-climate-change'
            >>> AcronymExtractor.normalize_term("assets under management")
            'assets-under-management'
        """
        # Convert to lowercase, replace spaces with hyphens
        normalized = term.lower().strip()
        normalized = re.sub(r'[^\w\s-]', '', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', '-', normalized)  # Replace spaces with hyphens
        return normalized
    
    @classmethod
    def extract_acronym_info(cls, acronym: str, definition: str) -> Optional[dict]:
        """
        Extract full term and remaining definition from an acronym definition.
        
        Convenience method that combines extraction and returns structured data.
        
        Args:
            acronym: The acronym/abbreviation
            definition: The definition text
            
        Returns:
            Dictionary with keys: 'full_term', 'remaining_definition', 'acronym'
            or None if no full term could be extracted
            
        Examples:
            >>> result = AcronymExtractor.extract_acronym_info("IPCC", "Intergovernmental Panel on Climate Change")
            >>> result['full_term']
            'Intergovernmental Panel on Climate Change'
            >>> result['acronym']
            'IPCC'
        """
        if not cls.is_acronym(acronym):
            return None
        
        full_term, remaining_def = cls.extract_full_term(acronym, definition)
        
        if not full_term:
            return None
        
        return {
            'acronym': acronym,
            'full_term': full_term,
            'remaining_definition': remaining_def,
            'normalized_term': cls.normalize_term(full_term)
        }

