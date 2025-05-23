import codecs
import codecs
import csv
import glob
import logging
import os
import pprint
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

import lxml
import lxml.etree
import lxml.html
import pandas as pd
import pdfplumber as pdfp
import requests

import test.test_all
from amilib.ami_bib import Publication
from amilib.pdf_args import PDFArgs
from amilib.ami_pdf_libs import PDFSlide
from amilib.ami_integrate import HtmlGenerator

"""NOTE REQUIRES LATEST pdfplumber"""
import pdfplumber
from PIL import Image
from lxml.html import HTMLParser

# local

from amilib.ami_pdf_libs import SVG_NS, SVGX_NS, PDFDebug, PDFParser
from amilib.ami_pdf_libs import AmiPage, X, Y, SORT_XY, PDFImage, AmiPDFPlumber, AmiPlumberJsonPage, AmiPlumberJson
from amilib.ami_pdf_libs import WORDS, IMAGES, ANNOTS, CURVES, TEXTS
from amilib.ami_html import HtmlUtil, STYLE, FILL, STROKE, FONT_FAMILY, FONT_SIZE, HtmlLib
from amilib.ami_html import H_SPAN, H_BODY, H_P
from amilib.amix import AmiLib
from amilib.bbox import BBox
from amilib.file_lib import FileLib
from amilib.util import Util


from test.resources import Resources
from test.test_all import AmiAnyTest

HERE = os.path.abspath(os.path.dirname(__file__))

logger = Util.get_logger(__name__)

# class PDFTest:

FINAL_DRAFT_DIR = "/Users/pm286/projects/readable_climate_reports/ipcc/dup/finalDraft/svg"  # PMR only
PAGE_9 = Path(Resources.TEST_CLIMATE_10_SVG_DIR, "fulltext-page.9.svg")
PAGE_6 = Path(Resources.TEST_CLIMATE_10_SVG_DIR, "fulltext-page.6.svg")
CURRENT_RANGE = range(1, 20)
# CHAPTER_RANGE = range(1, 200)

# output directories in /temp
TEMP_PNG_IPCC_CHAP06 = Path(AmiAnyTest.TEMP_DIR, "png", "ar6", "chap6")
TEMP_PNG_IPCC_CHAP06.mkdir(exist_ok=True, parents=True)

PMC1421_PDF = Path(Resources.RESOURCES_DIR, "projects", "liion4", "PMC4391421", "fulltext.pdf")

IPCC_DIR = Path(Resources.TEST_RESOURCES_DIR, "ar6")

UNHLAB_DIR = Path(Resources.TEST_RESOURCES_DIR, "unlibrary")
IPCC_GLOSS_DIR = Path(IPCC_DIR, "glossary")
IPCC_GLOSSARY = Path(IPCC_GLOSS_DIR, "IPCC_AR6_WGIII_Annex-I.pdf")
IPCC_WG2_DIR = Path(IPCC_DIR, "wg2")
IPCC_WG2_3_DIR = Path(IPCC_WG2_DIR, "wg2_03")
IPCC_WG2_3_PDF = Path(IPCC_WG2_3_DIR, "fulltext.pdf")

# arg_dict


INPATH = "inpath"
MAXPAGE = "maxpage"
PAGES = "pages"
OUTDIR = "outdir"
OUTFORM = "outform"
OUTPATH = "outpath"
OUTSTEM = "outstem"
PDF2HTML = "pdf2html"
PDFMINER = "pdfminer"
PDFPLUMBER = "pdfplumber"
FLOW = "flow"
# FORMAT = "fmt"
IMAGEDIR = "imagedir"
RESOLUTION = "resolution"
TEMPLATE = "template"


# ==============================
# Helpers
# ==============================


def make_full_chap_10_draft_html_from_svg(pretty_print, use_lines, rotated_text=False):
    """
    reads SVG output from ami3/pdfbox and converts to HTML
    :param pretty_print: pretty print the HTML. Warning may introduce whitespace
    :param use_lines: output is CompositeLines. Not converted into running text (check)
    :param rotated_text: include/ignore tex# ts with non-zero @rotateDegress attribute
    """
    if not Path(FINAL_DRAFT_DIR, f"fulltext-page.2912.svg").exists():
        logging.warning("SVG file not available in repo; ignored")
        return
        # raise Exception("must have SVG from ami3")
    for page_index in CURRENT_RANGE:
        page_path = Path(FINAL_DRAFT_DIR, f"fulltext-page.{page_index}.svg")
        html_path = Path(AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR, f"page.{page_index}.html")
        AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR.mkdir(exist_ok=True, parents=True)
        ami_page = AmiPage.create_page_from_svg(page_path, rotated_text=rotated_text)
        ami_page.write_html(html_path, pretty_print, use_lines)


def make_html_dir():
    html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
    html_dir.mkdir(exist_ok=True, parents=True)
    return html_dir


class PDFPlumberTest(AmiAnyTest):
    def test_logger(self):
        logger.error("this is testing logger ERROR")

        logger.warning("this is testing logger WARNING")
        logger.info("this is testing logger INFO")
        logger.debug("this is testing logger DEBUG")


    """
    tests that we can tun the new PDFPlumber tests
    Mainly directly for PDFPlumber rather than applications
    """

    def test_pdfplumber_json_single_page_debug(self):
        """creates AmiPDFPlumber and reads pdf and debugs"""
        path = Path(os.path.join(HERE, "resources/pdffill-demo.pdf"))
        assert path.exists, f"{path} should exist"
        ami_pdfplumber = AmiPDFPlumber()
        ami_plumber_json = ami_pdfplumber.create_ami_plumber_json(path)
        pages = ami_plumber_json.get_ami_json_pages()
        assert type(pages[0]) is AmiPlumberJsonPage
        imagedir = str(Path(AmiAnyTest.TEMP_DIR, "images"))
        ami_pdfplumber.debug_page(pages[0], imagedir=imagedir)

    def test_pdfplumber_singlecol_create_spans_with_CSSStyles(self):
        """
        creates AmiPDFPlumber and reads single-column pdf and debugs
        probably belongs in UNIPCC

        writes one div per line
        """
        input_pdf = Path(Resources.TEST_IPCC_LONGER_REPORT, "fulltext.pdf")
        output_page_dir = Path(AmiAnyTest.TEMP_DIR, "html", "ar6", "LongerReport", "pages")
        page_json_dir = output_page_dir
        output_page_dir.mkdir(exist_ok=True, parents=True)
        ami_pdfplumber = AmiPDFPlumber()
        logger.info(f"writing to {output_page_dir}")
        HtmlGenerator.create_html_pages(
            ami_pdfplumber, input_pdf=input_pdf, outdir=output_page_dir, page_json_dir=page_json_dir,
            pages=[1, 2, 3, 4, 5, 6, 7])

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    # @unittest.skip("documents not in distribution")
    def test_pdfplumber_doublecol_create_pages_for_WGs_HACKATHON(self):
        """
        creates AmiPDFPlumber and reads double-column pdf and debugs
        This is also an integration/project test
        """

        report_names = [
            # "SYR_LR",
            # "SYR_SPM",
            # "SR15_SPM",
            # "SR15_TS",
            # "SRCCL_SPM",
            # "SRCCL_TS",
            # "SROCC_SPM",
            # "SROCC_TS",
            # "WG1_SPM",
            # "WG1_TS",
            # "WG2_SPM",
            # "WG2_TS",
            # "WG3_SPM",
            # "WG3_TS",
            "WG3_CHAP08",
        ]
        for report_name in report_names:
            report_dict = Resources.WG_REPORTS[report_name]
            logger.info(f"\n==================== {report_name} ==================")
            input_pdf = report_dict["input_pdf"]
            if not input_pdf.exists():
                logger.error(f"cannot find {input_pdf}")
                continue
            output_page_dir = report_dict["output_page_dir"]
            logger.debug(f"output dir {output_page_dir}")
            output_page_dir.mkdir(exist_ok=True, parents=True)
            page_json_dir = output_page_dir
            ami_pdfplumber = AmiPDFPlumber(param_dict=report_dict)
            HtmlGenerator.create_html_pages(ami_pdfplumber, input_pdf=input_pdf, outdir=output_page_dir, debug=True,
                                            page_json_dir=page_json_dir, outstem="total_pages")
            # MUST test output.

    def test_unusual_chars(self):
        """badly decoded characters default to #65533"""
        x = """Systems������������ 867"""
        for c in x:
            logger.debug(f"c {c} {ord(c)}")

    @unittest.skip("LONG BOOK")
    def test_climate_academy_create_html_LONG(self):
        # """an aritrary NGO report The result"""
        # input_pdf = Path("/Users/pm286/workspace/misc/380981eng.pdf")
        # assert input_pdf.exists(), f"file should exist {input_pdf}"
        # output_page_dir = Path(AmiAnyTest.TEMP_DIR, "html", "misc", "380981")

        """Matthew Pye's 'ClimateAcademy' - only available on request"""
        climate_academy = "ClimateAcademy"
        student_book = "student_book_2025_02"
        # in PMR's workspace dir, nit generally available
        input_pdf = Path(Path(Resources.TEST_RESOURCES_DIR).parent.parent.parent,
                         climate_academy, f"{student_book}.pdf")
        if not input_pdf.exists():
            logger.error("No climate book")
            return
        output_page_dir = Path(AmiAnyTest.TEMP_DIR, "html", climate_academy, student_book)

        output_page_dir.mkdir(exist_ok=True, parents=True)
        page_json_dir = output_page_dir
        # ami_pdfplumber = AmiPDFPlumber(param_dict=report_dict)
        ami_pdfplumber = AmiPDFPlumber(param_dict=None)
        HtmlGenerator.create_html_pages(
            ami_pdfplumber,
            input_pdf=input_pdf,
            outdir=output_page_dir,
            page_json_dir=page_json_dir,
            debug=False)

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_pdf_plumber_table_LONG(self):
        """haven't found any tables yet!
        tests DataFrames
        """
        inpdf = Path(Resources.TEST_IPCC_DIR, "Chapter15", "fulltext.pdf")
        with pdfplumber.open(inpdf) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    logger.info(f"===========page {i + 1} {len(tables)}===========")
                    for j, table in enumerate(tables):
                        logger.debug(f"table {j + 1} {table}")
                        df = pd.DataFrame(table)
                        logger.debug(f"df {df}")


    def test_pdf_index(self):
        """
        Reads a medium PDF (Breward Chapter 1) and extracts words
        Still evolving
        """
        import pdfplumber
        infile = Path(Resources.TEST_RESOURCES_DIR, "pdf", "breward_1.pdf")
        assert infile.exists()
        outdir = Path(Resources.TEMP_DIR, "pdf", "html", "breward_1")

        AmiPage.create_html_pages_pdfplumber(
             # bbox=DEFAULT_BBOX,
             input_pdf=infile,
             output_dir=outdir,
             output_stem="page",
#             range_list=range(1, 9999999)
        )

    def test_combining_characters(self):
        """
        reads accented French text with overprinting
        The PDF does not use modern approaches
        """

        # dictionary of diacritic conversions for lowercase letters
        # expand this with more accents and diacritics
        dia_dict = {
            "`a": "à",
            "`e": "è",
            "`u": "ù",
            "´e": "é"
        }
        infile = Path(Resources.TEST_RESOURCES_DIR, "combining", "french.pdf")
        with pdfplumber.open(infile) as pdf:
            page0 = pdf.pages[0]
            text = page0.extract_text()
            print(f" text {text}")
            for item in dia_dict.items():
                text = re.sub(item[0], item[1], text )
            print("--converts to-->>")
            print(f" text {text}")



