#!/usr/bin/env python3
"""
Script to extract significant phrases from the breward2023 corpus using KeyBERT.
"""

import json
import sys
from pathlib import Path

# Add the amilib directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from corpus_module.corpus import AmiCorpus


def main():
    """Extract significant phrases from the breward2023 corpus using KeyBERT."""
    print("🔍 KeyBERT Phrase Extraction from Breward2023 Corpus")
    print("=" * 60)
    
    # Set up paths
    corpus_dir = Path("test", "resources", "corpus", "breward2023_corpus")
    output_dir = Path("temp", "phrase_extraction_keybert")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create or load corpus
    print(f"📁 Creating corpus at: {corpus_dir}")
    corpus = AmiCorpus(topdir=corpus_dir, mkdir=True)
    
    # Set up directory structure if needed
    data_container = None
    for container in corpus.ami_container.child_containers:
        if container.file.name == "data":
            data_container = container
            break
    
    if not data_container:
        data_container = corpus.ami_container.create_corpus_container(
            "data", bib_type="bagit_data", mkdir=True
        )
    
    # Create subdirectories
    data_container.create_corpus_container("files", bib_type="files", mkdir=True)
    data_container.create_corpus_container("indices", bib_type="indices", mkdir=True)
    data_container.create_corpus_container("metadata", bib_type="metadata", mkdir=True)
    
    # 2. Check for existing files
    print(f"📁 Checking for existing files in corpus...")
    files_container = None
    for container in corpus.ami_container.child_containers:
        if container.file.name == "data":
            for child in container.child_containers:
                if child.file.name == "files":
                    files_container = child
                    break
            break
    
    if not files_container:
        print("❌ No 'data/files' container found. Please ingest files first.")
        return {}
    
    existing_files = list(files_container.file.glob("*.pdf"))
    print(f"✅ Found {len(existing_files)} existing PDF files")
    
    # 3. Extract significant phrases using KeyBERT
    print("\n🔍 Extracting significant phrases using KeyBERT...")
    
    # Extract with different KeyBERT configurations
    extraction_configs = [
        {
            "name": "keybert_200_terms",
            "max_phrases": 200,
            "min_word_length": 3,
            "diversity": 0.7
        },
        {
            "name": "keybert_high_diversity",
            "max_phrases": 100,
            "min_word_length": 3,
            "diversity": 0.9
        },
        {
            "name": "keybert_low_diversity",
            "max_phrases": 100,
            "min_word_length": 3,
            "diversity": 0.3
        }
    ]
    
    all_results = {}
    
    for config in extraction_configs:
        print(f"\n📊 Configuration: {config['name']}")
        print(f"   - Max phrases: {config['max_phrases']}")
        print(f"   - Min word length: {config['min_word_length']}")
        print(f"   - Diversity: {config['diversity']}")
        
        phrases = corpus.extract_significant_phrases_keybert(
            file_pattern="*.pdf",
            max_phrases=config["max_phrases"],
            min_word_length=config["min_word_length"],
            diversity=config["diversity"]
        )
        
        print(f"   ✅ Extracted {len(phrases)} phrases")
        
        # Save results
        output_file = output_dir / f"phrases_{config['name']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(phrases, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved to: {output_file}")
        
        all_results[config["name"]] = phrases
        
        # Show top phrases
        if phrases:
            print("   📋 Top 10 phrases:")
            for i, phrase_data in enumerate(phrases[:10]):
                print(f"      {i+1:2d}. '{phrase_data['phrase']}' (score: {phrase_data['keybert_score']:.3f}, freq: {phrase_data['frequency']})")
    
    # 4. Create summary report
    print(f"\n📈 Summary Report")
    print("-" * 40)
    
    summary_file = output_dir / "extraction_summary.json"
    summary = {
        "corpus_info": {
            "corpus_dir": str(corpus_dir),
            "files_processed": len(existing_files)
        },
        "extraction_results": {}
    }
    
    for config_name, phrases in all_results.items():
        summary["extraction_results"][config_name] = {
            "config": next(c for c in extraction_configs if c["name"] == config_name),
            "phrases_extracted": len(phrases),
            "top_phrases": [p["phrase"] for p in phrases[:20]],
            "avg_keybert_score": sum(p["keybert_score"] for p in phrases) / len(phrases) if phrases else 0
        }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Summary saved to: {summary_file}")
    
    # 5. Show top phrases across all configurations
    print(f"\n📊 Top Phrases Summary")
    print("-" * 40)
    
    for config_name, phrases in all_results.items():
        print(f"\n{config_name.upper()}:")
        if phrases:
            print(f"  Top 20 phrases by KeyBERT score:")
            for i, phrase_data in enumerate(phrases[:20]):
                print(f"    {i+1:2d}. '{phrase_data['phrase']}' (score: {phrase_data['keybert_score']:.3f}, freq: {phrase_data['frequency']})")
        else:
            print("  No phrases found with current parameters")
    
    print(f"\n✅ KeyBERT phrase extraction complete!")
    print(f"📁 Results saved in: {output_dir}")
    
    return all_results


if __name__ == "__main__":
    try:
        results = main()
        print(f"\n🎉 Successfully extracted phrases from {len(results)} configurations")
    except Exception as e:
        print(f"\n❌ Error during KeyBERT phrase extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 