#!/usr/bin/env python3
"""
Test script to extract terms and definitions from IPCC Glossary PDF.
Outputs a CSV file with: term|definition|address_of_entry
"""

import csv
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import fitz  # PyMuPDF


class IPCCGlossaryExtractor:
    """Extract terms and definitions from IPCC Glossary PDF."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self.terms = []
        
    def open_pdf(self):
        """Open the PDF document."""
        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"✅ Opened PDF: {self.pdf_path}")
            print(f"📄 Total pages: {len(self.doc)}")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            raise
    
    def close_pdf(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
    
    def extract_text_with_formatting(self, page_num: int) -> str:
        """Extract text from a page with formatting information."""
        if not self.doc or page_num >= len(self.doc):
            return ""
        
        page = self.doc[page_num]
        
        # Get text blocks with formatting info
        blocks = page.get_text("dict")
        text_with_format = []
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            # Check if text is bold (font flags)
                            is_bold = span.get("flags", 0) & 2**4  # Bold flag
                            text_with_format.append({
                                "text": text,
                                "bold": bool(is_bold),
                                "font_size": span.get("size", 0)
                            })
        
        return text_with_format
    
    def identify_terms_from_text(self, text_blocks: List[Dict]) -> List[Dict]:
        """Identify terms from text blocks based on formatting and patterns."""
        terms = []
        current_term = None
        current_definition = []
        
        for i, block in enumerate(text_blocks):
            text = block["text"]
            is_bold = block["bold"]
            font_size = block["font_size"]
            
            # Skip header/footer text
            if any(skip in text.lower() for skip in ["ipcc glossary", "semanticclimate", "page", "|", "translations", "parent-term", "sub-terms", "wikipedia entry"]):
                continue
            
            # Look for term patterns
            # Terms are often in bold, have larger font, or are followed by definitions
            if self._is_likely_term(text, is_bold, font_size, text_blocks, i):
                # Save previous term if exists
                if current_term:
                    definition = self._extract_first_sentence(" ".join(current_definition).strip())
                    terms.append({
                        "term": current_term,
                        "definition": definition,
                        "page": None  # Will be set later
                    })
                
                # Start new term
                current_term = text.strip()
                current_definition = []
                
            elif current_term and text:
                # This is part of the definition
                current_definition.append(text)
        
        # Add the last term
        if current_term:
            definition = self._extract_first_sentence(" ".join(current_definition).strip())
            terms.append({
                "term": current_term,
                "definition": definition,
                "page": None
            })
        
        return terms
    
    def _extract_first_sentence(self, text: str) -> str:
        """Extract the first sentence from definition text."""
        if not text:
            return ""
        
        # Look for sentence endings
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        
        for ending in sentence_endings:
            if ending in text:
                return text.split(ending)[0] + ending.rstrip()
        
        # If no sentence ending found, return the whole text
        return text
    
    def _is_likely_term(self, text: str, is_bold: bool, font_size: float, 
                       all_blocks: List[Dict], index: int) -> bool:
        """Determine if text is likely a term."""
        text = text.strip()
        
        # Skip very short text
        if len(text) < 2:
            return False
        
        # Skip common non-term patterns
        skip_patterns = [
            r"^[A-Z]{2,}$",  # All caps abbreviations
            r"^[0-9]+$",     # Just numbers
            r"^[A-Z][a-z]+$",  # Single word with capital
            r"^[a-z]+$",     # All lowercase
            r"^[A-Z][a-z]+ [A-Z][a-z]+$",  # Two words with capitals
            r"^https?://",   # URLs
            r"^www\.",       # URLs
            r"^[A-Z][a-z]+, [A-Z]",  # Author citations
            r"^\([A-Z]",     # Parenthetical citations
            r"^[A-Z]+\|",    # Page headers
            r"^[0-9]+\|[0-9]+",  # Page numbers
            r"^[A-Z]+$",     # Single word all caps
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Three words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Four words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Five words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Six words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Seven words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Eight words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Nine words with capitals
            r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$",  # Ten words with capitals
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, text):
                return False
        
        # Look for term indicators
        term_indicators = [
            # Bold text is likely a term
            is_bold,
            # Larger font size might indicate terms
            font_size > 10,
            # Text followed by definition patterns
            self._is_followed_by_definition(all_blocks, index),
            # Text that looks like a term (mixed case, reasonable length)
            self._looks_like_term(text)
        ]
        
        return any(term_indicators)
    
    def _is_followed_by_definition(self, blocks: List[Dict], index: int) -> bool:
        """Check if text is followed by definition-like content."""
        if index + 1 >= len(blocks):
            return False
        
        next_text = blocks[index + 1]["text"]
        
        # Definition indicators
        definition_patterns = [
            r"^[A-Z][a-z]",  # Starts with capital letter
            r"^The ",        # Starts with "The"
            r"^A ",          # Starts with "A"
            r"^An ",         # Starts with "An"
            r"^All ",        # Starts with "All"
            r"^Any ",        # Starts with "Any"
        ]
        
        return any(re.match(pattern, next_text) for pattern in definition_patterns)
    
    def _looks_like_term(self, text: str) -> bool:
        """Check if text looks like a term."""
        text = text.strip()
        
        # Good term characteristics - focus on actual glossary terms
        good_patterns = [
            r"^[a-z]+(-[a-z]+)*$",  # lowercase with optional hyphens (e.g., "active-layer")
            r"^[a-z]+ [a-z]+$",     # two lowercase words (e.g., "active layer")
            r"^[a-z]+ [a-z]+ [a-z]+$",  # three lowercase words (e.g., "acute food insecurity")
            r"^[a-z]+–[a-z]+$",     # lowercase with en-dash (e.g., "aerosol–cloud")
            r"^[a-z]+–[a-z]+ [a-z]+$",  # lowercase with en-dash and word
            r"^[a-z]+ [a-z]+–[a-z]+$",  # word with en-dash (e.g., "adaptation gap")
            r"^[a-z]+ [a-z]+ [a-z]+–[a-z]+$",  # three words with en-dash
            r"^[a-z]+ [a-z]+ [a-z]+ [a-z]+$",  # four lowercase words
            r"^[a-z]+ [a-z]+ [a-z]+ [a-z]+ [a-z]+$",  # five lowercase words
        ]
        
        return any(re.match(pattern, text) for pattern in good_patterns)
    
    def extract_terms_from_page(self, page_num: int) -> List[Dict]:
        """Extract terms from a specific page."""
        text_blocks = self.extract_text_with_formatting(page_num)
        terms = self.identify_terms_from_text(text_blocks)
        
        # Add page number to terms
        for term in terms:
            term["page"] = page_num + 1  # Convert to 1-based page numbers
        
        return terms
    
    def extract_all_terms(self, max_pages: Optional[int] = None) -> List[Dict]:
        """Extract all terms from the PDF."""
        if not self.doc:
            self.open_pdf()
        
        all_terms = []
        total_pages = min(len(self.doc), max_pages) if max_pages else len(self.doc)
        
        print(f"🔍 Extracting terms from {total_pages} pages...")
        
        for page_num in range(total_pages):
            if page_num % 50 == 0:
                print(f"   Processing page {page_num + 1}/{total_pages}")
            
            try:
                page_terms = self.extract_terms_from_page(page_num)
                all_terms.extend(page_terms)
            except Exception as e:
                print(f"⚠️  Error processing page {page_num + 1}: {e}")
                continue
        
        print(f"✅ Extracted {len(all_terms)} terms total")
        return all_terms
    
    def create_pdf_address(self, term: str, page: int) -> str:
        """Create a PDF address for the term."""
        # Simple address format: page number and term
        safe_term = term.replace(" ", "_").replace("-", "_").lower()
        return f"page={page}&term={safe_term}"
    
    def save_to_csv(self, terms: List[Dict], output_path: str):
        """Save terms to CSV file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            
            # Write header
            writer.writerow(['term', 'definition', 'address_of_entry'])
            
            # Write terms
            for term_data in terms:
                address = self.create_pdf_address(term_data['term'], term_data['page'])
                writer.writerow([
                    term_data['term'],
                    term_data['definition'],
                    address
                ])
        
        print(f"💾 Saved {len(terms)} terms to: {output_file}")


def main():
    """Main function to extract IPCC glossary terms."""
    pdf_path = "test/resources/pdf/IPCC Glossary.pdf"
    output_path = "temp/ipcc_glossary_terms.csv"
    
    print("🔍 IPCC Glossary Term Extraction")
    print("=" * 50)
    
    # Check if PDF exists
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    extractor = IPCCGlossaryExtractor(pdf_path)
    
    try:
        # Extract terms (start with first 50 pages for testing)
        terms = extractor.extract_all_terms(max_pages=50)
        
        if terms:
            # Save to CSV
            extractor.save_to_csv(terms, output_path)
            
            # Show sample results
            print(f"\n📋 Sample extracted terms:")
            for i, term in enumerate(terms[:10]):
                print(f"  {i+1}. {term['term']} (page {term['page']})")
                print(f"     Definition: {term['definition'][:100]}...")
                print()
        else:
            print("❌ No terms extracted")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close_pdf()


if __name__ == "__main__":
    main() 