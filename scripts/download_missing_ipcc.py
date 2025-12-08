#!/usr/bin/env python3
"""
Download Missing IPCC Components

Downloads missing SPM/TS documents and SYR annexes.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.ipcc_classes import IPCCGatsby
from test.ipcc_constants import WG1_URL, WG2_URL, WG3_URL, SYR_URL
from test.resources import Resources

BASE_OUTPUT_DIR = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")

# Missing components to download
MISSING_COMPONENTS = [
    {"report": "wg1", "component": "summary-for-policymakers", "url": WG1_URL, "name": "SPM"},
    {"report": "wg1", "component": "technical-summary", "url": WG1_URL, "name": "TS"},
    {"report": "wg2", "component": "summary-for-policymakers", "url": WG2_URL, "name": "SPM"},
    {"report": "wg2", "component": "technical-summary", "url": WG2_URL, "name": "TS"},
    {"report": "wg3", "component": "summary-for-policymakers", "url": WG3_URL, "name": "SPM"},
    {"report": "wg3", "component": "technical-summary", "url": WG3_URL, "name": "TS"},
    {"report": "syr", "component": "summary-for-policymakers", "url": SYR_URL, "name": "SPM"},
    {"report": "syr", "component": "technical-summary", "url": SYR_URL, "name": "TS"},
]

# SYR Annexes (may need PDF download)
SYR_ANNEXES = [
    {"report": "syr", "annex": "annex-i", "type": "glossary", "name": "Annex I - Glossary"},
    {"report": "syr", "annex": "annex-ii", "type": "acronyms", "name": "Annex II - Acronyms"},
]


def download_component(component_info):
    """Download a component (SPM/TS)"""
    report = component_info["report"]
    component = component_info["component"]
    wg_url = component_info["url"]
    name = component_info["name"]
    
    print(f"\n{'='*80}")
    print(f"Downloading: {report.upper()} - {name}")
    print(f"Component: {component}")
    print(f"URL: {wg_url}")
    print(f"{'='*80}")
    
    # Create publisher instance
    publisher = IPCCGatsby()
    
    # Check if already exists (in the correct location)
    final_dir = BASE_OUTPUT_DIR / report / component
    html_with_ids = final_dir / "html_with_ids.html"
    if html_with_ids.exists() and html_with_ids.stat().st_size > 10000:
        print(f"  ✅ Already exists: {html_with_ids.name} ({html_with_ids.stat().st_size / 1024:.1f}KB)")
        return True
    
    try:
        # Use download_save_chapter directly to avoid path bug in download_clean_chapter
        from test.ipcc_classes import IPCC
        
        # Create output directory
        final_dir.mkdir(parents=True, exist_ok=True)
        
        # Download raw file
        IPCC.download_save_chapter(report, component, wg_url, outdir=BASE_OUTPUT_DIR, sleep=1)
        
        # Files are written to BASE_OUTPUT_DIR/report/component/
        raw_file = final_dir / f"{publisher.raw_filename}.html"
        
        if not raw_file.exists() or raw_file.stat().st_size < 50000:
            print(f"  ⚠️  Download produced small or missing file")
            return False
        
        # Process the file
        html_elem = publisher.remove_unnecessary_markup(raw_file)
        if html_elem is None:
            print(f"  ⚠️  Failed to process markup")
            return False
        
        # Write cleaned file
        de_gatsby_file = final_dir / f"de_{publisher.base_filename}.html"
        from amilib.ami_html import HtmlLib
        HtmlLib.write_html_file(html_elem, outfile=de_gatsby_file, debug=False)
        
        # Add IDs
        html_ids_file, idfile, parafile = publisher.add_ids(
            de_gatsby_file, final_dir, assert_exist=True,
            min_id_sizs=10, min_para_size=10
        )
        
        # Check if download was successful
        if html_with_ids.exists() and html_with_ids.stat().st_size > 10000:
            print(f"  ✅ Successfully downloaded: {html_with_ids.name} ({html_with_ids.stat().st_size / 1024:.1f}KB)")
            return True
        else:
            print(f"  ⚠️  Downloaded but file is small")
            return False
            
    except Exception as e:
        print(f"  ❌ Error downloading {name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def download_syr_annex(annex_info):
    """Download SYR annex (try HTML first, then PDF)"""
    report = annex_info["report"]
    annex = annex_info["annex"]
    annex_type = annex_info["type"]
    name = annex_info["name"]
    
    print(f"\n{'='*80}")
    print(f"Downloading: {report.upper()} - {name}")
    print(f"{'='*80}")
    
    # Create output directory
    output_dir = BASE_OUTPUT_DIR / report / f"{annex}-{annex_type}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already exists
    html_files = list(output_dir.glob("*.html"))
    pdf_files = list(output_dir.glob("*.pdf"))
    
    if html_files:
        main_html = None
        for html_file in html_files:
            if html_file.stat().st_size > 10000:
                main_html = html_file
                break
        
        if main_html:
            print(f"  ✅ Already exists: {main_html.name} ({main_html.stat().st_size / 1024:.1f}KB)")
            return True
    
    # Try HTML download first
    try:
        annex_url = f"{SYR_URL}annex/{annex_type}/"
        print(f"  Trying HTML download from: {annex_url}")
        
        publisher = IPCCGatsby()
        publisher.download_clean_chapter(
            chap=f"annex/{annex_type}",
            minsize=50000,
            outdir=output_dir,
            report=report,
            wg_url=SYR_URL
        )
        
        # Check if successful
        html_files = list(output_dir.glob("*.html"))
        for html_file in html_files:
            if html_file.stat().st_size > 10000:
                print(f"  ✅ Successfully downloaded HTML: {html_file.name} ({html_file.stat().st_size / 1024:.1f}KB)")
                return True
        
        print(f"  ⚠️  HTML download produced small files, trying PDF...")
        
    except Exception as e:
        print(f"  ⚠️  HTML download failed: {e}")
        print(f"  Trying PDF download...")
    
    # Try PDF download
    try:
        from scripts.download_pdf_annexes import download_pdf, convert_pdf_to_html
        
        # Try common PDF URL patterns
        base_url = "https://www.ipcc.ch/report/ar6/syr/downloads/report/"
        pdf_patterns = [
            f"IPCC_AR6_SYR_AnnexI.pdf",  # Annex I
            f"IPCC_AR6_SYR_Annex-II.pdf",  # Annex II
            f"IPCC_AR6_SYR_Annex_I.pdf",
            f"IPCC_AR6_SYR_Annex_II.pdf",
        ]
        
        pdf_url = None
        for pattern in pdf_patterns:
            test_url = base_url + pattern
            try:
                import requests
                response = requests.head(test_url, timeout=5)
                if response.status_code == 200:
                    pdf_url = test_url
                    print(f"  Found PDF: {pdf_url}")
                    break
            except:
                continue
        
        if not pdf_url:
            print(f"  ❌ Could not find PDF URL")
            return False
        
        # Download PDF
        pdf_file = output_dir / pdf_url.split('/')[-1]
        success, file_size = download_pdf(pdf_url, pdf_file)
        if not success:
            print(f"  ❌ Failed to download PDF")
            return False
        
        print(f"  ✅ Downloaded PDF: {pdf_file.name} ({file_size / 1024:.1f}KB)")
        
        # Convert to HTML
        html_file = convert_pdf_to_html(pdf_file, output_dir)
        if html_file and html_file.exists() and html_file.stat().st_size > 10000:
            # Rename to standard name
            final_html = output_dir / f"{annex}-{annex_type}.html"
            if html_file != final_html:
                html_file.rename(final_html)
            print(f"  ✅ Converted to HTML: {final_html.name} ({final_html.stat().st_size / 1024:.1f}KB)")
            return True
        else:
            print(f"  ⚠️  PDF conversion produced small file")
            return False
            
    except Exception as e:
        print(f"  ❌ Error downloading PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Download all missing components"""
    print("\n" + "="*80)
    print("DOWNLOADING MISSING IPCC COMPONENTS")
    print("="*80)
    
    # Download SPM/TS
    print("\n" + "="*80)
    print("PHASE 1: Downloading SPM and TS documents")
    print("="*80)
    
    results_spm_ts = []
    for component_info in MISSING_COMPONENTS:
        success = download_component(component_info)
        results_spm_ts.append({
            "report": component_info["report"],
            "name": component_info["name"],
            "success": success
        })
    
    # Download SYR Annexes
    print("\n" + "="*80)
    print("PHASE 2: Downloading SYR Annexes")
    print("="*80)
    
    results_annexes = []
    for annex_info in SYR_ANNEXES:
        success = download_syr_annex(annex_info)
        results_annexes.append({
            "report": annex_info["report"],
            "name": annex_info["name"],
            "success": success
        })
    
    # Summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    
    print("\nSPM/TS Downloads:")
    for result in results_spm_ts:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['report'].upper()} - {result['name']}")
    
    print("\nSYR Annex Downloads:")
    for result in results_annexes:
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {result['name']}")
    
    total = len(results_spm_ts) + len(results_annexes)
    successful = sum(1 for r in results_spm_ts + results_annexes if r["success"])
    
    print(f"\nTotal: {successful}/{total} successful downloads")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

