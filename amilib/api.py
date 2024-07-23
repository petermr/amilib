import pandas as pd
import lxml.etree as ET

from amilib.util import Util
from amilib.xml_lib import HtmlLib


class EPMCBib:
    """
        # all_cols = [id,source,pmid,pmcid,fullTextIdList,doi,title,authorString,authorList,authorIdList,
        # dataLinksTagsList,journalInfo,pubYear,pageInfo,abstractText,affiliation,publicationStatus,language,
        # pubModel,pubTypeList,grantsList,keywordList,fullTextUrlList,isOpenAccess,inEPMC,inPMC,hasPDF,
        # hasBook,hasSuppl,citedByCount,hasData,hasReferences,hasTextMinedTerms,hasDbCrossReferences,hasLabsLinks,
        # license,hasEvaluations,authMan,epmcAuthMan,nihAuthMan,hasTMAccessionNumbers,tmAccessionTypeList,
        # dateOfCreation,firstIndexDate,fullTextReceivedDate,dateOfRevision,electronicPublicationDate,
        # firstPublicationDate,subsetList,commentCorrectionList,meshHeadingList,dateOfCompletion,manuscriptId,
        # embargoDate,chemicalList]
    """
    INT = "int"
    LIST = "list"
    ORDERED_DICT = "OrderedDict"
    STR = "str"

    PMCID = 'pmcid'
    DOI = 'doi'
    TITLE = 'title'
    AUTHOR_STRING = 'authorString'
    JOURNAL_INFO = 'journalInfo'
    PUB_YEAR = 'pubYear'
    PAGE_INFO = 'pageInfo'

    FORMATS = {
        PMCID: STR,
        DOI: STR,
        TITLE: STR,
        AUTHOR_STRING: LIST,
        JOURNAL_INFO: ORDERED_DICT,
        PUB_YEAR: INT,
        PAGE_INFO: STR,
    }

    COMMON = [
        'pmcid',
        'doi',
        'title',
        'authorString',
        'journalInfo',
        'pubYear',
        'pageInfo'
    ]

    @classmethod
    def format_field(cls, name, val):
        """
        uses 'name' in EPMC metadata to find format and return transformed value,

        :param name: name of field (e.g. 'journalInfo')
        :param val: raw string value
        :return: object of correct type (e.g. List or OrderedDict
        """

        fmt = cls.FORMATS.get(name)
        if fmt is None:
            fmt = cls.STR
        valx = str(val)
        if fmt == cls.LIST:
            valx = [v.strip() for v in val.split(",")]
        if fmt == cls.INT:
            valx = int(val)
        if fmt == cls.ORDERED_DICT:
            valx = Util.read_ordered_dict_from_str(val)

        return valx

    @classmethod
    def make_bib_html(cls, infile):
        htmlx = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(htmlx)
        ul = ET.SubElement(body, "ul")

        usecols = EPMCBib.COMMON
        usecols = None
        df = pd.read_csv(str(infile), usecols=usecols)
        for index, row in df.iterrows():
            cls.create_add_li(row, ul)
        return htmlx

    @classmethod
    def create_add_li(cls, row, ul):
        line_span = ET.SubElement(ul, "li")
        # cls.add_span(row, line_span, cls.PMCID)
        # jinfo = JournalInfo.create_journal_info_span(row, line_span)
        cls.add_span(row, line_span, cls.AUTHOR_STRING, end=", ")
        cls.add_span(row, line_span, cls.TITLE, start=' "', end='" ')
        cls.add_journal_info_span(row, line_span)
        cls.add_span(row, line_span, cls.PAGE_INFO, start=' ', end=' ')
        cls.add_span(row, line_span, cls.DOI, start=' DOI: ', end='')


    @classmethod
    def add_span(cls, row, line_span, name, start="", end = ""):
        val = row.get(name)
        if val is not None:
            el = ET.SubElement(line_span, "span")
            el.text = start + str(val)
            el.tail = end

    @classmethod
    def add_journal_info_span(cls, row, line_span):
        jinfo = JournalInfo.create_journal_info(row)
        if jinfo is not None:
            jinfo_span = ET.SubElement(line_span, "span")
            cls._add_span(jinfo_span, jinfo.vol, start=" ", end="")
            cls._add_span(jinfo_span, jinfo.issue, start="(", end=") ")
            # cls._add_span(jinfo_span, jinfo.pub_date, start=" (", end="): ")
            # cls._add_span(jinfo_span, jinfo.month_pub, start=" M ", end=" ")
            cls._add_span(jinfo_span, jinfo.year_pub, start=" (", end="): ")
            # cls._add_span(jinfo_span, jinfo.print_pub_date, start=" X ", end=" ")
            # cls._add_span(jinfo_span, jinfo.nlm_id)
            # cls._add_span(jinfo_span, jinfo.issn)
            # cls._add_span(jinfo_span, jinfo.essn)


    @classmethod
    def _add_span(cls, jinfo_span, text, start="", end=""):
        if jinfo_span is not None and text is not None:
            el = ET.SubElement(jinfo_span, "span")
            el.text = start + text + end