class PDFTest(AmiAnyTest):
    MAX_PAGE = 5
    MAX_ITER = 20

    # all are skipUnless
    ADMIN = True and AmiAnyTest.ADMIN
    CMD = True and AmiAnyTest.CMD
    DEBUG = True and AmiAnyTest.DEBUG
    LONG = True and AmiAnyTest.LONG
    NET = True and AmiAnyTest.NET
    OLD = True and AmiAnyTest.OLD
    NYI = True and AmiAnyTest.NYI
    USER = True and AmiAnyTest.USER

    # skipIf
    BUG = True and AmiAnyTest.BUG

    VERYLONG = False or AmiAnyTest.VERYLONG

    # local
    HTML = True
    SVG = True

    # old tests
    OLD = False

    @unittest.skipUnless("enviroment", ADMIN)
    def test_pdfbox_output_exists(self):
        """check CLIMATE dir exists
        """
        assert Resources.TEST_CLIMATE_10_PROJ_DIR.exists(), f"{Resources.TEST_CLIMATE_10_PROJ_DIR} should exist"

    @unittest.skipUnless(SVG, "svg")
    def test_get_text_attribs(self):
        """find various SVG attributes, including 'style'
        """
        ami_page = AmiPage.create_page_from_svg(PAGE_9)
        # <climate10_:text> element
        text0 = ami_page.get_svg_text(0)
        assert text0.svg_text_elem.tag == f"{{{SVG_NS}}}text"
        # single Y-coord
        assert text0.svg_text_elem.attrib.get(Y) == '44.76'
        # list of X-coords
        assert text0.svg_text_elem.attrib.get(X) == \
               '72.0,79.201,84.721,90.241,96.961,104.162,111.363,117.482,124.798,127.288,258.242,263.762,268.' \
               '802,276.601,284.401,288.841,292.202,297.241,299.761,303.001,308.041,311.402,313.921,319.441,' \
               '324.481,327.241,330.001,334.441,339.481,347.28,351.601,356.641,361.081,364.442,368.28,370.77,' \
               '448.08,451.439,456.96,463.563,470.167,472.687,480.006,486.61,491.651,494.171,503.533,510.718,' \
               '513.238,516.594,519.951,523.307'
        # list of character-widths (from publisher) (multiply by font-size to get pixels)
        assert text0.svg_text_elem.attrib.get(f"{{{SVGX_NS}}}width") == \
               '0.72,0.56,0.56,0.67,0.72,0.72,0.61,0.72,0.25,0.55,0.56,0.5,0.78,0.78,0.44,0.33,0.5,0.25,0.33,' \
               '0.5,0.33,0.25,0.56,0.5,0.28,0.28,0.44,0.5,0.78,0.44,0.5,0.44,0.33,0.39,0.25,0.55,0.33,0.56,' \
               '0.67,0.67,0.25,0.72,0.67,0.5,0.25,0.94,0.72,0.25,0.33,0.33,0.33,0.25'
        # style (dict-like collection of name-value pairs
        assert text0.svg_text_elem.get(STYLE) == \
               'fill:rgb(0,0,0);font-family:TimesNewRomanPSMT;font-size:9.96px;stroke:none;'
        # text-content without tags
        text_content = text0.get_text_content()
        assert text_content == "APPROVED Summary for Policymakers IPCC AR6 WG III "
        assert len(text_content) == 50  # some spaces have been elided??

    @unittest.skipUnless(SVG, "svg")
    def test_get_text_attrib_vals(self):
        """more attributes and convenience methods"""
        ami_page = AmiPage.create_page_from_svg(PAGE_9)
        # <climate10_:text> element
        ami_text0 = ami_page.get_svg_text(0)
        x_coords = ami_text0.get_x_coords()
        assert x_coords == [
            72.0, 79.201, 84.721, 90.241,
            96.961, 104.162, 111.363, 117.482, 124.798, 127.288, 258.242, 263.762, 268.802,
            276.601, 284.401, 288.841, 292.202, 297.241, 299.761,
            303.001, 308.041, 311.402, 313.921, 319.441, 324.481, 327.241, 330.001,
            334.441, 339.481, 347.28, 351.601, 356.641, 361.081, 364.442,
            368.28, 370.77, 448.08, 451.439, 456.96, 463.563, 470.167,
            472.687, 480.006, 486.61, 491.651, 494.171, 503.533, 510.718, 513.238, 516.594, 519.951, 523.307]
        assert len(x_coords) == 52

        widths = ami_text0.get_widths()
        assert widths == [
            0.72, 0.56, 0.56, 0.67, 0.72, 0.72, 0.61,
            0.72, 0.25, 0.55, 0.56, 0.5, 0.78, 0.78, 0.44, 0.33, 0.5, 0.25, 0.33, 0.5, 0.33,
            0.25, 0.56, 0.5, 0.28, 0.28, 0.44, 0.5, 0.78, 0.44, 0.5, 0.44, 0.33,
            0.39, 0.25, 0.55, 0.33, 0.56, 0.67, 0.67, 0.25, 0.72, 0.67, 0.5, 0.25, 0.94, 0.72, 0.25, 0.33, 0.33,
            0.33, 0.25
        ]
        assert len(widths) == 52

        # SVG style dict from SVG@style attribute
        style_dict = ami_text0.extract_style_dict_from_svg()
        # assert style_dict == {'fill': 'rgb(0,0,0)',\n 'font-family': 'TimesNewRomanPSMT',\n 'font-size': '9.96px',\n 'stroke': 'none'}
        assert style_dict[FILL] == 'rgb(0,0,0)'
        assert style_dict[FONT_FAMILY] == 'TimesNewRomanPSMT'
        assert style_dict[FONT_SIZE] == '9.96px'
        assert style_dict[STROKE] == 'none'
        assert ami_text0.get_font_size() == 9.96

    @unittest.skipUnless(SVG, "svg")
    def test_create_text_lines_page6(self):
        """creation of AmiPage from SVG page and creation of text spans"""
        page = AmiPage.create_page_from_svg(PAGE_6)
        page.create_text_spans(sort_axes=SORT_XY)
        assert 70 >= len(page.text_spans) >= 60

    # @unittest.skipUnless(USER or True, "page2sect")
    def test_make_raw_ami_pages_with_spans_from_charstream_ipcc_chap6(self):
        """
        The central AMI method to make HTML from PDF characters

        creates spans with coordinates inside divs
        Uses AmiPage.create_html_pages() which uses AmiPage.chars_to_spans()
        creates Raw HTML
        NOT FLOWABLE

        """
        output_stem = "raw_plumber"
        page_nos = range(3, 13)
        # page_nos = [3 4 5 8 ]
        input_pdf = Path(Resources.TEST_IPCC_CHAP06_PDF)
        assert input_pdf.exists(), f"{input_pdf} should exist"
        bbox = BBox(xy_ranges=[[60, 999], [60, 790]])
        output_dir = Path(AmiAnyTest.TEMP_PDF_IPCC_CHAP06)
        AmiPage.create_html_pages_pdfplumber(bbox=bbox, input_pdf=input_pdf,
                                             output_dir=output_dir, output_stem=output_stem,
                                             range_list=[range(3, 8), range(129, 131)])
        assert output_dir.exists()
        logger.debug(f"writing to dir: {output_dir}")
        assert Path(output_dir, f"{output_stem}_{5}.html").exists()

    def test_bmp_png_to_png(self):
        """
        convert bmp, jpgs, etc to PNG
        results in temp/ar6/chap6/png/
        checks existence on created PNG
        uses: pdf_image.convert_all_suffixed_files_to_target(dirx, [".bmp", ".jpg"], ".png", outdir=outdir)
        USEFUL

        """
        dirx = Path(Resources.TEST_IPCC_CHAP06, "image_bmp_jpg")
        outdir = TEMP_PNG_IPCC_CHAP06
        if not dirx.exists():
            logger.info(f"no directory {dirx}")
            return
        pdf_image = PDFImage()
        pdf_image.convert_all_suffixed_files_to_target(dirx, [".bmp", ".jpg"], ".png", outdir=outdir)
        pngs = [
            "Im1.png", "Im0.1.png", "Im0.2.png", "Im1.4.png", "Im1.5.png", "Im0.1.png",
            "Im0.0.png", "Im1.png", "Im3.png", "Im0.2.png", "Im0.3.png", "Im2.png",
        ]
        for png in pngs:
            assert (p := Path(outdir, png)).exists(), "{p} should exist"

    def test_merge_pdf2txt_bmp_jpg_with_coords(self):
        """
        creates coordinate data for images (20 pp doc) and also reads existing coord data from file
        (? from AMI3-java or previous run) and tries to match them
        """
        png_dir = Path(Resources.TEST_IPCC_CHAP06, "images")
        bmp_jpg_dir = Path(Resources.TEST_IPCC_CHAP06, "image_bmp_jpg")
        coord_file = Path(Resources.TEST_IPCC_CHAP06, "image_coords.txt")
        logger.debug(f"input {coord_file}")
        outdir = Path(Resources.TEST_IPCC_CHAP06, "images_new")
        outdir.mkdir(exist_ok=True, parents=True)
        with open(coord_file, "r") as f:
            coord_list = f.readlines()
        assert len(coord_list) == 14

        coord_list = [c.strip() for c in coord_list]
        wh_counter = Counter()
        coords_by_width_height = dict()
        for coord in coord_list:
            # image_9_0_80_514_72_298
            coords = coord.split("_")
            assert len(coords) == 7
            bbox = BBox(xy_ranges=[[coords[3], coords[4]], [coords[5], coords[6]]])
            logger.debug(f"coord {coord} {bbox} {bbox.width},{bbox.height}")
            wh_tuple = bbox.width, bbox.height
            logger.debug(f"wh {wh_tuple}")
            wh_counter[wh_tuple] += 1
            if coords_by_width_height.get(wh_tuple) is None:
                coords_by_width_height[wh_tuple] = [coord]
            else:
                coords_by_width_height.get(wh_tuple).append(coord)
        logger.debug(f"counter {wh_counter}")
        logger.debug(f"coords_by_wh {coords_by_width_height}")

        bmp_jpg_images = os.listdir(bmp_jpg_dir)
        for bmp_jpg_image in bmp_jpg_images:
            if Path(bmp_jpg_image).suffix == ".png":
                logger.debug(f"png {bmp_jpg_image}")
                with Image.open(str(Path(bmp_jpg_dir, bmp_jpg_image))) as image:
                    wh_tuple = image.width, image.height
                    logger.debug(f"wh ... {wh_tuple}")
                    logger.debug(f"coords {coords_by_width_height.get(wh_tuple)}")

    # See https://pypi.org/project/depdf/0.2.2/ for paragraphs?

    # https://towardsdatascience.com/pdf-text-extraction-in-python-5b6ab9e92dd

    @unittest.skipIf(LONG, "doesn't obey --maxpage or --pages")
    def test_make_structured_html_cmdline_DEBUG(self):
        """
        Previous one gives:
        arg_dict {'convert': 'html', 'flow': True, 'footer': 80, 'header': 80, 'indir': None,
        'inpath': PosixPath('/Users/pm286/workspace/pyami/test/resources/ar6/Chapter06/fulltext.pdf'),
        'maxpage': 10, 'outdir': None, 'outform': 'html', 'outstem': 'fulltext'}

        Tried to run:
        python -m amilib.ami_pdf
        --inpath /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/fulltext.pdf
        --maxpage 88 --outdir /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/

        which didn't give flow html, but sections.
        Its debug

        Namespace(convert=None, debug=None, flow=True, footer=80, header=80, imagedir=None,
        indir=None, inpath=['/Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/fulltext.pdf'],
         maxpage=[88], outdir=['/Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/'],
         outform='html', outstem='fulltext.flow', resolution=400, template=None)"""

        """
        python -m amilib.amix PDF --inpath /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter17.pdf --outdir /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter17/raw/"""
        args = " PDF --inpath /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter17.pdf" \
               " --outdir /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter17/raw/" \
               " --pages 1_4"

        pyami = AmiLib()
        pyami.run_command(args)

    @unittest.skipUnless(AmiAnyTest.run_long() or True, "run occasionally")
    def test_make_ipcc_html_spans_LONG(self):
        """
        read some/all PDF pages in chapter
        parse with pdfplumber into raw_html

        uses PDFMiner library (no coordinates I think)
        then
        uses flow_tidy() to determine pages, wrap lines (span/div) in pages
        join pages
        trim headers and footers and sides
        then
        creates and HtmlTidy to remove or edit unwanted span/div/br

        CREATES ONE GIANT PARAGRAPH (unlikely to be useful)


        USED
        MODEL
        """
        chapter_dict = {
            "Chapter04": {
                "pages": "107"
            },
            "Chapter15": {
                "pages": "103"
            }
        }
        chapter = "Chapter04"
        chapter = "Chapter15"
        chapters_dir = Path(Resources.TEST_IPCC_DIR)
        unwanteds = {
            "chapter": {
                "xpath": ".//div/span",
                "regex": "^Chapter\\s+\\d+\\s*$"
            },
            "final_gov": {
                "xpath": ".//div/span",
                "regex": "^\\s*Final Government Distribution\\s*$"
            },
            "page": {
                "xpath": ".//div/a",
                "regex": "^\\s*Page\\s*\\d+\\s*$",
            },
            "wg3": {
                "xpath": ".//div/span",
                "regex": "^\\s*(IPCC AR6 WGIII)|(IPCC WGIII AR6)\\s*$",
            }
        }

        logger.info(f"Converting chapter: {chapter}")
        chapter_dir = Path(chapters_dir, chapter)
        outdir = Path(AmiAnyTest.TEMP_DIR, "html", "ar6", f"{chapter}")
        logger.info(f"wrote to dir {outdir}")

        pdf_args = PDFArgs.create_pdf_args_for_chapter(
            chapter=chapter,
            chapter_dir=chapter_dir,
            chapter_dict=chapter_dict,
            outdir=outdir,
            unwanteds=unwanteds)
        _, _ = pdf_args.convert_write()  # refactor, please

    def test_make_composite_lines_from_pdf_chap_6_3_toc(self):
        path = Path(Resources.TEST_IPCC_CHAP06, "html", "chap6_3.html")
        assert path.exists(), f"path exists {path}"
        AmiPage.create_page_from_pdf_html(path)

    # @unittest.skipUnless(VERYLONG, "why is this so long?")
    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally; why is this so long?")

    def test_pdf_html_wg2_format(self):

        chapter_dict = {"wg2_03": {'pages': '14'}}
        PDFArgs.create_pdf_args_for_chapter(
            chapter="wg2_03",
            chapter_dir=Resources.TEST_IPCC_WG2_CHAP03,
            chapter_dict=chapter_dict,
            outdir=Path(AmiAnyTest.TEMP_HTML_IPCC, "wg2", "chapter03"),
            unwanteds=None
        ).convert_write()  # refactor, please


