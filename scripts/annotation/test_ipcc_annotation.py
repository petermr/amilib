#!/usr/bin/env python3
"""
Test script for IPCC chapter annotation functionality.
Demonstrates basic usage of the markup_ipcc_chapters_with_keywords.py script.
"""

import sys
from pathlib import Path

from markup_ipcc_chapters_with_keywords import IPCCChapterAnnotator


def test_csv_annotation():
    """Test CSV-based annotation for Chapter 1."""
    print("🧪 Testing CSV-based annotation for Chapter 1")
    print("=" * 50)
    
    # Create annotator
    annotator = IPCCChapterAnnotator()
    
    # Test loading keywords from CSV
    keywords = annotator.load_keywords_from_csv(1)
    print(f"📊 Loaded {len(keywords)} keywords from CSV")
    
    if keywords:
        # Show first few keywords
        sample_keywords = list(keywords.items())[:5]
        print("📝 Sample keywords:")
        for term, info in sample_keywords:
            print(f"  - {info['term']}: {info['link']}")
    
    # Test processing Chapter 1
    success = annotator.process_chapter(1, keyword_source='csv')
    if success:
        print("✅ Chapter 1 annotation completed successfully")
    else:
        print("❌ Chapter 1 annotation failed")
    
    return success


def test_dictionary_annotation():
    """Test dictionary-based annotation (if dictionary available)."""
    print("\n🧪 Testing dictionary-based annotation")
    print("=" * 50)
    
    # Look for existing dictionary files
    dict_candidates = [
        Path("test", "resources", "dictionary", "climate", "climate_dict.xml"),
        Path("test", "resources", "dictionary", "html", "sample_dict.html"),
    ]
    
    dict_path = None
    for candidate in dict_candidates:
        if candidate.exists():
            dict_path = candidate
            break
    
    if not dict_path:
        print("⚠️  No dictionary file found, skipping dictionary test")
        return False
    
    print(f"📚 Using dictionary: {dict_path}")
    
    # Create annotator
    annotator = IPCCChapterAnnotator()
    
    # Test loading keywords from dictionary
    keywords = annotator.load_keywords_from_dictionary(dict_path)
    print(f"📊 Loaded {len(keywords)} keywords from dictionary")
    
    if keywords:
        # Show first few keywords
        sample_keywords = list(keywords.items())[:5]
        print("📝 Sample keywords:")
        for term, info in sample_keywords:
            print(f"  - {info['term']}: {info['link']}")
    
    # Test processing Chapter 1
    success = annotator.process_chapter(1, keyword_source='dictionary', dict_path=dict_path)
    if success:
        print("✅ Chapter 1 dictionary annotation completed successfully")
    else:
        print("❌ Chapter 1 dictionary annotation failed")
    
    return success


def main():
    """Run all tests."""
    print("🚀 IPCC Chapter Annotation Test Suite")
    print("=" * 60)
    
    # Test CSV annotation
    csv_success = test_csv_annotation()
    
    # Test dictionary annotation
    dict_success = test_dictionary_annotation()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"CSV Annotation: {'✅ PASS' if csv_success else '❌ FAIL'}")
    print(f"Dictionary Annotation: {'✅ PASS' if dict_success else '❌ FAIL'}")
    
    if csv_success or dict_success:
        print("\n🎉 At least one annotation method is working!")
        print("📁 Check the output directories for annotated files:")
        print("  - temp/annotate/keyphrases/csv_annotated/")
        print("  - temp/annotate/keyphrases/dict_annotated/")
    else:
        print("\n❌ All tests failed. Check the error messages above.")


if __name__ == "__main__":
    main()
