#!/usr/bin/env python3
"""
Download PDF-only AR6 Annexes and Convert to HTML

Downloads PDF annexes that are only available as PDF (not HTML) and converts them
to HTML format, saving them in the standard location:
test/resources/ipcc/cleaned_content/<wg>/annex-<roman>-<type>.html

Date: 2025-12-06
"""

import sys
import os
from pathlib import Path
import requests
from urllib.parse import urljoin

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from amilib.pdf_args import PDFArgs
from amilib.html_generator import HtmlGenerator
from test.resources import Resources
import lxml.etree as ET
from amilib.ami_html import HtmlLib

# Base URLs for IPCC AR6 reports
BASE_URLS = {
    "wg1": "https://www.ipcc.ch/report/ar6/wg1/downloads/report/",
    "wg2": "https://www.ipcc.ch/report/ar6/wg2/downloads/report/",
    "wg3": "https://www.ipcc.ch/report/ar6/wg3/downloads/report/",
    "syr": "https://www.ipcc.ch/report/ar6/syr/downloads/report/",
}

# PDF-only annexes (based on failed HTML downloads with ~51KB files)
# Try multiple URL patterns for each annex
PDF_ONLY_ANNEXES = [
    {
        "report": "wg1", 
        "annex": "annex-i", 
        "type": "glossary", 
        "pdf_patterns": [
            "IPCC_AR6_WG1_AnnexI.pdf",
            "IPCC_AR6_WG1_Annex_I.pdf",
            "AnnexI.pdf",
            "Annex_I.pdf",
            "annex-i.pdf",
        ]
    },
    {
        "report": "wg1", 
        "annex": "annex-ii", 
        "type": "acronyms", 
        "pdf_patterns": [
            "IPCC_AR6_WG1_AnnexII.pdf",
            "IPCC_AR6_WG1_Annex_II.pdf",
            "AnnexII.pdf",
            "Annex_II.pdf",
            "annex-ii.pdf",
        ]
    },
    {
        "report": "wg3", 
        "annex": "annex-i", 
        "type": "glossary", 
        "pdf_patterns": [
            "IPCC_AR6_WG3_AnnexI.pdf",
            "IPCC_AR6_WG3_Annex_I.pdf",
            "AnnexI.pdf",
            "Annex_I.pdf",
            "annex-i.pdf",
        ]
    },
    {
        "report": "wg3", 
        "annex": "annex-ii", 
        "type": "acronyms", 
        "pdf_patterns": [
            "IPCC_AR6_WG3_AnnexII.pdf",
            "IPCC_AR6_WG3_Annex_II.pdf",
            "AnnexII.pdf",
            "Annex_II.pdf",
            "annex-ii.pdf",
        ]
    },
]

BASE_OUTPUT_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")


def download_pdf(url, output_path):
    """Download a PDF file from URL"""
    print(f"  Trying: {url}")
    try:
        response = requests.get(url, timeout=30, allow_redirects=True)
        # Check if it's actually a PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not url.endswith('.pdf'):
            # Check first few bytes for PDF magic number
            if len(response.content) > 4 and response.content[:4] != b'%PDF':
                return False, None
        
        response.raise_for_status()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size = output_path.stat().st_size
        print(f"  ✅ Downloaded {file_size:,} bytes to {output_path}")
        return True, file_size
    except Exception as e:
        return False, None


def convert_pdf_to_html(pdf_path, output_dir):
    """Convert PDF to HTML using the existing pipeline"""
    print(f"  Converting PDF to HTML...")
    try:
        # Use PDFArgs to convert PDF to HTML
        pdf_args = PDFArgs()
        pdf_args.inpath = pdf_path
        pdf_args.outdir = output_dir
        
        # Convert PDF to HTML
        html_elem = HtmlGenerator.read_pdf_convert_to_html(
            input_pdf=pdf_path,
            outdir=output_dir,
            write=True
        )
        
        if html_elem is None:
            print(f"  ❌ Conversion returned None")
            return None
        
        # Get the output HTML file (usually total_pages.html)
        html_file = Path(output_dir, "total_pages.html")
        if not html_file.exists():
            # Try to find any HTML file in the directory
            html_files = list(output_dir.glob("*.html"))
            if html_files:
                html_file = html_files[0]
            else:
                print(f"  ❌ No HTML file found in {output_dir}")
                return None
        
        print(f"  ✅ Converted to HTML: {html_file}")
        return html_file
        
    except Exception as e:
        print(f"  ❌ Error converting PDF to HTML: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_pdf_url(base_url, pdf_patterns):
    """Try multiple PDF URL patterns to find the correct one"""
    for pattern in pdf_patterns:
        url = urljoin(base_url, pattern)
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'pdf' in content_type:
                    return url
        except:
            continue
    return None


def process_pdf_annex(annex_info):
    """Download PDF annex and convert to HTML"""
    report = annex_info["report"]
    annex = annex_info["annex"]
    annex_type = annex_info["type"]
    pdf_patterns = annex_info["pdf_patterns"]
    
    # Create output directory
    output_dir = BASE_OUTPUT_DIR / report / f"{annex}-{annex_type}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # PDF URL
    base_url = BASE_URLS.get(report)
    if not base_url:
        print(f"❌ No base URL found for {report}")
        return False
    
    # Try to find the correct PDF URL
    print(f"\n{'='*80}")
    print(f"Processing: {report.upper()} - {annex} ({annex_type})")
    print(f"Base URL: {base_url}")
    print(f"Trying {len(pdf_patterns)} URL patterns...")
    print(f"{'='*80}")
    
    # Try checking the annex HTML page for PDF links first
    annex_html_url = f"https://www.ipcc.ch/report/ar6/{report}/annex/{annex_type}/"
    pdf_url = find_pdf_url(base_url, pdf_patterns, annex_html_url)
    
    if not pdf_url:
        print(f"  ❌ Could not find PDF URL automatically")
        print(f"  Please check manually at: {annex_html_url}")
        print(f"  Or provide the PDF URL directly")
        return False
    
    # Temporary PDF path
    pdf_filename = pdf_url.split('/')[-1]
    temp_pdf = output_dir / pdf_filename
    
    # Download PDF
    success, file_size = download_pdf(pdf_url, temp_pdf)
    if not success:
        return False
    
    # Convert PDF to HTML
    html_file = convert_pdf_to_html(temp_pdf, output_dir)
    if not html_file:
        return False
    
    # Rename to standard name: annex-<roman>-<type>.html
    final_html = output_dir / f"{annex}-{annex_type}.html"
    if html_file != final_html:
        html_file.rename(final_html)
        print(f"  ✅ Renamed to: {final_html}")
    
    # Clean up PDF if desired (optional)
    # temp_pdf.unlink()
    
    return True


def get_file_info(file_path):
    """Get file size and type information"""
    if not file_path.exists():
        return None, None
    
    size = file_path.stat().st_size
    
    # Determine file type
    if file_path.suffix == '.html':
        # Check if it's a valid HTML file with content
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1000)
                if b'<html' in content.lower() or b'<!doctype' in content.lower():
                    # Check if it has actual content (not just navigation)
                    if size > 10000:  # More than 10KB likely has content
                        return size, "HTML (with content)"
                    else:
                        return size, "HTML (navigation only)"
        except:
            pass
        return size, "HTML"
    elif file_path.suffix == '.pdf':
        return size, "PDF"
    else:
        return size, file_path.suffix[1:].upper()