class PDFChapterTest(test.test_all.AmiAnyTest):
    """
    processes part or whole of a chapter
    """

    @unittest.skipUnless(PDFTest.VERYLONG or True, "processes Chapters 04, 05, 16, 17")
    @unittest.skip("output is not HTML")
    def test_make_ipcc_html_EXAMPLE_FAILS(self):
        """
        Converts a complete chapter to HTML
        KEEPS STYLES
        JOINS LINES

        DOES NOT CLIP PAGES
        There should be a better one
        """
        #        sem_clim_dir = Path("/users/pm286", "projects", "semanticClimate")
        sem_clim_dir = Path(Resources.TEST_IPCC_DIR)
        if not sem_clim_dir.exists():
            logger.debug(f"no ar6 dir {sem_clim_dir}, so skipping")
            return
        ipcc_dir = Path(Resources.TEST_IPCC_DIR)
        assert ipcc_dir.exists(), f"ipcc_dir {ipcc_dir} does not exist"
        chapter_dict = {
            # "Chapter01",
            # "Chapter04", # works
            # "Chapter06",
            # "Chapter07",
            #            "Chapter06": 30,
            "Chapter15": 100,
            # "Chapter16",
        }
        for i, chapter in enumerate(chapter_dict.keys()):
            logger.info(f"Converting chapter: {chapter}")
            pdf_args = PDFArgs()
            chapter_dir = Path(ipcc_dir, chapter)
            # pdf_args.arg_dict[INDIR] = chapter_dir
            # inpath = Path(chapter, "fulltext.pdf")
            # pdf_args.arg_dict[INPATH] = Path(chapter_dir, "fulltext.pdf")
            # assert pdf_args.arg_dict[INPATH].exists(), f"file does not exist {inpath}"
            # pdf_args.arg_dict[MAXPAGE] = chapter_dict[chapter]
            # pdf_args.arg_dict[OUTFORM] = "flow.html"
            # pdf_args.arg_dict[OUTDIR] = Path(AmiAnyTest.TEMP_HTML_IPCC, chapter.lower())
            logger.debug(f"arg_dict {pdf_args.arg_dict}")

            pdf_args.convert_write(
                indir=chapter_dir,
                inpath=Path(chapter_dir, "fulltext.pdf"),
                maxpage=chapter_dict[chapter],
                outdir=Path(AmiAnyTest.TEMP_HTML_IPCC, chapter.lower()),
                outform="flow.html",
            )

    @unittest.skip(f"{PMC1421_PDF} has long filenames")
    def test_convert_article_pdf_to_html_and_save_raw(self):
        """Uses PDFParser.convert_pdf to convert PDF to HTML and save
        to temp (/Users/pm286/workspace/pyami/temp/html/pmc4121.xml)
        This is raw output with <br> between lines and mirrors the layout of
        the initial page. Still has y-coordinate ("top")

<span style="position:absolute; border: gray 1px solid; left:0px; top:50px; width:595px; height:842px;"></span>
<div style="position:absolute; top:50px;"><a name="1">Page 1</a></div>
<div style="position:absolute; border: textbox 1px solid; writing-mode:lr-tb; left:319px; top:87px; width:221px; height:9px;"><span style="font-family: Calibri,Italic; font-size:9px">Journal of Medicine and Life Volume 7, </span><span style="font-family: Calibri,BoldItalic; font-size:9px">Special Issue 3</span><span style="font-family: Calibri,Italic; font-size:9px">, 2014
<br></span></div><div style="position:absolute; border: textbox 1px solid; writing-mode:lr-tb; left:133px; top:108px; width:336px; height:34px;"><span style="font-family: ArialNarrow,Bold; font-size:16px">Thymus vulgaris essential oil: chemical composition

        """
        # Use `pip3 install pdfminer.six` for python3

        """reading amilib/resources/projects/liion4/PMC4391421/fulltext.pdf"""
        pathx = Path(PMC1421_PDF)

        # convert PDF to html
        result = PDFParser().convert_pdf_CURRENT(
            path=str(pathx),
            fmt="html",
            caching=True,
        )
        # output dir
        html_dir = Path(AmiAnyTest.TEMP_DIR, "html")
        html_dir.mkdir(exist_ok=True, parents=True)
        # ouytput file
        path = Path(html_dir, "pmc4121.xml")
        # clean because text requires new file
        if path.exists():
            os.remove(path)
        with codecs.open(path, "w", "UTF-8") as f:
            f.write(result)
            logger.info(f"wrote {f}")
        assert path.exists(), f"should output html to {path}"
        assert 76000 < os.path.getsize(path) < 77000, f"size should be in range , was {os.path.getsize(path)}"

    @unittest.skip("output is not HTML")
    def test_make_structured_html_MAIN(self):
        """
        structures the flat HTML from pdfplumber, but no coordinates (why are these lost?)
        Can still be used for word frequency, etc.
        uses tidy_flow()
        reorganizes the section order so result has incorrect order
        uses PDFArgs but populates directly, not from commandline
        creates text with coordinates and styles.


</span><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 14px;" id="id634">
<div style="top: 3691px;" id="id709" marker="Executive Summary "><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 14px;" id="id710">Executive Summary </span>
<div style="top: 3721px;" id="id712"><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 11px;" id="id713">Warming cannot be limited to well below 2&#176;C without rapid and deep reductions in energy system CO</span><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 6px;" id="id715">2</span><span style="font-family: TimesNewRomanPS-BoldMT; font-size: 11px;" id="id716"> and GHG emissions. </span><span style="font-family: TimesNewRomanPSMT; font-size: 11px;" id="id717">In scenarios
        """

        logger.info(f" converting {Resources.TEST_IPCC_CHAP06_PDF}")
        assert Resources.TEST_IPCC_CHAP06_PDF.exists(), f"chap6 {Resources.TEST_IPCC_CHAP06_PDF}"
        pdf_args = PDFArgs()
        pdf_args.arg_dict[INPATH] = Resources.TEST_IPCC_CHAP06_PDF
        pdf_args.arg_dict[MAXPAGE] = 10
        pdf_args.arg_dict[PAGES] = "1_10"
        #        outdir = Path(Resources.TEMP_DIR, "htnl", "ar6", "chap6")
        outdir = AmiAnyTest.TEMP_HTML_IPCC_CHAP06
        pdf_args.arg_dict[OUTPATH] = Path(outdir, "pdf.html")

        print(f"arg_dict {pdf_args.arg_dict}")
        outfile, _ = pdf_args.convert_write()
        if not outfile:
            logger.info(f"no file written")
        else:
            logger.info(f"check {outfile} exists")
            assert outfile.exists(), f"outfile {outfile} should exist"

    @unittest.skipUnless(PDFTest.HTML, "create running text")
    @unittest.skipUnless(PDFTest.USER, "develop for commandline")
    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_convert_to_raw_html_chap6_maxpage_example(self):
        """
        structures the flat HTML from pdfplumber into a running stream, but no coordinates
        the only test that uses tidy_flow()
        Can still be used for word frequency, etc.

Uses:
    self.raw_html = PDFParser().convert_pdf(path=self.inpath, fmt=self.outform, maxpages=self.maxpage)

    if self.flow:
        self.html = self.tidy_flow()

        creates single file ~/pyami/temp/ipcc_chap6/flow.test4.html (concatenated pages in WRONG ORDER)
        /pyami/temp/ipcc_chap6/chapter_6:.html - seems to be Chapter/author page.


        """

        assert Resources.TEST_IPCC_CHAP06_PDF.exists(), f"chap6 {Resources.TEST_IPCC_CHAP06_PDF}"
        pdf_args = PDFArgs()
        maxpage = 5
        # pdf_args.arg_dict[MAXPAGE] = maxpage  # works
        # pdf_args.arg_dict[INPATH] = Resources.TEST_IPCC_CHAP06_PDF
        # pdf_args.arg_dict[OUTPATH] = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06, f"flow.test{maxpage}.html")
        # pdf_args.arg_dict[PDF2HTML] = PDFPLUMBER

        pprint.pprint(pdf_args.arg_dict)
        # pdf_args.arg_dict[PAGES] = [(1,3), (5,10)]

        logger.debug(f"arg_dict {pdf_args.arg_dict}")
        outpath = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06, f"flow.test{maxpage}.html")
        outfile, _ = pdf_args.convert_write(
            maxpage=5,
            inpath=Resources.TEST_IPCC_CHAP06_PDF,
            outpath=outpath,
            pdf2html=PDFPLUMBER,
            process_args=False

        )  # all the conversion happens here
        assert outfile is not None and Path(outfile).exists(), f"{outfile} should exist"
        if not outfile:
            logger.info(f"no file written")
        else:
            logger.info(f"check {outfile.absolute()} exists")
            assert outfile.exists(), f"outfile {outfile} should exist"
            size = outfile.stat().st_size
            if maxpage == 4:
                assert size > 15000, f"size {outfile} {size}"

    @unittest.skipUnless(PDFTest.CMD, "command")
    @unittest.skip("output is not HTML")
    def test_convert_to_raw_html_chap6_page_ranges__fail(self):
        """
        converts complete chapter to raw HTML.
        outputs each page as
        .../pyami/temp/ipcc_chap6/fulltext.flow_5.html
        and also concatenates into .../pyami/temp/ipcc_chap6/flow.test.html
        If --maxpage or --pages is used then only output specific pages
        --maxpage is obsolete

        DOES NOT CREATE FLOW YET.
        FAILS

        """
        outdir = AmiAnyTest.TEMP_HTML_IPCC_CHAP06
        outfile = Path(outdir, "all.html")
        pdf = Resources.TEST_IPCC_CHAP06_PDF
        print(f"pdf file {pdf}")
        args = f"PDF --infile {pdf} --outdir {outdir} --pages 3_5 --flow True --outpath {outfile} --pdf2html pdfplumber"
        AmiLib().run_command(args)
        logger.info(f"created outfile {outfile}")
        logging.warning(f"DID NOT CREATE FILE {outfile}")
        # assert outfile.exists(), f"{outfile} should exist"

    def test_read_ipcc_chapter__debug(self):
        """read multipage document and extract properties

        """
        assert IPCC_GLOSSARY.exists(), f"{IPCC_GLOSSARY} should exist"
        max_page = PDFTest.MAX_PAGE
        # max_page = 999999
        options = [WORDS, ANNOTS]
        # max_page = 100  # increase this if yu want more output

        for (pdf_file, page_count) in [
            # (IPCC_GLOSSARY, 51),
            (Resources.TEST_IPCC_CHAP06_PDF, 219)
        ]:
            pdf_debug = PDFDebug()
            with pdfplumber.open(pdf_file) as pdf:
                logger.debug(f"file {pdf_file}")
                pages = list(pdf.pages)
                assert len(pages) == page_count
                for page in pages[:max_page]:
                    pdf_debug.debug_page_properties(page, debug=options)


    @unittest.skip("output is not HTML")
    def test_extract_single_page_ipcc_toc_chap6(self):
        """
        ERROR extracts all text in chapter into single unstructured paragraph
        extract a single page which is the TableOfContents
        NOTE. pages 4 extracts "page 4" in 1-based but output file is 0-based.(Doh!)

        has x0 and x1 coordinates
,
        """
        assert Path(Resources.TEST_IPCC_CHAP06_PDF).exists(), f"expected {Resources.TEST_IPCC_CHAP06_PDF}"

        args = f"PDF --infile {Resources.TEST_IPCC_CHAP06_PDF} --pages 4 --outdir {AmiAnyTest.TEMP_HTML_IPCC_CHAP06} --flow True"
        AmiLib().run_command(args)
        outpath = Path(AmiAnyTest.TEMP_HTML_IPCC_CHAP06, "fulltext.flow_3.html")
        assert outpath.exists(), f"{outpath} should be created"

    @unittest.skip("No idea what the problem is")
    def test_ipcc_2_column__explore__fail(self):
        """
        Reads double column format of IPCC.
        FAILS - does not produce HTML body content
        (only creates
        <html>
          <head><meta/></head>
          <body>
            <div class="top">
              <div/>
            </div>
          </body>
        </html>)

        """
        infile = Path(Resources.TEST_IPCC_DIR, "wg2_03", "fulltext.pdf")
        pages = "5_8"  # total is 0_171 (172pp)
        outdir = Path(AmiAnyTest.TEMP_DIR, "html", "ar6", "wg2_chap03")
        args = f"PDF --infile {infile} --outdir {outdir} --pages {pages}"
        AmiLib().run_command(args)


