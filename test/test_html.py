"""Create, transform, markup up HTML, etc."""
import copy
import glob
import logging
import os
import pprint
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path

import lxml.etree
import lxml.etree as ET

# local
from lxml.etree import HTMLParser, _Element

from amilib.ami_bib import Reference, Biblioref
from amilib.file_lib import FileLib
from amilib.ami_html import HTMLSearcher, HtmlTree, HtmlAnnotator, AnnotatorCommand, URLCache, AmiAnnotator, HtmlEditor
from amilib.ami_html import HtmlUtil, H_SPAN, CSSStyle, HtmlTidy, HtmlStyle, HtmlClass, SectionHierarchy, AmiFont, \
    FloatBoundary, Footnote, HtmlGroup
from amilib.html_extra import HtmlExtra
from amilib.pdf_args import PDFArgs
from amilib.ami_pdf_libs import AmiPDFPlumber
from amilib.amix import AmiLib
from amilib.util import Util
from amilib.ami_html import (HtmlLib)
from amilib.xml_lib import XmlLib
from amilib.ami_integrate import HtmlGenerator

from test.resources import Resources
from test.test_all import AmiAnyTest

PARA1 = """
<span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id2507">First, the studies are relevant to different spatial levels, ranging from macro-scale regions with globally
comprehensive coverage to national level (4.2.2.3) and subnational and company level in a few cases
(4.2.3).  It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah (Deep  Decarbonization  Pathways  Project  2015;
Roelfsema et al. 2020) and even more blah.
</span>
"""

HTML_SINGLE_REF = """<span>It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah </span>"""
HTML_COMPOUND_REF = """<span>and more blah (Deep  Decarbonization  Pathways  Project  2015; Roelfsema et al. 2020)  and even more blah</span>"""
HTML_SUBSECTION_REF = """<span>to national level (4.2.2.3) and subnational</span>"""

# chunk of HTML from pdf2html on IPCC chapter
MINI_IPCC_PATH = Path(Resources.TEST_IPCC_CHAP06, "mini.html")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
logger.warning("*****Test logger {logger}****")



"""
see ami_html

NOTE. the use of classname, classref and similar is inconsistent. We want to have:
s1  to mean class name (classname)
.s1 to mean a reference to a classname (only used in <style> elements but involved in conversions
"""


# def add_children(jats, htmlx):
#     tag = jats.tag()
#     if tag == 'p':
#         html


