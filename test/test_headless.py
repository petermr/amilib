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

SC_TEST_DIR = Path(OUT_DIR_TOP, "ar6", "test")

SYR_OUT_DIR = Path(SC_TEST_DIR, "syr")
WG1_OUT_DIR = Path(SC_TEST_DIR, "wg1")
# WG2_OUT_DIR = Path(SC_TEST_DIR, "wg2")
# WG3_OUT_DIR = Path(SC_TEST_DIR, "wg3")

TOTAL_GLOSS_DIR = Path(SC_TEST_DIR, "total_glossary")

OMIT_LONG = True

SLEEP = 1

EXPAND_SECTION_PARAS = [
    '//button[contains(@class, "chapter-expand") and contains(text(), "Expand section")]',
    '//p[contains(@class, "expand-paras") and contains(text(), "Read more...")]'
]



run_test = False
force = False

logger = Util.get_logger(__name__)

# force = True # uncomment to run tests with this keyword
@unittest.skipUnless(AmiAnyTest.IS_PMR, "headless browsing still giving intermittent problems that PMR has to solve")
class DriverTest(AmiAnyTest):
    """ Currently 8 minutes"""
    """
    Many of these tests run a headless Chrome browser and may flash up web pages while running
    """

    # helper

    # ===================tests=======================

    @unittest.skipUnless(AmiAnyTest.run_long() or force, "run occasionally")
    def test_download_ipcc_syr_longer_report(self):
        driver = AmiDriver(sleep=SLEEP)
        url = SYR_URL + "longer-report/"
        level = 99
        click_list = EXPAND_SECTION_PARAS

        html_out = Path(SC_TEST_DIR, f"complete_text_{level}.html")
        driver.download_expand_save(url, click_list, html_out, level=level)
        logger.debug(f"elem {driver.get_lxml_element_count()}")
        XmlLib.remove_common_clutter(driver.lxml_root_elem)

        logger.debug(f"elem {driver.get_lxml_element_count()}")
        driver.write_html(Path(html_out))
        driver.quit()

    @unittest.skipUnless(AmiAnyTest.run_long() or force, "run occasionally")
    def test_download_syr_annexes_and_index(self):
        """
        A potential multiclick download
        """
        """
        fails with:
         OSError: [Errno 8] Exec format error:
         """
        url = SYR_URL + "annexes-and-index/"
        driver = AmiDriver(sleep=SLEEP)
        click_list = EXPAND_SECTION_PARAS

        html_out = Path(SYR_OUT_DIR, "annexes-and-index", "gatsby.html")
        driver.download_expand_save(url, click_list, html_out)
        XmlLib.remove_common_clutter(driver.lxml_root_elem)
        driver.write_html(html_out, debug=True)
        driver.quit()

    @unittest.skipUnless(AmiAnyTest.run_long() or force, "run occasionally")
    def test_download_ancillary_html(self):
        """tries to find SPM, TS, glossary, etc
        TODO reduce to single """
        for doc in [
            (AR6_URL, "wg1"),
            (AR6_URL, "wg2"),
            (AR6_URL, "wg3"),  # https://www.ipcc.ch/report/ar6/wg3
            (AR6_URL, "wg3", "spm",
             "https://www.ipcc.ch/report/ar6/wg3/chapter/summary-for-policymakers/"),
            (AR6_URL, "wg3", "ts",
             "https://www.ipcc.ch/report/ar6/wg3/chapter/technical-summary/"),
            (AR6_URL, "syr"),  # https://www.ipcc.ch/report/ar6/syr/annexes-and-index/
            (IPCC_URL, "srocc", "chapter"),  # https://www.ipcc.ch/srocc/chapter/glossary/ - has sections
            (IPCC_URL, "sr15", "chapter"),  # https://www.ipcc.ch/sr15/chapter/glossary/ - has sections
            (IPCC_URL, "srccl", "chapter"),  # https://www.ipcc.ch/srccl/chapter/glossary/ - NO HTML found
        ]:
            driver = AmiDriver(sleep=SLEEP)
            outfile = Path(SC_TEST_DIR, doc[1], "glossary.html")
            url = doc[0] + doc[1] + "/"
            if len(doc) == 3:
                url = url + doc[2] + "/"
            url = url + "glossary" + "/"
            logger.debug(f"url: {url}")
            GLOSSARY_TOP = "glossary"
            rep_dict = {
                GLOSSARY_TOP:
                    {
                        URL: url,
                        XPATH: None,
                        OUTFILE: outfile
                    }
            }
            keys = [GLOSSARY_TOP]
            AmiDriver().run_from_dict(outfile, rep_dict, keys=keys)
            driver.quit()

    @unittest.skipUnless(AmiAnyTest.run_long() or force, "run occasionally")
    def test_download_with_dict(self):
        """download single integrated glossary
        """
        # "https://apps.ipcc.ch/glossary/"

        """useful if we can't download the integrated glossary"""
        driver = AmiDriver(sleep=SLEEP)
        gloss_dict = {
            "syr":
                {
                    URL: "https://apps.ipcc.ch/glossary/",
                    XPATH: None,  # this skips any button pushes
                    OUTFILE: Path(SC_TEST_DIR, "total_glossary.html")
                },
            "wg1_ch1":
                {
                    URL: WG1_URL + "chapter/chapter-1/",
                    XPATH: None,
                    OUTFILE: Path(WG1_OUT_DIR, "chapter_1.html")
                },
            "wg1_ch2":
                {
                    URL: WG1_URL + "chapter/chapter-2/",
                    XPATH: "//button[contains(@class, 'chapter-expand') and contains(text(), 'Expand section')]",
                    OUTFILE: Path(WG1_OUT_DIR, "chapter_2.html")
                },
            "wg1_spm":
                {
                    URL: WG1_URL + "chapter/summary-for-policymakers/",
                    XPATH: ["//button[contains(text(), 'Expand all sections')]",
                            "//span[contains(text(), 'Expand')]"],
                    OUTFILE: Path(WG1_OUT_DIR, "wg1", "spm.html")
                }
        }

        # driver.execute_instruction_dict(gloss_dict, keys=["wg1_ch1"])
        # driver.execute_instruction_dict(gloss_dict, keys=["wg1_ch2"])
        driver.execute_instruction_dict(gloss_dict, keys=["wg1_spm"])
        driver.quit()

    @unittest.skipUnless(run_test and (AmiAnyTest.run_long() or force), "run occasionally")
    def test_download_all_toplevel(self):
        """
        download toplevel material from WG1
        likely to expand as we find more resources in it.
        """

        MAX_REPORTS = 1
        for report_base in [
                               (AR6_URL, "wg1"),
                               (AR6_URL, "wg2"),
                               (AR6_URL, "wg3"),
                               (AR6_URL, "syr"),
                               (IPCC_URL, "srocc"),
                               (IPCC_URL, "sr15"),
                               (IPCC_URL, "srccl"),
                           ][:MAX_REPORTS]:
            driver = AmiDriver(sleep=SLEEP)
            outfile = Path(SC_TEST_DIR, report_base[1], "toplevel.html")
            url = report_base[0] + report_base[1] + "/"
            REPORT_TOP = "report_top"
            rep_dict = {
                REPORT_TOP:
                    {
                        URL: url,
                        XPATH: None,
                        OUTFILE: outfile
                    }
            }
            keys = [REPORT_TOP]
            AmiDriver().run_from_dict(outfile, rep_dict, keys=keys)
            driver.quit()

    @unittest.skipUnless(AmiAnyTest.run_long() or force, "run occasionally")
    def test_download_wg1_chapter_1(self):
        """
        download Chapter_1 from WG1
        """

        driver = AmiDriver(sleep=SLEEP)
        ch1_url = WG1_URL + "chapter/chapter-1/"

        outfile = Path(WG1_OUT_DIR, "chapter_1_noexp.html")
        wg1_dict = {
            "wg1_ch1":
                {
                    URL: ch1_url,
                    XPATH: None,  # no expansiom
                    OUTFILE: outfile
                },
        }
        keys = ["wg1_ch1"]
        AmiDriver().run_from_dict(outfile, wg1_dict, keys=keys)

        driver.quit()

    @unittest.skipUnless(run_test and (AmiAnyTest.run_long() or force), "run occasionally")
    def test_download_wg_chapters(self):
        """
        download all chapters from WG1/2/3
        saves output in petermr/semanticClimate and creates noexp.html as main output
        """
        CHAP_PREF = "Chapter"
        for wg in range(3, 4):
            logger.debug(f"wg = {wg}")
            wg_url = AR6_URL + f"wg{wg}/"
            logger.info(f"downloading from {wg_url}")
            for ch in range(1, 18):
                chs = str(ch)
                if len(chs) == 1:
                    chs = "0" + chs
                driver = AmiDriver(sleep=SLEEP)
                ch_url = wg_url + f"chapter/chapter-{ch}/"

                outfile = Path(SC_TEST_DIR, f"wg{wg}", f"{CHAP_PREF}{chs}", "noexp.html")
                outfile_clean = Path(SC_TEST_DIR, f"wg{wg}", f"{CHAP_PREF}{chs}", "clean.html")
                outfile_figs = Path(SC_TEST_DIR, f"wg{wg}", f"{CHAP_PREF}{chs}", "figs.html")
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
                # remove some clutter
                if driver.lxml_root_elem is not None:
                    XmlLib.remove_elements(driver.lxml_root_elem, xpath="//div[contains(@class, 'col-12')]",
                                           new_parent=div, debug=True)
                    # write the in-driver tree
                    XmlLib.write_xml(driver.lxml_rootx_elem, outfile_clean)

                    XmlLib.write_xml(htmlx, outfile_figs)

                driver.quit()
                # print(f"break for test, remove later")
                # break

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
                logger.debug(f"Failed to decode with {encoding} goves {e1}")
            except UnicodeEncodeError as e2:
                logger.warning(f"failed encode with {encoding} gives {e2}")

    def test_glossary_encoding_CHAR(self):
        """
        Adaptation_limits_A.html
        """
        input = Path(TOTAL_GLOSS_DIR, "input", "Adaptation_limits_A.html")
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
        with open(csvfile, "w") as f:
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

    @unittest.skip("no idea what this does - I only wrote it!")
    def test_abbreviations_wikimedia_WIKI(self):
        """
        reads an acronym file as CSV and looks up entries in Wikidata and Wikipedia
        TODO move elsewhere
        """
        abbrev_file = Path(TOTAL_GLOSS_DIR, "glossaries", "total", "acronyms.csv")
        logger.info(f"looking up acronym file {abbrev_file} in Wikidata")
        offset = 1000
        count = 0
        MAXCOUNT = 3
        for start in range(0, 3):
            end = start + 1
            lookup = WikidataLookup()
            output_file = Path(TOTAL_GLOSS_DIR, "glossaries", "total", f"acronyms_wiki_{start}_{end}.csv")
            with open(output_file, "w") as fout:
                csvwriter = csv.writer(fout)
                csvwriter.writerow(['abb', 'term', 'qid', 'desc', 'hits'])
                with open(abbrev_file, newline='') as input:
                    csvreader = csv.reader(input)
                    for i, row in enumerate(csvreader):
                        abb = row[0]
                        term = row[1]
                        qitem0, desc, hits = lookup.lookup_wikidata(term)
                        if qitem0 is None:
                            logger.warning(f"failed on text: {row}")
                            # qitem0, desc, hits = lookup.lookup_wikidata(abb)
                            if qitem0 is None:
                                logger.warning(f"failed on text {term} and abbreviation: {abb}")
                                out_row = [abb, term, "?", "?", "?"]
                            else:
                                out_row = [abb, term, qitem0, desc, hits]
                        else:
                            out_row = [abb, term, qitem0, desc, hits]
                        csvwriter.writerow(out_row)

    def test_add_wikipedia_to_abbreviations_WIKI(self):
        """
        reads an abbreviations and looks up wikipedia
        """
        glossdir = Path(TOTAL_GLOSS_DIR, "glossaries", "total")
        glossdir.mkdir(exist_ok=True, parents=True)
        abbrev_file = Path(glossdir, "acronyms_wiki.csv")
        output_file = Path(glossdir, "acronyms_wiki_pedia.csv")
        maxout = 5  # 1700 in total
        lookup = WikidataLookup()
        with open(output_file, "w") as fout:
            csvwriter = csv.writer(fout)
            # csv header
            csvwriter.writerow(['abb', 'term', 'qid', 'desc', 'hits', 'wikipedia'])
            with open(abbrev_file, newline='') as input:
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


