"""manages bibligraphy and related stuff"""
import datetime
import json
from enum import Enum
from typing import List

import lxml.etree as ET
import re

from lxml.etree import _Element

from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.ami_util import AmiUtil, AmiJson
# local
from amilib.util import Util
from amilib.xml_lib import XmlLib

logger = Util.get_logger(__name__)


class Reference:
    SINGLE_REF_REC = re.compile(r"""
                    (?P<pre>.*)   # leading string without bracket
                    \(            # bracket
                    (?P<body>
                    (?:[A-Z]|de|d')
                    .*(?:20|19)\d\d[a-z,]*  # body starts uppcase and ends with date (without brackets)
                    )
                    \)            # trailing bracket
                    (?P<post>.*)  # trailing string without bracket
                    """, re.VERBOSE)
    DOI_REC = re.compile(r".*\s(doi:[^\s]*)\.")  # finds DOI string in running text

    AUTHORS_DATE_REC = re.compile(r"""
    (?P<first>((de )|(d')|(el ))?\s*[A-Z][^\s]+) # doesn't seem to do the prefixes yet
    (?P<others>.+)
    (?P<date>20\d\d[a-z]*)
    """, re.VERBOSE)

    DOI_PROTOCOL = "doi:"
    HTTPS_DOI_ORG = "https://doi.org/"

    def __init__(self):
        self.spans = []

    @classmethod
    def create_ref_from_div(cls, div):
        """create from div which contains one or more spans
        """
        if div is None:
            return None
        ref = Reference()
        ref.div = div
        ref.spans = div.xpath("./span")
        return ref

    def markup_dois_in_spans(self):
        """iterates over contained spans until the doi-containing one is found
        """
        for span in self.spans:
            text = span.text
            doi_match = self.DOI_REC.match(text)
            if doi_match:
                doi_txt = doi_match.group(1)
                if self.DOI_PROTOCOL in doi_txt:
                    doi_txt = doi_txt.replace("doi:https", "https")
                    doi_txt = doi_txt.replace(self.DOI_PROTOCOL, self.HTTPS_DOI_ORG)
                    if doi_txt.startswith(self.DOI_PROTOCOL):
                        doi_txt = "https://" + doi_txt
                    logger.debug(f"doi: {doi_txt}")
                    a = ET.SubElement(span.getparent(), "a")  # to avoid circulkar import of H_A TODO

                    a.attrib["href"] = doi_txt
                    a.text = doi_txt
                    break
            else:
                # logger.debug(f"no doi: {text}")
                pass

    @classmethod
    def markup_dois_in_div_spans(cls, ref_divs):
        """creates refs and then marks up the spans
        May be rather specific to IPCC"""
        for div in ref_divs:
            ref = Reference.create_ref_from_div(div)
            spans = div.xpath("./span")
            ref.markup_dois_in_spans()


class Biblioref:
    """in-text pointer to References
    of form:
    Lave 1991
    Lecocq and Shalizi 2014
    Gattuso  et  al.  2018;  Bindoff  et  al.  2019
    IPBES 2019b

    IPCC  2018b:  5.3.1    # fist part only
    """

    def __init__(self):
        self.str = None
        self.first = None
        self.others = None
        self.date = None

    def __str__(self):
        s = f"{self.str} => {self.first}|{self.others}|{self.date}"
        return s

    @classmethod
    def create_refs_from_biblioref_string(cls, brefstr):
        """create from in-text string without the brackets
        :param brefstr: string may contain repeated values
        :return: list of Bibliorefs (may be empty or have one member

        """
        bibliorefs = []
        if brefstr:
            bref = " ".join(brefstr.splitlines()).replace(r"\s+", " ")
            chunks = bref.split(";")
            for chunk in chunks:
                # logger.debug(f" chunk {chunk}")
                brefx = Biblioref.create_bref(chunk.strip())
                if brefx:
                    bibliorefs.append(brefx)
        return bibliorefs

    @classmethod
    def create_bref(cls, brefstr):
        """create Biblioref from single string
        :param brefstr: of form 'Author/s date' """

        bref = None
        match = Reference.AUTHORS_DATE_REC.match(brefstr)
        if match:
            bref = Biblioref()
            bref.str = brefstr
            bref.first = match.group("first")
            bref.others = match.group("others")
            bref.date = match.group("date")
        return bref

    @classmethod
    def make_bibliorefs(cls, file):
        chap_elem = ET.parse(str(file))
        div_spans = chap_elem.xpath(".//div[span]")
        total_bibliorefs = []
        rec = re.compile(Util.SINGLE_BRACKET_RE)
        for div in div_spans:
            for span in div.xpath("./span"):
                match = rec.match(span.text)
                if match:
                    body = match.group('body')
                    bibliorefs = Biblioref.create_refs_from_biblioref_string(body)
                    for biblioref in bibliorefs:
                        total_bibliorefs.append(biblioref)
        return total_bibliorefs


