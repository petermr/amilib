#!/usr/bin/env python3
"""
Generate AR6 Annexes Status Table

Creates a table showing file sizes and types for all AR6 annexes.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources

BASE_OUTPUT_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")


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
        return size, file_path.suffix[1:].upper() if file_path.suffix else "Unknown"


def format_size(size):
    """Format file size in human-readable format"""
    if size is None:
        return "N/A"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def generate_status_table():
    """Generate a table showing file sizes and types for all annexes"""
    print("\n" + "="*100)
    print("AR6 Annexes Status Table")
    print("="*100)
    
    # All annexes
    all_annexes = [
        {"report": "wg1", "annex": "annex-i", "type": "glossary"},
        {"report": "wg1", "annex": "annex-ii", "type": "acronyms"},
        {"report": "wg2", "annex": "annex-ii", "type": "glossary"},
        {"report": "wg3", "annex": "annex-i", "type": "glossary"},
        {"report": "wg3", "annex": "annex-ii", "type": "definitions"},
        {"report": "wg3", "annex": "annex-vi", "type": "acronyms"},
        {"report": "syr", "annex": "annex-i", "type": "glossary"},
        {"report": "syr", "annex": "annex-ii", "type": "acronyms"},
        {"report": "syr", "annex": "annexes-and-index", "type": "combined"},
    ]
    
    table_data = []
    
    for annex_info in all_annexes:
        report = annex_info["report"]
        annex = annex_info["annex"]
        annex_type = annex_info["type"]
        
        # Handle special case for "annexes-and-index" which is both annex name and type
        if annex == "annexes-and-index" and annex_type == "combined":
            annex_dir = BASE_OUTPUT_DIR / report / annex
        else:
            annex_dir = BASE_OUTPUT_DIR / report / f"{annex}-{annex_type}"
        
        # Check for HTML files
        html_files = list(annex_dir.glob("*.html")) if annex_dir.exists() else []
        
        # Check for main HTML file (prefer annex-<roman>-<type>.html, then any HTML)
        main_html = None
        target_html = annex_dir / f"{annex}-{annex_type}.html"
        if target_html.exists():
            main_html = target_html
        elif html_files:
            # Prefer html_with_ids.html, then total_pages.html (from PDF conversion), then de_gatsby.html, then gatsby_raw.html
            for preferred in ["html_with_ids.html", "total_pages.html", "de_gatsby.html", "gatsby_raw.html"]:
                preferred_file = annex_dir / preferred
                if preferred_file.exists():
                    main_html = preferred_file
                    break
            if not main_html:
                main_html = html_files[0]
        
        # Check for PDF files (also check parent directory for combined PDFs)
        pdf_files = list(annex_dir.glob("*.pdf")) if annex_dir.exists() else []
        if not pdf_files and annex_dir.exists():
            # Check parent directory for combined annexes PDFs
            parent_pdfs = list(annex_dir.parent.glob("*.pdf"))
            pdf_files = parent_pdfs
        pdf_file = pdf_files[0] if pdf_files else None
        
        # Get file info
        html_size, html_type = get_file_info(main_html) if main_html else (None, None)
        pdf_size, pdf_type = get_file_info(pdf_file) if pdf_file else (None, None)
        
        # Get all file sizes for summary
        all_files = []
        if main_html:
            all_files.append(("HTML", main_html.name, html_size, html_type))
        if pdf_file:
            all_files.append(("PDF", pdf_file.name, pdf_size, pdf_type))
        
        table_data.append({
            "Report": report.upper(),
            "Annex": annex.replace("annex-", "").upper().replace("-", " "),
            "Type": annex_type.title(),
            "HTML File": main_html.name if main_html else "None",
            "HTML Size": format_size(html_size),
            "HTML Type": html_type or "N/A",
            "PDF File": pdf_file.name if pdf_file else "None",
            "PDF Size": format_size(pdf_size),
            "PDF Type": pdf_type or "N/A",
            "Status": "✅" if (html_size and html_size > 10000) or pdf_file else "❌",
        })
    
    # Print table
    print(f"\n{'Report':<8} {'Annex':<15} {'Type':<12} {'Status':<6} {'HTML File':<30} {'HTML Size':<12} {'HTML Type':<20} {'PDF File':<30} {'PDF Size':<12} {'PDF Type':<15}")
    print("-" * 150)
    
    for row in table_data:
        print(f"{row['Report']:<8} {row['Annex']:<15} {row['Type']:<12} {row['Status']:<6} {row['HTML File']:<30} {row['HTML Size']:<12} {row['HTML Type']:<20} {row['PDF File']:<30} {row['PDF Size']:<12} {row['PDF Type']:<15}")
    
    # Summary
    print("\n" + "="*100)
    print("Summary")
    print("="*100)
    total = len(table_data)
    with_html = sum(1 for row in table_data if row['HTML File'] != 'None' and row['HTML Size'] != 'N/A' and 'navigation' not in row['HTML Type'])
    with_pdf = sum(1 for row in table_data if row['PDF File'] != 'None')
    missing = sum(1 for row in table_data if row['Status'] == '❌')
    
    print(f"Total Annexes: {total}")
    print(f"With HTML Content: {with_html}")
    print(f"With PDF Files: {with_pdf}")
    print(f"Missing/Incomplete: {missing}")
    
    return table_data


if __name__ == "__main__":
    generate_status_table()

