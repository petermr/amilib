#!/usr/bin/env python3
"""
Climate PDF Markup with IPCC Glossary
Processes climate change PDFs and adds hyperlinks to IPCC glossary terms.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF
from amilib.ami_pdf_libs import PDFHyperlinkAdder

class ClimatePDFHyperlinkAdder(PDFHyperlinkAdder):
    """Custom PDF hyperlink adder for climate glossary terms"""
    
    def __init__(self, input_pdf: str, word_list_file: str, output_pdf: str):
        super().__init__(input_pdf, word_list_file, output_pdf)
        self.entries = []  # Store definitions for tooltips
        
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

class ClimatePDFProcessor:
    """Process climate PDFs with IPCC glossary annotation"""
    
    def __init__(self):
        self.glossary_file = Path("temp", "ipcc_glossary_wordlist.csv")
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
            writer.writerow(['term', 'link'])
            
            for term_data in terms:
                term = term_data['term']
                link = term_data['link_to_glossary_entry']
                writer.writerow([term, link])
        
        print(f"📖 Loading word list from CSV: {csv_file}")
        return csv_file
    
    def process_pdf(self, pdf_file: Path, terms: List[Dict[str, str]]) -> Dict[str, int]:
        """Process a single PDF and return hit counts"""
        csv_file = self.create_csv_for_pdf(terms, pdf_file)
        
        # Output PDF path with derived name
        output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
        
        print(f"📄 Processing PDF: {pdf_file}")
        print(f"📝 Word list: {csv_file}")
        print(f"💾 Output: {output_pdf}")
        print("-" * 50)
        
        # Create hyperlink adder
        adder = ClimatePDFHyperlinkAdder(
            input_pdf=str(pdf_file),
            word_list_file=str(csv_file),
            output_pdf=str(output_pdf)
        )
        
        # Process PDF
        hit_counts = adder.process_pdf()
        
        print("-" * 44)
        print("✅ Processing complete!")
        print(f"📊 Statistics:")
        print(f"   Total words processed: {len(hit_counts)}")
        print(f"   Total matches found: {sum(hit_counts.values())}")
        print(f"   Output saved to: {output_pdf}")
        
        return hit_counts
    
    def add_hit_summary_to_pdf(self, pdf_path: Path, hit_counts: Dict[str, int], total_hits: int):
        """Add hit summary to the end of the PDF"""
        try:
            doc = fitz.open(str(pdf_path))
            
            # Create a new page for summary
            page = doc.new_page()
            
            # Add summary text
            text = f"Glossary Term Hit Summary\n\n"
            text += f"Total hits across all terms: {total_hits}\n\n"
            text += "Top terms by frequency:\n"
            
            # Sort by hit count
            sorted_hits = sorted(hit_counts.items(), key=lambda x: x[1], reverse=True)
            
            for term, count in sorted_hits[:20]:  # Top 20 terms
                text += f"• {term}: {count} hits\n"
            
            # Insert text
            page.insert_text((50, 50), text, fontsize=12)
            
            # Save with incremental update
            doc.saveIncr()
            doc.close()
            
            print(f"✅ Added hit summary to {pdf_path.name}")
            
        except Exception as e:
            print(f"Warning: Could not add summary to {pdf_path}: {e}")
    
    def process_single_pdf(self, pdf_file: Path):
        """Process a single PDF file and return hit counts"""
        print(f"🚀 Processing single PDF: {pdf_file.name}")
        print("=" * 50)
        
        # Load terms from glossary
        terms = self.load_glossary_terms()
        print(f"✅ Loaded {len(terms)} terms from glossary")
        
        # Create CSV for this PDF
        csv_file = self.create_csv_for_pdf(terms, pdf_file)
        
        # Output PDF path with derived name
        output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
        
        # Process PDF
        hit_counts = self.process_pdf(pdf_file, terms)
        
        # Add summary to PDF
        total_hits = sum(hit_counts.values())
        self.add_hit_summary_to_pdf(output_pdf, hit_counts, total_hits)
        
        print(f"\n✅ COMPLETED: {pdf_file.name}")
        print(f"📊 Total hits: {total_hits}")
        print(f"📊 Unique terms: {len(hit_counts)}")
        print(f"💾 Output: {output_pdf.name}")
        
        return hit_counts
    
    def process_all_pdfs(self):
        """Process all climate PDF files"""
        print("🚀 Starting Climate PDF Markup Process")
        print("=" * 50)
        
        # Load terms from glossary
        terms = self.load_glossary_terms()
        
        # Find PDF files
        pdf_dir = Path("test", "resources", "pdf", "climate_change")
        pdf_files = list(pdf_dir.glob("[A-W]*.pdf"))
        print(f"✅ Found {len(pdf_files)} PDF files to process")
        
        all_hit_counts = {}
        total_hits = 0
        
        for pdf_file in pdf_files:
            print(f"\n📄 Processing: {pdf_file.name}")
            
            # Create CSV for this PDF
            csv_file = self.create_csv_for_pdf(terms, pdf_file)
            
            # Output PDF path with derived name
            output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
            
            # Process PDF
            hit_counts = self.process_pdf(pdf_file, terms)
            
            # Accumulate hit counts
            for term, count in hit_counts.items():
                all_hit_counts[term] = all_hit_counts.get(term, 0) + count
                total_hits += count
            
            print(f"✅ Processed {pdf_file.name} -> {output_pdf.name}")
            print(f"   Hits: {sum(hit_counts.values())} total")
        
        # Print overall summary
        print("\n" + "=" * 50)
        print("📊 OVERALL SUMMARY")
        print("=" * 50)
        print(f"Total hits across all PDFs: {total_hits}")
        print(f"Unique terms found: {len(all_hit_counts)}")
        
        # Top 10 terms
        sorted_hits = sorted(all_hit_counts.items(), key=lambda x: x[1], reverse=True)
        print("\nTop 10 terms by frequency:")
        for i, (term, count) in enumerate(sorted_hits[:10], 1):
            print(f" {i:2d}. {term}: {count} hits")
        
        # Add hit summaries to PDFs
        print("\n📝 Adding hit summaries to PDFs...")
        for pdf_file in pdf_files:
            output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
            if output_pdf.exists():
                self.add_hit_summary_to_pdf(output_pdf, all_hit_counts, total_hits)
        
        print(f"\n✅ Processing complete! Annotated PDFs saved to: {self.output_dir}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process climate PDFs with IPCC glossary")
    parser.add_argument("--single", type=str, help="Process a single PDF file")
    
    args = parser.parse_args()
    processor = ClimatePDFProcessor()
    
    if args.single:
        # Process single PDF
        pdf_file = Path(args.single)
        if not pdf_file.exists():
            print(f"❌ PDF file not found: {pdf_file}")
            return
        processor.process_single_pdf(pdf_file)
    else:
        # Process all PDFs
        processor.process_all_pdfs()

if __name__ == "__main__":
    main() 