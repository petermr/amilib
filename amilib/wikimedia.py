import copy
import json
import logging
import os
import re
import sys
from enum import Enum
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

import html5lib.html5parser
import lxml.etree
import requests
from SPARQLWrapper import SPARQLWrapper
from lxml import etree as ET
from lxml import html

# local
from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.xml_lib import XmlLib

logger = Util.get_logger(__name__)

WIKIDATA_QUERY_URI = "https://www.wikidata.org/w/index.php?search="
WIKIDATA_SITE = "https://www.wikidata.org/wiki/"

STATEMENTS = "statements"
# HTML classes in WD search output
SEARCH_RESULT = "searchresult"
MW_SEARCH_RESULT_DATA = "mw-search-result-data"
MW_SEARCH_RESULTS = "mw-search-results"
MW_SEARCH_RESULT_HEADING = "mw-search-result-heading"
WB_SLLV_LV = "wikibase-sitelinklistview-listview"
ID = "id"
CLASS = "class"

BODY = "body"
DIV = "div"
NOSCRIPT = "noscript"
PRINTFOOTER = "printfooter"
HREF = "href"
TITLE = "title"
DESC = "desc"

# elements in SPARQL output
SPQ_RESULTS = "SPQ:results"
SPQ_RESULT = "SPQ:result"
SPQ_URI = "SPQ:uri"
SPQ_BINDING = "SPQ:binding"

# entry
NS_MAP = {'SPQ': 'http://www.w3.org/2005/sparql-results#'}  # add more as needed
NS_URI = "SPQ:uri"
NS_LITERAL = "SPQ:literal"

# names mapping SPARQL output to amidict
ID_NAME = "id_name"
SPQ_NAME = "sparql_name"
DICT_NAME = "dict_name"

ARTICLEs = [
    ".*((scientific|journal)\\s+)?article.*",
    ".*((scientific|academic)\\s+)?journal.*"
]
ARTS = [".*(film|song|album)"]

"""
<header class="vector-header mw-header">
    <div class="vector-header-start">
        <a href="/wiki/Main_Page" class="mw-logo">
            <img class="mw-logo-icon" src="/static/images/icons/wikipedia.png" alt="" aria-hidden="true" height="50" width="50">
            <span class="mw-logo-container skin-invert">
                <img class="mw-logo-wordmark" alt="Wikipedia" src="/static/images/mobile/copyright/wikipedia-wordmark-en.svg" style="width: 7.5em; height: 1.125em;">
                <img class="mw-logo-tagline" alt="The Free Encyclopedia" src="/static/images/mobile/copyright/wikipedia-tagline-en.svg" width="117" height="13" style="width: 7.3125em; height: 0.8125em;">
            </span>
        </a>

    </div>
<div class="vector-header-end">

    <div id="p-search" role="search" class="vector-search-box-vue  vector-search-box-collapses vector-search-box-show-thumbnail vector-search-box-auto-expand-width vector-search-box">
        <a href="/wiki/Special:Search" class="cdx-button cdx-button--fake-button cdx-button--fake-button--enabled cdx-button--weight-quiet cdx-button--icon-only search-toggle" title="Search Wikipedia [f]" accesskey="f"><span class="vector-icon mw-ui-icon-search mw-ui-icon-wikimedia-search">
            <span>Search</span>
            </span>
        </a>
        <div class="vector-typeahead-search-container">
            <div class="cdx-typeahead-search cdx-typeahead-search--show-thumbnail cdx-typeahead-search--auto-expand-width">
            </div>
        </div>
    </div>

</div>
</header>
"""


class MediawikiParser:

    WIKIPEDIA_PAGE = "wikipedia_page"
    WIKTIONARY = "wiktionary"

    def __init__(self, target=None):
        """
        construct Mediawiki parser
        :param target: type of wikimedia page , default WIKIPEDIA_PAGE
        """
        self.remove_body_xpaths = None
        self.stem = None
        self.style_txt = None
        self.break_classes = None
        self.levels = None
        self.remove_head_xpaths = None
        self.add_defaults()
        if target is not None:
            self.target = target
        # parsed compponents
        self.htmlx = None
        self.body = None
        self.main = None
        self.firstHeading = None

    def add_defaults(self):
        self.target = self.WIKIPEDIA_PAGE
        self.break_classes = [
            "mw-heading mw-heading2",
            "mw-heading mw-heading3",
            "mw-heading mw-heading4",
            "mw-heading mw-heading5",
        ]

        self.levels = [5, 4, 3, 2, 1]

        self.style_txt = """
        div {border:1px solid red; margin: 2px;}
        div.mw-heading2 {border:5px solid red; margin: 5px; background: #eee;}
        div.mw-heading3 {border:4px solid orange; margin: 4px; background: #ddd;}
        div.mw-heading4 {border:3px solid yellow; margin: 3px; background: #ccc;}
        div.mw-heading5 {border:2px solid green; margin: 2px; background: #bbb;}
        """

        self.remove_head_xpaths = [
            "/html/head/style",
            "/html/head/script",
            "/html/head/link",
            # "/html/head/meta",
            ]

        self.remove_body_xpaths = [
            ".//comment()",
            ".//button",
            ".//footer",
            ".//form",
            ".//input",
            ".//label",
            ".//nav",
            ".//script",
            ".//style",

            """
            "//a[@class='mw-jump-link' and @href='#bodyContent' and .='Jump to content']
            """
            ".//span[@class='mw-editsection']",
            ".//div[@id='mw-navigation']",
            ".//div[contains(@class,'interproject-box')]", # interwiki projects

        ]




    def parse_nest_write_entry(self, input_file, output):
        """
        reads a wiktionary file, nests the elements and writes to temp
        :param stem: wiktionary word
        :param input_file:
        :param output:
        """
        htmlx = self.read_file_and_make_nested_divs(input_file)
        self.add_div_style(htmlx)

        HtmlLib.write_html_file(htmlx, output, debug=True)

    def read_file_and_make_nested_divs(self, input_file):
        self.htmlx = HtmlUtil.parse_html_file_to_xml(input_file)
        self.body = self.get_body_and_remove_unwanted_children()

        # TODO make polymorphic with Target
        if self.target == self.WIKIPEDIA_PAGE:
            self.body_content = self.get_wikipedia_page_body_content()
        elif self.target == self.WIKTIONARY:
            self.body_content = self.get_wiktionary_body_content()

        assert self.body_content is not None
        XmlLib.remove_elements(self.body_content, [
            "./div[@class='vector-body-before-content']",
            "./div[@id='catlinks']",
        ])

        self.mw_content_text = XmlLib.get_single_element(self.body_content, "./div[@id='mw-content-text']")
        assert self.mw_content_text is not None
        XmlLib.remove_elements(self.mw_content_text, [
            "./noscript",
            "./div[@class='printfooter']",
        ])

        self.mw_content_ltr = XmlLib.get_single_element(self.mw_content_text, "./div[@class='mw-content-ltr mw-parser-output']")
        assert self.mw_content_ltr is not None
        # after this we grouo by headings

        self.group_by_headings()

        # htmlx = HtmlLib.create_html_with_empty_head_body()
        # self.add_div_style(htmlx, self.style_txt)
        #
        # body = HtmlLib.get_body(htmlx)
        # body.append(self.mw_content_ltr)

        return self.htmlx

    def get_wikipedia_page_body_content(self):
        mw_page_container_inner = XmlLib.get_single_element(
            self.body, "./div[@class='mw-page-container']/div[@class='mw-page-container-inner']")
        XmlLib.remove_elements(mw_page_container_inner, [
            "./div[@class='vector-sitenotice-container']",
            "./div[@class='vector-column-start']",
            "./div[@class='mw-footer-container']",
        ])
        assert mw_page_container_inner is not None
        mw_content_container = XmlLib.get_single_element(
            mw_page_container_inner, "./div[@class='mw-content-container']")
        assert mw_content_container is not None
        self.main = XmlLib.get_single_element(mw_content_container, "./main[@id='content']")
        assert self.main is not None
        XmlLib.remove_elements(self.main, [
            "./div[@id='siteNotice']",
            "./div[@class='vector-page-toolbar']",
            "./div[@class='vector-column-end']",
        ])
        self.header = XmlLib.get_single_element(self.main, "./header")
        assert self.header is not None
        XmlLib.remove_elements(self.header, [
            "./nav",
            "./div[@id='p-lang-btn']",
        ])
        self.firstHeading = XmlLib.get_single_element(self.header, "./h1[@id='firstHeading']")
        assert self.firstHeading is not None
        self.body_content = XmlLib.get_single_element(self.main, "./div[@id='bodyContent']")
        return self.body_content

    def group_by_headings(self):
        # self.add_h1_header(body, mw_content_ltr)
        # self.remove_non_content(mw_content_ltr)
        if self.mw_content_ltr is None:
            logger.warning("mw_content_ltr is None")
            return
        self.add_initial_break()
        child_elems = self.mw_content_ltr.xpath("./*")
        logger.debug(f"child_elems: {len(child_elems)}")
        parent_elem = self.mw_content_ltr
        for lev in self.levels:
            logger.debug(f"level {lev}")
            xpath = f"./div[@class='mw-heading mw-heading{lev}']"
            logger.debug(f"xpath is {xpath}")
            header_divs = parent_elem.xpath(xpath)
            logger.debug(f"level {lev}: xpath{xpath} found {len(header_divs)}")
            for header_div in header_divs:
                self.group_elems_of_same_level(lev, header_div)

    def get_body_and_remove_unwanted_children(self):
        self.body = HtmlLib.get_body(self.htmlx)
        unwanted_body_mw_xpaths = [
            "./a[@class='mx-jump-link']",
            "./div[@class='vector-header-container']",

            "./div[@class='vector-settings']",
        ]
        XmlLib.remove_elements(self.body, unwanted_body_mw_xpaths)
        return self.body

    def read_file_and_make_nested_divs_old(self, input_file):
        body, mw_content_ltr = self.get_mw_content_ltr(input_file)

        self.add_h1_header(body, mw_content_ltr)
        self.remove_non_content(mw_content_ltr)
        child_elems = mw_content_ltr.xpath("./*")
        logger.debug(f"child_elems: {len(child_elems)}")
        parent_elem = mw_content_ltr
        for lev in self.levels:
            logger.debug(f"level {lev}")
            xpath = f"./div[@class='mw-heading mw-heading{lev}']"
            logger.debug(f"xpath is {xpath}")
            header_divs = parent_elem.xpath(xpath)
            logger.debug(f"level {lev}: xpath{xpath} found {len(header_divs)}")
            for header_div in header_divs:
                self.group_elems_of_same_level(lev, header_div)

        htmlx = HtmlLib.create_html_with_empty_head_body()
        self.add_div_style(htmlx, self.style_txt)

        body = HtmlLib.get_body(htmlx)
        body.append(mw_content_ltr)
        return htmlx

    def get_mw_content_ltr(self, input_file):
        body = self.read_html_path()
        # mw_contents = body.xpath(".//div[div[@id='toc']]")
        mw_content_ltr = XmlLib.get_single_element(body, ".//div[contains(@class,'mw-content-ltr')]")
        assert mw_content_ltr is not None
        return body, mw_content_ltr

    def read_html_path(self, input_file, remove_non_content=True, remove_head=True, remove_empty_elements=True):
        """
        reads Wikimedia file , parses to heml and optionally reonves non-content elements
        :param input_file:
        :param remove_non_content: removes non-content elements (nav, input, buttom, etc.) default True
        :param remove_empty_elements:recursively remove empty elements

        """
        htmlx = HtmlUtil.parse_html_file_to_xml(input_file)
        body = HtmlLib.get_body(htmlx)
        if remove_head:
            self.remove_head(body)
        if remove_non_content:
            self.remove_non_content(body)
        if remove_empty_elements:
            self.remove_empty_elements(body)
        return htmlx, body

    def add_h1_header(self, body, mw_content_ltr):
        h1_headings = body.xpath(".//h1[@id='firstHeading']")
        logger.debug(f"h1_headings {h1_headings}")
        for h1_heading in h1_headings[:1]:
            logger.debug(f"added h1 {h1_heading.xpath('.//text()')}")
            mw_content_ltr.insert(0, h1_heading)

    def remove_head(self, content):
        """
        remove script, style, link from head
        :param content: parent element
        """
        XmlLib.remove_all(content, self.remove_head_xpaths, debug=True)

    def remove_non_content(self, content):
        """
        remove edit boxes, style, etc.
        :param mw_content_ltr: parent element
        """
        XmlLib.remove_all(content, self.remove_body_xpaths, debug=True)


    def remove_empty_elements(self, content):
        """
        recursively remove empty elements
        :param mw_content_ltr: parent element
        """
        xpath = ".//*[count(*)=0 and text()='']"

        empty_elements = content.xpath(xpath)
        if len(empty_elements) != 0:
            XmlLib.remove_all(empty_elements)
            self.remove_empty_elements()

    def group_elems_of_same_level(self, lev, header_div):

        if self.break_classes is None or len(self.break_classes) == 0:
            logger.warning(f"no break_classes in group elements")
            return

        header_label = header_div.attrib.get("class")
        if header_label is None:
            header_label = header_div.tag
        following_siblings = list(header_div.xpath("following-sibling::*"))
        logger.debug(f"level {lev}: following-siblings {len(following_siblings)}")
        count = 0
        # break_class = f"mw-heading mw-heading{lev}"
        for sibling in following_siblings:
            clazz = sibling.attrib.get("class")
            if clazz in self.break_classes[:lev - 1]:
                logger.debug(f"broke grouping on {clazz}")
                break
            count += 1
            logger.debug(f"moved {sibling.tag} to {header_label}")
            header_div.append(sibling)
        logger.debug(f"following siblings {count}")

    def add_div_style(self, htmlx):
        if self.style_txt is not None:
            style = ET.SubElement(HtmlLib.get_head(htmlx), "style")
            style.text = self.style_txt

    def add_initial_break(self):
        """
        adds empty high-level container to capture the material before first top-level header (currently h2)
        """
        top_level_break = ET.Element("div")
        top_level_break.attrib["class"] = "mw-heading mw-heading2"
        h2 = ET.SubElement(top_level_break, "h2")
        h2.text = ("Initial Content")
        self.mw_content_ltr.insert(0, top_level_break)

    def get_wiktionary_body_content(self):
        self.body_content = XmlLib.get_single_element(
            self.body, "./div[@id='content']/div[@id='bodyContent']")
        return self.body_content




