import glob
import logging
import os
import pprint
import re
import traceback
import unittest
from pathlib import Path

import lxml
from lxml import etree
from lxml.etree import XMLSyntaxError, _Element

# local
from amilib.ami_dict import AmiDictionary, AmiEntry, AMIDictError, \
    AmiDictValidator, NAME, TITLE, TERM, LANG_UR, VERSION, WIKIDATA_ID
from amilib.amix import AmiLib
from amilib.constants import LOCAL_CEV_OPEN_DICT_DIR
from amilib.dict_args import AmiDictArgs
from amilib.dict_args import MARKUP_FILE
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.wikimedia import WikidataSparql
from amilib.xml_lib import XmlLib
from amilib.ami_html import HtmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest

# from parametrized import parametrized

# MUST use RAW content , not HTML
CEV_OPEN_RAW_DICT_URL = "https://raw.githubusercontent.com/petermr/CEVOpen/master/dictionary/"
PLANT_PART_RAW_DICT_URL = CEV_OPEN_RAW_DICT_URL + "eoPlantPart/eoplant_part.xml"
COMPOUND_RAW_DICT_URL = CEV_OPEN_RAW_DICT_URL + "eoCompound/plant_compound.xml"
ANALYSIS_METHOD_RAW_DICT_URL = CEV_OPEN_RAW_DICT_URL + "eoAnalysisMethod/eoAnalysisMethod.xml"
TEST_DIR = Path(Path(__file__).parent.parent, "test")
TEST_RESOURCE_DIR = Path(TEST_DIR, "resources")
DICTFILE1 = "dictfile1"
ROOT = "root"
ONE_ENTRY_PATH = "one_entry_file"
ONE_ENTRY_DICT = "one_entry_dict"
MINI_PLANT_PART = "mini_plant_part"
MINI_MENTHA = "mini_mentha"
ETHNOBOT_DICT = "VC_EthnobotanicalUse"
DUPLICATE_ENTRIES = "test_duplicate_entries"

RESOURCES_DIR = "resources"
# AMIDICTS = Path(Path(__file__).parent.parent, "py4ami/resources/amidicts")  # relative to dictribution base
AMIDICTS = Path(Path(__file__).parent.parent, f"{RESOURCES_DIR}/amidicts")  # relative to dictribution base

STARTING_VERSION = "0.0.1"

HOME = os.path.expanduser("~")
IPCC_DICT_ROOT = Path(HOME, "projects/semanticClimate/ipcc/ar6/wg3")  # needs resetting if tests are to be run

logger = Util.get_logger(__name__, level=logging.DEBUG)

# ===== helpers =====
def _create_amidict_with_foo_bar_entries():
    amidict = AmiDictionary.create_minimal_dictionary()
    entry_foo = amidict.create_and_add_entry_with_term("foo")
    entry_bar = amidict.create_and_add_entry_with_term("bar")
    return amidict


