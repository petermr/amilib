#!/usr/bin/env python3
"""
IPCC Data Coverage Summary

Generates a comprehensive summary of IPCC data coverage, indicating:
- What has been scraped (HTML from web)
- What has been converted (PDF to HTML)
- What is missing and needs to be downloaded or converted

Reports covered: WG1, WG2, WG3, SYR, SR15, SROCC, SRCCL
Components: SPM, TS, Chapters, Chapter-boxes, Chapter floats, Cross-Chapter papers,
            Glossary, Acronyms, Definitions
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.resources import Resources

BASE_OUTPUT_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")

# Expected components for each report
EXPECTED_COMPONENTS = {
    "wg1": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 13)),  # Chapters 1-12 (WG1 has 12 chapters total)
        "glossary": "Annex I - Glossary",
        "acronyms": "Annex II - Acronyms",
    },
    "wg2": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 19)),  # Chapters 1-18
        "cross_chapters": "Cross-Chapter Papers",
        "glossary": "Annex II - Glossary",
    },
    "wg3": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 18)),  # Chapters 1-17
        "glossary": "Annex I - Glossary",
        "definitions": "Annex II - Definitions",
        "acronyms": "Annex VI - Acronyms",
    },
    "syr": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary (if applicable)",
        "longer_report": "Longer Report",
        "glossary": "Annex I - Glossary",
        "acronyms": "Annex II - Acronyms",
        "annexes_index": "Annexes and Index",
    },
    "sr15": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 6)),  # Chapters 1-5
        "glossary": "Glossary",
    },
    "srocc": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 7)),  # Chapters 1-6
        "glossary": "Glossary",
    },
    "srccl": {
        "spm": "Summary for Policymakers",
        "ts": "Technical Summary",
        "chapters": list(range(1, 8)),  # Chapters 1-7
    },
}


def get_file_type(file_path):
    """Determine if file is scraped HTML or converted from PDF"""
    if not file_path.exists():
        return None, None
    
    if file_path.suffix == '.pdf':
        return 'PDF', 'PDF'
    
    if file_path.suffix == '.html':
        # Check file size and content to determine source
        size = file_path.stat().st_size
        
        # Read first part of file to check for PDF conversion markers
        try:
            with open(file_path, 'rb') as f:
                content = f.read(2000).decode('utf-8', errors='ignore').lower()
                
            # PDF conversion markers
            pdf_markers = [
                'total_pages.html',
                'page_',
                'pdfplumber',
                'converted from pdf',
            ]
            
            # Scraped HTML markers (Gatsby/WordPress)
            scraped_markers = [
                'gatsby',
                'wordpress',
                'de_gatsby',
                'de_wordpress',
            ]
            
            # Check filename
            filename_lower = file_path.name.lower()
            if 'total_pages' in filename_lower or 'pdf' in filename_lower:
                return 'HTML (PDF converted)', 'PDF→HTML'
            
            # Check content
            if any(marker in content for marker in pdf_markers):
                return 'HTML (PDF converted)', 'PDF→HTML'
            elif any(marker in content or marker in filename_lower for marker in scraped_markers):
                return 'HTML (scraped)', 'Scraped'
            elif size > 10000:  # Substantial content
                return 'HTML (scraped)', 'Scraped'
            else:
                return 'HTML (small)', 'Unknown'
        except:
            return 'HTML', 'Unknown'
    
    return None, None


def check_component(report, component_name, component_path):
    """Check status of a component"""
    status = {
        'name': component_name,
        'path': str(component_path),
        'exists': component_path.exists(),
        'html_files': [],
        'pdf_files': [],
        'scraped': False,
        'converted': False,
        'has_content': False,
        'main_html': None,
        'main_pdf': None,
    }
    
    if not component_path.exists():
        return status
    
    # Find HTML and PDF files
    html_files = list(component_path.glob("*.html"))
    pdf_files = list(component_path.glob("*.pdf"))
    
    status['html_files'] = [f.name for f in html_files]
    status['pdf_files'] = [f.name for f in pdf_files]
    
    # Identify main HTML file (prefer html_with_ids, then annex-*.html, then largest)
    main_html_candidates = []
    for html_file in html_files:
        name_lower = html_file.name.lower()
        size = html_file.stat().st_size
        
        # Skip page_*.raw.html files (intermediate PDF conversion files)
        if 'page_' in name_lower and '.raw.html' in name_lower:
            continue
        
        priority = 0
        if 'html_with_ids' in name_lower:
            priority = 100
        elif component_name.lower().replace(' ', '-') in name_lower or 'annex-' in name_lower:
            priority = 90
        elif 'total_pages' in name_lower:
            priority = 80
        elif 'de_gatsby' in name_lower or 'de_wordpress' in name_lower:
            priority = 70
        elif 'gatsby' in name_lower or 'wordpress' in name_lower:
            priority = 60
        
        main_html_candidates.append((priority, size, html_file))
    
    if main_html_candidates:
        main_html_candidates.sort(key=lambda x: (-x[0], -x[1]))  # Sort by priority then size
        status['main_html'] = main_html_candidates[0][2]
    
    # Identify main PDF file
    if pdf_files:
        status['main_pdf'] = pdf_files[0]  # Take first PDF
    
    # Check for scraped HTML (gatsby_raw, de_gatsby, wordpress, etc.)
    scraped_patterns = ['gatsby_raw', 'de_gatsby', 'wordpress', 'de_wordpress', 'html_with_ids']
    for html_file in html_files:
        name_lower = html_file.name.lower()
        if any(pattern in name_lower for pattern in scraped_patterns):
            status['scraped'] = True
            if html_file.stat().st_size > 10000:  # Substantial content
                status['has_content'] = True
    
    # Check for PDF-converted HTML (total_pages, page_*.raw.html, annex-*.html from PDF)
    converted_patterns = ['total_pages', 'page_', 'annex-i-glossary', 'annex-ii-acronyms', 
                        'annex-ii-definitions', 'annex-vi-acronyms', 'annex-ii-glossary']
    for html_file in html_files:
        name_lower = html_file.name.lower()
        size = html_file.stat().st_size
        
        # Check if it's a PDF conversion artifact
        if any(pattern in name_lower for pattern in ['page_', 'total_pages']):
            status['converted'] = True
            if size > 10000:
                status['has_content'] = True
        
        # Check if it's an annex HTML file (likely from PDF conversion)
        if any(pattern in name_lower for pattern in converted_patterns):
            # Check if there's also a PDF file
            if pdf_files:
                status['converted'] = True
                if size > 10000:
                    status['has_content'] = True
    
    # Check for PDF files
    if pdf_files:
        status['converted'] = True  # Has PDF, may need conversion or already converted
    
    return status


def check_chapters(report, expected_chapters):
    """Check chapter coverage"""
    chapters_status = {}
    report_dir = BASE_OUTPUT_DIR / report
    
    for chapter_num in expected_chapters:
        chapter_name = f"Chapter{chapter_num:02d}"
        chapter_path = report_dir / chapter_name
        chapters_status[chapter_name] = check_component(report, chapter_name, chapter_path)
    
    return chapters_status


def generate_coverage_summary():
    """Generate comprehensive coverage summary"""
    print("\n" + "="*120)
    print("IPCC DATA COVERAGE SUMMARY")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*120)
    
    summary = {
        'scraped': {'components': [], 'chapters': 0},
        'converted': {'components': [], 'chapters': 0},
        'missing': {'components': [], 'chapters': 0},
        'partial': {'components': [], 'chapters': 0},
    }
    
    for report in EXPECTED_COMPONENTS.keys():
        print(f"\n{'='*120}")
        print(f"{report.upper()}")
        print(f"{'='*120}")
        
        report_dir = BASE_OUTPUT_DIR / report
        components = EXPECTED_COMPONENTS[report]
        
        # Check SPM
        if 'spm' in components:
            # Try multiple possible paths
            spm_paths = [
                report_dir / 'summary-for-policymakers',
                report_dir / 'spm' / 'summary-for-policymakers',
                report_dir / 'spm',
            ]
            spm_path = None
            for path in spm_paths:
                if path.exists():
                    spm_path = path
                    break
            if not spm_path:
                spm_path = report_dir / 'summary-for-policymakers'
            status = check_component(report, 'SPM', spm_path)
            print_status('SPM', status, summary)
        
        # Check TS
        if 'ts' in components:
            # Try multiple possible paths
            ts_paths = [
                report_dir / 'technical-summary',
                report_dir / 'ts' / 'technical-summary',
                report_dir / 'ts',
            ]
            ts_path = None
            for path in ts_paths:
                if path.exists():
                    ts_path = path
                    break
            if not ts_path:
                ts_path = report_dir / 'technical-summary'
            status = check_component(report, 'TS', ts_path)
            print_status('TS', status, summary)
        
        # Check Chapters
        if 'chapters' in components:
            chapters_status = check_chapters(report, components['chapters'])
            print(f"\n  Chapters:")
            for chapter_name, status in sorted(chapters_status.items()):
                print_status(chapter_name, status, summary, indent=4)
        
        # Check Cross-Chapter Papers (WG2)
        if 'cross_chapters' in components:
            cross_path = report_dir / 'CrossChapters'
            status = check_component(report, 'Cross-Chapter Papers', cross_path)
            print_status('Cross-Chapter Papers', status, summary)
        
        # Check Glossary
        if 'glossary' in components:
            glossary_paths = [
                report_dir / 'annex-i-glossary',
                report_dir / 'annex-ii-glossary',
                report_dir / 'glossary',
            ]
            found = False
            for glossary_path in glossary_paths:
                if glossary_path.exists():
                    status = check_component(report, 'Glossary', glossary_path)
                    print_status('Glossary', status, summary)
                    found = True
                    break
            if not found:
                status = {'name': 'Glossary', 'exists': False, 'scraped': False, 'converted': False}
                print_status('Glossary', status, summary)
        
        # Check Acronyms
        if 'acronyms' in components:
            acronym_paths = [
                report_dir / 'annex-ii-acronyms',
                report_dir / 'annex-vi-acronyms',
            ]
            found = False
            for acronym_path in acronym_paths:
                if acronym_path.exists():
                    status = check_component(report, 'Acronyms', acronym_path)
                    print_status('Acronyms', status, summary)
                    found = True
                    break
            if not found:
                status = {'name': 'Acronyms', 'exists': False, 'scraped': False, 'converted': False}
                print_status('Acronyms', status, summary)
        
        # Check Definitions (WG3)
        if 'definitions' in components:
            def_path = report_dir / 'annex-ii-definitions'
            status = check_component(report, 'Definitions', def_path)
            print_status('Definitions', status, summary)
        
        # Check Longer Report (SYR)
        if 'longer_report' in components:
            lr_path = report_dir / 'longer-report'
            status = check_component(report, 'Longer Report', lr_path)
            print_status('Longer Report', status, summary)
        
        # Check Annexes and Index (SYR)
        if 'annexes_index' in components:
            annex_path = report_dir / 'annexes-and-index'
            status = check_component(report, 'Annexes and Index', annex_path)
            print_status('Annexes and Index', status, summary)
    
    # Print summary
    print("\n" + "="*120)
    print("OVERALL SUMMARY")
    print("="*120)
    print(f"\nScraped (HTML from web):")
    print(f"  Components: {len(summary['scraped']['components'])}")
    print(f"  Chapters: {summary['scraped']['chapters']}")
    
    print(f"\nConverted (PDF to HTML):")
    print(f"  Components: {len(summary['converted']['components'])}")
    print(f"  Chapters: {summary['converted']['chapters']}")
    
    print(f"\nMissing:")
    print(f"  Components: {len(summary['missing']['components'])}")
    print(f"  Chapters: {summary['missing']['chapters']}")
    
    print(f"\nPartial (needs completion):")
    print(f"  Components: {len(summary['partial']['components'])}")
    print(f"  Chapters: {summary['partial']['chapters']}")
    
    # Alert for missing components
    print("\n" + "="*120)
    print("⚠️  COMPONENTS NEEDING DOWNLOAD OR CONVERSION")
    print("="*120)
    
    if summary['missing']['components']:
        print("\nMissing Components:")
        for comp in summary['missing']['components']:
            print(f"  ❌ {comp}")
    
    if summary['missing']['chapters'] > 0:
        print(f"\nMissing Chapters: {summary['missing']['chapters']} chapters")
    
    if summary['partial']['components']:
        print("\nPartial Components (need completion):")
        for comp in summary['partial']['components']:
            print(f"  ⚠️  {comp}")
    
    if not summary['missing']['components'] and summary['missing']['chapters'] == 0:
        print("\n✅ All expected components are present!")
    
    return summary


def print_status(name, status, summary, indent=2):
    """Print status of a component"""
    prefix = " " * indent
    
    if not status.get('exists', False):
        print(f"{prefix}❌ {name}: MISSING")
        if 'Chapter' in name:
            summary['missing']['chapters'] += 1
        else:
            summary['missing']['components'].append(f"{name}")
        return
    
    sources = []
    if status.get('scraped', False):
        sources.append("Scraped")
    if status.get('converted', False):
        sources.append("PDF→HTML")
    
    if not sources:
        print(f"{prefix}⚠️  {name}: EXISTS but no clear source")
        if 'Chapter' in name:
            summary['partial']['chapters'] += 1
        else:
            summary['partial']['components'].append(f"{name}")
        return
    
    # Check if has substantial content
    has_content = status.get('has_content', False)
    main_html = status.get('main_html')
    main_pdf = status.get('main_pdf')
    
    if main_html:
        size = main_html.stat().st_size
        if size > 10000:
            has_content = True
    
    if has_content or main_pdf:
        source_str = " + ".join(sources)
        print(f"{prefix}✅ {name}: {source_str}", end="")
        if main_html:
            size_str = f"{main_html.stat().st_size / 1024:.1f}KB" if main_html.stat().st_size < 1024*1024 else f"{main_html.stat().st_size / (1024*1024):.1f}MB"
            print(f" ({main_html.name}, {size_str})")
        else:
            print()
        
        if 'Chapter' in name:
            if 'Scraped' in sources:
                summary['scraped']['chapters'] += 1
            if 'PDF→HTML' in sources:
                summary['converted']['chapters'] += 1
        else:
            if 'Scraped' in sources:
                summary['scraped']['components'].append(f"{name}")
            if 'PDF→HTML' in sources:
                summary['converted']['components'].append(f"{name}")
    else:
        print(f"{prefix}⚠️  {name}: {sources[0]} but minimal content")
        if 'Chapter' in name:
            summary['partial']['chapters'] += 1
        else:
            summary['partial']['components'].append(f"{name}")


if __name__ == "__main__":
    generate_coverage_summary()

