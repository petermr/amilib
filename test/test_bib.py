import ast
import collections
import configparser
import logging
import lxml.etree as ET
from pathlib import Path
import pandas as pd

from amilib.ami_bib import (SAVED, SAVED_CONFIG_INI, SECTION_KEYS, API, LIMIT, QUERY, STARTDATE, XML, \
                            EUPMC_RESULTS_JSON, PMCID, ABS_TEXT, EPMC_KEYS, JOURNAL_INFO, DOI, TITLE, AUTHOR_STRING,
                            PUB_YEAR, JOURNAL_INFO_TITLE, Pygetpapers)
from amilib.ami_html import HtmlUtil, HtmlLib, Datatables
from amilib.ami_util import AmiJson, AmiUtil
from amilib.ami_corpus import AmiCorpus, AmiCorpusContainer
from amilib.amix import AmiLib
from amilib.file_lib import FileLib
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)

class AmiBibliographyTest(AmiAnyTest):
    """

    """
    @classmethod
    def convert_csv_to_bib(cls):
        """

        """

def df_toupper(s):
    return f"<a href='{s}`>s</a>"

def df_truncate(s):
    return f"{s[:200]}..."

class DictParser(ast.NodeVisitor):
    def visit_Dict(self,node):
        keys,values = node.keys,node.values
        keys = [n.s for n in node.keys]
        values = [n.s for n in node.values]
        self.od = collections.OrderedDict(zip(keys, values))

def df_unpack_dict(json_string):
    """
    this is messy. I think we need a recursive descent parser
    """
    print(f"DIKT {json_string}")
    try:
        # dikt = json.loads(s)
    # or
        # decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
        # dikt = decoder.decode(json_string)
    # or
        dp = DictParser()
        dp.visit(ast.parse(json_string))
        dikt = dp.od
    except Exception as e:
        print(f"EXC {e}")
        return "None"
    print(f"dikt {type(dikt)} {dikt.keys()}")
    title = dikt.get("journal").get("title")
    return title

HTML_WITH_IDS = "html_with_ids"

