#!/usr/bin/env python3
"""
Add paragraph IDs to SPM and TS documents.

Processes all SPM/TS documents for WG1/2/3 and adds paragraph IDs
to achieve 95%+ coverage.

After fixing create_and_add_id() method, this script re-runs
the ID generation process on cleaned HTML files.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test.ipcc_classes import IPCCGatsby
from test.resources import Resources
from test.ipcc_constants import HTML_WITH_IDS, ID_LIST, PARA_LIST

# Target documents
SPM_TS_DOCUMENTS = [
    {"report": "wg1", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg1", "doc": "technical-summary", "type": "ts"},
    {"report": "wg2", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg2", "doc": "technical-summary", "type": "ts"},
    {"report": "wg3", "doc": "summary-for-policymakers", "type": "spm"},
    {"report": "wg3", "doc": "technical-summary", "type": "ts"},
]


def check_coverage(html_file):
    """Check paragraph ID coverage."""
    from lxml import html
    from lxml.html import HTMLParser
    
    parser = HTMLParser(recover=True)
    tree = html.parse(str(html_file), parser=parser)
    root = tree.getroot()
    
    total_paras = len(root.xpath('.//p'))
    paras_with_ids = len(root.xpath('.//p[@id]'))
    
    return {
        'total': total_paras,
        'with_ids': paras_with_ids,
        'coverage': paras_with_ids * 100 / total_paras if total_paras > 0 else 0
    }


def process_document(report, doc, doc_type, dry_run=False):
    """Process a single SPM/TS document."""
    base_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
    doc_dir = base_dir / report / doc
    
    # Find cleaned HTML file
    cleaned_file = doc_dir / "de_gatsby.html"
    if not cleaned_file.exists():
        print(f"⚠️  Skipping {report}/{doc}: de_gatsby.html not found")
        return False
    
    print(f"\n{'='*80}")
    print(f"Processing: {report.upper()} - {doc_type.upper()}")
    print(f"Directory: {doc_dir}")
    print(f"{'='*80}")
    
    # Check current coverage
    existing_ids_file = doc_dir / f"{HTML_WITH_IDS}.html"
    if existing_ids_file.exists():
        coverage = check_coverage(existing_ids_file)
        print(f"Current Coverage: {coverage['with_ids']}/{coverage['total']} ({coverage['coverage']:.1f}%)")
        
        if coverage['coverage'] >= 95 and not dry_run:
            print(f"✅ Already has good coverage, skipping")
            return True
    
    if dry_run:
        print(f"DRY RUN: Would process {cleaned_file}")
        return True
    
    publisher = IPCCGatsby()
    
    # Define output file paths
    html_ids_file = doc_dir / f"{HTML_WITH_IDS}.html"
    idfile = doc_dir / f"{ID_LIST}.html"
    parafile = doc_dir / f"{PARA_LIST}.html"
    
    # Add paragraph IDs (this will use the fixed create_and_add_id method)
    publisher.add_para_ids_and_make_id_list(
        infile=str(cleaned_file),
        idfile=str(idfile),
        outfile=str(html_ids_file),
        parafile=str(parafile)
    )
    
    # Verify coverage
    coverage = check_coverage(html_ids_file)
    print(f"New Coverage: {coverage['with_ids']}/{coverage['total']} ({coverage['coverage']:.1f}%)")
    
    if coverage['coverage'] >= 95:
        print(f"✅ Success! Achieved {coverage['coverage']:.1f}% coverage")
        print(f"   Output file: {html_ids_file}")
        return True
    else:
        print(f"⚠️  Warning: Only {coverage['coverage']:.1f}% coverage (target: 95%+)")
        return False


def main():
    """Process all SPM/TS documents."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add paragraph IDs to SPM/TS documents')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without actually processing')
    parser.add_argument('--report', choices=['wg1', 'wg2', 'wg3'], help='Process specific report only')
    parser.add_argument('--doc-type', choices=['spm', 'ts'], help='Process specific document type only')
    
    args = parser.parse_args()
    
    documents = SPM_TS_DOCUMENTS
    
    if args.report:
        documents = [d for d in documents if d['report'] == args.report]
    
    if args.doc_type:
        documents = [d for d in documents if d['type'] == args.doc_type]
    
    print(f"\nProcessing {len(documents)} documents")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    results = []
    for doc_info in documents:
        success = process_document(
            report=doc_info["report"],
            doc=doc_info["doc"],
            doc_type=doc_info["type"],
            dry_run=args.dry_run
        )
        results.append({
            'doc': f"{doc_info['report']}/{doc_info['doc']}",
            'success': success
        })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"Summary")
    print(f"{'='*80}")
    successful = sum(1 for r in results if r['success'])
    print(f"Processed: {successful}/{len(results)} documents")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"  {status} {r['doc']}")


if __name__ == '__main__':
    main()