# EPMC keys

ABS_TEXT = 'abstractText'
PMCID = 'pmcid'
UNNAMED_0 = 'Unnamed: 0'
ID = 'id'
SOURCE = 'source'
PMID = 'pmid'
FULLTEXT_IDLIST = 'fullTextIdList'
DOI = 'doi'
TITLE = 'title'
AUTHOR_STRING = 'authorString'
AUTHOR_LIST = 'authorList'
AUTHOR_IDLIST = 'authorIdList'
DATALINKS_TAGSLIST = 'dataLinksTagsList'
JOURNAL_INFO = 'journalInfo'
PUB_YEAR = 'pubYear'
PAGE_INFO = 'pageInfo'
AFFILIATION = 'affiliation'
PUBLICATION_STATUS = 'publicationStatus'
LANGUAGE = 'language'
PUBMODEL = 'pubModel'
PUBTYPE_LIST = 'pubTypeList'
KEYWORD_LIST = 'keywordList'
FULLTEXT_URLLIST = 'fullTextUrlList'
IS_OPENACCESS = 'isOpenAccess'
IN_EPMC = 'inEPMC'
IN_PMC = 'inPMC'
HAS_PDF = 'hasPDF'
HAS_BOOK = 'hasBook'
HAS_SUPPL = 'hasSuppl'
CITEDBY_COUNT = 'citedByCount'
HAS_DATA = 'hasData'
HAS_REFERENCES = 'hasReferences'
HAS_TEXTMINED_TERMS = 'hasTextMinedTerms'
HAS_DBCROSSREFERENCES = 'hasDbCrossReferences'
HAS_LABLINKS = 'hasLabsLinks'
LICENSE = 'license'
HAS_EVALUATIONS = 'hasEvaluations'
AUTH_MAN = 'authMan'
EPMC_AUTH_MAN = 'epmcAuthMan'
NIH_AUTH_MAN = 'nihAuthMan'
HAS_TMACCESSION_NUMBERS = 'hasTMAccessionNumbers'
TMACCESSION_TYPELIST = 'tmAccessionTypeList'
DATE_O_CREATION = 'dateOfCreation'
FIRST_INDEX_DATE = 'firstIndexDate'
FULLTEXT_RECEIVED_DATE = 'fullTextReceivedDate'
DATE_OF_REVISION = 'dateOfRevision'
ELECTRONIC_PUBLICATION_DATE = 'electronicPublicationDate'
FIRST_PUBLICATION_DATE = 'firstPublicationDate'
GRANTS_LIST = 'grantsList'
COMMENT_CORRECTION_LIST = 'commentCorrectionList'
MESH_HEADING_LIST = 'meshHeadingList'
SUBSET_LIST = 'subsetList'
DATE_OF_COMPLETION = 'dateOfCompletion'
CHEMICAL_LIST = 'chemicalList'
INVESTIGATOR_LIST = 'investigatorList'
EMBARGO_DATE = 'embargoDate'
MANUSCRIPT_ID = 'manuscriptId'
EPMC_KEYS = [
    UNNAMED_0, ID, SOURCE, PMID, PMCID, FULLTEXT_IDLIST, DOI,
    TITLE, AUTHOR_STRING, AUTHOR_LIST, AUTHOR_IDLIST,
    DATALINKS_TAGSLIST, JOURNAL_INFO, PUB_YEAR, PAGE_INFO,
    ABS_TEXT, AFFILIATION, PUBLICATION_STATUS, LANGUAGE,
    PUBMODEL, PUBTYPE_LIST, KEYWORD_LIST, FULLTEXT_URLLIST,
    IS_OPENACCESS, IN_EPMC, IN_PMC, HAS_PDF, HAS_BOOK, HAS_SUPPL,
    CITEDBY_COUNT, HAS_DATA, HAS_REFERENCES, HAS_TEXTMINED_TERMS,
    HAS_DBCROSSREFERENCES, HAS_LABLINKS, LICENSE, HAS_EVALUATIONS,
    AUTH_MAN, EPMC_AUTH_MAN, NIH_AUTH_MAN, HAS_TMACCESSION_NUMBERS,
    TMACCESSION_TYPELIST, DATE_O_CREATION, FIRST_INDEX_DATE,
    FULLTEXT_RECEIVED_DATE, DATE_OF_REVISION, ELECTRONIC_PUBLICATION_DATE,
    FIRST_PUBLICATION_DATE, GRANTS_LIST, COMMENT_CORRECTION_LIST,
    MESH_HEADING_LIST, SUBSET_LIST, DATE_OF_COMPLETION, CHEMICAL_LIST,
    INVESTIGATOR_LIST, EMBARGO_DATE, MANUSCRIPT_ID]

