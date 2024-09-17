import ast
import copy
import logging
import os
import re
import urllib.request
from collections import Counter
from enum import Enum
from pathlib import Path
from shutil import copyfile
from urllib.error import URLError

import lxml
import pandas as pd
from lxml import etree
from lxml import etree as ET
from lxml.etree import _Element, Element
from lxml.html import HTMLParser

from amilib.ami_html import HtmlUtil, CSSStyle, H_A, H_SPAN, H_BODY, H_DIV, H_UL, H_LI, A_ID, \
    A_HREF, A_NAME, A_TITLE, A_TERM
from amilib.constants import LOCAL_CEV_OPEN_DICT_DIR, LOCAL_OV21_DIR, LOCAL_DICT_AMI3
from amilib.dict_args import AmiDictArgs, SYNONYM, WIKIPEDIA
from amilib.file_lib import FileLib
# local
from amilib.util import Util
from amilib.wikimedia import WikidataSparql, WikidataLookup, WikidataPage, WikipediaPage, WiktionaryPage
from amilib.ami_html import HtmlLib

# elements in amidict
DICTIONARY = "dictionary"
ENTRY = "entry"
IMAGE = "image"
LINK = "link"
RAW = "raw"
TITLE = "title"

# attributes in amidict
AMI_ENTRY = "ami_entry"
DESC = "desc" # description attribute in <dictionary> or <entry>
DEFINITION = "definition"  # one-sentence definition for entry
DESCRIPTION = "description"  # description attribute in <dictionary> or <entry> (often paragraph)

NAME = "name" # non-lexical name for entry (maybe obsolete
ROLE = "role"
TERM = "term" # exact term for entry (includes case and spaces)
WIKIDATA_ID = "wikidataID" # primary ID for entry where it exists
WIKIDATA_URL = "wikidataURL" # link to Wikidata entry
WIKIDATA_SITE = "https://www.wikidata.org/entity/" # URL of Wikidata site
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/" # bases of English Wikipedia
WIKIPEDIA_PAGE = "wikipediaPage" # container for whole Wikipedia page??
TYPE = "type"
ANY = "ANY"
VERSION = "version"
WIKIDATA_HITS = "wikidata_hits" # container for Wikidata lookup hits
WIKIDATA_HIT = "wikidataHit" # wikidata hit

# constants
UTF_8 = "UTF-8"

# languages
LANG_UR = "ur"

# elements

# logger = logging.getLogger("ami_dict")
logger = Util.get_logger(__name__)


# class syntax
class DictValue(Enum):
    NOT_LOOKED_UP = "notLookedUp",
    NOT_FOUND = "notFound",
    AMBIGUOUS = "ambiguous",


"""
work with lxml Elements as far as possible, and only wrap as Ami* objects when thos functions
are needed. Gradually increasing specific names (e.g. _lxml_entry). I know it's not pythonic
but it stops me making errors
"""

class AmiEntry:
    """
    wraps the HTML element  representing the entry and provides access and mutatiom
    """
    TAG = ENTRY

    TERM_A = TERM
    DESCRIPTION_A = DESCRIPTION
    NAME_A = NAME
    WIKIDATA_A = WIKIDATA_ID
    WIKIPEDIA_A = WIKIPEDIA_PAGE

    REQUIRED_ATTS = {TERM_A}
    OPTIONAL_ATTS = {DESCRIPTION_A, NAME_A, WIKIDATA_A, WIKIPEDIA_A}
    ALLOWED_ATTS = REQUIRED_ATTS.union(OPTIONAL_ATTS)
    assert len(ALLOWED_ATTS) == 5

    def __init__(self):
        self.element = None

    @classmethod
    def create_from_element(cls, entry_element):
        """create from raw XML element (wraps element)
        :param entry_element: directly constructed from dictionary files or constructed
        :return: AmiEntry
        """
        ami_entry = AmiEntry()
        ami_entry.element = entry_element
        return ami_entry

