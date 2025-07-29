import csv
import logging
import re
import unittest
from collections import Counter
from pathlib import Path

import lxml
import lxml.etree as ET
from amilib.file_lib import FileLib
from amilib.html_generator import HtmlGenerator
#
from amilib.html_marker import SpanMarker, HtmlPipeline
from amilib.util import Util
from amilib.ami_html import HtmlLib

# from climate.amix import AMIClimate, REPO_DIR
# from climate.un import DECISION_SESS_RE, MARKUP_DICT, INLINE_DICT, UNFCCC, UNFCCCArgs
#
from test.resources import Resources
from test.test_all import AmiAnyTest

"""Mainly to test PDF conversion (which used to work)"""
#
# required for UNFCCC which was developed in amiclimat
REPO_DIR = Path(Resources.TEST_RESOURCES_DIR).parent

UNFCCC_DIR = Path(Resources.TEST_RESOURCES_DIR, "unfccc")
UNFCCC_TEMP_DIR = Path(Resources.TEMP_DIR, "unfccc")
UNFCCC_TEMP_DOC_DIR = Path(UNFCCC_TEMP_DIR, "unfcccdocuments1")

ROMAN = "I|II|III|IIII|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI*"
L_ROMAN = "i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx"
INT = "\\d+"  # integer of any length
DIGIT = "\\d"  # single digit
DOT = f"\\."  # dot
MINUS = "-"
FLOAT = f"{MINUS}?{INT}({DOT}{INT})?"
SP = "\\s"  # single space
WS = "\\s+"  # spaces
ANY = ".*"
SL = "/"  # slash
LP = "\\("  # left parenthesis
RP = "\\)"  # right parenthesis
LC = "[a-z]"  # single uppercase
UC = "[A-Z]"  # single uppercase
#
DECISION_SESS_RE = re.compile(
    f"(?P<front>{ANY}\\D)(?P<dec_no>{INT})/(?P<body>{ANY}){DOT}(?P<sess_no>{INT}){DOT}?(?P<end>{ANY})")

RESERVED_WORDS = {
    'Recalling',
    'Also recalling',
    'Further recalling',
    'Recognizing',
    'Cognizant',
    'Annex',
    'Abbreviations and acronyms',
    'Noting',
    'Acknowledging',
}

RESERVED_WORDS1 = "(Also|[Ff]urther )?([Rr]ecalling|[Rr]ecogniz(es|ing)|Welcomes|[Cc]ognizant|[Nn]ot(ing|es)" \
                  "|Invit(es|ing)|Acknowledging|[Ex]pressing appreciation]|Recalls|Stresses|Urges|Requests|Expresses alarm)"

CPTYPE = "CP|CMA|CMP"
SUBPARA = f"({LP}?P<subpara>{LC}){RP}"
SUBSUBPARA = f"({LP}?P<subsubpara>{L_ROMAN}){RP}"
PARENT_DIR = "unfccc/unfcccdocuments1"  # probably temporary
TARGET_DIR = "../../../../../temp/unfccc/unfcccdocuments1/"

REPO_TOP = "https://raw.githubusercontent.com/petermr/pyamihtml/main"
TEST_REPO = f"{REPO_TOP}/test/resources/unfccc/unfcccdocuments1"
TEMP_REPO = f"{REPO_TOP}/temp/unfccc/unfcccdocuments1"

# markup against terms in spans
TARGET_STEM = "marked"  # was "split"

