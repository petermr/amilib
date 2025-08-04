#!/usr/bin/env python3
"""
Process remaining bioRxiv PDFs in background
Uses existing working PDF annotation infrastructure
"""

import subprocess
import time
from pathlib import Path
import sys
import os
import signal

# Note: amilib should be installed with 'pip install -e .' for scripts to work properly

from scripts.markup_climate_pdfs_with_glossary import ClimatePDFProcessor

def run_in_background():
    """Run the PDF processing in background"""
    # Find all bioRxiv PDFs (excluding versioned ones)
    pdf_dir = Path("test", "resources", "pdf", "climate_change")
    pdf_files = [f for f in pdf_dir.glob("*bioRxiv.pdf") if not f.name.startswith(('2024.', '2025.'))]
    
    print(f"📚 Found {len(pdf_files)} bioRxiv PDFs")
    
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
    
    # Test with ONE file first
    print(f"\n🧪 TESTING with ONE file first:")
    test_file = unannotated_files[0]
    print(f"📄 Testing with: {test_file.name}")
    
    # Run the processing in background
    cmd = [
        "python3", "scripts/markup_climate_pdfs_with_glossary.py",
        "--single", str(test_file)
    ]
    
    print(f"🚀 Starting background process: {' '.join(cmd)}")
    
    # Start background process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ Background process started with PID: {process.pid}")
    print(f"📝 Output will be logged to: temp/biorxiv_processing.log")
    
    # Save PID for later reference
    with open("temp/biorxiv_process.pid", "w") as f:
        f.write(str(process.pid))
    
    return process

def check_status():
    """Check the status of background processing"""
    try:
        with open("temp/biorxiv_process.pid", "r") as f:
            pid = int(f.read().strip())
        
        # Check if process is still running
        try:
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            print(f"🔄 Background process (PID: {pid}) is still running")
            return True
        except OSError:
            print(f"✅ Background process (PID: {pid}) has completed")
            return False
    except FileNotFoundError:
        print("❌ No background process found")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process bioRxiv PDFs in background")
    parser.add_argument("--start", action="store_true", help="Start background processing")
    parser.add_argument("--status", action="store_true", help="Check status of background processing")
    parser.add_argument("--stop", action="store_true", help="Stop background processing")
    
    args = parser.parse_args()
    
    if args.start:
        run_in_background()
    elif args.status:
        check_status()
    elif args.stop:
        try:
            with open("temp/biorxiv_process.pid", "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)  # Send SIGTERM first
            print(f"🛑 Stopped background process (PID: {pid})")
        except FileNotFoundError:
            print("❌ No background process found")
        except OSError:
            print(f"❌ Could not stop background process (PID: {pid})")
    else:
        # Default: start background processing
        run_in_background()

if __name__ == "__main__":
    main() 