# AmiEntry

    @classmethod
    def create_lxml_entry_from_term(cls, term):
        """create lxml entry element
        :param term: creates @term attribute
        :return: lxml entry element with @term
        """
        assert term is not None
        entry_element = lxml.etree.Element(ENTRY)
        entry_element.attrib[TERM] = term
        return entry_element

    @property
    def name(self):
        return self.element.get(NAME)

    @property
    def term(self):
        return self.element.get(TERM)

    @property
    def wikidata_id(self):
        return self.element.get(WIKIDATA_ID)

    @property
    def get_wikipedia_page(self):
        return self.element.get(WIKIPEDIA)

    # AmiEntry

    """not tested"""
    def get_synonyms(self):
        """list of child synonym objects"""
        synonyms = [] if self.element is None else self.element.xpath("./" + AmiSynonym.TAG)
        return [AmiSynonym(s) for s in synonyms]

    def get_synonym_by_language(self, lang):
        synonyms = self.get_synonyms()
        for synonym in synonyms:
            if lang == synonym.element.attrib[XML_LANG]:
                return synonym
        return None

    def add_term(self, term):
        self.element.attrib[TERM] = term

    def get_term(self):
        term = self.element.attrib[TERM]
        return term

    # AmiEntry

    @classmethod
    def add_name(cls, lxml_entry_element, name):
        assert type(lxml_entry_element) is _Element, f"found {type(lxml_entry_element)}"
        assert lxml_entry_element is not None
        assert lxml_entry_element.tag == ENTRY
        lxml_entry_element.attrib[NAME] = name

    def set_name(self, name):
        AmiEntry.add_name(self.element, name)

    # @classmethod
    # def get_name(cls, entry):
    #     return AmiEntry.get_attribute_value(entry, NAME)

    def get_name(self):
        return AmiEntry.get_attribute_value(self.element, NAME)

    @classmethod
    def get_attribute_value(cls, element, attname):
        if attname not in element.attrib:
            return None
        else:
            return element.attrib[attname]

    def set_wikidata_id(self, idx):
        """set wikidataID, id must be Pddd... or Q... """
        if idx is None or not re.match("[PQ]\\d+", idx):
            raise AMIDictError(f"wikidata id {idx} must be Qddd... or Pddd...")
        self.set_attribute(WIKIDATA_ID, idx)

    # AmiEntry

    def set_description(self, desc):
        """set description attribute, can be anything"""
        if desc:
            self.set_attribute(DESCRIPTION, desc)

    def get_description(self):
        return self.get_attribute_value(DESCRIPTION)

    def check_validity(self):
        self.check_valid_attributes()
        self.check_valid_children()

    # AmiEntry

    def check_valid_attributes(self):
        attribute_names = list(self.element.attrib)
        assert attribute_names is not None
        # assert str(attributes) == "['name']", f"attributes {attributes}"
        # assert len(attributes) == 2, f" ATTS {attributes}"
        for attribute_name in attribute_names:
            # msg = f"ATT {attribut}"
            assert type(attribute_name) is str
            assert attribute_name in AmiEntry.ALLOWED_ATTS, f"attribute {attribute_name} is not allowed in <entry>"
            self.validate_attribute(WIKIDATA_ID)

    def check_valid_children(self):
        if False:
            for child in self.element:
                assert child.tag in self.ELEMENT_CHILD_TAGS

    # AmiEntry

    def get_synonyms(self):
        """create AmiSynonyms from <synonym> children
        :return: list of AmiSynonyms created from children
        """
        ami_synonyms = []
        synonym_elements = self.element.xpath(f"./{SYNONYM}")
        for synonym_element in synonym_elements:
            ami_synonyms.append(AmiSynonym.create_from_element(synonym_element))
        return ami_synonyms

    def get_raw_child_wikidata_ids(self):
        """
        for single child of form <raw wikidataID = [Q1, Q2...]
        :return: list of ids, else []
        """
        raw_child = self.get_single_raw_child_element()
        if raw_child is None:
            return []
        wikidata_id_att = raw_child.get(WIKIDATA_ID)
        wikidata_ids = ast.literal_eval(wikidata_id_att) if wikidata_id_att else []
        return wikidata_ids

    def get_single_raw_child_element(self):
        """
        :return: <raw> child of element if exactly 1, else None
        """
        raw_children = self.get_raw_child_elements()
        raw_child = raw_children[0] if len(raw_children) == 1 else None
        return raw_child

    # AmiEntry

    def get_raw_child_elements(self):
        """
        get all <raw> child elements of AmiEntry.element
        :return: list of elements (may be zero-length never None)
        """
        raw_children = self.element.findall(RAW)
        return raw_children

    def validate_attribute(self, att_name):
        if not att_name:
            logger.warning(f"attribute name is None")
            return
        value = self.element.attrib.get(att_name)
        if not value:
            logging.error(f"Attribute {att_name} cannot have null value")
        if att_name == WIKIDATA_ID:
            self.validate_wikidata_id(value)

    def validate_wikidata_id(self, value):
        if not value:
            return None
        mm = re.match("([QP])\\d{1,11}", value)
        if not mm:
            logging.warning(f"{WIKIDATA_ID} bad value: {value}")
        return mm

    # AmiEntry

    @classmethod
    def find_name_to_wikidata_match(cls, wikidata_pages, wikidata_title=None):
        """
        matches wikidata pages against wikidata_title
        (Later may have fuzzy matching)
        :param wikidata_pages: list of pages
        :param wikidata_title: title to match
        :return: list of pages that match
        """
        matched_pages = []
        for wikidata_page in wikidata_pages:
            title = wikidata_page.get_title()
            if wikidata_page.title_matches(wikidata_title):
                matched_pages.append(wikidata_page)
        return matched_pages

    @classmethod
    def get_wikidata_pages_for_ids(cls, wikidata_ids):
        """
        get WikidataPages for list of PQids
        :param wikidata_ids: list of PQitems
        :return: list of corresponding WikidataPages
        """
        wikidata_pages = []
        url_errors = []
        for id in wikidata_ids:
            try:
                wikidata_page = WikidataPage(pqitem=id)
                wikidata_pages.append(wikidata_page)
            except URLError as e:
                url_errors.append(e)
        if url_errors:
            logger.error(f"could not find URLs {url_errors}")

        return wikidata_pages

    # AmiEntry

    def get_wikidata_id(self, empty_to_none=True):
        """gets value of wikidataID attribute
        :param empty_to_none: if True treats "" as None
        :return: raw value or None
        """
        return self.element.get(WIKIDATA_ID)

    @classmethod
    def get_wikidata_ids_for_entries(cls, entries, empty_to_none=True):
        """
        list of wikidata_ids for list of entries
        may contain None values if no wikidata_id
        :param entries: list of entries to process
        :param empty_to_none: if true treat "" as None
        :return: list of wikidata IDs (may be [])
        """

        return [AmiEntry.create_from_element(entry).get_wikidata_id(empty_to_none=empty_to_none) for entry in entries] if entries else []

    # AmiEntry

    @classmethod
    def get_terms_for_lxml_entries(cls, lxml_entries):
        """
        Convenience method
        get list of @term's for list of AmiEntries
        USABLE
        :param entries: list of entries to process
        :return: list of terms (may be [])
        """
        if len(lxml_entries) == 0:
            return []
        type1 = type(lxml_entries[0])
        assert type1 is _Element, f"found {type1}"

        return [lxml_entry.get(TERM) for lxml_entry in lxml_entries]

    def get_wikidata_pages_from_raw_wikidata_ids_matching_wikidata_page_title(self):
        """
        use entry name to search for wikidata pages (from raw@wikidataID child ids) whose title/label == name
        <entry term="GHG" name="Greenhouse Gas" >
            <raw wikidataID="['Q167336', 'Q3588927', 'Q925312', 'Q57584895', 'Q110612403', 'Q112192791', 'Q140182']"/>
        </entry>
        Object: find all wikidata pages whose titles match the `name`s in the raw wikidata pages
        1) retrieve the wikidata pages with the given wikidataIDs
        2) find each of their titles/labels
        3) check the entry name ("greenhouse gas") against the titles (case-insensitive, exact match)
        4) return the pages which match
        USABLE

        :return: list of pages with title (may be empty)
        """
        raw_wikidata_ids = self.get_raw_child_wikidata_ids()
        if not raw_wikidata_ids:
            return []
        wikidata_pages = AmiEntry.get_wikidata_pages_for_ids(raw_wikidata_ids)
        name = self.get_name().lower()
        matched_pages = AmiEntry.find_name_to_wikidata_match(wikidata_pages, wikidata_title=name)
        return matched_pages

    @classmethod
    def create_from_elements(cls, _entries):
        """create a list of AmiEntry's wrapping a list of lxml elements"""
        ami_entries = [AmiEntry.create_from_element(_element) for _element in _entries]
        return ami_entries

    def add_hits_to_xml(self, qid, dikt):
        """
        adds hits to XML element
        :param diktt: Python dict with hits

        """
        incl_keys = ["title", "description"]

        subelement = ET.SubElement(self.element, "div")
        subelement.attrib["qid"] = qid
        a = ET.SubElement(subelement, "a")
        a.attrib["href"] = f"{WIKIDATA_URL}/{qid}"
        a.text = "Wikidata"
        for key in dikt.keys():
            if key in incl_keys:
                value = dikt.get(key)
                p = ET.SubElement(subelement, "p")
                p.attrib["role"] = key
                p.text = str(value)

    def lookup_and_add_wikipedia_page(self):
        term = self.get_term()
        wikipedia_page = None
        if term:
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
            if wikipedia_page:
                wp_para = wikipedia_page.create_first_wikipedia_para()
                if wp_para is not None:
                    self.element.append(wp_para.para_element)
        return wikipedia_page

    def create_semantic_html(self):
        """
        output semantic html for dictionary
        :return: semantic HTML
        """
        logger.debug(f"create_semantic_html NYI")

    def get_wikipedia_page_child_para(self, xpath="./p"):
        """
        return child paragraph added by wikipedia lookup as first_para of wikipedia_page
        :param xpath: paragrapg selector (default './p')
        :return: wikpedia first para or None
        """
        child_paras  = self.element.xpath(xpath)
        return None if len(child_paras) == 0 else child_paras[0]

    def create_semantic_div_from_term(self, entry_elem=None, add_figures=False):
        """
        create html div for term with wikipedia page para
        :param ami_entry: ami entry with wikipedia page paragraph

        :return: div with term and para
        """
        logger.warning("Dont create default entry at this stage")
        html_div = ET.Element("div")
        html_div.attrib[ROLE] = AMI_ENTRY
        term = self.get_term()
        name = self.get_name()
        id = self.create_id(name)
        html_div.attrib["id"] = id

        self._add_raw_term(html_div)

        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        wikipedia_page.get_infobox()
        wp_para = wikipedia_page.create_first_wikipedia_para()
        if wp_para is None:
            logger.error(f"could not find page for term {term}")
            return None
        assert wp_para is not None
        pe = wp_para.para_element
        html_div.append(pe)
        return html_div

    def _add_raw_term(self, html_div):
        term_para = ET.SubElement(html_div, "p")
        term_name_span = ET.SubElement(term_para, "span")
        term_name_span.text = "Term:"
        term_value_span = ET.SubElement(term_para, "span")
        term_value_span.text = self.get_term()

    @classmethod
    def create_id(cls, name):
        """
        create id from name
        converts to lowercase and replaces space by "_"
        :param name: name for term
        :return: lowercase term with underscores (or None)

        """
        id = None if name is None else name.strip().lower().replace("\\s+", "_")
        return id

    def add_figures_to_entry_old(self):
        """

        """
        term = self.get_term()
        if term is None:
            logger.warning(f"element has no term")
            return
        wikipedia_page = self.lookup_wikipedia_page(term)
        if wikipedia_page is not None:
            logger.warning(f"no wikipedia page for {term}")
            wiktionary_page = self.lookup_wiktionary(term)
            if wiktionary_page is not None:
                self.add_figures_from_wiktionary(term, wiktionary_page)
        else:
            self.add_figures_from_wikipedia(term, wikipedia_page)

    def add_figures_to_entry(self, wikipedia_page):
        """
        extracts figures from Wikipedia page and returns the first
        Currently (2024-09) we look at:
        * infobox
        * first <figure> thumbnail


        """
        term = self.get_term()
        if term is None:
            logger.warning(f"element has no term")
            return
        # dictionary = self.element.xpath('parent::*')[0]
        # wikipedia_page = self.lookup_wikipedia_page(term)
        if wikipedia_page is None:
            logger.warning(f"no wikipedia page for {term}")
            return
            # wiktionary_page = self.lookup_wiktionary(term)
            # if wiktionary_page is not None:
            #     self.add_figures_from_wiktionary(term, wiktionary_page)
        self.add_figures_from_wikipedia(term, wikipedia_page)

    def add_figures_from_wikipedia(self, term, wikipedia_page):
        """
        extract figures from Wikipedia page, either infobox or first thumbnail
        """
        a_elem = wikipedia_page.extract_a_elem_with_image_from_infobox()
        logger.debug(f"{term}: {a_elem}")
        figures = wikipedia_page.html_elem.xpath(".//figure")
        if a_elem is None and len(figures) == 0:
            logger.info(f"NO FIGURES for {term}")
            return
        figure_div = ET.SubElement(self.element, "div")
        figure_div.attrib["title"] = "figure"
        if a_elem is not None:
            figure_div.append(copy.deepcopy(a_elem))
            logger.info(f"added figure {a_elem} for {term} ")
        elif len(figures) > 0:
            figure_div.append(copy.deepcopy(figures[0]))

    def lookup_wikipedia_page(self, term):
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
        if wikipedia_page is None:
            logger.warning(f"Cannot find wikipedia page for {term}")
        logger.debug(f"WP page for {term}: {wikipedia_page.search_url}")
        return wikipedia_page

    def create_semantic_div(self):
        html_div = Element("div")
        # copy attributes
        for (k, v) in self.element.attrib.items():
            html_div.attrib[k] = v
        # copy children
        for child in self.element.xpath("./*"):
            html_div.append(copy.deepcopy(child))
        term = self.get_term()
        html_div.attrib[ROLE] = AMI_ENTRY
        p = ET.SubElement(html_div, "p")
        return html_div

    def lookup_wiktionary(self, term):
        """
        lookup term in Wiktionary
        currently will take the first
        """
        logger.warning(f"Wiktionary lookup NYI")
        return None

    def add_figures_from_wiktionary(self, term, wiktionary_page):
        """
        extract figures from Wiktionary page first thumbnail
        by default add all figures to help readers disambiguate
        needs deeper parsing of wikitionary
        :param term:
        :param wiktionary_page: page to extract figures from
        """
        figures = wiktionary_page.html_elem.xpath(".//figure")
        if len(figures) == 0:
            logger.info(f"NO FIGURES for {term}")
            return
        figure_div = ET.SubElement(self.element, "div")
        figure_div.attrib["title"] = "figure"
        if len(figures) > 0:
            for figure in figures:
                figure_div.append(copy.deepcopy(figures))