INLINE_DICT = {
    "decision": {
        "example": ["decision 1/CMA.2", "noting decision 1/CMA.2, paragraph 10 and ", ],
        "regex":
        # f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})",
        # f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})(,{WS}paragraph(?P<paragraph>{WS}{INT}))?",
            f"(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})",
        "href": "FOO_BAR",
        "split_span": True,
        "idgen": "NYI",
        "_parent_dir": f"{TARGET_DIR}",
        "span_range": [0, 99],

        # "href_template": f"{PARENT_DIR}/{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}",
        # "href_template": f"../../{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}",
        "href_template": f"{TARGET_DIR}/{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}/{TARGET_STEM}.html",
    },
    "paragraph": {
        "example": [
            "paragraph 32 above",
            "paragraph 23 below",
            "paragraph 9 of decision 19/CMA.3",
            "paragraph 77(d)(iii)",
            "paragraph 37 of chapter VII of the annex",
        ],
        "regex": [f"paragraph (?P<paragraph>{INT} (above|below))",
                  f"paragraph (?P<paragraph>{INT}{LP}{LC}{RP}{LP}{L_ROMAN}{RP})"
                  ],
    },
    "exhort": {
        "regex": f"{RESERVED_WORDS1}",
        "href": "None",
    },
    "article": {
        "example": ["Article 4, paragraph 19, of the (Paris Agreement)",
                    "tenth preambular paragraph of the Paris Agreement",
                    "Article 6, paragraph 3"],
        "regex": f"Article (?P<article>{INT}), paragraph (?P<paragraph>{INT}), (of the (?P<agreement>Paris Agreement))?",
    },
    "trust_fund": {
        "regex": "Trust Fund for Supplementary Activities",
        "href_template": "https://unfccc.int/documents/472648",
    },
    "adaptation_fund": {
        "regex": "([Tt]he )?Adaptation Fund",
        "href_template": "https://unfccc.int/Adaptation-Fund",
    },
    "paris": {
        "regex": "([Tt]he )?Paris Agreement",
        "href_template": "https://unfccc.int/process-and-meetings/the-paris-agreement",
    },
    "cop": {
        "regex": "([Tt]he )?Conference of the Parties",
        "href_template": "https://unfccc.int/process/bodies/supreme-bodies/conference-of-the-parties-cop",
    },
    "sbi": {
        "regex": "([Tt]he )?Subsidiary Body for Implementation",
        "acronym": "SBI",
        "wiki": "https://en.wikipedia.org/wiki/Subsidiary_Body_for_Implementation",
        "href": "https://unfccc.int/process/bodies/subsidiary-bodies/sbi"
    },
    # data
    "temperature": {
        "example": "1.5 °C",
        "regex": f"{FLOAT}{WS}°C",
        "class": "temperature",
    },
    # date
    "date": {
        "example": "2019",
        "regex": f"20\\d\\d",
        "class": "date",
    }
}
# section dict
MARKUP_DICT = {
    "Decision": {
        "level": 0,
        "parent": [],
        "example": ["Decision 1/CMA.1", "Decision 1/CMA.3"],
        "regex": f"Decision (?P<Decision>{INT})/(?P<type>{CPTYPE})\\.(?P<session>{INT})",
        "components": ["", ("Decision", f"{INT}"), "/", ("type", {CPTYPE}), f"{DOT}", ("session", f"{INT}"), ""],
        "names": ["roman", "title"],
        "class": "Decision",
        "span_range": [0, 1],
        "template": "Decision_{Decision}_{type}_{session}",
    },
    "Resolution": {
        "level": 0,
        "parent": [],
        "example": ["Resolution 1/CMA.1", "Resolution 1/CMA.3"],
        "regex": f"Resolution (?P<Resolution>{INT})/(?P<type>{CPTYPE})\\.(?P<session>{INT})",
        "components": ["", ("Resolution", f"{INT}"), "/", ("type", {CPTYPE}), f"{DOT}", ("session", f"{INT}"), ""],
        "names": ["roman", "title"],
        "class": "Resolution",
        "span_range": [0, 1],
        "template": "Resolution{Resolution}_{type}_{session}",
    },
    "chapter": {
        "level": 1,
        "parent": ["Decision"],
        "example": ["VIII.Collaboration", "I.Science and urgency"],
        "regex": f"(?P<dummy>)(?P<roman>{ROMAN}){DOT}\\s*(?P<title>{UC}.*)",
        "components": [("dummy", ""), ("roman", f"{ROMAN}"), f"{DOT}{WS}", ("title", f"{UC}{ANY}")],
        "names": ["roman", "title"],
        "class": "chapter",
        "span_range": [0, 1],
        "template": "chapter_{roman}",
    },
    "subchapter": {
        "level": "C",
        "parent": ["chapter"],
        "example": ["B.Annual information"],
        "regex": f"(?P<capital>{UC}){DOT}",
        "names": ["subchapter"],
        "class": "subchapter",
        "span_range": [0, 1],
        "template": "subchapter_{capital}",
    },

    "para": {
        "level": 2,
        "parent": ["chapter", "subchapter"],
        "example": ["26. "],
        "regex": f"(?P<para>{INT}){DOT}{SP}*",
        "names": ["para"],
        "class": "para",
        "parent": "preceeding::div[@class='roman'][1]",
        "idgen": {
            "parent": "Decision",
            "separator": ["_", "__"],
        },
        "span_range": [0, 1],
        "template": "para_{para}",
    },
    "subpara": {
        "level": 3,
        "parent": ["para"],
        "example": ["(a)Common time frames"],
        "regex": f"{LP}(?P<subpara>{LC}){RP}",
        "names": ["subpara"],
        "class": "subpara",
        "span_range": [0, 1],
        "template": "subpara_{subpara}",

    },
    "subsubpara": {
        "level": 4,
        "parent": ["subpara"],
        "example": ["(i)Methods for establishing"],
        "regex": f"{LP}(?P<subsubpara>{L_ROMAN}){RP}",
        "names": ["subsubpara"],
        "class": "subsubpara",
        "span_range": [0, 1],
    },

}
DECISION_SESS_RE = ""
#
MAXPDF = 1  # Reduced from 3 for faster testing
#
# OMIT_LONG = True  # omit long tests
#
# #
TEST_DIR = Path(REPO_DIR, "test")
TEMP_DIR = Path(REPO_DIR, "temp")
#
IPCC_TOP = Path(TEST_DIR, "resources", "ipcc", "cleaned_content")
# assert IPCC_TOP.exists(), f"{IPCC_TOP} should exist"
#
QUERIES_DIR = Path(TEMP_DIR, "queries")
# assert QUERIES_DIR.exists(), f"{QUERIES_DIR} should exist"
#
IPCC_DICT = {
    "_IPCC_REPORTS": IPCC_TOP,
    "_IPCC_QUERIES": QUERIES_DIR,
}
#
CLEANED_CONTENT = 'cleaned_content'
SYR = 'syr'
SYR_LR = 'longer-report'
IPCC_DIR = 'ipcc'
#