# this should go in config files
class WikidataPredicate:
    chemistry = {
        "P31": {
            "Q11173": "chemical compound",
            "weight": 0.9
        },

        "P117": {"object": "chemical structure",
                 "weight": 0.9
                 },
        "P271": {"object": "chemical formula",
                 "weight": 0.9
                 },
        "P223": {"object": "canonical SMILES",
                 "weight": 0.9
                 },
        # "IDENTIFIER": {"InChI" : }
    }


# TODO add docstrings and check return values
class WikidataLookup:

    def __init__(self, exact_lookup=False):
        self.term = None
        self.wikidata_dict = None
        self.root = None
        self.exact_lookup = exact_lookup
        self.hits_dict = dict()

    def lookup_wikidata(self, term):
        """
        Looks up term in Wikidata and gets Q number and descriptiom

        NOTE requires Internet

        :param term: word or phrase to lookup
        :return: triple (e.g. hit0_id, hit0_description, wikidata_hits)
        """

        if not term:
            logging.warning("null term")
            return None, None, None
        self.term = term
        MAX_ENTRIES = 5
        url = WIKIDATA_QUERY_URI + quote(term.encode('utf8'))
        # logger.debug(f"url {url}")
        self.root = ParserWrapper.parse_utf8_html_to_root(url)
        body = self.root.find(BODY)
        ul = body.find(".//ul[@class='" + MW_SEARCH_RESULTS + "']")
        hit0 = None  # to avoid UnboundLocalError
        if ul is not None:
            self.wikidata_dict = self.create_dict_for_all_possible_wd_matches(ul)
            if len(self.wikidata_dict) == 0:
                assert False, f"no wikidata hits for {term}"
            sort_orders = sorted(self.wikidata_dict.items(), key=lambda item: int(item[1][STATEMENTS]), reverse=True)
            if sort_orders:
                wikidata_hits = [s[0] for s in sort_orders[:MAX_ENTRIES]]
                #  take the first
                hit0 = sort_orders[0]
            else:
                logger.debug(f"no wikidata hits for {term}")

                # TODO fix non-tuples
        if hit0 is None:
            return None, None, None
        else:

            hit0_id = hit0[0]
            hit0_description = hit0[1]["desc"]
            if hit0_description is None:
                logger.debug(f"NULL DESCRIPTION in WD {hit0[1]}")
            return hit0_id, hit0_description, wikidata_hits

    def lookup_items(self, terms):
        """looks up a series of terms and returns a tuple of list(qitem), list(desc)
        NOTE requires Internet
        :terms: strings to search for"""

        qitems = []
        descs = []
        for term in terms:
            qitem0, desc, wikidata_hits = self.lookup_wikidata(term)
            qitems.append(qitem0)
            descs.append(desc)
        return qitems, descs

    def create_dict_for_all_possible_wd_matches(self, ul):
        wikidata_dict = {}
        for li in ul:
            result_heading_a_elem = li.find("./div[@class='" + MW_SEARCH_RESULT_HEADING + "']/a")
            if result_heading_a_elem is None:
                logger.debug(f"no result_heading_a_elem in {lxml.etree.tostring(li)}")
                continue
            if not result_heading_a_elem.attrib.get(HREF):
                logger.debug(f"no href in {result_heading_a_elem}")
                continue
            qitem = result_heading_a_elem.attrib[HREF].split("/")[-1]
            if qitem in wikidata_dict:
                logger.debug(f"duplicate wikidata entry {qitem}")
            else:
                self.add_subdict_title_desc_statements(li, qitem, result_heading_a_elem, wikidata_dict)
        return wikidata_dict

    def add_subdict_title_desc_statements(self, li, qitem, result_heading_a, wikidata_dict):
        sub_dict = {}
        wikidata_dict[qitem] = sub_dict
        # make title from text children not tooltip
        text = ''.join(result_heading_a.itertext())  # acetone (Q49546)
        title = text.split("(Q")[0]
        sub_dict[TITLE] = title
        find_arg = "./div[@class='" + SEARCH_RESULT + "']/span"
        find_elem = li.find(find_arg)
        sub_dict[DESC] = None if find_elem is None else find_elem.text

        # just take statements at present (n statements or 1 statement)
        find_arg0 = "./div[@class='" + MW_SEARCH_RESULT_DATA + "']"
        text0 = li.find(find_arg0).text
        text1 = text0.split(",")[0]
        sub_dict[STATEMENTS] = text1.split(" statement")[0]

    def get_possible_wikidata_hits(self, name, blacklist=None):
        entry_hits = self.lookup_wikidata(name)
        logger.debug(f"------{name}-------")
        if not entry_hits[0]:
            # logger.debug(f" no hit for {name}")
            pass
        else:
            hits = dict()
            for qid in entry_hits[2]:
                wpage = WikidataPage(qid)
                description = wpage.get_description()
                regex = Util.matches_regex_list(description, blacklist)
                if regex:
                    logging.debug(f"{regex} // {description}")
                else:
                    logging.debug(f"\n{wpage.get_title()}\n{description}")
                    hits[qid] = wpage.get_title()
            if hits:
                self.hits_dict[name] = hits


class WikidataFilter:

    @classmethod
    def create_filter(cls, file):
        if not file:
            return None
        if not file.exists():
            logger.debug(f"no file {file}")
            return None
        filter = WikidataFilter()
        with open(file, "r") as f:
            text = f.read()
        filter.json = json.loads(text)
        # logger.debug(f"dict {type(filter.json)} {filter.json}")
        return filter


class WikidataProperty:

    def __init__(self):
        self.element = None

    def __str__(self):
        s = "WikidataProperty: "
        if self.element is not None:
            # logger.debug(f"type self.element {type(self.element)}")
            s += f"{lxml.etree.tostring(self.element)}"
        return s

    @classmethod
    def create_property_from_element(cls, html_element):
        """Create from HTML element from wikidata.org page"""
        propertyx = None
        if html_element is not None:
            propertyx = WikidataProperty()
            propertyx.element = html_element
        return propertyx

    @property
    def id(self):
        return None if self.element is None else self.element.get("id")

    @property
    def property_name(self):
        return None if self.element is None else self.element.xpath('./div/div/a')[0].text

    def extract_statements(self):
        xpath = f"./div[@class='wikibase-statementlistview']/div[@class='wikibase-statementlistview-listview']/div/div[@class='wikibase-statementview-mainsnak-container']/div[@class='wikibase-statementview-mainsnak']/div/div[@class='wikibase-snakview-value-container']/div[@class='wikibase-snakview-body']//div/a"
        statements = self.element.xpath(xpath)
        return statements

    # class WikidataProperty:

    def create_property_dict(self):
        """creates python dict from wikidata_page
        Not complete (doesn't do scalar values)"""
        # id = self.id
        name = self.property_name
        property_dict = {
            "name": name,
        }
        statements = self.extract_statements()
        if len(statements) > 0:
            statement_dict = {}
            for statement in statements:
                title = statement.get('title')
                value = statement.text
                if title:
                    statement_dict[title] = value
                    # logger.debug(f"statement {id} {value}")
                else:
                    # logger.debug(f"value: {value}")
                    property_dict["value"] = value
            if len(statement_dict) > 0:
                property_dict["statements"] = statement_dict
        return property_dict

    @classmethod
    def get_properties_dict(cls, property_list):
        """makes python dict from list of Wikidata properties
        """

        properties_dict = {}
        if not property_list:
            return properties_dict

        for propertyx in property_list:
            property_dict = propertyx.create_property_dict()
            properties_dict[propertyx.id] = property_dict
        return properties_dict


# class WikidataProperty:


def label_match(label, wikidata_label, method, ignorecase):
    raise NotImplemented("label match")