class AmiDictionary:
    """wrapper for an ami dictionary including search flags

    """
    # tries to avoid circular import
    TAG = DICTIONARY
    NOT_FOUND = "NOT_FOUND"

    TITLE_A = "title"
    VERSION_A = "version"

    REQUIRED_ATTS = {TITLE_A, VERSION_A}
    OPTIONAL_ATTS = {}
    ALLOWED_ATTS = REQUIRED_ATTS.union(OPTIONAL_ATTS)
    assert len(ALLOWED_ATTS) == 2

    REQUIRED_CHILDREN = set()
    OPTIONAL_CHILDREN = {AmiEntry.TAG, "desc"}
    ALLOWED_CHILDREN = REQUIRED_CHILDREN.union(OPTIONAL_CHILDREN)
    assert len(ALLOWED_CHILDREN) == 2

    def __init__(self, title=None, wikilangs=["en"], ignorecase=True, **kwargs):
        self.logger = logger
        self.xml_content = None
        self.entries = []
        self.entry_by_id = dict()
        self.entry_by_term = dict()
        self.entry_by_wikidata_id = {}
        self.file = None
        self.ignorecase = ignorecase
        self.title = title
        self.root = None
        self.sparql_result_list = None
        self.sparql_result_by_wikidata_id = None
        self.sparql_to_dictionary = None
        self.split_terms = False
        self.term_set = set()
        self.url = None
        self.wikilangs = wikilangs
        self.wikidata_lookup = WikidataLookup()
        self.location_xml = None # path where dictionary lives; maybe set on dictionary reading or writing
        self.html_base = WIKIPEDIA_URL
        self.options = {} if "options" not in kwargs else kwargs["options"]

        if "synonyms" in self.options:
            logger.info("use synonyms")
        if "noignorecase" in self.options:
            logger.info("use case")
        self.split_terms = True
        self.split_terms = False

    #    class AmiDictionary:

    @classmethod
    def create_from_xml_file(cls, xml_file,
                             title=None,
                             ignorecase=False):
        """
        reads a dictionary XML file, creates and returns the AMIDictionary from it
        uses AmiDictionary.read_dictionary_from_xml_file()
        :param xml_file: file containing an AMI Dictionary as XML
        :param title: Obsolete
        :param ignorecase: see AmiDictionary.create_from_xml_object
        :returns: AmiDictionary object or null
        """
        if not os.path.exists(xml_file):
            logging.warning("cannot find dictionary path " + str(xml_file))
            return None
        try:
            xml_tree = ET.parse(str(xml_file), parser=ET.XMLParser(encoding="utf-8"))
        except lxml.etree.XMLSyntaxError as e:
            logging.error(f"Cannot parse xml file {xml_file} because {e}")
            logging.error(f"cannot parse xml_file {xml_file}")
            return None
        except Exception as e:
            logging.warning(f"error parsing {xml_file} {e}")

        dictionary = AmiDictionary.create_from_xml_object(xml_tree, ignorecase=ignorecase)
        dictionary.xml_content = xml_tree
        dictionary.file = xml_file
        dictionary.root = xml_tree.getroot()
        dictionary.location_xml = xml_file

        return dictionary

    def check_validity(self):
        logger.warning("ami_dict.check_validity() NYI ")

    @classmethod
    def create_from_html_file(cls, html_file,
                             title=None,
                             ignorecase=False):
        """
        reads a dictionary XML file, creates and returns the AMIDictionary from it
        uses AmiDictionary.read_dictionary_from_xml_file()
        :param xml_file: file containing an AMI Dictionary as XML

        :param title: Obsolete
        :param ignorecase: see AmiDictionary.create_from_xml_object
        :returns: AmiDictionary object or null

        Structure is:
        <html>
          <head>...</head>
          <body>
            <div title="some_title" role="ami_dictionary">
              <div role="ami_entry" id="something"
        """
        html_root = None
        if not os.path.exists(html_file):
            logging.warning("cannot find dictionary path " + str(html_file))
            return None
        try:
            html_root = HtmlUtil.parse_html_file_to_xml(html_file)
            assert html_root is not None, f"cannot parse htnl dictionary from {html_file}"
        except lxml.etree.XMLSyntaxError as e:
            logging.error(f"Cannot parse xml file {html_file} becauslogging.errore {e}")
            logging.error(f"cannot parse xml_file {html_file}")
            return None
        except Exception as e:
            logging.warning(f"error parsing {html_file} {e}")

        if html_root is None:
            logger.warning(f"could not create dictionary from {html_file}")
            return
        dictionary_divs = html_root.xpath("./body/div[@role='ami_dictionary']")
        if len(dictionary_divs) == 0:
            raise ValueError("HTML dictionary needs html/body/div[@role='ami_dictionary']")
        dictionary_div = dictionary_divs[0]
        title = dictionary_div.attrib.get(TITLE)
        if title is None:
            raise ValueError("HTML dictionary needs html/body/div[@role='ami_dictionary' and @title]")

        dictionary = AmiDictionary.create_dictionary_with_root(title=title)
        dictionary.xml_content = None
        dictionary.file = None
        dictionary.location_html = html_file

        cls.add_ami_entries_to_dict_and_create_entries_by_term(dictionary, dictionary_div)
        return dictionary

    @classmethod
    def add_ami_entries_to_dict_and_create_entries_by_term(cls, dictionary, dictionary_div):
        """
        :param dictionary: AmiDidictionary
        :param dictionary_div: div in HTML with @role='ami_dictionary' and @title attributes
        """
        html_entries = dictionary_div.xpath("./div[@role='ami_entry']")
        dictionary.entry_by_term = dict()
        for html_entry in html_entries:
            term = cls.get_term_from_html_entry(html_entry)
            if term is None:
                logger.warning(f" cannot find term for entry")
                continue
            id = html_entry.attrib.get("id")
            ami_entry = AmiEntry()
            dictionary.entry_by_term[term] = ami_entry
            ami_entry.element = ET.SubElement(dictionary_div, "entry")

            ami_entry.element.attrib[TERM] = term
            ami_entry.element.attrib["id"] = id
            contents = html_entry.xpath("*")
            for content in contents:
                ami_entry.element.append(content)

    @classmethod
    def get_term_from_html_entry(cls, html_entry_element):
        """

        assumes
        <div role="ami_entry" term="term" ...
        OR
        <div role="ami_entry">
           <p><span>Term:</span><span>anthropogenic</span></p>
        """
        if html_entry_element is None:
            return None
        term = html_entry_element.attrib.get(TERM)
        if term is None:
            spans = html_entry_element.xpath("p[span='Term:']/span[2]")
            if len(spans) == 1:
                term = spans[0].text
        return term
    @classmethod
    def create_dictionary_from_words(cls, terms, title=None, desc=None, wikilangs=None,
                                     wikidata=False, wiktionary=False, outdir=None,
                                     debug=True):
        """use raw list of words and optionally lookup each. choosing WD page and using languages
        :param terms: list of words/phrases,
        :param title: for dictionary object and file
        :param desc: description of dictionary
        :param wikilangs: languages to use in Wikidata default EN)
        :param wikidata: if true lookup wikidata
        :param outdir: if not None write dictionary to outpath=<outdir>/<title>.xml
        :param debug: debug
        :return dictionary,outpath tuple (outpath may be None)
        """
        if title is None:
            title = "no_title"
        dictionary = cls.create_dictionary_with_root(title, wikilangs)
        if desc:
            dictionary.add_desc_element(desc)
        dictionary.add_entries_from_words(terms)
        if wikidata:
            dictionary.add_wikidata_from_terms()
        if wiktionary:
            dictionary.add_wiktionary_from_terms()
        outpath = None
        if outdir:
            outdir.mkdir(exist_ok=True)
            outpath = Path(outdir, title + ".xml")
            dictionary.location_xml = outpath
            with open(outpath, "wb") as f:
                f.write(lxml.etree.tostring(dictionary.root))
            if debug:
                logger.info(f"wrote dictionary {outpath}")

        return dictionary, outpath

    @classmethod
    def create_dictionary_with_root(cls, title, wikilangs=None):
        dictionary = AmiDictionary(title=title, wikilangs=wikilangs)
        dictionary.root = ET.Element(DICTIONARY)
        dictionary.root.attrib[TITLE] = title
        return dictionary

    @classmethod
    def create_dictionary_from_csv(cls, csv_term_file, col_name=None, title=None):
        """
        creates a dictionary from a column of terms in CSV file.
        The file may be written by docanalysis
        :param csv_term_file: filename with CSV data (mandatory)
        :param col_name: name of column to extract (mandatory)
        :param title: title of dictionary (NO spabes, [a-z_0-9] only)
        :return: AmiDictionary
        :except: file not exist, missing col_name, title
        """
        if col_name is None:
            raise ValueError("must give column name")
        if title is None:
            raise ValueError("must give title")
        df = pd.read_csv(csv_term_file)
        keywords = df[col_name]
        keyword_dict, _ = AmiDictionary.create_dictionary_from_words(keywords, title=title, wikidata=True)
        return keyword_dict


    #    class AmiDictionary:

    def add_entries_from_words(self, terms, duplicates="ignore"):
        """add list of words as entry's
        :param terms:   list of terms
        :param duplicates: action if term is duplicate ("ignore", "replace", "error") NYI
        """
        self.entries = self.entries if self.entries else []
        for term in terms:
            term = term.strip()
            if term:
                dup_entry = self.get_lxml_entry(term)
                if dup_entry is None:
                    self._add_entry(term)
                elif duplicates == "error":
                    raise AMIDictError("Duplicate entry")
                elif duplicates == "ignore":
                    logger.info(f"duplicate term: {term} ignored ")
                elif duplicates == "replace":
                    self.root.remove(dup_entry)
                    self._add_entry(term)

    def _add_entry(self, term):
        entry = self.add_entry_element(term=term)
        self.entries.append(entry)
        self.entry_by_term[term] = entry

    @classmethod
    def create_dictionary_from_wordfile(cls, wordfile=None, desc=None, wikidata=False, outdir=None, title=None,
                                        max_entries=1000000, debug=True):
        """
        :param wordfile: contains lists of words and file stem gives title
        :param desc: description of dictionary
        :param wikilangs: languages to use in Wikidata default EN)
        :param wikidata: if true lookup wikidata
        :param outdir: if not None write dictionary to outpath=<outdir>/<title>.xml
        :param title: title (required to create outfile) max_lengh 30, no spaces, [a-z0-9] will be lowercased
            if absent taken from wordfile
        :param max_entries: maximum entries (default 1000000)
        :param debug: output debug
        :return dictionary,outpath tuple (outpath may be None)

        """
        if not wordfile:
            raise ValueError(f"must gove wordfile to create dictionary")
        wordpath = Path(wordfile)
        with open(wordpath, "r") as f:
            words = [line.strip() for line in f.readlines()]
        words = words[:max_entries] # maximum words
        stem = Path(wordfile).stem
        if not title:
            title = stem
        title = title.lower().replace(" ", "")

        logger.info(f"creating dictionary title = {title}")
        dictionary, outpath = cls.create_dictionary_from_words(terms=words, title=title, desc=desc, wikidata=wikidata,
                                                               outdir=outdir, debug=debug)
        return dictionary, outpath

    #    class AmiDictionary:

    @classmethod
    def create_dictionary_from_xml_string(cls, xml_str):
        """create dictionary from xml string
        :param xml_str: well-formed XML string
        :return AMIDictionary or null
        """
        xml = lxml.etree.fromstring(xml_str)
        dictionary = AmiDictionary.create_from_xml_object(xml)
        return dictionary

    #    class AmiDictionary:

    def add_entry_element(self, term):
        """create and add antry with term/name
        :param term: term (will also set name attribute
         :return entry"""
        if not term:
            raise ValueError("must have term for new entry")
        entry = ET.SubElement(self.root, ENTRY)
        entry.attrib[NAME] = term
        entry.attrib[TERM] = term
        self.entry_by_term[term] = entry
        return entry

    def add_desc_element(self, desc):
        """create and add desc element to root element"""
        desc_elem = ET.SubElement(self.root, DESC)
        desc_elem.text = desc

    #    class AmiDictionary:

    @classmethod
    def read_dictionary(cls, file):
        """create dictionary from file
        :param file: containing dictionary
        :return: new Dictionary"""
        return AmiDictionary.create_from_xml_file(file) if file is not None else None

    #    class AmiDictionary:

    @classmethod
    def create_from_xml_object(cls, xml_object, ignorecase=True):
        if xml_object is None:
            return None
        if not xml_object.xpath("@title"):
            raise ValueError("No title given for dictionary")
        dictionary = AmiDictionary()
        if isinstance(xml_object, lxml.etree._ElementTree):
            dictionary.root = xml_object.getroot()
        elif isinstance(xml_object, lxml.etree._Element):
            dictionary.root = xml_object
        else:
            raise AMIDictError(f"bad object {type(xml_object)}")
        dictionary.title = dictionary.root.xpath("@title")
        dictionary.ignorecase = ignorecase
        dictionary.entries = list(dictionary.root.findall(ENTRY))
        dictionary.create_entry_by_term()
        dictionary.term_set = set()
        return dictionary

    @classmethod
    def create_dictionary_from_url(cls, xml_url):
        """
        Create dictionary from (the content and filename) of a URL
        See also AmiDictionary.read_dictionary

        """
        assert xml_url is not None
        try:
            with urllib.request.urlopen(xml_url) as f:
                content = f.read()
        except URLError as e:
            raise AMIDictError(f"Failed to read URL: {xml_url}; reason = {e.reason}")
        assert content is not None
        assert type(content) is bytes
        element = etree.fromstring(content)
        assert element.tag == AmiDictionary.TAG
        amidict = AmiDictionary.create_from_xml_object(element)
        amidict.url = xml_url
        # save filename  in dictionary
        amidict.file = Util.get_file_from_url(amidict.url)
        return amidict

    #    class AmiDictionary:

    def get_or_create_term_set(self):
        if len(self.term_set) == 0:
            for entry in self.entries:
                if TERM in entry.attrib:
                    term = self.term_from_entry(entry)
                    # single word terms
                    if " " not in term:
                        self.add_processed_term(term)
                    elif self.split_terms:
                        # multiword terms
                        for termx in term.split(" "):
                            self.add_processed_term(termx)
                    else:
                        # add multiword term
                        self.add_processed_term(term)

        return self.term_set

    #    class AmiDictionary:

    def get_or_create_multiword_terms(self):
        return
        """NYI"""
        if len(self.multiwords) == 0:
            for entry in self.entries:
                if TERM in entry.attrib:
                    term = self.term_from_entry(entry)
                    # single word terms
                    if " " not in term:
                        self.add_processed_term(term)
                    elif self.split_terms:
                        # multiword terms
                        for term in " ".split(term):
                            self.add_processed_term(term)

        return self.term_set

    #    class AmiDictionary:

    def term_from_entry(self, entry):
        if TERM not in entry.attrib:
            logger.warning("missing term", ET.tostring(entry))
            term = None
        else:
            term = entry.attrib[TERM].strip()
        return term.lower() if term is not None and self.ignorecase else term

    def get_xml_and_image_url(self, term):
        entry = self.get_lxml_entry(term)
        entry_xml = ET.tostring(entry)
        image_url = entry.find(".//" + IMAGE)
        return entry_xml, image_url.text if image_url is not None else None

    def add_processed_term(self, term):
        if self.ignorecase:
            term = term.lower()
        self.term_set.add(term)  # single word countries

    #    class AmiDictionary:

    def match(self, target_words):
        matched = []
        self.term_set = self.get_or_create_term_set()
        for target_word in target_words:
            target_word = target_word.lower()
            if target_word in self.term_set:
                matched.append(target_word)
        return matched

    def match_multiple_word_terms_against_sentences(self, sentence_list):
        """this will be slow with large dictionaries until we optimise the algorithm """
        matched = []

        for term in self.term_set:
            term = term.lower()
            term_words = term.split(" ")
            if len(term_words) > 1:
                for sentence in sentence_list:
                    if term in sentence.lower():
                        matched.append(term)
        return matched

    #    class AmiDictionary:

    def get_lxml_entry(self, termx, ignorecase=True):
        """get entry if term attribute == term (case may matter
        :param termx: term to search for
        :param ignorecase: if true searches for any case variant
        :return: the entry or None

        all terms are keyed as lowercase in dictionary and case is checked if there
        is a lowercase match

        """
        if termx is None:
            logger.warning("term is None")
            return None
        lcase = termx.lower()  # all keys are lowercase
        if self.entry_by_term is None or len(self.entry_by_term) == 0:
            self.create_entry_by_term()
        entry = self.entry_by_term[lcase] if lcase in self.entry_by_term else None
        # if case-sensitive check whether term was different case
        if entry is not None:
            assert type(entry) is _Element, f"found {type(entry)}"
            entry_term = entry.attrib[TERM]
            # if the term is case sensitive, compare them
            if not ignorecase and entry_term != termx:
                entry = None
        return entry

    #    class AmiDictionary:

    def get_ami_entry(self, term):
        """creates an AmiEntry object from raw entry
        :param term: to search for
        :return: entry wrapped in AmiEntry
        """
        entry = self.get_lxml_entry(term)
        return None if entry is None else AmiEntry.create_from_element(entry)

    def get_ami_entry_by_id(self, id):
        pass

    def get_entry_count(self):
        assert self.entry_by_term is not None
        return len(self.entry_by_term)

    def get_lxml_entries(self):
        """
        get lxml_entries from dictionary
        :return: list of lxml_entry's
        """
        assert self.entry_by_term
        return list(self.entry_by_term.values())

    @classmethod
    def get_term(cls, lxml_entry):
        return lxml_entry.get(TERM)

    @classmethod
    def get_wikidata_id(cls, lxml_entry):
        return lxml_entry.get(WIKIDATA_ID)

    def get_ami_entries(self):
        """creates entriws from elements in self.entry_by_term
        TODO maybe index the AmiEntry's instead
        :return: list of AmiEntries"""
        assert self.entry_by_term is not None
        ami_entry_list = []
        for entry_element in self.entry_by_term.values():
            ami_entry = AmiEntry.create_from_element(entry_element)
            ami_entry_list.append(ami_entry)
        return ami_entry_list

    def create_entry_by_term(self, lower=True):
        self.entry_by_term = dict()
        for entry in self.entries:
            term = self.term_from_entry(entry)
            # index by lowercase?
            if lower:
                term = term.lower()
            if term in self.entry_by_term:
                logger.warning(f"duplicate terms not allowed {term}")
            else:
                self.entry_by_term[term] = entry

    def delete_entry_by_term(self, term):
        """removes an entry with given term"""
        entry = self.get_lxml_entry(term)
        if entry is not None:
            self.root.remove(entry)
            self.entry_by_term.pop(term)

    def create_and_add_entry_with_term(self, term, replace=True):
        """creates lxml_entry element from term
        uses AmiEntry.create_lxml_entry_from_term(term)
        :param term: term attribute
        :param replace: if True, replace entry element
        :return: new lxml_entry
        """
        lxml_entry_new = AmiEntry.create_lxml_entry_from_term(term)
        lxml_entry_exist = self.get_lxml_entry(term)

        if lxml_entry_exist is not None:
            if replace:
                lxml_entry_exist.addnext(lxml_entry_new)
                lxml_entry_exist.getparent().remove(lxml_entry_exist)
            else:
                raise AMIDictError("attempt to add duplicate entry with replace=False")
        else:
            self.root.append(lxml_entry_new)
        if lxml_entry_new is not None:
            self.entry_by_term[term] = lxml_entry_new
        return lxml_entry_new

    def check_unique_wikidata_ids(self):
        self.entry_by_wikidata_id = {}
        for entry in self.entries:
            if WIKIDATA_ID not in entry.attrib:
                logger.warning("No wikidata ID for", entry)
            else:
                wikidata_id = entry.attrib[WIKIDATA_ID]
                if wikidata_id in self.entry_by_wikidata_id.keys():
                    logger.warning("duplicate Wikidata ID:", wikidata_id, entry)
                else:
                    self.entry_by_wikidata_id[wikidata_id] = entry


    def write_to_dir(self, directory):
        """write dictionary to file based on title
        :param directory: directory which will contain <title>.xml"""
        if not directory:
            logger.warning(f"None directory")
        directory.mkdir(exist_ok=True)
        file = Path(directory, f"{self.root.attrib[TITLE]}.xml")
        self.create_html_write_to_file(file)
        return file

    def create_html_write_to_file(self, file, debug=True):
        """write dictionary to file
        :param file: to write to (type is determined by suffix (.xml) or (.html)
        :param debug: debug output
        :param has_figures: Figures and desciptions already added
        """
        root = etree.ElementTree(self.root)
        FileLib.force_mkparent(file)
        file_str = str(file)
        if file_str.endswith(".xml"):
            self.write_xml_dictionary(file, root)
        elif file_str.endswith(".html"):
            title = Path(file).stem
            sem_html = self.create_html_dictionary_and_format(title)
            HtmlLib.write_html_file(sem_html, file, debug=debug)

        else:
            logger.error(f"unknown output suffix in {file}")

        if debug:
            logger.debug(f"wrote dictionary {self.title} to {file}")

    def create_html_dictionary_and_format(self, title):
        sem_html = self.create_html_dictionary(create_default_entry=False, title=title)
        HtmlLib.add_base_to_head(sem_html, self.html_base)
        return sem_html

    def write_xml_dictionary(self, file, root):
        with open(file, 'wb') as f:
            root.write(f, encoding="utf-8",
                       xml_declaration=True, pretty_print=True)

    def add_wikidata_from_terms(self, allowed_descriptions=ANY):

        entries = self.root.findall(ENTRY)
        for entry in entries:
            self.lookup_and_add_wikidata_to_entry(entry, allowed_descriptions=allowed_descriptions)

    def lookup_and_add_wikidata_to_entry(self, entry, allowed_descriptions=ANY):
        """lookup term and  add wikidata Info to entry if desc fits required description
        :param entry: to add wikidata to
        :param allowed_descriptions: only add if the description fits (ANY overrides)"""
        term = entry.attrib[TERM]
        qitem, desc, qitems = self.wikidata_lookup.lookup_wikidata(term)
        if not qitem:
            logger.info(f"Wikidata lookup for {term} failed")
            return

        if allowed_descriptions == ANY:
            if qitem:
                entry.attrib[WIKIDATA_ID] = qitem
                entry.attrib[WIKIDATA_URL] = WIKIDATA_SITE + qitem
            if desc:
                entry.attrib[DESC] = desc
            for wid in qitems:
                if wid != qitem:
                    wikidata_hit = ET.SubElement(entry, WIKIDATA_HIT)
                    wikidata_hit.attrib[TYPE] = WIKIDATA_HITS
                    wikidata_hit.text = str(wid)
            wikidata_page = WikidataPage(qitem)
            assert wikidata_page is not None
            wikipedia_dict = wikidata_page.get_wikipedia_page_links(self.wikilangs)
            self.add_wikipedia_page_links(entry, wikipedia_dict)

    def add_wiktionary_from_terms(self):

        entries = self.root.findall(ENTRY)
        for entry in entries:
            self.lookup_and_add_wiktionary_to_entry(entry)

    def lookup_and_add_wiktionary_to_entry(self, entry):
        """lookup term and  add wikidata Info to entry if desc fits required description
        :param entry: to add wikidata to
        :param allowed_descriptions: only add if the description fits (ANY overrides)"""
        term = entry.attrib[TERM]
        wiktionary_page = WiktionaryPage.create_wiktionary_page(term)
        desc = f"ET.tostring(wiktionary_page.html_div)[:200]..."
        desc = HtmlUtil.get_text_content(wiktionary_page.html_div)
        entry.attrib[DESC] = desc[:200]
        logger.info(f"entry {ET.tostring(entry)}")
        pass
    @classmethod
    def add_wikipedia_page_links(cls, entry, wikipedia_dict):
        """
        TODO improve documantation
        iterates over items in wikipedia_dict
        if item has "en" field adds  wikipediaPage attribute
        otherwise creates list of subelemnts, one for each language
        :param entry: dictionary entry
        :
        """
        for wp in wikipedia_dict.items():
            if wp[0] == "en":
                entry.attrib[WIKIPEDIA_PAGE] = wp[1]
            else:
                wikipedia = ET.SubElement(entry, WIKIPEDIA)
                wikipedia.attrib["lang"] = wp[0]
                wikipedia.text = wp[1]

    @classmethod
    def is_valid_wikidata_id(cls, wikidata_id):
        """is a wikidataID not null, not empty and not a reserved keyword """
        if wikidata_id is None:
            return False
        if wikidata_id == "":
            return False
        if wikidata_id == AmiDictionary.NOT_FOUND:
            return False
        return True

    # new
    def has_valid_root_tag(self):
        return self.root.tag == DICTIONARY

    def create_wikidata_page(self, entry_element):
        from amilib.wikimedia import WikidataPage

        # refactor this - make entry a class
        wikidata_page = None
        qitem = entry_element.attrib[WIKIDATA_ID]
        if qitem is not None:
            wikidata_page = WikidataPage(qitem)

        return wikidata_page

    def disambiguate_wikidata_by_desc(self, entry):
        """

        """
        wikidata_id = AmiDictionary.get_wikidata_id(entry)
        if not AmiDictionary.is_valid_wikidata_id(wikidata_id):
            term = AmiDictionary.get_term(entry)
            self.lookup_and_add_wikidata_to_entry(entry, allowed_descriptions="")
            wikidata_id = AmiDictionary.get_wikidata_id(entry)
            if wikidata_id is None:
                entry.attrib[WIKIDATA_ID] = AmiDictionary.NOT_FOUND
            else:
                logging.debug(f"found {wikidata_id} for {term} desc = {entry.get('desc')}")

    def get_disambiguated_raw_wikidata_ids(self):
        """
        returns disambiguated list of (term, idlist) tuples for ambiguous raw@wikidataIDs
        iterates over all entry/raw@wikidataID attributes and disambiguates the IDs by matching
        against the entry name
        :return: list of (term, idlist) tuples if disambiguates

        """
        _entries = self.get_entries_with_raw_wikidata_ids()
        ami_entries = AmiEntry.create_from_elements(_entries)
        _term_id_list = []
        for ami_entry in ami_entries:
            wikidata_pages = ami_entry.get_wikidata_pages_from_raw_wikidata_ids_matching_wikidata_page_title()
            ids = [page.get_id() for page in wikidata_pages]
            if ids:
                _term_id_list.append((ami_entry.get_term(), ids))
        return _term_id_list

    def lookup_missing_wikidata_ids(self, lookup_string=NAME, maxhits=99999):
        """
        finds entries with missing WikidataIDs and searches wikidata by name or term
        creates WikidataLookup which holds hits_dict with details of possible match

        e.g .
        # {
#     {'BECCS': {'Q146790': 'Aomori',
#                'Q209727': 'palmitic acid',
#                'Q455712': 'Domenico di Pace Beccafumi',
#                'Q472237': 'Nikolaos Gyzis',
#                'Q507854': 'Karlstadt am Main'},
#      'CBEs': {'Q1391': 'Maryland',
#               'Q227': 'Azerbaijan',
#               'Q7024': 'Lugano',
#               'Q8093': 'Nintendo',
#               'Q884': 'South Korea'},
#      'WMO': {'Property:P4136': 'WIGOS station ID',
#              'Property:P5956': 'War Memorials Online ID',
#              'Property:P9737': 'WMO code',
#              'Q170424': 'World Meteorological Organization',
#              'Q4468436': 'White Mountain Airport'}}
#     }

        :param lookup_string: either "name" (NAME) OR "term" (TERM); default NAME
        :param maxhits: exit after maxhits entries
        :return: new WikidataLookup with lookup.hits_dict
        """
        lxml_entries = self.get_lxml_entries_with_missing_wikidata_ids()
        lookup = WikidataLookup()
        for i, lxml_entry in enumerate(lxml_entries):
            if i >= maxhits:
                break
            ami_entry = AmiEntry.create_from_element(lxml_entry)
            # where only some of name/term are present
            if lookup_string == NAME:
                string = ami_entry.get_name()
                if not string:
                    string = ami_entry.get_term()
            else:
                string = ami_entry.get_term()
                if not string:
                    string = ami_entry.get_name()

            lookup.get_possible_wikidata_hits(string)
        return lookup

    def markup_html_from_dictionary(self, target_path, output_path, background_color="pink", recurse=False):
        term_set = self.get_or_create_term_set()
        re_join = '|'.join(term_set)
        try:
            rec = re.compile(f"(.*?)({re_join})(.*)")
        except Exception as e:
            logging.error(f"dictionary {self.title}: Cannot parse terms into regex: \\n{re_join}\\n please remove or escape characters")
            return None
        target_elem = ET.parse(str(target_path), HTMLParser())
        div_spans = target_elem.xpath(f".//{H_DIV}/{H_SPAN}")
        for span in div_spans:
            text = span.text
            id_root = span.attrib.get('id')
            if id_root is not None:
                id_root += "_"
            new_elems = HtmlUtil.split_span_at_match(span, rec, new_tags=[H_SPAN, H_A, H_SPAN],
                                                     recurse=recurse, id_root=id_root, id_counter=0)
        self.convert_matched_spans_to_a(target_elem)

        id_dict, multidict = self.write_annotated_html(background_color, output_path, target_elem)

        self.write_index(id_dict, multidict, output_path)

    def write_annotated_html(self, background_color, output_path,
                             target_elem):
        a_elems = target_elem.xpath(f".//{H_A}")
        multidict = dict()
        match_counter = Counter()
        id_dict = dict()
        for a_elem in a_elems:
            entry = self.get_lxml_entry(a_elem.text, ignorecase=True)  # lookup in dictionary
            if entry is None:
                continue
            preceding = a_elem.xpath("preceding-sibling::*[1]")
            preceding_text = preceding[0].text if len(preceding) > 0 else None
            following = a_elem.xpath("following-sibling::*[1]")
            following_text = following[0].text if len(following) > 0 else None
            id_dict[a_elem.attrib[A_ID]] = preceding_text, (a_elem.text), following_text
            # add to multidict
            if a_elem.text not in multidict:
                multidict[a_elem.text] = []
            multidict[a_elem.text].append(a_elem.attrib[A_ID])
            match_counter[a_elem.text] += 1
            CSSStyle.add_name_value(a_elem, "background-color", background_color)
            if "wikidataID" in entry.attrib:
                href = entry.attrib["wikidataID"]
                if href:
                    a_elem.attrib[A_HREF] = WIKIDATA_SITE + href
                name = entry.attrib.get(A_NAME)
                if name:
                    a_elem.attrib[A_TITLE] = name
                else:
                    a_elem.attrib[A_TITLE] = entry.attrib.get(A_TERM)

            else:
                pass
        with open(str(output_path), "wb") as f:
            f.write(lxml.etree.tostring(target_elem))
            logger.info(f"wrote {output_path}")

        return id_dict, multidict

    def write_index(self, id_dict, multidict, output_path):
        output_path = Path(output_path)
        html = HtmlUtil.create_skeleton_html()
        body = html.xpath(f".//{H_BODY}")[0]
        ul = lxml.etree.SubElement(body, H_UL)
        for key in multidict:
            id_list = multidict[key]
            li = lxml.etree.SubElement(ul, H_LI)
            li.text = key
            ul2 = lxml.etree.SubElement(li, H_UL)
            for id in id_list:
                li2 = lxml.etree.SubElement(ul2, H_LI)
                prec_follow = id_dict[id]
                if prec_follow[0]:
                    span = lxml.etree.SubElement(li2, H_SPAN)
                    span.text = prec_follow[0]
                a = lxml.etree.SubElement(li2, H_A)
                a.text = prec_follow[1]
                a.attrib[A_HREF] = f"{Path(output_path).stem}.html#{id}"
                if prec_follow[2]:
                    span = lxml.etree.SubElement(li2, H_SPAN)
                    span.text = prec_follow[2]
        logging.info(f"outpath {output_path} {output_path.parent}")
        list_path = Path(output_path.parent, "index.html")
        with open(str(list_path), "wb") as f:
            f.write(lxml.etree.tostring(html))
            logger.info(f"wrote {list_path}")

    def convert_matched_spans_to_a(self, chap_elem):
        """some matches are complete span and need converting to <a>
        """
        re_spans = chap_elem.xpath(".//span[@class='re_match']")
        for re_span in re_spans:
            re_span.tag = "a"

    @classmethod
    def create_and_write_dictionary(cls, dictionary_file, dictionary_root, i, keystring, sparq2dict, sparql_file):
        assert (os.path.exists(sparql_file))
        dictionary = AmiDictionary.create_from_xml_file(dictionary_file)
        wikidata_sparql = WikidataSparql(dictionary)
        wikidata_sparql.update_from_sparql(sparql_file, sparq2dict)
        dictionary_file = f"{dictionary_root}{keystring}_{i + 1}.xml"
        dictionary.create_html_write_to_file(dictionary_file)
        return dictionary_file

    @classmethod
    def create_minimal_dictionary(cls):
        element = etree.Element(AmiDictionary.TAG)
        element.attrib["title"] = "minimal"
        dictionary = AmiDictionary.create_from_xml_object(element)
        dictionary.set_version()
        dictionary.set_encoding()
        return dictionary

    def set_title(self, title):
        assert self.root is not None
        self.root.title = title

    def set_encoding(self, encoding=UTF_8):
        assert self.root is not None

    def set_version(self, version='0.0.1'):
        assert self.root is not None
        self.root.attrib[VERSION] = version

    def get_version(self):
        if self.root is None or self.root.attrib is None or VERSION not in self.root.attrib:
            return None
        return self.root.attrib.get(VERSION)

    def get_first_entry(self):
        """gets first entry mainly for testing
        """
        if self.root is None or len(self.get_lxml_entries()) == 0:
            return None
        return self.get_lxml_entries()[0]

    def get_first_ami_entry(self):
        """gets first entry mainly for testing
        """
        if self.root is None or len(self.get_lxml_entries()) == 0:
            return None
        return AmiEntry.create_from_element(self.get_lxml_entries()[0])

    # TODO is this in the right place?
    @classmethod
    def apply_dicts_and_sparql(cls, dictionary_file, rename_file, sparql2amidict_dict, sparql_files):
        """TODO this is a mess"""
        keystring = ""
        # save original path
        original_name = dictionary_file
        dictionary_root = os.path.splitext(dictionary_file)[0]
        save_file = dictionary_root + ".xml.save"
        copyfile(dictionary_file, save_file)
        for key in sparql2amidict_dict.keys():
            sparq2dict = sparql2amidict_dict[key]
            keystring += f"_{key}"
            for i, sparql_file in enumerate(sparql_files):
                dictionary_file = cls.create_and_write_dictionary(dictionary_file, dictionary_root, i, keystring,
                                                                  sparq2dict, sparql_file)
        if rename_file:
            copyfile(dictionary_file, original_name)

    def remove_attribute(self, attname):
        if self.get_attribute_value(attname) is not None:
            self.root.attrib.pop(attname)

    def get_attribute_value(self, attname):
        if attname not in self.root.attrib:
            return None
        else:
            return self.root.attrib[attname]

    def find_entries_with_term(self, term: str, abort_multiple: bool = False) -> list:
        """iterates over all entries checking `term` attribute against "term" argument
        May allow multiple terms
        :param term: term to match in entry@term
        :param abort_multiple: if True raise AmiDictError for multiple entries with same term
        """
        _entries = []
        for entry in self.get_lxml_entries():
            _term = AmiEntry.get_attribute_value(entry, TERM)
            if _term == term:
                if abort_multiple and len(_entries) > 0:
                    raise AMIDictError(f"multiple entries with term = {_term}")
                _entries.append(entry)
        return _entries

    def get_terms(self):
        assert self.entry_by_term
        return list(self.entry_by_term.keys())

    @classmethod
    def is_valid_version_string(cls, version):
        """tests validity of version string major.minor.patch
        :param version: e.g. version = "1.2.3"
        :raises AMIDictError: version is None (maybe missing attribute)
        :raises AMIDictError: version does not have 3 parts")
        :raises AMIDictError: version parts must be integers")
        :returns: True (errors raises exceptions)
        """
        if version is None:
            raise AMIDictError(f"{cls} version is None")
        parts = version.split(".")
        if len(parts) != 3:
            raise AMIDictError(f"{cls} version attribute {version} does not have 3 parts")
        try:
            for part in parts:
                _ = int(part)
        except Exception:
            raise AMIDictError(f"{cls} version attribute {version} parts must be integers")
        return True

    def check_validity(self):

        self.check_valid_attributes()
        self.check_valid_children()

    def check_valid_attributes(self):
        attributes = list(self.root.attrib)
        assert attributes is not None
        # assert str(attributes) == "['name']", f"attributes {attributes}"
        # assert len(attributes) == 2, f" ATTS {attributes}"
        for attribut in attributes:
            # msg = f"ATT {attribut}"
            assert type(attribut) is str
            assert attribut in AmiDictionary.ALLOWED_ATTS, f"attribute {attribut} is not allowed in <entry>"

    def check_valid_children(self):
        for child in self.root:
            if child.tag in AmiDictionary.ALLOWED_CHILDREN:
                pass
            else:
                logger.warning(f"forbidden child of {self.root.tag}: {child.tag} ; allowed = {AmiDictionary.ALLOWED_CHILDREN}")

    def get_lxml_entries_with_missing_wikidata_ids(self):
        """
        get all entries for which there is no wikidataId or its value is ""
        :return: list of lxml_entries (may be empty)
        """
        lxml_entries = self.get_lxml_entries()
        missing_wikidata_entries = []
        for lxml_entry in lxml_entries:
            wikidata_id = AmiEntry.create_from_element(lxml_entry).get_wikidata_id()
            if not wikidata_id or wikidata_id.strip() == "":
                missing_wikidata_entries.append(lxml_entry)
        return missing_wikidata_entries

    def get_entries_with_raw_wikidata_ids(self):
        """
        get all entries for which there is a raw@wikidataID child
        :return: list of entries (may be empty)
        """
        entries = self.get_lxml_entries()
        missing_wikidata_entries = []
        for entry in entries:
            wikidata_id = AmiEntry.create_from_element(entry).get_wikidata_id()
            if not wikidata_id or wikidata_id.strip() == "":
                missing_wikidata_entries.append(entry)
        return missing_wikidata_entries

    def get_entry_ids(self):
        """
        gets list of ids of <entry>s
        :return: list of ids (may be empty)
        """
        lxml_entries = self.get_lxml_entries()
        id_list = list()
        for entry in lxml_entries:
            id = entry.attrib.get("id")
            if id is not None:
                id_list.append(id)
        return id_list

    def create_html_dictionary(self, create_default_entry=False, title=None):
        """
        output semantic html for dictionary
        :return: semantic HTML
        """
        html_dict = HtmlLib.create_html_with_empty_head_body()
        self.add_style(html_dict)
        body = HtmlLib.get_body(html_dict)
        dictionary_div = ET.SubElement(body, "div")
        dictionary_div.attrib["role"] = "ami_dictionary"
        if title is not None:
            dictionary_div.attrib[TITLE] = title
        self.add_html_entries(dictionary_div, create_default_entry=False)
        return html_dict

    def add_html_entries(self, dictionary_div, create_default_entry=False):
        """
        add html entries to html dictionary
        :param dictionary_div:to add html entries to
        :param create_default_entry: Obsolete (don't create dictionary at this stage
        """
        entries = self.get_ami_entries()
        for ami_entry in entries:
            term = ami_entry.get_term()
            wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(term)
            if create_default_entry:
                entry_div = ami_entry.create_semantic_div_from_term()
            else:
                entry_div = ami_entry.create_semantic_div()
                p = ET.Element("p")
                wp_info = "None" if wikipedia_page is None else wikipedia_page.search_url
                p.text = f"search term:  {ami_entry.get_term()} "
                if wikipedia_page.search_url is not None:
                    a = ET.SubElement(p, "a")
                    a.attrib[A_HREF] = wikipedia_page.search_url
                    a.text = "Wikipedia Page"
                entry_div.insert(0, p)
            if len(entry_div.xpath("*")) == 0:

                p = ET.Element( "p")
                p.text = f"Cannot find Wikimedia for {ami_entry.get_term()}: {entry_div.attrib.get(TERM)}"
                entry_div.insert(0, p)
            dictionary_div.append(entry_div)

    def add_style(self, html_dict):
        head = HtmlLib.get_head(html_dict)
        style = ET.SubElement(head, "style")
        style.text = ("div[role] {border:solid 1px;margin:1px;}")

    @classmethod
    def read_html_dictionary_and_markup_html_file(cls, inpath, outpath, html_dict_path, remove_styles=False):
        """
        read semantic HTML file, extract paras with ids, create AmiDictionary from HTML,
        markup paras, and write marked  file
        :param inpath: to be marked up
        :param outpath: resulting marked file
        :param html_dict_path: dictiomary in HTML format
        :return: HTML element marked_up
        """
        assert Path(inpath).exists()
        paras = HtmlLib._extract_paras_with_ids(inpath)
        if remove_styles:
            HtmlUtil.remove_elems(paras[0], "/html/head/style")
        assert Path(html_dict_path).exists()
        dictionary = AmiDictionary.create_from_html_file(html_dict_path)
        assert dictionary is not None
        phrases = dictionary.get_terms()
        dictionary.location = html_dict_path
        HtmlLib.search_phrases_in_paragraphs(paras, phrases, markup=html_dict_path)
        # write marked_up html. The 'paras' are views on the original file
        chapter_elem = paras[0].xpath("/html")[0]
        HtmlLib.write_html_file(chapter_elem, outpath, debug=True)
        assert Path(outpath).exists()
        return chapter_elem