class AmiDictionaryTest(AmiAnyTest):
    """These are tests for developing CODE for dictionary creation and validation

    Code for VALIDATION of dictionaries should probably be bundled with the dictionaries themselves

    """

    logging.info(f"loading {__file__}")

    HTML_WITH_IDS = "html_with_ids"

    DICTFILE1 = "dictfile1"
    ROOT = "root"
    ONE_ENTRY_PATH = "one_entry_file"
    ONE_ENTRY_DICT = "one_entry_dict"
    MINI_PLANT_PART = "mini_plant_part"
    MINI_MENTHA = "mini_mentha"
    ETHNOBOT_DICT = "VC_EthnobotanicalUse"
    DUPLICATE_ENTRIES = "test_duplicate_entries"

    # AMIDICTS = Path(Path(__file__).parent.parent, "py4ami/resources/amidicts")  # relative to dictribution base
    # AMIDICTS = Path(Path(__file__).parent.parent, f"{AMI_TOP}/resources/amidicts")  # relative to dictribution base

    STARTING_VERSION = "0.0.1"

    ADMIN = True and AmiAnyTest.ADMIN
    CMD = True and AmiAnyTest.CMD
    LONG = True and AmiAnyTest.LONG
    NET = True and AmiAnyTest.NET
    NYI = True and AmiAnyTest.NYI
    USER = True and AmiAnyTest.USER
    VERYLONG = True and AmiAnyTest.VERYLONG

    CEV_EXISTS = Path(LOCAL_CEV_OPEN_DICT_DIR).exists()

    def create_file_dict(self):
        """Variables created afresh for every test"""
        dictfile1 = Path(AMIDICTS, "dict1.xml")
        # dictfile1 = Path(Path(__file__).parent.parent, "py4ami/resources/amidicts/dict1.xml")
        one_entry_path = Path(Path(__file__).parent.parent, f"{AMIDICTS}/dict_one_entry.xml")
        root = etree.parse(str(dictfile1)).getroot()
        assert dictfile1.exists(), "{dictfile1} exists"
        one_entry_path = Path(AMIDICTS, "dict_one_entry.xml")
        one_entry_dict_new = AmiDictionary.create_from_xml_file(one_entry_path)
        assert one_entry_dict_new is not None
        mini_plant_part_path = Path(AMIDICTS, "mini_plant_part.xml")

        # BUG: this should be available through pytest
        setup_dict = {
            DICTFILE1: dictfile1,  # type path
            ROOT: root,
            ONE_ENTRY_PATH: one_entry_path,
            ONE_ENTRY_DICT: one_entry_dict_new,
            MINI_PLANT_PART: mini_plant_part_path,
            MINI_MENTHA: Path(AMIDICTS, "mentha_tps.xml"),
            ETHNOBOT_DICT: Path(AMIDICTS, ETHNOBOT_DICT + ".xml"),
            DUPLICATE_ENTRIES: Path(AMIDICTS, DUPLICATE_ENTRIES + ".xml"),
        }
        logger.info(f"setup_dict {setup_dict}")
        return setup_dict

    @unittest.skipUnless("environment", ADMIN)
    def test_dictionary_file1_exists(self):
        """Test that a simple dictionary "dictfile1" file exists"""
        setup_dict = self.create_file_dict()
        assert setup_dict[DICTFILE1].exists(), f"file should exist {setup_dict['dict1']}"

    def test_dictionary_element(self):
        """
        reads xml string into dictiomary and tests that has "dictionary" root element
        and no child entries
        """
        dict_str = """
        <dictionary title='foo'>
        </dictionary>
        """
        ami_dict = AmiDictionary.create_dictionary_from_xml_string(dict_str)
        assert ami_dict is not None
        assert ami_dict.root.tag == "dictionary"
        assert ami_dict.has_valid_root_tag()
        assert ami_dict.get_entry_count() == 0


    def test_title_from_url_stem(self):
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.url = "https://some.where/foo/bar.xml"
        assert amidict.root.attrib[TITLE] == "minimal"  # needs fixing

    def test_title_from_file_stem(self):
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.file = "/user/me/foo.xml"
        assert amidict.root.attrib[TITLE] == "minimal"

    def test_dict_has_root_dictionary(self):
        """
        Tests that the dictionary has <dictionary> root element
        """
        setup_dict = self.create_file_dict()
        root = setup_dict[ROOT]
        assert root.tag == AmiDictionary.TAG

    def test_dict_contains_xml_element(self):
        root = etree.parse(str(self.create_file_dict()[DICTFILE1]))
        assert root is not None

    def test_can_read_dictionary_from_url_as_xml(self):
        """
        Checks that a dictionary can be read from a URL into XML
        Reads PLANT_PART_RAW_DICT_URL and validates that has about 728 entries
        """

        url = PLANT_PART_RAW_DICT_URL
        tree = XmlLib.parse_url_to_tree(url)
        descendants = tree.getroot().xpath('.//*')
        assert 730 >= len(descendants) >= 720

    def test_dictionary_has_xml_declaration_with_encoding(self):
        """Checks dictionary has encoding of 'UTF-8' and XML Version 1.0
        USEFUL 2022-07"""
        dicts = [ETHNOBOT_DICT, DICTFILE1, ]
        for dikt in dicts:
            logger.debug(f"...{dikt}")
            root = etree.parse(str(self.create_file_dict()[dikt]))
            dictionary = AmiDictionary.create_from_xml_object(root)
            validator = AmiDictValidator(dictionary)
            error_list = validator.get_xml_declaration_error_list()
            assert not error_list

    # @pytest.mark.url
    def test_validate_url_dict(self):
        """
        tests that historic dictionaries read into validator
        TODO skip this
        """
        urllist = [
            PLANT_PART_RAW_DICT_URL,
            ANALYSIS_METHOD_RAW_DICT_URL,
            COMPOUND_RAW_DICT_URL
        ]
        for url in urllist:
            logger.debug(f"url: {url}")
            # tree = XmlLib.parse_url_to_tree(url)
            # dictionary = AmiDictionary.create_from_xml_object(tree)
            dictionary = AmiDictionary.create_dictionary_from_url(url)
            validator = AmiDictValidator(dictionary)
            # validator.validate_title()
            error_list = validator.get_error_list()
            logger.warning(f"error_list {error_list}")

    # AmiDictionary

    def test_can_create_ami_dict_from_file(self):
        """read an existing XML AmiDictionary"""
        setup_dict = self.create_file_dict()
        one_entry_path = setup_dict[ONE_ENTRY_PATH]
        amidict = AmiDictionary.create_from_xml_file(one_entry_path)
        assert amidict is not None

    # @pytest.mark.simple
    def test_dictionary_is_an_ami_dictionary(self):
        """
        test dictionary with one entry
        """
        setup_dict = self.create_file_dict()
        amidict = setup_dict[ONE_ENTRY_DICT]
        assert type(amidict) is AmiDictionary

    def test_dictionary_get_entries(self):
        """
        unit test
        """
        setup_dict = self.create_file_dict()
        amidict = setup_dict[ONE_ENTRY_DICT]
        entries = amidict.get_lxml_entries()
        assert entries is not None

    # @pytest.mark.simple
    def test_dictionary_contains_one_entry(self):
        """
        unit test
        """
        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert amidict.get_entry_count() == 1, f"dict should have 1 entry, found  {amidict.get_entry_count()}"

    def test_get_first_entry(self):
        """
        unit test
        """
        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert amidict.get_first_ami_entry() is not None

    def test_get_attribute_names(self):
        """
        unit test
        """

        first_entry = self.create_file_dict()[ONE_ENTRY_DICT].get_first_ami_entry()
        assert type(first_entry) is AmiEntry
        attrib_names = {name for name in first_entry.element.attrib}
        assert attrib_names is not None

    def test_get_term_of_first_entry(self):
        """
        tests that we can retrieve the `term` value from an element

        """
        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert amidict.get_first_entry().attrib[TERM] == "Douglas Adams"

    def test_get_name_of_first_entry(self):
        """
        unit test
        """

        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert amidict.get_first_entry().attrib[NAME] == "Douglas Adams"

    def test_get_wikidata_of_first_entry(self):
        """
        unit test
        """

        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert amidict.get_first_entry().attrib[WIKIDATA_ID] == "Q42"

    def test_get_synonym_count(self):
        """
        unit test
        """
        amidict = AmiDictionaryTest().create_file_dict()[ONE_ENTRY_DICT]
        assert type(amidict) is AmiDictionary
        assert len(amidict.get_first_ami_entry().get_synonyms()) == 2

    def test_get_synonym_by_language(self):
        """
        unit test
        """

        amidict = self.create_file_dict()[ONE_ENTRY_DICT]
        assert type(amidict) is AmiDictionary
        elem = amidict.get_first_ami_entry().get_synonym_by_language(LANG_UR).element
        assert "ڈگلس ایڈمس" == ''.join(elem.itertext())

    def test_add_entry_with_term_to_zero_entry_dict(self):
        """
        Creates minimal dictionary with no entries and adds one entry
        tests its components
        """
        amidict = AmiDictionary.create_minimal_dictionary()
        print()
        logger.info(f"amidict {amidict.get_entry_count()}")
        entry = amidict.create_and_add_entry_with_term("foo")
        assert etree.tostring(entry) == b'<entry term="foo"/>'
        assert etree.tostring(
            amidict.root) == b'<dictionary title="minimal" version="0.0.1"><entry term="foo"/></dictionary>'
        assert amidict.get_entry_count() == 1

    def test_add_two_entry_with_term_to_zero_entry_dict(self):
        amidict = AmiDictionary.create_minimal_dictionary()
        entry_foo = amidict.add_entry_element("foo")
        entry_bar = amidict.add_entry_element("bar")
        assert etree.tostring(entry_bar) == b'<entry name="bar" term="bar"/>'
        assert etree.tostring(
            amidict.root) == b'<dictionary title="minimal" version="0.0.1"><entry name="foo" term="foo"/><entry name="bar" term="bar"/></dictionary>'
        assert amidict.get_entry_count() == 2

    def test_add_list_of_entries_from_list_of_string(self):
        """
        from a list of strings creates a list of entries and adds to existing dictionary
        (the entries only have term/name fields)
        """
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        term_count = len(terms)
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.add_entries_from_words(terms)
        assert amidict.get_entry_count() == term_count

    def test_find_entry_after_add_list_of_entries_from_list_of_string(self):
        """
        creates entries from strings and tests that they can be accessed by term
        """
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.add_entries_from_words(terms)
        entry_bar = amidict.get_lxml_entry("bar")
        assert entry_bar is not None

    def test_fail_on_missing_entry_after_add_list_of_entries_from_list_of_string(self):
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.add_entries_from_words(terms)
        entry_zilch = amidict.get_lxml_entry("zilch")
        assert entry_zilch is None, f"missing entry returns None"

    def test_add_second_list_of_entries_from_list_of_string(self):
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.add_entries_from_words(terms)
        terms1 = ["wibble", "wobble"]
        amidict.add_entries_from_words(terms1)
        assert amidict.get_entry_count() == len(terms) + len(terms1)

    def test_add_list_of_entries_from_list_of_string_with_duplicates_and_replace(self):
        """
        creates dictionary from list of words and force replacement of duplicates
        """
        terms = ["foo", "bar", "plugh", "xyzzy", "bar"]
        amidict = AmiDictionary.create_minimal_dictionary()
        amidict.add_entries_from_words(terms, duplicates="replace")
        assert amidict.get_entry_count() == 4, f"'bar' should be present"

    def test_add_list_of_entries_from_list_of_string_with_duplicates_and_no_replace(self):
        """
        add list of terms which contains duplicate and raise error
        """
        terms = ["foo", "bar", "plugh", "xyzzy", "bar"]
        amidict = AmiDictionary.create_minimal_dictionary()
        try:
            amidict.add_entries_from_words(terms, duplicates="error")
            assert False, f"AMIDict duplicate error (bar) should have been thrown"
        except AMIDictError:
            assert True, "error should have been throwm"
        assert amidict.get_entry_count() == 4, f"'bar' should be present"

    def test_add_then_remove_entry_and_replace(self):
        """create new entry , then delete, then re-add"""
        amidict, _ = AmiDictionary.create_dictionary_from_words(["foo", "bar", "plugh", "xyzzy"])
        assert amidict.get_entry_count() == 4
        amidict.delete_entry_by_term("bar")
        assert amidict.get_entry_count() == 3, f"entry 'bar' should have been removed"
        amidict.create_and_add_entry_with_term("bar")
        assert amidict.get_entry_count() == 4, f"entry 'bar' should have been re-added"

    # find entries
    def test_find_entry_by_term(self):
        """searches for entry by value of term"""
        amidict = _create_amidict_with_foo_bar_entries()
        entry = amidict.get_lxml_entry("foo")
        assert entry is not None
        assert entry.attrib[TERM] == "foo", f"should retrieve entry with term 'foo'"

    def test_find_entry_by_term_bar(self):
        amidict = _create_amidict_with_foo_bar_entries()
        entry = amidict.get_lxml_entry("bar")
        assert entry is not None

    def test_find_entry_by_term_zilch(self):
        amidict = _create_amidict_with_foo_bar_entries()
        entry = amidict.get_lxml_entry("zilch")
        assert entry is None

    def test_delete_entry_by_term_foo(self):
        amidict = _create_amidict_with_foo_bar_entries()
        logger.debug(f"amidict0 {lxml.etree.tostring(amidict.root)}")
        amidict.delete_entry_by_term("foo")
        logger.debug(f"amidict1 {lxml.etree.tostring(amidict.root)}")
        assert amidict.get_entry_count() == 1

    def test_delete_entry_by_term_foo_and_re_add(self):
        amidict = _create_amidict_with_foo_bar_entries()
        amidict.delete_entry_by_term("foo")
        amidict.create_and_add_entry_with_term("foo")
        assert amidict.get_entry_count() == 2

    def test_create_and_add_entry_with_term(self):
        term = "foo"
        amidict = AmiDictionary.create_minimal_dictionary()
        assert amidict.get_entry_count() == 0
        amidict.create_and_add_entry_with_term(term)
        assert amidict.get_entry_count() == 1
        entry = amidict.get_ami_entry(term)
        assert type(entry) is AmiEntry
        assert term == entry.get_term()

    def test_create_and_overwrite_entry_with_duplicate_term(self):
        term = "foo"
        amidict = AmiDictionary.create_minimal_dictionary()
        assert amidict.get_entry_count() == 0
        entry = amidict.create_and_add_entry_with_term(term)
        logger.debug(f"entry: {type(entry)}")
        assert isinstance(entry, _Element)
        AmiEntry.add_name(entry, "foofoo")
        amidict.create_and_add_entry_with_term(term, replace=True)
        assert amidict.get_entry_count() == 1
        entry = amidict.get_lxml_entry(term)
        assert type(entry) is _Element

        assert term == entry.attrib[TERM]
        assert NAME not in entry.attrib

    def test_create_and_fail_on_add_entry_with_duplicate_term(self):
        term = "foo"
        amidict = AmiDictionary.create_minimal_dictionary()
        entry = amidict.create_and_add_entry_with_term(term)
        try:
            amidict.create_and_add_entry_with_term(term, replace=False)
            assert False, f"should fail with duplicate entry"
        except AMIDictError as e:
            assert True, "should raise duplicate error"

    def test_create_and_overwrite_duplicate_term(self):
        """
        setting term which already exists in dictionary, and replace with new term
        """
        term = "foo"
        amidict = AmiDictionary.create_minimal_dictionary()
        ami_entry = AmiEntry.create_from_element(amidict.create_and_add_entry_with_term(term))
        assert ami_entry.get_name() is None
        ami_entry.set_name("bar")
        assert ami_entry.get_name() == "bar"
        try:
            amidict.create_and_add_entry_with_term(term, replace=True)
            assert True, f"should overwrite duplicate entry"
        except AMIDictError as e:
            assert True, "should not raise duplicate error"

    # dictionary tests
    def test_minimal_dictionary(self):
        amidict = AmiDictionary.create_minimal_dictionary()
        assert amidict.get_version() is not None
        # amidict.check_validity()
        amidict.remove_attribute(VERSION)
        if amidict.get_version() is not None:
            raise AMIDictError("should have removed version")

        try:
            amidict.check_validity()
            raise AMIDictError("should fail is_valid()")
        except Exception as e:
            logging.info(f"failed test {e}")

    def test_get_duplicate_entries(self):
        """Dictionary has two entries for 'apical' but only one for 'cone'"""
        dup_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[DUPLICATE_ENTRIES])
        entries = dup_dict.get_lxml_entries()
        assert len(entries) == 4, "one duplicate term omitted"
        entries = dup_dict.find_entries_with_term("apical")
        assert entries is not None and len(entries) == 1
        entries = dup_dict.find_entries_with_term("zilch")
        assert entries is not None and len(entries) == 0

    def test_get_terms_from_valid_dictionary(self):
        """ETHNOBOT has no multiple entries'"""
        ethno_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        terms = ethno_dict.get_terms()
        assert terms is not None
        assert len(terms) == 8
        assert terms == ['anti-fumitory', 'adaptogen', 'homeopathy variable agent', 'ethnomedicinal agent',
                         'phytochemical agent', 'phytomedical agent', 'plant-extracted agent', 'lung-tonifying agent']

    def test_get_terms_from_invalid_dictionary(self):
        """DUPLICATE_ENTRIES has two entries for 'apical' and some missing terms"""
        dup_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[DUPLICATE_ENTRIES])
        terms = dup_dict.get_terms()
        assert terms == ['apical', 'flowering top', 'cone', 'pistil']

    # review dictionaries
    def test_mini_plant_part_is_valid(self):
        # pp_dict = AmiDictionary(setup_amidict[MINI_PLANT_PART])
        pp_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[MINI_PLANT_PART])
        if pp_dict is None:
            raise AMIDictError(f"test_dictionary_should_have_desc cannot read dictionary {pp_dict}")
        pp_dict.check_validity()

    def test_mini_mentha_tps_dict_is_valid(self):
        mentha_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[MINI_MENTHA])
        if mentha_dict is None:
            raise AMIDictError("cannot find/read mentha_dict")
        mentha_dict.check_validity()

    def test_ethnobot_dict_has_version(self):
        ethnobot_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        version = ethnobot_dict.get_version()
        assert version is not None
        assert AmiDictionary.is_valid_version_string(version)
        # assert ethnobot_dict.get_version() == "0.0.1"

    def test_ethnobot_dict_is_valid(self):
        logger.info(f" validating {ETHNOBOT_DICT}")
        ethnobot_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        ethnobot_dict.check_validity()
        # assert ethnobot_dict.get_version() == "0.0.1"

    def test_ethnobot_dict_has_8_entries(self):
        ethnobot_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        entries = ethnobot_dict.get_lxml_entries()
        assert len(entries) == 8

    def test_ethnobot_dict_entry_0_is_valid(self):
        ethnobot_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        entry0 = ethnobot_dict.get_lxml_entries()[0]
        AmiEntry.create_from_element(entry0).check_validity()

    def test_all_ethnobot_dict_entries_are_valid(self):
        ethnobot_dict = AmiDictionary.create_from_xml_file(self.create_file_dict()[ETHNOBOT_DICT])
        for entry in ethnobot_dict.get_lxml_entries():
            AmiEntry.create_from_element(entry).check_validity()

    # integrations

    def test_find_missing_wikidata_ids(self):
        ami_dict = AmiDictionary.create_from_xml_file(Resources.TEST_IPCC_CHAP02_ABB_DICT)
        lxml_entries = ami_dict.get_lxml_entries_with_missing_wikidata_ids()
        # missing_wikidata_ids = AmiEntry.get_wikidata_ids_for_entries(_entries)
        missing_wikidata_terms = AmiEntry.get_terms_for_lxml_entries(lxml_entries)
        assert missing_wikidata_terms == [

            'HFCs',
            'HCFCs',
            'CRF',
            'WMO',
            'NGHGI',
            'GWP',
            'FFI',
            'PBEs',
            'TCBA',
            'HCEs',
            'EBEs',
            'IBE',
            'RSD',
            'HDI',
            #            'CSP',
            'BECCS',
            'IAMs',
            # 'CDR',
            'ECR',
            'ETSs',
            #            'EVs',
            'ODSs',
            'HCS'
        ]

    def test_disambiguate_raw_wikidata_ids_in_dictionary(self):
        """
        find
        USABLE
        """
        ami_dict = AmiDictionary.create_from_xml_file(Resources.TEST_IPCC_CHAP02_ABB_DICT)
        _term_id_list = ami_dict.get_disambiguated_raw_wikidata_ids()
        assert len(_term_id_list) == 1
        assert _term_id_list[0] == ('GWP', ['Q901028'])

    #
    @unittest.skipUnless(VERYLONG, "lookup whole dictionaries")
    def test_lookup_missing_abbreviation_wikidata_ids_by_name(self):
        """
        scans dictionary for missing @wikidataID and searches wikidata by name/term
        USEFUL
        """
        ami_dict = AmiDictionary.create_from_xml_file(Resources.TEST_IPCC_CHAP02_ABB_DICT)
        lookup = ami_dict.lookup_missing_wikidata_ids()
        pprint.PrettyPrinter(indent=4).pprint(lookup.hits_dict)
        assert 15 <= len(lookup.hits_dict) <= 19
        """{   'Electric vehicles': {   'Q13629441': 'electric vehicle',
                             'Q17107666': 'Miles Electric Vehicles',
                             'Q1720353': 'Smith Electric Vehicles',
                             'Q5029961': 'Canadian Electric Vehicles',
                             'Q67371583': 'John Bradshaw Ltd.'},
    'Frequently Asked Questions': {   'Property:P9214': 'FAQ URL',
                                      'Q189293': 'FAQ',
                                      'Q76407407': 'Ffatrïoedd a busnesau a '
                                                   'gynorthwyir : cwestiynau '
                                                   'cyffredin = Supported '
                                                   'factories and businesses : '
                                                   'frequently asked '
                                                   'questions'},
    'Global Warming Potential': {'Property:P2565': 'global warming potential'},
    'Greenhouse Gas': {   'Q107315539': 'Greenhouse Gas Mitigation Workshop '
                                        '(2016)',
                          'Q167336': 'greenhouse gas',
                          'Q5604172': 'greenhouse gas emissions by the United '
                                      'Kingdom'},
"""

    @unittest.skipUnless(VERYLONG, "runs several chapters")
    def test_debug_chapter_dictionaries(self):
        self.debug_dict(dict_path=Resources.LOCAL_IPCC_CHAP07_ABB_DICT)
        self.debug_dict(dict_path=Resources.LOCAL_IPCC_CHAP07_MAN_DICT)
        self.debug_dict(dict_path=Resources.TEST_IPCC_CHAP08_ABB_DICT)
        self.debug_dict(dict_path=Resources.TEST_IPCC_CHAP08_MAN_DICT)

    @classmethod
    def debug_dict(cls, dict_path):
        logger.info(f"======={dict_path}=======")
        ami_dict = AmiDictionary.create_from_xml_file(dict_path)
        if ami_dict:
            lookup = ami_dict.lookup_missing_wikidata_ids()
            pprint.PrettyPrinter(indent=4).pprint(lookup.hits_dict)
        else:
            print(f"****Cannot find valid dict {dict_path}****")
            logging.error(f"Cannot find valid dict {dict_path}")

    @unittest.skipUnless(VERYLONG, "lookup whole dictionaries")
    def test_lookup_missing_manual_wikidata_ids_by_name(self):
        """
        scans dictionary for missing @wikidataID and searches wikidata by name/term
        USEFUL
        """
        ami_dict = AmiDictionary.create_from_xml_file(Resources.LOCAL_IPCC_CHAP07_MAN_DICT)
        lookup = ami_dict.lookup_missing_wikidata_ids()
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(lookup.hits_dict)
        assert 8 >= len(lookup.hits_dict) >= 6

    @unittest.skipUnless(VERYLONG, "lookup whole dictionaries")
    def test_lookup_missing_wikidata_ids_by_term(self):
        """
        scans dictionary for missing @wikidataID and searches wikidata by term
        USEFUL
        """
        ami_dict = AmiDictionary.create_from_xml_file(Resources.TEST_IPCC_CHAP02_ABB_DICT)
        lookup = ami_dict.lookup_missing_wikidata_ids(lookup_string=TERM)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(lookup.hits_dict)
        assert 28 >= len(lookup.hits_dict) >= 22


    # TODO set changes over time
    def test_get_property_ids(self):
        """gets properties af a dictionary entry"""
        words = ["limonene"]
        dictionary, _ = AmiDictionary.create_dictionary_from_words(
            words, "test", "created from words",wikilangs=["en", "de"])
        dictionary.add_wikidata_from_terms()
        pprint.pprint(lxml.etree.tostring(dictionary.root).decode("UTF-8"))
        assert len(dictionary.entries) == 1
        wikidata_page = dictionary.create_wikidata_page(dictionary.entries[0])
        property_ids = wikidata_page.get_property_ids()
        assert len(property_ids) >= 60
        id_set = set(property_ids)
        test_set = {'P31', 'P279', 'P361', 'P2067', 'P274', 'P233', 'P2054', 'P2101', 'P2128', 'P2199'}
        assert test_set.issubset(id_set)


    @unittest.skipUnless(CEV_EXISTS, "requires local CEVOpen")
    def test_invasive(self):
        """

        """


        INVASIVE_DIR = Path(LOCAL_CEV_OPEN_DICT_DIR, "invasive_species")
        assert INVASIVE_DIR.exists(), f"INVASIVE_DIR should exists {INVASIVE_DIR}"
        dictionary_file = Path(INVASIVE_DIR, "invasive_plant.xml")
        assert dictionary_file.exists(), f"dictionary_file should exist {dictionary_file}"
        SPARQL_DIR = Path(INVASIVE_DIR, "sparql_output")
        assert SPARQL_DIR.exists(), f"SPARQL_DIR should exist {SPARQL_DIR}"
        rename_file = False

        sparql_files = glob.glob(os.path.join(SPARQL_DIR, "sparql_*.xml"))

        sparql_files.sort()
        sparql2amidict_dict = {
            "image": {
                "id_name": "item",
                "sparql_name": "image_link",
                "dict_name": "image",
            },
            "map": {
                "id_name": "item",
                "sparql_name": "taxon_range_map_image",
                "dict_name": "image",
            },
            # "taxon": {
            #     "id_name": "item",
            #     "sparql_name": "taxon",
            #     "dict_name": "synonym",
            # }
        }
        AmiDictionary.apply_dicts_and_sparql(dictionary_file, rename_file, sparql2amidict_dict, sparql_files)
        # TODO needs assert

    # LONG
    @unittest.skip("VERY LONG, SPARQL")
    @unittest.skipUnless(CEV_EXISTS, "requires local CEVOpen")
    def test_plant_genus(cls):
        """
        """

        DICT_DIR = Path(LOCAL_CEV_OPEN_DICT_DIR, "plant_genus")
        assert DICT_DIR.exists(), f"DICT_DIR should exist {DICT_DIR}"
        dictionary_file = Path(DICT_DIR, "plant_genus.xml")
        assert dictionary_file.exists(), f"dictionary_file should exists {dictionary_file}"
        SPARQL_DIR = Path(DICT_DIR, "raw")
        assert SPARQL_DIR.exists(), f"SPARQL_DIR should exist {SPARQL_DIR}"
        rename_file = False

        sparql_files = glob.glob(os.path.join(SPARQL_DIR, "sparql_test_concatenation.xml"))

        sparql_files.sort()
        sparql2amidict_dict = {
            "image": {
                "id_name": "plant_genus",
                "sparql_name": "images",
                "dict_name": "image",
            },
            "map": {
                "id_name": "plant_genus",
                "sparql_name": "taxon_range_map_image",
                "dict_name": "map",
            },
            "wikipedia": {
                "id_name": "plant_genus",
                "sparql_name": "wikipedia",
                "dict_name": "wikipedia",
            },
        }
        AmiDictionary.apply_dicts_and_sparql(dictionary_file, rename_file, sparql2amidict_dict, sparql_files)

    @unittest.skipUnless(CEV_EXISTS, "requires local CEVOpen")
    def test_compound(cls):
        """
        ???
        """

        DICT_DIR = Path(LOCAL_CEV_OPEN_DICT_DIR, "eoCompound")
        assert DICT_DIR.exists(), f"DICT_DIR should exists {DICT_DIR}"
        dictionary_file = Path(DICT_DIR, "plant_compound.xml")
        assert (os.path.exists(dictionary_file)), f"dictionary_file should exist {dictionary_file}"
        SPARQL_DIR = Path(DICT_DIR, "raw")
        SPARQL_DIR = DICT_DIR
        assert SPARQL_DIR.exists(), f"SPARQL_DIR should exist {SPARQL_DIR}"
        rename_file = False

        sparql_files = glob.glob(os.path.join(SPARQL_DIR, "sparql_6.xml"))
        sparql_files.sort()
        sparql2amidict_dict = {
            "image": {
                "id_name": "item",
                "sparql_name": "t",
                "dict_name": "image",
            },
            "chemform": {
                "id_name": "item",
                "sparql_name": "chemical_formula",
                "dict_name": "chemical_formula",
            },
            "wikipedia": {
                "id_name": "plant_genus",
                "sparql_name": "wikipedia",
                "dict_name": "wikipedia",
            },
            # "taxon": {
            #     "id_name": "item",
            #     "sparql_name": "taxon",
            #     "dict_name": "taxon",
            # }
        }

        AmiDictionary.apply_dicts_and_sparql(dictionary_file, rename_file, sparql2amidict_dict, sparql_files)

    @unittest.skipUnless(CEV_EXISTS, "requires local CEVOpen")
    def test_plant_part_sparql(cls):
        """
        Takes WD-SPARQL-XML output (sparql.xml) and maps to AMIDictionary (eo_plant_part.xml)

        """
        # current dictionary does not need updating

        logger.debug(f"***test_plant_part")
        DICT_DIR = Path(LOCAL_CEV_OPEN_DICT_DIR, "eoPlantPart")
        DICT_DIR = Path(TEST_RESOURCE_DIR, "eoPlantPart")
        assert DICT_DIR.exists(), f"{DICT_DIR} should exist"
        dictionary_file = Path(DICT_DIR, "eoplant_part.xml")
        assert dictionary_file.exists(), f"dictionary_file should exist {dictionary_file}"
        SPARQL_DIR = Path(DICT_DIR, "raw")
        SPARQL_DIR = DICT_DIR
        assert SPARQL_DIR.exists(), f"SPARQL_DIR should exists {SPARQL_DIR}"
        rename_file = False

        sparql_files = glob.glob(os.path.join(SPARQL_DIR, "sparql.xml"))

        sparql_files.sort()
        sparql2amidict_dict = {
            "image": {
                "id_name": "item",
                "sparql_name": "image",
                "dict_name": "image",
            },
        }

        AmiDictionary.apply_dicts_and_sparql(dictionary_file, rename_file, sparql2amidict_dict, sparql_files)

    def test_merge_dicts_ipcc_same_chap(self):
        """test merge dictionaries from IPCC (heavy commonality)"""

        abb2_dict = AmiDictionary.create_from_xml_file(Resources.TEST_IPCC_CHAP02_ABB_DICT)
        abb2_set = abb2_dict.get_or_create_term_set()
        assert abb2_set == {
            'BECCS',
            #            'CBEs',
            #            'CDR',
            'CRF',
            #            'CSP',
            'EBEs', 'ECR',
            # 'EET',
            'ETSs',
            'EU ETS',
            #            'EVs',
            #            'F-gases', 'FAQs',
            'FFI',
            # 'GDP', 'GHG',
            'GTP',
            'GWP',
            #            'GWP100',
            'HCEs', 'HCFCs',
            'HCS', 'HDI', 'HFCs', 'IAMs',
            'IBE', 'LULUCF', 'NGHGI', 'ODSs',
            'PBEs',
            # 'PFCs',
            'RGGI', 'RSD',
            'TCBA',
            # 'UNFCCC',
            'WMO'
        }, f"abb2 set {abb2_set}"

        man2_dict = AmiDictionary.create_from_xml_file(
            Path(Resources.TEST_IPCC_CHAP02_DICT, "ip_3_2_emissions_man.xml"))
        man2_set = man2_dict.get_or_create_term_set()
        assert man2_set == {
            'CAIT', 'CEDS', 'CGTP', 'CO2-equivalent emission',
            'CRF', 'EDGAR', 'FAOSTAT', 'FFI', 'FOLU', 'Final Energy Demand', 'GTP', 'GWP',
            'GWP100', 'GtCO2eq', 'LULUCF', 'NMVOC',
            'PRIMAP', 'Paris Agreement', 'Primary Energy', 'Primary Energy Conversion',
            'SLCF', 'SRES', 'SSP', 'UNFCCC', 'WMO',
            'atmospheric lifetime', 'baseline scenario',
            'carbon budget', 'carbon pricing',
            'cumulative CO2 emissions', 'demand side solutions',
            'emission inventory', 'emission sectors',
            'emissions factor', 'emissions trajectory',
            'fluorinated gas', 'social discount rate',
            'top down atmospheric measurement'
        }, f"man2 set {man2_set}"

        # phrases
        phr2_dict = AmiDictionary.create_from_xml_file(
            Path(Resources.TEST_IPCC_CHAP02_DICT, "ip_3_2_emissions_phr.xml"))
        phr2_set = phr2_dict.get_or_create_term_set()
        assert phr2_set == {
            'BECCS', 'CBEs', 'CDR', 'CRF', 'CSP', 'EBEs', 'ECR', 'EET',
            'ETSs', 'EU ETS', 'EVs', 'F-gases',
            'FAQs', 'FFI', 'GDP', 'GHG', 'GTP', 'GWP', 'GWP-100', 'GWP100',
            'HCEs', 'HCFCs', 'HCS', 'HDI', 'HFCs', 'IAMs', 'IBE', 'LULUCF',
            'NGHGI', 'ODSs', 'PBEs', 'PFCs', 'RGGI', 'RSD', 'TCBA', 'UNFCCC', 'WMO'
        }

        # terms common to abbrev and manual
        abb_man_set = abb2_set.intersection(man2_set)
        assert len(abb_man_set) == 6, f"man2 set {len(abb_man_set)}"
        assert abb_man_set == {
            'GTP', 'FFI',
            #            'GWP', 'UNFCCC',
            'WMO', 'GWP', 'CRF', 'LULUCF'}


    def test_entries_have_ids(self):
        dict_file = Path(Resources.TEST_IPCC_DICT_DIR, "raw_linked_dict.xml")
        assert dict_file.exists(), f"file {dict_file} should exist"
        linked_dict = AmiDictionary.create_from_xml_file(dict_file)
        assert linked_dict is not None
        assert linked_dict.get_entry_count() == 17, f"found {linked_dict.get_entry_count()} entries"
        # assert linked_dict.get_lxml_entries_with_ids() == 2

    def test_entry_id(self):
        """
        Tests whether entries have ids, and (later) creates default values
        """
        dict_dir = Path(Resources.TEST_RESOURCES_DIR, "eoCompound")
        assert dict_dir.exists(), f"{dict_dir} should exist"
        ambig_dict_file = Path(dict_dir, "disambig.xml")
        assert ambig_dict_file.exists(), f"{ambig_dict_file} should exist"
        disambig_dict = AmiDictionary.create_from_xml_file(ambig_dict_file)
        assert disambig_dict is not None

        assert disambig_dict.get_entry_count() == 9, f"dictionary should have 9 entries"
        assert disambig_dict.get_entry_ids() == ['____alloaromadendrene']

    def test_dict_commands_COMMAND_OK(self):
        """
        prints help
        """
        amilib = AmiLib()
        amilib.run_command(["--help"])

        amilib.run_command(["DICT", "--help"])


    def test_search_with_dictionary_and_make_links_IMPORTANT(self):
        """
        uses a simple dictionary to search WG chapter (wg2/ch03) *html_with_ids)

        Returns
        -------


        """

        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", f"{self.HTML_WITH_IDS}.html")
        paras = HtmlLib._extract_paras_with_ids(chapter_file, count=1163)
        xml_dict_path = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", "climate_words.xml")
        dictionary = AmiDictionary.create_from_xml_file(xml_dict_path)
        assert dictionary is not None
        phrases = dictionary.get_terms()
        html_path = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", "climate_words.html")
        dictionary.create_html_write_to_file(html_path, debug=True)
        dictionary.location = html_path
        assert len(phrases) == 11
        para_phrase_dict = HtmlLib.search_phrases_in_paragraphs(paras, phrases, markup=html_path)
        chapter_elem = paras[0].xpath("/html")[0]
        chapter_outpath = Path(Resources.TEMP_DIR, "ipcc", "Chapter03", "marked_up.html", debug=True)
        HtmlLib.write_html_file(chapter_elem, chapter_outpath, debug=True)

    def test_search_with_dictionary_and_make_links_WORKFLOW(self):
        """
        uses a simple dictionary to search WG chapter (wg2/ch03) *html_with_ids)

        Returns
        -------


        """
        stem = "carbon_cycle"
        words_path = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}_edited.txt")
        assert words_path.exists()

        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ar6", "wg1", "Chapter05", f"{self.HTML_WITH_IDS}.html")
        assert chapter_file.exists()

        paras = HtmlLib._extract_paras_with_ids(chapter_file, count=1724)

        dictionary, outpath = AmiDictionary.create_dictionary_from_wordfile(words_path)
        assert dictionary is not None
        assert len(dictionary.get_terms()) == 43

        xml_dict_path = Path(Resources.TEMP_DIR, "dictionary", "climate", f"{stem}.xml")
        dictionary.create_html_write_to_file(xml_dict_path, debug=True)
        assert xml_dict_path.exists()

        html_dict_path = Path(Resources.TEMP_DIR, "dictionary", "climate", f"{stem}.html")
        dictionary.create_html_write_to_file(html_dict_path, debug=True)
        assert html_dict_path.exists()

        phrases = dictionary.get_terms()
        dictionary.location = html_dict_path
        assert len(phrases) == 43
        para_phrase_dict = HtmlLib.search_phrases_in_paragraphs(paras, phrases, markup=html_dict_path)

        # write marked_up html
        chapter_elem = paras[0].xpath("/html")[0]
        chapter_outpath = Path(Resources.TEMP_DIR, "ipcc", "wg1", "Chapter05", "marked_up.html", debug=True)
        HtmlLib.write_html_file(chapter_elem, chapter_outpath, debug=True)
        assert  chapter_outpath.exists()

    def test_search_with_dictionary_and_make_links_code(self):
        """
        uses a simple dictionary to search WG chapter (wg2/ch03) *html_with_ids) and add hyperlinks
        -------

        """
        stem = "carbon_cycle"
        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ar6", "wg1", "Chapter05", f"{self.HTML_WITH_IDS}.html")
        chapter_outpath = Path(Resources.TEMP_DIR, "ipcc", "wg1", "Chapter05", "marked_up.html", debug=True)
        FileLib.delete_file(chapter_outpath)
        html_dict_path = Path(Resources.TEMP_DIR, "dictionary", "climate", f"{stem}.html")

        AmiDictionary.read_html_dictionary_and_markup_html_file(
            chapter_file, chapter_outpath, html_dict_path=html_dict_path)
        assert chapter_outpath.exists()

    def test_search_with_dictionary_and_make_links_COMMANDLINE(self):
        """
        same logice and files as test_search_with_dictionary_and_make_links_CODE. Check that that runs
        """

        stem = "carbon_cycle"
        chapter_file = str(Path(Resources.TEST_RESOURCES_DIR, "ar6", "wg1", "Chapter05", f"{self.HTML_WITH_IDS}.html"))
        chapter_outpath = str(Path(Resources.TEMP_DIR, "ipcc", "wg1", "Chapter05", "marked_up.html", debug=True))
        FileLib.delete_file(chapter_outpath)
        html_dict_path = str(Path(Resources.TEMP_DIR, "dictionary", "climate", f"{stem}.html"))

        # commandline
        args = [
            "DICT",
            "--inpath", chapter_file,
            "--outpath", chapter_outpath,
            "--dict", html_dict_path,
            "--operation", MARKUP_FILE,
        ]
        logger.info(f"cmd> {' '.join(args)}")
        AmiLib().run_command(args)
        assert Path(chapter_outpath).exists()

    def test_args_help(self):
        args = [
            "DICT",
            "--help"
        ]
        AmiLib().run_command(args)