class WikidataPage:
    PROPERTY_ID = "id"

    def __init__(self, pqitem=None, file=None):

        self.root = None
        self.pqitem = pqitem
        self.json = None
        self.file = file
        if pqitem:
            self.root = self.get_root_for_item(self.pqitem)

    @classmethod
    def create_wikidata_ppage_from_file(cls, file):
        page = None
        if file and Path(file).exists():
            tree = html.parse(str(file))
            page = WikidataPage()
            page.root = tree.getroot()
            page.file = file
        return page

    @classmethod
    def create_wikidata_page_from_response(cls, response):
        if not response:
            return None
        wikidata_page = WikidataPage()
        wikidata_page.json = response.json()
        return wikidata_page

    def get_root_for_item(self, pqitem):
        """search wikidata site for QItem OR read local file
        TODO clean up reading of local wikidata file
        :return: parsed lxml root or None if not found
        :param pqitem: Qitem (or P item to search
        """
        if self.root is None:
            if not pqitem:
                return None
            url_for_pqitem = self.get_url_for_pqitem(pqitem)
            if url_for_pqitem:
                self.root = ParserWrapper.parse_utf8_html_to_root(url_for_pqitem)
        return self.root

    def get_url_for_pqitem(self, qitem):
        """
        Creates URL to lookup up P or Q item in wikidata.org
        :param qitem: P or Q item (case-insensive)
        :return: URL or None (doesn't match syntax)
        """
        pq_re = re.compile("[PpQq]\\d+")
        if pq_re.match(qitem):
            return self.get_wikidata_site() + qitem
        return None

    @classmethod
    def get_wikidata_site(cls):
        return WIKIDATA_SITE

    # WikidataPage

    def get_wikipedia_page_links(self, lang_list=["en"]):
        """
        get dict of Wikipedia URLS by language
        :param lang_list: list of ISO languages
<h2 class="wb-section-heading section-heading wikibase-sitelinks" dirx="auto">
  <span class="mw-headline" id="sitelinks">Sitelinks</span></h2>
  <div class="wikibase-sitelinkgrouplistview">
    <div class="wikibase-listview">
      <div class="wikibase-sitelinkgroupview mw-collapsible" data-wb-sitelinks-group="wikipedia">
        <div class="wikibase-sitelinkgroupview-heading-section">
          <div class="wikibase-sitelinkgroupview-heading-container">
            <h3 class="wb-sitelinks-heading" dirx="auto" id="sitelinks-wikipedia">Wikipedia<span
            class="wikibase-sitelinkgroupview-hit_counter">(27 entries)</span></h3>
            <span class="wikibase-toolbar-container">
              <span class="wikibase-toolbar-item wikibase-toolbar ">
                <span class="wikibase-toolbar-item wikibase-toolbar-button wikibase-toolbar-button-edit">
                  <a href="/wiki/Special:SetSiteLink/Q144362" title="">
                    <span class="wb-icon"></span>edit
                  </a>
                </span>
            </span>
        </span>
        </div>
        </div>
<div class="mw-collapsible-content">
<div class="wikibase-sitelinklistview">
<ul class="wikibase-sitelinklistview-listview">
  <li class="wikibase-sitelinkview wikibase-sitelinkview-arwiki" data-wb-siteid="arwiki">
    <span class="wikibase-sitelinkview-siteid-container">
      <span class="wikibase-sitelinkview-siteid wikibase-sitelinkview-siteid-arwiki" title="Arabic">arwiki</span>
    </span>
    <span class="wikibase-sitelinkview-link wikibase-sitelinkview-link-arwiki">
      <span class="wikibase-sitelinkview-page" dirx="auto" lang="ar">
        <a href="https://ar.wikipedia.org/wiki/%D8%A2%D8%B2%D9%88%D9%84%D9%8A%D9%86" hreflang="ar"
        title="آزولين">آزولين</a>
      </span>
      <span class="wikibase-badgeselector wikibase-sitelinkview-badges"></span>
    </span>
  </li>
  ...
  <li class="wikibase-sitelinkview wikibase-sitelinkview-enwiki" data-wb-siteid="enwiki">
    <span class="wikibase-sitelinkview-siteid-container">
      <span class="wikibase-sitelinkview-siteid wikibase-sitelinkview-siteid-enwiki" title="English">enwiki</span>
    </span>
    <span class="wikibase-sitelinkview-link wikibase-sitelinkview-link-enwiki">
      <span class="wikibase-sitelinkview-page" dirx="auto" lang="en">
        <a href="https://en.wikipedia.org/wiki/Azulene" hreflang="en" title="Azulene">Azulene</a>
      </span>
      <span class="wikibase-badgeselector wikibase-sitelinkview-badges"></span>
    </span>
  </li>
        """
        # ul = root.find(".//ul[@class='" + "wikibase-sitelinklistview-listview" +"']")
        #     li_lang = ul.find("./li[@data-wb-siteid='" +f"{lang}wiki" + "']")
        #     ahref = li_lang.find(".//a[@hreflang]")
        #     logger.error(ahref.attrib["href"])

        lang_pages = {}
        if lang_list:
            for lang in lang_list:
                href_lang = ".//ul[@class='" + WB_SLLV_LV + "']" + "/li[@data-wb-siteid='" + f"{lang}wiki" + "']" + \
                            "//a[@hreflang]"
                a = self.root.find(href_lang)
                if a is not None:
                    lang_pages[lang] = a.attrib[HREF]
        return lang_pages

    def get_wikipedia_page_link(self, lang="en"):
        """
        gets WikipediaPage for WikidataPage
        :param lang: ISO langiage code
        :return: URL
        """
        if not lang:
            return None
        lang = lang.lower()
        url_dict = self.get_wikipedia_page_links([lang])
        return url_dict.get(lang)

    def get_image(self):
        pass

    """
    <div class="wikibase-statementgroupview" id="P5037" data-property-id="P5037">
    <div class="wikibase-statementgroupview-property">
    """

    # WikidataPage

    def get_property_ids(self):
        pdivs = self.root.findall(".//div[@class='wikibase-statementgroupview']")
        ids = [pdiv.attrib[ID] for pdiv in pdivs]
        return ids

    def get_data_property_list(self):
        """gets data_properties (the Statements and Identifiers)
        :return: list of properties as WikidataProperty , may be empty
        USEFUL
        """
        selector = WikidataPage.get_data_property_xpath()
        property_element_list = self.root.xpath(selector)
        property_list = [WikidataProperty.create_property_from_element(p_element) for p_element in
                         property_element_list]
        return property_list

    @classmethod
    def get_data_property_xpath(cls):
        """selector for data_properties """
        return f".//div[@data-property-id]"

    def get_property_id_list(self):
        """get list of ids presenting properties
        These will be in the left-hand column of the page
        :return: ids , example ['P31', 'P279', 'P361', 'P117']"""
        property_list = self.get_data_property_list()  # WikidataProperty
        property_id_list = [property.id for property in property_list]
        return property_id_list

    def get_property_name_list(self):
        """get list of property names (left-hand column of page]
        :return: names, e.g. ['instance of', 'subclass of', 'part of', 'chemical structure']
         """
        property_list = self.get_data_property_list()
        property_name_list = [property.property_name for property in property_list]
        return property_name_list

    def get_qitems_for_property_id(self, property_id):
        """get qitem/s for a property
        USEFUL (but fragile as HTML page may change)
        :param property_id: id such as 'P31'
        :return: list of xml_elements representing values

        """
        qvals = []
        hdiv_p = self.root.xpath(f".//div[@id='{property_id}']")
        if len(hdiv_p) >= 1:
            qvals = hdiv_p[0].xpath(".//div[@class='wikibase-snakview-body']//a[starts-with(@title,'Q')]")
        return qvals

    @classmethod
    def get_predicate_object_from_file(cls, wikidata_file, pred, obj):
        """finds wikidata predicate+object
        a WikidataPage contains a list of predicate+obj
        we search with their values
        :param
        """
        wikidata = WikidataPage(wikidata_file)
        # root = html.parse(wikidata_file).getroot()
        pred_obj_list = wikidata.get_predicate_object(pred, obj)
        return pred_obj_list

    def get_predicate_object(self, pred, obj):
        """get predicate-object from their id pair
        :param pred: e.g. "P31"
        :param obj:
        :return: list of all pairs
        """
        pred_obj_list = self.root.xpath(
            f".//div[@id='{pred}']//div[@class='wikibase-snakview-body']//a[@title='{obj}']")
        return pred_obj_list

    def get_title(self):
        """gets title (string preceeding Q/P number)
        identical to label in language of browser (or only en?)
        """
        if self.root is None:
            return "No title"
        title_elem_list = self.root.xpath(
            f"/html/body/div/h1/span/span[normalize-space(@class)='wikibase-title-label']")
        title = title_elem_list[0].text
        return title

    def get_aliases(self):
        """gets aliases ("also known as")
        """
        """
        < ul
        class ="wikibase-entitytermsview-aliases" >
        < li class ="wikibase-entitytermsview-aliases-alias" data-aliases-separator="|" > l-menthol < / li > 
        < li class ="wikibase-entitytermsview-aliases-alias" data-aliases-separator="|" > levomenthol < / li > 
        """
        alias_elem_list = self.root.xpath(
            f"/html/body//ul[normalize-space(@class)='wikibase-entitytermsview-aliases']/li")
        alias_list = [li.text for li in alias_elem_list]
        return alias_list

    def get_description(self):
        """gets description (maybe in English?)
        precedes the aliases

        <div class="wikibase-entitytermsview-heading-description">chemical compound</div>

        """
        desc_list = self.get_elements_for_normalized_attrib_val("class", "wikibase-entitytermsview-heading-description")
        desc = "" if not desc_list else desc_list[0].text
        return desc

    def get_aliases_from_wikidata_page(self):
        """
        <div class="wikibase-entitytermsview-heading-description ">chemical compound</div>
        <div class="wikibase-entitytermsview-heading-aliases ">
            <ul class="wikibase-entitytermsview-aliases">
                <li class="wikibase-entitytermsview-aliases-alias" data-aliases-separator="|">propanone</li>
                <li class="wikibase-entitytermsview-aliases-alias" data-aliases-separator="|">dimethylketone</li>
                ...
            </ul>
        </div>
        """
        li_list = self.root.xpath(
            ".//div[normalize-space(@class)='wikibase-entitytermsview-heading-aliases']/ul/li[@class='wikibase-entitytermsview-aliases-alias']")
        aliases = [li.text for li in li_list]
        return

    def get_id(self):
        """
        get id from <span class="wikibase-title-id">(Q42)</span>
        remove brackets
        :return: P/Q id or None
        """
        id_list = self.get_elements_for_normalized_attrib_val("class", "wikibase-title-id")
        id = None if not id_list else id_list[0].text
        if id:
            id = id.strip("(").strip(")")
        else:
            id = None
        return id

    def get_elements_for_normalized_attrib_val(self, attname, attval, lead="//*", trail=""):
        """some attvals contain leading/trailing space
        searches for <lead>/*[@foo=bar] where bar might be whitespaced
        :param attname: attribute name
        :param attval: normalized attribute value required
        :param lead: leading string (e.g. "/html//*")
        :param trail: trailing string (e.g. "/li"
        """
        if self.root is None:
            return []
        xpath = self.create_xpath_for_equality_whitespaced_attvals(attname, attval, lead=lead, trail=trail)
        elems = self.root.xpath(xpath)
        return elems

    def create_xpath_for_equality_whitespaced_attvals(self, attname, attval, lead="", trail=""):
        """Some attribute values have extraneous whitespace
        <zz foo="bar "/>
        then [@foo='bar'] fails
        This is a hack
        :param attname: attribute name
        :param attval: normalized attribute value required
        :param lead: leading string (e.g. "/html//*")
        :param trail: trailing string (e.g. "/li"
        return xpath
        """

        xpath = f"{lead}[concat(' ',normalize-space(@{attname}),' ')=concat(' ',normalize-space('{attval}'),' ')]{trail}"
        return xpath

    def get_elements_for_attval_containing_word(self, attname, attval, lead="//*", trail=""):
        """some attvals contain leading/trailing space
        searches for <lead>/*[@foo=bar] where bar might be whitespaced
        :param attname: attribute name
        :param attval: normalized attribute value required
        :param lead: leading string (e.g. "/html//*")
        :param trail: trailing string (e.g. "/li"
        """
        xpath = self.create_xpath_for_contains_whitespaced_attvals(attname, attval, lead=lead, trail=trail)
        # logger.error(f"{xpath}")
        elems = self.root.xpath(xpath)
        return elems

    def create_xpath_for_contains_whitespaced_attvals(self, attname, attval, lead="", trail=""):
        """searches for complete words in whitespace-concatenated attribute values
        <zz foo="bar plugh barbara plinge"/>
        searches for 'bar' but not 'barbara'
        Not tested
        :param attname: attribute name
        :param attval: normalized attribute value required
        :param lead: leading string (e.g. "/html//*")
        :param trail: trailing string (e.g. "/li"
        return xpath
        """

        xpath = f"{lead}[contains(concat(' ',normalize-space(@{attname}),' '),concat(' ',normalize-space('{attval}'),' '))]{trail}"
        return xpath

    # WikidataPage

    def title_matches(self, wikidata_title, ignorecase=True):
        """
        does the wikidata_title match the title of the psge
        """
        if not wikidata_title:
            return False
        title = self.get_title()
        if not title:
            return False
        if ignorecase:
            title = title.lower()
            wikidats_title = wikidata_title.lower()
        return title == wikidata_title

    class WikidataLabelMatch(Enum):
        EXACT = 1,
        SUBSTRING = 2,

    def find_name_to_wikidata_match(labels=None,
                                    ids=None,
                                    wikidata_label=None,
                                    method=WikidataLabelMatch.EXACT,
                                    ignorecase=True,
                                    ):
        """iterate over list of wikidata titles/labels to find closest/exact match for title
        :param titles: list of previously extracted wikidata labels
        NOT YET USED
        """
        if labels is None:
            logging.info(f"no labels given")
            return None
        if ids is None:
            logging.error(f"must give list of ids")
            return None
        if len(labels) != len(ids):
            logging.error(f"labels {labels} and ids {ids} are different lengths")
            return None
        if wikidata_label is None:
            logging.error(f"must give required wikidata label")
            return None
        idlist = []
        for label, id in zip(labels, ids):
            if label_match(label, wikidata_label, method, ignorecase):  # METHOD NOT WRITTEN
                idlist.append(id)

    """<div class="wikibase-entitytermsview-heading-description">chemical compound</div>"""

    def debug_page(self):
        """debug crude"""
        if self.root is None:
            logger.error(f"no root for wikidata")
        else:
            HtmlUtil.write_html_elem(self.root, sys.stdout, pretty_print=True)

    # @classmethod
    # def get_first_para(cls, html_element):
    #     """
    #     get the first paragraph (p) - normally the definition
    #     :param html_element: trimmed html from Wikipedia
    #     TODO make this an instance method
    #     TODO deal with disambiguation
    #     """
    #     main_element = copy(WikipediaPage.get_main_element(html_element))
    #     XmlLib.write_xml(html_element, Path(Resources.TEMP_DIR, "html", "junk", f"{datetime.datetime.now()}.html"), debug=True)
    #     if main_element is None:
    #         print(f"none main_element")
    #         return None
    #     ps = main_element.xpath(".//p")
    #     print(f"len ps {len(ps)}")
    #
    #     for p in ps:
    #         text = p.text
    #         print(f"text:: {text[:50]}")
    #     if len(ps) == 0:
    #         print(f"no paras: ")
    #     else:
    #         return ps[0]


class WikidataSparql:

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def update_from_sparql(self, sparql_file, sparql_to_dictionary):
        self.sparql_to_dictionary = sparql_to_dictionary

        self.dictionary.check_unique_wikidata_ids()
        self.create_sparql_result_list(sparql_file)
        self.create_sparql_result_by_wikidata_id()
        self.update_dictionary_from_sparql()

    def create_sparql_result_list(self, sparql_file):
        assert (os.path.exists(sparql_file))
        logger.info(f"sparql path {sparql_file}")
        self.current_sparql = ET.parse(sparql_file, parser=ET.XMLParser(encoding="utf-8"))
        self.sparql_result_list = list(self.current_sparql.findall(SPQ_RESULTS + "/" + SPQ_RESULT, NS_MAP))
        assert (len(self.sparql_result_list) > 0)
        logger.info(f"results {len(self.sparql_result_list)}")

    def create_sparql_result_by_wikidata_id(self):
        self.sparql_result_by_wikidata_id = {}
        id_element = self.sparql_to_dictionary[ID_NAME]
        for result in self.sparql_result_list:
            # TODO fix syntax
            # bindings = result.findall(SPQ_BINDING + "[@name='%s']/" + SPQ_URI % id_element, NS_MAP)
            # print(f"NS_MAP {NS_MAP}")
            # print(f"result {result} {ET.tostring(result)}")
            spq_uri = SPQ_BINDING + f"[@name='{id_element}']/" + SPQ_URI
            # print(spq_uri)
            bindings = result.findall(spq_uri, namespaces=NS_MAP)
            if len(bindings) == 0:
                # print(f"no bindings for {id_element}")
                pass
            else:
                uri = list(bindings)[0]
                wikidata_id = uri.text.split("/")[-1]
                if wikidata_id not in self.sparql_result_by_wikidata_id:
                    self.sparql_result_by_wikidata_id[wikidata_id] = []
                self.sparql_result_by_wikidata_id[wikidata_id].append(result)

    # WikidataSparql

    def update_dictionary_from_sparql(self):

        logger.info("sparql result by id {len(self.sparql_result_by_wikidata_id)}")
        sparql_name = self.sparql_to_dictionary[SPQ_NAME]
        dict_name = self.sparql_to_dictionary[DICT_NAME]
        for wikidata_id in self.sparql_result_by_wikidata_id.keys():
            if wikidata_id in self.dictionary.entry_by_wikidata_id.keys():
                entry = self.dictionary.entry_by_wikidata_id[wikidata_id]
                result_list = self.sparql_result_by_wikidata_id[wikidata_id]
                for result in result_list:
                    bindings = list(result.findall(SPQ_BINDING + "/" + f"[@name='{sparql_name}']", NS_MAP))
                    if len(bindings) > 0:
                        binding = bindings[0]
                        self.update_entry(entry, binding, dict_name)

    #                print("dict", ET.tostring(entry))

    def update_entry(self, entry, binding, dict_name):
        updates = list(binding.findall(NS_URI, NS_MAP)) + \
                  list(binding.findall(NS_LITERAL, NS_MAP))
        entry_child = ET.Element(dict_name)
        entry_child.text = updates[0].text
        if entry_child.text is not None and len(entry_child.text.strip()) > 0:
            entry.append(entry_child)

    def get_results_xml(self, query):
        """query Wikidata SPARQL endpoint and return XML results
        Shweata M Hegde and Peter Murray-Rust
        :query: as SPARQL
        :return: xml <results>"""
        WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(WIKIDATA_SPARQL_ENDPOINT, agent=user_agent)
        sparql.setQuery(query)
        # sparql.setReturnFormat(XML)
        return sparql.query().convert().toxml()


class ParserWrapper:
    @classmethod
    def parse_utf8_html_to_root(cla, url):

        if url is None:
            raise ValueError("url is None")
        try:
            content = None
            with urlopen(url) as u:
                content = u.read().decode("utf-8")
        except HTTPError as e:
            logger.info(f"cannout open {url} because {e}")
            raise URLError(f"failed to read {url} because {e}")
        tree = ET.parse(StringIO(content), ET.HTMLParser())
        root = tree.getroot()
        return root


class WikidataExtractor:
    """Thanks to Awena for showing the approach"""
    VERSION = "0.1"
    USER_AGENT = "Mozilla/5.0 (compatible; Pyami/" + VERSION + "; +https://github.com/petermr/pyami/)"
    WIKIDATA_API = "https://www.wikidata.org/w/api.php"

    def __init__(self, lang='en'):
        self.lang = lang.lower()
        self.cache = {}
        self.query = None
        self.number_of_requests = 0
        self.result = None

    def __str__(self):
        return self.query

    def __len__(self):
        return len(self.cache)

    def __eq__(self, other):
        if isinstance(other, bool):
            return bool(self.cache) == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def number_of_requests(self):
        return self.number_of_requests

    def search(self, query):
        return self._request(query, False)

    def load(self, id=None):
        if not id:
            return {}
        if id not in self.cache:
            data = self._request(False, id)
            self.cache[id] = self._parse(data, id)
        return self.cache[id]

    def _request(self, query=False, id=False):
        headers = {
            "User-Agent": WikidataExtractor.USER_AGENT
        }

        params, self.query = self.get_params(id, query)
        data = requests.get(self.WIKIDATA_API, headers=headers, params=params)
        result = data.json()
        self.result = result

        self.number_of_requests += 1
        CODE = "code"
        ENTITIES = "entities"
        ERR = "error"
        ID = "id"
        INFO = "info"
        LANGUAGE = "language"
        MATCH = "match"
        SEARCH = "search"
        TEXT = "text"

        if ERR in result:
            raise Exception(result[ERR][CODE], result[ERR][INFO])
        elif query and SEARCH in result and result[SEARCH]:
            guess = None
            for item in result[SEARCH]:
                if ID in item and MATCH in item and TEXT in item[MATCH] and LANGUAGE in item[MATCH]:
                    if item[MATCH][LANGUAGE] == self.lang:
                        if not guess:
                            guess = item[ID]
                        if item[MATCH][TEXT].lower().strip() == query.lower():
                            return item[ID]
                return guess
        elif id and ENTITIES in result and result[ENTITIES]:
            if id in result[ENTITIES] and result[ENTITIES][id]:
                return result[ENTITIES][id]
        if query:
            return {}
        # return None
        return result

    def get_params(self, id, query):
        params = None
        if id:
            params = {
                "action": "wbgetentities",
                "ids": id,
                "language": self.lang,
                "format": "json"
            }
        elif query:
            query = query.strip()
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": self.lang,
                "format": "json"
            }
        return params, query

    def _parse(self, data, id):
        DESCRIPTION = "description"
        DESCRIPTIONS = "descriptions"
        ID = "id"
        LABEL = "label"
        LABELS = "labels"
        VALUE = "value"

        result = {ID: id}
        if id and data:
            if LABELS in data:
                if self.lang in data[LABELS]:
                    result[LABEL] = data[LABELS][self.lang][VALUE]
            if DESCRIPTIONS in data:
                if self.lang in data[DESCRIPTIONS]:
                    result[DESCRIPTION] = data[DESCRIPTIONS][self.lang][VALUE]
        # if "claims" in data:
        # 	# results to human readable format
        # 	for key	in data["claims"]:
        # 		try:
        # 			if key=="P31":		# instance of
        # 				result["instance"]			= data["claims"][key][0]["mainsnak"]["datavalue"]["value"]["id"]
        return result