class AmiSynonym:
    TAG = "synonym"

    def __init__(self):
        self.element = None

    @classmethod
    def create_from_element(cls, element):
        ami_synonym = None
        if element is not None:
            ami_synonym = AmiSynonym()
            ami_synonym.element = element
        return ami_synonym


class AmiDictionaries:
    """collection of current and some historic dictionaries"""

    ACTIVITY = "activity"
    COMPOUND = "compound"
    COUNTRY = "country"
    DISEASE = "disease"
    ELEMENT = "elements"
    INVASIVE_PLANT = "invasive_plant"
    PLANT_GENUS = "plant_genus"
    ORGANIZATION = "organization"
    PLANT_COMPOUND = "plant_compound"
    PLANT = "plant"
    PLANT_PART = "plant_part"
    SOLVENT = "solvents"

    ANIMAL_TEST = "animaltest"
    COCHRANE = "cochrane"
    COMP_CHEM = "compchem"
    CRISPR = "crispr"
    CRYSTAL = "crystal"
    DISTRIBUTION = "distributions"
    DITERPENE = "diterpene"
    DRUG = "drugs"
    EDGE_MAMMAL = "edgemammals"
    CHEM_ELEMENT = "elements"
    EPIDEMIC = "epidemic"
    ETHICS = "ethics"
    EUROFUNDER = "eurofunders"
    ILLEGAL_DRUG = "illegaldrugs"
    INN = "inn"
    INSECTICIDE = "insecticide"
    MAGNETISM = "magnetism"
    MONOTERPENE = "monoterpene"
    NAL = "nal"
    NMR = "nmrspectroscopy"
    OBESITY = "obesity"
    OPTOGENETICS = "optogenetics"
    PECTIN = "pectin"
    PHOTOSYNTH = "photosynth"
    PLANT_DEV = "plantDevelopment"
    POVERTY = "poverty"
    PROT_STRUCT = "proteinstruct"
    PROT_PRED = "protpredict"
    REFUGEE = "refugeeUNHCR"
    SESQUITERPENE = "sesquiterpene"
    STATISTICS = "statistics"
    TROPICAL_VIRUS = "tropicalVirus"
    WETLANDS = "wetlands"
    WILDLIFE = "wildlife"

    def __init__(self):
        self.dictionary_dict = {}
        self.create_search_dictionary_dict()
        self.ami3_dict_index = None

    def create_search_dictionary_dict(self):

        # / Users / pm286 / projects / CEVOpen / dictionary / eoActivity / eo_activity / Activity.xml
        self.add_with_check(AmiDictionaries.ACTIVITY,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "eoActivity", "eo_activity", "activity.xml"))
        self.add_with_check(AmiDictionaries.COUNTRY,
                            os.path.join(LOCAL_OV21_DIR, "country", "country.xml"))
        self.add_with_check(AmiDictionaries.DISEASE,
                            os.path.join(LOCAL_OV21_DIR, "disease", "disease.xml"))
        self.add_with_check(AmiDictionaries.COMPOUND,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "eoCompound", "plant_compound.xml"))
        self.add_with_check(AmiDictionaries.PLANT,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "eoPlant", "plant.xml"))
        self.add_with_check(AmiDictionaries.PLANT_GENUS,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "plant_genus", "plant_genus.xml"))
        self.add_with_check(AmiDictionaries.ORGANIZATION,
                            os.path.join(LOCAL_OV21_DIR, "organization", "organization.xml"))
        self.add_with_check(AmiDictionaries.PLANT_COMPOUND,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "eoCompound", "plant_compound.xml"))
        self.add_with_check(AmiDictionaries.PLANT_PART,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "eoPlantPart", "eoplant_part.xml"))
        self.add_with_check(AmiDictionaries.INVASIVE_PLANT,
                            os.path.join(LOCAL_CEV_OPEN_DICT_DIR, "Invasive_species", "invasive_plant.xml"))

        self.make_ami3_dictionaries()

        return self.dictionary_dict

    def print_dicts(self):
        logger.info("DICTIONARIES LOADED")
        dd = dir(self)
        for d in dd:
            if d[0].isupper():
                print(">>", d)

    def make_ami3_dictionaries(self):

        self.ami3_dict_index = {
            AmiDictionaries.ANIMAL_TEST: os.path.join(LOCAL_DICT_AMI3, "animaltest.xml"),
            AmiDictionaries.COCHRANE: os.path.join(LOCAL_DICT_AMI3, "cochrane.xml"),
            AmiDictionaries.COMP_CHEM: os.path.join(LOCAL_DICT_AMI3, "compchem.xml"),
            AmiDictionaries.CRISPR: os.path.join(LOCAL_DICT_AMI3, "crispr.xml"),
            AmiDictionaries.CRYSTAL: os.path.join(LOCAL_DICT_AMI3, "crystal.xml"),
            AmiDictionaries.DISTRIBUTION: os.path.join(LOCAL_DICT_AMI3, "distributions.xml"),
            AmiDictionaries.DITERPENE: os.path.join(LOCAL_DICT_AMI3, "diterpene.xml"),
            AmiDictionaries.DRUG: os.path.join(LOCAL_DICT_AMI3, "drugs.xml"),
            AmiDictionaries.EDGE_MAMMAL: os.path.join(LOCAL_DICT_AMI3, "edgemammals.xml"),
            AmiDictionaries.ETHICS: os.path.join(LOCAL_DICT_AMI3, "ethics.xml"),
            AmiDictionaries.CHEM_ELEMENT: os.path.join(LOCAL_DICT_AMI3, "elements.xml"),
            AmiDictionaries.EPIDEMIC: os.path.join(LOCAL_DICT_AMI3, "epidemic.xml"),
            AmiDictionaries.EUROFUNDER: os.path.join(LOCAL_DICT_AMI3, "eurofunders.xml"),
            AmiDictionaries.ILLEGAL_DRUG: os.path.join(LOCAL_DICT_AMI3, "illegaldrugs.xml"),
            AmiDictionaries.INN: os.path.join(LOCAL_DICT_AMI3, "inn.xml"),
            AmiDictionaries.INSECTICIDE: os.path.join(LOCAL_DICT_AMI3, "insecticide.xml"),
            AmiDictionaries.MAGNETISM: os.path.join(LOCAL_DICT_AMI3, "magnetism.xml"),
            AmiDictionaries.MONOTERPENE: os.path.join(LOCAL_DICT_AMI3, "monoterpene.xml"),
            AmiDictionaries.NAL: os.path.join(LOCAL_DICT_AMI3, "nal.xml"),
            AmiDictionaries.NMR: os.path.join(LOCAL_DICT_AMI3, "nmrspectroscopy.xml"),
            AmiDictionaries.OBESITY: os.path.join(LOCAL_DICT_AMI3, "obesity.xml"),
            AmiDictionaries.OPTOGENETICS: os.path.join(LOCAL_DICT_AMI3, "optogenetics.xml"),
            AmiDictionaries.PECTIN: os.path.join(LOCAL_DICT_AMI3, "pectin.xml"),
            AmiDictionaries.PHOTOSYNTH: os.path.join(LOCAL_DICT_AMI3, "photosynth.xml"),
            AmiDictionaries.PLANT_DEV: os.path.join(LOCAL_DICT_AMI3, "plantDevelopment.xml"),
            AmiDictionaries.POVERTY: os.path.join(LOCAL_DICT_AMI3, "poverty.xml"),
            AmiDictionaries.PROT_STRUCT: os.path.join(LOCAL_DICT_AMI3, "proteinstruct.xml"),
            AmiDictionaries.PROT_PRED: os.path.join(LOCAL_DICT_AMI3, "protpredict.xml"),
            AmiDictionaries.REFUGEE: os.path.join(LOCAL_DICT_AMI3, "refugeeUNHCR.xml"),
            AmiDictionaries.SESQUITERPENE: os.path.join(LOCAL_DICT_AMI3, "sesquiterpene.xml"),
            AmiDictionaries.SOLVENT: os.path.join(LOCAL_DICT_AMI3, "solvents.xml"),
            AmiDictionaries.STATISTICS: os.path.join(LOCAL_DICT_AMI3, "statistics.xml"),
            AmiDictionaries.TROPICAL_VIRUS: os.path.join(LOCAL_DICT_AMI3, "tropicalVirus.xml"),
            AmiDictionaries.WETLANDS: os.path.join(LOCAL_DICT_AMI3, "wetlands.xml"),
            AmiDictionaries.WILDLIFE: os.path.join(LOCAL_DICT_AMI3, "wildlife.xml"),
        }

        for item in self.ami3_dict_index.items():
            self.add_with_check(item[0], item[1])

    def add_with_check(self, key, file):
        if key in self.dictionary_dict:
            raise Exception("duplicate dictionary key " +
                            key + " in " + str(self.dictionary_dict))
        FileLib.check_exists(file)
        try:
            dictionary = AmiDictionary.create_from_xml_file(file)
            self.dictionary_dict[key] = dictionary
        except Exception as ex:
            logger.warning("Failed to read dictionary", file, ex)
        return