class PDFCharacterTest(test.test_all.AmiAnyTest):
    """
    tests which cover the creation of character stream by PDF parsers
    (pdfminer and pdflumber)
    """

    def test_pdfplumber_debug_LTTextLine_LTTextBox_PMC1421(self):
        """
        read PDF and chunk into text_lines and text_boxes
        Keeps box coordinates but loses style
        uses pdfplumber
        (doesn't do whole document)
        """
        # need to pass in laparams, otherwise pdfplumber page would not
        # have high level pdfminer layout objects, only LTChars.
        assert Path(PMC1421_PDF).exists()
        logging.warning(f"PMC1421 is {PMC1421_PDF}")
        inpath = PMC1421_PDF
        pdfdebug = PDFDebug()
        pdf = pdfdebug.pdfplumber_debug(inpath, page_num=1)
        assert len(pdf.pages) == 5, f"expected 5 pages"

    # https://stackoverflow.com/questions/34606382/pdfminer-extract-text-with-its-font-information

    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_final_ipcc_format_debug_LONG(self):
        """
        Reads final format of IPCC reports (double column)
        PDFPLUMBER
        """
        assert Path(Resources.TEST_IPCC_WG2_CHAP03_PDF).exists()
        logging.warning(f"input is {Resources.TEST_IPCC_WG2_CHAP03_PDF}")
        inpath = Resources.TEST_IPCC_WG2_CHAP03_PDF
        pdfdebug = PDFDebug()
        pdf = pdfdebug.pdfplumber_debug(inpath, page_num=0)
        num_pages = len(pdf.pages)
        expected_pages = 172
        assert num_pages == expected_pages, f"expected {expected_pages} pages, found {num_pages}"
        for page in [
            # 0,
            # 10,
            13  # this has many graphics components and may be long
        ]:
            logger.info(f"=======page {page} 0-based=========")
            pdf = pdfdebug.pdfplumber_debug(inpath, page_num=page)

    @unittest.skipUnless(PDFTest.DEBUG, "too much output")
    def test_pdfminer_font_and_character_output(self):
        """Examines every character and annotates it
        Typical:
LTPage
  LTTextBoxHorizontal                               Journal of Medicine and Life Volume 7, Special Issue 3, 2014
    LTTextLineHorizontal                            Journal of Medicine and Life Volume 7, Special Issue 3, 2014
      LTChar                   KAAHHD+Calibri,Itali J
      LTChar                   KAAHHD+Calibri,Itali o
      LTChar                   KAAHHD+Calibri,Itali u
        """
        MAXITEM = 2
        from pathlib import Path
        from typing import Iterable, Any

        from pdfminer.high_level import extract_pages

        # recursive
        def show_ltitem_hierarchy(o: Any, depth=0):
            """Show location and text of LTItem and all its descendants"""
            debug = False
            debug = True
            if depth == 0:
                print('element                        fontname             text')
                print('------------------------------ -------------------- -----')

            name = get_indented_name(o, depth)
            if debug or name.strip() == "LTTextLineHorizontal":
                print(
                    f'{name :<30.30s} '
                    f'{get_optional_fontinfo(o):<20.20s} '
                    f'{get_optional_text(o)}'
                )

            if isinstance(o, Iterable):
                for i in list(o)[:MAXITEM]:
                    show_ltitem_hierarchy(i, depth=depth + 1)

        def get_indented_name(o: Any, depth: int) -> str:
            """Indented name of class"""
            return '  ' * depth + o.__class__.__name__

        def get_optional_fontinfo(o: Any) -> str:
            """Font info of LTChar if available, otherwise empty string"""
            name = o.__class__.__name__
            if hasattr(o, 'fontname') and hasattr(o, 'size'):
                if name == "LTChar":
                    dummy = ['_text', 'matrix', 'fontname', 'ncs', 'graphicstate', 'adv', 'upright', 'x0', 'y0', 'x1',
                             'y1',
                             'width', 'height', 'bbox', 'size', '__module__', '__doc__', '__init__', '__repr__',
                             'get_text',
                             'is_compatible', '__lt__', '__le__', '__gt__', '__ge__', 'set_bbox', 'is_empty',
                             'is_hoverlap',
                             'hdistance', 'hoverlap', 'is_voverlap', 'vdistance', 'voverlap', 'analyze', '__dict__',
                             '__weakref__', '__hash__', '__str__', '__getattribute__', '__setattr__', '__delattr__',
                             '__eq__',
                             '__ne__', '__new__', '__reduce_ex__', '__reduce__', '__subclasshook__',
                             '__init_subclass__',
                             '__format__', '__sizeof__', '__dir__', '__class__']
                    print(f"LTChar {o.__dir__()}//{o.ncs}//{o.graphicstate}//")
                return f'{o.fontname} {round(o.size)}pt {o.matrix} {o.ncs} {o.x1} {o.y1}'
            return ''

        def get_optional_text(o: Any) -> str:
            """Text of LTItem if available, otherwise empty string"""
            if hasattr(o, 'get_text'):
                return o.get_text().strip()
            return ''

        path = Path(PMC1421_PDF)
        pages = list(extract_pages(path))
        # this next debugs the character_stream
        show_ltitem_hierarchy(pages[0])

    @unittest.skipUnless(AmiAnyTest.run_long(),
                         "run occasionally; other methods may be better")
    def test_pdfminer_images(self):
        import pdfminer
        from pdfminer.image import ImageWriter
        from pdfminer.high_level import extract_pages

        path = Path(Resources.TEST_IPCC_CHAP06_PDF)
        pages = list(extract_pages(path))
        page = pages[10]

        def get_image(layout_object):
            if isinstance(layout_object, pdfminer.layout.LTImage):
                print(f"LTImage {layout_object.__dir__()}")
                return layout_object
            if isinstance(layout_object, pdfminer.layout.LTContainer):
                for child in layout_object:
                    return get_image(child)
            else:
                return None

        def save_images_from_page(page: pdfminer.layout.LTPage):
            images = list(filter(bool, map(get_image, page)))
            outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "chap6", "pdf miner")
            iw = ImageWriter(str(outdir))
            for image in images:
                iw.export_image(image)
                print(f" image {image}")

        save_images_from_page(page)

    def test_pdfminer_style(self):
        """Examines every character and annotates it
        Typical:
LTPage
  LTTextBoxHorizontal                               Journal of Medicine and Life Volume 7, Special Issue 3, 2014
    LTTextLineHorizontal                            Journal of Medicine and Life Volume 7, Special Issue 3, 2014
      LTChar                   KAAHHD+Calibri,Itali J
      LTChar                   KAAHHD+Calibri,Itali o
      LTChar                   KAAHHD+Calibri,Itali u
        """
        from pathlib import Path
        from typing import Iterable, Any

        from pdfminer.high_level import extract_pages

        def show_ltitem_hierarchy(o: Any, depth=0):
            """Show location and text of LTItem and all its descendants"""
            MAXITEM = 2
            MAXITEM = 4
            if depth == 0:
                print('element                        fontname             text')
                print('------------------------------ -------------------- -----')

            print(
                f'{get_indented_name(o, depth):<30.30s} '
                f'{get_optional_fontinfo(o):<20.20s} '
                f'{get_optional_text(o)}'
            )

            if isinstance(o, Iterable):
                for i in list(o)[:MAXITEM]:
                    show_ltitem_hierarchy(i, depth=depth + 1)

        def get_indented_name(o: Any, depth: int) -> str:
            """Indented name of class"""
            return '  ' * depth + o.__class__.__name__

        def get_optional_fontinfo(o: Any) -> str:
            """Font info of LTChar if available, otherwise empty string"""
            if hasattr(o, 'fontname') and hasattr(o, 'size'):
                return f'{o.fontname} {round(o.size)}pt'
            return ''

        def get_optional_text(o: Any) -> str:
            """
            Text of LTItem if available, otherwise empty string
            """
            if hasattr(o, 'get_text'):
                return f"{o.get_text().strip()}"
            return ''

        path = Path(PMC1421_PDF)
        pages = list(extract_pages(path))
        # this next debugs the character_stream
        show_ltitem_hierarchy(pages[0])

    def test_pdfminer_text_html_xml(self):
        # Use `pip3 install pdfminer.six` for python3
        """
        runs pdfinterpreter/converter over 5-page article and creates html and xml versions
        """
        fmt = "html"
        maxpages = 0
        path = Path(PMC1421_PDF)
        result = PDFParser().convert_pdf_CURRENT(
            path=str(path),
            fmt=fmt,
            maxpages=maxpages
        )
        html_dir = make_html_dir()
        with Util.open_write_utf8(Path(html_dir, f"pmc4121.{fmt}")) as f:
            f.write(result)
            print(f"wrote {f.name}")


    def test_pdfplumber_full_page_info_LOWLEVEL_CHARS(self):
        """The definitive catalog of all objects on a page"""
        assert PMC1421_PDF.exists(), f"{PMC1421_PDF} should exist"

        include_float = False # don't test if values are floats
        # TODO use pytest.approx or similar

        # also ['_text', 'matrix', 'fontname', 'ncs', 'graphicstate', 'adv', 'upright', 'x0', 'y0', 'x1', 'y1',
        # 'width', 'height', 'bbox', 'size', 'get_text',
        # 'is_compatible', 'set_bbox', 'is_empty', 'is_hoverlap',
        # 'hdistance', 'hoverlap', 'is_voverlap', 'vdistance', 'voverlap', 'analyze', ']
        with pdfplumber.open(PMC1421_PDF) as pdf:
            first_page = pdf.pages[0]
            """
            dir: ['pdf', 'root_page', 'page_obj', 'page_number', 'rotation', 'initial_doctop', 'cropbox', 'mediabox', 
            'bbox', 'cached_properties', 'is_original', 'pages', 'width', 
            'height', 'layout', 'annots', 'hyperlinks', 'objects', 'process_object', 'iter_layout_objects', 'parse_objects', 
            'debug_tablefinder', 'find_tables', 'extract_tables', 'extract_table', 'get_text_layout', 'search', 'extract_text',
             'extract_words', 'crop', 'within_bbox', 'filter', 'dedupe_chars', 'to_image', 'to_dict', 
             'flush_cache', 'rects', 'lines', 'curves', 'images', 'chars', 'textboxverticals', 'textboxhorizontals', 
             'textlineverticals', 'textlinehorizontals', 'rect_edges', 'edges', 'horizontal_edges', 'vertical_edges', 'to_json',
              'to_csv', ]
            """
            assert first_page.page_number == 1
            assert first_page.rotation == 0
            assert first_page.initial_doctop == 0
            # cropbox and medibox seem to vary beteween lists and tuples on different versionns of Python
            # assert first_page.cropbox == (0, 0, 595.22, 842)
            # assert first_page.mediabox == (0, 0, 595.22, 842)
            # assert first_page.bbox == (0, 0, 595.22, 842)
            assert first_page.cached_properties == ['_rect_edges', '_curve_edges', '_edges', '_objects', '_layout']
            assert first_page.is_original
            assert first_page.pages is None
            assert first_page.width == 595.22
            assert first_page.height == 842
            # assert first_page.layout: < LTPage(1)
            # 0.000, 0.000, 595.220, 842.000
            # rotate = 0 >
            assert first_page.annots == []
            assert first_page.hyperlinks == []
            assert len(first_page.objects) == 2
            assert type(first_page.objects) is dict
            assert list(first_page.objects.keys()) == ['char', 'line']
            assert len(first_page.objects['char']) == 4411
            if not include_float:
                print(f"omitting float comparisons")
                return
            assert first_page.objects['char'][:2] == [
                {'matrix': (9, 0, 0, 9, 319.74, 797.4203),
                 'mcid': None,
                 'ncs': 'DeviceCMYK',
                 'non_stroking_pattern': None,
                 'stroking_pattern': None,
                 'tag': None,
                 'fontname': 'KAAHHD+Calibri,Italic',
                 'adv': 0.319,
                 'upright': True,
                 'x0': 319.74, 'y0': 795.1703, 'x1': 322.611, 'y1': 804.1703,
                 'width': 2.870999999999981, 'height': 9.0, 'size': 9.0,
                 'object_type': 'char', 'page_number': 1,
                 'text': 'J', 'stroking_color': None, 'non_stroking_color': (0.86667, 0.26667, 1, 0.15294),
                 'top': 37.8297, 'bottom': 46.8297, 'doctop': 37.8297
                 },
                {'matrix': (9, 0, 0, 9, 322.6092, 797.4203), 'fontname': 'KAAHHD+Calibri,Italic', 'adv': 0.513,
                 'mcid': None,
                 'ncs': 'DeviceCMYK',
                 'non_stroking_pattern': None,
                 'stroking_pattern': None,
                 'tag': None,
                 'upright': True,
                 'x0': 322.6092, 'y0': 795.1703, 'x1': 327.2262, 'y1': 804.1703, 'width': 4.617000000000019,
                 'height': 9.0, 'size': 9.0,
                 'object_type': 'char', 'page_number': 1, 'text': 'o', 'stroking_color': None,
                 'non_stroking_color': (0.86667, 0.26667, 1, 0.15294),
                 'top': 37.8297, 'bottom': 46.8297, 'doctop': 37.8297},
            ], f"first_page.objects['char'][0]  {first_page.objects['char'][0]}"

            assert len(first_page.objects['line']) == 1, f" len(first_page.objects['line'])"
            assert first_page.objects['line'][0] == {
                'bottom': 48.24000000000001,
                'doctop': 48.24000000000001,
                'evenodd': False,
                'fill': False,
                'height': 0.0,
                'linewidth': 1,
                'mcid': None,
                'non_stroking_color': (0,),
                'non_stroking_pattern': None,
                'object_type': 'line',
                'page_number': 1,
                #  this may be different y-coord system
                # 'pts': [(56.7, 793.76), (542.76, 793.76)],
                'pts': [(56.7, 48.24000000000001), (542.76, 48.24000000000001)],
                'stroke': True,
                'stroking_color': (0.3098, 0.24706, 0.2549, 0),
                'stroking_pattern': None,
                'tag': None,
                'top': 48.24000000000001,
                'width': 486.06,
                'x0': 56.7,
                'x1': 542.76,
                'y0': 793.76,
                'y1': 793.76
            }, f"first_page.objects['line'][0]  {first_page.objects['line'][0]}"
            # assert first_page.process_object(obj) == [], f"process_object (LTItem) {first_page.process_object()}"

            assert first_page.find_tables() == []
            assert first_page.extract_tables() == []
            assert first_page.extract_text()[:20] == "Journal of Medicine "
            assert first_page.extract_words()[:3] == [
                {'text': 'Journal', 'x0': 319.74, 'x1': 346.2432, 'top': 37.8297, 'doctop': 37.8297, 'bottom': 46.8297,
                 'upright': True, 'direction': 1},
                {'text': 'of', 'x0': 348.2808, 'x1': 355.641, 'top': 37.8297, 'doctop': 37.8297, 'bottom': 46.8297,
                 'upright': True, 'direction': 1},
                {'text': 'Medicine', 'x0': 357.6786, 'x1': 391.08299999999997, 'top': 37.8297, 'doctop': 37.8297,
                 'bottom': 46.8297, 'upright': True, 'direction': 1}]
            assert first_page.rects == []
            assert first_page.lines == [
                {'x0': 56.7, 'y0': 793.76, 'x1': 542.76, 'y1': 793.76, 'width': 486.06, 'height': 0.0,
                 # 'pts': [(56.7, 793.76), (542.76, 793.76)],
                 # looks like coordinate system was changed
                 'pts': [(56.7, 48.24000000000001), (542.76, 48.24000000000001)],
                 'linewidth': 1, 'stroke': True, 'fill': False,
                 'evenodd': False, 'stroking_color': (0.3098, 0.24706, 0.2549, 0),
                 'mcid': None,
                 'non_stroking_color': (0,),
                 'non_stroking_pattern': None,
                 'object_type': 'line', 'page_number': 1,
                 'stroking_pattern': None,
                 'tag': None,
                 'top': 48.24000000000001, 'bottom': 48.24000000000001,
                 'doctop': 48.24000000000001}]

            assert first_page.curves == []
            assert first_page.images == []
            assert len(first_page.chars) == 4411  # same as first_page.objects['char'] I think
            assert first_page.chars[:1] == [{'adv': 0.319,
  'bottom': 46.8297,
  'doctop': 37.8297,
  'fontname': 'KAAHHD+Calibri,Italic',
  'height': 9.0,
  'matrix': (9, 0, 0, 9, 319.74, 797.4203),
  'mcid': None,
  'ncs': 'DeviceCMYK',
  'non_stroking_color': (0.86667, 0.26667, 1, 0.15294),
  'non_stroking_pattern': None,
  'object_type': 'char',
  'page_number': 1,
  'size': 9.0,
  'stroking_color': None,
  'stroking_pattern': None,
  'tag': None,
  'text': 'J',
  'top': 37.8297,
  'upright': True,
  'width': 2.870999999999981,
  'x0': 319.74,
  'x1': 322.611,
  'y0': 795.1703,
  'y1': 804.1703}]

            """first_page.objects['char']"""
            assert first_page.chars[0] == {'adv': 0.319,
 'bottom': 46.8297,
 'doctop': 37.8297,
 'fontname': 'KAAHHD+Calibri,Italic',
 'height': 9.0,
 'matrix': (9, 0, 0, 9, 319.74, 797.4203),
 'mcid': None,
 'ncs': 'DeviceCMYK',
 'non_stroking_color': (0.86667, 0.26667, 1, 0.15294),
 'non_stroking_pattern': None,
 'object_type': 'char',
 'page_number': 1,
 'size': 9.0,
 'stroking_color': None,
 'stroking_pattern': None,
 'tag': None,
 'text': 'J',
 'top': 37.8297,
 'upright': True,
 'width': 2.870999999999981,
 'x0': 319.74,
 'x1': 322.611,
 'y0': 795.1703,
 'y1': 804.1703}
            first_100 = first_page.extract_text()[:100]
            assert first_100.startswith("Journal of Medicine and Life Volume 7, Special Issue 3")
            assert 612 < len(first_page.extract_words()) < 616
            word0 = first_page.extract_words()[0]
            assert list(word0.keys()) == ['text', 'x0', 'x1', 'top', 'doctop', 'bottom', 'upright', 'direction']

            # too fragile
            assert first_page.edges == [{'bottom': 48.24000000000001,
  'doctop': 48.24000000000001,
  'evenodd': False,
  'fill': False,
  'height': 0.0,
  'linewidth': 1,
  'mcid': None,
  'non_stroking_color': (0,),
  'non_stroking_pattern': None,
  'object_type': 'line',
  'orientation': 'h',
  'page_number': 1,
  'pts': [(56.7, 48.24000000000001), (542.76, 48.24000000000001)],
  'stroke': True,
  'stroking_color': (0.3098, 0.24706, 0.2549, 0),
  'stroking_pattern': None,
  'tag': None,
  'top': 48.24000000000001,
  'width': 486.06,
  'x0': 56.7,
  'x1': 542.76,
  'y0': 793.76,
  'y1': 793.76}]
            assert first_page.horizontal_edges == [{'bottom': 48.24000000000001,
  'doctop': 48.24000000000001,
  'evenodd': False,
  'fill': False,
  'height': 0.0,
  'linewidth': 1,
  'mcid': None,
  'non_stroking_color': (0,),
  'non_stroking_pattern': None,
  'object_type': 'line',
  'orientation': 'h',
  'page_number': 1,
  'pts': [(56.7, 48.24000000000001), (542.76, 48.24000000000001)],
  'stroke': True,
  'stroking_color': (0.3098, 0.24706, 0.2549, 0),
  'stroking_pattern': None,
  'tag': None,
  'top': 48.24000000000001,
  'width': 486.06,
  'x0': 56.7,
  'x1': 542.76,
  'y0': 793.76,
  'y1': 793.76}]
            assert first_page.vertical_edges == []
            assert first_page.textboxverticals == []
            assert first_page.textboxhorizontals == []
            assert first_page.textlineverticals == []
            assert first_page.textlinehorizontals == []

            # CSV
            csv = first_page.to_csv()
            assert type(csv) is str
            rows = csv.split("\r")
            assert len(rows) == 4414
            assert rows[0] == "object_type,page_number,x0,x1,y0,y1,doctop,top,bottom,width,height,adv,evenodd,fill,fontname,linewidth,matrix,mcid,ncs,non_stroking_color,non_stroking_pattern,pts,size,stroke,stroking_color,stroking_pattern,tag,text,upright"
            assert rows[0].split() == ['object_type,page_number,x0,x1,y0,y1,doctop,top,bottom,width,height,adv,evenodd,fill,fontname,linewidth,matrix,mcid,ncs,non_stroking_color,non_stroking_pattern,pts,size,stroke,stroking_color,stroking_pattern,tag,text,upright']
            assert rows[1].split() == ['char,1,319.74,322.611,795.1703,804.1703,37.8297,37.8297,46.8297,2.870999999999981,9.0,0.319,,,"KAAHHD+Calibri,Italic",,"(9,',
 '0,',
 '0,',
 '9,',
 '319.74,',
 '797.4203)",,DeviceCMYK,"(0.86667,',
 '0.26667,',
 '1,',
 '0.15294)",,,9.0,,,,,J,1']

            #        assert rows[1] == 'char,1,319.74,322.611,795.1703,804.1703,37.8297,37.8297,46.8297,2.870999999999981,9.0,0.319,,,"KAAHHD+Calibri,Italic",,"(9, '\n '0, 0, 9, 319.74, 797.4203)","(0.86667, 0.26667, 1, 0.15294)",,9.0,,,J,1'

            assert first_page.chars[0:1] == [{'adv': 0.319,
  'bottom': 46.8297,
  'doctop': 37.8297,
  'fontname': 'KAAHHD+Calibri,Italic',
  'height': 9.0,
  'matrix': (9, 0, 0, 9, 319.74, 797.4203),
  'mcid': None,
  'ncs': 'DeviceCMYK',
  'non_stroking_color': (0.86667, 0.26667, 1, 0.15294),
  'non_stroking_pattern': None,
  'object_type': 'char',
  'page_number': 1,
  'size': 9.0,
  'stroking_color': None,
  'stroking_pattern': None,
  'tag': None,
  'text': 'J',
  'top': 37.8297,
  'upright': True,
  'width': 2.870999999999981,
  'x0': 319.74,
  'x1': 322.611,
  'y0': 795.1703,
  'y1': 804.1703}]
            assert type(first_page.extract_text()) is str
            for ch in first_page.chars:  # prints all text as a single line
                logger.debug(ch.get("text"), end="")

    def test_make_styled_text_chunks_PDFPlumber(self):
        """
        PDFPlumber does not keep styles for words and text (it lumps them all together)
        This builds chunks of constant style, font-size and y-coord
        """
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "ar6", "chap6")
        with pdfplumber.open(Resources.TEST_IPCC_CHAP06_PDF) as pdf:
            pages = list(pdf.pages)
            for page in pages[:1]:
                PDFDebug().debug_page_properties(page, debug=[WORDS, IMAGES], outdir=outdir)

    def test_debug_page_properties_chap6_word_count_and_images_data_wg3_old__example(self):
        """debug the old-style IPCC WG3 PDF objects (crude)
        outputs wordcount for page, and any image data.
        Would be better if we knew how to read PDFStream
        """
        maxpage = 9  # images on page 8, and 9
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "ar6", "chap6")
        pdf_debug = PDFDebug()

        with pdfplumber.open(Resources.TEST_IPCC_CHAP06_PDF) as pdf:
            pages = list(pdf.pages)
            for page in pages[:maxpage]:
                pdf_debug.debug_page_properties(page, debug=[WORDS, IMAGES], outdir=outdir)
        pdf_debug.write_summary(outdir=outdir)
        logger.debug(f"pdf_debug {pdf_debug.image_dict}\n outdir {outdir}")
        assert maxpage != 9 or pdf_debug.image_dict == {
            ((1397, 779), 143448): (8, (72.0, 523.3), (412.99, 664.64)),
            ((1466, 655), 122016): (8, (72.0, 523.3), (203.73, 405.38)),
            ((1634, 854), 204349): (9, (80.9, 514.25), (543.43, 769.92))
        }

    def test_debug_page_properties_chap6_word_count_and_images_data_wg2_new__example(self):
        """debug the new style IPCC PDF objects (crude)
        outputs wordcount for page, and any image data.
        Would be better if we knew how to read PDFStream
        """
        maxpage = 4  # images on page 8, and 9
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "wg2_chap3")
        pdf_debug = PDFDebug()

        with pdfplumber.open(Resources.TEST_IPCC_WG2_CHAP03_PDF) as pdf:
            pages = list(pdf.pages)
            logger.debug(f"PDF pages: {len(pages)}")
            for page in pages[:maxpage]:
                pdf_debug.debug_page_properties(page, debug=[WORDS, IMAGES], outdir=outdir)
        pdf_debug.write_summary(outdir=outdir)
        logger.debug(f"pdf_debug {pdf_debug.image_dict}\n outdir {outdir}")

        # assert maxpage != 9 or pdf_debug.image_dict == {
        #     ((1397, 779), 143448): (8, (72.0, 523.3), (412.99, 664.64)),
        #     ((1466, 655), 122016): (8, (72.0, 523.3), (203.73, 405.38)),
        #     ((1634, 854), 204349): (9, (80.9, 514.25), (543.43, 769.92))
        # }

    def test_page_properties_pmc__debug(self):
        """ high-level debug the PDF objects (crude) uses PDFDebug on 5-page document
        finds WORDS (count) and IMAGE details
        """

        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "pmc1421", "images")
        infile = PMC1421_PDF
        PDFDebug.debug_pdf(infile, outdir)

    run_me = False

    # wg2_3 is 20 Mb and has many vectors/boxes

    @unittest.skipUnless(PDFTest.VERYLONG or run_me, "complete chapter")
    def test_page_properties_ipcc_wg2_3__debug_LONG(self):
        """ high-level debug the PDF objects (crude) uses PDFDebug on large document with many graphics components
        PDFPLUMBER
        finds WORDS (count) and IMAGE details
        about 2 minutesw

        """
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "wg2_3")
        infile = IPCC_WG2_3_PDF
        pdf_debug = PDFDebug()
        pdf_debug.debug_pdf(infile, outdir, debug_options=[WORDS, IMAGES, CURVES, TEXTS], page_len=15)

    @unittest.skipUnless(PDFTest.VERYLONG, "complete chapter - has graphics")
    def test_page_properties_ipcc_wg2__debug_LONG(self):
        """ high-level debug the PDF objects (crude) uses PDFDebug on 5-page document
        finds WORDS (count) and IMAGE details
        """
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "wg2_3")
        infile = IPCC_WG2_3_PDF
        PDFDebug.debug_pdf(infile, outdir)

    @unittest.skipUnless(PDFTest.VERYLONG or True, "complete chapter wg3 15")
    @unittest.skipUnless(AmiAnyTest.run_long(), "run occasionally")
    def test_wg3_15_character_and_page_properties(self):
        """
        Initia
        """
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "ar6", "Chapter15")
        infile = Path(Resources.TEST_IPCC_CHAP15, "fulltext.pdf")
        PDFDebug.debug_pdf(infile, outdir, debug_options=[WORDS, IMAGES])

    def test_download_all_hlab_shifts_convert_to_html(self):
        url = "https://highleveladvisoryboard.org/breakthrough/pdf/56892_UNU_HLAB_report_Final_LOWRES.pdf"
        outdir = Path(UNHLAB_DIR, "downloads")
        outdir.mkdir(exist_ok=True)
        file = self.download_url(url, outdir=Path(UNHLAB_DIR, "downloads"))
        logger.debug(f"{file}")

    def download_row(self, tr, outdir):
        a_elems = tr.xpath("td/a")
        for a_elem in a_elems:
            if a_elem.text == "Access":
                url = a_elem.attrib['href']
                filepath = self.download_url(url, outdir)
                print(f" saved {filepath}")

        print(f"=================")

    def download_url(self, url, outdir):
        print(f"\n >>> {url} ")
        response = requests.get(url, stream=True)
        # isolate PDF filename from URL
        split_ = url.split("/")[-1]
        pdf_file_name = str(Path(outdir, split_))
        if response.status_code == 200:
            # Save in current working directory
            # filepath = os.path.join(os.getcwd(), pdf_file_name)
            filepath = pdf_file_name
            try:
                with open(filepath, 'wb') as pdf_object:
                    pdf_object.write(response.content)
                    print(f'{filepath} was successfully saved!')
                    return filepath
            except Exception as e:
                print(f"EXCEPT {e}")
                return None
        else:
            print(f'Could not download {pdf_file_name},HTTP response status code: {response.status_code}')
            return None