class HtmlTest(AmiAnyTest):
    """
    parsing , structuring linking in/to.form HTML
    This will evolve into an ami_html.py module
    """
    # all are skipUnless

    ADMIN = True and AmiAnyTest.ADMIN
    BUG = True and AmiAnyTest.BUG
    CMD = True and AmiAnyTest.CMD
    DEBUG = True and AmiAnyTest.DEBUG
    LONG = True and AmiAnyTest.LONG
    NET = True and AmiAnyTest.NET
    OLD = True and AmiAnyTest.OLD
    NYI = True and AmiAnyTest.NYI
    USER = True and AmiAnyTest.USER

    def setUp(self) -> None:
        self.html = """<span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id2507">First, the studies are relevant to different spatial levels, ranging from macro-scale regions with globally 
        comprehensive coverage to national level (4.2.2.3) and subnational and company level in a few cases 
        (4.2.3).  It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah (Deep  Decarbonization  Pathways  Project  2015; 
        Roelfsema et al. 2020) and even more blah. 
        </span>"""
        self.html_single_ref = """<span>It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah </span>"""
        self.html_compound_ref = """<span>and more blah (Deep  Decarbonization  Pathways  Project  2015; Roelfsema et al. 2020)  and even more blah</span>"""
        self.html_subsection_ref = """<span>to national level (4.2.2.3) and subnational</span>"""

    def test_parse(self):
        """
        tests that test reference compiles
        """
        html_span = lxml.etree.fromstring(HTML_SINGLE_REF)
        assert type(html_span) is lxml.etree._Element
        assert html_span.text == "It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah "

        html_span = lxml.etree.fromstring(HTML_COMPOUND_REF)
        assert type(html_span) is lxml.etree._Element
        assert html_span.text == "and more blah (Deep  Decarbonization  Pathways  Project  2015; Roelfsema et al. 2020)  and even more blah"

        html_span = lxml.etree.fromstring(HTML_SUBSECTION_REF)
        assert type(html_span) is lxml.etree._Element
        assert html_span.text == "to national level (4.2.2.3) and subnational"

    def test_html_help(self):
        ''' runs HTML parser with --help to see if it produces terminal output
        '''
        pyami = AmiLib()
        pyami.run_command("HTML")
        pyami.run_command("HTML --help")


    @unittest.skip("dictionaries not included")
    def test_parse_commandline(self):
        """
        Simulate running from commandline
        """
        infile = Path(Resources.TEST_IPCC_CHAP06, "fulltext.html")
        assert infile.exists()
        outpath = Path(AmiAnyTest.TEMP_DIR, "html", 'fulltext.annot.html')
        if outpath.exists():
            os.remove(outpath)
        dictfile = Path(Resources.TEST_IPCC_CHAP06, 'abbrev_as.xml')
        assert dictfile.exists()
        args = f"HTML --inpath {infile} --outpath {outpath} --annotate --dict {dictfile} --color YELLOW"
        AmiLib().run_command(args)
        assert outpath.exists(), f"outpath {outpath} should exist"
        element = lxml.etree.parse(str(outpath))
        # crude count of success
        xpath = "//*[@href]"
        href_elems = element.xpath(xpath)
        assert len(href_elems) == 3, f"expected 3 hrefs, found {len(href_elems)}"

    @unittest.skipIf(OLD, "use TextChunker")
    def test_find_single_brackets_in_span(self):
        """
        add docs here
        """
        html_span = lxml.etree.fromstring(HTML_SINGLE_REF)
        text = html_span.text
        rec = re.compile(Util.SINGLE_BRACKET_RE)
        match = rec.match(text)
        assert match
        assert len(match.groups()) == 3
        assert match.group(
            0) == "It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah "
        assert match.group(1) == "It  is  important  blah blah detailed  national  studies  "
        assert match.group(2) == "Bataille  et  al.  2016a"
        assert match.group(3) == "  and more blah "

    def test_find_single_biblio_ref_in_span(self):
        """
        need docs
        """
        html_span = lxml.etree.fromstring(HTML_SINGLE_REF)
        text = html_span.text
        match = Reference.SINGLE_REF_REC.match(text)
        assert match
        assert len(match.groups()) == 3
        assert match.group(
            0) == "It  is  important  blah blah detailed  national  studies  (Bataille  et  al.  2016a)  and more blah "
        assert match.group('pre') == "It  is  important  blah blah detailed  national  studies  "
        assert match.group('body') == "Bataille  et  al.  2016a"
        assert match.group('post') == "  and more blah "
        assert match.groupdict() == {
            'body': 'Bataille  et  al.  2016a',
            'post': '  and more blah ',
            'pre': 'It  is  important  blah blah detailed  national  studies  '
        }

    def test_find_single_biblio_ref_in_span_add_links(self):
        """
        need docs
        """
        html_span = lxml.etree.fromstring(HTML_SINGLE_REF)
        text = html_span.text
        match = Reference.SINGLE_REF_REC.match(text)
        assert match
        assert len(match.groups()) == 3

    def test_find_brackets_in_text(self):
        """
        read chunks of text and find brackets
        """
        chap444 = Path(Resources.TEST_IPCC_CHAP04, "4.4.html")
        chap444_elem = lxml.etree.parse(str(chap444))
        div_spans = chap444_elem.xpath(".//div[span]")
        bodylist = []
        rec = re.compile(Util.SINGLE_BRACKET_RE)
        for div in div_spans:
            for span in div.xpath("./span"):
                match = rec.match(span.text)
                if match:
                    body = match.group('body')
                    bodylist.append(body)
        assert len(bodylist) == 114

    def test_find_bracketed_multiple_bibliorefs_in_text(self):
        """
        read chunks of text and find biblioref brackets
        """
        chap444 = Path(Resources.TEST_IPCC_CHAP04, "4.4.html")
        chap444_elem = lxml.etree.parse(str(chap444))
        div_spans = chap444_elem.xpath(".//div[span]")
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
        assert len(total_bibliorefs) == 103
        assert str(total_bibliorefs[0]) == 'de Coninck et al. 2018 => de Coninck| et al. |2018'
        assert str(total_bibliorefs[1]) == 'Grubb et al.  2021 => Grubb| et al.  |2021'

    def test_make_biblioref_manager(self):
        """
        read chunks of text and find biblioref brackets
        """
        chap444 = Path(Resources.TEST_IPCC_CHAP04, "4.4.html")
        bibliorefs = Biblioref.make_bibliorefs(chap444)
        counter = Counter()
        for biblioref in bibliorefs:
            ref = biblioref.first
            if ref not in counter:
                counter[ref] = 0
            counter[ref] += 1
        assert len(counter) == 86
        assert counter["IPCC"] == 6
        assert counter['Bindoff'] == 5
        assert counter['de Coninck'] == 2

    @unittest.skip("excluded from pyami_lite")
    def test_exceptions_biblio_ref_in_span(self):
        """
        Need docs
        """
        assert Reference.SINGLE_REF_REC.match("Foo bar (d'Arcy & other stuff in 2008) not a ref")
        assert Reference.SINGLE_REF_REC.match("Foo bar (de Sitter and other stuff in 2008) not a ref")

    @unittest.skip("excluded from pyami_lite")
    def test_not_ref_fail(self):
        assert not Reference.SINGLE_REF_REC.match("Foo bar (and other stuff in 2008) not a ref")

    @unittest.skip("excluded from pyami_lite")
    def test_markup_dois_in_references_(self):
        """reads a references file and creates active hyperlinks to referenced articles"""

        ref_path = Path(Resources.TEST_IPCC_CHAP04, "references.html")
        assert ref_path.exists()
        ref_elem = lxml.etree.parse(str(ref_path))
        ref_divs = ref_elem.xpath("body/div")
        assert len(ref_divs) == 1316

        for div in ref_divs:
            ref = Reference.create_ref_from_div(div)
            ref.markup_dois_in_spans()
        path = Path(AmiAnyTest.TEMP_DIR, "ipcc_html")
        path.mkdir(exist_ok=True)
        chap4_dir = Path(path, "chapter04")
        chap4_dir.mkdir(exist_ok=True)
        outpath = Path(chap4_dir, "ref_doi.html")
        ref_elem.write(str(outpath))

    def test_make_reference_class(self):
        """reads a references file and creates class"""

        # ami_html = AmiHtml()
        ref_path = Path(Resources.TEST_IPCC_CHAP04, "references.html")
        assert ref_path.exists()
        ref_elem = lxml.etree.parse(str(ref_path))
        ref_divs = ref_elem.xpath("body/div")
        assert len(ref_divs) == 1316

        Reference.markup_dois_in_div_spans(ref_divs)

        # path = Path(AmiAnyTest.TEMP_DIR)
        # path.mkdir(exist_ok=True)
        chap4_dir = Path(AmiAnyTest.TEMP_HTML_DIR, "ar6", "chapter04")
        chap4_dir.mkdir(exist_ok=True, parents=True)
        outpath = Path(chap4_dir, "ref_doi.html")
        ref_elem.write(str(outpath))

    def test_split_matched_string_in_span0(self):
        """split string in span into 3 using regex"""
        s = "prefix the (bracketed) string postfix"
        div_elem = lxml.etree.Element("div")
        span_elem = lxml.etree.SubElement(div_elem, "span")
        span_elem.attrib["class"] = "foo"
        span_elem.text = s
        assert lxml.etree.tostring(div_elem).decode("UTF-8") == \
               "<div><span class=\"foo\">prefix the (bracketed) string postfix</span></div>"
        span = div_elem.xpath("./span")[0]
        text = span.text
        match = re.compile(Util.SINGLE_BRACKET_RE).match(text)
        assert match
        assert len(match.groups()) == 3
        assert match.group(0) == "prefix the (bracketed) string postfix"
        assert match.group(1) == "prefix the "
        assert match.group(2) == "bracketed"
        assert match.group(3) == " string postfix"

        pref_span = HtmlUtil.add_sibling_after(span, H_SPAN, replace=True, copy_atts=True, text=match.group(1))
        target_span = HtmlUtil.add_sibling_after(pref_span, H_SPAN, copy_atts=True, text=match.group(2))
        post_span = HtmlUtil.add_sibling_after(target_span, H_SPAN, text=match.group(3))

        assert lxml.etree.tostring(div_elem).decode("UTF-8") == \
               "<div><span class=\"foo\">prefix the </span><span class=\"foo\">bracketed</span><span> string postfix</span></div>"

    def test_split_matched_string_in_span(self):
        """split string in span into 3 using regex
        Tests: HtmlUtil.split_span_at_match"""
        div_elem = lxml.etree.fromstring("<div><span class='foo'>prefix the (bracketed) string postfix</span></div>")
        span = div_elem.xpath("./span")[0]

        regex = Util.SINGLE_BRACKET_RE
        spans, _ = HtmlUtil.split_span_at_match(span, regex)
        assert spans[0] is not None
        assert spans[1] is not None
        assert spans[2] is not None

        assert lxml.etree.tostring(div_elem).decode("UTF-8") == \
               """<div><span class="re_pref">prefix the </span><span class="re_match">bracketed</span><span class="re_post"> string postfix</span></div>"""

        # no leading string
        div_elem = lxml.etree.fromstring("<div><span class='foo'>(bracketed) string postfix</span></div>")
        span = div_elem.xpath("./span")[0]
        spans, _ = HtmlUtil.split_span_at_match(span, regex)
        assert spans[0] is None
        assert spans[1] is not None
        assert spans[2] is not None

        # no trailing string
        div_elem = lxml.etree.fromstring("<div><span class='foo'>prefix the (bracketed)</span></div>")
        span = div_elem.xpath("./span")[0]
        spans, _ = HtmlUtil.split_span_at_match(span, regex)
        assert spans[0] is not None
        assert spans[1] is not None
        assert spans[2] is None

        # no leading or trailing string
        div_elem = lxml.etree.fromstring("<div><span class='foo'>(bracketed)</span></div>")
        span = div_elem.xpath("./span")[0]
        spans, _ = HtmlUtil.split_span_at_match(span, regex)
        assert spans[0] is None
        assert spans[1] is not None
        assert spans[2] is None

    def test_split_matched_string_in_span_recursively(self):
        """split string in span into 2n+1 using regex
        Tests: HtmlUtil.split_span_at_match"""
        div_elem = lxml.etree.fromstring(
            "<div><span class='foo'>prefix the (bracketed) and more (brackets) string postfix </span></div>")
        span = div_elem.xpath("./span")[0]

        regex = Util.SINGLE_BRACKET_RE
        HtmlUtil.split_span_at_match(span, regex, recurse=True)

        assert lxml.etree.tostring(div_elem).decode("UTF-8") == \
               """<div><span class="re_pref">prefix the </span><span class="re_match">bracketed</span><span class="re_pref"> and more </span><span class="re_match">brackets</span><span class="re_post"> string postfix </span></div>"""

    def test_split_caption_at_bracketed_panel_refs(self):
        """split at text (a) more (b) etc
        Test recursive splitting through HtmlUtil.split_span_at_match"""
        s = f"Box 6.2 Figure 1 Retirement of coal-fired power plants to limit warming to 1.5°C and" \
            f" likely 2°C. (a) Historical facility age at retirement (b) the vintage year of existing" \
            f" units, (c) global coal capacity under different plant lifetimes, compared to capacity" \
            f" levels consistent with a well-below 2°C (green) and 1.5°C(blue) pathway assuming no new" \
            f" coal plants, and (d) and assuming plants currently under construction come online as scheduled," \
            f" but those in planning or permitting stages are not built. (Cui et al. 2019)"

        div, span = HtmlUtil.create_div_span(s, style={"font-size: 12pt; font-weight: bold"})
        assert len(div.getchildren()) == 1
        regex = Util.SINGLE_BRACKET_RE
        HtmlUtil.split_span_at_match(span, regex, recurse=True, id_root="ss", id_counter=0)
        assert len(div.getchildren()) == 14
        phrases = []

        for span in div.getchildren():
            phrases.append(span.text)
        assert phrases == ['Box 6.2 Figure 1 Retirement of coal-fired power plants to limit warming to '
                           '1.5°C and likely 2°C. ', 'a', ' Historical facility age at retirement ', 'b',
                           ' the vintage year of existing units, ', 'c',
                           ' global coal capacity under different plant lifetimes, compared to capacity '
                           'levels consistent with a well-below 2°C ', 'green', ' and 1.5°C', 'blue',
                           ' pathway assuming no new coal plants, and ', 'd',
                           ' and assuming plants currently under construction come online as scheduled, '
                           'but those in planning or permitting stages are not built. ', 'Cui et al. 2019']

    def test_add_href_annotation(self):
        """
        Add Href for annotated word
        """
        s = f"We believe the GHG emissions are huge"
        rec = re.compile(r"(.*?)(\bGHG\b)(.*)")
        match = rec.search(s)
        assert match and len(match.groups()) == 3
        assert match.group(1) == "We believe the "
        assert match.group(2) == "GHG"
        assert match.group(3) == " emissions are huge"

    def test_add_href_annotation_in_span(self):
        """Add Href for annotated word
        Tests HtmlUtil.split_span_at_match"""
        s = f"We believe the GHG emissions are huge"
        div, span = HtmlUtil.create_div_span(s, style={"font-size: 12pt; font-weight: bold"})
        regex = r"(.*?)(\bGHG\b)(.*)"
        HtmlUtil.split_span_at_match(span, regex, new_tags=["b", "a", "i"],
                                     recurse=False, id_root="ss", id_counter=0)
        assert len(div.getchildren()) == 3
        bb = b'<div><b style="font-size: 12; font-weight: bold;" class="re_pref"' \
             b' id="ss0">We believe the </b><a style="font-size: 12; font-weight: bold;"' \
             b' class="re_match" id="ss1">GHG</a><i style="font-size: 12; font-weight: bold;"' \
             b' class="re_post" id="ss2"> emissions are huge</i></div>'
        assert lxml.etree.tostring(div) == bb
        a_elem = div.xpath("./a")[0]
        a_elem.attrib["href"] = "https://wikidata.org/wiki/Q167336"
        test_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        test_dir.mkdir(exist_ok=True)
        with open(str(Path(test_dir, "add_href.html")), "wb") as f:
            f.write(lxml.etree.tostring(div, method="html"))

    @unittest.skip("needs dictionary")
    def test_markup_chapter_with_dictionary_no_css(self):
        """read dictionary file and index a set of spans
        Test: ami_dict.markup_html_from_dictionary
        and add style
        and write result
        """
        dictionary_file = Path(Resources.TEST_IPCC_CHAP06, "abbrev_as.xml")
        assert dictionary_file.exists(), f"file should exist {dictionary_file}"
        # FIXME
        # ami_dict = AmiDictionary.create_from_xml_file(dictionary_file)
        ami_dict = None
        ami_dict.ignorecase = False
        inpath = Path(Resources.TEST_IPCC_CHAP06, "fulltext.flow20.html")
        output_dir = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06)
        output_dir.mkdir(exist_ok=True)
        output_path = Path(output_dir, "index.html")
        ami_dict.markup_html_from_dictionary(inpath, output_path, "pink")

    @unittest.skip("needs dictioary")
    def test_markup_chapter_with_dictionary(self):
        """read dictionary file and index a set of spans
        Test: ami_dict.markup_html_from_dictionary
        and add style
        and write result]
        TODO USE THIS!
        """

        dict_path = Path(Resources.TEST_IPCC_CHAP06, "abbrev_as.xml")
        dict_path = Path(Resources.TEST_IPCC_CHAP06, "ipcc_ch6_rake.xml")
        # FIXME when dictiomary is available
        # ami_dict = AmiDictionary.create_from_xml_file(dict_path, ignorecase=False)
        ami_dict = None
        input_path = Path(Resources.TEST_IPCC_CHAP06, "fulltext.flow.html")
        logger.info(f"reading pdf_html {input_path}")
        html_output_dir = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06)
        logger.info(f"output html {html_output_dir}")
        chap6_marked_path = Path(html_output_dir, "raked.html")

        ami_dict.markup_html_from_dictionary(input_path, chap6_marked_path, "pink")
        assert chap6_marked_path.exists(), f"marked-up html in {chap6_marked_path}"
        with open(chap6_marked_path, "rb") as f:
            marked_elem = lxml.etree.parse(f)

    # TODO fails
    def test_extract_styles_as_css(self):
        """read dictionary file and index a set of spans
        Test: ami_dict.markup_html_from_dictionary
        and add style
        and write result
        USEFUL
        """
        target_path = Path(Resources.TEST_IPCC_CHAP06, "fulltext.flow20.html")
        output_dir = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06)
        output_dir.mkdir(exist_ok=True)
        output_path = Path(output_dir, "styled.html")

        with open(target_path, "rb") as f:
            elem = lxml.etree.parse(f)
        styles = elem.xpath(".//@style")
        assert 200 >= len(styles) >= 100
        style_set = set()
        for style in styles:
            style_set.add(style)

        assert 10 >= len(style_set) >= 8

        sorted_styles = sorted(style_set)
        # assert sorted_styles == ['',
        #                          'font-family: ArialMT; font-size: 10px;',
        #                          'font-family: Calibri-Bold; font-size: 10px;',
        #                          'font-family: Calibri-Bold; font-size: 12px;',
        #                          'font-family: Calibri-Bold; font-size: 13px;',
        #                          'font-family: Calibri; font-size: 10px;',
        #                          'font-family: TimesNewRomanPS-BoldMT; font-size: 11px;',
        #                          'font-family: TimesNewRomanPS-BoldMT; font-size: 14px;',
        #                          'font-family: TimesNewRomanPS-BoldMT; font-size: 15px;',
        #                          'font-family: TimesNewRomanPS-BoldMT; font-size: 6px;',
        #                          'font-family: TimesNewRomanPS-BoldMT; font-size: 9px;',
        #                          'font-family: TimesNewRomanPS-ItalicMT; font-size: 11px;',
        #                          'font-family: TimesNewRomanPSMT; font-size: 11px;',
        #                          'font-family: TimesNewRomanPSMT; font-size: 6px;',
        #                          'font-family: TimesNewRomanPSMT; font-size: 9px;'
        #                          ]

        CSSStyle.extract_bold_italic_from_font_family_for_styles(sorted_styles)
        for style in sorted_styles:
            logger.debug(f"normalized style {style}")

    def test_join_spans(self):
        """join sibling spans with the same styles
        IMPORTANT
        """
        html_path = Path(Resources.TEST_IPCC_CHAP04, "fulltext.flow20.html")
        html_element = lxml.etree.parse(str(html_path))
        divs = html_element.xpath(".//div")
        assert 400 <= len(divs)
        last_div = None
        last_style = None
        for div in divs:
            spans = div.xpath("./span")
            for span in spans:
                style = CSSStyle.create_css_style_from_attribute_of_body_element(span)
                if style == last_style:
                    pass
                last_span = span
                last_style = style

    @unittest.skipUnless(USER, "claim paras")
    @unittest.skipIf(BUG and False, "bad input file")
    def test_make_ipcc_obsidian_md_CURRENT(self):
        """
        Read IPCC exec_summary Chapter and make obsidian MD.
        Reads an executive.summary consisting of about 20 paras, each of which
        has a bold first sentence (main claim).
        Tries to split this into the main claim and subclaims.

        writes 1 file per paragraph into B_1.md, B_2.md, etc.

<body>
<p class="p1"><span class="s1"><b>Executive Summary</b></span></p>
<p class="p2"><span class="s1"><b>Global net anthropogenic Greenhouse Gas (GHG) emissions during the last decade (2010-2019) were higher than at any previous time in human history </b><i>(high confidence)</i>. Since 2010, GHG emissions have continued to grow reaching 59±6.6 GtCO<sub>2</sub>eq in 2019<sup>1</sup>, but the average annual growth in the last decade (1.3%, 2010-2019) was lower than in the previous decade (2.1%, 2000-2009) (<i>high confidence</i>). Average annual GHG emissions were 56 GtCO<sub>2</sub>eqyr<sup>-1</sup> for the decade 2010-2019 growing by about 9.1 GtCO<sub>2</sub>eqyr<sup>-1</sup> from the previous decade (2000-2009) – the highest decadal average on record (<i>high confidence</i>). {2.2.2, Table 2.1, Figure 2.5}</span></p>
<p class="p2"><span class="s1"><b>Emissions growth has varied, but persisted across all groups of greenhouse gases </b><i>(high confidence)</i>. The average annual emission levels of the last decade (2010-2019) were higher than in any previous decade for each group of greenhouse gases (<i>high confidence</i>). In 2019, CO<sub>2</sub> emissions were 45±5.5 GtCO<sub>2</sub>,<sub>2</sub> CH<sub>4</sub> 11±3.2 GtCO<sub>2</sub>eq, N<sub>2</sub>O 2.7±1.6 GtCO<sub>2</sub>eq and fluorinated gases (F-gases: HFCs, PFCs, SF<sub>6</sub>, NF<sub>3</sub>) 1.4±0.41 GtCO<sub>2</sub>eq. Compared to 1990, the magnitude and speed of these increases differed across gases: CO<sub>2</sub> from fossil fuel and industry (FFI) grew by 15 GtCO<sub>2</sub>eqyr<sup>-1</sup> (67%), CH<sub>4</sub> by 2.4 GtCO<sub>2</sub>eqyr<sup>-1</sup>(29%), F-gases by 0.97 GtCO<sub>2</sub>eqyr<sup>-1</sup> (250%), N<sub>2</sub>O by 0.65 GtCO<sub>2</sub>eqyr<sup>-1</sup> (33%). CO<sub>2</sub> emissions from net land use, land-use change and forestry (LULUCF) have shown little long-term change, with large uncertainties preventing the detection of statistically significant trends. F-gases excluded from GHG emissions inventories such as <i>chlorofluorocarbons</i> and <i>hydrochlorofluorocarbons</i> are about the same size as those included (<i>high confidence</i>). {2.2.1, 2.2.2, Table 2.1, Figure 2.2, Figure 2.3, Figure 2.5}</span></p>

        BUGS: furst bold sentence missed out in B_10.md and B_20.md
        Maybe full-stop after italics is bold?

        THIS USED A STYLE-NORMALISED FILE WHICH I THINK WAS CREARTED  BY ATOM.
        THE FILE MAY BE LOST
        BUG

        https://stackoverflow.com/questions/62472162/lxml-xpath-expression-for-selecting-all-text-under-a-given-child-node-including
        """
        in_file = Path(Resources.TEST_IPCC_CHAP02, "exec_summary.html")
        outdir = Path(AmiAnyTest.TEMP_DIR, "obsidian")
        os.makedirs(outdir, exist_ok=True)
        path = Path(in_file)
        assert path.exists(), f"{path} should exist"
        tree = lxml.etree.parse(str(path))
        ps = tree.findall(".//p")
        assert 23 <= len(ps) <= 50
        i = 0
        for p in ps:
            bs = p.xpath(".//b")
            if len(bs) > 0:
                i += 1
                for b in bs:
                    t = b.xpath('.//text()')
                    bstr = "__".join(t)
                    nonb = p.xpath(".//text()[not(ancestor::b)]")
                    tstr = "".join(nonb)
                file = Path(outdir, f"B_{i}.md")
                logger.info(f"writing {file}")
                with open(file, "w", encoding="UTF-8") as f:
                    f.write(bstr)
                    f.write(tstr)

    @unittest.skip("climate-specific")
    def test_extract_ipcc_nodes_and_pointers_raw_format_NODES_CURRENT(self):
        """
        read (old style) raw html with IPCC nodes and node_pointers and convert to HTML@a elements
        example
        '(high confidence). {2.2.2, Table 2.1, Figure 2.5}' contains 3 node pointers
        """
        # html = "executive_summary_css.html"
        # html = "executive_summary1.html"
        # file = Path(Resources.TEST_IPCC_CHAP02, "maintext_old.html")
        file = Path(Resources.TEST_IPCC_DIR, "LongerReport", "fulltext.html")
        # make dictionary of regex extractor/splitters
        target_dict_from_ipcc_para_text = {
            TargetExtractor.TARGET_LIST_RE: "{([^}]+)}", # curly {...}
            TargetExtractor.TARGET_RE: "\\s*[,;]\\s*",   # semicolon/comma list ...; ...;
            TargetExtractor.TARGET_VALUE_RE: "(Table|Figure)\\s+(.*)", # (table, figure) value
        }
        logger.debug(f"text_dict {target_dict_from_ipcc_para_text}")

        node_extractor = TargetExtractor()
        HAS_CURLY = "//div[//text()[contains(., '{')]]"
        div_xp = HAS_CURLY
        paragraph_dict = node_extractor.extract_anchor_paragraphs(div_xp, file, target_dict_from_ipcc_para_text)
        logger.debug(f"paragraph_dict {paragraph_dict.keys()}")
        PACKAGE = 'package'
        SECTION = 'section'
        SUBPACKAGE = 'subpackage'

        node_re = re.compile(
            f"(?P<{PACKAGE}>"
              "(?:"
                "(?:WG\\s*(?:1|2|3|I|II|III)|SROCC|SRCCL|SR1\\.5"
                ")?"
              ")"
            ")"
            "\\s*"
                             
             f"(?P<{SUBPACKAGE}>"
             "(?:(?:Table|Figure|Box|SPM|TS|Chapter|Sections?|CCB|"
             "Cross-Chapter\\s+Box"
             "(?:\\s*[A-Z]+\\s*in\\s+Chapter\\s+[0-9]+)?"
             ")?)"
             ")"
            "\\s*"
             
             f"(?P<{SECTION}>"
             "(?:(?:(?:TS\\.)?[A-Z]|SPM|TS|[Ff]ootnote )\\.?)?"
             "\\d+(?:\\.\\d+)*"
             ")"
        )
        matched_dict = HtmlExtra.create_matched_dict_and_unmatched_keys(paragraph_dict, node_re)

        return HtmlExtra.create_counters(PACKAGE, SECTION, SUBPACKAGE, matched_dict, debug=True)
        # print(f"unmatched {len(unmatched_keys)} {unmatched_keys}")

        (matched_dict.keys(), Counter(pck_counter), Counter(subp_counter), Counter(sect_counter))



    def test_remove_floats_from_fulltext_html_DEVELOP(self):
        package = "LongerReport"
        file = Path(Resources.TEST_IPCC_DIR, package, "fulltext.html")
        html_elem = lxml.etree.parse(str(file)).getroot()
        FloatBoundary.extract_floats_and_boundaries(html_elem, package, outdir=str(Path(AmiAnyTest.TEMP_HTML_IPCC, package)))
        XmlLib.write_xml(html_elem, Path(AmiAnyTest.TEMP_HTML_IPCC, package, "defloated.html"))


    def test_remove_footnotes_from_fulltext_html_DEVELOP(self):
        """
        <style classref=".s0">.s0 {font-family:TimesNewRomanPSMT; font-size:11px; font-weight:Bold;}</style>
        <style classref=".s1">.s1 {}</style>
        <style classref=".s10">.s10 {font-family:TimesNewRomanPSMT; font-size:11px;}</style>
        <style classref=".s1001">.s1001 {font-family:TimesNewRomanPSMT; font-size:11px; font-style:Italic;}</style>
        <style classref=".s1007">.s1007 {font-family:TimesNewRomanPSMT; font-size:11px; font-weight:Bold; font-style:Italic;}</style>
        <style classref=".s1010">.s1010 {font-family:TimesNewRomanPSMT; font-size:6px;}</style> <!-- super/.sub -->
        <style classref=".s1045">.s1045 {font-family:TimesNewRomanPSMT; font-size:9px;}</style> <!-- main footnote -->
        <style classref=".s1046">.s1046 {font-family:TimesNewRomanPSMT; font-size:9px; font-weight:Bold;}</style> <!-- bold footnote? -->
        <style classref=".s1298">.s1298 {font-family:TimesNewRomanPSMT; font-size:6px; font-weight:Bold;}</style>
        <style classref=".s1317">.s1317 {font-family:TimesNewRomanPSMT; font-size:9px; font-style:Italic;}</style> <-- Italic footnote -->
        <style classref=".s1469">.s1469 {font-family:TimesNewRomanPSMT; font-size:5px;}</style>
        <style classref=".s1847">.s1847 {font-family:TimesNewRomanPSMT; font-size:12px; font-weight:Bold;}</style>
        <style classref=".s2597">.s2597 {font-family:TimesNewRomanPSMT; font-size:7px; font-weight:Bold;}</style>
        <style classref=".s2598">.s2598 {font-family:TimesNewRomanPSMT; font-size:7px;}</style>
        <style classref=".s3406">.s3406 {font-family:TimesNewRomanPSMT; font-size:12px;}</style>
        <style classref=".s4097">.s4097 {font-family:TimesNewRomanPSMT; font-size:10px;}</style>
        """
        """<div style="top: 3278px;" id="id699" class="s1">
             <span id="id700" class="s1010">1</span>
             <span id="id701" class="s1045">  The  three  Working  Group  contributions  to  AR6  are:  Climate  Change  2021:  The  Physical  Science  Basis;  Climate  Change  2022: Impacts,  Adaptation  and  Vulnerability;  and  Climate  Change  2022:  Mitigation of  Climate  Change, respectively.  Their  assessments cover scientific literature accepted for publication respectively by 31 January 2021, 1 September 2021 and 11 October 2021. </span>
<!-- sub/super s1010 , normal s1045,
             <span id="id705" class="s1010">2</span>
             <span id="id706" class="s1045"> The three Special Reports are : Global Warming of 1.5&#176;C (2018): an IPCC Special Report on the impacts of global warming of 1.5&#176;C above pre-industrial levels and related global greenhouse gas emission pathways, ...

             pan id="id723" class="s1010">5</span>
             <span id="id724" class="s1045">  Each  finding  is  grounded  in  an evaluation  of underlying  evidence  and  agreement.  A  level of  confidence  is  expressed  using five  qualifiers: very low, low, medium, high and very high, and typeset in italics, for example, </span><span id="id727" class="s1317">medium confidence</span><span id="id728" class="s1045">. The following terms have been used to indicate the assessed likelihood of an outcome or result: virtually certain 99&#8211;100% probability; very likely 90&#8211;100%; likely  66&#8211;100%;  more  likely  than  not  &gt;50-100%;  about  as  likely  as  not  33&#8211;66%;  unlikely  0&#8211;33%;  very  unlikely  0&#8211;10%;  and exceptionally unlikely 0&#8211;1%. Additional terms (extremely likely 95&#8211;100%; more likely than not &gt;50&#8211;100%; and extremely unlikely 0&#8211;5%) are also used when appropriate. Assessed likelihood also is typeset in italics: for example, </span><span id="id733" class="s1317">very likely</span><span id="id734" class="s1045">. This is consistent with AR5. In this Report, unless stated otherwise, square brackets [x to y] are used to provide the assessed </span><span id="id736" class="s1317">very likely</span><span id="id737" class="s1045"> range, or 90% interval. </span>
             """
        package = "LongerReport"
        file = Path(Resources.TEST_IPCC_DIR, package, "fulltext.html")
        html_elem = lxml.etree.parse(str(file)).getroot()
        # font size seem to get rounded up/down
        footnote_text_classes = ["s1045", "s1046",  "s1317"]
        fn_xpath = Footnote.create_footnote_number_xpath(["s1010", "s1469"])
        new_html_elem = Footnote.extract_footnotes(fn_xpath, footnote_text_classes, html_elem)
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "LongerReport")
        outdir.mkdir(exist_ok=True, parents=False)
        XmlLib.write_xml(new_html_elem, str(Path(outdir, "footnotes.html")))
        XmlLib.write_xml(html_elem, str(Path(outdir, "de_footnoted.html")))

    def test_concatenate_equal_classes(self):
        package = "LongerReport"
        file = Path(Resources.TEST_IPCC_DIR, package, "fulltext.html")
        html_elem = lxml.etree.parse(str(file)).getroot()
        divs = html_elem.xpath(".//div")
        for div in divs:
            HtmlTidy.concatenate_spans_with_identical_styles(div)
        outfile = Path(AmiAnyTest.TEMP_HTML_IPCC, "LongerReport", "fulltext_spaced.html")
        XmlLib.write_xml(html_elem, outfile)
        logger.debug(f"write {outfile}")

    def test_remove_footnotes_and_floats_from_fulltext_html_DEVELOP(self):
        """
        combines float removal and footnote removal
        """
        package = "LongerReport"
        file = Path(Resources.TEST_IPCC_DIR, package, "fulltext.html")
        html_elem = lxml.etree.parse(str(file)).getroot()
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, package)
        outdir.mkdir(exist_ok=True, parents=False)

        footnote_text_classes = ["s1045", "s1046", "s1317"]
        fn_xpath = Footnote.create_footnote_number_xpath(["s1010", "s1469"])
        new_html_elem = Footnote.extract_footnotes(fn_xpath, footnote_text_classes, html_elem)
        XmlLib.write_xml(new_html_elem, str(Path(outdir, "footnotes.html")))

        new_new_html_elem = FloatBoundary.extract_floats_and_boundaries(html_elem, package, outdir=outdir)

        XmlLib.write_xml(new_new_html_elem, str(Path(outdir, "de_footnoted_defloated.html")))

    def test_number_paras(self):
        """
        splits numbered sections into paras and adds subnumbers
        """
        package = "LongerReport"
        file = Path(Resources.TEST_IPCC_DIR, package, "de_footnoted_defloated.html")
        html_elem = lxml.etree.parse(str(file)).getroot()
        xpath = "//div[span[@class='s1007']]"
        divs = html_elem.xpath(xpath)
        logger.debug(f"paras {len(divs)}")
        for div in divs:
            span = div.xpath("./span")
            text = span[0].text[:60]
            logger.debug(f"text>> {text}")
            following_divs = list(div.xpath("following::div"))
            # following_divs.insert(0, div)
            following_sections = []
            last_section = None
            for following_div in following_divs:
                spans = following_div.xpath("./span")
                if len(spans) > 0 and spans[0].attrib['class'] == 's1007':
                    last_section = following_div
                    break
                following_sections.append(following_div)
            if last_section is not None:
                # following_divs.pop()
                pass
            logger.info(f"{text} ==> {len(following_sections)}")

    def test_find_paras_with_ids(test):
        """
        test HtmlLib.find_paras_with_ids(html)
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "html", "html_with_ids.html")
        assert 1_300_000 < FileLib.size(infile) < 1_320_000
        html = lxml.etree.parse(str(infile), HTMLParser())
        paras = HtmlLib.find_paras_with_ids(html)
        assert len(paras) >= 1163
        # None returns 0 paras
        paras = HtmlLib.find_paras_with_ids(None)
        assert len(paras) == 0

    def test_para_contains_phrase(test):

        para = lxml.etree.Element("p")
        para.text = "there is a greenhouse gas which"
        phrase = "greenhouse gas"
        contains = HtmlLib.find_and_markup_phrases(para, phrase, ignore_case=True)
        assert contains

        phrase = "greenhouse solid"
        contains = HtmlLib.find_and_markup_phrases(para, phrase, ignore_case=True)
        assert not contains

        phrase = "Greenhouse gas"
        contains = HtmlLib.find_and_markup_phrases(para, phrase, ignore_case=True)
        assert contains

        phrase = "Greenhouse gas"
        contains = HtmlLib.find_and_markup_phrases(para, phrase, ignore_case=False)
        assert not contains


    # outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, package)

    def test_unescape_xml_character_entity_to_unicode(self):
        """
        reads HTML with embedded character entities (e.g. "&#176;")
        uses html.unescape() to convert to Unicode

         """
        # import HTMLParser
        # h = HTMLParser.HTMLParser()
        # h.unescape('&copy; 2010')  # u'\xa9 2010'
        # h.unescape('&#169; 2010')  # u'\xa9 2010'
        import html
        copy = html.unescape('&copy; 2010')
        degrees = html.unescape('&#176; 2010')
        two = 2
        logger.debug(f"\ncopy is {copy} on {two} December 18{degrees}")
        degrees = html.unescape('document &#169; PMR 2022 18&#176;')
        assert degrees == 'document © PMR 2022 18°'

    def test_unescape_xml_entities_old(self):
        """
        """
        # import HTMLParser
        # h = HTMLParser.HTMLParser()
        # h.unescape('&copy; 2010')  # u'\xa9 2010'
        # h.unescape('&#169; 2010')  # u'\xa9 2010'
        import html
        copy = html.unescape('&copy; 2010')
        degrees = html.unescape('&#176; 2010')
        two = 2
        logger.info(f"\ncopy is {copy} on {two} December 18{degrees}")
        degrees = html.unescape('document &#169; PMR 2022 18&#176;')
        assert degrees == 'document © PMR 2022 18°'

    def test_extract_ipcc_bib_pointers(self):
        """
        BEING DEVELOPED
        find biblio refs in HTML
    (Peters et al., 2020; Jackson et al., 2019; Friedlingstein et al., 2020).
    Refactor and generalise to python dict
        """
        # text_has_bracket_xpath = "//div//text()[contains(., '(')]"
        D = "\\d"
        S = "\\s"
        LB = "\\("
        RB = "\\)"
        dictx = {
            "xpath": "foo",
        }
        html_searcher = HTMLSearcher(xpath_dict=dictx)
        descend_with_paren_in_text = "//*[contains(text(), '(')]"
        balanced_brackets = f"{LB}([^{RB}]*){RB}"
        comma_semicolon_chunks = f"{S}*[,;]{S}*"
        dates1920 = f"([A-Z].*{S}+(20|19){D}{D}[a-z]?)"

        in_file = str(Path(Resources.TEST_IPCC_CHAP06, "fulltext.html"))
        html_entity = lxml.etree.parse(in_file)
        html_searcher.add_xpath("text_with_paren", descend_with_paren_in_text)
        html_searcher.add_chunk_re(balanced_brackets)
        html_searcher.add_splitter_re(comma_semicolon_chunks)
        html_searcher.add_subnode_key_re("ref", dates1920)
        html_searcher.set_unmatched_flag(False)

        # use first div paragraph chunk
        div712 = html_entity.xpath("//div[@id='id712']")[0]
        str_un = HtmlLib.convert_character_entities_in_lxml_element_to_unicode_string(div712)

        assert str_un == '<div style="" id="id712"><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 11px;" id="id713">Warming cannot be limited to well below 2°C without rapid and deep reductions in energy system CO</span><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 6px;" id="id715">2</span><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 11px;" id="id716"> and GHG emissions. </span><span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id717">In scenarios limiting likely warming to 1.5°C with limited overshoot (likely below 2°C), net energy system CO</span><span style="font-family: TimesNewRomanPSMT; font-size: 6px;" id="id719">2</span><span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id720"> emissions (interquartile range) fall by 87% to 97%% (60% to 79%) in 2050. In 2030, in scenarios limiting warming to 1.5°C with no or limited overshoot, net CO2 and GHG emissions fall by 35-51% and 38-52% respectively. In scenarios limiting warming to 1.5°C with no or limited overshoot (likely below 2°C), net electricity sector CO</span><span style="font-family: TimesNewRomanPSMT; font-size: 6px;" id="id724">2</span><span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id725"> emissions reach zero globally between 2045 and 2055 (2050 and 2080) </span><span style="font-family: TimesNewRomanPS-ItalicMT; font-size: 11px;" id="id727">(high confidence)</span><span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id728"> {6.7}  </span></div>'
        html_path = Path(Resources.TEST_IPCC_CHAP02, "maintext_old.html")
        html_searcher.search_path_chunk_node(html_path)

    @unittest.skip("uses xml not lxml")
    def test_write_list_of_text_strings_as_html(self):
        """read a list of strings and outout as (X)HTML
        """
        strings = [
            "WG1 physical basis",
            "WG2 adaptation",
            "WG3 mitigation",
        ]
        html = lxml.etree.Element('html')
        head = lxml.etree.SubElement(html, 'head')
        style = lxml.etree.SubElement(head, "style")
        style.text = ".wg1 {color: red;}" \
                     "div {background: cyan;}" \
                     "span {background: pink;} "
        title = lxml.etree.SubElement(head, 'title')
        title.text = "test html"

        body = lxml.etree.SubElement(html, 'body')
        ul = lxml.etree.SubElement(body, "ul")
        for string in strings:
            li = lxml.etree.SubElement(ul, "li")
            li.text = string
            if string.startswith("WG1"):
                li.attrib["class"] = "wg1"
        div = lxml.etree.SubElement(body, "div")
        span = lxml.etree.SubElement(div, "span")
        span.attrib["style"] = "font-size: 10px; color:green;"
        span.text = "The physical basis of climate change"
        span = lxml.etree.SubElement(div, "span")
        span.attrib["style"] = "font-size: 20px; border: blue dotted 1px;"
        span.text = "very important"


        lxml.etree.dump(html)
        path = Path(AmiAnyTest.TEMP_HTML_DIR, "misc", "list.html")
        HtmlLib.write_html_file(html, path)
        assert path.exists()

    def test_get_html_head_style_from_classref(self):
        html = lxml.etree.fromstring(
"""
        <html>
          <head>
            <style>.s1 {font-size: 12px;}</style>
            <style>.s2 {font-size: 14px; font-weight: bold;}</style>
          </head>
          <body>
            <span class="s1">value1</span>
            <span class="s2">value2</span>
          </body>
        </html>
