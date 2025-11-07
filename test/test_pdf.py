import codecs
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
from amilib.ami_pdf_libs import (AmiPage, X, Y, SORT_XY, PDFImage, AmiPDFPlumber,
                                 AmiPlumberJsonPage, AmiPlumberJson, PDFHyperlinkAdder)
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


    def test_unusual_chars(self):
        """badly decoded characters default to #65533"""
        x = """Systems������������ 867"""
        for c in x:
            logger.debug(f"c {c} {ord(c)}")


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


    def test_make_composite_lines_from_pdf_chap_6_3_toc(self):
        path = Path(Resources.TEST_IPCC_CHAP06, "html", "chap6_3.html")
        assert path.exists(), f"path exists {path}"
        AmiPage.create_page_from_pdf_html(path)


class PDFChapterTest(test.test_all.AmiAnyTest):
    """
    processes part or whole of a chapter
    """


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


    run_me = False


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


# test PDFHyperlinkAdder 
class TestPDFHyperlinkAdder(AmiAnyTest):
    def test_pdf_hyperlink_adder(self):
        inpath = Path(Resources.TEST_PDFS_DIR, "1758-2946-3-44.pdf")
        outpath = Path(AmiAnyTest.TEMP_DIR, "pdf", "1758-2946-3-44.pdf")
        words_file = Path(Resources.TEST_PDFS_DIR, "1758-2946-3-44.words.csv")
        pdf_adder = PDFHyperlinkAdder(input_pdf=str(inpath), word_list_file=str(words_file), output_pdf=str(outpath))
        pdf_adder.process_pdf()

    
    
       
    

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
