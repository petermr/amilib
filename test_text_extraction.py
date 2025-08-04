#!/usr/bin/env python3
"""
Simple test to verify text content preservation during HTML annotation.
"""

from pathlib import Path
from lxml.html import fromstring, tostring
import re

def extract_text_from_html(html_file):
    """Extract all text content from HTML file, removing all markup."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    doc = fromstring(html_content)
    
    # Extract all text content
    text_content = doc.text_content()
    
    # Clean up whitespace
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    return text_content

def main():
    print("🔍 Testing text content preservation during HTML annotation")
    print("=" * 60)
    
    # File paths
    original_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/edited_html_with_ids.html")
    annotated_file = Path("temp/ipcc/cleaned_content/wg1/Chapter01/html_annotated_demo.html")
    
    # Extract text from original HTML
    print(f"📄 Extracting text from original: {original_file}")
    text_orig = extract_text_from_html(original_file)
    print(f"   Original text length: {len(text_orig):,} characters")
    print(f"   First 200 chars: {text_orig[:200]}...")
    print()
    
    # Extract text from annotated HTML
    print(f"📄 Extracting text from annotated: {annotated_file}")
    text_marked = extract_text_from_html(annotated_file)
    print(f"   Annotated text length: {len(text_marked):,} characters")
    print(f"   First 200 chars: {text_marked[:200]}...")
    print()
    
    # Compare
    print("🔍 Comparison:")
    print(f"   Text lengths match: {len(text_orig) == len(text_marked)}")
    print(f"   Text content identical: {text_orig == text_marked}")
    
    if text_orig != text_marked:
        print("\n❌ TEXT CONTENT IS NOT PRESERVED!")
        print("   Differences found:")
        
        # Find first difference
        min_len = min(len(text_orig), len(text_marked))
        for i in range(min_len):
            if text_orig[i] != text_marked[i]:
                print(f"   First difference at position {i}:")
                print(f"     Original:  '{text_orig[i:i+50]}...'")
                print(f"     Annotated: '{text_marked[i:i+50]}...'")
                break
        
        # Show length differences
        if len(text_orig) != len(text_marked):
            print(f"   Length difference: {len(text_orig) - len(text_marked)} characters")
    else:
        print("\n✅ TEXT CONTENT IS PRESERVED!")

if __name__ == "__main__":
    main() 