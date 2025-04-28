import logging
import re
import unittest
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

# INLINE_DICT = {
#     "decision": {
#         "example": ["decision 1/CMA.2", "noting decision 1/CMA.2, paragraph 10 and ", ],
#         "regex":
#         # f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})",
#         # f"decision{WS}(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})(,{WS}paragraph(?P<paragraph>{WS}{INT}))?",
#             f"(?P<decision>{INT})/(?P<type>{CPTYPE}){DOT}(?P<session>{INT})",
#         "href": "FOO_BAR",
#         "split_span": True,
#         "idgen": "NYI",
#         "_parent_dir": f"{TARGET_DIR}",
#         "span_range": [0, 99],
#
#         # "href_template": f"{PARENT_DIR}/{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}",
#         # "href_template": f"../../{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}",
#         "href_template": f"{TARGET_DIR}/{{type}}_{{session}}/Decision_{{decision}}_{{type}}_{{session}}/{TARGET_STEM}.html",
#     },
#     "paragraph": {
#         "example": [
#             "paragraph 32 above",
#             "paragraph 23 below",
#             "paragraph 9 of decision 19/CMA.3",
#             "paragraph 77(d)(iii)",
#             "paragraph 37 of chapter VII of the annex",
#         ],
#         "regex": [f"paragraph (?P<paragraph>{INT} (above|below))",
#                   f"paragraph (?P<paragraph>{INT}{LP}{LC}{RP}{LP}{L_ROMAN}{RP})"
#                   ],
#     },
#     "exhort": {
#         "regex": f"{RESERVED_WORDS1}",
#         "href": "None",
#     },
#     "article": {
#         "example": ["Article 4, paragraph 19, of the (Paris Agreement)",
#                     "tenth preambular paragraph of the Paris Agreement",
#                     "Article 6, paragraph 3"],
#         "regex": f"Article (?P<article>{INT}), paragraph (?P<paragraph>{INT}), (of the (?P<agreement>Paris Agreement))?",
#     },
#     "trust_fund": {
#         "regex": "Trust Fund for Supplementary Activities",
#         "href_template": "https://unfccc.int/documents/472648",
#     },
#     "adaptation_fund": {
#         "regex": "([Tt]he )?Adaptation Fund",
#         "href_template": "https://unfccc.int/Adaptation-Fund",
#     },
#     "paris": {
#         "regex": "([Tt]he )?Paris Agreement",
#         "href_template": "https://unfccc.int/process-and-meetings/the-paris-agreement",
#     },
#     "cop": {
#         "regex": "([Tt]he )?Conference of the Parties",
#         "href_template": "https://unfccc.int/process/bodies/supreme-bodies/conference-of-the-parties-cop",
#     },
#     "sbi": {
#         "regex": "([Tt]he )?Subsidiary Body for Implementation",
#         "acronym": "SBI",
#         "wiki": "https://en.wikipedia.org/wiki/Subsidiary_Body_for_Implementation",
#         "href": "https://unfccc.int/process/bodies/subsidiary-bodies/sbi"
#     },
#     # data
#     "temperature": {
#         "example": "1.5 °C",
#         "regex": f"{FLOAT}{WS}°C",
#         "class": "temperature",
#     },
#     # date
#     "date": {
#         "example": "2019",
#         "regex": f"20\\d\\d",
#         "class": "date",
#     }
# }

# mocking
INLINE_DICT = dict()
MARKUP_DICT = dict()
DECISION_SESS_RE = ""
#
MAXPDF = 3
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


