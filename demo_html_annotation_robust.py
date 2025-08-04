#!/usr/bin/env python3
"""
Robust HTML Annotation Demo
Uses DOM-based approach to handle complex documents
"""

from pathlib import Path
from lxml.html import tostring, HTMLParser, fromstring
import lxml.etree as ET
import re

def create_annotated_document_robust(html_elem, terms):
    """Create a full annotated HTML document using DOM-based approach."""
    from lxml.html import fromstring, tostring
    import re

    # Sort terms by length (longest first) to avoid partial matches
    sorted_terms = sorted(terms, key=len, reverse=True)
    
    # Precompile regexes for all terms
    term_patterns = [
        (term, re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE))
        for term in sorted_terms
    ]
    
    def annotate_text_node(text_node, parent_elem):
        """Annotate a text node and return list of elements to insert."""
        if not text_node or not text_node.strip():
            return []
        
        result = []
        text = text_node
        idx = 0
        
        while idx < len(text):
            match_obj = None
            match_term = None
            match_start = None
            match_end = None
            
            # Find the earliest match among all terms
            for term, pattern in term_patterns:
                m = pattern.search(text, idx)
                if m:
                    if match_obj is None or m.start() < match_start:
                        match_obj = m
                        match_term = term
                        match_start = m.start()
                        match_end = m.end()
            
            if match_obj:
                # Add text before match
                if match_start > idx:
                    result.append(text[idx:match_start])
                
                # Create annotation element
                term_id = match_term.lower().replace(' ', '_').replace('°', '').replace('c', 'c')
                a_elem = ET.Element('a', {'class': 'annotation', 'href': f'#{term_id}'})
                a_elem.text = match_obj.group(0)
                result.append(a_elem)
                
                idx = match_end
            else:
                # No more matches
                result.append(text[idx:])
                break
        
        return result
    
    def process_element(elem):
        """Process an element recursively, annotating text nodes."""
        # Skip if this is an <a> element (don't annotate inside existing links)
        if elem.tag == 'a':
            return elem
        
        # Create a new element to avoid mutating the original
        new_elem = ET.Element(elem.tag, attrib=elem.attrib)
        
        # Process text content
        if elem.text:
            annotated_parts = annotate_text_node(elem.text, elem)
            for part in annotated_parts:
                if isinstance(part, str):
                    if len(new_elem) == 0:
                        new_elem.text = part
                    else:
                        # Add as tail to the last child
                        if new_elem[-1].tail is None:
                            new_elem[-1].tail = part
                        else:
                            new_elem[-1].tail += part
                else:
                    new_elem.append(part)
        
        # Process children
        for child in elem:
            processed_child = process_element(child)
            new_elem.append(processed_child)
            
            # Process tail content
            if child.tail:
                annotated_tail_parts = annotate_text_node(child.tail, elem)
                for part in annotated_tail_parts:
                    if isinstance(part, str):
                        if new_elem[-1].tail is None:
                            new_elem[-1].tail = part
                        else:
                            new_elem[-1].tail += part
                    else:
                        new_elem.append(part)
        
        return new_elem
    
    # Process the entire document
    annotated_root = process_element(html_elem)
    
    # Return as string
    return tostring(annotated_root, encoding='unicode', pretty_print=False)

def demo_html_annotation_robust():
    """Demonstrate robust HTML annotation functionality"""
    print("🔗 Robust HTML Annotation Demo")
    print("=" * 50)
    
    # Use the WG1 Chapter 1 file (working group report)
    html_file = Path("./temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return
    
    print(f"📄 Loading HTML file: {html_file}")
    
    # Load the HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_elem = fromstring(html_content)
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
    
    # Apply annotation
    print(f"\n🔧 Applying robust annotation...")
    
    # Create full annotated HTML document
    annotated_html = create_annotated_document_robust(html_elem, climate_terms)
    
    # Save annotated output
    output_file = Path("./temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_robust.html")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(annotated_html)
    
    print(f"\n💾 Saved annotated HTML to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size:,} bytes")
    
    # Test text content preservation
    print(f"\n🔍 Testing text content preservation...")
    
    # Extract text from original
    original_doc = fromstring(html_content)
    original_text = original_doc.text_content()
    original_text = re.sub(r'\s+', ' ', original_text).strip()
    
    # Extract text from annotated
    annotated_doc = fromstring(annotated_html)
    annotated_text = annotated_doc.text_content()
    annotated_text = re.sub(r'\s+', ' ', annotated_text).strip()
    
    print(f"   Original text length: {len(original_text):,} characters")
    print(f"   Annotated text length: {len(annotated_text):,} characters")
    print(f"   Text content identical: {original_text == annotated_text}")
    
    if original_text != annotated_text:
        print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
        print("   Length difference: {len(original_text) - len(annotated_text)} characters")
    else:
        print("\n✅ TEXT CONTENT IS PRESERVED!")
    
    return output_file

if __name__ == "__main__":
    output_file = demo_html_annotation_robust()
    if output_file and output_file.exists():
        print(f"\n✅ Robust demo completed successfully!")
        print(f"📄 You can view the annotated HTML at: {output_file}")
    else:
        print(f"\n❌ Robust demo failed") 