class JournalInfo:
    """
    OrderedDict([('volume', '9'), ('journalIssueId', '3560901'), ('dateOfPublication', '2023'),
    ('monthOfPublication', '0'), ('yearOfPublication', '2023'), ('printPublicationDate', '2023-01-01'),
    ('NLMid', '101660598'), ('ISSN', '2167-9843'), ('ESSN', '2376-5992')])
    """
    JOURNAL = 'journal'
    JOURNAL_INFO = 'journalInfo'
    VOLUME = 'volume'  # int
    ISSUE = 'issue'
    JOURNAL_ISSUE_ID = 'journalIssueId'
    DATE_OF_PUBLICATION = 'dateOfPublication'
    MONTH_OF_PUBLICATION = 'monthOfPublication'
    YEAR_OF_PUBLICATION = 'yearOfPublication'  # int
    PRINT_PUBLICATION_DATE = 'printPublicationDate'  # yyyy-mm-dd '2023-01-01'),
    NLM_ID = 'NLMid'  # str
    ISSN = 'ISSN'  # dddd-dddd,
    ESSN = 'ESSN'  # dddd-dddd,

    def __init__(self):
        self.vol = None
        self.jissue_id = None
        self.pub_date = None
        self.month_pub = None
        self.year_pub = None
        self.print_pub_date = None
        self.nlm_id = None
        self.issn = None
        self.essn = None

    @classmethod
    def create_journal_info(cls, row):
        jinfo = None
        if row is not None:
            jinfo = JournalInfo()
            jinfo_s = row.get(cls.JOURNAL_INFO)
            keys = row.keys()
            print(f"row keys {keys} /// {jinfo_s}")
            jinfo_od = Util.read_ordered_dict_from_str(jinfo_s)
            # jinfo_dict = Util.read_ordered_dict_from_str1(jinfo_s)
            keys = jinfo_od.keys()
            print(f"keys0 {keys}")

            jinfo.vol = jinfo_od.get(cls.VOLUME)
            jinfo.issue = jinfo_od.get(cls.ISSUE)
            jinfo.pub_date = jinfo_od.get(cls.DATE_OF_PUBLICATION)
            jinfo.month_pub = jinfo_od.get(cls.MONTH_OF_PUBLICATION)
            jinfo.year_pub = jinfo_od.get(cls.YEAR_OF_PUBLICATION)
            jinfo.print_pub_date = jinfo_od.get(cls.PRINT_PUBLICATION_DATE)
            jinfo.nlm_id = jinfo_od.get(cls.NLM_ID)
            jinfo.issn = jinfo_od.get(cls.ISSN)
            jinfo.essn = jinfo_od.get(cls.ESSN)

            jnl_s = row.get(cls.JOURNAL)
            if jnl_s is not None:
                jnl_od = Util.read_ordered_dict_from_str(jnl_s)
                keys = jnl_od.keys()
                print(f"JNL {keys} {jnl_od}")
        return jinfo



    def get_html_span(cls, row):
        pass
