import csv
import unittest
from pathlib import Path

import lxml.etree as ET
from lxml.html import HTMLParser, Element, HtmlElement

from amilib.ami_html import HtmlLib
from amilib.amidriver import AmiDriver, URL, XPATH, OUTFILE  # EXPAND_SECTION_PARAS
from amilib.file_lib import FileLib
from amilib.headless_lib import HeadlessLib
from amilib.util import Util
from amilib.wikimedia import WikidataLookup, WikidataPage
from amilib.xml_lib import XmlLib, DECLUTTER_BASIC
from test.resources import Resources

from test.test_all import AmiAnyTest

# reset this yourself
# FileLib
OUT_DIR_TOP = Path(Resources.TEMP_DIR)
# input
IPCC_URL = "https://www.ipcc.ch/"
AR6_URL = IPCC_URL + "report/ar6/"
SYR_URL = AR6_URL + "syr/"
WG1_URL = AR6_URL + "wg1/"
WG2_URL = AR6_URL + "wg2/"
WG3_URL = AR6_URL + "wg3/"

SC_OUT_DIR = Path(OUT_DIR_TOP, "ar6")

SYR_OUT_DIR = Path(SC_OUT_DIR, "syr")
WG1_OUT_DIR = Path(SC_OUT_DIR, "wg1")

TOTAL_GLOSS_DIR = Path(Resources.TEST_RESOURCES_DIR, "ar6", "test", "total_glossary")

OMIT_LONG = True

SLEEP = 1

# xpath expressions for expand buttons in ?SYR web-html
EXPAND_SECTION_PARAS = [
    '//button[contains(@class, "chapter-expand") and contains(text(), "Expand section")]',
    '//p[contains(@class, "expand-paras") and contains(text(), "Read more...")]'
]



run_test = False
force = False
# force = True

logger = Util.get_logger(__name__)