class AmiEntryTest(AmiAnyTest):
    """
    test functionality of AmiEntry
    """

    def dummy(self):
        pass


class ValidateTest(AmiAnyTest):
    """
    test validity of AmiEntry and AmiDictionary
    """

    def test_read_wellformed_dictionary(self):
        """test can create from XML string
        includes well-formed and non-well-formed XML
        """
        dict_str = """
        <dictionary title='foo'>
        </dictionary>
        """
        ami_dict = AmiDictionary.create_dictionary_from_xml_string(dict_str)
        assert ami_dict is not None

        assert ami_dict.root.tag == "dictionary"

        dict_str = """
        <diktionary title='foo'>
        </dictionary>
        """
        try:
            ami_dict = AmiDictionary.create_dictionary_from_xml_string(dict_str)
        except XMLSyntaxError as e:
            logger.warning(f"xml error {e}")

    def test_one_entry_dict_is_ami_dictionary(self):
        """require the attribute to be present but does not check value"""
        setup_dict = AmiDictionaryTest().create_file_dict()
        one_dict = setup_dict[ONE_ENTRY_DICT]
        assert type(one_dict) is AmiDictionary, f"fila is not AmiDictionary {one_dict}"

    def test_dict1_has_version_attribute(self):
        """require the version attribute to be present but does not check value"""
        setup_dict = AmiDictionaryTest().create_file_dict()
        one_dict = setup_dict[DICTFILE1]
        amidict = AmiDictionary.create_from_xml_file(Path(one_dict))
        version = amidict.get_version()
        assert version == STARTING_VERSION

    def test_dict1_with_missing_version_attribute_is_not_valid(self):
        """
        require the version attribute to have starting value
        """
        setup_dict = AmiDictionaryTest().create_file_dict()
        amidict = AmiDictionary.create_from_xml_file(Path(setup_dict[DICTFILE1]))
        version = amidict.get_version()
        assert version == STARTING_VERSION

    def test_one_entry_dict_has_version_attribute(self):
        """require the attribiute to be present but does not check value"""
        setup_dict = AmiDictionaryTest().create_file_dict()
        one_dict = setup_dict[ONE_ENTRY_DICT]
        assert one_dict is not None
        version = one_dict.get_version()
        assert version == "1.2.3"

    def test_dictionary_has_version(self):
        """require the attribute to be present but does not check value"""
        setup_dict = AmiDictionaryTest().create_file_dict()
        one_dict = setup_dict[ONE_ENTRY_DICT]
        version = one_dict.get_version()
        assert version is not None, "missing version"

    @unittest.skip("superseded by Validator")
    def test_dictionary_has_valid_version(self):
        """require the attribute to be present but does not check value"""
        setup_dict = self.setup()
        one_dict = setup_dict[ONE_ENTRY_DICT]
        validator = AmiDictValidator(one_dict)
        version = one_dict.get_version()
        # assert validator. f"invalid version {version}"

    def test_catch_invalid_version(self):
        minimal_dict = AmiDictionary.create_minimal_dictionary()
        try:
            minimal_dict.set_version("1.2.a")
            raise AMIDictError("should catch bad version error")
        except AMIDictError as e:
            """should catch bad version"""
            # logger.warning(f"caught expected error")

    def test_dict_has_xml_title(self):
        """has root dictionary element got title attribute?
        e.g. <dictionary title='dict1'> ..."""
        setup_dict = AmiDictionaryTest().create_file_dict()
        root = setup_dict[ROOT]
        assert root.attrib[TITLE] == "dict1"

    def test_dict_title_matches_filename(self):
        setup_dict = AmiDictionaryTest().create_file_dict()
        root = setup_dict[ROOT]
        last_path = setup_dict[DICTFILE1].stem
        logger.debug(last_path)
        assert root.attrib["title"] == last_path

    def test_validate_dictionary_created_from_words(self):
        """
        validate dictionary created from list of words
        """
        ami_dictionary, _ = AmiDictionary.create_dictionary_from_words(["curlicue", "bread"],
                                                                    title="test",
                                                                    desc="test dictionary")
        validator = AmiDictValidator(ami_dictionary)

    def test_validate_dictionary_created_from_wordfile(self):
        """
        validate dictionary created from list of words
        """
        file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "carbon_cycle.txt")
        ami_dictionary, _ = AmiDictionary.create_dictionary_from_wordfile(file,
                                                                    title="test",
                                                                    desc="test dictionary")
        validator = AmiDictValidator(ami_dictionary)


    def test_xml_dictionary(self):
        """
        reads previously created XML dictionary
        """
        file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "xml", "climate_words_dict.xml")
        ami_dictionary = AmiDictionary.create_from_xml_file(file)
        validator = AmiDictValidator(ami_dictionary)


