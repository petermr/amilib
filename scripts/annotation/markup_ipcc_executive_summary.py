#!/usr/bin/env python3
"""
Markup IPCC Executive Summary with glossary terms using HTML Builder
"""

import csv
import re
from pathlib import Path
from lxml import html, etree
from amilib.ami_html import HtmlLib

class IPCCExecutiveSummaryMarkup:
    """Markup IPCC Executive Summary with glossary terms using HTML Builder"""
    
    def __init__(self):
        self.glossary_file = Path("temp", "ipcc_glossary_flat.csv")
        self.input_html = Path("test", "resources", "ipcc", "cleaned_content", "wg1", "Chapter04", "html_with_ids.html")
        self.output_dir = Path("temp", "ipcc_executive_summary")
        self.output_dir.mkdir(exist_ok=True)
        self.terms = {}
        
    def load_glossary_terms(self) -> dict:
        """Load terms from IPCC glossary CSV"""
        if not self.glossary_file.exists():
            raise FileNotFoundError(f"Glossary file not found: {self.glossary_file}")
        
        terms = {}
        with open(self.glossary_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                term = row['term'].strip()
                link = row['link_to_glossary_entry'].strip()
                definition = row['definition'].strip()
                
                terms[term.lower()] = {
                    'term': term,
                    'link': link,
                    'definition': definition
                }
        
        print(f"✅ Loaded {len(terms)} terms from glossary")
        return terms
    
    def extract_executive_summary(self, html_elem) -> etree._Element:
        """Extract Executive Summary div content"""
        # Find the div with id="Executive"
        executive_div = html_elem.xpath('//div[@id="Executive"]')
        if not executive_div:
            raise ValueError("Could not find div with id='Executive'")
        
        print(f"✅ Extracted Executive Summary div")
        return executive_div[0]
    
    def add_links_to_text(self, html_elem, terms: dict) -> etree._Element:
        """Add links to text content using HtmlLib.add_element for proper DOM manipulation"""
        # Sort terms by length (longest first) to avoid partial matches
        sorted_terms = sorted(terms.keys(), key=len, reverse=True)
        
        # Process each element that contains text
        for elem in html_elem.xpath('//*[text()]'):
            if elem.text and elem.text.strip():
                text = elem.text.strip()
                
                # Check each term against this text
                for term_lower in sorted_terms:
                    term_info = terms[term_lower]
                    term = term_info['term']
                    
                    if term.lower() in text.lower():
                        # Create link element using HtmlLib.add_element
                        link_elem = HtmlLib.add_element(
                            elem, 
                            "a", 
                            attribs={
                                "href": term_info["link"],
                                "title": term_info["definition"]
                            },
                            text=term
                        )
                        
                        # Clear the original text content
                        elem.text = ""
                        break
        
        return html_elem
    
    def markup_executive_summary(self):
        """Main method to markup the executive summary"""
        print("🚀 Starting IPCC Executive Summary Markup")
        print("=" * 50)
        
        # Load glossary terms
        self.terms = self.load_glossary_terms()
        
        # Read HTML file
        print(f"📖 Reading HTML file: {self.input_html}")
        html_elem = HtmlLib.parse_html(self.input_html)
        
        # Extract Executive Summary
        executive_elem = self.extract_executive_summary(html_elem)
        
        # Add glossary links using HTML Builder
        print("🔗 Adding glossary links...")
        marked_elem = self.add_links_to_text(executive_elem, self.terms)
        
        # Count links added
        link_count = len(marked_elem.xpath('//a[@href]'))
        print(f"✅ Added links to {link_count} elements")
        
        # Create output HTML with proper structure
        output_html = self.create_output_html(marked_elem)
        
        # Save to file
        output_file = self.output_dir / "IPCC_WG1_Chapter4_Executive_Summary_Marked.html"
        HtmlLib.write_html_file(output_html, output_file, debug=False)
        print(f"✅ Saved marked up Executive Summary to: {output_file}")
        
        print("=" * 50)
        print("📊 Summary:")
        print(f"   - Input: {self.input_html}")
        print(f"   - Output: {output_file}")
        print(f"   - Glossary terms: {len(self.terms)}")
        print(f"   - File size: {len(etree.tostring(output_html, encoding='unicode'))} characters")
    
    def create_output_html(self, marked_elem: etree._Element) -> etree._Element:
        """Create proper HTML structure with marked content"""
        # Create new HTML document using HTML Builder
        html_elem = etree.Element("html")
        head = etree.SubElement(html_elem, "head")
        body = etree.SubElement(html_elem, "body")
        
        # Add title
        title = etree.SubElement(head, "title")
        title.text = "IPCC WG1 Chapter 4 Executive Summary - Marked"
        
        # Add CSS styles for links
        style = etree.SubElement(head, "style")
        style.text = """
        a[href*="htmlpreview.github.io"] {
            color: #0066cc;
            text-decoration: underline;
        }
        a[href*="htmlpreview.github.io"]:hover {
            color: #003366;
            text-decoration: none;
        }
        """
        
        # Add the marked content to body
        body.append(marked_elem)
        
        return html_elem

def main():
    markup = IPCCExecutiveSummaryMarkup()
    markup.markup_executive_summary()

if __name__ == "__main__":
    main() 