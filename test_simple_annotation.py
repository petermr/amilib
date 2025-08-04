#!/usr/bin/env python3
"""
Simple test of HTML annotation logic
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
    """Test the annotation logic with a simple HTML file"""
    print("🧪 Testing HTML annotation with simple document")
    print("=" * 50)
    
    # Read the simple test HTML
    html_file = Path("test_simple.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    html_elem = fromstring(html_content)
    
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
    
    print(f"📄 Original HTML length: {len(html_content)} characters")
    print(f"🎯 Climate terms: {climate_terms}")
    
    # Apply annotation
    annotated_html = create_annotated_document(html_elem, climate_terms)
    
    print(f"📄 Annotated HTML length: {len(annotated_html)} characters")
    
    # Save annotated output
    output_file = Path("test_simple_annotated.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(annotated_html)
    
    print(f"💾 Saved annotated HTML to: {output_file}")
    
    # Extract text content for comparison
    original_doc = fromstring(html_content)
    annotated_doc = fromstring(annotated_html)
    
    original_text = original_doc.text_content()
    annotated_text = annotated_doc.text_content()
    
    # Clean up whitespace for comparison
    original_text = re.sub(r'\s+', ' ', original_text).strip()
    annotated_text = re.sub(r'\s+', ' ', annotated_text).strip()
    
    print(f"\n📝 Text content comparison:")
    print(f"   Original text length: {len(original_text)} characters")
    print(f"   Annotated text length: {len(annotated_text)} characters")
    print(f"   Text content identical: {original_text == annotated_text}")
    
    if original_text != annotated_text:
        print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
        print("   Original text:")
        print(f"   '{original_text}'")
        print("   Annotated text:")
        print(f"   '{annotated_text}'")
    else:
        print("\n✅ TEXT CONTENT IS PRESERVED!")
    
    # Show the annotated HTML
    print(f"\n🔗 Annotated HTML preview:")
    print("-" * 30)
    print(annotated_html[:500] + "..." if len(annotated_html) > 500 else annotated_html)

if __name__ == "__main__":
    main() 