class DictionaryCreationTest(AmiAnyTest):
    """
    test methods which create dictionaries
    (from lists of strings, files, urls, sparql etc.

    """

    def test_read_wellformed_dictionary(self):
        """test can create from XML string
        includes well-formed and non-well-formed XML
        """
        dict_str = """
        <dictionary title='foo'>
        </dictionary>
        """
        ami_dict = AmiDictionary.create_dictionary_from_xml_string(dict_str)
        assert ami_dict is not None

        assert ami_dict.root.tag == "dictionary"

        dict_str = """
        <diktionary title='foo'>
        </dictionary>
        """
        try:
            ami_dict = AmiDictionary.create_dictionary_from_xml_string(dict_str)
        except XMLSyntaxError as e:
            logger.warning(f"xml error {e}")


    def test_dictionary_creation(self):
        """
        unit test
        """
        amidict = AmiDictionary.create_minimal_dictionary()
        assert amidict is not None
        assert amidict.get_version() == STARTING_VERSION


    def test_create_dictionary_from_list_of_strings_in_file(dictionary
#                                                                         , words_txt, entry_count
                                                                         ):
        """
        read file with lists of strings and create AmiDictionary
        """
        dictionary = "climate"
        words_txt = "ar5_wg3_food_security_words.txt"
        entry_count = 60
        dictionary_in_dir = Path(Resources.TEST_RESOURCES_DIR, "dictionary")
        out_dict_dir = Path(Resources.TEMP_DIR, "dictionary", "climate")
        words_file = Path(dictionary_in_dir, dictionary, words_txt)
        assert words_file.exists(), f"{words_file} should exist"