class WikipediaPage:
    WM_DISAMBIGUATION_PAGE = "Wikimedia disambiguation page"

    FIRST_PARA = "wpage_first_para"
    FIRST_PARA = "wpage_first_para"
    WIKIPEDIA_PHP = "https://en.wikipedia.org/w/index.php?"

    def __init__(self):
        self.html_elem = None
        self.search_term = None
        self.search_url = None

    @classmethod
    def lookup_wikipedia_page_for_term(cls, search_term):
        """
        gets Wikipedia URL by term.
        Also gets exact page if last fiels of URL is used
        :param search_term: term/phrase to search with
        :return: new WikipediaPage or None
        """

        "https://en.wikipedia.org/w/index.php?search=lulucx&title=Special%3ASearch&ns0=1"
        url = f"{WikipediaPage.WIKIPEDIA_PHP}search={search_term}"
        wikipedia_page = cls.lookup_wikipedia_page_for_url(url)
        wikipedia_page.search_term = search_term
        return wikipedia_page

    @classmethod
    def lookup_wikipedia_page_for_url(cls, url):
        """
        lookup wikipedia page by url
        The url may not be the final address of the page
        :param url: url to search with
        :return: WikipediaPage or None
        """
        wikipedia_page = None
        if url is not None:
            try:
                response = requests.get(url)
                decode = response.content.decode("UTF-8")
                html_content = HtmlLib.parse_html_string(decode)
                wikipedia_page = WikipediaPage()
                wikipedia_page.html_elem = html_content
                wikipedia_page.search_url = url
            except Exception as e:
                logger.info(f"HTML exception {e}")
        return wikipedia_page

    def get_main_element(self):
        """gets main content from Wikipedia page
        also cleans some non-content elements incl buttons, navs, etc.
        """
        try:
            main_contents = self.html_elem.xpath(".//main")
            main_content = main_contents[0]
        except Exception as e:
            logger.debug(f"except {e}")
            return None
        XmlLib.remove_elements(main_content, xpath="//nav")
        XmlLib.remove_elements(main_content, xpath="//noscript")
        XmlLib.remove_elements(main_content, xpath="//div[@id='p-lang-btn']")
        return main_content

    def create_first_wikipedia_para(self):
        """
        get wrapper for first paragraph in main content (usually with definitions in lead sentence
        """
        main_elem = self.get_main_element()
        ps = main_elem.xpath(".//p")
        if not ps:
            return None
        # iterate until meaningfile para length found
        for p in ps:
            text = XmlLib.get_text(p).strip()
            if len(text) > WikipediaPara.MIN_FIRST_PARA_LEN:
                return WikipediaPara(self, p, para_class=WikipediaPage.FIRST_PARA)
        return None

    def get_wikidata_item(self):
        """
<li id="t-wikibase" class="mw-list-item">
<a href="https://www.wikidata.org/wiki/Special:EntityPage/Q13461160"
    title="Structured data on this page hosted by Wikidata [g]" accesskey="g">
<span>Wikidata item</span>
</a>
</li>
        """
        if self.html_elem is not None:
            wds = self.html_elem.xpath(".//li[a[span[text()='Wikidata item']]]")
            spans = self.html_elem.xpath(".//span[.='Wikidata item']")
            alist = self.html_elem.xpath(".//li/a[span[.='Wikidata item']]")
            if len(wds) > 0:
                alist = wds[0].xpath("a")
                href = alist[0].attrib.get("href")
                return href
        return None

    @classmethod
    def create_html_of_leading_wp_paragraphs(cls, words, outfile=None, debug=True):
        """
        looks up Wikipedia entries for list of words and optionally writes to file
        :param words: list of words/phrases to search for
        :param outfile: optional output file for paragraphs
        :param debug: debug output
        :return: html file with list of paragraphs
        """
        html_out = HtmlLib.create_html_with_empty_head_body()
        new_body = HtmlLib.get_body(html_out)
        for word in words:
            if debug:
                logger.info(f"\nword: {word}")
            cls.create_html_of_leading_wp_para(new_body, word, debug)
            first_wp_para = WikipediaPage.get_leading_paragraph_for_word(new_body, word)
            if first_wp_para is not None:
                div = ET.SubElement(new_body, "div")
                div.append(first_wp_para.para_element)
        if outfile:
            XmlLib.write_xml(new_body, outfile, debug=debug)
        return html_out

    @classmethod
    def create_html_of_leading_wp_para(cls, parent_elem, word, debug=False):
        first_wp_para = WikipediaPage.get_leading_paragraph_for_word(parent_elem, word)
        if (first_wp_para is not None):
            div = ET.SubElement(parent_elem, "div")
            div.append(first_wp_para.para_element)

    @classmethod
    def get_leading_paragraph_for_word(cls, new_body, word):

        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_term(word)
        first_wp_para = None
        if wikipedia_page is not None:
            first_wp_para = wikipedia_page.create_first_wikipedia_para()
        return first_wp_para

    @classmethod
    def get_page_for_url(cls, url):
        pass

    def get_qitem_from_wikipedia_page(self):
        """
        gets Qitem from wikipedia page
        navigates right menu (2024)
        :return:pqid or None
        """
        ahrefs = self.html_elem.xpath(".//li[@id='t-wikibase']/a[@href]")
        qitem = None
        if len(ahrefs) == 1:
            ahref = ahrefs[0]
            href = ahref.get("href")
            qitem = href.split("/")[-1]
        return qitem

    def get_infobox(self):
        """
        <table class="infobox biography vcard">
          <tbody>
            <tr><th colspan="2" class="infobox-above">
              <div class="fn">Peter Murray-Rust</div></th></tr>
              <tr><td colspan="2" class="infobox-image">
                <span class="mw-default-size" typeof="mw:File/Frameless">
                  <a href="/wiki/File:Peter_Murray-Rust,8083939.JPG" class="mw-file-description">
                    <img src="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Peter_Murray-Rust%2C8083939.JPG/220px-Peter_Murray-Rust%2C8083939.JPG" decoding="async" width="220" height="293" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Peter_Murray-Rust%2C8083939.JPG/330px-Peter_Murray-Rust%2C8083939.JPG 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/31/Peter_Murray-Rust%2C8083939.JPG/440px-Peter_Murray-Rust%2C8083939.JPG 2x" data-file-width="3024" data-file-height="4032"></a></span>
                    <div class="infobox-caption">at Wikimania 2014</div></td></tr><tr><th scope="row" class="infobox-label">Born</th>
                    <td class="infobox-data">1941 (age&nbsp;82–83)<br><div style="display:inline" class="birthplace"><a href="/wiki/Guildford" title="Guildford">Guildford</a>, England</div></td></tr><tr><th scope="row" class="infobox-label">Alma&nbsp;mater</th><td class="infobox-data"><a href="/wiki/Balliol_College,_Oxford" title="Balliol College, Oxford">Balliol College, Oxford</a></td></tr><tr><th scope="row" class="infobox-label">Known&nbsp;for</th><td class="infobox-data"><style data-mw-deduplicate="TemplateStyles:r1126788409">.mw-parser-output .plainlist ol,.mw-parser-output .plainlist ul{line-height:inherit;list-style:none;margin:0;padding:0}.mw-parser-output .plainlist ol li,.mw-parser-output .plainlist ul li{margin-bottom:0}</style><div class="plainlist">
<ul><li><a href="/wiki/Blue_Obelisk" title="Blue Obelisk">Blue Obelisk</a></li>
<li><a href="/wiki/Chemical_Markup_Language" title="Chemical Markup Language">Chemical Markup Language</a></li>
</ul>
</div></td></tr><tr><th scope="row" class="infobox-label">Awards</th><td class="infobox-data"><a href="/wiki/Herman_Skolnik_Award" title="Herman Skolnik Award">Herman Skolnik Award</a></td></tr><tr><td colspan="2" class="infobox-full-data"><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1229112069"><b>Scientific career</b></td></tr><tr><th scope="row" class="infobox-label">Fields</th><td class="infobox-data category"><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1126788409"><div class="plainlist">
<ul><li><a href="/wiki/Chemistry" title="Chemistry">Chemistry</a></li>
<li><a href="/wiki/Cheminformatics" title="Cheminformatics">Cheminformatics</a></li></ul>
</div></td></tr><tr><th scope="row" class="infobox-label">Institutions</th><td class="infobox-data"><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1126788409"><div class="plainlist">
<ul><li><a href="/wiki/University_of_Cambridge" title="University of Cambridge">University of Cambridge</a></li>
<li><a href="/wiki/University_of_Oxford" title="University of Oxford">University of Oxford</a></li>
<li><a href="/wiki/University_of_Stirling" title="University of Stirling">University of Stirling</a></li>
<li><a href="/wiki/University_of_Nottingham" title="University of Nottingham">University of Nottingham</a></li>
<li><a href="/wiki/GlaxoSmithKline" class="mw-redirect" title="GlaxoSmithKline">Glaxo</a></li></ul>
</div></td></tr><tr><th scope="row" class="infobox-label"><a href="/wiki/Thesis" title="Thesis">Thesis</a></th><td class="infobox-data"><i><a rel="nofollow" class="external text" href="http://ora.ox.ac.uk/objects/uuid:a5979458-2d50-4bfc-b728-de1f4e0bf14d">A structural investigation of some compounds showing charge-transfer properties</a></i>&nbsp;<span style="font-size:97%;">(1969)</span></td></tr><tr style="display:none"><td colspan="2">
</td></tr><tr><td colspan="2" class="infobox-full-data"><style data-mw-deduplicate="TemplateStyles:r1217611005">.mw-parser-output .side-box{margin:4px 0;box-sizing:border-box;border:1px solid #aaa;font-size:88%;line-height:1.25em;background-color:#f9f9f9;display:flow-root}.mw-parser-output .side-box-abovebelow,.mw-parser-output .side-box-text{padding:0.25em 0.9em}.mw-parser-output .side-box-image{padding:2px 0 2px 0.9em;text-align:center}.mw-parser-output .side-box-imageright{padding:2px 0.9em 2px 0;text-align:center}@media(min-width:500px){.mw-parser-output .side-box-flex{display:flex;align-items:center}.mw-parser-output .side-box-text{flex:1;min-width:0}}@media(min-width:720px){.mw-parser-output .side-box{width:238px}.mw-parser-output .side-box-right{clear:right;float:right;margin-left:1em}.mw-parser-output .side-box-left{margin-right:1em}}</style><style data-mw-deduplicate="TemplateStyles:r1096940132">.mw-parser-output .listen .side-box-text{line-height:1.1em}.mw-parser-output .listen-plain{border:none;background:transparent}.mw-parser-output .listen-embedded{width:100%;margin:0;border-width:1px 0 0 0;background:transparent}.mw-parser-output .listen-header{padding:2px}.mw-parser-output .listen-embedded .listen-header{padding:2px 0}.mw-parser-output .listen-file-header{padding:4px 0}.mw-parser-output .listen .description{padding-top:2px}.mw-parser-output .listen .mw-tmh-player{max-width:100%}@media(max-width:719px){.mw-parser-output .listen{clear:both}}@media(min-width:720px){.mw-parser-output .listen:not(.listen-noimage){width:320px}.mw-parser-output .listen-left{overflow:visible;float:left}.mw-parser-output .listen-center{float:none;margin-left:auto;margin-right:auto}}</style><div class="side-box side-box-left listen noprint listen-embedded listen-noimage"><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r1126788409">
<div class="side-box-flex">
<div class="side-box-text plainlist"><div class="haudio">
<div class="listen-file-header"><a href="/wiki/File:Peter_Murray-Rust_voice.flac" title="File:Peter Murray-Rust voice.flac">Peter Murray-Rust's voice</a></div>
<div><span typeof="mw:File"><span><span class="mw-tmh-player audio mw-file-element" style="width:215px;"><audio id="mwe_player_0_placeholder" preload="none" data-mw-tmh="" class="" width="215" style="width:215px;" data-durationhint="14" data-mwtitle="Peter_Murray-Rust_voice.flac" data-mwprovider="wikimediacommons" playsinline="" disabled="disabled" tabindex="-1"></audio><a class="mw-tmh-play" href="/wiki/File:Peter_Murray-Rust_voice.flac" title="Play audio" role="button"><span class="mw-tmh-play-icon notheme"></span></a><span class="mw-tmh-duration mw-tmh-label"><span class="sr-only">Duration: 14 seconds.</span><span aria-hidden="true">0:14</span></span></span></span></span></div>
<div class="description">recorded July 2014</div></div></div></div>
</div></td></tr><tr><th scope="row" class="infobox-label">Website</th><td class="infobox-data"><span class="url"><a rel="nofollow" class="external text" href="http://www-pmr.ch.cam.ac.uk">www-pmr<wbr>.ch<wbr>.cam<wbr>.ac<wbr>.uk</a></span></td></tr></tbody></table>
        """

        iboxes = self.html_elem.xpath(".//table[contains(@class,'infobox')]")
        wp_infobox = None
        if len(iboxes) == 1:
            wp_infobox = WikipediaInfoBox(iboxes[0])
        return wp_infobox

    def get_basic_information(self):
        """
        get BasicInformation wrapper for table


<div id="mw-content-text" class="mw-body-content">
  <div class="mw-parser-output">...
  <h2 id="Basic_information"><span id="mw-pageinfo-header-basic"></span>Basic information</h2>
  <table class="wikitable mw-page-info">
      <tbody>
         <tr id="mw-pageinfo-display-title" style="vertical-align: top;"><td>Display title</td><td>MV <i>Arctic Sea</i></td></tr>
<tr id="mw-pageinfo-default-sort" style="vertical-align: top;"><td>Default sort key</td><td>Arctic Sea, Mv</td></tr>
<tr id="mw-pageinfo-length" style="vertical-align: top;"><td>Page length (in bytes)</td><td>40,084</td></tr>
<tr id="mw-pageinfo-namespace-id" style="vertical-align: top;"><td>Namespace ID</td><td>0</td></tr>
<tr id="mw-pageinfo-article-id" style="vertical-align: top;"><td>Page ID</td><td>23947896</td></tr>
<tr style="vertical-align: top;"><td>Page content language</td><td>en - English</td></tr>
<tr id="mw-pageinfo-content-model" style="vertical-align: top;"><td>Page content model</td><td>wikitext</td></tr>
<tr id="mw-pageinfo-robot-policy" style="vertical-align: top;"><td>Indexing by robots</td><td>Allowed</td></tr>
<tr id="mw-pageinfo-watchers" style="vertical-align: top;"><td>Number of page watchers</td><td>91</td></tr>
<tr id="mw-pageinfo-visiting-watchers" style="vertical-align: top;"><td>Number of page watchers who visited in the last 30 days</td><td>2</td></tr>
<tr style="vertical-align: top;"><td><a href="/w/index.php?title=Special:WhatLinksHere/MV_Arctic_Sea&amp;hidelinks=1&amp;hidetrans=1" title="Special:WhatLinksHere/MV Arctic Sea">Number of redirects to this page</a></td><td>4</td></tr>
<tr id="mw-pageinfo-contentpage" style="vertical-align: top;"><td>Counted as a content page</td><td>Yes</td></tr>
<tr style="vertical-align: top;"><td>Wikidata item ID</td><td><a class="extiw wb-entity-link external" href="https://www.wikidata.org/wiki/Special:EntityPage/Q615783">Q615783</a></td></tr>
<tr style="vertical-align: top;"><td>Local description</td><td>Ship</td></tr>
<tr style="vertical-align: top;"><td>Central description</td><td>ship built in 1992</td></tr>
<tr id="mw-pageimages-info-label" style="vertical-align: top;"><td>Page image</td><td><a href="/wiki/File:MV_Arctic_sea.svg" class="mw-file-description"><img alt="MV Arctic sea.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/7f/MV_Arctic_sea.svg/220px-MV_Arctic_sea.svg.png" decoding="async" width="220" height="156" data-file-width="1052" data-file-height="744"></a></td></tr>
<tr id="mw-pvi-month-count" style="vertical-align: top;"><td>Page views in the past 30 days</td><td><div class="mw-pvi-month"><a rel="nofollow" class="external text" href="https://pageviews.wmcloud.org/?project=en.wikipedia.org&amp;platform=all-access&amp;agent=user&amp;redirects=0&amp;range=latest-30&amp;pages=MV_Arctic_Sea">268</a></div></td></tr>
</tbody></table>

<li id="t-info" class="mw-list-item">
  <a href="/w/index.php?title=Troposphere&amp;action=info" title="More information about this page"><span>Page information</span></a></li>
        """
        tinfo = "t-info"

        t_info_page = self.create_tools_wikipedia_page(tinfo)
        info_xpath = ".//*[@id='Basic_information'][1]"
        h2_basics = t_info_page.html_elem.xpath(info_xpath)
        if len(h2_basics) != 1:
            logger.warning(f"cannot find Basic Information section {info_xpath}")
            return None
        h2_basic = h2_basics[0]
        parent = h2_basic.getparent()
        children = parent.xpath("*")
        idx = parent.index(h2_basic)
        idx += 1
        table_ok = children[idx]
        rows = table_ok.xpath(".//tr")
        wp_basicinfo = WikipediaBasicInfo(table_ok)
        return wp_basicinfo

    def create_tools_wikipedia_page(self, t_item):
        """
        create page for item in Tools dropdown
        :param t_item: id in Tools menu (e.g. "t-info")

        """
        # print(f"looking up t_item: {t_item}")
        ahrefs = self.html_elem.xpath(f".//li[@id='{t_item}']/a[@href]")
        ahref = ahrefs[0] if len(ahrefs) == 1 else None
        if ahref is None:
            logger.warning(f"cannot find {t_item} in drop-down tools")
            return None
        href = ahref.attrib.get("href")
        assert href is not None
        url = f"{WikipediaPage.get_default_wikipedia_url()}/{href}"
        url = url.replace("///", "/")
        wikipedia_page = WikipediaPage.lookup_wikipedia_page_for_url(url)
        return wikipedia_page

    @classmethod
    def get_default_wikipedia_url(cls):
        """
        base url (=currently "https://en.wikipedia.org/")
        """
        # return "https://www.wikipedia.org/"
        return "https://en.wikipedia.org/"

    def is_disambiguation_page(self):
        """
        uses basic info to determine whether page is a disambiguation page
        :return: Trie if basic_info.central_desceription is Wikimedia disambiguation page
        """
        is_disambig = False
        basic_info = self.get_basic_information()
        if basic_info is not None:
            central_desc = basic_info.get_central_description()
            is_disambig = central_desc == WikipediaPage.WM_DISAMBIGUATION_PAGE
        return is_disambig

    @classmethod
    def lookup_pages_for_words_in_file(cls, filestem, indir, suffix=".txt"):
        """
        from file of words/phrases lookup page in wikipedia
        input file is {indir}/{filestem}{suffix}
        :param filestem; stem of file
        :param indir: input directory
        :param suffix: of file including period
        :return: dict of Wikipedia pages {phrase:page}, phrase has spaces replaced by "_"
        """
        path = Path(indir, f"{filestem}{suffix}")
        return cls.create_page_dict_for_words_in_file(path)

    @classmethod
    def create_page_dict_for_words_in_file(cls, inpath):
        """
        from file/path of words/phrases lookup page in wikipedia
        :param inpath:file/url with list of words
        :return: dict of Wikipedia pages {phrase:page}, phrase has spaces replaced by "_"
        """
        with open(inpath) as f:
            words = f.readlines()
        page_by_word_dict = dict()
        for word in words:
            word = word.replace("\\s+", "_")
            page = cls.lookup_wikipedia_page_for_term(word)
            page_by_word_dict[word] = page
        return page_by_word_dict

    def extract_a_elem_with_image_from_infobox(self):
        """

        """
        infobox = self.get_infobox()
        if infobox is None:
            logger.warning("no infobox")
            return None
        table = infobox.get_table()
        if table is None:
           logger.warning("no table in infobox")

        figure_td_xpath = "tbody/tr/td[span[a[img]]]"
        figure_tds = table.xpath(figure_td_xpath)
        if len(figure_tds) == 0:
            logger.warning("no a elems with img in infobox table")
            return None
        td0 = figure_tds[0]
        a_elem = self.get_a_with_image_and_caption(td0)
        return a_elem

    def get_a_with_image_and_caption(self, td0):
        """
        gets a elem with child img
        """
        a_elems = td0.xpath("span/a[img]")
        return a_elems[0] if len(a_elems) > 0 else None



