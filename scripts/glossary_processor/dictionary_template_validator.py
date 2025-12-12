"""
Validator for IPCC Dictionary Template structure.

Validates HTML files against the dictionary template specification.
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import lxml.etree as ET

from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.util import Util
from scripts.glossary_processor.dictionary_template_constants import (
    TAG_HTML, TAG_HEAD, TAG_BODY, ROLE_IPCC_DICTIONARY, CLASS_GLOSSARY,
    CLASS_ENTRY, ROLE_DICTIONARY_ENTRY, ROLE_DICTIONARY_METADATA, ROLE_TERM,
    ROLE_DEFINITION, TAG_DT, TAG_DD, DATA_REPORT, DATA_ANNEX, DATA_TERM,
    DATA_ENTRY_NUMBER, ATTR_ID, ATTR_HREF, VALID_REPORTS, TAG_H1,
    XPATH_DICT_CONTAINER, XPATH_DICT_ENTRIES, XPATH_TERMS, XPATH_DEFINITIONS,
    XPATH_METADATA, XPATH_CROSS_REFS, XPATH_HEAD, XPATH_BODY,
    MSG_NO_DICT_CONTAINER, MSG_MULTIPLE_CONTAINERS, MSG_MISSING_REQUIRED_ATTR,
    MSG_UNKNOWN_REPORT, MSG_NO_METADATA, MSG_NO_ENTRIES, MSG_ENTRY_MISSING_ID,
    MSG_DUPLICATE_ID, MSG_ENTRY_MISSING_TERM, MSG_ENTRY_MISSING_DATA_TERM,
    MSG_ENTRY_MISSING_DATA_NUMBER, MSG_EMPTY_TERM, MSG_NO_DEFINITION,
    MSG_INVALID_CROSS_REF, MSG_ROOT_MUST_BE_HTML, MSG_NO_HEAD, MSG_NO_BODY,
    MSG_ERROR_PARSING, MSG_ERROR_ANALYZING
)

logger = Util.get_logger(__name__)


class DictionaryTemplateValidator:
    """Validates dictionary HTML against template specification."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, html_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate HTML file against template.
        
        Args:
            html_path: Path to HTML file to validate
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        try:
            html_tree = HtmlUtil.parse_html_lxml(str(html_path))
            html_elem = html_tree.getroot()
            
            # Validate root structure
            self._validate_root(html_elem)
            
            # Validate dictionary container
            dict_container = self._validate_dictionary_container(html_elem)
            
            if dict_container is not None:
                # Validate metadata
                self._validate_metadata(dict_container)
                
                # Validate entries
                self._validate_entries(dict_container)
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(MSG_ERROR_PARSING.format(error=e))
            return False, self.errors, self.warnings
    
    def _validate_root(self, html_elem: ET.Element):
        """Validate root HTML structure."""
        if html_elem.tag != TAG_HTML:
            self.errors.append(MSG_ROOT_MUST_BE_HTML)
        
        head = html_elem.xpath(XPATH_HEAD)
        if not head:
            self.warnings.append(MSG_NO_HEAD)
        
        body = html_elem.xpath(XPATH_BODY)
        if not body:
            self.errors.append(MSG_NO_BODY)
    
    def _validate_dictionary_container(self, html_elem: ET.Element) -> Optional[ET.Element]:
        """Validate dictionary container exists and has required attributes."""
        # Look for dictionary container (flexible: role or class)
        dict_containers = html_elem.xpath(XPATH_DICT_CONTAINER)
        
        if not dict_containers:
            self.errors.append(MSG_NO_DICT_CONTAINER)
            return None
        
        if len(dict_containers) > 1:
            self.warnings.append(MSG_MULTIPLE_CONTAINERS.format(count=len(dict_containers)))
        
        container = dict_containers[0]
        
        # Check required data attributes
        required_attrs = [DATA_REPORT, DATA_ANNEX]
        for attr in required_attrs:
            if not container.get(attr):
                self.errors.append(MSG_MISSING_REQUIRED_ATTR.format(attr=attr))
        
        # Validate report value
        report = container.get(DATA_REPORT)
        if report and report not in VALID_REPORTS:
            self.warnings.append(MSG_UNKNOWN_REPORT.format(report=report))
        
        return container
    
    def _validate_metadata(self, container: ET.Element):
        """Validate metadata section."""
        metadata_sections = container.xpath(XPATH_METADATA)
        
        if not metadata_sections:
            self.warnings.append(MSG_NO_METADATA)
    
    def _validate_entries(self, container: ET.Element):
        """Validate dictionary entries."""
        entries = container.xpath(XPATH_DICT_ENTRIES)
        
        if not entries:
            self.errors.append(MSG_NO_ENTRIES)
            return
        
        entry_ids = []
        
        for i, entry in enumerate(entries):
            # Validate entry ID
            entry_id = entry.get(ATTR_ID)
            if not entry_id:
                self.errors.append(MSG_ENTRY_MISSING_ID.format(num=i+1))
            elif entry_id in entry_ids:
                self.errors.append(MSG_DUPLICATE_ID.format(id=entry_id))
            else:
                entry_ids.append(entry_id)
            
            # Validate entry has term
            terms = entry.xpath(XPATH_TERMS)
            if not terms:
                self.errors.append(MSG_ENTRY_MISSING_TERM.format(num=i+1, id=entry_id or 'unknown'))
            
            # Validate data attributes
            data_term = entry.get(DATA_TERM)
            if not data_term:
                self.warnings.append(MSG_ENTRY_MISSING_DATA_TERM.format(num=i+1, id=entry_id or 'unknown'))
            
            data_entry_number = entry.get(DATA_ENTRY_NUMBER)
            if not data_entry_number:
                self.warnings.append(MSG_ENTRY_MISSING_DATA_NUMBER.format(num=i+1, id=entry_id or 'unknown'))
            
            # Validate term content
            for term in terms:
                term_text = ''.join(term.itertext()).strip()
                if not term_text:
                    self.errors.append(MSG_EMPTY_TERM.format(num=i+1, id=entry_id or 'unknown'))
            
            # Validate definition (optional but common)
            definitions = entry.xpath(XPATH_DEFINITIONS)
            if not definitions:
                self.warnings.append(MSG_NO_DEFINITION.format(num=i+1, id=entry_id or 'unknown'))
            
            # Validate cross-reference links
            cross_refs = entry.xpath(XPATH_CROSS_REFS)
            for ref in cross_refs:
                href = ref.get(ATTR_HREF)
                if href and href.startswith('#'):
                    target_id = href[1:]  # Remove #
                    if target_id not in entry_ids:
                        self.warnings.append(MSG_INVALID_CROSS_REF.format(num=i+1, id=entry_id or 'unknown', target_id=target_id))
    
    def validate_template_structure(self, html_path: Path) -> Dict:
        """
        Validate against full template structure and return detailed report.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            Dictionary with validation results
        """
        is_valid, errors, warnings = self.validate(html_path)
        
        try:
            html_tree = HtmlUtil.parse_html_lxml(str(html_path))
            html_elem = html_tree.getroot()
            
            # Count elements
            dict_containers = html_elem.xpath(XPATH_DICT_CONTAINER)
            entries = html_elem.xpath(XPATH_DICT_ENTRIES)
            terms = html_elem.xpath(XPATH_TERMS)
            definitions = html_elem.xpath(XPATH_DEFINITIONS)
            cross_refs = html_elem.xpath(XPATH_CROSS_REFS)
            
            return {
                'is_valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'statistics': {
                    'dictionary_containers': len(dict_containers),
                    'entries': len(entries),
                    'terms': len(terms),
                    'definitions': len(definitions),
                    'cross_references': len(cross_refs)
                }
            }
        except Exception as e:
            return {
                'is_valid': False,
                'errors': errors + [MSG_ERROR_ANALYZING.format(error=e)],
                'warnings': warnings,
                'statistics': {}
            }


def main():
    """Command-line interface for validator."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: dictionary_template_validator.py <html_file>")
        sys.exit(1)
    
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)
    
    validator = DictionaryTemplateValidator()
    result = validator.validate_template_structure(html_path)
    
    print(f"\nValidation Results for: {html_path}")
    print("=" * 60)
    
    print(f"\nValid: {'✅ YES' if result['is_valid'] else '❌ NO'}")
    
    if result['statistics']:
        print(f"\nStatistics:")
        for key, value in result['statistics'].items():
            print(f"  {key}: {value}")
    
    if result['errors']:
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['warnings']:
        print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    sys.exit(0 if result['is_valid'] else 1)


if __name__ == '__main__':
    main()