class TestUNFCCC(AmiAnyTest):
    """Tests high level operations relating to UN content (currently SpanMarker and UN/IPCC)
    """

    @unittest.skip("Spanish language")
    def test_read_unfccc(self):
        """Uses a file in Spanish"""
        input_pdf = Path(UNFCCC_DIR, "cma2023_10a02S.pdf")
        assert input_pdf.exists()
        outdir = Path(Resources.TEMP_DIR, "unfccc")
        outdir.mkdir(exist_ok=True)
        # PDFDebug.debug_pdf(input_pdf, outdir, debug_options=[WORDS, IMAGES, TEXTS])
        html_elem = HtmlGenerator.create_sections(input_pdf)
        """decisión 2/CMA.3, anexo, capítulo IV.B"""
        doclink = re.compile(
            ".*decisión (?P<decision>\\d+)/CMA\\.(?P<cma>\\d+), (?P<anex>(anexo)), (?P<capit>(capítulo)) (?P<roman>[IVX]+)\\.?(?P<letter>[A-F])?.*")
        texts = html_elem.xpath("//*/text()")
        for text in texts:
            match = re.match(doclink, text)
            if match:
                for (k, v) in match.groupdict().items():
                    print(f"{k, v}", end="")
                print()

    @unittest.skip("probably obsolete")
    def test_read_unfccc_many(self):
        """
        NOT YET WORKING
        * reads MAXPDF unfccc reports in PDF,
        * transdlates to HTML,
        * adds semantic indexing for paragraphs
        * extracts targets from running text (NYI)
        * builds csv table (NYI)
        which can be fed into pyvis to create a knowledge graph
        """
        """TODO needs markup_dict"""
        """currently matches but does not output"""
        input_dir = Path(UNFCCC_DIR, "unfcccdocuments")
        pdf_list = FileLib.posix_glob(f"{input_dir}/*.pdf")[:MAXPDF]

        span_marker = SpanMarker()
        span_marker.indir = input_dir
        span_marker.outdir = Path(Resources.TEMP_DIR, "unfcccOUT")
        span_marker.outfile = "links.csv"
        # span_marker.markup_dict = MARKUP_DICT
        span_marker.markup_dict = INLINE_DICT
        span_marker.read_and_process_pdfs(pdf_list)
        span_marker.analyse_after_match_NOOP()

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

    @unittest.skip("not sure this is useful")
    def test_find_unfccc_decisions_multiple_documents(self, UNFCCC_TEMP_DIR=None):
        """
        looks for strings such as decision 20/CMA.3:
        over a complete recursive directory

        takes simple HTML element:
        """

        input_dir = Path(UNFCCC_DIR, "unfcccdocuments1")
        pdf_glob = "/*C*/*.pdf"
        # pdf_glob = "/CMA*/*.pdf"
        pdf_files = FileLib.posix_glob(str(input_dir) + pdf_glob)[:MAXPDF]
        assert len(pdf_files) > 0

        for pdf_infile in pdf_files[:999]:
            html_elem = HtmlGenerator.read_pdf_convert_to_html("foo", pdf_infile,
                                                               section_regexes="")  # section_regexes forces styles
            stem = Path(pdf_infile).stem
            HtmlLib.write_html_file(html_elem, Path(UNFCCC_TEMP_DIR, "html", stem, f"{stem}.raw.html"), debug=True)
            # html_infile = Path(input_dir, "1_CMA_3_section target.html")
            # SpanMarker.parse_unfccc_doc(html_infile, debug=True)


    @unittest.skip("maybe obsolete")
    def test_split_infcc_on_decisions_multiple_file_not_finished(self):
        span_marker = SpanMarker()
        html_files = FileLib.posix_glob(str(Path(UNFCCC_TEMP_DIR, "html/*/*.raw.html")))
        decision = "dummy_decis"
        type = "dummy_type"
        session = "dummy_session"
        for html_file in html_files:
            print(f"html file {html_file}")
            span_marker.infile = str(html_file)
            span_marker.parse_html(
                splitter_re="Decision\\s+(?P<decision>\\d+)/(?P<type>CMA|CP|CMP)\\.(?P<session>\\d+)\\s*"
                # ,split_files=f"{decision}_{type}_{session}"
            )
            if str(span_marker.infile).endswith(".decis.html"):
                continue
            outfile = span_marker.infile.replace(".raw.html", ".decis.html")
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

        UNFCCC.run_pipeline_on_unfccc_session(
            in_dir,
            session_dir,
            top_out_dir=top_out_dir
        )

    def _make_top_in_and_out_and_session(self, in_top=UNFCCC_DIR, out_top=UNFCCC_TEMP_DIR, sub_top="unfcccdocuments1",
                                         session_dir="CMA_3"):
        in_dir = Path(in_top, sub_top)
        top_out_dir = Path(out_top, sub_top)
        return in_dir, session_dir, top_out_dir

    @unittest.skipUnless(AmiAnyTest.run_long() or True, "run occasionally")
    def test_explicit_conversion_pipeline_IMPORTANT_CORPUS(self):
        """reads a corpus of 12 sessions and generates split.html for each
        See test_explicit_conversion_pipeline_IMPORTANT_DEFINITIVE(self): which is run for each session document
        """
        sub_top = "unfcccdocuments1"
        in_dir = Path(UNFCCC_DIR, sub_top)
        top_out_dir = Path(UNFCCC_TEMP_DIR, sub_top)

        session_files = FileLib.posix_glob(str(in_dir) + "/*")
        session_dirs = [d for d in session_files if Path(d).is_dir()]
        print(f">session_dirs {session_dirs}")
        assert len(session_dirs) >= 1

        maxsession = 5  # otyherwise runs for ever
        for session_dir in session_dirs[:maxsession]:
            UNFCCC.run_pipeline_on_unfccc_session(
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

    def test_extract_decision_hyperlinks_from_CORPUS(self):
        """iterates over all marked.html and extracts hyperlinks to Decisions
        """
        sub_top = "unfcccdocuments1"
        in_dir = Path(UNFCCC_TEMP_DIR, sub_top)
        outcsv = Path(in_dir, "decision_links.csv")
        outcsv_wt = Path(in_dir, "decision_links_wt.csv")
        UNFCCC.create_decision_table(in_dir, outcsv, outcsv_wt=None)

        print(f"wrote csv {outcsv}")

    def test_OBOE_error_for_split_to_marked(self):
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
        out_sub_dir = Path(top_out_dir, session)
        skip_assert = True
        file_splitter = "span[@class='Decision']"  # TODO move to dictionary
        targets = ["decision", "paris"]
        class_with_directory_maker = UNFCCC
        for instem in instem_list:

            HtmlPipeline.stateless_pipeline(
                file_splitter=file_splitter, in_dir=in_dir, in_sub_dir=in_sub_dir, instem=instem,
                out_sub_dir=out_sub_dir,
                # skip_assert=skip_assert,
                top_out_dir=top_out_dir,
                directory_maker=class_with_directory_maker,
                markup_dict=MARKUP_DICT,
                inline_dict=INLINE_DICT,
                targets=targets)
        decision = "Decision_1_CP_20"
        split_file = Path(out_sub_dir, decision, "split.html")
        assert split_file.exists()
        marked_file = Path(out_sub_dir, decision, "marked.html")
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