class WikipediaPara:
    """
    a paragraph of a WikipediaPage
    The first para is often the most important
    """
    #  split after '.' with following space(s) and [A-Z]  OR end of para
    # SENTENCE_RE = ".*\\.(\\s*$|\\s+[A-Z].*)" # maybe obsolete
    # SENTENCE_START_RE = ".*\\.\\s+[A-Z].*"
    MIN_FIRST_PARA_LEN = 20

    def __init__(self, parent, para_element=None, para_class=None):
        self.parent = parent
        self.para_element = para_element
        if self.para_element is not None and para_class:
            self.para_element.attrib[HtmlLib.CLASS_ATTNAME] = para_class

    def get_bolds(self):
        """get all <b> descendants
        :return list of <b> elements (may be empty
        """
        bolds = []
        if self.para_element is not None:
            bolds = self.para_element.xpath(".//b")
        return bolds

    def get_ahrefs(self):
        """get all <a href=''> descendants
        :return list of <a> elements (may be empty
        """
        ahrefs = []
        if self.para_element is not None:
            ahrefs = self.para_element.xpath(".//a[@href]")
        return ahrefs

    def get_texts(self):
        """returns all descendant texts
        :return: list of mixed content text objects (tail) (may be empty)
        """
        texts = [] if self.para_element is None else self.para_element.xpath(".//text()")
        return texts

    @classmethod
    def get_tuple_for_first_paragraph(cls, para, debug=True):
        """empirical approach to extract:
          * term word/phrase
          * abbreviation (in brackets)
          * definition (first sentence)
          * definition (rest of para)
          :param para: para to extract assumed to be first
          :return: (para, term, sentence, abbrev)
          """
        if not para:
            return None
        sentence = None
        term = None
        abbrev = None

        # para = self.get_leading_para()
        rex = re.compile("(.*\\.)\\s+\\.*")
        if para is None:
            return None
        # find first full stop in normal text (not bold)
        texts = para.xpath("./text()")
        for text in texts:
            # logger.debug(f"text> {text}")
            pass

        bolds = para.xpath("./b")
        for bold in bolds:
            # print(f"bold> {bold.text}")
            pass

        # split first sentence
        for tb in para.xpath("./text()|*"):
            if debug:
                try:
                    logger.debug(f"<{tb.tag}>{HtmlUtil.get_text_content(tb)}</{tb.tag}>")
                except Exception as e:
                    logger.debug(f"{tb}")
        for text in para.xpath("./text()|./b/text()"):
            if debug:
                logger.debug(f"t> {text}")

            match = rex.match(text)
            if match:
                if debug:
                    logger.debug(f">> {match.group(1)}")

        return (para, term, sentence, abbrev)


class WikipediaInfoBox:
    """
    wrapper for wikipedia infobox HTML <table>
    """

    def __init__(self, table=None):
        """
        Wrapper for Wikipedia InfoBox
        """
        self.table = table

    def get_table(self):
        return self.table


# class WikipediaBasicInfo:
#     """
#     wrapper for wikipedia basic information tabls
#     """
#
#     """
#     Display title	MV Arctic Sea
#     Default sort key	Arctic Sea, Mv
#     Page length (in bytes)	40,084
#     Namespace ID	0
#     Page ID	23947896
#     Page content language	en - English
#     Page content model	wikitext
#     Indexing by robots	Allowed
#     Number of page watchers	91
#     Number of page watchers who visited in the last 30 days	2
#     Number of redirects to this page	4
#     Counted as a content page	Yes
#     Wikidata item ID	Q615783
#     Local description	Ship
#     Central description	ship built in 1992
#     Page image	MV Arctic sea.svg
#     Page views in the past 30 days	273
#     """
#     DISPLAY_TITLE = "Display title"
#     SORT_KEY = "Default sort key"
#     PAGE_LENGTH = "Page length (in bytes)"
#     NAMESPACE_ID = "Namespace ID"
#     PAGE_ID = "Page ID"
#     PAGE_LANGAUGE = "Page content language"
#     CONTENT_MODEL = "Page content model"
#     INDEXING_BY_ROBOTS = "Indexing by robots"
#     PAGE_WATCHERS = "Number of page watchers"
#     PAGE_WATCHERS_30 = "Number of page watchers who visited in the last 30 days"
#     REDIRECTS = "Number of redirects to this page"
#     IS_CONTENT_PAGE = "Counted as a content page"
#     WIKIDATA_ITEM = "Wikidata item ID"
#     LOCAL_DESCRIPTION = "Local description"
#     CENTRAL_DESCRIPTION = "Central description"
#     PAGE_IMAGE = "Page image"
#     PAGE_VIEWS_30 = "Page views in the past 30 days"
#
#     KEYS = [
#         DISPLAY_TITLE,
#         SORT_KEY,
#         PAGE_LENGTH,
#         NAMESPACE_ID,
#         PAGE_ID,
#         PAGE_LANGAUGE,
#         CONTENT_MODEL,
#         INDEXING_BY_ROBOTS,
#         PAGE_WATCHERS,
#         PAGE_WATCHERS_30,
#         REDIRECTS,
#         IS_CONTENT_PAGE,
#         WIKIDATA_ITEM,
#         LOCAL_DESCRIPTION,
#         CENTRAL_DESCRIPTION,
#         PAGE_IMAGE,
#         PAGE_VIEWS_30,
#     ]
#
#     def __init__(self, table=None):
#         """
#         Wrapper for Wikipedia basic information
#         """
#         self.table = table
#         self.table_dict = dict()
#         self.create_table_dict()
#
#     def get_wikidata_href_id(self):
#         """
#         return wikidate href and id (Note
#         :return: (href, id) tuplpe or None
#         """
#         value = self.get_value_for_key(self.WIKIDATA_ITEM)
#         id = value.split("/")[-1]
#         return None if value is None else (value, id)
#
#     def get_local_description(self):
#         return self.get_value_for_key(self.LOCAL_DESCRIPTION)
#
#     def get_central_description(self):
#         return self.get_value_for_key(self.CENTRAL_DESCRIPTION)
#
#     def get_value_for_key(self, key):
#         return self.table_dict[key]
#
#     def get_image_url(self):
#         url_tail = self.get_value_for_key(self.PAGE_IMAGE)
#         url = f"{WikipediaPage.get_default_wikipedia_url()}{url_tail}"
#         return url
#
#     def create_table_dict(self):
#         """
#         creates name-value table, where value can be text or XML element
#         """
#         self.table_dict = dict()
#         rows = self.table.xpath(".//tr")
#         for row in rows:
#             name = self.get_cell_value(row.xpath("./td[1]")[0], 0)
#             if not name in self.KEYS:
#                 logger.warning(f"unknown key {name} in Basic Information")
#             value = self.get_cell_value(row.xpath("./td[2]")[0], 1)
#             self.table_dict[name] = value
#
#     def get_cell_value(self, td, idx):
#         """
#         HYPERLINK
#         <td>
#           <a
#             class="extiw wb-entity-link external"
#             href="https://www.wikidata.org/wiki/Special:EntityPage/Q615783"
#             >Q615783</a>
#         </td>
#         """
#         tda = td.xpath("a")  # might be a hyperlink
#         if len(tda) > 0:
#             href = tda[0].attrib.get("href")
#             aval = tda[0].text
#             href = aval if idx == 0 else href
#             return href
#         """
#         IMAGE
#         <td>
#           <a href="/wiki/File:MV_Arctic_sea.svg" class="mw-file-description">
#             <img
#               alt="MV Arctic sea.svg"
#               src="//upload.wikimedia.org/wikipedia/commons/thumb/7/7f/MV_Arctic_sea.svg/220px-MV_Arctic_sea.svg.png"
#               decoding="async"
#               width="220"
#               height="156"
#               data-file-width="1052"
#               data-file-height="744"
#               # ></a></td>"""
#         return td.text