""")
        span1 = html.xpath("/html/body/span[@class='s1']")[0]
        class1 = span1.get("class")
        assert class1 == "s1"
        head_style1 = html.xpath(f"/html/head/style[contains(.,'.{class1} ')]")[0]
        assert lxml.etree.tostring(head_style1).decode("UTF-8").strip() == "<style>.s1 {font-size: 12px;}</style>"
        _, css_style1 = CSSStyle.create_css_style_from_html_head_style_elem(head_style1)
        assert not css_style1.is_bold

        span2 = html.xpath("/html/body/span[@class='s2']")[0]
        css_style2 = HtmlStyle.lookup_head_style_by_classref(span2)
        assert css_style2.is_bold

    def test_jats_to_html_xslt(self):
        """uses PerrJ XSLT to convert to HTML
        """
        lantana_dir = Path(Resources.TEST_RESOURCES_DIR, "plant", "lantana_oil_india")
        xml_dir = Path(lantana_dir, "PMC4535484")
        assert xml_dir.exists()
        fulltext_xml_file = str(Path(xml_dir, "fulltext.xml"))
        fulltext_xml = ET.parse(fulltext_xml_file)
        jats2html_xsl = Path(Resources.RESOURCES_DIR, "xsl", "jats-to-html.xsl")
        assert jats2html_xsl.exists()
        html_out = XmlLib.xslt_transform(fulltext_xml, str(jats2html_xsl))
        assert html_out is not None
        outpath = Path(xml_dir, "fulltext.html")
        HtmlLib.write_html_file(html_out, str(outpath), debug=True)
        assert outpath.exists()


    @unittest.skip("NYI")
    def test_jats_to_html(self):
        """

        """

        test_dir = Path(Resources.TEST_RESOURCES_DIR, "plant", "lantana_oil_india")
        filesx = FileLib.posix_glob(f"{test_dir}/PMC*/sections/1_body")
        if len(filesx) > 0:
            logger.debug(f"intro {len(filesx)}")
        for filex in filesx:
            introductions = FileLib.posix_glob(f"{filex}/**/*introduction*/")
            if len(introductions) > 0:
                print("INTRO")
            # htmlx = HtmlLib.create_html_with_empty_head_body()
            # headh = HtmlLib.get_head(htmlx)
            # bodyh = HtmlLib.get_body(htmlx)
            # backh = lxml.etree.SubElement(bodyh, "back")
            # try:
            #     jats = lxml.etree.parse(file)
            #     front = jats.xpath("/article/front")[0]
            #     body = jats.xpath("/article/body")[0]
            #     back = jats.xpath("/article/back")[0]
            # except Exception as e:
            #     print(f"EXC {e}")
            #     continue
            # # add_children(front, headh)
            # # add_children(body, bodyh)
            # # add_children(back, backh)

    def test_element_to_string(self):
        """
        checks pretty-printing in XmlLib.element_to_string()
        Note we cannot display it here without '\n'
        """
        p_elem = ET.Element("p")
        span = ET.SubElement(p_elem, "span")
        span.text = "text"

        pretty_string = XmlLib.element_to_string(p_elem)
        assert pretty_string == """<p>\n  <span>text</span>\n</p>\n"""

        ugly_string = XmlLib.element_to_string(p_elem, pretty_print=False)
        assert ugly_string == """<p><span>text</span></p>"""

    def test_editor(self):
        """
        create simple HTML object and write to file
        then add child paras and also CSS style (in head)
        """
        editor = HtmlEditor()
        editor.create_skeleton_html()
        editor.write(Path(Resources.TEMP_DIR, "html", "editor_0.html"), debug=True)
        # get complete html object
        html = editor.html
        assert html is not None
        # find body by xpath
        body = editor.html.xpath("body")[0]
        assert body is not None
        # add div to body
        div = ET.SubElement(body, "div")
        # add p as child of div
        p = ET.SubElement(div, "p")
        # add text to p
        p.text = "AMI loves html"
        editor.write(Path(Resources.TEMP_DIR, "html", "editor_1.html"), debug=True)
        # add new paragraph with class
        p1 = ET.SubElement(div, "p")
        p1.text = "paragraph with class=warning"
        # add attribute
        p1.attrib["class"] = "warning"
        editor.write(Path(Resources.TEMP_DIR, "html", "editor_2.html"), debug=True)
        # add <style> to <head> with CSS style
        style = ET.SubElement(editor.head, "style")
        # CSS selector (<p class='warning'> and style
        style.text = "p.warning {background: red;}"
        editor.write(Path(Resources.TEMP_DIR, "html", "editor_warning.html"), debug=True)

    def test_extract_styles_into_stylesheet(self):
        """
        extract list of <head><style> elements into stylesheet
        optionally replace styles by single call to load stylesheet
        """
        html = HtmlLib.parse_html(Path(Resources.TEST_RESOURCES_DIR,
                "ipcc", "cleaned_content", "wg1", "Chapter01", "html_with_ids.html"))
        assert html is not None
        css_file = Path(Resources.TEMP_DIR, "styles", "nested_boxes.css")
        styles = HtmlLib.extract_styles_to_css_file(html, css_file=css_file, link=True)
        assert len(styles) == 19
        assert css_file.exists()

    def test_replace_style_elems_by_css_link(self):
        """
        removes all <style> elements and replaces by <link rel='stylesheet'>
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter01", "html_with_ids.html")
        html = HtmlLib.parse_html(inpath)
        assert html is not None
        css_file = Path(Resources.TEST_RESOURCES_DIR, "styles", "nested_boxes.css")
        styles = HtmlLib.extract_styles_to_css_file(html, css_file=css_file, link=True)
        outfile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter01", "html_with_ids.restyled.html")
        HtmlLib.write_html_file(html, outfile=outfile, debug=True)