# create dictionary without save or lookup
        words_dictionary, _ = AmiDictionary.create_dictionary_from_wordfile(wordfile=words_file)
        assert words_dictionary is not None, (f"words dictionary from {words_file} must not be None")
        assert words_dictionary.get_entry_count() == entry_count, f"should have {entry_count} entries , found {words_dictionary.get_entry_count()}"

# parametrize doesn't work easily withe unittest subclasses
    # @pytest.mark.parametrize("dictionary,words_txt,entry_count",
    #                          [("climate", "ar5_wg3_food_security_words.txt", 60)])
    # def test_create_dictionary_from_list_of_strings_in_file_parameterize(dictionary, words_txt, entry_count):
    #     """
    #     read file with lists of strings and create AmiDictionary
    #     """
    #     dictionary_in_dir = Path(Resources.TEST_RESOURCES_DIR, "dictionary")
    #     out_dict_dir = Path(Resources.TEMP_DIR, "dictionary", "climate")
    #     words_file = Path(dictionary_in_dir, dictionary, words_txt)
    #     assert words_file.exists(), f"{words_file} should exist"
    #     # create dictionary without save or lookup
    #     words_dictionary, _ = AmiDictionary.create_dictionary_from_wordfile(wordfile=words_file)
    #     assert words_dictionary is not None, (f"words dictionary from {words_file} must not be None")
    #
    #     assert words_dictionary.get_entry_count() == entry_count, f"should have {entry_count} entries , found {words_dictionary.get_entry_count()}"

    def test_createdictionary_from_list_of_strings_in_file_and_lookup_wikidata(self):