class WiktionaryToc:
    """
    supports Wiktionary table of contents
    """


class WiktionaryPage:
    """page for wiktionary lookup
    """
    WIKTIONARY_BASE = "https://en.wiktionary.org/wiki/"
    NOT_FOUND = "Wiktionary does not yet have an entry for"
    DEFAULT_STYLE = """
    li {border : blue 1px dotted;}
    div[class=wiktionary_pos] {border : #21618c 2px solid; margin : 3px;}
    div[class=citation-whole] {display : none;}
    """

    # use enums
    class POS(Enum):
        NOUN = ("Noun", "#ffaaaa")
        ADJ = ("Adjective", "#aaffaa")
        VERB = ("Verb", "#aaaaff")
        PREP = ("Prepopsition", "#aaaaff")
        ADV = ("Adverb", "#aaaaff")
        PHRASE = ("Phrase", "#ffffaa")

    def __init__(self, html_element=None):
        self.html_element = html_element
        self.html_div = None

    @classmethod
    def create_wiktionary_page(cls, term):
        """
        lookup wiktionary page for term
        if present create WiktionaryPage and the transformed html_div with selected info
        save url in wiktionary_page
        :param term: term to look up
        :return: new WiktionaryPage object (if term is missing contains "missing" messages
        """
        html_element, mw_content_text = cls.lookup_wiktionary_content(term)
        assert mw_content_text is not None
        # cls.write_mw_content_text(mw_content_text, index=1)
        wiktionary_page = WiktionaryPage(html_element)
        language_chunks = cls.split_mw_content_text_by_language(mw_content_text)
        assert len(language_chunks) > 0, f"must have language chunks, found 0"
        # cls.write_mw_content_text(mw_content_text, index=2)

        html_div = ET.Element("div")
        html_div.append(copy.deepcopy(language_chunks))
        cls.process_parts_of_speech(html_element, mw_content_text, html_div)
        # cls.write_mw_content_text(mw_content_text, index=3)
        wiktionary_page.html_div = html_div
        logger.debug(f"html_div {ET.tostring(html_div)[:200]}...")
        wiktionary_page.url = cls.get_url(term)

        return wiktionary_page

    @classmethod
    def write_mw_content_text(cls, mw_content_text, index):
        ss = XmlLib.element_to_string(mw_content_text, pretty_print=True)
        with open((Path(FileLib.get_home(), "junk", f"junk{index}.xml")), "w") as f:
            f.write(ss)

    @classmethod
    def get_url(cls, term):
        """
        create url for wiktionary page
        in multiword terms spaces are replaced by single "_"
        :param term: term to search for (not sure about case sensitivity), spaces are normalised to "_"
        :return: normalised term prepended with WIKTIONARY_BASE
        """
        logger.error(f"{term} type {type(term)}")
        term = re.sub(r"\s+", "_", term)
        url = f"{cls.WIKTIONARY_BASE}{term}"
        # print(f"term: {term}")
        return url

    @classmethod
    def split_into_language_chunks(cls):
        """
        divide WiktionaryPage at languages
        experimental
        """

    @classmethod
    def process_parts_of_speech(cls, html_element, mw_content_text_elem, html_div):
        """
        looks for parts of speech and their immediate environment.
        probably not optimal - use languages first
        """

        stem = "junk1"
        term = cls.get_term_from_html_element(html_element)
        file = Path(FileLib.get_home(), "junk", f"{stem}.html")
        HtmlLib.write_html_file(html_element, file, pretty_print=True, debug=True)
        assert term is not None, f"term must not be None"
        WiktionaryPage.validate_mw_content(mw_content_text_elem, term, outdir=None)
        logger.debug(f"mw_content {XmlLib.element_to_string(mw_content_text_elem)}")
        # assert html_div is not None, "process_parts_of_speech arg html_div is None"
        WiktionaryPage.validate_mw_content(mw_content_text_elem, term)
        pphtml = ET.tostring(mw_content_text_elem, pretty_print=True).decode()
        logger.debug(f"mw-content-text: {pphtml}")
        for i, pos in enumerate(cls.POS):
            pos_div = cls.lookup_part_of_speech_div(pos, mw_content_text_elem)
            # assert pos_div is not None, f"no pos_div for {pos}"
            if pos_div is None:
                logger.error(f"no pos_div for {pos}")
                continue
            pos = pos_div.xpath("./h3/@id")[0]
            span_xpath = ".//span[@class='mw-editsection']"
            pos_div.attrib["class"] = pos
            pos_span = ET.Element("span")
            pos_span.text = f" ({pos[0]}) "
            edit_sects = pos_div.xpath(span_xpath)

            p_elem = cls.get_following_p(pos_div, pos)
            assert p_elem is not None
            p_elem.insert(1, pos_span)

            ol_elem = cls.get_following_ol(pos_div)
            assert ol_elem is not None, f"no ol following div"
            # HtmlUtil.remove_elems(ol_elem, "./li/ul")

            html_div.append(copy.deepcopy(pos_span))
            html_div.append(copy.deepcopy(p_elem))
            if ol_elem is not None:
                html_div.append(copy.deepcopy(ol_elem))

            # HtmlUtil.remove_elems(pos_div, xpath=span_xpath)

    @classmethod
    def get_following_p(cls, elem, pos):
        ps = elem.xpath("following-sibling::p[1]")
        if len(ps) == 0:
            # print("no p follower")
            return None
        p = ps[0]
        return p

    @classmethod
    def get_following_ol(cls, div):
        """
        :param div: with following ol
        :return: ol element or None
        """
        """children of ol

            <li>
              <span class="usage-label-sense">
                <span class="ib-brac">(</span>
                <span class="ib-content">usually <a href="https://en.wiktionary.org/wiki/derogatory#English" title="derogatory">derogatory</a></span>
                <span class="ib-brac">)</span>
              </span>
              Someone who objects to the building of an undesirable structure in their neighborhood, especially in <a href="https://en.wiktionary.org/wiki/public_policy#English" title="public policy">public policy</a> <a href="https://en.wiktionary.org/wiki/debate#English" title="debate">debate</a>.
              <dl>
                <dd><i>politically correct green (as in vegetation) <b>nimbies</b> (may object to nuclear power plants, polluting factories, etc.)</i>
                </dd>
                <dd><i>socially conservative brown (as in shirts) <b>nimbies</b> (may object to the building of jails, prisons, housing for ex-convicts, drinking or adult entertainment establishments)</i></dd>
                <dd><i>fiscally conservative green (as in money) <b>nimbies</b> (may object to the building of anything which may decrease preexisting property values)</i></dd>
              </dl>
            </li>
            """
        ols = div.xpath("following-sibling::ol[1]")
        if len(ols) == 0:
            logger.warning("no ol follower")
            return None
        # print(f"following ol")
        ol = ols[0]
        return ol
        """
            <p>
              <span class="headword-line">
                <strong class="Latn headword" lang="en">nimby</strong>
              </span>
            </p>
            """

    @classmethod
    def lookup_wiktionary_content(cls, term=None, url=None):
        """
        gets Wiktionary raw Wiktionary content
        The page is unfortunately structured as a linear list of components, so we add
        structure. The most common mw_content with a linear list of
        h3[@id] part_of_speech
        p with more info
        ol with alternative definitions
        :param url: is complete wiktionary url
        :return: (html_element, mw_content)
        """
        if term is not None:
            assert type(term) is str, f"term should be str, not {type(term)}"
            url = cls.get_url(term)
        if url is None:
            logger.debug(f"no term or url given")
            return (None, None)
        try:
            res = requests.get(url)
            html_element = HtmlLib.parse_html_string(res.content)
        except Exception as e:
            raise e
        body = HtmlLib.get_body(html_element)
        content = cls.get_content(body)
        body_content = content.xpath("./div[@id='bodyContent']")[0]
        h1_first_heading = content.xpath("./h1[@id='firstHeading']")[0]
        logger.debug(f"\n\n>>>h1 {''.join(h1_first_heading.itertext())}")
        mw_content_text = body_content.xpath("./div[@id='mw-content-text']")[0]
        return html_element, mw_content_text

    @classmethod
    def get_content(cls, body):
        content = body.xpath("./div[@id='content']")[0]
        return content

    @classmethod
    def lookup_part_of_speech_div(cls, pos, mw_content_text):
        """
        NOT YET TESYED
        lookup part of speech (Noun, Adjective, Verb) in descendants of div[@id='mw_content_text']
        :param pos: part opf speech
        :return: span of concatenated components
        """
        FileLib.write_temp_html(mw_content_text, Path(FileLib.get_home(), "junk"), "junk.html")

        val = pos.value[0]
        logger.info(f"looking for pos=={val}")
        # xps = [f"./div/div[h3[starts-with(@id,'{val}']]", f"./div/div/div[h4[@id='{val}']]"]
        xp = f".//div[h3[starts-with(@id,'{val}')]]"
        elems = mw_content_text.xpath(xp)

        if len(elems) == 1:
            elem = mw_content_text.xpath(xp)[0]
            assert elem.tag == "div", (f"expected <div> , found {elem.tag}")
            pphtml = ET.tostring(elem, pretty_print=True).decode()
            logger.debug(f"\ndiv for {val}:\n{pphtml}")
            return elem
        return None

    @classmethod
    def _has_term_not_found_message_(cls, html_element):
        """
        look for "page not found message" in html_element
        :return: TRUE if page contains some form of 'not found' message
        """

        if html_element is None:
            return False
        text = "".join(html_element.itertext())
        not_found_message = WiktionaryPage.NOT_FOUND in text
        if not_found_message:
            pass
        return not_found_message

    def has_term_not_found_message(self):
        """
        look for "page not found message" in html_element
        :return: TRUE if page contains some form of 'not found' message
        """

        return WiktionaryPage._has_term_not_found_message_(self.html_element)

    @classmethod
    def create_skeleton_html_page(cls, add_base=True, add_style=DEFAULT_STYLE):
        """
        create skeleton html_page for wiktionary
        adds HTML <base>

        :return: html_body, html_page
        """
        html_page = HtmlLib.create_html_with_empty_head_body()
        if add_base:
            base = ET.SubElement(html_page, "base")
            base.attrib["href"] = WiktionaryPage.WIKTIONARY_BASE
        if add_style:
            style = ET.SubElement(html_page, "style")
            style.text = cls.DEFAULT_STYLE
        html_body = HtmlLib.get_body(html_page)
        return html_body, html_page

    @classmethod
    def create_div_for_term(cls, term):
        """
        lookup term in Wiktionary and format results in an html div
        :param term: to lookup
        :return: html <div> element containing result of lookup
        """
        wiktionary_page = WiktionaryPage.create_wiktionary_page(term)
        if wiktionary_page.has_term_not_found_message():
            logger.debug(f" NO TERM")
        assert wiktionary_page is not None  # missing terms return a page
        # assert not wiktionary_page.has_term_not_found_message()
        return wiktionary_page.html_div

    @classmethod
    def lookup_list_of_terms(cls, terms, add_style):
        """
        reads list of terms and generates an html object with divs for each
        :param terms: list of terms as strings
        :return: html document with div children os body
        """
        html_body, html_page = WiktionaryPage.create_skeleton_html_page(add_style=add_style)
        for term in terms:
            logger.info(f"==============={term}=================")
            html_div = WiktionaryPage.create_div_for_term(term)
            if html_div is not None:
                html_body.append(html_div)
        return html_page

    @classmethod
    def loookup_wordlist_file_write_html(cls, wordfile, outdir, html_stem):
        """
        :param wordfile: input list of words, one per line
        :param outdir: output directory
        :param html_stem: file stem of html output
        :return: filename of html output
        """
        assert wordfile.exists()
        with open(wordfile, "r") as f:
            terms = f.readlines()
        terms1 = []
        for term in terms:
            # term = term.lower()
            if len(term.strip()) > 0:
                terms1.append(term)
        html_page = WiktionaryPage.lookup_list_of_terms(terms1, add_style=WiktionaryPage.DEFAULT_STYLE)
        html_out = Path(outdir, f"{html_stem}.html")
        HtmlUtil.write_html_elem(html_page, html_out)
        return html_out

    @classmethod
    def split_mw_content_text_by_language(cls, mw_content_text):
        """
        <div class="mw-heading mw-heading2">
          <h2 id="English">English</h2>
          <span class="mw-editsection">
            <span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bread&amp;action=edit&amp;section=1" title="Edit section: English"><span>edit</span></a><span class="mw-editsection-bracket">]</span>
          </span>
        </div>
        """
        h2_with_ids = mw_content_text.xpath("./div/div/h2[@id]")
        # get all ids
        # id_list = [h2.attrib.get("id") for h2 in h2_with_ids]
        # print (f"idlist {id_list}")
        language_chunks = []
        mw_grandchildren = mw_content_text.xpath("./div/*")

        level_class_list = [
            ("h2", "lang"),
            ("h3", "etym"),
            ("h4", "pos"),
            ("h5", "xxx"),
        ]

        level = 0
        chunklist_elem = cls.group_list(level, level_class_list, mw_grandchildren)
        return chunklist_elem

    @classmethod
    def group_list(cls, level, level_class_list, elems):
        if level >= len(level_class_list):
            return None
        logger.debug(f"level {level} {type(elems)}")
        level_class = level_class_list[level]
        h_level = level_class[0]
        clazz = level_class[1]
        chunklist_elem = ET.Element("div")
        chunklist_elem.attrib["class"] = f"{clazz}_{h_level}"
        logger.debug(chunklist_elem.attrib["class"])
        while len(elems) > 0:
            elem = elems.pop()
            headers = elem.xpath(h_level)
            if len(headers) > 0:
                chunklist_subelem = cls.group_list(level + 1, level_class_list, elems)
                if chunklist_subelem is not None:
                    chunklist_elem.append(copy.deepcopy(chunklist_subelem))
            else:
                chunklist_elem.append(copy.deepcopy(elem))
        logger.debug(f"chunklist_elem {type(chunklist_elem)}")
        return chunklist_elem

        """
        NOTE: variable structure. Sometimes PoS are under languag with Etymology siblings
        English
          Etymology
          Noun

        sometimes its language with Etymology 1, Etymology 2 children and Noun, etc as grandchildren


Contents
1	English
  1.1	Etymology
  1.2	Pronunciation
  1.3	Noun
    1.3.1	Usage notes
    1.3.2	Hyponyms
    1.3.3	Derived terms
    1.3.4	Descendants
    1.3.5	Translations
  1.4	Verb
  1.5	Further reading
  1.6	Anagrams
2	Basque
  2.1	Noun
3	Irish
  3.1	Pronunciation
  3.2	Etymology 1
    3.2.1	Noun
      3.2.1.1	Declension
      3.2.1.2	Derived terms
    3.2.2	Pronoun
    3.2.3	Further reading
  3.3	Etymology 2
    3.3.1	Verb
      3.3.1.1	Inflection
  3.4	Mutation
  3.5	References


        """

        """
<!DOCTYPE html>
<html>
  <head>
    <title></title>
  </head>
  <body>
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr">
        <div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading" data-nosnippet="">
          <input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none">
          <div class="toctitle" lang="en" dir="ltr">
            <h2 id="mw-toc-heading">
              Contents
            </h2>
          </div>
          <ul>
            <li class="toclevel-1 tocsection-1">
              <a href="#English"><span class="tocnumber">1</span> <span class="toctext">English</span></a>
              <ul>
                <li class="toclevel-2 tocsection-2">
                  <a href="#Alternative_forms"><span class="tocnumber">1.1</span> <span class="toctext">Alternative forms</span></a>
                </li>
                <li class="toclevel-2 tocsection-3">
                  <a href="#Etymology"><span class="tocnumber">1.2</span> <span class="toctext">Etymology</span></a>
                </li>
                <li class="toclevel-2 tocsection-4">
                  <a href="#Noun"><span class="tocnumber">1.3</span> <span class="toctext">Noun</span></a>
                  <ul>
                    <li class="toclevel-3 tocsection-5">
                      <a href="#Derived_terms"><span class="tocnumber">1.3.1</span> <span class="toctext">Derived terms</span></a>
                    </li>
                    <li class="toclevel-3 tocsection-6">
                      <a href="#Translations"><span class="tocnumber">1.3.2</span> <span class="toctext">Translations</span></a>
                    </li>
                  </ul>
                </li>
                <li class="toclevel-2 tocsection-7">
                  <a href="#Verb"><span class="tocnumber">1.4</span> <span class="toctext">Verb</span></a>
                </li>
                <li class="toclevel-2 tocsection-8">
                  <a href="#Further_reading"><span class="tocnumber">1.5</span> <span class="toctext">Further reading</span></a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <div class="mw-heading mw-heading2">
          <h2 id="English">
            English
          </h2><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=1" title="Edit section: English"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>
        <figure class="mw-default-size" typeof="mw:File/Thumb">
          <a href="/wiki/File:Initial_t_Paulus_Frank_1601.jpg" class="mw-file-description"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Initial_t_Paulus_Frank_1601.jpg/220px-Initial_t_Paulus_Frank_1601.jpg" decoding="async" width="220" height="308" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Initial_t_Paulus_Frank_1601.jpg/330px-Initial_t_Paulus_Frank_1601.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Initial_t_Paulus_Frank_1601.jpg/440px-Initial_t_Paulus_Frank_1601.jpg 2x" data-file-width="547" data-file-height="765"></a>
        </figure>

        <div class="mw-heading mw-heading3">
          <h3 id="Alternative_forms">
            Alternative forms
          </h3><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=2" title="Edit section: Alternative forms"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>

        <ul>
          <li>
            <span class="Latn" lang="en"><a href="/wiki/curlycue#English" title="curlycue">curlycue</a></span>
          </li>
        </ul>

        <div class="mw-heading mw-heading3">
          <h3 id="Etymology">
            Etymology
          </h3><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=3" title="Edit section: Etymology"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>

        <p>
          From <i class="Latn mention" lang="en"><a href="/wiki/curly#English" title="curly">curly</a></i> +‎ <i class="Latn mention" lang="en"><a href="/wiki/cue#English" title="cue">cue</a></i>.
        </p>

        <div class="mw-heading mw-heading3">
          <h3 id="Noun">
            Noun
          </h3><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=4" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>

        <p>
          <span class="headword-line"><strong class="Latn headword" lang="en">curlicue</strong> (<i>plural</i> <b class="Latn form-of lang-en p-form-of" lang="en"><a href="/wiki/curlicues#English" title="curlicues">curlicues</a></b>)</span>
        </p>
        <ol>
          <li>A fancy <a href="https://en.wiktionary.org/wiki/twist#English" title="twist">twisting</a> or <a href="https://en.wiktionary.org/wiki/curl#English" title="curl">curling</a> shape usually made from a series of <a href="https://en.wiktionary.org/wiki/spiral#English" title="spiral">spirals</a> and <a href="https://en.wiktionary.org/wiki/loop#English" title="loop">loops</a>. <span class="HQToggle" data-nosnippet="" style="margin-left: 5px;"><a role="button" tabindex="0">quotations&nbsp;▼</a></span>
            <ul style="display: none;">
              <li>
              <!-- citations removed-->
              </li>
            </ul>
          </li>
        </ol>

        <div class="mw-heading mw-heading4">
          <h4 id="Derived_terms">
            Derived terms
          </h4><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=5" title="Edit section: Derived terms"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>

        <ul>
          <li>
            <span class="Latn" lang="en"><a href="/wiki/curlicue_fractal#English" title="curlicue fractal">curlicue fractal</a></span>
          </li>
        </ul>

        <div class="mw-heading mw-heading4">
          <h4 id="Translations">
            Translations
          </h4><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=6" title="Edit section: Translations"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>
        <div class="NavFrame" id="Translations-fancy_curling_shape">
          <div class="NavHead" style="text-align:left;cursor:pointer">
            <span class="NavToggle" data-nosnippet=""><a role="button" tabindex="0">show ▼</a></span><a href="#" title="Edit table heading" style="padding: 2px; margin-left: -5px;">±</a>fancy curling shape
          </div>
          <div class="NavContent" style="display: none;">
            <div>
              <a style="font-size: 85%;">Select preferred languages</a>
            </div>
            <table class="translations" role="presentation" data-gloss="fancy curling shape" style="width:100%">
              <tbody>
                <tr>
                  <td class="translations-cell multicolumn-list" colspan="3" style="background-color:#ffffe0;vertical-align:top;text-align:left">
                    <ul>
                      <li>Bulgarian: <span class="Cyrl" lang="bg"><a href="/w/index.php?title=%D0%B7%D0%B0%D0%B2%D1%8A%D1%80%D1%82%D1%83%D0%BB%D0%BA%D0%B0&amp;action=edit&amp;redlink=1" class="new" title="завъртулка (page does not exist)">завъртулка</a></span><span class="tpos">&nbsp;<a href="https://bg.wiktionary.org/wiki/%D0%B7%D0%B0%D0%B2%D1%8A%D1%80%D1%82%D1%83%D0%BB%D0%BA%D0%B0" class="extiw" title="bg:завъртулка">(bg)</a></span>&nbsp;<span class="gender"><abbr title="feminine gender">f</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="bg-Latn" class="tr Latn">zavǎrtulka</span><span class="mention-gloss-paren annotation-paren">)</span>
                      </li>
                      <li>Finnish: <span class="Latn" lang="fi"><a href="/wiki/koukero#Finnish" title="koukero">koukero</a></span>
                      </li>
                      <li>German: <span class="Latn" lang="de"><a href="/wiki/Schn%C3%B6rkel#German" title="Schnörkel">Schnörkel</a></span><span class="tpos">&nbsp;<a href="https://de.wiktionary.org/wiki/Schn%C3%B6rkel" class="extiw" title="de:Schnörkel">(de)</a></span>&nbsp;<span class="gender"><abbr title="masculine gender">m</abbr></span>
                      </li>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td></td>
                  <td></td>
                  <td style="text-align: left;">
                    <ul>
                      <li>
                      <!-- form removed -->
                      </li>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="mw-heading mw-heading3">
          <h3 id="Verb">
            Verb
          </h3><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=7" title="Edit section: Verb"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>
        <p>
          <span class="headword-line"><strong class="Latn headword" lang="en">curlicue</strong> (<i>third-person singular simple present</i> <b class="Latn form-of lang-en s-verb-form-form-of" lang="en"><a href="/wiki/curlicues#English" title="curlicues">curlicues</a></b>, <i>present participle</i> <b class="Latn form-of lang-en ing-form-form-of" lang="en"><a href="/wiki/curlicuing#English" title="curlicuing">curlicuing</a></b>, <i>simple past and past participle</i> <b class="Latn form-of lang-en ed-form-form-of" lang="en"><a href="/wiki/curlicued#English" title="curlicued">curlicued</a></b>)</span>
        </p>
        <ol>
          <li>
            <span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content"><a href="/wiki/Appendix:Glossary#transitive" title="Appendix:Glossary">transitive</a> and <a href="/wiki/Appendix:Glossary#intransitive" title="Appendix:Glossary">intransitive</a></span><span class="ib-brac">)</span></span> To make or adorn (something) with curlicues, or as if with curlicues. <span class="HQToggle" data-nosnippet="" style="margin-left: 5px;"><a role="button" tabindex="0">quotations&nbsp;▼</a></span>
            <!-- ul citation removed -->
          </li>
        </ol>
        <div class="mw-heading mw-heading3">
          <h3 id="Further_reading">
            Further reading
          </h3><span class="mw-editsection" data-nosnippet=""><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=curlicue&amp;action=edit&amp;section=8" title="Edit section: Further reading"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span>
        </div>
        <ul>
          <li>
            <span typeof="mw:File"><a href="https://en.wikipedia.org/wiki/curlicue" title="w:curlicue"><img src="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/15px-Wikipedia-logo-v2.svg.png" decoding="async" width="15" height="14" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/23px-Wikipedia-logo-v2.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/30px-Wikipedia-logo-v2.svg.png 2x" data-file-width="103" data-file-height="94"></a></span> <b class="Latn" lang="en"><a href="https://en.wikipedia.org/wiki/curlicue" class="extiw" title="w:curlicue">curlicue</a></b> on Wikipedia.<span class="interProject"><a href="https://en.wikipedia.org/wiki/curlicue" class="extiw" title="w:curlicue">Wikipedia</a></span>
          </li>
        </ul>
      </div><!--esi <esi:include src="/esitest-fa8a495983347898/content" /> --><noscript><img src="https://login.wikimedia.org/wiki/Special:CentralAutoLogin/start?type=1x1" alt="" width="1" height="1" style="border: none; position: absolute;"></noscript>
      <div class="printfooter" data-nosnippet="">
        Retrieved from "<a dir="ltr" href="https://en.wiktionary.org/w/index.php?title=curlicue&amp;oldid=75896679">https://en.wiktionary.org/w/index.php?title=curlicue&amp;oldid=75896679</a>"
      </div>
    </div>
  </body>
</html>
        """

    @classmethod
    def create_toc_and_main_content(cls, language, part_of_speech, mw_content_text):

        """
        reads medi_wiki_content_text and extracts ToC , and pos+defintions
        Not finished. Safest to take the first definition which will be main English one
        Horribly messay and fragile
        :param language: language or list of languges 'English' and possibly others
        :param part_of_speech: partOfSpeech wanted or list of Partsofspeech
        :param mw_content_text: mediawiki content
        :return: element with POS and definition/s
        """
        if language is None:
            logger.warning("No language/s given")
            return (None, None)
        reqd_langs = language if type(language) is list else [language]
        if part_of_speech is None:
            logger.warning(f"No parts of speec given")
            return (None, None)
        pos_list = part_of_speech if type(part_of_speech) is list else [part_of_speech]
        if mw_content_text is None:
            logger.warning(f"no mw_content_text given")
            return (None, None)
        logger.info(f"lang: {reqd_langs} ppos: {pos_list}")

        """
        <li>
                <div class="citation-whole">
        """
        XmlLib.remove_all(mw_content_text, [
            ".//form",
            ".//input",
            "ul[li[div[@class='citation-whole']]]"
        ])
        toc_elems = mw_content_text.xpath(".//div[@id='toc']")
        if len(toc_elems) == 0:
            logger.info(f"no toc...")
            return (None, None)
        toc_elem = toc_elems[0]
        XmlLib.remove_all(toc_elem, [
            "./input",
            "./div/span[@class='toctogglespan']",
            "./div/h2[@id='mw-toc-heading']"
        ])

        # toclevel 1 is languages
        language_elems = toc_elem.xpath("./ul/li[contains(@class,'toclevel-1')]")
        # languages have prepended # at this stage
        languages = [elem.xpath("./a/@href")[0][1:] for elem in language_elems]
        possible_langs = set(reqd_langs).intersection(set(languages))
        if len(possible_langs) == 0:
            logger.warning(f"no required languages {reqd_langs} in {languages}")
            return (None, None)

        result_html = ET.Element("div")
        result_html.attrib["class"] = "wiktionary_result"

        logger.info(f"langs {languages}")
        # the ids for Nouns, Verbs, etc are Noun, Noun_2, Noun_3, etc.
        # I bet they change every revision . We have to get the ID from the TOC
        for pos in pos_list:
            cls.get_pos_meanings_and_definitions(mw_content_text, pos, result_html)

        return (toc_elem, result_html)

    @classmethod
    def get_pos_meanings_and_definitions(cls, mw_content_text, pos, result_html):

        pos_elem = ET.SubElement(result_html, "div")
        pos_elem.attrib["class"] = "parts_of_speech"
        pos_xpath = f".//div[*[starts-with(@id,'{pos}')]]"
        pos_divs = mw_content_text.xpath(pos_xpath)
        logger.debug(f"\n === {pos} === ")
        for pos_div in pos_divs:
            cls.add_word_variants_and_defintions(pos_div, pos_elem)
        return pos_elem

    @classmethod
    def add_word_variants_and_defintions(cls, pos_div, pos_elem):
        pos_div_elem = ET.SubElement(pos_elem, "div")
        pos_div_elem.attrib["class"] = "pos_div"
        cls.add_words_p_element(pos_div, pos_div_elem)
        cls.add_definition_li_elements(pos_div, pos_div_elem)

    @classmethod
    def add_definition_li_elements(cls, pos_div, pos_div_elem):
        following_ol = pos_div.xpath("./following-sibling::ol")[0]
        ol_lis = following_ol.xpath("li")
        ol = ET.SubElement(pos_div_elem, "ol")
        for li in ol_lis:
            text = cls.extract_main_text_from_definition(li).strip()
            if text:
                li_new = ET.SubElement(ol, "li")
                li_new.text = text
                logger.info(f"def: {li_new.text}")

    @classmethod
    def add_words_p_element(cls, pos_div, pos_div_elem):
        language_elem_div = pos_div.xpath("./preceding-sibling::div[h2][1]")[0]
        lang = language_elem_div.xpath("./h2")[0].text
        logger.debug(f"LANG {lang}")
        following_p = pos_div.xpath("./following-sibling::p")[0]
        words_elem = ET.SubElement(pos_div_elem, "p")
        words_elem.text = following_p.xpath("./span/strong/text()")[0]
        logger.debug(f"variant: {words_elem.text}")

    @classmethod
    def extract_main_text_from_definition(cls, li):
        XmlLib.remove_all(li, ".//dl")
        # ul><li><div class="citation-whole"
        # remove citations
        XmlLib.remove_all(li, ".//ul[li[div[@class='citation-whole']]]")
        # concatenate text (removes some bold and italis but we can work on that later
        text = "".join(li.itertext()).strip()
        return text

    @classmethod
    def search_terms_create_html(cls, term, language="English", part_of_speech="Noun", add_toc=False):
        """
        search for terms and create Wiktionary-based HTML
        :param terms: single term or list
        :param language: str/list. defaults to ENGLISH
        :param part_of_speech: str/list defaults to NOUN
        :param add_toc: add Wiktionary ToC, default False
        :return: HTML object
        """
        htmlx = HtmlUtil.create_skeleton_html()
        body = HtmlLib.get_body(htmlx)
        if term is None:
            logger.warning(F"cannot search for None")
            return None
        terms = term if type(term) is list else [term]

        for termx in terms:
            cls.create_and_add_html_for_term(termx, htmlx, language, part_of_speech, add_toc)
        return htmlx

    @classmethod
    def create_and_add_html_for_term(cls, termx, htmlx, language="English", part_of_speech="Noun", add_toc=False):
        """
        create html object for term
        :param termx: term to lookup
        :param htmlx: existing html object
        :param language: str/list default "English"
        :param part_of_speech: str/list default "Noun"
        :param add_toc: adds ToC, default False
        :return: body
        """
        html_element, mw_content_text = WiktionaryPage.lookup_wiktionary_content(termx)
        (toc_elem, content_elem) = WiktionaryPage.create_toc_and_main_content(language, part_of_speech, mw_content_text)
        if content_elem is None:
            return None
        body = HtmlLib.get_body(htmlx) if htmlx is not None else ET.Element("body")
        div = ET.SubElement(body, "div")
        if add_toc:
            div.append(toc_elem)
        div.append(content_elem)
        return body

    @classmethod
    def validate_mw_content(cls, mw_content_text, term, outdir=None, nchild=3):
        """
        search for term, return mw-content-text and validate it
        :param term: term to search for
        :param outdir: output dir for HTML (generally a temporary dir)
        :param nchild: number of children of mw-content-text (assumed 3)
        """
        assert term is not None, f"must give term"
        assert mw_content_text is not None
        # tostring = etree.tostring(mw_content_text, pretty_print=True)
        if outdir is not None:
            # filename = str(Path(outdir, f"{term}.html"))
            # with open(filename, "w") as f:
            #     f.write(tostring.decode())
            # logger.debug(f"wrote html to {filename}")
            children_xpath = "*"
            mw_content_text_children = mw_content_text.xpath(children_xpath)
            assert len(mw_content_text_children) == nchild, f"mw_content_text should have 3 children"
            mw_content_ltr = mw_content_text_children[0]
            assert mw_content_ltr.tag == DIV and "mw-content-ltr" in mw_content_ltr.attrib.get(
                CLASS), f"first child should ne main content"
            noscript = mw_content_text_children[1]
            printfooter = mw_content_text_children[2]
            assert noscript.tag == NOSCRIPT, f"{term}: second child should be <noscript>"
            assert printfooter.tag == DIV and printfooter.attrib.get(CLASS) == PRINTFOOTER, \
                f"third child should be Div[@class=printfooter]"

    @classmethod
    def get_term_from_html_element(cls, html_element):
        """
        gets term from main title
        :param html_element: from Wiktionary search
        :return: term text or None
        """
        if html_element is None:
            return None
        spans = html_element.xpath(".//span[@class='mw-page-title-main']")
        return spans[0].text if len(spans) > 0 else None


