#!/usr/bin/env python3
"""
Ingest PDF files into Breward2023 corpus using AmiCorpus.ingest_files().
STYLE: No top-level or pipeline files. Uses only AmiCorpus methods.
"""

import sys
from pathlib import Path

# Note: amilib should be installed with 'pip install -e .' for scripts to work properly

from corpus_module.corpus import AmiCorpus

def main():
    # Set up paths (comma-separated Path construction)
    source_dir = Path("test", "resources", "corpus", "breward2025")
    corpus_dir = Path("test", "resources", "corpus", "breward2023_corpus")
    
    # Construct AmiCorpus (will create directory if needed)
    corpus = AmiCorpus(topdir=corpus_dir, mkdir=True)
    
    # Ingest PDF files using the new method
    print(f"Ingesting PDF files from {source_dir} into {corpus_dir}")
    
    ingested_files = corpus.ingest_files(
        source_dir=source_dir,
        file_pattern="*.pdf",
        target_container="files",
        file_type="pdf"
    )
    
    print(f"\nIngestion complete. {len(ingested_files)} files ingested.")
    for file_path in sorted(ingested_files):
        print(f"  - {file_path.name}")

if __name__ == "__main__":
    main() 