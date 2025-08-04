#!/usr/bin/env python3
"""
Simplified BioRxiv PDF annotation script
Processes climate change PDFs and adds hyperlinks to IPCC glossary terms.
Avoids pdfplumber dependency issues.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF
from fitz import Document, Rect

class SimplePDFHyperlinkAdder:
    """Simplified PDF hyperlink adder for climate glossary terms"""
    
    def __init__(self, input_pdf: str, word_list_file: str, output_pdf: str):
        self.input_pdf = input_pdf
        self.word_list_file = word_list_file
        self.output_pdf = output_pdf
        self.word_list = {}
        self.entries = []
        
    def load_word_list(self) -> None:
        """Load word list from CSV with definitions"""
        with open(self.word_list_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                term = row['term'].strip().lower()
                definition = row['definition'].strip()
                link = row['link_to_glossary_entry'].strip()
                
                self.word_list[term] = link
                self.entries.append({
                    'term': term,
                    'definition': definition,
                    'link': link
                })
        
        print(f"✅ Loaded {len(self.word_list)} words with hyperlinks from CSV")
    
    def get_entry_info(self, term: str) -> Optional[Dict[str, str]]:
        """Get definition for tooltip"""
        for entry in self.entries:
            if entry['term'] == term.lower():
                return entry
        return None

    def find_word_instances(self, doc: Document) -> List[Tuple[int, str, Rect, str]]:
        """Find instances of glossary terms in the PDF"""
        word_instances = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks from the page
            text_blocks = page.get_text("dict")["blocks"]
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].lower()
                            
                            # Check each glossary term
                            for term in self.word_list.keys():
                                if term in text:
                                    # Get the bounding box
                                    bbox = Rect(span["bbox"])
                                    
                                    # Find the exact position of the term
                                    term_pos = text.find(term)
                                    if term_pos >= 0:
                                        # Calculate the position of the term within the span
                                        char_width = span["bbox"][2] - span["bbox"][0]
                                        if len(text) > 0:
                                            char_width /= len(text)
                                        
                                        term_x0 = span["bbox"][0] + (term_pos * char_width)
                                        term_x1 = term_x0 + (len(term) * char_width)
                                        
                                        term_bbox = Rect(term_x0, span["bbox"][1], term_x1, span["bbox"][3])
                                        
                                        word_instances.append((page_num, term, term_bbox, self.word_list[term]))
        
        return word_instances

    def add_hyperlinks_and_styling(self, doc: Document, word_instances: List[Tuple[int, str, Rect, str]]) -> None:
        """Add hyperlinks and styling to the PDF"""
        for page_num, term, bbox, link in word_instances:
            page = doc[page_num]
            
            # Get entry info for tooltip
            entry_info = self.get_entry_info(term)
            tooltip = entry_info["definition"] if entry_info else term
            
            # Add hyperlink
            link_annot = page.insert_link({
                "kind": fitz.LINK_URI,
                "uri": link,
                "from": bbox,
                "title": tooltip
            })
            
            # Add blue underline
            page.draw_rect(bbox, color=(0, 0, 1), width=1)

    def process_pdf(self) -> Dict[str, int]:
        """Process the PDF and return hit counts"""
        print(f"📄 Processing: {self.input_pdf}")
        
        # Open the PDF
        doc = fitz.open(self.input_pdf)
        
        # Find word instances
        word_instances = self.find_word_instances(doc)
        
        # Count hits per term
        hit_counts = {}
        for _, term, _, _ in word_instances:
            hit_counts[term] = hit_counts.get(term, 0) + 1
        
        # Add hyperlinks and styling
        self.add_hyperlinks_and_styling(doc, word_instances)
        
        # Save the annotated PDF
        doc.save(self.output_pdf)
        doc.close()
        
        print(f"✅ Saved annotated PDF: {self.output_pdf}")
        print(f"📊 Found {len(word_instances)} total hits for {len(hit_counts)} unique terms")
        
        return hit_counts

class SimpleClimatePDFProcessor:
    """Process climate PDFs with IPCC glossary annotation"""
    
    def __init__(self):
        self.glossary_file = Path("temp", "ipcc_glossary_flat.csv")
        self.output_dir = Path("temp", "climate_pdfs_annotated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_glossary_terms(self) -> List[Dict[str, str]]:
        """Load terms from IPCC glossary CSV"""
        if not self.glossary_file.exists():
            raise FileNotFoundError(f"Glossary file not found: {self.glossary_file}")
        
        terms = []
        with open(self.glossary_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                terms.append(row)
        
        print(f"✅ Loaded {len(terms)} terms from glossary")
        return terms
    
    def create_csv_for_pdf(self, terms: List[Dict[str, str]], pdf_file: Path) -> Path:
        """Create CSV file for a specific PDF"""
        csv_file = self.output_dir / f"{pdf_file.stem}_terms.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['term', 'definition', 'link_to_glossary_entry'])
            
            for term_data in terms:
                term = term_data['term']
                definition = term_data['definition']
                link = term_data['link_to_glossary_entry']
                writer.writerow([term, definition, link])
        
        print(f"📖 Created word list CSV: {csv_file}")
        return csv_file
    
    def process_single_pdf(self, pdf_file: Path) -> Dict[str, int]:
        """Process a single PDF file and return hit counts"""
        print(f"🚀 Processing single PDF: {pdf_file.name}")
        print("=" * 50)
        
        # Load terms from glossary
        terms = self.load_glossary_terms()
        
        # Create CSV for this PDF
        csv_file = self.create_csv_for_pdf(terms, pdf_file)
        
        # Output PDF path with derived name
        output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
        
        # Create hyperlink adder
        adder = SimplePDFHyperlinkAdder(
            input_pdf=str(pdf_file),
            word_list_file=str(csv_file),
            output_pdf=str(output_pdf)
        )
        
        # Load word list
        adder.load_word_list()
        
        # Process PDF
        hit_counts = adder.process_pdf()
        
        # Print summary
        total_hits = sum(hit_counts.values())
        print(f"\n✅ COMPLETED: {pdf_file.name}")
        print(f"📊 Total hits: {total_hits}")
        print(f"📊 Unique terms: {len(hit_counts)}")
        print(f"💾 Output: {output_pdf.name}")
        
        return hit_counts

def main():
    processor = SimpleClimatePDFProcessor()
    
    # Find PDF files (only named bioRxiv PDFs, excluding versioned ones)
    pdf_dir = Path("test", "resources", "pdf", "climate_change")
    pdf_files = [f for f in pdf_dir.glob("*bioRxiv.pdf") if not f.name.startswith(('2024.', '2025.'))]
    
    print(f"📚 Found {len(pdf_files)} bioRxiv PDFs to process")
    
    # Check which ones are already annotated
    annotated_files = list(Path("temp", "climate_pdfs_annotated").glob("CLIMATE_GLOSSARY_ANNOTATED_*.pdf"))
    annotated_names = {f.name.replace("CLIMATE_GLOSSARY_ANNOTATED_", "") for f in annotated_files}
    
    # Filter out already annotated files
    unannotated_files = [f for f in pdf_files if f.name not in annotated_names]
    
    print(f"✅ Already annotated: {len(pdf_files) - len(unannotated_files)}")
    print(f"🔄 Need annotation: {len(unannotated_files)}")
    
    if not unannotated_files:
        print("🎉 All PDFs are already annotated!")
        return
    
    # Process first 2 PDFs
    print(f"\n📄 Processing first 2 PDFs:")
    for i, pdf_file in enumerate(unannotated_files[:2], 1):
        print(f"\n[{i}/2] Processing: {pdf_file.name}")
        try:
            hit_counts = processor.process_single_pdf(pdf_file)
            print(f"✅ Successfully processed: {pdf_file.name}")
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
    
    print(f"\n🎯 Completed processing 2 PDFs")
    print(f"📁 Annotated PDFs saved to: {processor.output_dir}")

if __name__ == "__main__":
    main() 