# class WikipediaInfoBox:
#     """
#     wrapper for wikipedia infobox HTML <table>
#     """
#
#     def __init__(self, table=None):
#         """
#         Wrapper for Wikipedia InfoBox
#         """
#         self.table = table

# class WikipediaBasicInfo:
#     """
#     wrapper for wikipedia basic information tabls
#     """
#
#     """
#     Display title	MV Arctic Sea
#     Default sort key	Arctic Sea, Mv
#     Page length (in bytes)	40,084
#     Namespace ID	0
#     Page ID	23947896
#     Page content language	en - English
#     Page content model	wikitext
#     Indexing by robots	Allowed
#     Number of page watchers	91
#     Number of page watchers who visited in the last 30 days	2
#     Number of redirects to this page	4
#     Counted as a content page	Yes
#     Wikidata item ID	Q615783
#     Local description	Ship
#     Central description	ship built in 1992
#     Page image	MV Arctic sea.svg
#     Page views in the past 30 days	273
#     """
#     DISPLAY_TITLE = "Display title"
#     SORT_KEY = "Default sort key"
#     PAGE_LENGTH = "Page length (in bytes)"
#     NAMESPACE_ID = "Namespace ID"
#     PAGE_ID = "Page ID"
#     PAGE_LANGAUGE = "Page content language"
#     CONTENT_MODEL = "Page content model"
#     INDEXING_BY_ROBOTS = "Indexing by robots"
#     PAGE_WATCHERS = "Number of page watchers"
#     PAGE_WATCHERS_30 = "Number of page watchers who visited in the last 30 days"
#     REDIRECTS = "Number of redirects to this page"
#     IS_CONTENT_PAGE = "Counted as a content page"
#     WIKIDATA_ITEM = "Wikidata item ID"
#     LOCAL_DESCRIPTION = "Local description"
#     CENTRAL_DESCRIPTION = "Central description"
#     PAGE_IMAGE = "Page image"
#     PAGE_VIEWS_30 = "Page views in the past 30 days"
#
#     KEYS = [
#         DISPLAY_TITLE,
#         SORT_KEY,
#         PAGE_LENGTH,
#         NAMESPACE_ID,
#         PAGE_ID,
#         PAGE_LANGAUGE,
#         CONTENT_MODEL,
#         INDEXING_BY_ROBOTS,
#         PAGE_WATCHERS,
#         PAGE_WATCHERS_30,
#         REDIRECTS,
#         IS_CONTENT_PAGE,
#         WIKIDATA_ITEM,
#         LOCAL_DESCRIPTION,
#         CENTRAL_DESCRIPTION,
#         PAGE_IMAGE,
#         PAGE_VIEWS_30,
#     ]
#
#     def __init__(self, table=None):
#         """
#         Wrapper for Wikipedia basic information
#         """
#         self.table = table
#         self.table_dict = dict()
#         self.create_table_dict()
#
#     def get_wikidata_href_id(self):
#         """
#         return wikidate href and id (Note
#         :return: (href, id) tuplpe or None
#         """
#         value = self.get_value_for_key(self.WIKIDATA_ITEM)
#         id = value.split("/")[-1]
#         return None if value is None else (value, id)
#
#     def get_local_description(self):
#         key = self.LOCAL_DESCRIPTION
#         return self.get_value_for_key(key)
#
#     def get_value_for_key(self, key):
#         return self.table_dict[key]
#
#     def get_image_url(self):
#         url_tail = self.get_value_for_key(self.PAGE_IMAGE)
#         url = f"{WikipediaPage.get_default_wikipedia_url()}{url_tail}"
#         return url
#
#     def create_table_dict(self):
#         """
#         creates name-value table, where value can be text or XML element
#         """
#         self.table_dict = dict()
#         rows = self.table.xpath(".//tr")
#         for row in rows:
#             name = self.get_cell_value(row.xpath("./td[1]")[0], 0)
#             if not name in self.KEYS:
#                 logger.warning(f"unknown key {name} in Basic Information")
#             value = self.get_cell_value(row.xpath("./td[2]")[0], 1)
#             self.table_dict[name] = value
#
#     def get_cell_value(self, td, idx):
#         """
#         HYPERLINK
#         <td>
#           <a
#             class="extiw wb-entity-link external"
#             href="https://www.wikidata.org/wiki/Special:EntityPage/Q615783"
#             >Q615783</a>
#         </td>
#         """
#         tda = td.xpath("a")  # might be a hyperlink
#         if len(tda) > 0:
#             href = tda[0].attrib.get("href")
#             aval = tda[0].text
#             href = aval if idx == 0 else href
#             return href
#         """
#         IMAGE
#         <td>
#           <a href="/wiki/File:MV_Arctic_sea.svg" class="mw-file-description">
#             <img
#               alt="MV Arctic sea.svg"
#               src="//upload.wikimedia.org/wikipedia/commons/thumb/7/7f/MV_Arctic_sea.svg/220px-MV_Arctic_sea.svg.png"
#               decoding="async"
#               width="220"
#               height="156"
#               data-file-width="1052"
#               data-file-height="744"
#               ></a></td>"""
#         return td.text


