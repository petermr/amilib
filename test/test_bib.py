import ast
import collections
import configparser
import json
import logging
from pathlib import Path
import pandas as pd

from amilib.ami_bib import (SAVED, SAVED_CONFIG_INI, SECTION_KEYS, API, LIMIT, QUERY, STARTDATE, XML, \
                            EUPMC_RESULTS_JSON, PMCID, ABS_TEXT, EPMC_KEYS, JOURNAL_INFO, DOI, TITLE, AUTHOR_STRING,
                            PUB_YEAR, JOURNAL_INFO_TITLE, Pygetpapers)
from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.ami_util import AmiJson, AmiUtil
from amilib.ami_corpus import AmiCorpus
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

    def test_create_corpus_from_ipcc(self):
        """
        reads all IPCC htmls and creates a corpus/datatables
        """
        """https://github.com/semanticClimate/ipcc/tree/main/cleaned_content"""
        ipcc_dir =  Path(Path(Path(Resources.TEST_RESOURCES_DIR).parent.parent.parent.parent), "projects", "ipcc", "cleaned_content")
        ipcc_dir =  Path(Resources.TEST_RESOURCES_DIR, "..", "..", "..", "..", "projects", "ipcc", "cleaned_content").resolve()
        logger.info(f"ipcc_dir {ipcc_dir}")
        assert ipcc_dir.exists(), f"{ipcc_dir} should exist"
        glob_str = f"{str(ipcc_dir)}/*"
        logger.info(f"glob {glob_str}")
        child_dirs = FileLib.posix_glob(glob_str, recursive=False)
        assert len(child_dirs) == 7, f"child files are {child_dirs}"
        chapter_count = 0
        all_files = []
        for child_dir in child_dirs:
            chapter = Path(child_dir).stem
            chapter_str = f"{str(child_dir)}/Chapter*"
            chapter_dirs = FileLib.posix_glob(chapter_str, recursive=False)
            chapter_count += len(chapter_dirs)
            logger.info(f"chapter {chapter}: {chapter_count}")
            for chapter_dir in chapter_dirs:
                file_str = f"{str(chapter_dir)}/de_*.html"
                files =  FileLib.posix_glob(file_str, recursive=False)
                for file in files:
                    stem = Path(file).stem
                    if stem == "de_wordpress" or stem == "de_gatsby":
                        logger.info(f">> {Path(file).stem}")
                        all_files.append(file)
            logger.info(f"files {len(all_files)}")