# ==========please split into TDDDict==============
# this should not be here but I can't load it from an outside file
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


class AMIDictError(Exception):
    """Basic exception for errors raised in AMIDict"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "An unspecifed error occured"
        super(AMIDictError, self).__init__(msg)



class AmiDictValidator:
    """
    reads an AmiDictinary object and validates it
    """
    def __init__(self, dictionary, path=None):
        """
        constructs validator from existing dictionary
        checks dictionary has XML root
        :param dictionary: AmiDictionary to validate
        :param path: ?path containing dictionary - validate title against filename
        """
        assert type(dictionary) is AmiDictionary, f"should be AmiDictionary, found {type(dictionary)}"
        self.ami_dictionary = dictionary
        self.validate_root(dictionary)
        self.path = path

    def validate_root(self, dictionary):
        """
        validates that dictionary.root contains XML element
        """
        assert dictionary.root is not None
        assert str(type(dictionary.root)) == "<class 'lxml.etree._Element'>", f"found: {type(dictionary.root)}"
        assert dictionary.root.tag == DICTIONARY

    def get_error_list(self):
        """
        aggregates all errors into single list
        """
        error_list = []
        error_list.extend(self.get_xml_declaration_error_list())
        error_list.extend(self.get_dictionary_element_error_list())
        logger.info (f"errors: {error_list}")
        return error_list

    def get_xml_declaration_error_list(self):
        tree = lxml.etree.ElementTree(self.ami_dictionary.root)
        info = tree.docinfo
        error_list1 = []
        if "1.0" != info.xml_version:
            error_list1.append(f"unsupported xml_version: {info.xml_version}")
        if info.encoding is None or info.encoding.upper() != "UTF-8":
            error_list1.append(f"unsupported encoding: {info.encoding}")
        if info.doctype is not None and info.doctype != '':
            error_list1.append(f"DOCTYPE unsupported {info.doctype}")
        return error_list1

    def get_dictionary_element_error_list(self):
        """
        Validate <dictionary> element and return errors
        """
        error_list1 = []
        title = self.ami_dictionary.title
        if not title:
            error_list1.append(f"Dictionary does not have title")
        if not self.ami_dictionary.file:
            error_list1.append(f"Dictionary does not have file")
        if self.ami_dictionary.file != self.ami_dictionary.file:
            error_list1.append(f"Dictionary file {self.ami_dictionary.file} does not match title {self.ami_dictionary.title}")

        return error_list1