class WikipediaBasicInfo:
    """
    wrapper for wikipedia basic information tabls
    """

    """
    Display title	MV Arctic Sea
    Default sort key	Arctic Sea, Mv
    Page length (in bytes)	40,084
    Namespace ID	0
    Page ID	23947896
    Page content language	en - English
    Page content model	wikitext
    Indexing by robots	Allowed
    Number of page watchers	91
    Number of page watchers who visited in the last 30 days	2
    Number of redirects to this page	4
    Counted as a content page	Yes
    Wikidata item ID	Q615783
    Local description	Ship
    Central description	ship built in 1992
    Page image	MV Arctic sea.svg
    Page views in the past 30 days	273
    """
    DISPLAY_TITLE = "Display title"
    SORT_KEY = "Default sort key"
    PAGE_LENGTH = "Page length (in bytes)"
    NAMESPACE_ID = "Namespace ID"
    PAGE_ID = "Page ID"
    PAGE_LANGAUGE = "Page content language"
    CONTENT_MODEL = "Page content model"
    INDEXING_BY_ROBOTS = "Indexing by robots"
    PAGE_WATCHERS = "Number of page watchers"
    PAGE_WATCHERS_30 = "Number of page watchers who visited in the last 30 days"
    REDIRECTS = "Number of redirects to this page"
    IS_CONTENT_PAGE = "Counted as a content page"
    WIKIDATA_ITEM = "Wikidata item ID"
    LOCAL_DESCRIPTION = "Local description"
    CENTRAL_DESCRIPTION = "Central description"
    PAGE_IMAGE = "Page image"
    PAGE_VIEWS_30 = "Page views in the past 30 days"

    KEYS = [
        DISPLAY_TITLE,
        SORT_KEY,
        PAGE_LENGTH,
        NAMESPACE_ID,
        PAGE_ID,
        PAGE_LANGAUGE,
        CONTENT_MODEL,
        INDEXING_BY_ROBOTS,
        PAGE_WATCHERS,
        PAGE_WATCHERS_30,
        REDIRECTS,
        IS_CONTENT_PAGE,
        WIKIDATA_ITEM,
        LOCAL_DESCRIPTION,
        CENTRAL_DESCRIPTION,
        PAGE_IMAGE,
        PAGE_VIEWS_30,
    ]

    def __init__(self, table=None):
        """
        Wrapper for Wikipedia basic information
        """
        self.table = table
        self.table_dict = dict()
        self.create_table_dict()

    def get_wikidata_href_id(self):
        """
        return wikidate href and id (Note
        :return: (href, id) tuplpe or None
        """
        value = self.get_value_for_key(self.WIKIDATA_ITEM)
        id = value.split("/")[-1]
        return None if value is None else (value, id)

    def get_local_description(self):
        key = self.LOCAL_DESCRIPTION
        return self.get_value_for_key(key)

    def get_value_for_key(self, key):
        return self.table_dict[key]

    def get_image_url(self):
        url_tail = self.get_value_for_key(self.PAGE_IMAGE)
        url = f"{WikipediaPage.get_default_wikipedia_url()}{url_tail}"
        return url

    def create_table_dict(self):
        """
        creates name-value table, where value can be text or XML element
        """
        self.table_dict = dict()
        rows = self.table.xpath(".//tr")
        for row in rows:
            name = self.get_cell_value(row.xpath("./td[1]")[0], 0)
            if not name in self.KEYS:
                logger.warning(f"unknown key {name} in Basic Information")
            value = self.get_cell_value(row.xpath("./td[2]")[0], 1)
            self.table_dict[name] = value

    def get_cell_value(self, td, idx):
        """
        HYPERLINK
        <td>
          <a
            class="extiw wb-entity-link external"
            href="https://www.wikidata.org/wiki/Special:EntityPage/Q615783"
            >Q615783</a>
        </td>
        """
        tda = td.xpath("a")  # might be a hyperlink
        if len(tda) > 0:
            href = tda[0].attrib.get("href")
            aval = tda[0].text
            href = aval if idx == 0 else href
            return href
        """
        IMAGE
        <td>
          <a href="/wiki/File:MV_Arctic_sea.svg" class="mw-file-description">
            <img 
              alt="MV Arctic sea.svg" 
              src="//upload.wikimedia.org/wikipedia/commons/thumb/7/7f/MV_Arctic_sea.svg/220px-MV_Arctic_sea.svg.png" 
              decoding="async" 
              width="220" 
              height="156" 
              data-file-width="1052"
              data-file-height="744"
              ></a></td>"""
        return td.text
