#!/usr/bin/env python3
"""
Demo HTML annotation using the existing amilib annotation infrastructure.
This uses the proven HtmlLib.search_phrases_in_paragraphs() method.
"""

from pathlib import Path
from lxml.html import fromstring, tostring
from amilib.ami_html import HtmlLib

def create_annotated_document_using_library(html_elem, terms):
    """Create annotated HTML document using the existing amilib annotation infrastructure."""
    
    # Find all paragraphs in the document
    paras = html_elem.xpath("//p")
    
    # Use the existing library method to annotate paragraphs
    phrase_counter_by_para_id = HtmlLib.search_phrases_in_paragraphs(
        paras=paras,
        phrases=terms,
        markup=True,  # This enables actual annotation
        ignore_non_id_para=False,  # Process all paragraphs, not just those with IDs
        url_base=None  # No external URLs, just internal anchors
    )
    
    # Return the modified HTML element
    return html_elem

def main():
    """Main function to demonstrate annotation using the library."""
    print("🔗 HTML Annotation using amilib library infrastructure")
    print("=" * 60)
    
    # Climate terms for annotation
    climate_terms = [
        "climate change",
        "global warming", 
        "greenhouse gas",
        "carbon dioxide",
        "IPCC",
        "atmosphere",
        "emissions",
        "mitigation",
        "adaptation"
    ]
    
    # File paths
    input_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    output_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_using_library.html")
    
    print(f"📄 Input file: {input_file}")
    print(f"📄 Output file: {output_file}")
    print(f"🔍 Terms to annotate: {len(climate_terms)} terms")
    print()
    
    # Read and parse HTML
    print("📖 Reading HTML file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_elem = fromstring(html_content)
    print(f"   HTML parsed successfully")
    print(f"   Document size: {len(html_content):,} characters")
    
    # Apply annotation using library
    print("\n🔗 Applying annotation using amilib library...")
    annotated_elem = create_annotated_document_using_library(html_elem, climate_terms)
    
    # Write annotated HTML
    print(f"\n💾 Writing annotated HTML to {output_file}...")
    annotated_html = tostring(annotated_elem, encoding='unicode', pretty_print=False)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(annotated_html)
    
    print(f"   Annotated HTML written successfully")
    print(f"   Output size: {len(annotated_html):,} characters")
    
    # Count annotations
    annotations = annotated_elem.xpath('//a[@class="annotation"]')
    print(f"\n📊 Annotation statistics:")
    print(f"   Total annotations found: {len(annotations)}")
    
    # Count by term
    term_counts = {}
    for annotation in annotations:
        term = annotation.text_content().lower()
        term_counts[term] = term_counts.get(term, 0) + 1
    
    print(f"   Annotations by term:")
    for term, count in sorted(term_counts.items()):
        print(f"     {term}: {count}")
    
    print(f"\n✅ Annotation completed successfully using amilib library!")
    print(f"   Output file: {output_file}")

if __name__ == "__main__":
    main() 