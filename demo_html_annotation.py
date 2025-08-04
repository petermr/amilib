#!/usr/bin/env python3
"""
Demo: HTML Annotation with IPCC Executive Summary
Shows current state and annotated output
"""

from pathlib import Path
from lxml.html import tostring, HTMLParser
import lxml.etree as ET

from amilib.ami_html import HtmlLib, AmiAnnotator
from amilib.core.util import Util

logger = Util.get_logger(__name__)

def demo_html_annotation():
    """Demonstrate HTML annotation functionality"""
    print("🔗 HTML Annotation Demo")
    print("=" * 50)
    
    # Use the WG1 Chapter 1 file (working group report)
    html_file = Path("./temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return
    
    print(f"📄 Loading HTML file: {html_file}")
    
    # Load the HTML
    html_elem = HtmlLib.parse_html(html_file)
    if html_elem is None:
        print("❌ Failed to parse HTML file")
        return
    
    # Extract a sample paragraph for demonstration
    paragraphs = html_elem.xpath("//p")
    if not paragraphs:
        print("❌ No paragraphs found in HTML")
        return
    
    # Get first few paragraphs for demo
    sample_paragraphs = paragraphs[:3]
    
    print(f"\n📝 Sample paragraphs from executive summary:")
    print("-" * 50)
    
    for i, p in enumerate(sample_paragraphs):
        text = p.text_content().strip()
        if text and len(text) > 50:  # Only show substantial paragraphs
            print(f"\nParagraph {i+1}:")
            print(f"  {text[:200]}...")
    
    # Climate terms for annotation
    climate_terms = [
        "climate change",
        "global warming", 
        "greenhouse gas",
        "carbon dioxide",
        "temperature",
        "emissions",
        "mitigation",
        "adaptation",
        "IPCC",
        "atmosphere",
        "1.5°C",
        "2°C"
    ]
    
    print(f"\n🎯 Climate terms for annotation: {climate_terms}")
    
    # Create annotator
    annotator = AmiAnnotator(words=climate_terms)
    
    # Apply annotation to sample paragraphs
    print(f"\n🔧 Applying annotation...")
    
    annotated_paragraphs = []
    for p in sample_paragraphs:
        # Create a copy for annotation
        p_copy = ET.fromstring(tostring(p, encoding='unicode'))
        
        # Apply annotation (placeholder - will be implemented)
        annotated_p = apply_annotation_to_paragraph(p_copy, climate_terms)
        annotated_paragraphs.append(annotated_p)
    
    # Show annotated output
    print(f"\n📋 Annotated output:")
    print("-" * 50)
    
    for i, p in enumerate(annotated_paragraphs):
        # Get text content safely
        if hasattr(p, 'text_content'):
            text = p.text_content().strip()
        else:
            text = ''.join(p.itertext()).strip()
        if text and len(text) > 50:
            print(f"\nAnnotated Paragraph {i+1}:")
            print(f"  {text[:200]}...")
            
            # Show HTML structure
            html_output = tostring(p, encoding='unicode', pretty_print=True)
            print(f"\n  HTML structure:")
            print(f"    {html_output[:300]}...")
    
    # Save annotated output
    output_file = Path("./temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_demo.html")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create full annotated HTML document
    annotated_html = create_annotated_document(html_elem, climate_terms)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(annotated_html)
    
    print(f"\n💾 Saved annotated HTML to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size:,} bytes")
    
    return output_file

def create_annotated_document(html_elem, terms):
    """Create a full annotated HTML document that preserves text content exactly, skipping annotation inside <a> tags."""
    from lxml.html import fromstring, tostring
    import re

    # Convert the HTML element to a string first
    html_string = tostring(html_elem, encoding='unicode', pretty_print=False)
    
    # Sort terms by length (longest first) to avoid partial matches
    sorted_terms = sorted(terms, key=len, reverse=True)
    
    # Create a function to check if a position is inside an <a> tag
    def is_inside_link_tag(html_str, pos):
        """Check if position is inside an existing <a> tag"""
        # Look backwards from position to find the last <a> or </a>
        before_pos = html_str[:pos]
        last_a_open = before_pos.rfind('<a')
        last_a_close = before_pos.rfind('</a>')
        
        # If we found an <a> tag and it's after the last </a> (or there's no </a>), we're inside a link
        if last_a_open > last_a_close:
            return True
        return False
    
    # Process each term
    for term in sorted_terms:
        # Create regex pattern for the term (word boundaries, case insensitive)
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        
        # Find all matches
        matches = list(pattern.finditer(html_string))
        
        # Process matches in reverse order to avoid offset issues
        for match in reversed(matches):
            start_pos = match.start()
            end_pos = match.end()
            
            # Check if this match is inside an existing <a> tag
            if is_inside_link_tag(html_string, start_pos):
                continue  # Skip annotation inside existing links
            
            # Get the matched text
            matched_text = match.group(0)
            
            # Create the annotation HTML
            term_id = term.lower().replace(' ', '_').replace('°', '').replace('c', 'c')
            annotation_html = f'<a class="annotation" href="#{term_id}">{matched_text}</a>'
            
            # Replace the text with the annotation
            html_string = html_string[:start_pos] + annotation_html + html_string[end_pos:]
    
    return html_string

def apply_annotation_to_paragraph(paragraph_elem, terms):
    """Apply annotation to a paragraph element - simplified to just return the element."""
    # For now, just return the element as-is
    # The actual annotation will be done at the document level
    return paragraph_elem

def markup_term_in_element(element, term):
    """Mark up a specific term within an element - simplified to just return the element."""
    # For now, just return the element as-is
    # The actual annotation will be done at the document level
    return element

if __name__ == "__main__":
    output_file = demo_html_annotation()
    if output_file and output_file.exists():
        print(f"\n✅ Demo completed successfully!")
        print(f"📄 You can view the annotated HTML at: {output_file}")
    else:
        print(f"\n❌ Demo failed") 