# def test_plot_mentions(self):
#
#     from pyvis.network import Network
#     import networkx as nx
#     nx_graph = nx.cycle_graph(10)
#     nx_graph.nodes[1]['title'] = 'Number 1'
#     nx_graph.nodes[1]['group'] = 1
#     nx_graph.nodes[3]['title'] = 'I belong to a different group!'
#     nx_graph.nodes[3]['group'] = 10
#     nx_graph.add_node(20, size=20, title='couple', group=2)
#     nx_graph.add_node(21, size=15, title='couple', group=2)
#     nx_graph.add_edge(20, 21, weight=5)
#     nx_graph.add_node(25, size=25, label='lonely', title='lonely node', group=3)
#     nt = Network('500px', '500px')
#     # populates the nodes and edges data structures
#     nt.from_nx(nx_graph)
#     nt.show('nx.html')


# cleaned_ipcc_graph = pd.read_csv(str(Path(TOTAL_GLOSS_DIR, "mentions.csv")))
#
# # cleaned_ipcc_graph = cleaning_nan(mention_df, ['source', 'package','target', 'section'])
# ipcc_graph_with_coloured_nodes = get_package_names(cleaned_ipcc_graph, "package.json")
# ipcc_graph_with_coloured_nodes.to_csv('coloured.csv')
# make_graph(ipcc_graph_with_coloured_nodes, source='source', target='target', colour ='node_colour')

class Utils1Test:

    @unittest.skip("not written")
    def test_strip_guillemets(self):
        text = "Adjustments (in relation to effective radiative forcing) « WGI »"
        HeadlessLib.extract_chunks()