# add title, description, and save
        out_dict_dir = Path(Resources.TEMP_DIR, "dictionary", "climate")
        words_file = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate",
                          "ar5_wg3_food_security_words.txt")
        max_entries = 2 # to reduce time

        description = "food security terms in AR5_WG3_ch_5 selected by Anmol Negi"
        # add title, description, and save
        description = "food security terms in AR5_WG3_ch_5 selected by Anmol Negi and wikidata lookup"
        words_dictionary, outfile = AmiDictionary.create_dictionary_from_wordfile(
            wordfile=words_file, desc=description, title="food_security", outdir=out_dict_dir, wikidata=True,
            max_entries=max_entries, debug=True)
        assert words_dictionary is not None, f"words dictionary from {words_file} must not be None"
        assert words_dictionary.get_entry_count() == max_entries, \
            f"should have {max_entries} entries , found {words_dictionary.get_entry_count()}"
        assert outfile.exists(), f"should create {outfile}"


    def test_process_args_build_dictionary_add_wikidata_CMD_OK(self):
        """commandline
        reads list of words, creates a dictionary, looks up Wikidata
        Wikidata has <entry>s in in format:
    <entry name="UNFCCC" term="UNFCCC">
    <div qid="Q21707860">
        <a href="wikidataURL/Q21707860">Wikidata</a>
        <p role="title">Paris Agreement</p>
        <p role="description">international agreement from 12 December 2015 within the United Nations Framework Convention on Climate Change (UNFCCC) dealing with greenhouse gas emissions mitigation, adaptation and finance starting in the year 2020</p>
    </div>
    <div qid="Q208645">
        <a href="wikidataURL/Q208645">Wikidata</a>
        <p role="title">United Nations Framework Convention on Climate Change</p>
        <p role="description">international treaty</p>
    </div>
    ...

        Note that wikidata lookup does not necessarily put the best answers first
        """
        amilib = AmiLib()
        title = "small_2"
        title_path = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{title}.txt")
        assert title_path.exists(), f"{title_path} should exist"
        title_txt = f"{title_path}"
        logger.debug(f"words {title_txt}")
        with open(title_txt, "r") as f:
            logger.debug(f"words ==> {f.readlines()}")
        title_dict = Path(Resources.TEMP_DIR, "words", f"{title}_dict.xml")
        FileLib.delete_file(title_dict)

        word_xml = f"{Path(Resources.TEMP_DIR, '{title}.xml')}"
        args = ["DICT",
                "--words", f"{title_path}",
                "--dict", f"{title_dict}",
                "--wikidata"
                ]
        logger.debug(f" s2 {args}")
        amilib.run_command(args)
        assert Path(title_dict).exists(), f"should write dictionary {title_dict}"
        print(f"wrote {title_dict}")

    # integrations
    def test_create_dictionary_from_list_of_string(self):
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        title = "foobar"
        directory = None
        amidict, _ = AmiDictionary.create_dictionary_from_words(terms, title)
        assert amidict is not None
        title = amidict.root.attrib[TITLE]
        assert title == "foobar"

    def test_create_dictionary_from_list_of_string_and_save(self):
        """
        Create dictionary from list of strings (no lookup)
        """
        terms = ["acetone", "benzene", "chloroform", "DMSO", "ethanol"]
        title = "solvents"
        temp_dir = Path(AmiAnyTest.TEMP_DIR, "dictionary")
        temp_dir.mkdir(exist_ok=True, parents=True)
        amidict, dictfile = AmiDictionary.create_dictionary_from_words(terms, title=title, outdir=temp_dir)
        outfile = Path(temp_dir, title + ".xml")
        assert Path(dictfile) == Path(temp_dir, title + ".xml") and os.path.exists(dictfile)
        assert amidict.get_entry_count() == 5

    def test_make_dict_from_file_CMD_OK(self):

        amilib = AmiLib()
        words_file = Path(TEST_RESOURCE_DIR, "wordlists", "climate_words.txt")
        dictfile = Path(Resources.TEMP_DIR, "words", "climate_words.xml")
        expected_count = 11
        FileLib.delete_file(dictfile)
        amilib.run_command(["DICT",
                            "--words", words_file,
                            "--dict", dictfile
                            ])
        assert Path(dictfile).exists()
        ami_dictionary = AmiDictionary.create_from_xml_file(dictfile)
        assert (c := ami_dictionary.get_entry_count()) == expected_count, \
            f"dictionary should contain {expected_count} found {c}"

    def test_make_dict_from_words_CMD_OK(self):
        amilib = AmiLib()
        words_file = Path(TEST_RESOURCE_DIR, "wordlists", "climate_words.txt")
        dictfile = Path(Resources.TEMP_DIR, "words", "climate_words.xml")
        expected_count = 1
        FileLib.delete_file(dictfile)
        amilib.run_command(["DICT",
                            "--words", "bread",
                            "--dict", dictfile
                            ])
        assert Path(dictfile).exists()
        ami_dictionary = AmiDictionary.create_from_xml_file(dictfile)
        assert (c := ami_dictionary.get_entry_count()) == expected_count, \
            f"dictionary should contain {expected_count} found {c}"

    def test_make_dict_from_words(self):
        """
        filas on "kangaroo"
        Reason unknown
        """
        amilib = AmiLib()
        dictfile = Path(Resources.TEMP_DIR, "words", "kangaroo.xml")
        expected_count = 1
        FileLib.delete_file(dictfile)
        amilib.run_command(["DICT",
                            "--words", "kangaroo",
                            "--dict", dictfile,
                            ])
        assert Path(dictfile).exists()
        ami_dictionary = AmiDictionary.create_from_xml_file(dictfile)
        assert (c := ami_dictionary.get_entry_count()) >= expected_count, \
            f"dictionary should contain {expected_count} found {c}"


    def test_create_dictionary_from_csv(self):
        """This does lookup, unfortunately Wikidata lookup changes as terms are added so this test is a mess"""
        csv_term_file = Path(Resources.TEST_IPCC_CHAP08_DICT, "urban_terms_1.csv")
        assert os.path.exists(str(csv_term_file)), f"csv_term_file should exist {csv_term_file}"
        keyword_dict = AmiDictionary.create_dictionary_from_csv(csv_term_file, col_name='keyword/phrase',
                                                                title="urban_terms_1")
        print(f"keyword_dict {keyword_dict}")
        entry = keyword_dict.get_first_ami_entry()
        assert entry.get_term() == "urbanization"
        assert entry.get_wikidata_id() == "Q161078" or entry.get_wikidata_id() == 'Q1508'
        assert len(keyword_dict.entries) == 1
        root_elem = keyword_dict.root
        assert root_elem.tag == 'dictionary'
        entry0 = root_elem.xpath("entry")[0]
        assert entry0.attrib["desc"] == 'highly urbanized city in Metro Manila, Philippines'
        # assert entry0.attrib["desc"] == 'longterm population movements (shift) from rural to urban areas'
        assert entry0.attrib["name"] == 'urbanization'
        # assert str(root) == \
        #        '<dictionary title="urban_terms_1"><entry name="urbanization" term="urbanization" wikidataID="Q161078" wikidataURL="https://www.wikidata.org/entity/Q161078" desc="longterm population movements (shift) from rural to urban areas;gradual increase in the proportion of people living in urban areas, and the ways in which each society adapts to the change;process by which towns and cities are formed and become larger"><wikidataHit type="wikidata_hits">Q5381005</wikidataHit><wikidataHit type="wikidata_hits">Q23580084</wikidataHit><wikidataHit type="wikidata_hits">Q2608153</wikidataHit><wikidataHit type="wikidata_hits">Q95443723</wikidataHit></entry></dictionary>'

    def test_validate_linked_dict(self):
        """
        tests a veriety of exploratory concepts such as inter- and intra-dictionary links
        DEVELOP 2022-12
        """
        dict_path = Path(Resources.TEST_IPCC_DICT_DIR, "raw_linked_dict.xml")
        assert dict_path.exists(), f"{dict_path} should exist"
        dictx = AmiDictionary.create_from_xml_file(dict_path)
        assert dictx is not None
        assert dictx.get_entry_count() == 17, f"dictionary has {dictx.get_entry_count()} entries"
        assert dictx.get_version() == '0.0.5', f"dictionary has version {dictx.get_version()}"
        terms = dictx.get_terms()
        assert len(terms) > 0, f"found {len(terms)}"
        assert terms == ['carbon budget',
                         'ffi',
                         'folu',
                         'fluorinated gas',
                         'carbon pricing',
                         'edgar',
                         'cait',
                         'ceds',
                         'crf',
                         'emissions factor',
                         'emission inventory',
                         'emission sectors',
                         'gwp100',
                         'slcf',
                         'cgtp',
                         'co2-equivalent emission',
                         'baseline scenario'], f'found {terms}'
    def test_create_dictionary_from_sparql(self):
        """
        read spqrql file and create dictionary
        then update from another sparql file
        """
        # PLANT = os.path.join(PHYSCHEM_RESOURCES, "plant")
        PLANT = os.path.join(Resources.TEST_RESOURCES_DIR, "plant")
        sparql_file = os.path.join(PLANT, "plant_part_sparql.xml")
        dictionary_file = os.path.join(PLANT, "eoplant_part.xml")
        assert Path(sparql_file).exists(), f"sparql_file should exist {sparql_file}"
        assert Path(dictionary_file).exists(), f"dictionary_file should exist {dictionary_file}"
        """
        <result>
            <binding name='item'>
                <uri>http://www.wikidata.org/entity/Q2923673</uri>
            </binding>
            <binding name='image'>
                <uri>http://commons.wikimedia.org/wiki/Special:FilePath/White%20Branches.jpg</uri>
            </binding>
        </result>
"""
        sparql_to_dictionary = {
            "id_name": "item",
            "sparql_name": "image",
            "dict_name": "image",
        }
        dictionary = AmiDictionary.create_from_xml_file(dictionary_file)
        wikidata_sparql = WikidataSparql(dictionary)
        wikidata_sparql.update_from_sparql(sparql_file, sparql_to_dictionary)
        outdir = Path(AmiAnyTest.TEMP_DIR, "sparql")
        outdir.mkdir(exist_ok=True)
        dictionary.write_to_dir(outdir)
        outpath = Path(outdir, "eoplant_part.xml")
        assert outpath.exists(), f"{outpath} should have been written"

    @unittest.skipUnless(False, "LONG DOWNLOAD")
    def test_create_dictionary_terpenes(self):
        words = ["limonene", "alpha-pinene", "Lantana camara"]
        description = "created from words"
        title = "test"
        dictionary, _ = AmiDictionary.create_dictionary_from_words(words, title=title, desc=description, wikidata=True)
        assert len(dictionary.entries) == 3
        first_entry = dictionary.get_first_ami_entry()
        term = first_entry.term
        assert term == "limonene", f"first term is {term}"

    # @unittest.skip("LONG")
    def test_create_dictionary_from_list_of_string_and_add_wikidata(self):
        terms = ["acetone",
                 "chloroform",
                 # "DMSO",
                 # "ethanol"
                 ]
        amidict, _ = AmiDictionary.create_dictionary_from_words(terms, title="solvents", wikidata=True)
        temp_dir = Path(AmiAnyTest.TEMP_DIR, "dictionary")
        dictfile = amidict.write_to_dir(temp_dir)

        with open(dictfile, "r") as f:
            dict_text = f.read()
        dict_text = re.sub("date=\"[^\"]*\"", "date=\"TODAY\"", dict_text)

        # note, the date is stripped as it changes with each run
        text1 = """<dictionary version="0.0.1" title="solvents" encoding="UTF-8">
      <metadata user="pm286" date="TODAY"/>
      <entry term="acetone" wikidataID="Q49546" description="chemical compound"/>
      <entry term="chloroform" wikidataID="Q172275" description="chemical compound"/>
    </dictionary>
    """
        # assert text1 == dict_text, f"{text1} != {dict_text}"
        # TODO remove user from metadata

    def test_create_dictionary_from_list_of_string(self):
        terms = ["foo", "bar", "plugh", "xyzzy", "baz"]
        title = "foobar"
        directory = None
        amidict, _ = AmiDictionary.create_dictionary_from_words(terms, title)
        assert amidict is not None
        title = amidict.root.attrib[TITLE]
        assert title == "foobar"

    def test_create_dictionary_from_list_of_string_and_save(self):
        """
        Create dictionary from list of strings (no lookup)
        """
        terms = ["acetone", "benzene", "chloroform", "DMSO", "ethanol"]
        title = "solvents"
        temp_dir = Path(AmiAnyTest.TEMP_DIR, "dictionary")
        temp_dir.mkdir(exist_ok=True, parents=True)
        amidict, dictfile = AmiDictionary.create_dictionary_from_words(terms, title=title, outdir=temp_dir)
        outfile = Path(temp_dir, title + ".xml")
        assert Path(dictfile) == Path(temp_dir, title + ".xml") and os.path.exists(dictfile)
        assert amidict.get_entry_count() == 5

    def test_create_dictionary_from_list_of_string_save_and_compare(self):
        terms = ["acetone", "benzene", "chloroform", "DMSO", "ethanol"]
        temp_dir = Path(AmiAnyTest.TEMP_DIR, "dictionary")
        amidict, dictfile = AmiDictionary.create_dictionary_from_words(terms, title="solvents", outdir=temp_dir)
        with open(dictfile, "r") as f:
            dict_text = f.read()
        dict_text = re.sub("date=\"[^\"]*\"", "date=\"TODAY\"", dict_text)
        assert len(dict_text) > 200, "lines of dict_text"
        assert type(dict_text) is str, f"{type(dict_text)}"
        # note, the date is nstripped as it changes with each run
        text1 = """<dictionary version="0.0.1" title="solvents" encoding="UTF-8">
      <metadata user="pm286" date="TODAY"/>
      <entry term="acetone"/>
      <entry term="benzene"/>
      <entry term="chloroform"/>
      <entry term="DMSO"/>
      <entry term="ethanol"/>
    </dictionary>
    """
        # assert text1 == dict_text, f"{text1} != {dict_text}"
        # TODO remove user from metadata

    def test_create_dictionary_from_url(self):
        """lookup entry in Github repository
        note: depends on INTERNET"""
        mentha_url = "https://raw.githubusercontent.com/petermr/pyami/main/py4ami/resources/amidicts/mentha_tps.xml"
        mentha_dict = AmiDictionary.create_dictionary_from_url(mentha_url)
        assert len(mentha_dict.get_lxml_entries()) == 1
        assert mentha_dict.get_first_ami_entry().get_term() == "1,8-cineole synthase"
        assert mentha_dict.get_version() == "0.0.3"

    def test_make_dict_from_words_and_add_wikimedia_image(self):
        """
        Reason unknown
        """
        amilib = AmiLib()
        dictfile = Path(Resources.TEMP_DIR, "words", "kangaroo.xml")
        expected_count = 1
        FileLib.delete_file(dictfile)
        amilib.run_command(["DICT",
                            "--words", "kangaroo",
                            "--dict", dictfile,
                            ])
        assert Path(dictfile).exists()
        ami_dictionary = AmiDictionary.create_from_xml_file(dictfile)
        assert (c := ami_dictionary.get_entry_count()) >= expected_count, \
            f"dictionary should contain {expected_count} found {c}"

    def test_make_dict_from_wordlist_add_figures(self):
        stems = [
            # "breward",
            "carbon_cycle_noabb",
            # "chap2",
            # "chap5",
            # "chap6_7_8",
            # "food_ecosystem",
            # "human_influence",
            # "inews15",
            # "non_wikipedia",
            # "poverty",
            # "small_2",
            # "water_cyclone"
            ""

            ]

        for stem in stems:
            logger.info(f"creating figure entries for {stem}")
            self.create_dict_for_word_file(stem, wiktionary=True)

    def test_more_words(self):
        pass

    def create_dict_for_word_file(self, stem, wiktionary=True, input_file=None, output_dict=None):
        """
        Reads a wordlist file and creates output dictionary with figures
        :param stem: stem of files, also used as title
        :param input_file: if None, defaults to TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt"
        :param output_dict: if None, defaults to TEMP_DIR, "words", "html", f"{stem}.html"

        """
        if stem is None or stem.strip() == "":
            logger.error("no title given for dictionary")
            return None
        if input_file is None:
            input_file = Path(Resources.TEST_RESOURCES_DIR, "wordlists", f"{stem}.txt")
        if output_dict is None:
            output_dict = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")


        args = [
            "DICT",
            "--words", input_file,
            "--dict", output_dict,
            "--figures", "wikipedia",
            "--title", stem,
        ]
        if wiktionary:
            args.append("--wiktionary")

        AmiLib().run_command(args)
        assert Path(output_dict).exists()

    def test_make_dict_with_figures(self):
        stem = "with_figures1"
        output_dict = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")

        words = [
            "albedo",
            "ablation",
        ]
        args = [
            "DICT",
            "--words", words,
            "--dict", output_dict,
            "--title", stem,
            "--figures", "wikipedia",
        ]
        AmiLib().run_command(args)
        assert Path(output_dict).exists()

    def test_disambiguation(self):
        stem = ("disambiguation")
        output_dict = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.html")

        args = [
            "DICT",
            "--words",
            "stubble",
            "anthropogenic",
            "--dict", output_dict,
            # "--figures",
        ]
        AmiLib().run_command(args)
        assert Path(output_dict).exists()

    def test_create_dict_with_wikimedia_descriptions(self):
        """
        from commandline add descriptions to ditionary entries from wikimedia sources
        """
        stem = "parijat"
        output_dict = Path(Resources.TEMP_DIR, "words", "html", f"{stem}.xml")

        args = [
            "DICT",
            "--words",
            stem,
            "--description",
            "wikipedia",
            "wikidata",
            "wiktionary",
            "--dict", output_dict,
        ]
        AmiLib().run_command(args)
        assert Path(output_dict).exists()