EUPMC_RESULTS_JSON = "eupmc_results.json"

EUPMC_TRANSFORM = {
    "doi": {
        "url": {
            "prefix": "https://www.doi.org/",
        }
    },
    "authorString": {
        "text": {
            "split": ",",
        }
    },
    "abstractText": {
        "text": {
            "truncate": 200,
        }
    },
    "pmcid": {
        "url": {
            "prefix": "https://europepmc.org/betaSearch?query=",
        }
    }
}

OPENALEX_TRANSFORM = {
    "doi": {
        "url": {
            "prefix": "https://www.doi.org/",
        }
    },
    "authorString": {
        "text": {
            "split": ",",
        }
    },
    "abstractText": {
        "text": {
            "truncate": 200,
        }
    }
}


class ApiEnum(Enum):
    EPMC = 1,
    OPENALEX = 2

class Pygetpapers:


    @classmethod
    def get_saved_section(cls, inpath):
        """
        gets saved section from saved_config.ini
        :param inpath: saved_config.ini
        :return: saved_section and section_names (probably only [SAVED]
        """
        config, section_names = AmiUtil.get_config_and_section_names(inpath)
        saved_section = config[SAVED]
        return saved_section, section_names

    @classmethod
    def read_metadata_json_create_write_html_table(
            cls, infile, outfile_h, wanted_keys, api=ApiEnum.EPMC,
            styles=None, datatables=None, table_id=None, config_ini=None):
        """
        read pygetpapers output, select columns and create HTML table
        :param infile: eumpc_results from pygetpapers
        :param outfile_h: HTML table to write
        :param wanted_keys: column headings to select
        :param styles: datatables styles
        :param datatables: datatables
        :param table_id: id links script to table (default "my_table")
        :param config_ini: adds info from saved_config.ini - mainly the query
        :return: html table
        """
        if styles is None:
            styles = ["td {border:solid 1px black;}"]
        if table_id is None:
            table_id = "my_table"

        assert infile.exists(), f"infile {infile} must exist"
        with open(infile, "r") as f:
            jsonx = json.load(f)
        # look for all papers
        papers = jsonx.get("papers")
        assert papers is not None, f"cannot find papers"
        # specific keys we want
        # put these in
        if api == ApiEnum.EPMC:
            transform_dict = EUPMC_TRANSFORM
        elif api == ApiEnum.OPENALEX:
            transform_dict = OPENALEX_TRANSFORM

        dict_by_id = AmiJson.create_json_table(papers, wanted_keys)
        htmlx, table = HtmlLib.create_html_table(
            dict_by_id, transform_dict=transform_dict,
            styles=styles, datatables=datatables, table_id=table_id
        )
        Pygetpapers.add_query_as_caption(config_ini, table)

        HtmlUtil.write_html_elem(htmlx, outfile_h, debug=True)

    @classmethod
    def add_query_as_caption(cls, config_ini, table):
        """
        add query string from config.ini to table caption
        :param config_ini: saved_config.ini file
        :param table: to add caption to
        """
        if config_ini is not None:
            config, _ = AmiUtil.get_config_and_section_names(config_ini)
            saved_section = config[SAVED]
            query = saved_section[QUERY]
            startdate = saved_section[STARTDATE]
            if startdate == 'False':
                startdate = "..."
            enddate = saved_section[ENDDATE]
            if enddate == 'False':
                enddate = datetime.date.today()

            caption = ET.SubElement(table, "caption")
            caption.text = f"query: {query}"
            if startdate:
                caption.text += f"; start: {startdate}"
            if enddate:
                caption.text += f"; end: {enddate}"


class Publication:
    CHAPTER = "Chapter"
    TECHNICAL_SUMMARY = "Technical Summary"

    @classmethod
    def is_chapter_or_tech_summary(cls, span_text):
        return span_text.startswith(Publication.CHAPTER) or span_text.startswith(Publication.TECHNICAL_SUMMARY)


# EPMC_PYGETPAPERS
SAVED_CONFIG_INI = "saved_config.ini"
EUPMC_RESULTS_JSON = "eupmc_results.json"