class PDFSVGTest(test.test_all.AmiAnyTest):
    # all are skipUnless
    ADMIN = True and AmiAnyTest.ADMIN
    CMD = True and AmiAnyTest.CMD
    DEBUG = True and AmiAnyTest.DEBUG
    LONG = True and AmiAnyTest.LONG
    NET = True and AmiAnyTest.NET
    OLD = True and AmiAnyTest.OLD
    NYI = True and AmiAnyTest.NYI
    USER = True and AmiAnyTest.USER

    # SVG = True
    SVG = False  # too many things need updating

    def make_full_chap_10_draft_html_from_svg(pretty_print, use_lines, rotated_text=False):
        """
        reads SVG output from ami3/pdfbox and converts to HTML
        used by several tests at present and will be intergrated
        :param pretty_print: pretty print the HTML. Warning may introduce whitespace
        :param use_lines: output is CompositeLines. Not converted into running text (check)
        :param rotated_text: include/ignore tex# ts with non-zero @rotateDegress attribute
        """
        if not Path(FINAL_DRAFT_DIR, f"fulltext-page.2912.svg").exists():
            raise Exception("must have SVG from ami3")
        for page_index in CURRENT_RANGE:
            page_path = Path(FINAL_DRAFT_DIR, f"fulltext-page.{page_index}.svg")
            html_path = Path(AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR, f"page.{page_index}.html")
            AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR.mkdir(exist_ok=True, parents=True)
            ami_page = AmiPage.create_page_from_svg(page_path, rotated_text=rotated_text)
            ami_page.write_html(html_path, pretty_print, use_lines)

    @unittest.skipUnless("enviroment", ADMIN)
    def test_findall_svg_and_find_texts(self):
        """find climate10_:text elements
        """
        assert PAGE_9.exists(), f"{PAGE_9} should exist"
        page9_elem = lxml.etree.parse(str(PAGE_9))
        texts = page9_elem.findall(f"//{{{SVG_NS}}}text")
        assert len(texts) == 108

    @unittest.skipUnless(SVG, "svg")
    def test_get_text_attribs(self):
        """find various SVG attributes, including 'style'
        """
        ami_page = AmiPage.create_page_from_svg(PAGE_9)
        # <climate10_:text> element
        text0 = ami_page.get_svg_text(0)
        assert text0.svg_text_elem.tag == f"{{{SVG_NS}}}text"
        # single Y-coord
        assert text0.svg_text_elem.attrib.get(Y) == '44.76'
        # list of X-coords
        assert text0.svg_text_elem.attrib.get(X) == \
               '72.0,79.201,84.721,90.241,96.961,104.162,111.363,117.482,124.798,127.288,258.242,263.762,268.' \
               '802,276.601,284.401,288.841,292.202,297.241,299.761,303.001,308.041,311.402,313.921,319.441,' \
               '324.481,327.241,330.001,334.441,339.481,347.28,351.601,356.641,361.081,364.442,368.28,370.77,' \
               '448.08,451.439,456.96,463.563,470.167,472.687,480.006,486.61,491.651,494.171,503.533,510.718,' \
               '513.238,516.594,519.951,523.307'
        # list of character-widths (from publisher) (multiply by font-size to get pixels)
        assert text0.svg_text_elem.attrib.get(f"{{{SVGX_NS}}}width") == \
               '0.72,0.56,0.56,0.67,0.72,0.72,0.61,0.72,0.25,0.55,0.56,0.5,0.78,0.78,0.44,0.33,0.5,0.25,0.33,' \
               '0.5,0.33,0.25,0.56,0.5,0.28,0.28,0.44,0.5,0.78,0.44,0.5,0.44,0.33,0.39,0.25,0.55,0.33,0.56,' \
               '0.67,0.67,0.25,0.72,0.67,0.5,0.25,0.94,0.72,0.25,0.33,0.33,0.33,0.25'
        # style (dict-like collection of name-value pairs
        assert text0.svg_text_elem.get(STYLE) == \
               'fill:rgb(0,0,0);font-family:TimesNewRomanPSMT;font-size:9.96px;stroke:none;'
        # text-content without tags
        text_content = text0.get_text_content()
        assert text_content == "APPROVED Summary for Policymakers IPCC AR6 WG III "
        assert len(text_content) == 50  # some spaces have been elided??

    @unittest.skipUnless(SVG, "svg")
    def test_get_text_attrib_vals(self):
        """more attributes and convenience methods"""
        ami_page = AmiPage.create_page_from_svg(PAGE_9)
        # <climate10_:text> element
        ami_text0 = ami_page.get_svg_text(0)
        x_coords = ami_text0.get_x_coords()
        assert x_coords == [
            72.0, 79.201, 84.721, 90.241,
            96.961, 104.162, 111.363, 117.482, 124.798, 127.288, 258.242, 263.762, 268.802,
            276.601, 284.401, 288.841, 292.202, 297.241, 299.761,
            303.001, 308.041, 311.402, 313.921, 319.441, 324.481, 327.241, 330.001,
            334.441, 339.481, 347.28, 351.601, 356.641, 361.081, 364.442,
            368.28, 370.77, 448.08, 451.439, 456.96, 463.563, 470.167,
            472.687, 480.006, 486.61, 491.651, 494.171, 503.533, 510.718, 513.238, 516.594, 519.951, 523.307]
        assert len(x_coords) == 52

        widths = ami_text0.get_widths()
        assert widths == [
            0.72, 0.56, 0.56, 0.67, 0.72, 0.72, 0.61,
            0.72, 0.25, 0.55, 0.56, 0.5, 0.78, 0.78, 0.44, 0.33, 0.5, 0.25, 0.33, 0.5, 0.33,
            0.25, 0.56, 0.5, 0.28, 0.28, 0.44, 0.5, 0.78, 0.44, 0.5, 0.44, 0.33,
            0.39, 0.25, 0.55, 0.33, 0.56, 0.67, 0.67, 0.25, 0.72, 0.67, 0.5, 0.25, 0.94, 0.72, 0.25, 0.33, 0.33,
            0.33, 0.25
        ]
        assert len(widths) == 52

        # SVG style dict from SVG@style attribute
        style_dict = ami_text0.extract_style_dict_from_svg()
        # assert style_dict == {'fill': 'rgb(0,0,0)',\n 'font-family': 'TimesNewRomanPSMT',\n 'font-size': '9.96px',\n 'stroke': 'none'}
        assert style_dict[FILL] == 'rgb(0,0,0)'
        assert style_dict[FONT_FAMILY] == 'TimesNewRomanPSMT'
        assert style_dict[FONT_SIZE] == '9.96px'
        assert style_dict[STROKE] == 'none'
        assert ami_text0.get_font_size() == 9.96

    @unittest.skipUnless(SVG, "svg")
    def test_create_text_lines_page6(self):
        """creation of AmiPage from SVG page and creation of text spans"""
        page = AmiPage.create_page_from_svg(PAGE_6)
        page.create_text_spans(sort_axes=SORT_XY)
        assert 70 >= len(page.text_spans) >= 60

    @unittest.skipUnless(SVG, "svg")
    def test_create_html_from_svg(self):
        """
        Test 10 pages
        writes html. These may be used in further tests but should be hand copied
        """
        pretty_print = True
        use_lines = True
        svg_dir = Resources.TEST_CLIMATE_10_SVG_DIR
        html_dir = Path(AmiAnyTest.TEMP_DIR, "climate10")
        html_dir.mkdir(exist_ok=True, parents=True)
        for page_index in range(1, 9):
            page_path = Path(svg_dir, f"fulltext-page.{page_index}.svg")
            html_path = Path(html_dir, f"page.{page_index}.html")
            html_dir.mkdir(exist_ok=True, parents=True)
            ami_page = AmiPage.create_page_from_svg(page_path)
            ami_page.write_html(html_path, pretty_print, use_lines)
            assert html_path.exists(), f"{html_path} exists"

    # @unittest.skipUnless(SVG, "svg")
    @unittest.skip("Doesn't do SVG")
    def test_create_html_in_selection_from_svg(self):
        """
        Test 10 pages
        """
        pretty_print = True
        use_lines = True
        # selection = range(1, 2912)
        page_selection = range(1, 50)
        counter = 0
        counter_tick = 20
        html_out_dir = Path(AmiAnyTest.TEMP_DIR, "climate10")
        for page_index in page_selection:
            if counter % counter_tick == 0:
                print(f".", end="")
            page_path = Path(FINAL_DRAFT_DIR, f"fulltext-page.{page_index}.svg")
            html_path = Path(html_out_dir, f"page.{page_index}.html")
            html_out_dir.mkdir(exist_ok=True, parents=True)
            ami_page = AmiPage.create_page_from_svg(page_path, rotated_text=False)
            ami_page.write_html(html_path, pretty_print, use_lines)
            counter += 1
            assert html_path.exists(), f"{html_path} exists"

    # @unittest.skipUnless(SVG, "svg")
    @unittest.skip("doesn't do SVG")
    def test_create_chapters_through_svg(self):
        pretty_print = True
        use_lines = True
        self.make_full_chap_10_draft_html_from_svg(pretty_print, use_lines)
        selection = CURRENT_RANGE
        temp_dir = Path(AmiAnyTest.TEMP_DIR, "climate10")
        temp_dir.mkdir(exist_ok=True, parents=True)
        for page_index in selection:
            html_path = Path(temp_dir, f"page.{page_index}.html")
            with open(html_path, "r") as h:
                xml = h.read()
            root = lxml.etree.fromstring(xml)
            spans = root.findall(f"./{H_BODY}/{H_P}/{H_SPAN}")
            assert type(spans[0]) is lxml.etree._Element, f"expected str got {type(spans[0])}"
            assert len(HtmlUtil.get_text_content(spans[0])) > 0
            span = None
            chapter = ""
            # bug in parsing line 0
            if Publication.is_chapter_or_tech_summary(HtmlUtil.get_text_content(spans[0])):
                span = spans[0]
            if span is None and Publication.is_chapter_or_tech_summary(HtmlUtil.get_text_content(spans[1])):
                span = spans[1]
            if span is None:
                print(f"p:{page_index}, {HtmlUtil.get_text_content(spans[0])}, {HtmlUtil.get_text_content(spans[1])}")
            else:
                chapter = HtmlUtil.get_text_content(span)
                print("CHAP ", chapter)

    @unittest.skip("obsolete")
    @unittest.skipUnless(SVG, "svg")
    @unittest.skipUnless(CMD, "command")
    @unittest.skip("doesn't do SVG")
    def test_svg2page(self):
        proj = Resources.TEST_CLIMATE_10_PROJ_DIR
        args = f"--proj {proj} --apply svg2page"
        AmiLib().run_command(args)

    @unittest.skipUnless("enviroment", ADMIN)
    @unittest.skip("doesn't do SVG")
    def test_findall_svg_and_find_texts(self):
        """find climate10_:text elements
        """
        assert PAGE_9.exists(), f"{PAGE_9} should exist"
        page9_elem = lxml.etree.parse(str(PAGE_9))
        texts = page9_elem.findall(f"//{{{SVG_NS}}}text")
        assert len(texts) == 108

    @unittest.skipUnless(SVG, "svg")
    @unittest.skip("doesn't do SVG")
    def test_create_html_from_svg(self):
        """
        Test 10 pages
        """
        pretty_print = True
        use_lines = True
        svg_dir = Resources.TEST_CLIMATE_10_SVG_DIR
        html_dir = Path(AmiAnyTest.TEMP_DIR, "climate10")
        html_dir.mkdir(exist_ok=True, parents=True)
        for page_index in range(1, 9):
            page_path = Path(svg_dir, f"fulltext-page.{page_index}.svg")
            html_path = Path(html_dir, f"page.{page_index}.html")
            html_dir.mkdir(exist_ok=True, parents=True)
            ami_page = AmiPage.create_page_from_svg(page_path)
            ami_page.write_html(html_path, pretty_print, use_lines)
            assert html_path.exists(), f"{html_path} exists"

    @unittest.skipUnless(SVG and Path(FINAL_DRAFT_DIR).exists(), "svg")
    def test_create_html_in_selection_from_svg(self):
        """
        Test 10 pages
        """
        pretty_print = True
        use_lines = True
        # selection = range(1, 2912)
        page_selection = range(1, 50)
        counter = 0
        counter_tick = 20
        html_out_dir = AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR
        for page_index in page_selection:
            if counter % counter_tick == 0:
                print(f".", end="")
            page_path = Path(FINAL_DRAFT_DIR, f"fulltext-page.{page_index}.svg")
            html_path = Path(html_out_dir, f"page.{page_index}.html")
            assert not html_path.is_dir(), f"{html_path} is not a directory"
            html_out_dir.mkdir(exist_ok=True, parents=True)
            ami_page = AmiPage.create_page_from_svg(page_path, rotated_text=False)
            ami_page.write_html(html_path, pretty_print, use_lines)
            counter += 1
            assert html_path.exists(), f"{html_path} exists"
            assert not html_path.is_dir(), f"{html_path} is not a directory"
        return

    @unittest.skipUnless(SVG and Path(FINAL_DRAFT_DIR).exists(), "svg")
    def test_create_chapters_through_svg(self):
        pretty_print = True
        use_lines = True
        make_full_chap_10_draft_html_from_svg(pretty_print, use_lines)
        selection = CURRENT_RANGE
        temp_dir = AmiAnyTest.CLIMATE_10_HTML_TEMP_DIR
        for page_index in selection:
            html_path = Path(temp_dir, f"page.{page_index}.html")
            with open(html_path, "r") as h:
                xml = h.read()
            root = lxml.etree.fromstring(xml)
            spans = root.findall(f"./{H_BODY}/{H_P}/{H_SPAN}")
            assert type(spans[0]) is lxml.etree._Element, f"expected str got {type(spans[0])}"
            assert len(HtmlUtil.get_text_content(spans[0])) > 0
            span = None
            chapter = ""
            # bug in parsing line 0
            if Publication.is_chapter_or_tech_summary(HtmlUtil.get_text_content(spans[0])):
                span = spans[0]
            if span is None and Publication.is_chapter_or_tech_summary(HtmlUtil.get_text_content(spans[1])):
                span = spans[1]
            if span is None:
                print(f"p:{page_index}, {HtmlUtil.get_text_content(spans[0])}, {HtmlUtil.get_text_content(spans[1])}")
            else:
                chapter = HtmlUtil.get_text_content(span)
                print("CHAP ", chapter)

    # =====================================================================================================
    # =====================================================================================================

    MAX_RECT = 5
    MAX_CURVE = 5
    MAX_TABLE = 5
    MAX_ROW = 10
    MAX_IMAGE = 5


