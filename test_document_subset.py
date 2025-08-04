#!/usr/bin/env python3
"""
Test HTML annotation with a subset of the large document
"""

from pathlib import Path
from lxml.html import fromstring, tostring
import re

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

def main():
    """Test annotation with a subset of the large document"""
    print("🧪 Testing HTML annotation with document subset")
    print("=" * 50)
    
    # Read the large HTML file
    html_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📄 Original document length: {len(html_content):,} characters")
    
    # Parse HTML
    html_elem = fromstring(html_content)
    
    # Extract just the first 10 paragraphs
    paragraphs = html_elem.xpath("//p")
    print(f"📝 Found {len(paragraphs)} paragraphs")
    
    if len(paragraphs) < 10:
        print("❌ Not enough paragraphs for testing")
        return
    
    # Create a subset with just the first 10 paragraphs
    subset_elem = ET.Element('html')
    body_elem = ET.SubElement(subset_elem, 'body')
    
    for i, p in enumerate(paragraphs[:10]):
        # Copy the paragraph
        p_copy = ET.fromstring(tostring(p, encoding='unicode'))
        body_elem.append(p_copy)
    
    # Convert subset to string
    subset_html = tostring(subset_elem, encoding='unicode', pretty_print=False)
    print(f"📄 Subset document length: {len(subset_html):,} characters")
    
    # Climate terms for testing
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
        "atmosphere"
    ]
    
    print(f"🎯 Climate terms: {climate_terms}")
    
    # Apply annotation to subset
    print(f"\n🔧 Applying annotation to subset...")
    annotated_subset = create_annotated_document(subset_elem, climate_terms)
    
    # Save subset output
    subset_output_file = Path("test_subset_annotated.html")
    with open(subset_output_file, 'w', encoding='utf-8') as f:
        f.write(annotated_subset)
    
    print(f"💾 Saved subset annotated HTML to: {subset_output_file}")
    
    # Test text content preservation
    print(f"\n🔍 Testing text content preservation...")
    
    # Extract text from original subset
    subset_doc = fromstring(subset_html)
    subset_text = subset_doc.text_content()
    subset_text = re.sub(r'\s+', ' ', subset_text).strip()
    
    # Extract text from annotated subset
    annotated_subset_doc = fromstring(annotated_subset)
    annotated_subset_text = annotated_subset_doc.text_content()
    annotated_subset_text = re.sub(r'\s+', ' ', annotated_subset_text).strip()
    
    print(f"   Original subset text length: {len(subset_text):,} characters")
    print(f"   Annotated subset text length: {len(annotated_subset_text):,} characters")
    print(f"   Text content identical: {subset_text == annotated_subset_text}")
    
    if subset_text != annotated_subset_text:
        print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
        print("   Length difference: {len(subset_text) - len(annotated_subset_text)} characters")
        
        # Show first difference
        min_len = min(len(subset_text), len(annotated_subset_text))
        for i in range(min_len):
            if subset_text[i] != annotated_subset_text[i]:
                print(f"   First difference at position {i}:")
                print(f"     Original:  '{subset_text[i:i+50]}...'")
                print(f"     Annotated: '{annotated_subset_text[i:i+50]}...'")
                break
    else:
        print("\n✅ TEXT CONTENT IS PRESERVED!")
    
    # Show the annotated subset
    print(f"\n🔗 Annotated subset preview:")
    print("-" * 30)
    print(annotated_subset[:500] + "..." if len(annotated_subset) > 500 else annotated_subset)

if __name__ == "__main__":
    import lxml.etree as ET
    main() 