# from saved_config.ini
SAVED = "SAVED"

API = 'api'
CITATIONS = 'citations'
CONFIG = 'config'
ENDDATE = 'enddate'
FILTER = 'filter'
LIMIT = 'limit'
LOGFILE = 'logfile'
LOGLEVEL = 'loglevel'
MAKECSV = 'makecsv'
MAKEHTML = 'makehtml'
NOEXECUTE = 'noexecute'
NOTTERMS = 'notterms'
ONLYQUERY = 'onlyquery'
OUTPUT = 'output'
PDF = 'pdf'
QUERY = "query"
REFERENCES = 'references'
RESTART = 'restart'
SAVEQUERY = 'save_query'
STARTDATE = 'startdate'
SUPP = 'supp'
SYNONYM = 'synonym'
TERMS = 'terms'
UPDATE = 'update'
VERSION = 'version'
XML = 'xml'
ZIP = 'zip'
SECTION_KEYS = {
    API,
    CITATIONS,
    CONFIG,
    ENDDATE,
    FILTER,
    LIMIT,
    LOGFILE,
    LOGLEVEL,
    MAKECSV,
    MAKEHTML,
    NOEXECUTE,
    NOTTERMS,
    ONLYQUERY,
    OUTPUT,
    PDF,
    QUERY,
    REFERENCES,
    RESTART,
    SAVEQUERY,
    STARTDATE,
    SUPP,
    SYNONYM,
    TERMS,
    UPDATE,
    VERSION,
    XML,
    ZIP,
}
JOURNAL_INFO_TITLE = "journalInfo.journal.title"


class JATSSection:
    """
    a section in JATS file.
    Often child of <body> or <back>
    may have an ID and/or sec-type
    <sec sec-type = 'introduction' ...>
    """


class JATSDoc:
    """holds data for JATS file (possibly including parsed XML
    """

    ARTICLE = "article"
    BACK = "back"
    BODY = "body"
    FRONT = "front"
    SEC = 'sec'
    SEC_TYPE = 'sec-type'

    def __init__(self, xml):
        self.xml = xml
        self.article = self.get_article()
        self.front = self.get_front()
        self.body = self.get_body()
        self.back = self.get_back()
        self.body_secs, self.body_non_secs = None, None
        self.body_secs, self.body_non_secs = self.get_body_secs_non_secs()

    def get_article_component(self, jats_doc_component):
        self.get_article()
        if self.article is None:
            logger.warn(f"no self.article")
        component = XmlLib.get_single_element(
            element=self.article, xpath=f"./*[local-name()='{jats_doc_component}']")
        return component

    def get_article(self):
        """
        get <article> which must be root element
        """
        self.article = XmlLib.get_single_element(
            element=self.xml, xpath=f"/*[local-name()='{JATSDoc.ARTICLE}']")
        return self.article

    def get_front(self):
        """
        get <front> which must be child of <article>
        """
        self.front = self.get_article_component(JATSDoc.FRONT)
        return self.front

    def get_body(self):
        """
        get <body> which must be child of <article>
        """
        self.body = self.get_article_component(JATSDoc.BODY)
        return self.body

    def get_back(self):
        """
        get <back> which must be child of <article>
        """
        self.back = self.get_article_component(JATSDoc.BACK)
        return self.back

    def get_body_secs_non_secs(self):
        """
        gets all body-child elements grouped into secs , and non-secs
        """
        self.body = self.get_body()
        if self.body is None:
            logger.warn(f"no body")
        else:
            self.body_secs = self.body.xpath(f"*[local-name()='{JATSDoc.SEC}']")
            self.body_non_secs = self.body.xpath(f"*[local-name()!='{JATSDoc.SEC}']")
        return self.body_secs, self.body_non_secs

    @classmethod
    def get_titles_and_ids(cls, sec_list: List):
        """get titles from sections
        Assume <title> child
        """
        if sec_list is None:
            return None
        titles_and_ids = list()
        for sec in sec_list:
            title, id = cls.get_title_and_id(sec)
            titles_and_ids.append((title, id))
        return titles_and_ids

    @classmethod
    def get_title_and_id(cls, sec: _Element):
        """
        get title and id of sec(tion)
        generally title is <title> child and id is @id
        :param sec: section
        :return: title, id
        """
        title_text = None
        id = None
        if type(sec) is _Element:
            id = sec.get('id')
            title = XmlLib.get_single_element(sec, "./*[local-name()='title']")
            title_text = None if title is None else "".join(title.itertext())
        return title_text, id