def ensure_ul(para):

    pass



class PDFSlidesTest(AmiAnyTest):
    """
    for PDFs created as PPT dump
    """

    def test_read_ab_slidedeck(self):
        """(
        reads a slide deck and converts to running text
        """

        chapno = 1
        infile = Path(Resources.TEST_RESOURCES_DIR, "pdf", f"breward_{chapno}.pdf")
        outdir = Path(Resources.TEMP_DIR, "pdf", "ab_slides")

        htmlx, pdfToString = PDFSlide.create_html_chapter(chapno, infile)

        expected = """

page ============ 0 ==========
Climate Change
What to think and what to do
1. Framing Climate Change
We don’t inherit the Earth from our ancestors, we borrow it from our children.
Climate Change – What to think and What to do – Alastair Breward – Autumn 2023 – U3AC – Seminar 1

page ============ 1 ==========
Framing Climate Ch"""
        maxchar = 330
        assert expected == pdfToString[:maxchar]
        outfile = Path(Resources.TEMP_DIR, "pdf", "breward", f"chap_{chapno}.html")
        HtmlUtil.write_html_elem(htmlx, outfile)


    def test_convert_multiple_slidedecks(self):
        """
        read 8 chapters from Alastair Breward
        """
        pdfs_dir = Path(Resources.TEST_RESOURCES_DIR, "pdf")
        outdir = Path(Resources.TEMP_DIR, "pdf", "ab_slides")
        outdir.mkdir(exist_ok=True)
        prestem = "breward"
        for chapno in range(1,9):
            stem = f"{prestem}_{chapno}"
            infile = Path( pdfs_dir, f"{stem}.pdf")
            if not infile.exists():
                print(f"file {infile} not available in {pdfs_dir}, text ignored")
                return
            htmlx, pdfToString = PDFSlide.create_html_chapter(chapno, infile)
            html_out = Path(outdir, f"{stem}.html")
            HtmlUtil.write_html_elem(htmlx, html_out)
            outfile = Path(outdir, f"{stem}.txt")
            with open(outfile, "w", encoding="UTF-8") as f:
                f.write(pdfToString)
                print(f"wrote text to {outfile}")

    def test_pdf_index(self):
        """
        Reads a medium PDF (Breward Chapter 1) and extracts words
        Still evolving
        """
        import pdfplumber
        infile = Path(Resources.TEST_RESOURCES_DIR, "pdf", "breward_1.pdf")
        assert infile.exists()
        with pdfplumber.open(infile) as pdf:
            page0 = pdf.pages[0]
            page0.extract_words(
                x_tolerance=3,
                x_tolerance_ratio=None,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=False,
                line_dir="ttb",
                char_dir="ltr",
                line_dir_rotated="ttb",
                char_dir_rotated="ltr",
                extra_attrs=[],
                split_at_punctuation=False,
                expand_ligatures=True,
                return_chars=False)