class PygetpapersTest(AmiAnyTest):
    """
    manage output from pygetpapers
    """

    def test_edit_csv(self):
        """
        reade *.csv created by pygetpapers
        not working because of lack of OrderedDict parser
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "csv", "frictionless", "europe_pmc.csv")
        outdir = Path(Resources.TEMP_DIR, "csv", "frictionless")
        outdir.mkdir(parents=True, exist_ok=True)
        outfile = Path(outdir, "europe_pmc.csv")
        outfile_h = Path(outdir, "europe_pmc.html")
        assert infile.exists()
        df = pd.read_csv(infile)

        keys = df.keys()
        key_list = keys.to_list()
        assert EPMC_KEYS == keys.to_list()
        df[PMCID] = df[PMCID].apply(df_toupper)
        df[ABS_TEXT] = df[ABS_TEXT].apply(df_truncate)
        df[JOURNAL_INFO] = df[JOURNAL_INFO].apply(df_unpack_dict)
        df2 = df[[PMCID, DOI, TITLE, AUTHOR_STRING, JOURNAL_INFO, PUB_YEAR, ABS_TEXT]]

        with open(outfile, "w") as f:
            f.write(df2.to_csv())
        with open(outfile_h, "w") as f:
            f.write(df2.to_html(escape="False"))

    def test_make_html_table_from_json(self):
        """
        assume JSON is an implicit table
        """
        effective_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)

        project_name = "district_heating"
        indir = Path(Resources.TEST_RESOURCES_DIR, "json", project_name)
        outdir = Path(Resources.TEMP_DIR, "json", project_name)
        outfile_h = Path(outdir, "europe_pmc.html")

        AmiCorpus.make_datatables(indir, outdir, outfile_h)
        logger.setLevel(effective_level)

    def test_make_datatables_cli(self):
        """

        """
        indir = Path(Resources.TEST_RESOURCES_DIR, "json", "district_heating")
        args = ["HTML", "--indir", str(indir), "--operation", "DATATABLES"]
        amilib = AmiLib()
        amilib.run_command(args)

    def test_read_pygetpapers_config(self):
        """
        reads pygetpapers saved_config.ini and extracts meta/data
        """
        inpath = Path(Resources.TEST_RESOURCES_DIR, "pygetpapers", SAVED_CONFIG_INI)
        assert inpath.exists()
        saved_section, section_names = Pygetpapers.get_saved_section(inpath)

        assert type(section_names) is list
        assert section_names == [SAVED]
        assert type(saved_section) is configparser.SectionProxy

        assert SECTION_KEYS == saved_section.keys()
        assert saved_section.get(API) == "europe_pmc"
        assert saved_section.get(LIMIT) == '20'
        assert saved_section.get(QUERY) == "'district heating'"
        assert saved_section.get(STARTDATE) == "False"
        assert saved_section.get(XML) == "True"

    def test_search_all_chapters_with_query_words(self, outfile=None):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        query = "south_asia"
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(indir, f"{query}.html")
        debug = False
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        assert 2 == len(infiles)
        phrases = [
            "bananas",
            "South Asia",
        ]
        html1 = AmiCorpus.create_hit_html(infiles, phrases=phrases, outfile=outfile, debug=debug)
        assert html1 is not None
        assert len(html1.xpath("//p")) > 0

    def test_search_all_chapters_with_query_words_commandline(self, outfile=None):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        query = "south_asia"
        path = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(path, f"{query}.html")
        debug = False
        infiles = FileLib.posix_glob(f"{str(path)}/**/{HTML_WITH_IDS}.html", recursive=True)
        phrases = [
            "bananas",
            "South Asia"
        ]
        html1 = AmiCorpus.create_hit_html(infiles, phrases=phrases, outfile=outfile, debug=debug)



class AmiCorpusTest(AmiAnyTest):

    def test_simple_corpus(self):
        """
        creates a simple tree of containers and documents with token content
        """
        corpus_dir = Path(Resources.TEMP_DIR, "corpus")

        corpus = AmiCorpus(corpus_dir, mkdir=True)

        report1 = corpus.create_corpus_container(
            Path(corpus_dir, "report1"), type="report", mkdir=True)

        chapter11 = report1.create_corpus_container("chapter11", type="chapter", mkdir=True)
        html11 = chapter11.create_document("text.html", text="chapter11")

        chapter12 = report1.create_corpus_container("chapter12", type="chapter", mkdir=True)
        html12 = chapter12.create_document("text.html", text="chapter12")

        report2 = corpus.create_corpus_container(Path(corpus_dir, "report2"), mkdir=True)
        chapter21 = report2.create_corpus_container("chapter21", type="chapter", mkdir=True)
        html21 = chapter21.create_document("text.html", text="chapter21")
        chapter22 = report2.create_corpus_container("chapter22", type="chapter", mkdir=True)
        html22 = chapter22.create_document("text.html", text="chapter22")
        assert Path(html22) == Path(
            Resources.TEMP_DIR, "corpus", "report2", "chapter22", "text.html")
        assert html22.exists()


    def test_list_files_from_ipcc(self):
        """
        reads all IPCC htmls and creates a corpus/datatables
        """
        """https://github.com/semanticClimate/ipcc/tree/main/cleaned_content"""
        # Github repository is https://github.com/semanticClimate/ipcc
        # clone tnis
        # *****top director on PMR's machine = needs altering for youu implementation*****
        ipcc_top = Path(Resources.TEST_RESOURCES_DIR, "..", "..", "..", "..", "projects", "ipcc")

        assert ipcc_top.exists(), f"{ipcc_top} should exist, you need to change this for your machine"
        cleaned_content_dir =  Path(ipcc_top, "cleaned_content").resolve() # cleans the filename (removes "..")
        logger.info(f"ipcc_dir {cleaned_content_dir}")
        assert cleaned_content_dir.exists(), f"{cleaned_content_dir} should exist"

        report_glob_str = f"{str(cleaned_content_dir)}/*"
        logger.info(f"glob {report_glob_str}")
        report_dirs = FileLib.posix_glob(report_glob_str, recursive=False)
        assert len(report_dirs) == 7, f"child files are {report_dirs}"
        total_chapter_count = 0
        all_cleaned_files = []
        all_html_id_files = []
        for report_dir in sorted(report_dirs):
            report = Path(report_dir).stem
            chapter_str = f"{str(report_dir)}/Chapter*"
            chapter_dirs = FileLib.posix_glob(chapter_str, recursive=False)
            total_chapter_count += len(chapter_dirs)
            logger.info(f"chapter {report}: {total_chapter_count}")
            for chapter_dir in sorted(chapter_dirs):
                html_str = f"{str(chapter_dir)}/*.html"
                html_files =  FileLib.posix_glob(html_str, recursive=False)
                for html_file in html_files:
                    stem = Path(html_file).stem
                    if stem == "de_wordpress" or stem == "de_gatsby":
                        logger.info(f">> {stem}")
                        all_cleaned_files.append(html_file)
                    elif stem == "html_with_ids":
                        all_html_id_files.append(html_file)
                    else:
                        logger.info(f"skipped {html_file}")

            logger.info(f"cleaned files {len(all_cleaned_files)} html_with_ids {len(all_html_id_files)}")

    def test_create_corpus_from_ipcc(self):
        """
        reads all IPCC htmls and creates a corpus/datatables
        """
        """https://github.com/semanticClimate/ipcc/tree/main/cleaned_content"""
        # Github repository is https://github.com/semanticClimate/ipcc
        # clone tnis
        # *****top director on PMR's machine = needs altering for youu implementation*****

        CLEAN_WORDPRESS_STEM = "de_wordpress"
        CLEAN_GATSBY_STEM = "de_gatsby"
        REPORT = "report"
        REMOTE_CHAPTER = "remote_chapter"
        REMOTE_PDF= "remote_PDF"
        CHAPTER_ANY = "Chapter*"
        ANY_HTML = "*.html"
        CLEANED_CHAPTER = "cleaned_chapter"
        CHAP_WITH_IDS = "chapter_with_ids"
        HTML_WITH_IDS = "html_with_ids"
        IPCC_CH = "https://www.ipcc.ch"
        ROMAN_DICT = {"1": "I", "2": "II", "3": "III", }

        cls = AmiCorpusTest

        ipcc_top = Path(Resources.TEST_RESOURCES_DIR, "..", "..", "..", "..", "projects", "ipcc")

        assert ipcc_top.exists(), f"{ipcc_top} should exist, you need to change this for your machine"
        corpus_dir =  Path(ipcc_top, "cleaned_content").resolve() # cleans the filename (removes "..")

        corpus_files = FileLib.get_children(corpus_dir, dirx=True)
        labels = [REPORT, REMOTE_CHAPTER, REMOTE_PDF, CLEANED_CHAPTER, CHAP_WITH_IDS]

        datatables = True
        table_id = "table1"
        htmlx, tbody = self.create_table(cls, labels, table_id)

        for corpus_file in sorted(corpus_files):
            corpus_text = AmiCorpusContainer(corpus_file)
            report = Path(work).stem
            arx = "report/ar6/" if report.startswith("wg") else ""
            work = f"{IPCC_CH}/{arx}{report}"
            roman = None
            if report.startswith("wg"):
                wg_no = report[2:]
                roman = ROMAN_DICT.get(wg_no)

            chapter_glob = f"{str(work)}/{CHAPTER_ANY}"
            chapter_dirs = FileLib.posix_glob(chapter_glob, recursive=False)
            for chapter_dir in sorted(chapter_dirs):
                cls.output_chapter_row(work, chapter_dir, tbody)

        if datatables:
            Datatables.add_head_info(HtmlLib.get_head(htmlx), htmlx)
            Datatables.add_body_scripts(HtmlLib.get_body(htmlx), table_id=table_id)


        HtmlLib.write_html_file(htmlx, Path(ipcc_top, "cleaned_content", "datatables.html").resolve(), debug=True)

    def create_table(self, cls, labels, table_id):
        htmlx = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(htmlx)
        table = ET.SubElement(body, "table")
        table.attrib["id"] = table_id
        cls.create_thead_and_labels(cls, labels, table)
        tbody = ET.SubElement(table, "tbody")
        return htmlx, tbody

    def output_chapter_row(cls, IPCC_CH, arx, chapter_dir, report, roman, tbody):
        stem = Path(chapter_dir).stem
        chap_no = stem[-2:]
        if chap_no.startswith("0"):
            chap_no = chap_no[1:]
        # html_glob = f"{chapter_dir}/{ANY_HTML}"
        # html_files = FileLib.posix_glob(html_glob, recursive=False)
        tr = ET.SubElement(tbody, "tr")
        cls.add_cell_content(tr, text=report, href=f"{IPCC_CH}/{report}/")
        cls.add_cell_content(tr, text=chapter_dir.stem, href=f"{report}/chapter/chapter-{chap_no}")
        pdf_name = f"{chapter_dir.stem}.PDF"
        if roman:
            cls.add_cell_content(tr, text=pdf_name,
                                 href=f"{report}/downloads/report/IPCC_AR6_WG{roman}_{stem}.pdf")
        else:
            cls.add_cell_content(tr, text=pdf_name)
        gatsby_glob = f"{str(chapter_dir)}/de_gatsby.html"
        wordpress_glob = f"{str(chapter_dir)}/de_wordpress.html"
        cleaned_files = FileLib.posix_glob(gatsby_glob, recursive=False) + \
                        FileLib.posix_glob(wordpress_glob, recursive=False)
        cls.add_content_for_files(cleaned_files, tr)
        html_id_glob = f"{str(chapter_dir)}/html_with_ids.html"
        html_id_files = FileLib.posix_glob(html_id_glob, recursive=False)
        cls.add_content_for_files(html_id_files, tr)

    def create_thead_and_labels(self, cls, labels, table):
        thead = ET.SubElement(table, "thead")
        tr = ET.SubElement(thead, "tr")
        for label in labels:
            cls.add_cell_content(tr, cell_type="th", text=label)

    @classmethod
    def add_content_for_files(cls, files, tr):
        if files:
            cls.add_cell_content(tr, text=Path(files[0]).stem, href=f"file://{files[0]}")
        else:
            cls.add_cell_content(tr, text="?")

    @classmethod
    def add_cell_content(cls, tr, cell_type="td", text=None, title=None, href=None):
        """
        creates cell content
        :param tr: parent row elemnt
        :param cell_type: "td" or "th" (td by default)
        :param text: text content or <a>content.
        :param title: cell title (will be tooltip)
        :param href: target for hyperlink. content is text or 'LINK'
        :return: the cell
        """

        tcell = ET.SubElement(tr, cell_type)
        if href is not None:
            if text is None:
                text = "LINK"
            a = ET.SubElement(tcell, "a")
            a.attrib["href"] = href
            a.text = text
        elif text is not None:
            tcell.text = text
        if title is not None:
            tcell.title = title

        return tcell