class IPCCDictTest(AmiAnyTest):
    def test_ipcc_dictionaries_from_URL(self):
        """
        read a number of IPCC dictionaries from URL and test their validity.
        Maybe later move code to dictionary project
        """
        WG3_ROOT = "https://raw.githubusercontent.com/petermr/semanticClimate/main/ipcc/ar6/wg3"
        dictionary_names = [
            "Chapter02/dict/ip_3_2_emissions_abb.xml", "Chapter07/dict/ip_3_7_agri_abb.xml",
            "wg2_03/dict/ip_3_3_longmitig_abb.xml", "Chapter08/dict/ip_3_8_urban_abb.xml",
            "Chapter05/dict/ip_3_5_socmitig_abb.xml", "Chapter17/dict/ip_3_17_sustdev_abb.xml",
            "Chapter06/dict/ip_3_6_energy_abb.xml"
        ]

        for dictionary_name in dictionary_names:
            url = WG3_ROOT + "/" + dictionary_name
            print(f" url {url}")
            try:
                dictionary = AmiDictionary.create_dictionary_from_url(url)
            except Exception as e:
                print(f"cannot download dictionary {url} beacuse {e}")

    @unittest.skipUnless(Path(IPCC_DICT_ROOT).exists(), f"requires checked out IPCC dictionaries {IPCC_DICT_ROOT}")
    def test_ipcc_dictionaries_from_file(self):
        """
        read a number of IPCC dictionaries from LOCAL (PMR-only) files and test their validity.
        Maybe later move codeto dictionary project
        """
        dictionary_names = [
            "Chapter02/dict/ip_3_2_emissions_abb.xml",
            "Chapter07/dict/ip_3_7_agri_abb.xml",
            # "wg2_03/dict/ip_3_3_longmitig_abb.xml",
            "Chapter08/dict/ip_3_8_urban_abb.xml",
            "Chapter05/dict/ip_3_5_socmitig_abb.xml",
            "Chapter17/dict/ip_3_17_sustdev_abb.xml",
            "Chapter06/dict/ip_3_6_energy_abb.xml"
        ]
        for dictionary_name in dictionary_names:
            dict_file = Path(IPCC_DICT_ROOT, dictionary_name)
            print(f"reading {dict_file}")
            if not dict_file.exists():
                logger.warning(f"dict file does not exist {dict_file}")
                continue
            try:
                dictionary = AmiDictionary.read_dictionary(dict_file)
                assert dictionary is not None, f"reading from {dict_file}"
                assert dictionary.get_entry_count() > 0
            except Exception as e:
                print(f"cannot read dictionary {dict_file} beacuse {e}")

# ======================= helpers =====================
    def teardown(self):
        dict1_root = None



def main(argv=None):
    print(f"running PDFArgs main")
    pdf_args = AmiDictArgs()
    try:
        pdf_args.parse_and_process()
    except Exception as e:
        print(traceback.format_exc())
        print(f"***Cannot run pyami***; see output for errors: {e}")


if __name__ == "__main__":
    main()
else:
    pass


def main():
    pass