class PDFMainArgTest(test.test_all.AmiAnyTest):
    """
    contains Args and main test
    """

    def test_main_help(self):
        sys.argv = []
        sys.argv.append("--help")
        try:
            main()
        except SystemExit:
            pass

    def test_pdf_help(self):
        ''' runs PDF parser with --help to see if it produces terminal output
        '''
        pyami = AmiLib()
        pyami.run_command("PDF")
        pyami.run_command("PDF --help")

    def test_pdf_html_ipcc_command_help(self):
        pyami = AmiLib()
        pyami.run_command("HTML")
        pyami.run_command("PDF")
        # pyami.run_command("PDF")

    #    @unittest.skipUnless("old test", self.admin)
    def test_cannot_iterate(self):
        """
        Test that 'PDF' subcomand works without errors
        """

        AmiLib().run_command(
            ['HTML'])
        AmiLib().run_command(
            ['HTML', '--help'])

    def test_subcommands(self):
        # run args
        inpath = Path(Resources.TEST_PDFS_DIR, "1758-2946-3-44.pdf")
        outdir = Path(AmiAnyTest.TEMP_DIR, "pdf", "1758-2946-3-44")
        AmiLib().run_command(
            ['PDF', '--inpath', str(inpath), '--outdir', str(outdir), '--pages', '_2', '4', '6_8', '11_'])

    def test_subcommands_1(self):
        # run args
        inpath = Path(Resources.TEST_IPCC_DIR, "LongerReport", "fulltext.pdf")
        outdir = Path(AmiAnyTest.TEMP_DIR, "html", "LongerReport.html")
        AmiLib().run_command(
            ['PDF', '--inpath', str(inpath), '--outdir', str(outdir), '--maxpage', '999'])

    @unittest.skip("commands don't work properly")
    def test_subcommands_maxpage(self):
        """
        USER
         COMMAND
         PDF2HTML (but doesn't yet work)

         for Manny
        """
        # run args

        inpath = Path(Resources.TEST_IPCC_CHAP06, "fulltext.pdf")

        outdir = AmiAnyTest.TEMP_HTML_IPCC_CHAP06
        htmls = FileLib.delete_files(outdir, "*.html")
        out2 = Path(outdir, "fulltext.flow_2.html")
        assert not out2.exists()
        AmiLib().run_command(
            ['PDF', '--inpath', str(inpath), '--outdir', str(outdir),
             "--pdf2html", "pdfplumber", "--pages", "1_3", "--flow", "True"])
        files = FileLib.list_files(outdir, "*.html")
        assert len(files) == 3

    #        assert FileLib.size(out2) > 5000 # files may be empty

    @unittest.skip("obsolete")
    @unittest.skipUnless(PDFTest.SVG, "svg")
    @unittest.skipUnless(PDFTest.CMD, "command")
    def test_svg2page(self):
        proj = Resources.TEST_CLIMATE_10_PROJ_DIR
        args = f"--proj {proj} --apply svg2page"
        AmiLib().run_command(args)

    @unittest.skipIf(PDFTest.NYI, "page2sect")
    def test_page2chap(self):
        proj = Resources.TEST_CLIMATE_10_PROJ_DIR
        args = f"--proj {proj} --apply page2sect"
        AmiLib().run_command(args)


def main(argv=None):
    print(f"running PDFArgs main")
    pdf_args = PDFArgs()
    try:
        pdf_args.parse_and_process()
    except Exception as e:
        print(f"***Cannot run pyami***; see output for errors: {e}")


if __name__ == "__main__":
    main()
else:
    pass