class DriverTest(AmiAnyTest):
    """ Currently 8 minutes"""
    """
    Many of these tests run a headless Chrome browser and may flash up web pages while running
    """

    # helper

    # ===================tests=======================



    def test_total_glossary(self):
        """Ayush has written code to download the total glossary.
        This test assumes it is local as single files in a directory

        THIS DOES NOT DO DOWNLOAD
        """
        GLOSS_INPUT_DIR = Path(TOTAL_GLOSS_DIR, "input")
        assert GLOSS_INPUT_DIR.exists()
        dict_files = sorted(FileLib.posix_glob(f"{GLOSS_INPUT_DIR}/*.html"))
        logger.info(f"making glossary from {len(dict_files)} files in {GLOSS_INPUT_DIR}")
        out_dir = Path(TOTAL_GLOSS_DIR, "output")
        HeadlessLib.make_glossary(dict_files, out_dir, total_glossary=TOTAL_GLOSS_DIR, debug=True)

    def test_convert_characters_CHAR(self):
        """
            The original files are in an unknown encoding which we are gradually discovering by finding characters
            ?should be irrelevant if the encoding is known
            """

        text = """The point at which an actorâs objectives (or system needs) cannot be secured from intolerable risks through adaptive actions.
            â¢ Hard adaptation limit â No adaptive actions are possible to avoid intolerable risks.
            â¢ Soft adaptation limit â"""

        encodings_to_try = ["utf-8", "iso-8859-1", "windows-1252"]

        for encoding in encodings_to_try:
            try:
                decoded_text = text.encode(encoding).decode('utf-8')
                logger.info(f"Decoded with {encoding}: {decoded_text}")
            except UnicodeDecodeError as e1:
                logger.debug(f"Failed to decode with {encoding} gives {e1}")
            except UnicodeEncodeError as e2:
                logger.warning(f"failed encode with {encoding} gives {e2}")

    def test_glossary_encoding_CHAR(self):
        """
        Adaptation_limits_A.html
        """
        input = Path(TOTAL_GLOSS_DIR, "input", "Adaptation_limits_A.html")
        logger.info(f"adaptation {input}")
        with open(str(input), "r", encoding="UTF-8") as f:
            content = f.read()
            logger.debug(f"content {content}")

    def test_make_input_output_table(self):
        """
        hack to create output with input and output compares
        """
        # input of raw glossary files
        input_dir = Path(TOTAL_GLOSS_DIR, "input")
        # processed files in XML
        output_dir = Path(TOTAL_GLOSS_DIR, "output")
        input_files = FileLib.posix_glob(f"{input_dir}/*.html")

        html = HtmlLib.create_html_with_empty_head_body()
        # table of input and output text in glossary elements
        table = ET.SubElement(HtmlLib.get_body(html), "table")
        HeadlessLib.make_header(table)
        for input_file in sorted(input_files):
            input_file = Path(input_file)
            input_name = input_file.name
            # html in input glossary
            # make output filename from input name
            output_file = Path(output_dir, str(input_file.stem)[:-2] + ".html")  # strip letter
            if not output_file.exists():
                logger.warning(f"cannot read {output_file}")
                continue
            output_name = output_file.name
            tr = ET.SubElement(table, "tr")
            HeadlessLib.make_cell(output_file, output_name, tr, style="border: 1px blue; background: #eee; margin : 3px;")

        path = Path(TOTAL_GLOSS_DIR, "total.html")
        HtmlLib.write_html_file(html, path, encoding="UTF-8", debug=True)
        assert path.exists(), f"{path} should exist"

    def test_merge_IPCC_PDF_HTML_glosaries_MISC(self):
        glossaries = [
            "sr15",
            "srocc",
            "srccl",
            "wg1",
            "wg2",
            "wg3",
            "syr",
        ]
        for gloss in glossaries:
            glossary_dir = Path(TOTAL_GLOSS_DIR, "glossaries", gloss)
            glossary_file = Path(glossary_dir, "annotated_glossary.html")
            assert glossary_file.exists(), f"file should exist {glossary_file}"
            gloss_html = ET.parse(str(glossary_file))
            elements = gloss_html.xpath("//*")
            logger.debug(f"elements {len(elements)}")

    def test_wikimedia_WIKI(self):
        """

        """
        total_html = ET.parse(str(Path(TOTAL_GLOSS_DIR, "total.html")), HTMLParser())
        entries = total_html.xpath(".//div/h4")
        start = 190
        end = 200
        logger.info(f"downloading {start} - {end} from {len(entries)} entries")
        csvfile = Path(TOTAL_GLOSS_DIR, "wiki", f"{start}_{end}.csv")
        csvfile.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"writing to {csvfile}")
        with open(csvfile, "w", encoding="UTF-8") as f:
            wikiwriter = csv.writer(f, quoting=csv.QUOTE_ALL)
            wikiwriter.writerow(["term", "highestQid", "highest_desc", "list_of_others"])
            for i, entry in enumerate(entries):
                if i < start or i > end:
                    continue
                term = entry.text
                logger.info(f"entry: {i}; term {term}")
                wikidata_lookup = WikidataLookup()
                qitem0, desc, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
                logger.debug(f"qitem {qitem0, desc}")
                wikiwriter.writerow([term, qitem0, desc, wikidata_hits])


    def test_add_wikipedia_to_abbreviations_WIKI(self):
        """
        reads an abbreviations and looks up wikipedia
        """
        assert TOTAL_GLOSS_DIR.exists(), f"TOTAL_GLOSS_DIR exists {TOTAL_GLOSS_DIR}"
        glossdir = Path(TOTAL_GLOSS_DIR, "glossaries", "total")
        assert glossdir.exists(), f"glossdir must exist {glossdir}"
        # glossdir.mkdir(exist_ok=True, parents=True)
        abbrev_infile = Path(glossdir, "acronyms_wiki.csv")
        assert abbrev_infile.exists(), f"{abbrev_infile} must exist"
        output_file = Path(glossdir, "acronyms_wiki_pedia.csv")
 #       ./ test / resources / ar6 / test / total_glossary / glossaries / total / acronyms_wiki.csv
        maxout = 5  # 1700 in total
        lookup = WikidataLookup()
        with open(output_file, "w", encoding="UTF-8") as fout:
            csvwriter = csv.writer(fout)
            # csv header
            csvwriter.writerow(['abb', 'term', 'qid', 'desc', 'hits', 'wikipedia'])
            with open(abbrev_infile, newline='') as input:
                csvreader = csv.reader(input)
                for i, row in enumerate(csvreader):
                    if i > maxout:
                        break
                    abb = row[0]
                    term = row[1]
                    qid = row[2]
                    desc = row[3]
                    hits = row[4]
                    if qid is None or not qid.startswith("Q"):
                        logger.info(f"no QID")
                        continue
                    wikidata_page = WikidataPage(qid)
                    wikipedia_links = wikidata_page.get_wikipedia_page_links(["en"])
                    logger.info(f"wikipedia links {wikipedia_links}")
                    out_row = [abb, term, qid, desc, hits, wikipedia_links]
                    csvwriter.writerow(out_row)

                print(f"ENDED")

    def test_download_wg2_cross_chapters(self):
        """
        Some reports (such as wg2) contain cross chapters and this tests whether
        we can download them
        """
        """https://www.ipcc.ch/report/ar6/wg2/chapter/ccp1/"""

        CHAP_PREF = "cross_chapters"
        MAX_CCP = 2
        wg = 2
        logger.debug(f"wg = {wg}")
        wg_url = AR6_URL + f"wg{wg}/"
        logger.info(f"downloading from {wg_url}")
        # iterate over 7 cross-chapters (1-based)
        for ccp in range(1, MAX_CCP): # chapters 1-7
            ccp = str(ccp)
            # driver contains the headless browser
            driver = AmiDriver(sleep=SLEEP)
            ch_url = wg_url + f"chapter/ccp{ccp}/"
            logger.debug(f"downloading {ch_url}")

            outfile = Path(SC_OUT_DIR, f"wg{wg}", f"{CHAP_PREF}", f"ccp{ccp}", "raw.html")
            # outfile_clean = Path(SC_TEST_DIR, f"wg{wg}", f"{CHAP_PREF}{ccp}", "clean.html")
            outfile_figs = Path(SC_OUT_DIR, f"wg{wg}", f"{CHAP_PREF}{ccp}", "figs.html")
            wg_dict = {
                f"wg{wg}_ch":
                    {
                        URL: ch_url,
                        XPATH: None,  # no expansiom
                        OUTFILE: outfile
                    },
            }
            AmiDriver().run_from_dict(outfile, wg_dict, keys=wg_dict.keys())
            htmlx = HtmlLib.create_html_with_empty_head_body()
            # create a new div to receive the driver output
            div = ET.SubElement(HtmlLib.get_body(htmlx), "div")
            outxml = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", str(wg), "CrossChapters", ccp, "raw.xml")
            # remove some clutter
            if driver.lxml_root_elem is not None:
                XmlLib.write_xml(driver.lxml_root_elem, outxml)
                assert outxml.exists()

            driver.quit()


