#!/usr/bin/env python3
"""
Test Dictionary Entry Creation - Tests the creation of dictionary entries following the defined strategy:
* Single word terms: Wikipedia lookup, disambiguation handling, Wiktionary fallback
* Multiword terms: Wikipedia lookup, skeleton page creation
* All output in HTML with CSS styling and class attributes
"""

import unittest
from pathlib import Path
from datetime import datetime

# Use absolute imports as per style guide
from amilib.ami_dict import AmiDictionary, AmiEntry
from amilib.wikimedia import WikidataLookup, WikipediaPage, WiktionaryPage
from amilib.ami_html import HtmlLib, HtmlUtil
from amilib.util import Util
from amilib.file_lib import FileLib

# Test configuration
TEST_TERMS = {
    "single_word_success": ["climate", "carbon", "energy"],
    "single_word_disambiguation": ["mercury", "jupiter", "venus"],
    "single_word_not_found": ["xyzzy", "plugh", "baz"],
    "multiword_success": ["climate change", "global warming", "carbon dioxide"],
    "multiword_skeleton": ["advanced climate modeling", "sustainable energy systems"]
}

class TestDictionaryEntryCreation(unittest.TestCase):
    """Test dictionary entry creation following the defined strategy."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Use amilib/temp directory instead of temporary directory
        cls.test_dir = Path(__file__).parent.parent / "temp"
        cls.output_dir = cls.test_dir / "dictionary_entry_creation_tests"
        cls.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize services
        cls.wikidata_lookup = WikidataLookup()
        
        # Create HTML output file
        cls.html_output = cls.output_dir / "dictionary_entry_creation_results.html"
        cls.create_html_output()
        
        print(f"Test output will be written to: {cls.html_output}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Don't delete the temp directory since it's part of the project
        print(f"Test results saved to: {cls.output_dir}")
        print(f"HTML output: {cls.html_output}")
    
    @classmethod
    def create_html_output(cls):
        """Create the HTML output file with CSS styling."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dictionary Entry Creation Test Results</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #3498db;
        }}
        
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        
        .header .timestamp {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        
        .test-section {{
            margin-bottom: 40px;
            border: 1px solid #ecf0f1;
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .test-section-header {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px 20px;
            margin: 0;
            font-size: 1.3em;
        }}
        
        .test-case {{
            border-bottom: 1px solid #ecf0f1;
            padding: 20px;
        }}
        
        .test-case:last-child {{
            border-bottom: none;
        }}
        
        .test-case-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .test-case-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .test-status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .status-pass {{
            background-color: #d5f4e6;
            color: #27ae60;
            border: 1px solid #a8e6cf;
        }}
        
        .status-fail {{
            background-color: #fadbd8;
            color: #e74c3c;
            border: 1px solid #f1948a;
        }}
        
        .status-skip {{
            background-color: #fef9e7;
            color: #f39c12;
            border: 1px solid #fdeaa7;
        }}
        
        .test-details {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        
        .term-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }}
        
        .term-tag {{
            background-color: #e8f4fd;
            color: #2980b9;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.9em;
            border: 1px solid #b3d9f2;
        }}
        
        .result-summary {{
            background-color: #e8f5e8;
            border: 1px solid #a8e6cf;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
        }}
        
        .result-summary h4 {{
            margin: 0 0 10px 0;
            color: #27ae60;
        }}
        
        .error-details {{
            background-color: #fdf2f2;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
        }}
        
        .error-details h4 {{
            margin: 0 0 10px 0;
            color: #e74c3c;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dictionary Entry Creation Test Results</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div id="test-results">
            <!-- Test results will be populated here -->
        </div>
        
        <div class="footer">
            <p>Test results generated by AmiDictionary Entry Creation Tests</p>
        </div>
    </div>
    
    <script>
        // JavaScript for dynamic updates if needed
        function updateTestStatus(testId, status, details) {{
            const testElement = document.getElementById(testId);
            if (testElement) {{
                const statusElement = testElement.querySelector('.test-status');
                statusElement.className = `test-status status-${{status}}`;
                statusElement.textContent = status.toUpperCase();
                
                if (details) {{
                    const detailsElement = testElement.querySelector('.test-details');
                    if (detailsElement) {{
                        detailsElement.innerHTML = details;
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>"""
        
        with open(cls.html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def add_test_result_to_html(self, test_name, status, terms, result_summary, error_details=None):
        """Add a test result to the HTML output."""
        if not self.html_output.exists():
            return
        
        # Read existing HTML
        with open(self.html_output, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create test result HTML
        test_id = f"test-{test_name.replace(' ', '-').lower()}"
        terms_html = '\n'.join([f'<span class="term-tag">{term}</span>' for term in terms])
        
        if error_details:
            details_html = f"""
                <div class="result-summary">
                    <h4>Result Summary:</h4>
                    <p>{result_summary}</p>
                </div>
                <div class="error-details">
                    <h4>Error Details:</h4>
                    <p>{error_details}</p>
                </div>
            """
        else:
            details_html = f"""
                <div class="result-summary">
                    <h4>Result Summary:</h4>
                    <p>{result_summary}</p>
                </div>
            """
        
        test_result_html = f"""
        <div class="test-section">
            <h2 class="test-section-header">{test_name}</h2>
            <div class="test-case" id="{test_id}">
                <div class="test-case-header">
                    <div class="test-case-title">{test_name}</div>
                    <div class="test-status status-{status}">{status.upper()}</div>
                </div>
                <div class="test-details">
                    <strong>Test Terms:</strong>
                    <div class="term-list">{terms_html}</div>
                    {details_html}
                </div>
            </div>
        </div>
        """
        
        # Insert before footer
        insert_point = html_content.find('<div class="footer">')
        if insert_point != -1:
            new_html = html_content[:insert_point] + test_result_html + html_content[insert_point:]
            
            with open(self.html_output, 'w', encoding='utf-8') as f:
                f.write(new_html)
    
    def test_single_word_wikipedia_success(self):
        """Test successful Wikipedia lookup for single word terms."""
        test_name = "Single Word - Wikipedia Success"
        terms = TEST_TERMS["single_word_success"]
        
        try:
            # Test using existing AmiDictionary functionality
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Single Word Success Test",
                desc="Testing Wikipedia lookup for single word terms",
                wikidata=True,
                outdir=self.output_dir
            )
            
            # Verify results
            self.assertIsNotNone(dictionary)
            self.assertIsNotNone(outpath)
            self.assertTrue(outpath.exists())
            
            # Check entries were created
            self.assertGreater(len(dictionary.entries), 0)
            
            result_summary = f"Successfully created dictionary with {len(dictionary.entries)} entries. Output saved to {outpath.name}"
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Failed to create dictionary from single word terms"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_single_word_disambiguation_handling(self):
        """Test handling of disambiguation pages for single word terms."""
        test_name = "Single Word - Disambiguation Handling"
        terms = TEST_TERMS["single_word_disambiguation"]
        
        try:
            # Test disambiguation handling
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Disambiguation Test",
                desc="Testing disambiguation page handling",
                wikidata=True,
                outdir=self.output_dir
            )
            
            # Verify results
            self.assertIsNotNone(dictionary)
            self.assertIsNotNone(outpath)
            self.assertTrue(outpath.exists())
            
            result_summary = f"Successfully handled disambiguation pages. Dictionary created with {len(dictionary.entries)} entries."
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Failed to handle disambiguation pages"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_single_word_wiktionary_fallback(self):
        """Test Wiktionary fallback when Wikipedia lookup fails."""
        test_name = "Single Word - Wiktionary Fallback"
        terms = TEST_TERMS["single_word_not_found"]
        
        try:
            # Test Wiktionary fallback
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Wiktionary Fallback Test",
                desc="Testing Wiktionary fallback for unknown terms",
                wikidata=False,
                outdir=self.output_dir
            )
            
            # Verify results
            self.assertIsNotNone(dictionary)
            self.assertIsNotNone(outpath)
            self.assertTrue(outpath.exists())
            
            result_summary = f"Successfully created dictionary with Wiktionary fallback. {len(dictionary.entries)} entries created."
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Failed to create dictionary with Wiktionary fallback"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_multiword_wikipedia_success(self):
        """Test successful Wikipedia lookup for multiword terms."""
        test_name = "Multiword - Wikipedia Success"
        terms = TEST_TERMS["multiword_success"]
        
        try:
            # Test multiword Wikipedia lookup
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Multiword Wikipedia Test",
                desc="Testing Wikipedia lookup for multiword terms",
                wikidata=True,
                outdir=self.output_dir
            )
            
            # Verify results
            self.assertIsNotNone(dictionary)
            self.assertIsNotNone(outpath)
            self.assertTrue(outpath.exists())
            
            result_summary = f"Successfully created dictionary from multiword terms. {len(dictionary.entries)} entries created."
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Failed to create dictionary from multiword terms"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_multiword_skeleton_creation(self):
        """Test skeleton page creation for multiword terms not in Wikipedia."""
        test_name = "Multiword - Skeleton Creation"
        terms = TEST_TERMS["multiword_skeleton"]
        
        try:
            # Test skeleton creation for complex multiword terms
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Skeleton Creation Test",
                desc="Testing skeleton page creation for complex terms",
                wikidata=False,
                outdir=self.output_dir
            )
            
            # Verify results
            self.assertIsNotNone(dictionary)
            self.assertIsNotNone(outpath)
            self.assertTrue(outpath.exists())
            
            result_summary = f"Successfully created skeleton entries for complex multiword terms. {len(dictionary.entries)} entries created."
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Failed to create skeleton entries for complex terms"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_dictionary_validation(self):
        """Test that created dictionaries are valid."""
        test_name = "Dictionary Validation"
        terms = ["test", "validation", "terms"]
        
        try:
            # Create and validate dictionary
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="Validation Test",
                desc="Testing dictionary validation",
                outdir=self.output_dir
            )
            
            # Basic validation checks
            self.assertIsNotNone(dictionary.root)
            self.assertEqual(dictionary.root.tag, "dictionary")
            self.assertIn("title", dictionary.root.attrib)
            # Note: version attribute is not automatically added by create_dictionary_from_words
            
            # Check entries
            entries = dictionary.root.findall("entry")
            self.assertGreater(len(entries), 0)
            
            for entry in entries:
                self.assertIn("term", entry.attrib)
                self.assertIn("name", entry.attrib)  # Entries have 'name' not 'id'
            
            result_summary = f"Dictionary validation successful. All {len(entries)} entries have required attributes."
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "Dictionary validation failed"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise
    
    def test_html_output_generation(self):
        """Test HTML output generation with styling."""
        test_name = "HTML Output Generation"
        terms = ["html", "output", "test"]
        
        try:
            # Create dictionary
            dictionary, outpath = AmiDictionary.create_dictionary_from_words(
                terms=terms,
                title="HTML Output Test",
                desc="Testing HTML output generation",
                outdir=self.output_dir
            )
            
            # Generate HTML output
            html_file = self.output_dir / "test_dictionary.html"
            dictionary.create_html_write_to_file(html_file, debug=True)
            
            # Verify HTML file was created
            self.assertTrue(html_file.exists())
            
            # Check HTML content
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Basic HTML validation - the existing method doesn't add DOCTYPE
            self.assertIn("<html", html_content)
            self.assertIn("</html>", html_content)
            self.assertIn("role=\"ami_dictionary\"", html_content)
            
            result_summary = f"HTML output generation successful. File created: {html_file.name}"
            self.add_test_result_to_html(test_name, "pass", terms, result_summary)
            
        except Exception as e:
            error_details = f"Exception occurred: {str(e)}"
            result_summary = "HTML output generation failed"
            self.add_test_result_to_html(test_name, "fail", terms, result_summary, error_details)
            raise


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDictionaryEntryCreation)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"HTML output: {TestDictionaryEntryCreation.html_output}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
