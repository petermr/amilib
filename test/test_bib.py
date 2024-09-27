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