OUT_DIR_TOP = Path(FileLib.get_home(), "workspace")

# input
IPCC_URL = "https://www.ipcc.ch/"
AR6_URL = IPCC_URL + "report/ar6/"
SYR_URL = AR6_URL + "syr/"
WG1_URL = AR6_URL + "wg1/"
WG2_URL = AR6_URL + "wg2/"
WG3_URL = AR6_URL + "wg3/"

# SC_TEST_DIR = Path(OUT_DIR_TOP, "ipcc", "ar6", "test")

# logger = logging.getLogger(__file__)
# logger.setLevel(logging.WARNING)
logger = Util.get_logger(__name__)
logger.setLevel(logging.INFO)


@unittest.skip("Disabled for faster test runs during refactoring")
class TestUNFCCC(AmiAnyTest):
    """Tests high level operations relating to UN content (currently SpanMarker and UN/IPCC)
    """

    STYLES = [
        #  <style classref="div">div {border: red solid 0.5px;}</style>
        "span.temperature {border: purple solid 0.5px;}",
        ".chapter {border: blue solid 0.8px; font-weight: bold; background: red;}",
        ".subchapter {background: pink;}",
        ".para {border: blue dotted 0.6px; margin: 0.3px;}",
        ".subpara {border: blue solid 0.4px; margin: 0.2px; background: #eeeeee; opacity: 0.7}",
        ".subsubpara {border: blue dashed 0.2px; margin: 2px; background: #dddddd; opacity: 0.3}",
        "a[href] {background: #ffeecc;}",
        "* {font-size: 7; font-family: helvetica;}",
    ]

    UNFCCC_DICT = {
        # "1" : {
        #
        # },
        # "*" : {
        "name": "UNFCCC reports",
        "footer_height": 50,  # from lowest href underlines
        "header_height": 70,  # from 68.44
        "header_bottom_line_xrange": [20, 700],
        "footnote_top_line_xrange": [50, 300],
        "box_as_line_height": 1
    }

    @classmethod
    def create_initial_directories(cls, in_sub_dir, in_file, top_out_dir, out_stem=None, out_suffix="html"):
        """creates initial directory structure from PDF files
        in:
        test/resources/unfccc/unfcccdocuments1/CMA_3/1_4_CMA_3.pdf
        ............................top_in_dir| (implicit filename.parent.parent)
        ....................................._in_file............|
        ..................................in_sub_dir|
                                                    |.........| = in_subdir_stem
        out:
        temp/unfccc/unfcccdocuments1/CMA_3/1_4_CMA_3/raw.html
        .................top_outdir|
        ........................out_subdir|
        ...............................out_subsubdir|
                                                    |...|= out_stem
                                                         |....| = out_suffix

        Create outsubdir with same stem as in in_subdir
        create out_subsubdir from in_file stem
        create any directories with mkdir()
        :param in_sub_dir: subdirectory of corpus (session)
        :param in_file: file has implict subsub in stem
        :param top_out_dir: top of output directory (analogous to top_in_dir)
        :param out_stem: no default
        :param out_suffix: defaults to "html"
        :return: out_subsubdir, outfile (None if out_stem not given)

        thus
        """
        in_subdir_stem = Path(in_sub_dir).stem
        out_subdir_stem = in_subdir_stem
        out_subdir = Path(top_out_dir, out_subdir_stem)
        out_subdir.mkdir(parents=True, exist_ok=True)
        out_subsubdir = Path(out_subdir, in_file.stem)
        out_subsubdir.mkdir(parents=True, exist_ok=True)
        outfile = Path(out_subsubdir, out_stem + "." + out_suffix) if out_stem else None
        return out_subsubdir, outfile

    @classmethod
    def run_pipeline_on_unfccc_session(
            cls,
            in_dir,
            session_dir,
            in_sub_dir=None,
            top_out_dir=None,
            file_splitter=None,
            targets=None,
            directory_maker=None,
            markup_dict=None,
            inline_dict=None,
            param_dict=None,
            styles=None
    ):
        """
        directory structure is messy
        """

        session = Path(session_dir).stem
        if in_sub_dir is None:
            in_sub_dir = Path(in_dir, session)
        pdf_list = FileLib.posix_glob(str(in_sub_dir) + "/*.pdf")
        print(f"pdfs in session {session} => {pdf_list}")
        if not pdf_list:
            print(f"****no PDFs in {in_sub_dir}")
        subsession_list = [Path(pdf).stem for pdf in pdf_list]
        print(f"subsession_list {subsession_list}")
        if not top_out_dir:
            print(f"must give top_out_dir")
            return
        out_sub_dir = Path(top_out_dir, session)
        skip_assert = True
        if not file_splitter:
            file_splitter = "span[@class='Decision']"  # TODO move to dictionary
        if not targets:
            targets = ["decision", "paris", "wmo", "temperature"]
        if not directory_maker:
            directory_maker = TestUNFCCC
        if not markup_dict:
            markup_dict = MARKUP_DICT
        if not inline_dict:
            inline_dict = INLINE_DICT
        if not param_dict:
            param_dict = TestUNFCCC.UNFCCC_DICT
        if not styles:
            styles = TestUNFCCC.STYLES
        for subsession in subsession_list:
            HtmlPipeline.stateless_pipeline(

                file_splitter=file_splitter, in_dir=in_dir, in_sub_dir=in_sub_dir, instem=subsession,
                out_sub_dir=out_sub_dir,
                top_out_dir=top_out_dir,
                page_json_dir=Path(top_out_dir, "json"),
                directory_maker=directory_maker,
                markup_dict=markup_dict,
                inline_dict=inline_dict,
                param_dict=param_dict,
                targets=targets,
                styles=styles,
                force_make_pdf=True)

    @classmethod
    def create_decision_table(cls, in_dir, outcsv, outcsv_wt=None):
        """create table of links, rather ad hoc"""
        decision_files = TestUNFCCC.extract_decision_files_posix(in_dir)
        weight_dict = Counter()
        typex = "type"
        for decision_file in decision_files:
            decision_path = Path(decision_file)
            a_els = TestUNFCCC.extract_hyperlinks_to_decisions(decision_file)
            source_id = str(decision_path.parent.stem).replace("ecision", "")
            for a_elem in a_els:
                text = a_elem.text
                splits = text.split(",")
                # this should use idgen
                target_id = splits[0].replace("d", "D").replace(" ", "_").replace("/", "_").replace(".", "_") \
                    .replace("ecision", "")
                para = splits[1] if len(splits) == 2 else ""
                edge = (source_id, target_id, para)
                weight_dict[edge] += 1
        with open(outcsv, "w", encoding="UTF-8") as fw:
            FileLib.force_mkdir(outcsv.parent)
            csvwriter = csv.writer(fw)
            csvwriter.writerow(["source", "link_type", "target", "para", "weight"])
            for (edge, wt) in weight_dict.items():
                csvwriter.writerow([edge[0], typex, edge[1], edge[2], wt])
        print(f"wrote {outcsv}")

    @classmethod
    def extract_hyperlinks_to_decisions(self, marked_file):
        """Currently hyperlinks are
        file:///Users/pm286/workspace/pyamihtml_top/temp/unfccc/unfcccdocuments1//CP_21/Decision_1_CP_21/marked.html
        <a href="../../../../../temp/unfccc/unfcccdocuments1//CMA_3/Decision_1_CMA_3/marked.html">1/CMA.3</a>
        """

        html_elem = lxml.etree.parse(str(marked_file))
        a_elems = html_elem.xpath(".//a[@href[contains(.,'ecision')]]")
        return a_elems

    @classmethod
    def extract_decision_files_posix(cls, in_dir, stem="marked"):
        """extracts all files with "Decision" in file name
        :param in_dir: top directory of corpus (immediate children are session directories e.g. CMP_3
        :param stem: file stem, e.g. 'split', 'marked'"""
        files = FileLib.posix_glob(str(in_dir) + f"/*/Decision*/{stem}.html")
        return files


    # ========================== tests ==================

    # @unittest.skip("not the current approach. TODO add make to spanmarker pipeline")
    def test_read_unfccc_everything_MAINSTREAM(self):
        """"""
        """
        * reads unfccc reports in PDF,
        * transdlates to HTML,
        * adds semantic indexing for paragraphs
        * writes markedup html
        * extracts targets from running text (NYI)
        * builds csv table (NYI)
        which can be fed into pyvis to create a knowledge graph
        (writes outout to wrong dir)
        MAINSTREAM!
        """
        """
        Doesn't out
        ut anything
        """
        input_dir = Path(UNFCCC_DIR, "unfcccdocuments1")
        pdf_list = FileLib.posix_glob(f"{input_dir}/*C*/*.pdf")[:MAXPDF]  # select CMA/CMP/CP
        outcsv = "links.csv"
        outdir = Path(Resources.TEMP_DIR, "unfcccOUT")
        outhtmldir = str(Path(outdir, "newhtml"))
        markup_dict = MARKUP_DICT

        span_marker = SpanMarker(regex=DECISION_SESS_RE)
        span_marker.run_pipeline(input_dir=input_dir,
                                 outcsv=outcsv,
                                 outdir=outdir,
                                 pdf_list=pdf_list,
                                 markup_dict=markup_dict,
                                 outhtml=outhtmldir,
                                 debug=True
                                 )

    # @unittest.skip("probably redundant")
    def test_convert_pdfs_to_raw_html_IMPORTANT_STEP_1(self):
        """
        FIRST OPERATION
        tests reading the whole PDFs
        creates HTML elements
        OUTPUT - RAW HTML
        (raw HTML contains raw styles (e.g. .s1 ... .s78) in head/style)
        <style>.s15 {font-family: Times New Roman; font-size: 9.96;}</style>
        NOT normalized so we get
        <style>.s16 {font-family: Times New Roman; font-size: 9.96;}</style>

        steps:

        html_elem = HtmlGenerator.convert_to_html("foo", pdf)

        """

        input_dir = Path(UNFCCC_DIR, "unfcccdocuments1")
        assert input_dir.exists()
        pdfs = FileLib.posix_glob(f"{input_dir}/*C*/*.pdf")[:MAXPDF]
        assert MAXPDF >= len(pdfs) > 0
        for pdf in pdfs:
            print(f"parsing {pdf}")
            html_elem = HtmlGenerator.read_pdf_convert_to_html(pdf)

            # assertions
            assert html_elem is not None
            print (f"html {ET.tostring(html_elem)[:400]}")
            # does element contain styles?
            head = HtmlLib.get_head(html_elem)
            assert head is not None
            """
<head>
    <style>div {border : red solid 0.5px}</style>
    ...
</head>
"""
            styles = head.xpath("style")
            assert len(styles) > 5
            # are there divs?
            """
    <div left="113.42" right="123.75" top="451.04">
        <span x0="113.42" y0="451.04" x1="123.75" style="x0: 113.42; x1: 118.4; y0: 451.04; y1: 461.0; width: 4.98;" class="s34">1. </span>
        <span x0="141.74" y0="451.04" x1="184.67" style="x0: 141.74; x1: 150.04; y0: 451.04; y1: 461.0; width: 8.3;" class="s35">Welcomes </span>
        <span x0="184.7" y0="451.04" x1="451.15" style="x0: 184.7; x1: 187.47; y0: 451.04; y1: 461.0; width: 2.77;" class="s36">the entry into force of the Paris Agreement on 4 November 2016;  </span>
    </div>"""
            divs = HtmlLib.get_body(html_elem).xpath("div")
            assert len(divs) > 5
            # do they have spans with styles?
            spans = HtmlLib.get_body(html_elem).xpath("div/span[@class]")
            assert len(spans) > 20

            # outdir, outfile = SpanMarker.create_dir_and_file(pdf, stem="raw", suffix="html")
            outfile = f"{pdf}.raw.html"
            HtmlLib.write_html_file(html_elem, outfile=outfile, debug=True)

            assert Path(outfile).exists()

    def test_find_unfccc_decisions_INLINE_markup_regex_single_document_IMPORTANT(self):
        """
        INLINE marking
        looks for strings such as decision 20/CMA.3 using regex
        single

        takes simple HTML element and marks it with the in-span "decision"
        div
            span
        and splits the span with a regex, annotating the results
        adds classes
        tackles most of functionality



        """
        """
        Does inline markup
        """

        html_infile = self._normalized_test_file()
        targets = [
            "decision",
            "paris",
            # "adaptation_fund"
        ]

        span_marker = SpanMarker()
        span_marker.split_spans_in_html(html_infile=html_infile, targets=targets, markup_dict=INLINE_DICT, debug=True)

    def _normalized_test_file(self):
        UNFCCC_TEMP_DOC_DIR = Path(Resources.TEST_RESOURCES_DIR, "unfccc", "unfcccdocuments1")
        assert UNFCCC_TEMP_DOC_DIR.exists()
        input_dir = Path(UNFCCC_TEMP_DOC_DIR, "CMA_3")
        html_infile = Path(input_dir, "1_4_CMA_3", "normalized.html")  # not marked
        return html_infile

    def test_inline_dict_IMPORTANT(self):
        """
        This matches keywords but doesn't markup file .
        DOESNT do hyperlinks
        """
        html_infile = self._normalized_test_file()
        input_dir = html_infile.parent
        html_outdir = Path(Resources.TEMP_DIR, "unfccc", "html")
        span_marker = SpanMarker(markup_dict=INLINE_DICT)
        outfile = Path(html_outdir, "1_CMA_3", "normalized.marked.html")
        Util.delete_file_and_check(outfile)
        html_elem = ET.parse(str(html_infile))
        span_marker.markup_html_element_with_markup_dict(
            html_elem,
            input_dir=input_dir,
            html_outdir=html_outdir,
            dict_name="dummy_dict",
            html_out=outfile,
            debug=True
        )
        assert outfile.exists()
        html_out_elem = HtmlLib.parse_html(outfile)
        assert html_out_elem is not None, f"html_out_elem from {outfile} should not be None"
        ahrefs = html_out_elem.xpath(".//a/@href")
        print(f"hrefs: {len(ahrefs)}")

    def test_find_ids_markup_dict_single_document_IMPORTANT_2023_01_01(self):

        """TODO generate ids of section tags"""
        """
        looks for strings , especially with IDs ,
        single

        takes simple HTML element and marks it with the MARKUP_DICT
        div
            span
        and splits the span with a regex, annotating the results
        adds classes
        tackles most of functionality

        """
        """output_id of form DEC_1_CMA_3__VII__78__b"""
        """output_id of form RES_1_CMA_3__VII__78__b__iv"""
        """INPUT is HTML"""
        """WORKS - outputs marked up sections in files"""
        # regex = "[Dd]ecisions? \s*\d+/(CMA|CP)\.\d+"  # searches for strings of form fo, foo, for etc
        dict_name = "sections"

        html_infile = self._normalized_test_file()
        input_dir = html_infile.parent

        html_outdir = Path(Resources.TEMP_DIR, "unfccc", "html")
        outfile = Path(html_outdir, "1_4_CMA_3", f"split.{dict_name}.html")
        markup_dict = MARKUP_DICT
        html_elem = SpanMarker.markup_file_with_markup_dict(
            input_dir, html_infile, html_outdir=html_outdir, dict_name=dict_name, outfile=outfile,
            markup_dict=markup_dict, debug=True)
        assert outfile.exists()
        assert len(HtmlLib.get_body(html_elem).xpath("div")) > 0

    @unittest.skip("obsolete approach to splitting files. TODO needs mending")
    def test_split_into_files_at_id_single_IMPORTANT(self):

        dict_name = "sections"
        input_dir = Path(UNFCCC_TEMP_DOC_DIR, "CMA_3")
        infile = Path(input_dir, "1_CMA_3_section", f"normalized.{dict_name}.html")

        splitter = "./span[@class='Decision']"
        output_dir = input_dir
        SpanMarker.presplit_by_regex_into_sections(infile, output_dir, splitter=splitter, debug=True)

    @unittest.skip("until we fix the previous")
    def test_split_into_files_at_id_multiple_IMPORTANT(self):
        """Splits files at Decisions for all sessions"""
        """requires previous test to have been run"""

        dict_name = "sections"
        splitter = "./span[@class='Decision']/a/@href"
        MAXFILE = 3

        top_dir = Path(UNFCCC_DIR, "unfcccdocuments1")
        files = FileLib.posix_glob(str(top_dir) + "/*/*/normalized.html")
        assert len(files) > 0
        for infile in files[:MAXFILE]:
            print(f"infile {infile} ")
            session_dir = Path(infile).parent.parent
            print(f"session {session_dir}")
            output_dir = session_dir
            SpanMarker.presplit_by_regex_into_sections(infile, output_dir, splitter=splitter)

    @unittest.skip("Not finshed")
    def test_make_nested_divs(self):
        """IMPORTANT not finished"""
        """initial div files are 'flat' - all divs are siblings, Use parents in markup_dict to assemble
        """
        input_dir = Path(UNFCCC_DIR, "unfcccdocuments1", "CMA_3")
        infile = Path(input_dir, "1_4_CMA_3_section", f"normalized.sections.html")
        assert str(infile).endswith(
            "test/resources/unfccc/unfcccdocuments1/CMA_3/1_4_CMA_3_section/normalized.sections.html"),\
            f"should have a file .../test/resources/unfccc/unfcccdocuments1/CMA_3/1_4_CMA_3_section/normalized.sections.html"
        span_marker = SpanMarker(markup_dict=MARKUP_DICT)
        span_marker.parse_html(infile)
        span_marker.move_implicit_children_to_parents(span_marker.inhtml)
        outfile = str(infile).replace("sections", "nested")
        HtmlLib.write_html_file(span_marker.inhtml, outfile, debug=True)


    @unittest.skip("needs mending")
    def test_pipeline(self):
        """
        sequential operations
        input set of PDFs , -> raw.html -> id.html
        """

        print("lacking markup_dict")
        return
        # input dir of raw (unsplit PDFs) . Either single decisions or concatenated ones
        indir = Path(UNFCCC_DIR, "unfcccdocuments1")

        subdirs = FileLib.posix_glob(str(indir) + "/" + "C*" + "/")  # docs of form <UNFCCC_DIR>/C*/

        assert len(subdirs) == 12  # CMA_1 ... CMA_2... CP_27
        pdf_list = FileLib.posix_glob(subdirs[0] + "/" + "*.pdf")  # only CMA_1 to start with
        assert len(pdf_list) == 4
        # contains 4 PDFs as beloe
        skip = True
        if not skip:
            # TODO use symbolic top directory
            unittest.TestCase().assertListEqual(sorted(pdf_list), [
                '/Users/pm286/workspace/pyamihtml_top/test/resources/unfccc/unfcccdocuments1/CMA_1/13_20_CMA_1.pdf',
                '/Users/pm286/workspace/pyamihtml_top/test/resources/unfccc/unfcccdocuments1/CMA_1/1_CMA_1.pdf',
                '/Users/pm286/workspace/pyamihtml_top/test/resources/unfccc/unfcccdocuments1/CMA_1/2_CMA_1.pdf',
                '/Users/pm286/workspace/pyamihtml_top/test/resources/unfccc/unfcccdocuments1/CMA_1/3_12_CMA_1.pdf'
            ])

        # class for processing SpanMarker documents
        span_marker = SpanMarker(regex=DECISION_SESS_RE)

        span_marker.indir = '/Users/pm286/workspace/amiclimate/test/resources/unfccc/unfcccdocuments1'  # inout dir
        span_marker.outdir = Path(Resources.TEMP_DIR, "unfcccOUT")
        print(f"output to dir: {span_marker.outdir}")
        span_marker.outfile = "links.csv"  # probably in wrong place
        # convert to raw HTML
        span_marker.read_and_process_pdfs(pdf_list)
        span_marker.write_links("links.csv")  # currently no-op
        span_marker.analyse_after_match_NOOP()


    def test_explicit_conversion_pipeline_IMPORTANT_DEFINITIVE(self):
        """reads PDF and sequentially applies transformation to generate increasingly semantic HTML
        define output structure
        1 ) read a PDF with several concatenated Decisions and convert to raw html incluing paragraph-like divs => raw.html
           a) clip / extract headers and footers
           b) footnotes
        2 ) extract styles into head (one style per div)  combined
        3 ) normalize styles syntactically => normalized.html (syntactic styles)
        4 ) tag divs by style and content
        5 ) split major sections into separate HTML files (CMA1_4 -> CMA1, CMA2 ...)
        6 ) obsolete
        7 ) assemble hierarchical documents NYI
        8 ) search for substrings in spans and link to (a) dictionaries (b) other reports
        9 ) add hyperlinks to substrings
        10 ) create (a) manifest (b) reading order (c) ToC from HTML

        """
        # skip = {"step1"}
        in_dir, session_dir, top_out_dir = self._make_top_in_and_out_and_session()
        # sub_session_list = ["1_4_CMA_3", "5_CMA_3", "6_24_CMA_3"]

        # in_sub_dir = Path(in_dir, session_dir)
        # out_sub_dir = Path(top_out_dir, session_dir)
        force_make_pdf = True  # overrides the "make"
        # file_splitter = "span[@class='Decision']"  # TODO move to dictionary
        # targets = ["decision", "paris", "article", "temperature"]
        # debug = True

        TestUNFCCC.run_pipeline_on_unfccc_session(
            in_dir,
            session_dir,
            top_out_dir=top_out_dir
        )

    def _make_top_in_and_out_and_session(self, in_top=UNFCCC_DIR, out_top=UNFCCC_TEMP_DIR, sub_top="unfcccdocuments1",
                                         session_dir="CMA_3"):
        in_dir = Path(in_top, sub_top)
        top_out_dir = Path(out_top, sub_top)
        return in_dir, session_dir, top_out_dir

    @unittest.skip("run occasionally - long test")
    def test_explicit_conversion_pipeline_IMPORTANT_CORPUS(self):
        """reads a corpus of 12 sessions and generates split.html for each
        See test_explicit_conversion_pipeline_IMPORTANT_DEFINITIVE(self): which is run for each session document
        """
        sub_top = "unfcccdocuments1"
        MAXSESSION = 1  # Reduced from potential higher values for faster testing
        in_dir = Path(UNFCCC_DIR, sub_top)
        top_out_dir = Path(UNFCCC_TEMP_DIR, sub_top)

        session_files = FileLib.posix_glob(str(in_dir) + "/*")
        logger.info(f"using {len(session_files)} session_files")
        session_dirs = [d for d in session_files if Path(d).is_dir()]
        print(f">session_dirs {session_dirs}")
        assert len(session_dirs) >= 1

        for session_dir in session_dirs[:MAXSESSION]:
            TestUNFCCC.run_pipeline_on_unfccc_session(
                in_dir,
                session_dir,
                top_out_dir=top_out_dir
            )


    def test_create_decision_hyperlink_table(self):
        """creates table of hyperlinks from inline markuo to decisions
        relies on previously created *.marked.html
        """

        def _extract_hyperlinks_to_decisions(marked_file):
            """Currently hyperlinks are
            file:///Users/pm286/workspace/pyamihtml_top/temp/unfccc/unfcccdocuments1//CP_21/Decision_1_CP_21/marked.html
            <a href="../../../../../temp/unfccc/unfcccdocuments1//CMA_3/Decision_1_CMA_3/marked.html">1/CMA.3</a>
            """

            html_elem = lxml.etree.parse(str(marked_file))
            a_elems = html_elem.xpath(".//a[@href[contains(.,'ecision')]]")
            return a_elems

        sub_top = "unfcccdocuments1"
        # in_dir = Path(UNFCCC_TEMP_DIR, sub_top)
        in_dir = Path(Resources.TEST_RESOURCES_DIR, "unfccc", sub_top)
        in_sub_dir = Path(in_dir, "CMA_1")
        insub_sub_dir = Path(in_sub_dir, "Decision_4_CMA_1")
        marked_file = Path(insub_sub_dir, "marked.html")
        assert marked_file.exists()
        marked_elem = HtmlLib.parse_html(marked_file)
        a_elems = _extract_hyperlinks_to_decisions(marked_file)
        assert len(a_elems) > 12

    def test_extract_decision_hyperlinks_from_CORPUS_FAIL(self):
        """iterates over all marked.html and extracts hyperlinks to Decisions
        """
        sub_top = "unfcccdocuments1"
        in_dir = Path(UNFCCC_TEMP_DIR, sub_top)
        outcsv = Path(in_dir, "decision_links.csv")
        outcsv_wt = Path(in_dir, "decision_links_wt.csv")
        TestUNFCCC.create_decision_table(in_dir, outcsv, outcsv_wt=None)

        print(f"wrote csv {outcsv}")

    def test_OBOE_error_for_split_to_marked_FAIL(self):
        """converting a list of split.html to marked.html loses the last element
        tests the pipeline
        """

        session = "CP_21"
        session = "CP_20"

        # infile = Path(UNFCCC_DIR, "unfcccdocuments1", session, "1_CP_21.pdf")
        sub_top = "unfcccdocuments1"
        in_dir = Path(UNFCCC_DIR, sub_top)

        # instem_list = ["1_CP_21", "2_13_CP_21"]
        instem_list = ["1_CP_20", "2_12_CP_20"]

        in_sub_dir = Path(in_dir, session)
        top_out_dir = Path(UNFCCC_TEMP_DIR, sub_top)
        FileLib.force_mkdir(top_out_dir)
        logger.info(f"top_out_dir is {top_out_dir}")
        out_sub_dir = Path(top_out_dir, session)
        logger.info(f"out_sub_dir is {out_sub_dir}")
        FileLib.force_mkdir(out_sub_dir)
        skip_assert = True
        file_splitter = "span[@class='Decision']"  # TODO move to dictionary
        targets = ["decision", "paris"]

        # this needs methods
        class_with_directory_maker = TestUNFCCC
        for instem in instem_list:

            HtmlPipeline.stateless_pipeline(
                file_splitter=file_splitter,
                in_dir=in_dir,
                in_sub_dir=in_sub_dir,
                instem=instem,
                out_sub_dir=out_sub_dir,
                # skip_assert=skip_assert,
                top_out_dir=top_out_dir,
                directory_maker=class_with_directory_maker,
                markup_dict=MARKUP_DICT,
                inline_dict=INLINE_DICT,
                debug=True,
                targets=targets,
            )
        decision = "Decision_1_CP_20"
        split_file = Path(out_sub_dir, decision, "split.html")
        logger.info(f"split file is {split_file}")
        assert split_file.exists()
        marked_file = Path(out_sub_dir, decision, "marked.html")
        logger.info(f"marked file is {marked_file}")
        assert marked_file.exists()

    # def test_subcommands_simple(self):
    #
    #     # run args
    #     AMIClimate().run_command(
    #         ['UNFCCC', '--help'])
    #
    # @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    # def test_subcommands_long(self):
    #
    #     in_dir, session_dir, top_out_dir = self._make_top_in_and_out_and_session()
    #     try:
    #         AMIClimate().run_command(
    #             ['UNFCCC', '--indir', str(in_dir), '--outdir', str(top_out_dir), '--session', session_dir, '--operation',
    #              UNFCCCArgs.PIPELINE])
    #         raise ValueError("should raise bad argument 'Pipeline' NYI")
    #     except Exception as e:
    #         assert True, "expected fail"



