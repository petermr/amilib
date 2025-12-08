#!/usr/bin/env python3
"""
Process IPCC HTML Files to Add Semantic IDs

This script processes all IPCC HTML components to ensure:
1. Proper nested section structure
2. Semantic IDs for all sections and paragraphs
3. Appropriate ID prefixes based on document type (spm, ts, gloss, acr, etc.)

Usage:
    python scripts/process_ipcc_html_ids.py [--report REPORT] [--component COMPONENT] [--dry-run]
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.ipcc_classes import IPCCGatsby, IPCCWordpress
from test.ipcc_constants import HTML_WITH_IDS, DE_GATSBY, DE_WORDPRESS
from test.resources import Resources
import lxml.etree as ET
from lxml.etree import HTMLParser
from amilib.ami_html import HtmlLib

BASE_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")


def identify_document_type(file_path):
    """Identify document type from file path"""
    path_str = str(file_path).lower()
    
    if 'spm' in path_str or 'summary-for-policymakers' in path_str:
        return 'spm'
    elif 'ts' in path_str or 'technical-summary' in path_str:
        return 'ts'
    elif 'glossary' in path_str or 'annex-i-glossary' in path_str:
        return 'glossary'
    elif 'acronym' in path_str or 'annex-ii-acronyms' in path_str or 'annex-vi-acronyms' in path_str:
        return 'acronym'
    elif 'definition' in path_str or 'annex-ii-definitions' in path_str:
        return 'definition'
    elif 'chapter' in path_str:
        return 'chapter'
    elif 'faq' in path_str or 'frequently-asked' in path_str:
        return 'faq'
    elif 'executive-summary' in path_str:
        return 'executive-summary'
    elif 'references' in path_str:
        return 'references'
    else:
        return 'unknown'


def get_id_prefix(doc_type, report=None):
    """Get ID prefix based on document type"""
    prefixes = {
        'spm': 'spm',
        'ts': 'ts',
        'glossary': 'gloss',
        'acronym': 'acr',
        'definition': 'def',
        'faq': 'faq',
        'executive-summary': 'executive-summary',
        'references': 'references',
        'chapter': '',  # Chapters use numeric IDs
    }
    return prefixes.get(doc_type, '')


def find_html_files_to_process(base_dir=BASE_DIR, report=None, component=None):
    """Find all HTML files that need processing"""
    files_to_process = []
    
    for report_dir in base_dir.iterdir():
        if not report_dir.is_dir():
            continue
        
        report_name = report_dir.name
        if report and report_name != report:
            continue
        
        # Check for SPM/TS
        for spm_ts in ['summary-for-policymakers', 'technical-summary', 'spm', 'ts']:
            spm_ts_dir = report_dir / spm_ts
            if spm_ts_dir.exists():
                if component and spm_ts not in component:
                    continue
                html_file = spm_ts_dir / f"{HTML_WITH_IDS}.html"
                de_file = spm_ts_dir / f"de_{DE_GATSBY}.html" if (report_dir / 'wg1').exists() else spm_ts_dir / f"de_{DE_WORDPRESS}.html"
                
                if html_file.exists():
                    files_to_process.append({
                        'type': 'spm' if 'spm' in spm_ts or 'summary' in spm_ts else 'ts',
                        'report': report_name,
                        'component': spm_ts,
                        'html_file': html_file,
                        'de_file': de_file if de_file.exists() else None,
                        'dir': spm_ts_dir,
                    })
        
        # Check for chapters
        for chapter_dir in sorted(report_dir.glob("Chapter*")):
            if component and chapter_dir.name not in component:
                continue
            html_file = chapter_dir / f"{HTML_WITH_IDS}.html"
            de_file = chapter_dir / f"de_{DE_GATSBY}.html"
            
            if html_file.exists():
                files_to_process.append({
                    'type': 'chapter',
                    'report': report_name,
                    'component': chapter_dir.name,
                    'html_file': html_file,
                    'de_file': de_file if de_file.exists() else None,
                    'dir': chapter_dir,
                })
        
        # Check for annexes
        for annex_dir in sorted(report_dir.glob("annex-*")):
            if component and annex_dir.name not in component:
                continue
            
            # Find HTML files in annex directory
            html_files = list(annex_dir.glob("*.html"))
            # Prefer html_with_ids.html, then annex-*.html, then total_pages.html
            html_file = None
            de_file = None
            
            # Check for html_with_ids.html first
            html_with_ids = annex_dir / f"{HTML_WITH_IDS}.html"
            if html_with_ids.exists():
                html_file = html_with_ids
            else:
                # Look for other HTML files that might need processing
                for pattern in ["annex-*.html", "total_pages.html", "*.html"]:
                    matches = list(annex_dir.glob(pattern))
                    # Skip intermediate files
                    matches = [m for m in matches if not any(x in m.name for x in ['page_', 'raw', 'gatsby', 'wordpress'])]
                    if matches:
                        html_file = matches[0]
                        break
            
            # Find de_ file or use html_file as source
            de_files = list(annex_dir.glob("de_*.html"))
            if de_files:
                de_file = de_files[0]
            elif html_file and html_file.name != f"{HTML_WITH_IDS}.html":
                # Use the HTML file as source if no de_ file exists
                de_file = html_file
            
            # Process if we have a file to work with
            if de_file and de_file.exists():
                doc_type = identify_document_type(annex_dir)
                files_to_process.append({
                    'type': doc_type,
                    'report': report_name,
                    'component': annex_dir.name,
                    'html_file': html_file if html_file and html_file.exists() else None,
                    'de_file': de_file,
                    'dir': annex_dir,
                })
        
        # Check for glossaries (SR15, SROCC)
        glossary_dir = report_dir / 'glossary'
        if glossary_dir.exists():
            if component and 'glossary' not in component:
                continue
            html_file = glossary_dir / f"{HTML_WITH_IDS}.html"
            de_file = glossary_dir / f"de_{DE_WORDPRESS}.html"
            
            if not html_file.exists() and de_file.exists():
                files_to_process.append({
                    'type': 'glossary',
                    'report': report_name,
                    'component': 'glossary',
                    'html_file': None,
                    'de_file': de_file,
                    'dir': glossary_dir,
                })
    
    return files_to_process


def check_id_coverage(html_file):
    """Check ID coverage in an HTML file"""
    if not html_file or not html_file.exists():
        return None
    
    try:
        tree = ET.parse(str(html_file), HTMLParser())
        paragraphs = tree.xpath('//p[text()]')
        paras_with_ids = tree.xpath('//p[@id]')
        sections = tree.xpath('//div[contains(@class, "h")]')
        sections_with_ids = tree.xpath('//div[contains(@class, "h")][@id]')
        
        # Filter out navigation IDs
        semantic_ids = [
            e.get('id') for e in tree.xpath('//*[@id]')
            if e.get('id') and not e.get('id').startswith(('basic-', 'ref-', 'share-', 'copy-', 'doi', 'dropdown'))
        ]
        
        return {
            'total_paragraphs': len(paragraphs),
            'paragraphs_with_ids': len(paras_with_ids),
            'paragraph_coverage': len(paras_with_ids) / len(paragraphs) * 100 if paragraphs else 0,
            'total_sections': len(sections),
            'sections_with_ids': len(sections_with_ids),
            'section_coverage': len(sections_with_ids) / len(sections) * 100 if sections else 0,
            'semantic_ids_count': len(semantic_ids),
            'sample_ids': semantic_ids[:5],
        }
    except Exception as e:
        return {'error': str(e)}


def process_file(file_info, dry_run=False):
    """Process a single file to add semantic IDs"""
    report = file_info['report']
    component = file_info['component']
    doc_type = file_info['type']
    html_file = file_info['html_file']
    de_file = file_info['de_file']
    dir_path = file_info['dir']
    
    print(f"\n{'='*80}")
    print(f"Processing: {report.upper()} - {component} ({doc_type})")
    print(f"{'='*80}")
    
    # Check current coverage
    if html_file and html_file.exists():
        coverage = check_id_coverage(html_file)
        if coverage:
            print(f"Current Coverage:")
            print(f"  Paragraphs: {coverage['paragraphs_with_ids']}/{coverage['total_paragraphs']} ({coverage['paragraph_coverage']:.1f}%)")
            print(f"  Sections: {coverage['sections_with_ids']}/{coverage['total_sections']} ({coverage['section_coverage']:.1f}%)")
            print(f"  Semantic IDs: {coverage['semantic_ids_count']}")
            
            # Skip if coverage is good
            if coverage['paragraph_coverage'] >= 95 and coverage['section_coverage'] >= 99:
                print(f"  ✅ Already has good coverage, skipping")
                return True
    
    # Determine publisher type
    if report in ['sr15', 'srocc', 'srccl']:
        publisher = IPCCWordpress()
        cleaned_file_pattern = f"de_{DE_WORDPRESS}.html"
    else:
        publisher = IPCCGatsby()
        cleaned_file_pattern = f"de_{DE_GATSBY}.html"
    
    # Find cleaned file
    if not de_file:
        de_file = dir_path / cleaned_file_pattern
        if not de_file.exists():
            # Try alternative patterns
            alt_patterns = ['de_wordpress_styles.html', 'de_gatsby.html', 'wordpress.html', 'gatsby.html']
            for pattern in alt_patterns:
                alt_file = dir_path / pattern
                if alt_file.exists():
                    de_file = alt_file
                    break
    
    if not de_file or not de_file.exists():
        print(f"  ⚠️  No cleaned file found, skipping")
        return False
    
    if dry_run:
        print(f"  [DRY RUN] Would process: {de_file.name}")
        return True
    
    try:
        # Process using existing pipeline
        print(f"  Processing: {de_file.name}")
        
        # Use add_ids method
        html_ids_file, idfile, parafile = publisher.add_ids(
            de_file,
            dir_path,
            assert_exist=False,
            min_id_sizs=10,
            min_html_size=1000,
            min_para_size=10
        )
        
        # Check new coverage
        if html_ids_file.exists():
            new_coverage = check_id_coverage(html_ids_file)
            if new_coverage:
                print(f"  New Coverage:")
                print(f"    Paragraphs: {new_coverage['paragraphs_with_ids']}/{new_coverage['total_paragraphs']} ({new_coverage['paragraph_coverage']:.1f}%)")
                print(f"    Sections: {new_coverage['sections_with_ids']}/{new_coverage['total_sections']} ({new_coverage['section_coverage']:.1f}%)")
                print(f"    Semantic IDs: {new_coverage['semantic_ids_count']}")
                
                if new_coverage['paragraph_coverage'] >= 95:
                    print(f"  ✅ Successfully processed")
                    return True
                else:
                    print(f"  ⚠️  Processed but coverage still low")
                    return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Process IPCC HTML files to add semantic IDs'
    )
    parser.add_argument(
        '--report',
        help='Process specific report (wg1, wg2, wg3, syr, sr15, srocc, srccl)'
    )
    parser.add_argument(
        '--component',
        help='Process specific component (e.g., summary-for-policymakers, Chapter01)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without actually processing'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check coverage, do not process'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("IPCC HTML ID Processing Script")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No files will be modified]")
    
    if args.check_only:
        print("\n[CHECK ONLY MODE - Coverage report only]")
    
    # Find files to process
    files_to_process = find_html_files_to_process(
        base_dir=BASE_DIR,
        report=args.report,
        component=args.component
    )
    
    print(f"\nFound {len(files_to_process)} files to process")
    
    if not files_to_process:
        print("No files found to process")
        return
    
    # Group by type
    by_type = {}
    for file_info in files_to_process:
        doc_type = file_info['type']
        if doc_type not in by_type:
            by_type[doc_type] = []
        by_type[doc_type].append(file_info)
    
    print(f"\nBreakdown by type:")
    for doc_type, files in sorted(by_type.items()):
        print(f"  {doc_type}: {len(files)} files")
    
    # Process files
    results = {
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'errors': [],
    }
    
    for file_info in files_to_process:
        if args.check_only:
            html_file = file_info['html_file']
            if html_file and html_file.exists():
                coverage = check_id_coverage(html_file)
                if coverage:
                    print(f"\n{file_info['report']}/{file_info['component']}:")
                    print(f"  Paragraphs: {coverage['paragraph_coverage']:.1f}%")
                    print(f"  Sections: {coverage['section_coverage']:.1f}%")
            continue
        
        success = process_file(file_info, dry_run=args.dry_run)
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
    
    # Summary
    if not args.check_only:
        print("\n" + "="*80)
        print("PROCESSING SUMMARY")
        print("="*80)
        print(f"Successfully processed: {results['success']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
    
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