def generate_status_table():
    """Generate a table showing file sizes and types for all annexes"""
    print("\n" + "="*80)
    print("AR6 Annexes Status Table")
    print("="*80)
    
    # All annexes (including PDF-only and HTML ones)
    all_annexes = [
        {"report": "wg1", "annex": "annex-i", "type": "glossary"},
        {"report": "wg1", "annex": "annex-ii", "type": "acronyms"},
        {"report": "wg2", "annex": "annex-ii", "type": "glossary"},
        {"report": "wg3", "annex": "annex-i", "type": "glossary"},
        {"report": "wg3", "annex": "annex-ii", "type": "acronyms"},
        {"report": "syr", "annex": "annex-i", "type": "glossary"},
        {"report": "syr", "annex": "annex-ii", "type": "acronyms"},
        {"report": "syr", "annex": "annexes-and-index", "type": "combined"},
    ]
    
    table_data = []
    
    for annex_info in all_annexes:
        report = annex_info["report"]
        annex = annex_info["annex"]
        annex_type = annex_info["type"]
        
        annex_dir = BASE_OUTPUT_DIR / report / f"{annex}-{annex_type}"
        
        # Check for HTML file
        html_file = annex_dir / f"{annex}-{annex_type}.html"
        if not html_file.exists():
            # Check for other HTML files
            html_files = list(annex_dir.glob("*.html"))
            if html_files:
                html_file = html_files[0]
        
        # Check for PDF file
        pdf_files = list(annex_dir.glob("*.pdf"))
        pdf_file = pdf_files[0] if pdf_files else None
        
        # Get file info
        html_size, html_type = get_file_info(html_file) if html_file.exists() else (None, None)
        pdf_size, pdf_type = get_file_info(pdf_file) if pdf_file else (None, None)
        
        # Format sizes
        def format_size(size):
            if size is None:
                return "N/A"
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        
        table_data.append({
            "Report": report.upper(),
            "Annex": annex.replace("annex-", "").upper(),
            "Type": annex_type.title(),
            "HTML File": html_file.name if html_file.exists() else "None",
            "HTML Size": format_size(html_size),
            "HTML Type": html_type or "N/A",
            "PDF File": pdf_file.name if pdf_file else "None",
            "PDF Size": format_size(pdf_size),
            "PDF Type": pdf_type or "N/A",
        })
    
    # Print table
    print(f"\n{'Report':<8} {'Annex':<8} {'Type':<12} {'HTML File':<30} {'HTML Size':<12} {'HTML Type':<20} {'PDF File':<30} {'PDF Size':<12} {'PDF Type':<15}")
    print("-" * 150)
    
    for row in table_data:
        print(f"{row['Report']:<8} {row['Annex']:<8} {row['Type']:<12} {row['HTML File']:<30} {row['HTML Size']:<12} {row['HTML Type']:<20} {row['PDF File']:<30} {row['PDF Size']:<12} {row['PDF Type']:<15}")
    
    return table_data


def main():
    """Main entry point"""
    print("="*80)
    print("AR6 PDF Annexes Download and Conversion")
    print("="*80)
    print(f"Output Directory: {BASE_OUTPUT_DIR}")
    print(f"PDF-only Annexes: {len(PDF_ONLY_ANNEXES)}")
    print()
    
    success_count = 0
    fail_count = 0
    
    # Process PDF-only annexes
    for annex_info in PDF_ONLY_ANNEXES:
        if process_pdf_annex(annex_info):
            success_count += 1
        else:
            fail_count += 1
    
    # Generate status table
    table_data = generate_status_table()
    
    # Summary
    print("\n" + "="*80)
    print("Download Summary")
    print("="*80)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Total: {len(PDF_ONLY_ANNEXES)}")
    print()
    print(f"Files saved to: {BASE_OUTPUT_DIR}")
    print()
    print("Next Steps:")
    print("1. Verify converted HTML files")
    print("2. Add semantic IDs using IPCCGatsby.add_ids()")
    print("3. Add Wikimedia IDs (Wikidata/Wiktionary) to terms")


if __name__ == "__main__":
    main()

