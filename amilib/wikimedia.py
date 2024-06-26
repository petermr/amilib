import datetime
import json
import logging
import os
import re
import sys
from copy import copy
from enum import Enum
from pathlib import Path

import requests
from lxml import etree as ET
from lxml import etree, html
import lxml.etree
from urllib.parse import quote
from io import StringIO
from urllib.request import urlopen
from lxml import etree
from urllib.error import HTTPError, URLError
from SPARQLWrapper import SPARQLWrapper

# local
from amilib.ami_html import HtmlUtil
from amilib.util import Util
from amilib.xml_lib import HtmlLib, XmlLib

logging.debug("loading wikimedia.py")

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

BODY = "body"
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
        # print(f"url {url}")
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
                print(f"no wikidata hits for {term}")

                # TODO fix non-tuples
        if hit0 is None:
            return None, None, None
        else:

            hit0_id = hit0[0]
            hit0_description = hit0[1]["desc"]
            if hit0_description == None:
                print(f"NULL DESCRIPTION in WD {hit0[1]}")
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
                print(f"no result_heading_a_elem in {lxml.etree.tostring(li)}")
                continue
            if not result_heading_a_elem.attrib.get(HREF):
                print(f"no href in {result_heading_a_elem}")
                continue
            qitem = result_heading_a_elem.attrib[HREF].split("/")[-1]
            if qitem in wikidata_dict:
                print(f"duplicate wikidata entry {qitem}")
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
        print(f"------{name}-------")
        if not entry_hits[0]:
            #                print(f" no hit for {name}")
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
            print(f"no file {file}")
            return None
        filter = WikidataFilter()
        print(f"file.. {file}")
        with open(file, "r") as f:
            text = f.read()
        filter.json = json.loads(text)
        print(f"dict {type(filter.json)} {filter.json}")
        return filter


class WikidataProperty:

    def __init__(self):
        self.element = None

    def __str__(self):
        s = "WikidataProperty: "
        if self.element is not None:
            print(f"type self.element {type(self.element)}")
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
                    # print(f"statement {id} {value}")
                else:
                    # print(f"value: {value}")
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
        #     print(ahref.attrib["href"])

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
        # print(f"{xpath}")
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
            print(f"no root for wikidata")
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
        print("sparql path", sparql_file)
        self.current_sparql = ET.parse(sparql_file, parser=ET.XMLParser(encoding="utf-8"))
        self.sparql_result_list = list(self.current_sparql.findall(SPQ_RESULTS + "/" + SPQ_RESULT, NS_MAP))
        assert (len(self.sparql_result_list) > 0)
        print("results", len(self.sparql_result_list))

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

        print("sparql result by id", len(self.sparql_result_by_wikidata_id))
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

    #        print(">>", ET.tostring(entry))

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
            print(f"cannout open {url} because {e}")
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
    from requests import request
    WIKIPEDIA_PHP = "https://en.wikipedia.org/w/index.php?"

    def __init__(self):
        self.html_elem = None

    @classmethod
    def lookup_wikipedia_page(cls, search_term):
        """
        :param search_term: term/phrase to search with
        :return: new WikipediaPage or None
        """

        "https://en.wikipedia.org/w/index.php?search=lulucx&title=Special%3ASearch&ns0=1"
        url = f"{WikipediaPage.WIKIPEDIA_PHP}search={search_term}"
        if url is None:
            return None
        try:
            response = requests.get(url)
            decode = response.content.decode("UTF-8")
            html_content = HtmlLib.parse_html_string(decode)
            wikipedia_page = WikipediaPage()
            wikipedia_page.html_elem = html_content
        except Exception as e:
            print(f"HTML exception {e}")
            return None

        return wikipedia_page

    def get_main_element(self):
        """gets main content from Wikipedia page
        also cleans some non-content elements incl buttons, navs, etc.
        """
        try:
            main_contents = self.html_elem.xpath(".//main")
            main_content = main_contents[0]
        except Exception as e:
            print(f"except {e}")
            return None
        XmlLib.remove_elements(main_content, xpath="//nav")
        XmlLib.remove_elements(main_content, xpath="//noscript")
        # XmlLib.remove_elements(main_content, xpath="//style")
        XmlLib.remove_elements(main_content, xpath="//div[@id='p-lang-btn']")
        return main_content

    def get_leading_para(self):
        """get first paragraph in main content (usually with definitions in lead sentence
        """
        main_elem = self.get_main_element()
        ps = main_elem.xpath(".//p")
        for p in ps:
            text = XmlLib.get_text(p).strip()
            if len(text) > 20:
                return p
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
                print(f"\nword: {word}")
            first_p = WikipediaPage.get_leading_paragraph_for_word(new_body, word)
            WikipediaPage.get_tuple_for_first_paragraph(first_p, debug=debug)
            div = ET.SubElement(new_body, "div")
            div.append(first_p)
        if outfile:
            XmlLib.write_xml(new_body, outfile, debug=debug)
        return html_out

    @classmethod
    def get_leading_paragraph_for_word(cls, new_body, word):

        wikipedia_page = WikipediaPage.lookup_wikipedia_page(word)
        if wikipedia_page is not None:
            wiki_main = wikipedia_page.get_main_element()
            first_p = wikipedia_page.get_leading_para()
            wikidata_href = wikipedia_page.get_wikidata_item()
        else:
            first_p = ET.Element("p")
            first_p.text = "Could not find first para"

        return first_p

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
        sentence =None
        term = None
        abbrev = None

        # para = self.get_leading_para()
        rex = re.compile("(.*\\.)\\s+\\.*")
        if para is None:
            return None
        # find first full stop in normal text (not bold)
        texts = para.xpath("./text()")
        for text in texts:
            # print(f"text> {text}")
            pass

        bolds = para.xpath("./b")
        for bold in bolds:
            # print(f"bold> {bold.text}")
            pass

        # split first sentence
        for tb in para.xpath("./text()|*"):
            if debug:
                try:
                    print(f"<{tb.tag}>{HtmlUtil.get_text_content(tb)}</{tb.tag}>")
                except Exception as e:
                    print(f"{tb}")
        for text in para.xpath("./text()|./b/text()"):
            if debug:
                print(f"t> {text}")

            match = rex.match(text)
            if match:
                if debug:
                    print(f">> {match.group(1)}")

        return (para, term, sentence, abbrev)
