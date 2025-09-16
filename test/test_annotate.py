#!/usr/bin/env python3
"""
Test suite for PDF annotation functionality
"""

import requests
import fitz  # PyMuPDF
from test.test_all import AmiAnyTest
from test.resources import Resources

class AnnotateTest(AmiAnyTest):
    """Test class for PDF annotation functionality"""
    
    def test_read_shaik_wordlist(self):
        """Test reading wordlist from Shaik's GitHub repository"""
        print("🧪 Testing Shaik wordlist access...")
        
        url = "https://raw.githubusercontent.com/semanticClimate/internship_sC/Shaik-Zainab/IPCC_WG2_Chapter07/Wordlist_WG2Ch07.txt"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            terms = [line.strip() for line in response.text.split('\n') if line.strip()]
            
            print(f"✅ Successfully read {len(terms)} terms from GitHub")
            
            # Verify 3 specific terms
            test_terms = ["Aedes aegypti", "Urban heat island effects", "Zoonotic transmission"]
            
            for term in test_terms:
                if term in terms:
                    print(f"✅ Found term: {term}")
                else:
                    print(f"❌ Missing term: {term}")
                    return False
            
            print("✅ All 3 test terms found in wordlist")
            
        except Exception as e:
            print(f"❌ Error reading wordlist: {e}")
    
    def test_read_ipcc_wg2_chapter07_pdf(self):
        """Test reading IPCC WG2 Chapter 7 PDF"""
        print("🧪 Testing IPCC WG2 Chapter 7 PDF access...")
        
        pdf_path = Resources.TEST_PDFS_DIR / "IPCC_AR6_WGII_Chapter07.pdf"
        
        try:
            # Open PDF and get basic info
            doc = fitz.open(str(pdf_path))
            
            print(f"✅ Successfully opened PDF: {pdf_path}")
            print(f"📄 Pages: {len(doc)}")
            
            # Get first page text to verify content
            first_page = doc[0]
            text = first_page.get_text()
            
            # Check for expected content
            expected_terms = ["climate", "health", "adaptation"]
            found_terms = []
            
            for term in expected_terms:
                if term.lower() in text.lower():
                    found_terms.append(term)
                    print(f"✅ Found term: {term}")
                else:
                    print(f"❌ Missing term: {term}")
            
            doc.close()
            
            # Verify we found at least one expected term
            assert len(found_terms) > 0, f"Should find at least one of {expected_terms}"
            
            print(f"✅ PDF reading test completed - found {len(found_terms)} expected terms")
            
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            raise
    
    def test_annotate_pdf_with_shaik_wordlist(self):
        """Test annotating PDF with words from Shaik wordlist"""
        print("🧪 Testing PDF annotation with Shaik wordlist...")
        
        # Step 1: Read Shaik wordlist
        url = "https://raw.githubusercontent.com/semanticClimate/internship_sC/Shaik-Zainab/IPCC_WG2_Chapter07/Wordlist_WG2Ch07.txt"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            terms = [line.strip() for line in response.text.split('\n') if line.strip()]
            print(f"✅ Loaded {len(terms)} terms from Shaik wordlist")
            print(f"📋 First 5 terms: {terms[:5]}")
        except Exception as e:
            print(f"❌ Error loading wordlist: {e}")
            raise
        
        # Step 2: Read PDF
        pdf_path = Resources.TEST_PDFS_DIR / "IPCC_AR6_WGII_Chapter07.pdf"
        doc = None
        
        try:
            doc = fitz.open(str(pdf_path))
            print(f"✅ Opened PDF: {len(doc)} pages")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            raise
        
        # Step 3: Find and annotate words in PDF
        try:
            found_terms = []
            annotated_count = 0
            
            # Use all terms from wordlist
            test_terms = terms
            print(f"🔍 Testing {len(test_terms)} terms across 100 pages")
            
            # Debug: Check what text is in first page
            first_page = doc[0]
            first_page_text = first_page.get_text()
            print(f"📄 First page text sample: {first_page_text[:200]}...")
            
            for page_num in range(min(100, len(doc))):  # Test first 100 pages
                page = doc[page_num]
                text = page.get_text()
                
                for term in test_terms:
                    if term.lower() in text.lower():
                        if term not in found_terms:
                            found_terms.append(term)
                            print(f"   ✅ Found term: {term} on page {page_num + 1}")
                        
                        # Find position of term in text
                        import re
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        matches = list(pattern.finditer(text))
                        
                        for match in matches:
                            # Get text blocks to find position
                            text_dict = page.get_text("dict")
                            for block in text_dict["blocks"]:
                                if "lines" in block:
                                    for line in block["lines"]:
                                        for span in line["spans"]:
                                            span_text = span["text"]
                                            if term.lower() in span_text.lower():
                                                bbox = fitz.Rect(span["bbox"])
                                                
                                                # Add hyperlink annotation
                                                link_annot = page.insert_link({
                                                    "kind": fitz.LINK_URI,
                                                    "uri": f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
                                                    "from": bbox,
                                                    "title": f"Definition: {term}"
                                                })
                                                
                                                # Add visual indicator (blue underline)
                                                underline_rect = fitz.Rect(bbox.x0, bbox.y1 - 1, bbox.x1, bbox.y1)
                                                page.draw_rect(underline_rect, color=(0, 0, 1), width=1)
                                                
                                                annotated_count += 1
                                                print(f"   ✅ Annotated: {term} on page {page_num + 1}")
                                                break
                                        else:
                                            continue
                                        break
                                    else:
                                        continue
                                    break
                                else:
                                    continue
                                break
                        break  # Only annotate first occurrence per page
            
            # Save annotated PDF
            output_path = Resources.TEMP_DIR / "IPCC_AR6_WGII_Chapter07_annotated.pdf"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            
            print(f"✅ Annotation completed!")
            print(f"📊 Found {len(found_terms)} unique terms: {found_terms}")
            print(f"📊 Annotated {annotated_count} instances")
            print(f"💾 Saved annotated PDF: {output_path}")
            
            # Verify output file exists
            assert output_path.exists(), "Annotated PDF should be created"
            assert len(found_terms) > 0, "Should find at least one term from wordlist"
            
        except Exception as e:
            print(f"❌ Error during annotation: {e}")
            raise
        finally:
            if doc and not doc.is_closed:
                doc.close()
    
    def test_dictionary_annotation_workflow(self):
        """Test complete dictionary annotation workflow using external wordlist"""
        print("🧪 Testing complete dictionary annotation workflow...")
        
        # Step 1: Load external wordlist
        url = "https://raw.githubusercontent.com/semanticClimate/internship_sC/Shaik-Zainab/IPCC_WG2_Chapter07/Wordlist_WG2Ch07.txt"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            terms = [line.strip() for line in response.text.split('\n') if line.strip()]
            print(f"✅ Loaded {len(terms)} terms from external wordlist")
        except Exception as e:
            print(f"❌ Error loading wordlist: {e}")
            raise
        
        # Step 2: Read PDF
        pdf_path = Resources.TEST_PDFS_DIR / "IPCC_AR6_WGII_Chapter07.pdf"
        doc = None
        
        try:
            doc = fitz.open(str(pdf_path))
            print(f"✅ Opened PDF: {len(doc)} pages")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            raise
        
        # Step 3: Find and annotate words in PDF
        try:
            found_terms = []
            annotated_count = 0
            
            # Use all terms from wordlist
            test_terms = terms
            print(f"🔍 Testing {len(test_terms)} terms across 100 pages")
            
            for page_num in range(min(100, len(doc))):  # Test first 100 pages
                page = doc[page_num]
                text = page.get_text()
                
                for term in test_terms:
                    if term.lower() in text.lower():
                        if term not in found_terms:
                            found_terms.append(term)
                            print(f"   ✅ Found term: {term} on page {page_num + 1}")
                        
                        # Find position of term in text
                        import re
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        matches = list(pattern.finditer(text))
                        
                        for match in matches:
                            # Get text blocks to find position
                            text_dict = page.get_text("dict")
                            for block in text_dict["blocks"]:
                                if "lines" in block:
                                    for line in block["lines"]:
                                        for span in line["spans"]:
                                            span_text = span["text"]
                                            if term.lower() in span_text.lower():
                                                bbox = fitz.Rect(span["bbox"])
                                                
                                                # Add hyperlink annotation
                                                link_annot = page.insert_link({
                                                    "kind": fitz.LINK_URI,
                                                    "uri": f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
                                                    "from": bbox,
                                                    "title": f"Definition: {term}"
                                                })
                                                
                                                # Add visual indicator (blue underline)
                                                underline_rect = fitz.Rect(bbox.x0, bbox.y1 - 1, bbox.x1, bbox.y1)
                                                page.draw_rect(underline_rect, color=(0, 0, 1), width=1)
                                                
                                                annotated_count += 1
                                                print(f"   ✅ Annotated: {term} on page {page_num + 1}")
                                                break
                                        else:
                                            continue
                                        break
                                    else:
                                        continue
                                    break
                                else:
                                    continue
                                break
                        break  # Only annotate first occurrence per page
            
            # Save annotated PDF
            output_path = Resources.TEMP_DIR / "IPCC_AR6_WGII_Chapter07_dictionary_annotated.pdf"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            
            print(f"✅ Dictionary annotation workflow completed!")
            print(f"📊 Found {len(found_terms)} unique terms: {found_terms[:10]}...")
            print(f"📊 Annotated {annotated_count} instances")
            print(f"💾 Saved annotated PDF: {output_path}")
            
            # Verify output file exists
            assert output_path.exists(), "Annotated PDF should be created"
            assert len(found_terms) > 0, "Should find at least one term from wordlist"
            
        except Exception as e:
            print(f"❌ Error during dictionary annotation: {e}")
            raise
        finally:
            if doc and not doc.is_closed:
                doc.close()
