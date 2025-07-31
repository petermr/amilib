#!/usr/bin/env python3
"""
Climate PDF Markup Script

This script processes PDF files in test/resources/pdf/climate_change and adds hyperlinks
to glossary terms from the IPCC glossary TSV file.

Usage:
    python scripts/markup_climate_pdfs_with_glossary.py
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz  # PyMuPDF

# Add amilib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from amilib.ami_pdf_libs import PDFHyperlinkAdder


class ClimatePDFHyperlinkAdder(PDFHyperlinkAdder):
    """Enhanced PDFHyperlinkAdder that can handle definitions from TSV"""
    
    def __init__(self, input_pdf: str, word_list_file: str, output_pdf: str, definitions: Dict[str, Dict[str, str]] = None):
        super().__init__(input_pdf, word_list_file, output_pdf)
        self.definitions = definitions or {}
    
    def get_entry_info(self, term: str) -> Optional[Dict[str, str]]:
        """Get definition information for a term"""
        term_lower = term.lower()
        for term_key, info in self.definitions.items():
            if term_key.lower() == term_lower:
                return {
                    'term': term_key,
                    'description': info['definition']
                }
        return None


class ClimatePDFMarkupProcessor:
    """Process climate PDFs with IPCC glossary markup"""
    
    def __init__(self):
        self.glossary_tsv = Path("temp", "ipcc_glossary_wordlist.csv")
        self.pdf_dir = Path("test", "resources", "pdf", "climate_change")
        self.output_dir = Path("temp", "climate_pdfs_annotated")
        self.hit_counts = {}  # Track hits per term across all PDFs
        
    def load_glossary_terms(self) -> Dict[str, Dict[str, str]]:
        """Load terms from TSV file with definitions and links"""
        terms = {}
        
        if not self.glossary_tsv.exists():
            raise FileNotFoundError(f"Glossary TSV file not found: {self.glossary_tsv}")
        
        with open(self.glossary_tsv, 'r', encoding='utf-8') as f:
            # Skip UTF-8 BOM if present
            content = f.read()
            if content.startswith('\ufeff'):
                content = content[1:]
            
            reader = csv.DictReader(content.splitlines(), delimiter='\t')
            for row in reader:
                term = row['term'].strip()
                definition = row['definition'].strip()
                link = row['link_to_glossary_entry'].strip()
                
                terms[term] = {
                    'definition': definition,
                    'link': link
                }
        
        print(f"✅ Loaded {len(terms)} terms from glossary")
        return terms
    
    def find_pdf_files(self) -> List[Path]:
        """Find PDF files starting with A-W"""
        pdf_files = []
        for pdf_file in self.pdf_dir.glob("[A-W]*.pdf"):
            pdf_files.append(pdf_file)
            if len(pdf_files) >= 1:  # Limit to 1 file for testing
                break
        
        print(f"✅ Found {len(pdf_files)} PDF files to process")
        return pdf_files
    
    def create_csv_for_pdf(self, terms: Dict[str, Dict[str, str]], pdf_file: Path) -> Path:
        """Create a CSV file for the PDF markup process"""
        csv_file = self.output_dir / f"{pdf_file.stem}_terms.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # PDFHyperlinkAdder expects: term, link (2 columns only)
            for term, info in terms.items():
                writer.writerow([term, info['link']])
        
        return csv_file
    
    def process_pdf(self, pdf_file: Path, terms: Dict[str, Dict[str, str]]) -> Dict[str, int]:
        """Process a single PDF file and return hit counts"""
        print(f"\n📄 Processing: {pdf_file.name}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create CSV file for this PDF
        csv_file = self.create_csv_for_pdf(terms, pdf_file)
        
        # Output PDF path with derived name
        output_pdf = self.output_dir / f"CLIMATE_GLOSSARY_ANNOTATED_{pdf_file.stem}.pdf"
        
        # Process PDF
        try:
            # Create a custom PDFHyperlinkAdder that can handle definitions
            adder = ClimatePDFHyperlinkAdder(
                input_pdf=str(pdf_file),
                word_list_file=str(csv_file),
                output_pdf=str(output_pdf),
                definitions=terms
            )
            
            # Load word list
            adder.load_word_list()
            
            # Process PDF
            adder.process_pdf()
            
            # Get hit counts from the processed document
            hit_counts = self.count_hits_in_pdf(output_pdf, terms)
            
            print(f"✅ Processed {pdf_file.name} -> {output_pdf.name}")
            print(f"   Hits: {sum(hit_counts.values())} total")
            
            return hit_counts
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            return {}
    
    def count_hits_in_pdf(self, pdf_path: Path, terms: Dict[str, Dict[str, str]]) -> Dict[str, int]:
        """Count actual hits in the processed PDF"""
        hit_counts = {}
        
        try:
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().lower()
                
                for term in terms.keys():
                    term_lower = term.lower()
                    count = text.count(term_lower)
                    if count > 0:
                        hit_counts[term] = hit_counts.get(term, 0) + count
            
            doc.close()
            
        except Exception as e:
            print(f"Warning: Could not count hits in {pdf_path}: {e}")
        
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
    
    def process_all_pdfs(self):
        """Main processing function"""
        print("🚀 Starting Climate PDF Markup Process")
        print("=" * 50)
        
        # Load glossary terms
        terms = self.load_glossary_terms()
        
        # Find PDF files
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            print("❌ No PDF files found to process")
            return
        
        # Process each PDF
        all_hit_counts = {}
        
        for pdf_file in pdf_files:
            hit_counts = self.process_pdf(pdf_file, terms)
            
            # Accumulate hit counts
            for term, count in hit_counts.items():
                all_hit_counts[term] = all_hit_counts.get(term, 0) + count
        
        # Print overall summary
        print("\n" + "=" * 50)
        print("📊 OVERALL SUMMARY")
        print("=" * 50)
        
        total_hits = sum(all_hit_counts.values())
        print(f"Total hits across all PDFs: {total_hits}")
        print(f"Unique terms found: {len(all_hit_counts)}")
        
        # Top terms
        sorted_hits = sorted(all_hit_counts.items(), key=lambda x: x[1], reverse=True)
        print("\nTop 10 terms by frequency:")
        for i, (term, count) in enumerate(sorted_hits[:10], 1):
            print(f"{i:2d}. {term}: {count} hits")
        
        # Add summaries to each PDF
        print("\n📝 Adding hit summaries to PDFs...")
        for pdf_file in pdf_files:
            output_pdf = self.output_dir / f"{pdf_file.stem}_annotated.pdf"
            if output_pdf.exists():
                self.add_hit_summary_to_pdf(output_pdf, all_hit_counts, total_hits)
        
        print(f"\n✅ Processing complete! Annotated PDFs saved to: {self.output_dir}")


def main():
    """Main function"""
    processor = ClimatePDFMarkupProcessor()
    processor.process_all_pdfs()


if __name__ == "__main__":
    main() 