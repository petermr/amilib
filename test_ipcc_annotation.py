#!/usr/bin/env python3
"""
Test script for IPCC PDF annotation with HTML wordlists
"""

from amilib.ami_pdf_libs import process_ipcc_pdf_with_html_wordlist

def main():
    """Test the IPCC PDF annotation functionality"""
    print("🧪 Testing IPCC PDF Annotation with HTML Wordlist")
    print("=" * 60)
    
    # Test files
    pdf_path = "test/resources/ar6/glossary/IPCC_AR6_WGIII_Annex-I.pdf"
    html_wordlist = "test/resources/pdf/wg02chapt07_dict.html"
    output_path = "IPCC_AR6_annotated_test.pdf"
    
    try:
        # Process the PDF
        process_ipcc_pdf_with_html_wordlist(pdf_path, html_wordlist, output_path)
        
        print(f"\n✅ Success! Annotated PDF saved as: {output_path}")
        print("📖 You can now open this PDF and click on the underlined terms to visit Wikipedia")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 