def _make_test_elem():
    body = lxml.etree.Element("body")
    body.attrib["id"] = "b"
    d1 = lxml.etree.SubElement(body, "div")
    d1.attrib["id"] = "d1"
    d21 = lxml.etree.SubElement(d1, 'div')
    d21.attrib["id"] = "d21"
    d22 = lxml.etree.SubElement(d1, 'div')
    d22.attrib["id"] = "d22"
    d31 = lxml.etree.SubElement(d21, 'div')
    d31.attrib["id"] = "d31"
    s1 = lxml.etree.SubElement(d31, 'span')
    s1.text = "spantext"
    s1.attrib["id"] = "s1"
    string = lxml.etree.tostring(body).decode("utf-8")
    logger.info(f"string |{string}|")
    if string != """<body id="b"><div id="d1"><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div><div id="d22"/></div></body>""":
        print(f"string: {string}")
    return body



class PDFHTMLTest(AmiAnyTest):

    # def _make_test_elem():
    #     body = lxml.etree.Element("body")
    #     body.attrib["id"] = "b"
    #     d1 = ET.SubElement(body, "div")
    #     d1.attrib["id"] = "d1"
    #     d2 = ET.SubElement(d1, 'div')
    #     d2.attrib["id"] = "d2"
    #     d3 = ET.SubElement(d2, 'div')
    #     d3.attrib["id"] = "d3"
    #     s1 = ET.SubElement(d3, 'span')
    #     s1.text = "spantext"
    #     s1.attrib["id"] = "s1"
    #     assert lxml.etree.tostring(
    #         body) == b'<body id="b"><div id="d1"><div id="d2"><div id="d3"><span id="s1">spantext</span></div></div></div></body>'
    #     return body
    #
    """
    Combine PDF2HTML with styles and other tidy
    Many tests are generic
    """

    @unittest.skipUnless(AmiAnyTest.run_long() and AmiAnyTest.IS_PMR, "run occasionally")
    def test_pdf_to_styled_chapter_15_EXAMPLE(self):
        pdf_args = PDFArgs()
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "Chapter15")
        outpath1 = Path(AmiAnyTest.TEMP_HTML_IPCC, "Chapter15", "fulltext.html")
        maxpage = 30
        style_count = 17
        print_styles = True
        inpath = Path(Resources.TEST_IPCC_CHAP15, "fulltext.pdf")
        style_dict = pdf_args.pdf_to_styled_html_CORE(inpath, maxpage, outdir, outpath1)
        pprint.pprint(f"STYLE {style_dict}")

    @unittest.skipUnless(AmiAnyTest.IS_PMR, "multiple chapter and documents")
    def test_pdf_to_styled_multiple_EXAMPLE(self):
        pdf_args = PDFArgs()
        for chapter in [
            # "Chapter03",
            # "Chapter15",
            "LongerReport",
            # # "wg2_03", # this has performance problems due to vector graphics/boxes
            # "wg2_06",
            # "wg2_spm",
            # "wg3_spm",
        ]:
            outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, chapter)
            outpath1 = Path(AmiAnyTest.TEMP_HTML_IPCC, chapter, "fulltext.html")
            maxpage = 230
            inpath = Path(Resources.TEST_IPCC_DIR, chapter, "fulltext.pdf")
            style_dict = pdf_args.pdf_to_styled_html_CORE(inpath, maxpage, outdir, outpath1)
            pprint.pprint(f"STYLE\n{style_dict}")

    def test_extract_string(self):
        elem = lxml.etree.fromstring("""<div><span>lead A.1.2 rest</span></div>""")
        substrings = HtmlUtil.extract_substrings(elem, xpath='./span',
                                                regex='.*(?P<body>[A-Z]\\.\\d(\\.\\d+)*)', remove=False, add_id=False)
        assert substrings == ["A.1.2"]
        assert lxml.etree.tostring(elem).decode() == "<div><span>lead A.1.2 rest</span></div>"

        elem = lxml.etree.fromstring("""<div><span>lead A.1.2 rest</span></div>""")
        substrings = HtmlUtil.extract_substrings(elem, xpath='./span',
                            regex='(?P<pre>.*)(?P<body>[A-Z]\\.\\d(\\.\\d+)*)(?P<post>.*)', remove=True, add_id=True)
        assert substrings == ["A.1.2"]
        assert lxml.etree.tostring(elem).decode() == '<div><span id="A.1.2">lead  rest</span></div>'
        spans = elem.xpath(".//span[@id='A.1.2']")
        assert len(spans) == 1

        #multiple
        elem = lxml.etree.fromstring("""<div><span>lead A.1.2 rest</span><span>some junk</span><span>lead A.1.3 rest</span></div>""")
        substrings = HtmlUtil.extract_substrings(
            elem, xpath='./span', regex='(?P<pre>.*)(?P<body>[A-Z]\\.\\d(\\.\\d+)*).*', remove=False, include_none=True, add_id=True)
        assert substrings == ["A.1.2", None, "A.1.3"]
        assert XmlLib.are_elements_equal(elem, lxml.etree.fromstring(
            "<div><span id='A.1.2'>lead A.1.2 rest</span><span>some junk</span><span id=\"A.1.3\">lead A.1.3 rest</span></div>"
        )
                                         )
        #multiple
        elem = lxml.etree.fromstring("""
        <div><span>lead A.1.2 rest</span><span>some junk</span><span>lead A.1.3 rest</span></div>""")
        substrings = HtmlUtil.extract_substrings(
            elem, xpath='./span', regex='(?P<pre>.*)(?P<body>[A-Z]\\.\\d(\\.\\d+)*).*', remove=False, add_id=True)
        assert substrings == ["A.1.2", "A.1.3"]
        assert XmlLib.are_elements_equal(elem, lxml.etree.fromstring(
            '<div><span id="A.1.2">lead A.1.2 rest</span><span>some junk</span><span id="A.1.3">lead A.1.3 rest</span></div>'
        )
                                         )

    @unittest.skip("probably obsoledte as depends on old page format")
    def test_extract_ids_page_IPCC(self):
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "page_6.html")
        html_elem = lxml.etree.parse(str(input_html))
        divs = html_elem.xpath(".//div")
        logger.debug(f"divs {len(divs)}")
        section_regex = "(?P<pre>Section\\s*)(?P<body>\\d+)(?P<post>:.*)"
        subsection_regex = "(?P<pre>\\s*)(?P<body>\\d+(\\.\\d+)+)(?P<post>.*)"
        sections, subsections = HtmlGroup.extract_section_ids(
            html_elem, regexes=[section_regex, subsection_regex])
        assert len(sections) == 9
        assert len(subsections) == 0

    @unittest.skip("probably obsoledte as depends on old page format")
    def test_extract_ids_pages_IPCC(self):

        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "total_pages.html")
        html_elem = lxml.etree.parse(str(input_html))
        section_regex = "(?P<pre>Section\\s*)(?P<body>\\d+)(?P<post>:.*)"
        subsection_regex = "(?P<pre>\\s*)(?P<body>\\d+(\\.\\d+)+)(?P<post>.*)"

        sections, subsections = HtmlGroup.extract_section_ids(
            html_elem, regexes=[section_regex, subsection_regex])
        assert sections == ['1', '2', '3', '4', '1', '2', '3', '4']

        assert subsections == [
 '2.1', '2.1.1', '2.1.2',
 '2.2', '2.2.1', '2.2.2', '2.2.3',
 '2.3', '2.3.1', '2.3.2', '2.3.3',
 '3.1', '3.1.1', '3.1.2', '3.1.3',
 '3.2',
 '3.3', '3.3.1', '3.3.2', '3.3.3', '3.3.4',
 '3.4', '3.4.1', '3.4.2',
 '4.1',
 '4.2',
 '4.3',
 '4.4',
 '4.5', '4.5.1', '4.5.2', '4.5.3', '4.5.4', '4.5.5', '4.5.6',
 '4.6',
 '4.7',
 '4.8', '4.8.1', '4.8.2', '4.8.3',
 '4.9',

 '2.1', '2.1.1', '2.1.2',
 '2.2', '2.2.1', '2.2.2', '2.2.3',
 '2.3', '2.3.1', '2.3.2', '2.3.3',
 '3.1', '3.1.1', '3.1.2', '3.1.3',
 '3.2',
 '3.3', '3.3.1', '3.3.2', '3.3.3', '3.3.4',
 '3.4', '3.4.1', '3.4.2',
 '4.1',
 '4.2',
 '4.3',
 '4.4',
 '4.5', '4.5.1', '4.5.2', '4.5.3', '4.5.4', '4.5.5', '4.5.6',
 '4.6',
 '4.7',
 '4.8', '4.8.1', '4.8.2', '4.8.3',
 '4.9']

    @unittest.skip("probably obsoledte as depends on old page format")
    def test_extract_target_links_from_page(self):
        """extracts target ids from trailing {} on sections and paras
        does this still work? extract_section_ids
        """
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "page_16.html")
        html_elem = lxml.etree.parse(str(input_html))
        section_regexes = ["(?P<pre>.*)(?P<body>\\{.*\\})(?P<post>.*)"]
        sections, subsections = HtmlGroup.extract_section_ids(
            html_elem, xpaths=[".//span"], regexes=section_regexes)
        assert len(sections) == 1
        assert len(subsections) == 2


    def test_extract_divs_with_flattened_text_IPCC(self):
        """extract flat text from divs for indexing
        Probably obsolete"""
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "total_pages.html")
        elem = lxml.etree.parse(str(input_html))
        divs = elem.xpath(".//div")
        assert 640 > len(divs) > 630
        rows = []
        for div in divs:
            div_text = div.xpath('string(.//*)')
            print (f"div: {div_text[:10000]}")
            rows.append([HtmlUtil.get_id(div), div_text])


    def test_annotate_pdf_html_page_HACKATHON(self):
        """annotate divs and spans in semi-structured HTML
        The input is usually of the form
        <html><head/><body><div><span/><span/></div><div><span/><span/></div></body></html>
        Typical div
        <div><span>Section 2: Current Status and Trends</span></div>

        """
        p = 16
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", f"page_{p}.html")
        html_elem = lxml.etree.parse(str(input_html)).getroot()
        annotator = HtmlAnnotator.create_ipcc_annotator()
        # annotator.add_head_style(html_elem, )
        HtmlStyle.add_head_styles_orig(html_elem, HtmlGroup.DEFAULT_STYLES)
        spans = html_elem.xpath(".//span")
        for span in spans:
            annotator.run_commands(span)
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", "lr")
        outdir.mkdir(exist_ok=True, parents=True)
        outfile = Path(outdir, f"page_{p}.sections.html")
        with open(outfile, "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_annotate_pdf_html_report_HACKATHON_LONG(self):
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", f"total_pages.html")
        html_elem = lxml.etree.parse(str(input_html)).getroot()
        annotator = HtmlAnnotator.create_ipcc_annotator()
        HtmlStyle.add_head_styles_orig(html_elem, HtmlGroup.DEFAULT_STYLES)
        spans = html_elem.xpath(".//span")
        for span in spans:
            annotator.run_commands(span)
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", "lr")
        outdir.mkdir(exist_ok=True, parents=True)
        outfile = Path(outdir, f"fulltext.annotations.html")
        with open(outfile, "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))
    # IMPORTANT
    @unittest.skipUnless(AmiAnyTest.run_long() and AmiAnyTest.IS_PMR, "run occasionally")
    def test_annotate_spm_reports_HACKATHON(self):
        """uses Annotator approach"""
        reports = [

            "wg1",
            "wg2",
            "wg3",
        ]
        subreport = "spm"
        for report in reports:
            indir = Path(Resources.TEST_IPCC_DIR, report, subreport)
            input_html = Path(indir, f"total_pages.html")
            html_elem = lxml.etree.parse(str(input_html)).getroot()
            annotator = HtmlAnnotator.create_ipcc_annotator()
            HtmlStyle.add_head_styles_orig(html_elem, HtmlGroup.DEFAULT_STYLES)
            spans = html_elem.xpath(".//span")
            for span in spans:
                annotator.run_commands(span)
            outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", report, subreport)
            outdir.mkdir(exist_ok=True, parents=True)
            outfile = Path(outdir, f"fulltext.annotations.html")
            print(f"writing to {outfile}")
            with open(outfile, "wb") as f:
                f.write(lxml.etree.tostring(html_elem, method="html"))

    @unittest.skipUnless(AmiAnyTest.run_long() and AmiAnyTest.IS_PMR, "run occasionally")
    def test_extract_sections_report_HACKATHON_LATEST(self):
        """extract float/s from HTML and copy to custom directories"""
        # stem = "section2mini"
        # stem = "total_pages.manual"
        stem = "total_pages"
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", f"{stem}.html")
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", "syr", "lr")
        outfile = Path(outdir, f"test_{stem}_groups.html")
        HtmlGroup.annotate_div_spans_write_final_html(input_html, outfile)

    # IMPORTANT , CREATES single STATEMENTS
    def test_extract_sections_HACKATHON_LATEST(self):
        """extract sectionns into hierarchical divs"""
        stem = "total_pages"
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", f"{stem}.html")
        html_elem = lxml.etree.parse(str(input_html)).getroot()
        section_regexes = [
            ("section", "Section\\s*(?P<id>\\d):\\s+.*"), # for SYR/LR, not WGS
            ("sub_section", "(?P<id>\\d+\\.\\d+)\\s.*"), # A.1.2
            ("sub_sub_section", "(?P<id>\\d+\\.\\d+\\.\\d+)\\s.*")
        ]
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", "syr", "lr")
        HtmlGroup.make_hierarchical_sections_KEY(html_elem, stem, section_regexes=section_regexes, outdir=outdir)

    # IMPORTANT

    def test_extract_sections_wg123_HACKATHON_LATEST(self):
        """extract sectionns into hierarchical divs
        wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg1/spm/total_pages_styles.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg1/spm/total_pages_groups.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg1/spm/total_pages_statements.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg2/spm/styles1.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg2/spm/total_pages_styles.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg2/spm/total_pages_groups.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg2/spm/total_pages_statements.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/spm/styles1.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/spm/total_pages_styles.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/spm/total_pages_groups.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/spm/total_pages_statements.html

        """
        stem = "total_pages"
        for wg in ["wg1", "wg2", "wg3"]:
            input_html = Path(Resources.TEST_IPCC_DIR, wg, "spm", f"{stem}.html")
            html_elem = lxml.etree.parse(str(input_html)).getroot()
            section_regexes = [
                ("section", "(?P<id>[A-Z])\\.\\s*.*"),
                ("sub_section", "(?P<id>[A-Z]\\.\\d+)\\s.*"),
                ("sub_sub_section", "(?P<id>[A-Z]\\.\\d+\\.\\d+)\\s.*")
            ]
            outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", wg, "spm")
            HtmlGroup.make_hierarchical_sections_KEY(html_elem, stem, section_regexes=section_regexes, outdir=outdir)

    @unittest.skipUnless(AmiAnyTest.run_long() and AmiAnyTest.IS_PMR, "run occasionally")
    def test_extract_sections_report_all_wg_HACKATHON_LATEST(self):
        """create html for all WGs
        starts_with *total_pages.html
        creates *_groups.html files
        """
        stem = "total_pages"
        wgs = [
            # "wg1",
            # "wg2",
            # "wg3",
            "srocc",
            "srccl",
            "sr15",
        ]
        pages = "pages/"   # maybe "" in some dirs


        for wg in wgs:
            input_html = Path(Resources.TEST_IPCC_DIR, f"{wg}", "spm", f"{pages}{stem}.html")
            print(f"\n==========input: {input_html}===============")
            html_elem = lxml.etree.parse(str(input_html)).getroot()
            annotator = HtmlAnnotator.create_ipcc_annotator()
            HtmlStyle.add_head_styles_orig(html_elem, HtmlGroup.DEFAULT_STYLES)
            for span in html_elem.xpath(".//span"):
                annotator.run_commands(span)
            outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", f"{wg}", "spm")
            HtmlLib.write_html_file(html_elem, Path(outdir, f"test_{stem}_pre_groups.html"), debug=True)
            styles = [
            "border : solid purple 2px; margin:2px;",
            "border : dashed green 1.5px; margin:1.5px;",
            "border : dotted blue 1px; margin:1px;",
            ]
            HtmlGroup.group_nested_siblings(html_elem, styles=styles)
            HtmlLib.write_html_file(html_elem, Path(outdir, f"test_{stem}_groups.html"), debug=True)

    # Chapters within Working groups

    # @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    @unittest.skip("IPCC")
    def test_chapter_toolchain_chapters_HACKATHON(self):
        """
        writing XML /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/wg3/Chapter07/pages/page_114.html
writing XML /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/wg3/Chapter07/pages/total_pages.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/Chapter07/styles1.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/Chapter07/groups_styles.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/Chapter07/groups_groups.html
wrote: /Users/pm286/workspace/pyamihtml_top/temp/html/ar6/annotation/wg3/Chapter07/groups_statements.html

        """
        total_pages = "total_pages"
        stem = total_pages
        group_stem = "groups"
        wgs = [
            # "wg1",
            # "wg2",
            "wg3",
            # "srocc",
            # "srccl",
            # "sr15",
        ]
        pages = "pages/"   # maybe "" in some dirs
        chapters = [
            "Chapter07",
            "Chapter08",
            ]

        report_names = [
            "WG3_CHAP07",
            # "WG3_CHAP08",
        ]
        wg = "wg3"
        for report_name in report_names:
            chapter = "Chapter07" if "07" in report_name else "Chapter08"
            report_dict = Resources.WG_REPORTS[report_name]
            print(f"\n==================== {report_name} ==================")
            input_pdf = report_dict["input_pdf"]
            if not input_pdf.exists():
                print(f"cannot find {input_pdf}")
                continue
            output_page_dir = report_dict["output_page_dir"]
            print(f"output dir {output_page_dir}")
            output_page_dir.mkdir(exist_ok=True, parents=True)
            page_json_dir = output_page_dir
            ami_pdfplumber = AmiPDFPlumber(param_dict=report_dict)
            HtmlGenerator.create_html_pages(
                ami_pdfplumber, input_pdf=input_pdf, outdir=output_page_dir, page_json_dir=page_json_dir, debug=True, outstem=total_pages)

            outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", f"{wg}", f"{chapter}")
            outfile = Path(outdir, "fulltext_final.html")
            input_html_path = Path(output_page_dir, f"{total_pages}.html")
            # self.annotate_div_spans_write_final_html(input_html_path, outfile)
            html_elem = lxml.etree.parse(str(input_html_path))
            section_regexes = [
                ("section", "\\s*(?P<id>Table of Contents|Frequently Asked Questions|Executive Summary|References|\\d+\\.\\d+)\\s*.*"),  # 7.1 Introductiom
                ("sub_section", "(?P<id>FAQ \\d+\\.\\d+|\\d+\\.\\d+\\.\\d+)\\s.*"),  # 7.1.2 subtitle or FAQ 7.1 subtitle
                ("sub_sub_section", "(?P<id>\\d+\\.\\d+\\.\\d+\\.\\d+)\\s*.*") # 7.1.2.3 subsubtitle
            ]

            HtmlGroup.make_hierarchical_sections_KEY(html_elem, group_stem, section_regexes=section_regexes, outdir=outdir)

    # TODO bad url
    @unittest.skip("get better URL")
    def test_download_github_html(self):
        github_url = HtmlLib.create_rawgithub_url(
            username="petermr",
            repository="semanticClimate",
            branch="main",
            # filepath="ar6/ar6/syr/lr/total_pages.annotated.html"
            filepath = "ar6/ar6/syr/lr/total_pages.html"
        )
        print(f"github_url {github_url}")
        url_cache = URLCache()
        html_elem = url_cache.read_xml_element_from_github(github_url)
        assert html_elem is not None
        divs = html_elem.xpath("//div")
        assert 640 > len(divs) > 635

    @unittest.skip("MOVE TO UN")
    def test_extract_anchors_initial_TEST_HACKATHON_KEY(self):
        """tests target IDs in SYR/LR in WGI"""
        import requests

        url_cache = URLCache()
        # html_elem = url_cache.read_xml_element_from_github(github_url)

        # anchor_branch, anchor_repository, anchor_stem, anchor_username, link_factory, target_leaf_name, wg_dict = \
        link_factory = LinkFactory.create_default_ipcc_link_factory()

        leaf_name = "fulltext.annotations.id.html"

        anchor_div = lxml.etree.Element("div")
        anchor_div.attrib["id"] = "test_id"
        span_containing_curly_list = lxml.etree.fromstring(
            """<span class="targets"> by &#177;0.2&#176;C. {WGI SPM A.1, WGI SPM A.1.2, WGI SPM A.1.3, WGI SPM A.2.2, WGI Figure SPM.2; SRCCL TS.2} </span>""")
        anchor_div.append(span_containing_curly_list)
        print(f" new div {lxml.etree.tostring(anchor_div)}")
        HtmlLib.write_html_file(anchor_div, Path(AmiAnyTest.TEMP_HTML_IPCC, "misc", "split_a.html"), debug=True)

        IPCCTargetLink.read_links_from_span_and_follow_to_ipcc_repository_KEY(anchor_div, leaf_name, link_factory, span_containing_curly_list)


    @unittest.skip("MOVE TO UN")
    def test_extract_anchors_add_confidence_HACKATHON_KEY(self):
        """ reads whole of SYR/LR after grouping
      Then parses the confidence statements is SYR/LR
        """
        import requests

        url_cache = URLCache()
        link_factory = LinkFactory.create_default_ipcc_link_factory()

        leaf_name = "fulltext.annotations.id.html"
        syr_leaf = f"extract_floats.html"
        syr_stem = "total_pages_groups"
        # syr_stem = f"extract_floats"
        syr_path = Path(Resources.TEST_IPCC_DIR, "syr", "lr", f"{syr_stem}.html")
        syr_lr_html = lxml.etree.parse(str(syr_path)).getroot()
        div = None
        span = None
        divs = syr_lr_html.xpath("//div[span[@class='targets']]")
        assert 204 > len(divs) >= 200, f"expected 202 divs, found len{divs}"
        df = IPCCTargetLink.create_dataframe_from_IPCC_target_ids_in_curly_brackets_divs_KEY(
            divs, leaf_name, link_factory, max_divs=10)
        print(f"DATAFRAME\n{df}")
        Path(AmiAnyTest.TEMP_HTML_IPCC, "syr", "lr").mkdir(exist_ok=True, parents=True)
        path = Path(AmiAnyTest.TEMP_HTML_IPCC, "syr", "lr", f"{syr_stem}_table.csv")
        df.to_csv(str(path))
        print(f" wrote link table {path}")
        path = Path(AmiAnyTest.TEMP_HTML_IPCC, "syr", "lr", f"{syr_stem}_confidence.html")
        HtmlLib.write_html_file(syr_lr_html, outfile=path)

    def test_extract_footnotes_HACKATHON(self):
        """extract footnotes from HTML and copy to custom directories"""
        stem = "section2mini"
        stem = "total_pages.manual"
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", f"{stem}.html")
        html_elem = lxml.etree.parse(str(input_html)).getroot()
        HtmlUtil.extract_footnotes(html_elem, "font-size: 6.0")
        HtmlLib.write_html_file(html_elem, str(Path(AmiAnyTest.TEMP_HTML_IPCC, "syr", "lr", f"{stem}.footnoted.html")))


    def test_add_sub_superscripts_to_page_HACKATHON(self):
        p = 16
        input_html = Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", f"page_{p}.html")
        html_elem = lxml.etree.parse(str(input_html)).getroot()
        annotator = HtmlAnnotator()
        command = AnnotatorCommand(html_class="subscript", script="sub", add_id="sub_|")
        annotator.add_command(command)
        command = AnnotatorCommand(html_class="superscript", script="super", add_id="super_|")
        annotator.add_command(command)
        spans = html_elem.xpath(".//span")
        for span in spans:
            annotator.run_commands(span)
        outdir = Path(AmiAnyTest.TEMP_HTML_IPCC, "annotation", "lr")
        outfile = Path(outdir, f"page_{p}.scripts.html")
        HtmlLib.write_html_file(html_elem, outfile)

    def test_remove_html_attribute(self):
        """removes HTML attribute silently
        """
        elem = lxml.etree.Element('myelem')
        elem.attrib["att"] = "att_val"
        html_s = lxml.etree.tostring(elem).decode("utf-8")
        assert html_s == '<myelem att="att_val"/>'
        # remove exisying attribute
        HtmlUtil.remove_attribute(elem, "att")
        html_s = lxml.etree.tostring(elem).decode("utf-8")
        assert html_s == '<myelem/>'
        # remove non-existent attribute - no crash
        HtmlUtil.remove_attribute(elem, "foo")
        # check None values do not cause crash
        HtmlUtil.remove_attribute(elem, None)
        elem = None
        HtmlUtil.remove_attribute(elem, "foo")


    def test_remove_single_child_div_from_nesting(self):
        """removes divs from web pages which have no semantic purpose
        Example:
            <div id="d1">
              <div id="d2">
                <span id="s1">blah</span>
              </div>
            </div>
            a2 is playing no role in grouping, so can be removed to give:
            <div id="d1">
              <span id="s1">blah</span>
            </div>
            This can be recursive but spans should always have div parents
        """

        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        # now remove
        # removable_div_xpath = "//div[count(*)=1 and count(*)=1 and parent::div]"
        # elems = body.xpath(removable_div_xpath)
        # assert len(elems) == 2

        HtmlUtil.remove_element_in_hierarchy(d1)
        assert lxml.etree.tostring(body).decode("utf-8") == \
               '<body id="b"><div id="d22"/><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div></body>'

        body = _make_test_elem()
        d2 = body.xpath("//*[@id='d22']")[0]
        HtmlUtil.remove_element_in_hierarchy(d2)
        decode = lxml.etree.tostring(body).decode("utf-8")
        assert decode == '<body id="b"><div id="d1"><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div></div></body>'

        # remove both elements in various orders
        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        d2 = body.xpath("//*[@id='d22']")[0]
        HtmlUtil.remove_element_in_hierarchy(d2)
        HtmlUtil.remove_element_in_hierarchy(d1)
        assert lxml.etree.tostring(body).decode("utf-8") == \
               '<body id="b"><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div></body>'

        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        d2 = body.xpath("//*[@id='d22']")[0]
        HtmlUtil.remove_element_in_hierarchy(d1)
        HtmlUtil.remove_element_in_hierarchy(d2)
        assert lxml.etree.tostring(body).decode("utf-8") == \
               '<body id="b"><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div></body>'

        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        d3 = body.xpath("//*[@id='d31']")[0]
        HtmlUtil.remove_element_in_hierarchy(d1)
        HtmlUtil.remove_element_in_hierarchy(d3)
        assert lxml.etree.tostring(body).decode("utf-8") == \
               '<body id="b"><div id="d22"/><div id="d21"><span id="s1">spantext</span></div></body>'

        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        d3 = body.xpath("//*[@id='d31']")[0]
        HtmlUtil.remove_element_in_hierarchy(d3)
        HtmlUtil.remove_element_in_hierarchy(d1)
        assert lxml.etree.tostring(body).decode("utf-8") == \
               '<body id="b"><div id="d22"/><div id="d21"><span id="s1">spantext</span></div></body>'


    def test_remove_multiple_child_div_from_nesting(self):
        """removes divs from web pages which have no semantic purpose
        Example:
            <div id="d1">
              <div id="d2">
                <span id="s1">blah</span>
              </div>
            </div>
            d2 is playing no role in grouping, so can be removed to give:
            <div id="d1">
              <span id="s1">blah</span>
            </div>
            This can be recursive but spans should always have div parents
        """
        body = _make_test_elem()
        d1 = body.xpath("//*[@id='d1']")[0]
        # now remove
        removable_div_xpath = "//div[count(*)=1 and count(*)=1 and parent::div]"
        elems = body.xpath(removable_div_xpath)
        assert len(elems) == 2

        HtmlUtil.remove_element_in_hierarchy(d1)
        assert lxml.etree.tostring(body).decode(encoding="UTF-8") == '<body id="b"><div id="d22"/><div id="d21"><div id="d31"><span id="s1">spantext</span></div></div></body>'

    def test_find_single_child_divs(self):
        """
        find all divs with single child element
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", "wg1", "edited_toplevel.html")
        html_elem = HtmlLib.parse_html(inpath)

        single_child_divs = HtmlLib.find_single_child_divs(html_elem)
        classes = [div.get("class") for div in single_child_divs]
        assert len(classes) == 115
        assert classes[:20] == [
            None,
            None,
            None,
            'header__content pt-4',
            'home-top homepage',
            'container',
            'col-lg-4 col-sm-6 col-12',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'dropdown',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'col-lg-4 col-sm-6 col-12',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'dropdown',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'col-lg-4 col-sm-6 col-12',
            'mt-auto gap-2 d-flex flex-row align-items-center pb-1',
            'mt-auto gap-2 d-flex flex-column align-items-center',
            'dropdown',
            ]

        print(f"classes {classes}")

    def test_remove_selected_elements_in_hierarchy(self):
        """
        read wg1/toplevel page and remove single-child divs
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", "wg1", "edited_toplevel.html")
        html_elem = HtmlLib.parse_html(inpath)
        HtmlLib.remove_single_child_divs_in_hierarchy(html_elem)
        outfile = Path(Resources.TEMP_DIR, "ipcc", "wg1", "stripped_toplevel.html")
        HtmlLib.write_html_file(html_elem, outfile, debug=True)
        assert outfile.exists()



class HtmlTidyTest(AmiAnyTest):

    def test_html_good(self):
        """
        ensures valid html will pass
        """
        # ideal file html-head-body
        html_ideal = """
        <html>
          <!-- ideal file -->
          <head>
          </head>
          <body>
            <ul>
              <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
              <li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
            </ul>
          </body>
        </html>
            """
        html_raw = lxml.etree.fromstring(html_ideal)
        html_new = HtmlTidy._ensure_html_root(html_raw)
        assert len(html_new.xpath("/html")) == 1
        assert len(html_new.xpath("/*/html")) == 0

    def test_html_ok(self):
        """
        various allowable but non-ideal html
        """
        # ok file html-body
        html_body_only = """
        <html>
          <!-- no head -->
          <body>
            <ul>
              <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
              <li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
            </ul>
          </body>
        </html>
            """
        html_raw = lxml.etree.fromstring(html_body_only)
        html_new = HtmlTidy._ensure_html_root(html_raw)
        assert len(html_new.xpath("/html")) == 1
        assert len(html_new.xpath("/*/html")) == 0

        # ok file html-no-body
        html_body_only = """
        <html>
          <!-- no head -->
          <ul>
            <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
            <li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li>
          </ul>
        </html>
            """
        html_raw = lxml.etree.fromstring(html_body_only)
        html_new = HtmlTidy._ensure_html_root(html_raw)
        assert len(html_new.xpath("/html")) == 1
        assert len(html_new.xpath("/*/html")) == 0

    def test_wrap_element_html(self):
        """
        wraps element in <html>. Adds <head> and <body>
        """
        # no html head and implied body
        html_body_only = """<ul><li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li><li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li></ul>
            """
        html_raw = lxml.etree.fromstring(html_body_only)
        html_new = HtmlTidy.ensure_html_head_body(html_raw)
        assert len(html_new.xpath("/html")) == 1
        assert len(html_new.xpath("/html/head")) == 1
        assert len(html_new.xpath("/html/body")) == 1
        html_s = lxml.etree.tostring(html_new).decode('UTF-8')
        assert """<html><head/><body><ul><li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li><li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li></ul></body></html>""" == html_s, f"found {html_s}"

        # html but no explicit head and or body; wraps p, ul in body and wraps style in head
        html_only = """<html><style>p {color: green}</style><p>should be green</p><ul><li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li><li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li></ul></html>"""
        html_raw = lxml.etree.fromstring(html_only)
        html_new = HtmlTidy.ensure_html_head_body(html_raw)
        assert len(html_new.xpath("/html")) == 1
        assert len(html_new.xpath("/html/head")) == 1
        assert len(html_new.xpath("/html/body")) == 1
        html_s = lxml.etree.tostring(html_new).decode('UTF-8')
        assert """<html><head><style>p {color: green}</style></head><body><p>should be green</p><ul><li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li><li style="font-family: monospace; font-size: 13px; color: blue; left: 10px;">foo</li></ul></body></html>""" == html_s, f"found {html_s}"
        # for display
        html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        path = Path(html_dir, "html_only.html")
        HtmlLib.write_html_file(lxml.etree.fromstring(html_only), path)
        html_h = lxml.etree.fromstring(html_s)
        HtmlLib.write_html_file(html_h, Path(html_dir, "html_tidied.html"))

    def test_normalize_pdf2html_ipcc(self):
        """
        output of pdf2html normalized to have head and body
        """
        html_elem = lxml.etree.parse(str(MINI_IPCC_PATH))
        html_tidy_elem = HtmlTidy.ensure_html_head_body(html_elem)
        path = Path(AmiAnyTest.TEMP_DIR, "html", "tidy_mini.html")
        XmlLib.write_xml(html_tidy_elem, path)

TEST_HEAD = """<html><head>
<style>
        div {border: red solid 1px; margin: 1px;}
        span {background: #eeeeee; margin: 1px;}
        div.float {background: #ddffff;}
                     </style>

<style classref="div">div {border : red solid 0.5px}</style>
<style classref="span">span {border : blue dotted 0.5px}</style>
<style classref=".s0">.s0 {font-family: FrutigerLTProCn; font-size: 28.0; font-weight: Bold;}</style>
<style classref=".s10">.s10 {font-family: FrutigerLTPro-LightCn; font-size: 8.0;}</style>
<style classref=".s11">.s11 {font-family: FrutigerLTPro-LightCnIta; font-size: 8.0;}</style>
<style classref=".s16">.s16 {font-family: FrutigerLTPro-Condensed; font-size: 10.0;}</style>
<style classref=".s369">.s369 {font-family: Calibri; font-size: 9.5;}</style>
<style classref=".s666">.s666 {font-family: SymbolMT; font-size: 9.5;}</style>
<style classref=".s1000">.s1000 {font-family: FrutigerLTPro-Condensed; font-size: 9.5;}</style>
<style classref=".s1020">.s1020 {font-family: FrutigerLTPro-BlackCn; font-size: 9.5;}</style>
<style classref=".s1184">.s1184 {font-family: FrutigerLTPro-CondensedIta; font-size: 5.54;}</style>
<style classref=".s2726">.s2726 {font-family: Calibri-Italic; font-size: 9.5; font-style: italic;}</style>
<style classref=".s5690">.s5690 {font-family: FrutigerLTPro-Condensed; font-size: 8.5;}</style>
<style classref=".s5778">.s5778 {font-family: MyriadPro-Regular; font-size: 8.59;}</style></head></html>"""


class CSSStyleTest(AmiAnyTest):

    def test_extract_character_style(self):
        """
        Test extract character info and separate the rest
        creates 2 substyles
        """
        css = CSSStyle.create_css_style_from_css_string(
            "font-weight: bold; font-family: monospace; font-size: 13px; color: blue; bottom: 10px;")
        (extracted, retained) = font_style, rest_style = css.extract_substyles(
            [CSSStyle.FONT_STYLE, CSSStyle.FONT_WEIGHT, CSSStyle.FONT_FAMILY, CSSStyle.FONT_SIZE, CSSStyle.COLOR])
        assert type(extracted) is CSSStyle
        assert type(retained) is CSSStyle
        assert extracted == CSSStyle.create_css_style_from_css_string(
            "font-weight: bold; font-family: monospace; font-size: 13px; color: blue;")
        assert retained == CSSStyle.create_css_style_from_css_string("bottom: 10px")

    def test_extract_text_styles(self):
        """
        Extracts named styled components from string into new styles and creates HtmlStyle
        """
        css = CSSStyle.create_css_style_from_css_string(
            "font-weight: bold; font-family: monospace; font-size: 13px; color: blue; bottom: 10px;")
        extracted_style, retained_style = css.extract_text_styles()
        assert extracted_style == CSSStyle.create_css_style_from_css_string(
            "font-weight: bold; font-family: monospace; font-size: 13px; color: blue;")
        assert retained_style == CSSStyle.create_css_style_from_css_string("bottom: 10px")

    def test_extract_text_styles_into_html_style(self):
        """
        Extracts text style components into new <style>, updated class, remaining style value
        """
        css = CSSStyle.create_css_style_from_css_string(
            "font-weight: bold; font-family: monospace; font-size: 13px; color: blue; bottom: 10px;")
        class_name = "s1"
        old_class_name = "foo bar"
        new_html_style_element, retained_style_string, html_class_val = \
            css.extract_text_styles_into_class(class_name, old_classstr=old_class_name)
        assert new_html_style_element.text == ".s1 {font-weight: bold; font-family: monospace; font-size: 13px; color: blue;}"
        assert retained_style_string == "bottom: 10px;"
        assert html_class_val == "foo bar s1"

        #
        # assert ext_s == "<style>l1 {font-weight: bold; font-family: monospace; font-size: 13px; color: blue;}</style>", f"found {ext_s}"
        # ret_s = lxml.etree.tostring(retained_style_element).decode("UTF-8")
        # assert ret_s == "bottom: 10px;", f"found {ret_s}"

    def test_extract_many_text_styles_into_html_style(self):
        """
        Extracts named styled components into new styles with classrefs and creates HtmlStyle
        """
        html_s = """
        <html>
          <head>
            <style>.pink {background-color: pink;}</style>
          </head>
          <body>
            <ul>
              <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">13px bold</li>
              <li class="pink" style="font-family: monospace; font-size: 30px; color: purple; left: 10px;">purple on pink background</li>
              <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">bold blue</li>
              <li style="font-style: italic; font-family: monospace; font-size: 20px; color: red; left: 10px;">italic red</li>
              <li style="font-weight: bold; font-family: monospace; font-size: 13px; color: blue; left: 10px;">same as 3</li>
            </ul>
          </body>
        </html>
            """
        html_elem = lxml.etree.fromstring(html_s)
        html_elem = HtmlTidy.ensure_html_head_body(html_elem)  # redundant as tidy already
        HtmlStyle.extract_all_style_attributes_to_head(html_elem)
        html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        html_dir.mkdir(exist_ok=True)
        outpath = Path(html_dir, "styles.html")
        with open(str(outpath), "w", encoding="UTF-8") as f:
            f.write(lxml.etree.tostring(html_elem, method="html").decode('UTF-8'))
            logger.info(f"wrote style file to {outpath}")
            print(f"(logger) wrote style file to {outpath}")

    def test_extract_styles_from_mini_document_example(self):
        """
        starts with tidied html
        start of IPCC WG3 Chapter06
        identifies all styles and extacts into <head><style>s and replaces @style with @class
        """
        html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        html_dir.mkdir(exist_ok=True)
        html_elem = lxml.etree.parse(str(MINI_IPCC_PATH))
        html_elem = HtmlTidy.ensure_html_head_body(html_elem)
        assert len(html_elem.xpath("/html/head/style")) == 0, f"no head styles in original"
        assert len(html_elem.xpath("/html/body//*[not(normalize-space(@style))='']")) == 50, \
            f"raw document should have 50 elements with non-empty @style attributes"
        # this is so HTML browsers can see the initial file
        with open(str(Path(html_dir, "ipcc_styles0.html")), "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))

        HtmlStyle.extract_styles_and_normalize_classrefs(html_elem)

        outpath = str(Path(html_dir, "ipcc_styles_voloured.html"))
        with open(outpath, "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))
            print(f"(logger) output to {outpath}")

        assert len(html_elem.xpath("/html/head/style")) == 7, f"7 head styles"
        assert len(html_elem.xpath("/html/body//*[@class]")) == 51, \
            f"new document should have 51 elements with @class attributes"

    def test_extract_normalize_styles_old_chapter_4_EXAMPLE(self):
        """
        Old chapter still with header/footer.
        example mainly to find styles
        """
        output_html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        output_html_dir.mkdir(exist_ok=True)
        html_elem = lxml.etree.parse(str(Path(Resources.TEST_IPCC_CHAP04, "fulltext_old.html")))
        html_elem = HtmlTidy.ensure_html_head_body(html_elem)
        assert len(html_elem.xpath("/html/head/style")) == 0, f"no head styles in original"
        assert len(html_elem.xpath("/html/body//*[not(normalize-space(@style))='']")) == 2302, \
            f"raw document should have 50 elements with non-empty @style attributes"
        # this is so HTML browsers can see the initial file
        with open(str(Path(output_html_dir, "ipcc_fulltext_styles0.html")), "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))

        HtmlStyle.extract_styles_and_normalize_classrefs(html_elem)

        with open(str(Path(output_html_dir, "ipcc_chap4_fulltext_styles2.html")), "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))

        assert len(html_elem.xpath("/html/head/style")) == 23, f"23 head styles"
        assert len(html_elem.xpath("/html/body//*[@class]")) == 2304, \
            f"new document should have 2304 elements with @class attributes"
        assert len(html_elem.xpath("/html/body//*[contains(@class,'dec')]")) == 0, \
            f"new document should have 0 elements with @class attributes containing 'dec1', 'dec2' etc."

    def test_extract_normalize_styles_old_chapter_17_example(self):
        """
        starts with "fulltext.html" and converts to "fulltext_styles.html"
        Old chapter still with header/footer.
        example mainly to find styles
        """
        input_path = Path(Resources.TEST_IPCC_CHAP17, "fulltext.html")
        html_elem = lxml.etree.parse(str(input_path))
        html_elem = HtmlTidy.ensure_html_head_body(html_elem)
        HtmlStyle.extract_styles_and_normalize_classrefs(html_elem)

        temp_dir = Path(AmiAnyTest.TEMP_HTML_DIR, "ar6", "chapter17")
        temp_dir.mkdir(exist_ok=True, parents=True)
        with open(str(Path(temp_dir, "fulltext_styles.html")), "wb") as f:
            f.write(lxml.etree.tostring(html_elem, method="html"))

        assert len(html_elem.xpath("/html/head/style")) == 13, f"13 head styles"
        assert len(html_elem.xpath("/html/body//*[@class]")) == 1330, \
            f"new document should have 2304 elements with @class attributes"
        assert len(html_elem.xpath("/html/body//*[contains(@class,'dec')]")) == 0, \
            f"new document should have 0 elements with @class attributes containing 'dec1', 'dec2' etc."

    def test_css_parse(self):
        css_str = "height: 22; width: 34;"
        css_style = CSSStyle.create_dict_from_name_value_array_string(css_str)
        assert css_style
        assert "height" in css_style
        assert css_style.get("height") == "22"
        assert "width" in css_style
        assert css_style.get("width") == "34"

    def test_css_parse_with_curlies(self):
        css_str = "{height: 22; width: 34;}"
        css_style = CSSStyle.create_dict_from_name_value_array_string(css_str, )
        assert css_style
        assert "height" in css_style
        assert css_style.get("height") == "22"
        assert "width" in css_style
        assert css_style.get("width") == "34"


    def test_make_style_dict_from_html(self):
        """
        extracts <style> elements into a Python dic
        """
        html_str = """
        <html>
          <head>
            <style>.s0 {font-size:14 px; stroke: blue;}</style>
            <style>.s1 {font-size:10 px; fill: red;}</style>
            <style>.s2 {font-size:8 px; border: solid 1 px;}</style>
          </head>
          <body/>
        </html>
          """
        styles = CSSStyle.extract_styles_from_html_string(html_str)
        style_dict = CSSStyle.create_style_dict_from_styles(style_elems=styles)
        assert ".s1" in style_dict.keys()
        assert 'font-size:10 px; fill: red;' == style_dict[".s1"]

    def test_validate_html_styles_ERRORS(self):
        """
        try to create style_dict from invalid content. Should raise errors
        """
        duplicate_css_ref = """ 
        <html>
          <head>
            <style>.s0 {font-size:14 px; stroke: blue;}</style>
            <style>.s1 {font-size:10 px; fill: red;}</style>
            <style>.s0 {font-size:8 px; border: solid 1 px;}</style>
          </head>
          <body/>
        </html>
"""
        styles = CSSStyle.extract_styles_from_html_string(duplicate_css_ref)
        try:
            style_dict = CSSStyle.create_style_dict_from_styles(style_elems=styles)
        except ValueError as e:
            assert str(e) == "duplicate style ref .s0 {font-size:8 px; border: solid 1 px;}"

        missing_dot = """ 
        <html>
          <head>
            <style>.s0 {font-size:14 px; stroke: blue;}</style>
            <style>.s1 {font-size:10 px; fill: red;}</style>
            <style>s2 {font-size:8 px; border: solid 1 px;}</style>
          </head>
          <body/>
        </html>
"""
        styles = CSSStyle.extract_styles_from_html_string(missing_dot)
        try:
            style_dict = CSSStyle.create_style_dict_from_styles(style_elems=styles)
        except ValueError as e:
            assert str(e) == "BAD head_style s2 {font-size:8 px; border: solid 1 px;}"

        bad_css = """ 
        <html>
          <head>
            <style>.s0 {font-size:14 px; stroke: blue;}</style>
            <style>.s1 {font-size:10 px; fill: red;}</style>
            <style>.s2 {font-size:8 px border: solid 1 px;}</style>
          </head>
          <body/>
        </html>
"""
        styles = CSSStyle.extract_styles_from_html_string(bad_css)
        try:
            style_dict = CSSStyle.create_style_dict_from_styles(style_elems=styles)
        except KeyError as e:
            assert str(e) == "'bad style font-size:8 px border: solid 1 px in CSS: font-size:8 px border: solid 1 px;'"

    def test_extract_styles_from_html_style(self):
        """empirically uses fontnames to create styles for weight, styles, stretch, colour
        """
        test_head = """<html><head>
<style>
        div {border: red solid 1px; margin: 1px;}
        span {background: #eeeeee; margin: 1px;}
        div.float {background: #ddffff;}
                     </style>

<style classref="div">div {border : red solid 0.5px}</style>
<style classref="span">span {border : blue dotted 0.5px}</style>
<style classref=".s0">.s0 {font-family: FrutigerLTProCn; font-size: 28.0; font-weight: Bold;}</style>
<style classref=".s10">.s10 {font-family: FrutigerLTPro-LightCn; font-size: 8.0;}</style>
<style classref=".s11">.s11 {font-family: FrutigerLTPro-LightCnIta; font-size: 8.0;}</style>
<style classref=".s16">.s16 {font-family: FrutigerLTPro-Condensed; font-size: 10.0;}</style>
<style classref=".s369">.s369 {font-family: Calibri; font-size: 9.5;}</style>
<style classref=".s666">.s666 {font-family: SymbolMT; font-size: 9.5;}</style>
<style classref=".s1000">.s1000 {font-family: FrutigerLTPro-Condensed; font-size: 9.5;}</style>
<style classref=".s1020">.s1020 {font-family: FrutigerLTPro-BlackCn; font-size: 9.5;}</style>
<style classref=".s1184">.s1184 {font-family: FrutigerLTPro-CondensedIta; font-size: 5.54;}</style>
<style classref=".s2726">.s2726 {font-family: Calibri-Italic; font-size: 9.5; font-style: italic;}</style>
<style classref=".s5690">.s5690 {font-family: FrutigerLTPro-Condensed; font-size: 8.5;}</style>
<style classref=".s5778">.s5778 {font-family: MyriadPro-Regular; font-size: 8.59;}</style></head></html>"""

        html_elem = lxml.etree.fromstring(TEST_HEAD)
        html_styles = html_elem.xpath("/html/head/style")
        assert len(html_styles) == 15
        style_elem = html_elem.xpath("/html/head/style[contains(., 'FrutigerLTProCn;')]")[0]
        classref,cssstring = HtmlStyle.extract_classref_and_cssstring_from_style_text(style_elem.text)
        assert classref == ".s0"
        assert cssstring == "font-family: FrutigerLTProCn; font-size: 28.0; font-weight: Bold;"
        classref,cssstring = HtmlStyle.extract_classref_and_cssstring_from_html_style(style_elem)
        assert classref == ".s0"
        assert cssstring == "font-family: FrutigerLTProCn; font-size: 28.0; font-weight: Bold;"

        table = HtmlStyle.create_classref_cssstring_table(html_styles)
        assert table == [('div', 'border: red solid 1px; margin: 1px;'),
 ('div', 'border : red solid 0.5px'),
 ('span', 'border : blue dotted 0.5px'),
 ('.s0', 'font-family: FrutigerLTProCn; font-size: 28.0; font-weight: Bold;'),
 ('.s10', 'font-family: FrutigerLTPro-LightCn; font-size: 8.0;'),
 ('.s11', 'font-family: FrutigerLTPro-LightCnIta; font-size: 8.0;'),
 ('.s16', 'font-family: FrutigerLTPro-Condensed; font-size: 10.0;'),
 ('.s369', 'font-family: Calibri; font-size: 9.5;'),
 ('.s666', 'font-family: SymbolMT; font-size: 9.5;'),
 ('.s1000', 'font-family: FrutigerLTPro-Condensed; font-size: 9.5;'),
 ('.s1020', 'font-family: FrutigerLTPro-BlackCn; font-size: 9.5;'),
 ('.s1184', 'font-family: FrutigerLTPro-CondensedIta; font-size: 5.54;'),
 ('.s2726', 'font-family: Calibri-Italic; font-size: 9.5; font-style: italic;'),
 ('.s5690', 'font-family: FrutigerLTPro-Condensed; font-size: 8.5;'),
 ('.s5778', 'font-family: MyriadPro-Regular; font-size: 8.59;')]

    def test_extract_styles_from_font_name(self):
        """extracts weight/style from name"""
        cssstring = 'font-family: Helvetica; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 1 {cssstyle.name_value_dict}")
        assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-size': '8.0', 'x0': '23.4', 'font-name': 'Helvetica', 'font': 'sans'}

        cssstring = 'font-family: HelveticaBold; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 2 {cssstyle.name_value_dict}")
        assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-size': '8.0', 'x0': '23.4', 'font-name': 'HelveticaBold', 'font': 'sans', 'font-weight': 'bold'}

        cssstring = 'font-family: HelveticaItalic; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 3 {cssstyle.name_value_dict}")
        assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-size': '8.0', 'x0': '23.4', 'font-name': 'HelveticaItalic', 'font': 'sans', 'font-style': 'italic'}

        cssstring = 'font-family: HelveticaBoldItalic; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 4 {cssstyle.name_value_dict}")
        assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-size': '8.0', 'x0': '23.4', 'font-name': 'HelveticaBoldItalic', 'font': 'sans', 'font-weight': 'bold', 'font-style': 'italic'}



        # this isn't a real font but we can parse it
        cssstring = 'font-family: HelveticaItalicBold; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 5 {cssstyle.name_value_dict}")
        # assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-name': 'None', 'font-size': '8.0',
        #                                     'x0': '23.4', 'font': 'sans', 'font-style': 'italic', 'font-weight': 'bold'}

        # this isn't a real font but we can parse it
        cssstring = 'font-family: Foo-Bold; font-size: 8.0; x0: 23.4;'
        cssstyle = AmiFont.create_font_edited_style_from_css_style_object(cssstring)
        print(f"dict 6 {cssstyle.name_value_dict}")
        # assert cssstyle.name_value_dict == {'font-family': 'Helvetica', 'font-name': 'None', 'font-size': '8.0',
        #                                     'x0': '23.4', 'font': 'sans', 'font-style': 'italic', 'font-weight': 'bold'}

    def test_extract_styles_from_font_names(self):
        font_css_list = [
            ["FrutigerLTProCn", {'font': 'sans', 'font-family': 'FrutigerLTPro', 'font-name': 'FrutigerLTProCn', 'font-stretched': 'narrow'}],
            ["FrutigerLTPro-LightCn", {'font': 'sans', 'font-family': 'FrutigerLTPro', 'font-name': 'FrutigerLTPro-LightCn',
                                       'font-stretched': 'narrow', 'font-weight': 'light'}],
            ["FrutigerLTPro-LightCnIta", {'font': 'sans', 'font-family': 'FrutigerLTPro', 'font-name': 'FrutigerLTPro-LightCnIta',
                                          'font-stretched': 'narrow','font-style': 'italic', 'font-weight': 'light'}],
            ["FrutigerLTPro-Condensed", {'font': 'sans', 'font-family': 'FrutigerLTPro', 'font-name': 'FrutigerLTPro-Condensed',
                                         'font-stretched': 'narrow'}],
            ["Calibri", {'font': 'sans', 'font-family': 'Calibri', 'font-name': 'Calibri'}],
            ["SymbolMT", {'font': 'sans', 'font-family': 'SymbolMT', 'font-name': 'SymbolMT'}],
            ["FrutigerLTPro-BlackCn", {'font': 'sans', 'font-family': 'FrutigerLTPro', 'font-name': 'FrutigerLTPro-BlackCn',
                                       'font-stretched': 'narrow', 'font-weight': 'bold'}],
            ["Calibri-Italic", {'font': 'sans', 'font-family': 'Calibri', 'font-name': 'Calibri-Italic', 'font-style': 'italic'}],
            ["MyriadPro-Regular", {'font': 'sans', 'font-family': 'MyriadProRegular', 'font-name': 'MyriadPro-Regular'}],
        ]
        for f in font_css_list:
            assert len(f) == 2
            cssstyle = AmiFont.create_font_edited_style_from_css_style_object(f"font-family: {f[0]}")
            assert cssstyle.name_value_dict == f[1]

    def test_tinycss(self):
        import tinycss
        parser = tinycss.make_parser('page3')
        stylesheet = parser.parse_stylesheet_bytes(b'''@import "foo.css";
        ...     p.error { color: red }  @lorem-ipsum;
        ...     @page tables { size: landscape }''')
        print(f"stylesheet {stylesheet.__dir__()}")
        print(f"stylesheet.rules {stylesheet.rules}")
        for rule in stylesheet.rules:
            print(f"rule {rule}: {rule.__dir__}")

    def test_analyze_styles(self):
        """extracts styles from an already normalised styled document and summarise them"""
        for input_html in [
            lxml.etree.parse(str(Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "total_pages.html"))),
            lxml.etree.parse(str(Path(Resources.TEST_IPCC_DIR, "wg1", "glossary.html"))),
        ]:
            print(f"=\n====== {input_html} ========")
            HtmlUtil.analyze_styles(input_html)

    def test_analyze_coords(self):
        input_html_files = [
            Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "total_pages.html"),
            Path(Resources.TEST_IPCC_DIR, "wg1", "glossary.html"),
        ]

        for path in input_html_files:
            print(f"\n======= {path} ========")
            input_html = lxml.etree.parse(str(path))
            analyze = HtmlUtil.analyze_coordinates
            analyze(input_html)
            print(f"============================================")

    def test_analyze_coords_styles(self):
        input_html_files = [
            Path(Resources.TEST_IPCC_DIR, "syr", "lr", "pages", "total_pages.html"),
            Path(Resources.TEST_IPCC_DIR, "wg1", "glossary.html"),
        ]
        analysers = [
            HtmlUtil.analyze_coordinates,
            HtmlUtil.analyze_styles,
        ]

        for path in input_html_files:
            print(f"\n======= {path} ========")
            input_html = lxml.etree.parse(str(path))
            for analyzer in analysers:
                print(f"--------------{analyzer.__name__}-------------")
                analyzer(input_html)
                print(f"-------------------------------------")
            print(f"\n============================================")


class HtmlClassTest(AmiAnyTest):
    """

    """

    def test_minimal(self):
        """
        empty HtmlClass object
        """
        html_class = HtmlClass()
        assert html_class.classes == set()
        assert html_class.class_string == ""
        assert not html_class.has_class("foo")

    def test_single_class(self):
        """
        HtmlClass object with single class
        """
        html_class = HtmlClass("foo")
        assert html_class.classes == {"foo"}
        assert html_class.class_string == "foo"
        assert html_class.has_class("foo")

    def test_multiple_class(self):
        """
        HtmlClass object with multiple classes
        """
        html_class = HtmlClass("foo bar")
        assert html_class.classes == {"foo", "bar"}
        assert html_class.class_string == "bar foo"
        assert html_class.has_class("foo")
        assert html_class.has_class("bar")

    def test_add_class(self):
        """
        add classes to HtmlClass object
        """
        html_class = HtmlClass("")
        html_class.add_class("foo")
        assert html_class.classes == {"foo"}
        html_class.add_class("bar")
        assert html_class.classes == {"foo", "bar"}
        assert html_class.class_string == "bar foo"
        assert html_class.has_class("foo")
        assert html_class.has_class("bar")

    def test_remove_class(self):
        """
        remove classes from HtmlClass object
        """
        html_class = HtmlClass("foo bar")
        assert html_class.has_class("foo")
        assert html_class.has_class("bar")

        html_class.remove("foo")
        assert html_class.classes == {"bar"}
        assert not html_class.has_class("foo")
        assert html_class.has_class("bar")

        html_class.add_class("foo")
        assert html_class.classes == {"foo", "bar"}
        assert html_class.class_string == "bar foo"
        assert html_class.has_class("foo")
        assert html_class.has_class("bar")

        html_class.remove("baz")  # should be no effect
        assert html_class.classes == {"foo", "bar"}
        assert html_class.class_string == "bar foo"
        assert html_class.has_class("foo")
        assert html_class.has_class("bar")

    def test_replace(self):
        """
        replace existing class
        """
        html_class = HtmlClass("foo bar")

        html_class.replace_class("foo", "plugh")
        assert html_class.classes == {"bar", "plugh"}
        assert not html_class.has_class("foo")
        assert html_class.has_class("bar")
        assert html_class.has_class("plugh")
        assert html_class.class_string == "bar plugh"

        html_class.add_class("foo")
        assert html_class.classes == {"foo", "bar", "plugh"}
        assert html_class.class_string == "bar foo plugh"
        html_class.replace_class("foo", "plugh")  # contains existing class, so should equal remove
        assert html_class.class_string == "bar plugh"


class HtmlTreeTest(AmiAnyTest):
    """
    makes sections from unstructured text
    """

    def test_nest_decimal_sections(self):
        """
        nests decimal sections (1.2.3, 3.4, etc.) into a tree
        """
        html_elem = lxml.etree.parse(str(Path(Resources.TEST_IPCC_CHAP04, "ipcc_fulltext_styles.html")))
        #  "<span id="id1521" class="s0 dec2">4.1</span>")
        xpath = (".//div/span["
                 "contains(@class, 'dec1') "
                 "or contains(@class, 'dec2') "
                 "or contains(@class, 'dec3') "
                 "or contains(@class, 'dec4')]")
        decimal_sections = HtmlTree.get_decimal_sections(html_elem, xpath=xpath)

        hierarchy = SectionHierarchy()
        hierarchy.add_sections(decimal_sections, poplist=["Chapter 4:"])
        hierarchy.sort_sections()

    @unittest.skip
    def test_decimal_chapters_production(self):
        # """NOT WORKING FULLY"""
        # TEST_IPCC_WG3 = Path(Resources.TEST_IPCC_DIR)
        # if not TEST_IPCC_WG3.exists():
        #     print(f"semanticClimate files not available locally")
        #     return
        html_elem = lxml.etree.parse(str(Path(Resources.TEST_IPCC_DIR, "wg2_03", "fulltext.html")))
        xpath = (".//div/span["
                 "contains(@class, 'dec1') "
                 "or contains(@class, 'dec2') "
                 "or contains(@class, 'dec3') "
                 "or contains(@class, 'dec4')]")
        decimal_sections = HtmlTree.get_decimal_sections(html_elem, xpath=xpath)

        hierarchy = SectionHierarchy()
        hierarchy.add_sections(decimal_sections, poplist=["Chapter 3:"])
        hierarchy.sort_sections()

class FontTest(AmiAnyTest):

    def _assert_new_css_style(self, style, new_value):
        css_style = CSSStyle.create_css_style_from_css_string(style)
        new_css_style = AmiFont.create_font_edited_style_from_css_style_object(css_style)
        assert str(new_css_style) == new_value

    def _run_tests_0(self, tests):
        for test in tests:
            ami_font = AmiFont.extract_name_weight_style_stretched_as_font(test[0])
            # assert str(ami_font) == test[0] + "/" + test[1]
            assert str(ami_font) == test[1]

    # -------------------------------


    # TODO edit test results
    def test_create_from_names(self):
        tests = [
            ("ArialNarrow", "name:ArialNarrow;family:Arial;weight:;style:;stretched:narrow;font:sans"),
            ("ArialBoldItalic", "name:ArialBoldItalic;family:Arial;weight:bold;style:italic;stretched:;font:sans"),
            ("ArialItalic", "name:ArialItalic;family:Arial;weight:;style:italic;stretched:;font:sans"),
            ("ArialBold", "name:ArialBold;family:Arial;weight:bold;style:;stretched:;font:sans"),
            ("Arial", "name:Arial;family:Arial;weight:;style:;stretched:;font:sans"),
        ]
        self._run_tests_0(tests)

        test2s = [
            ("ArialNarrow", "name:ArialNarrow;family:Arial;weight:;style:;stretched:narrow;font:sans"),
            ("ArialNarrow-Bold", "name:ArialNarrow-Bold;family:Arial;weight:bold;style:;stretched:narrow;font:sans"),
            ("Calibri", "name:Calibri;family:Calibri;weight:;style:;stretched:;font:sans"),
            ("FrutigerLTPro-BlackCn", "name:FrutigerLTPro-BlackCn;family:FrutigerLTPro;weight:bold;style:;stretched:narrow;font:sans"),
            ("FrutigerLTPro-BoldCn", "name:FrutigerLTPro-BoldCn;family:FrutigerLTPro;weight:bold;style:;stretched:narrow;font:sans"),
            ("FrutigerLTPro-BoldCnIta", "name:FrutigerLTPro-BoldCnIta;family:FrutigerLTPro;weight:bold;style:italic;stretched:narrow;font:sans"),
            ("FrutigerLTPro-Condensed", "name:FrutigerLTPro-Condensed;family:FrutigerLTPro;weight:;style:;stretched:narrow;font:sans"),
            ("FrutigerLTPro-CondensedIta", "name:FrutigerLTPro-CondensedIta;family:FrutigerLTPro;weight:;style:italic;stretched:narrow;font:sans"),
            ("FrutigerLTPro-Light", "name:FrutigerLTPro-Light;family:FrutigerLTPro;weight:light;style:;stretched:;font:sans"),
            ("FrutigerLTPro-LightCn", "name:FrutigerLTPro-LightCn;family:FrutigerLTPro;weight:light;style:;stretched:narrow;font:sans"),
            ("FrutigerLTPro-LightCnIta", "name:FrutigerLTPro-LightCnIta;family:FrutigerLTPro;weight:light;style:italic;stretched:narrow;font:sans"),
            ("FrutigerLTPro-Roman", "name:FrutigerLTPro-Roman;family:FrutigerLTProRoman;weight:;style:;stretched:;font:sans"),

        ]
        self._run_tests_0(test2s)

    # TODO edit manually
    def test_edit_fonts_in_styles(self):
        """
        edits the style attributes to extract weights and styles
        tests: CSSStyle.create_css_style_from_css_string(style)
        """
        self._assert_new_css_style("font-family: ArialNarrowBold; fill: red",
                                  'font-family:Arial; fill:red; font-name:ArialNarrowBold; font:sans; font-weight:bold; font-stretched:narrow;')
        self._assert_new_css_style("font-family: ArialBold; fill: red",
                                  'font-family:Arial; fill:red; font-name:ArialBold; font:sans; font-weight:bold;')
        self._assert_new_css_style("font-family: FooBarBold; fill: red",
                                  'font-family:FooBar; fill:red; font-name:FooBarBold; font:sans; font-weight:bold;')


    # TODO edit test
    @unittest.skip("not yet written")
    def test_normalize_fonts_in_head_style_elements_CURRENT(self):
        """
        extract font properties from styles and write back into html header
        e.g.
        <html>
          <head>
            <style>.s1 {font-family:ArialNarrowBold; fill:red}</style>
            <style>.s2 {font-family:FooBar-Ita; fill:blue}</style>
          </head>
        </html>

        goes to
        <html>
          <head>
            <style>.s1 {font-family:Arial; font-weight: bold; font-stretched: Narrow; fill:red}</style>
            <style>.s2 {font-family:FooBar; font-style: italic; fill:red}</style>
          </head>
        </html>
        """
        html_str = """
        <html>
          <head>
            <style>.s1 {font-family:ArialNarrowBold; fill:red}</style>
            <style>.s2 {font-family:FooBar-Ita; fill:blue}</style>
          </head>
        </html>
"""
        html_elem = lxml.etree.fromstring(html_str)
        CSSStyle.normalize_styles_in_fonts_in_html_head(html_elem)

    def test_display_styles(self):
        """mainly to explore use of class attributes
        if class has multiple components, which clash, then order of
        <style> elements matters - last takes precedence.
        """
        html = HtmlLib.create_html_with_empty_head_body()
        head = HtmlLib.get_head(html)
        HtmlLib.add_explicit_head_style(html, ".blueborder", "{border:solid 1px blue;}")
        HtmlLib.add_explicit_head_style(html, ".redborder", "{border:solid 1px red;}")
        HtmlLib.add_explicit_head_style(html, ".blueborder", "{border:solid 1px blue;}")
        HtmlLib.add_explicit_head_style(html, ".yellowback", "{background: yellow;}")

        body = HtmlLib.get_body(html)
        div = lxml.etree.SubElement(body, "div")
        div.attrib["class"] = "div"

        span1 = lxml.etree.SubElement(div, "span")
        clazz = "blueborder"
        span1.text = f"This is {clazz}"
        span1.attrib["class"] = clazz


        span2 = lxml.etree.SubElement(div, "span")
        clazz = "yellowback"
        span2.text = f"This is {clazz}"
        span2.attrib["class"] = clazz

        # both styles are applied
        span3 = lxml.etree.SubElement(div, "span")
        clazz = "blueborder yellowback"
        span3.text = f"This is {clazz}"
        span3.attrib["class"] = clazz

        # both styles conflict
        span3 = lxml.etree.SubElement(div, "span")
        clazz = "blueborder redborder"
        span3.text = f"This is {clazz}"
        span3.attrib["class"] = clazz

        # both styles conflict
        span3 = lxml.etree.SubElement(div, "span")
        clazz = "redborder blueborder"
        span3.text = f"This is {clazz}"
        span3.attrib["class"] = clazz

        outfile = Path(Resources.TEMP_DIR, "styles", "classes.html")
        HtmlLib.write_html_file(html, outfile, debug=True)


class AnnotateTest(AmiAnyTest):
    """
    tests AmiAnnotator and annotation more generally
    """

    def test_annotate_element(self):
        """annotate text"""
        para = ET.Element("p")
        para.text = "We need to understand the carbon cycle and methane."
        annotator = AmiAnnotator(words=["carbon cycle", "methane", "AMOC"])
        assert 3 == len(annotator.words)
        annotator.annotate_elem(para)
        a_elems = annotator.get_anchors_with_annotations(para)
        assert len(a_elems) > 0
        for a_elem in a_elems:
            logger.debug(f"A {a_elem=}")

class HtmlEditorTest(AmiAnyTest):

    def test_create_element(self):
        editor = HtmlEditor(create_skeleton=True)
        editor.add_element("//body", "div")
        assert ET.tostring(editor.html) == b'<html><head/><body><div/></body></html>'

    def test_create_element_and_add_text_and_attributes(self):
        """
        create a div with a[@href]
        """
        editor = HtmlEditor(create_skeleton=True)

        editor.add_element("//body", "a", text="text", attrs={"href":"_blank", "title": "href",})

        assert ET.tostring(editor.html) == \
            b'<html><head/><body><a href="_blank" title="href">text</a></body></html>'


    def test_execute_commands(self):
        editor = HtmlEditor()
        wg = "wg1"

        logger.info(f"**** current wg {wg}")
        ar6 = Path(Resources.TEST_RESOURCES_DIR, "ar6")
        IN_WG = Path(ar6, wg)
        OUT_WG = Path(Resources.TEMP_DIR, "ipcc", wg)
        inpath = Path(IN_WG, "toplevel.html")

        # apply edit commands
        editor.read_html(inpath)
        json_path = Path(ar6, "edit_toplevel.json")
        logger.info(f"json commands {json_path}")
        editor.read_commands(json_path)
        editor.execute_commands()

        outpath = Path(OUT_WG, "edited_toplevel.html")
        HtmlLib.write_html_file(editor.html, outpath, debug=True)

    def test_de_gatsby_with_commands(self):
        """
        use HtmlEditor commands to remove gatsby markup
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc",
                        "cleaned_content", "wg2", "CrossChapters", "ccp5", "gatsby_raw.html")
        assert inpath.exists()
        editor = HtmlEditor()
        editor.read_html(inpath)
        json_path = Path(Resources.TEST_RESOURCES_DIR, "ar6", "de_gatsby.json")
        assert json_path.exists()
        logger.info(f"json commands {json_path}")
        editor.read_commands(json_path)
        editor.execute_commands()

        outpath = Path(Resources.TEMP_DIR, "ipcc", "wg2", "CrossChapters",
                       "ccp5", "de_gatsby.html")
        HtmlLib.write_html_file(editor.html, outpath, debug=True)

    def test_clean_de_gatsby_with_commands(self):
        """
        cleans html with unnecessary divs
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg2", "CrossChapters",
                       "ccp5", "de_gatsby.html")
        assert inpath.exists()
        editor = HtmlEditor()
        editor.read_html(inpath)
        json_path = Path(Resources.TEST_RESOURCES_DIR, "ar6", "de_gatsby1.json")
        assert json_path.exists()
        editor.read_commands(json_path)
        editor.execute_commands()

        outpath = Path(Resources.TEMP_DIR, "ipcc", "wg2", "CrossChapters",
                       "ccp5", "de_gatsby.html")
        HtmlLib.write_html_file(editor.html, outpath, debug=True)
        assert outpath.exists()

    def test_remove_single_child_divs_in_hierarchy_div3(self):
        """
        remove divs with single child elements in branched structure
        """
        editor = self._create_div3()
        assert (ss := ET.tostring(editor.html)) == b'<html><head/><body><div id="d1"><div id="d2"><div id="d3"/></div></div></body></html>'
        assert len(HtmlLib.find_single_child_divs(editor.html)) == 2
        removed = editor.remove_single_child_divs_in_hierarchy()
        assert removed == 2
        # try to recurse but no further possibility
        assert len(HtmlLib.find_single_child_divs(editor.html)) == 0
        assert ET.tostring(editor.html) == b'<html><head/><body><div id="d3"/></body></html>'
        removed = editor.remove_single_child_divs_in_hierarchy()
        assert removed == 0
        assert ET.tostring(editor.html) == b'<html><head/><body><div id="d3"/></body></html>'

    def test_remove_single_child_divs_in_hierarchy_div3_branch(self):
        """
        remove div with single child elements
        (D(D(D,D),D(D)))
        """
        editor = self._create_div3_branch()
        # assert ET.tostring(editor.html) == (
        assert editor.to_bytes() == (
           b'<html>'
              b'<head/>'
              b'<body>'
                b'<div id="d1">'
                  b'<div id="d1.1">'
                    b'<div id="d1.1.1"/>'
                    b'<div id="d1.1.2"/>'
                  b'</div>'
                  b'<div id="d1.2">'
                    b'<div id="d1.2.1"/>'
                  b'</div>'
                b'</div>'
              b'</body>'
            b'</html>')
        # removed = HtmlLib.remove_single_child_divs_in_hierarchy(editor.html)
        removed = editor.remove_single_child_divs_in_hierarchy()
        assert removed == 1
        # try to recurse but no further possibility
        assert len(HtmlLib.find_single_child_divs(editor.html)) == 0
        assert ET.tostring(editor.html) == (
            b'<html>'
              b'<head/>'
              b'<body>'
                b'<div id="d1">'
                  b'<div id="d1.1">'
                    b'<div id="d1.1.1"/>'
                    b'<div id="d1.1.2"/>'
                  b'</div>'
                  b'<div id="d1.2.1"/>'
                b'</div>'
              b'</body>'
            b'</html>')
        removed = HtmlLib.remove_single_child_divs_in_hierarchy(editor.html)
        assert removed == 0
        assert ET.tostring(editor.html) == (
            b'<html>'
              b'<head/>'
              b'<body>'
                b'<div id="d1">'
                  b'<div id="d1.1">'
                    b'<div id="d1.1.1"/>'
                    b'<div id="d1.1.2"/>'
                  b'</div>'
                  b'<div id="d1.2.1"/>'
                b'</div>'
              b'</body>'
            b'</html>')

    def _create_div3(self):
        """html for test
        hierarchy of 3 divs
        """
        editor = HtmlEditor()
        editor.add_element("//body", "div", attrs={'id': 'd1', })
        editor.add_element("//body/div", "div", attrs={'id': 'd2', })
        editor.add_element("//body/div/div", "div", attrs={'id': 'd3', })
        return editor

    def _create_div3_branch(self):
        """html for test
        hierarchy of 3 levels, branches at level 2
        """
        editor = HtmlEditor()
        editor.add_element("//body", "div", attrs={'id': 'd1', })
        editor.add_element("//body/div", "div", attrs={'id': 'd1.1', })
        editor.add_element("//body/div", "div", attrs={'id': 'd1.2', })
        editor.add_element("//body/div/div[@id='d1.1']", "div", attrs={'id': 'd1.1.1', })
        editor.add_element("//body/div/div[@id='d1.1']", "div", attrs={'id': 'd1.1.2', })
        editor.add_element("//body/div/div[@id='d1.2']", "div", attrs={'id': 'd1.2.1', })
        return editor


