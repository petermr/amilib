#!/usr/bin/env python3
"""
Demonstration script for PDF hyperlink adder functionality
Shows how to markup/annotate PDFs with wordlists
"""

import sys
from pathlib import Path
from amilib.pdf_hyperlink_adder import PDFHyperlinkAdder, create_sample_word_list

def demo_basic_usage():
    """Demonstrate basic usage of PDF hyperlink adder"""
    print("🔗 PDF Hyperlink Adder Demo")
    print("=" * 50)
    
    # Create sample word list
    print("\n1. Creating sample word list...")
    sample_words = "sample_words.csv"
    create_sample_word_list(sample_words)
    print(f"✅ Created: {sample_words}")
    
    # Show sample word list content
    print("\n2. Sample word list content:")
    with open(sample_words, 'r', encoding='utf-8') as f:
        for line in f:
            print(f"   {line.strip()}")
    
    return sample_words

def demo_with_test_pdf():
    """Demonstrate with test PDF"""
    print("\n3. Testing with available PDFs...")
    
    # Check for test PDFs
    test_pdfs = [
        "test/resources/pdf/1758-2946-3-44.pdf",
        "test/resources/pdf/breward_1.pdf",
        "test/resources/pdf/IPCC_AR6_WGII_Chapter07.pdf"
    ]
    
    word_lists = [
        "test/resources/pdf/climate_words.csv",
        "test/resources/pdf/breward_words.csv"
    ]
    
    available_pdfs = []
    for pdf_path in test_pdfs:
        if Path(pdf_path).exists():
            available_pdfs.append(pdf_path)
            print(f"   ✅ Found: {pdf_path}")
        else:
            print(f"   ❌ Missing: {pdf_path}")
    
    available_word_lists = []
    for word_list in word_lists:
        if Path(word_list).exists():
            available_word_lists.append(word_list)
            print(f"   ✅ Found: {word_list}")
        else:
            print(f"   ❌ Missing: {word_list}")
    
    return available_pdfs, available_word_lists

def demo_pdf_processing(pdf_path, word_list_path):
    """Demonstrate PDF processing"""
    print(f"\n4. Processing PDF: {pdf_path}")
    print(f"   Word list: {word_list_path}")
    
    # Create output path
    pdf_name = Path(pdf_path).stem
    output_pdf = f"output_{pdf_name}_with_links.pdf"
    
    # Process the PDF
    try:
        adder = PDFHyperlinkAdder(
            input_pdf=pdf_path,
            word_list_file=word_list_path,
            output_pdf=output_pdf
        )
        
        adder.process_pdf()
        
        print(f"✅ Successfully processed!")
        print(f"   Output: {output_pdf}")
        print(f"   Words processed: {adder.processed_words}")
        print(f"   Total matches: {adder.total_matches}")
        
        return output_pdf
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return None

def show_usage_instructions():
    """Show usage instructions"""
    print("\n📖 Usage Instructions:")
    print("=" * 50)
    print("""
1. Create a word list CSV file with format:
   word,hyperlink
   climate,https://en.wikipedia.org/wiki/Climate
   CO2,https://en.wikipedia.org/wiki/Carbon_dioxide

2. Run the script:
   python pdf_hyperlink_adder.py input.pdf word_list.csv output.pdf

3. Or use the Python API:
   from amilib.pdf_hyperlink_adder import PDFHyperlinkAdder
   
   adder = PDFHyperlinkAdder(
       input_pdf="document.pdf",
       word_list_file="words.csv", 
       output_pdf="document_with_links.pdf"
   )
   adder.process_pdf()

4. Features:
   - Case-insensitive word matching
   - Adds clickable hyperlinks to PDF
   - Adds blue underlines for visual indication
   - Supports multi-word terms
   - Preserves original PDF formatting
""")

def main():
    """Main demonstration function"""
    print("🎯 PDF Annotation/Markup Demo")
    print("=" * 60)
    
    # Demo basic usage
    sample_words = demo_basic_usage()
    
    # Demo with test PDFs
    available_pdfs, available_word_lists = demo_with_test_pdf()
    
    # Process PDFs if available
    if available_pdfs and available_word_lists:
        print(f"\n5. Processing available PDFs...")
        
        # Try to process the first available combination
        pdf_path = available_pdfs[0]
        word_list_path = available_word_lists[0]
        
        output_pdf = demo_pdf_processing(pdf_path, word_list_path)
        
        if output_pdf and Path(output_pdf).exists():
            print(f"\n🎉 Demo completed successfully!")
            print(f"   Check the output PDF: {output_pdf}")
            print(f"   Open it in a PDF viewer to see the hyperlinks")
        else:
            print(f"\n⚠️  Demo completed with warnings")
            print(f"   Check the error messages above")
    else:
        print(f"\n⚠️  No test PDFs or word lists found")
        print(f"   Please ensure test files are available")
    
    # Show usage instructions
    show_usage_instructions()
    
    print(f"\n✅ Demo completed!")

if __name__ == "__main__":
    main() 