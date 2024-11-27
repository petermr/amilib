import ast
import collections
import configparser
import logging
import re
import unittest
from copy import copy

import lxml.etree as ET
from pathlib import Path
import pandas as pd
from lxml.etree import _Element
from lxml.html import HtmlElement

from amilib.ami_bib import (SAVED, SAVED_CONFIG_INI, SECTION_KEYS, API, LIMIT, QUERY, STARTDATE, XML, \
                            EUPMC_RESULTS_JSON, PMCID, ABS_TEXT, EPMC_KEYS, JOURNAL_INFO, DOI, TITLE, AUTHOR_STRING,
                            PUB_YEAR, JOURNAL_INFO_TITLE, Pygetpapers)
from amilib.ami_html import HtmlUtil, HtmlLib, Datatables, SCROLL_PARENT
from amilib.ami_util import AmiJson, AmiUtil
from amilib.ami_corpus import AmiCorpus, AmiCorpusContainer
from amilib.amix import AmiLib
from amilib.file_lib import FileLib
from amilib.util import Util, TextUtil
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

    def test_make_datatables_from_pygetpapers_cli(self):
        """
        Reads json output of pygetpapers and creates datatables
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

    def test_search_all_chapters_with_query_words(self):
        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        debug = True
        query = "bananas"
        xpath = None
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(indir, f"{query}.html")
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        assert 50 == len(infiles)
        phrases = [
            "bananas",
            "South Asia",
        ]
        html1 = AmiCorpus.search_files_with_phrases_write_results(infiles, phrases=phrases, xpath=xpath, outfile=outfile, debug=debug)
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
        html1 = AmiCorpus.search_files_with_phrases_write_results(infiles, phrases=phrases, outfile=outfile, debug=debug)


# def _ipcc_create_zip_caption_img(chapter_html):
#     """
#     function to read html file, extracts figures with caption
#     :param chapter_html: HTML file containing images aith captions
#     :return: zip of (img, caption_text)
#     :except: any error returns None
#
#     <div id="chapter-figures">
#       <div class="col-lg-3 col-12">
#
#         <h3>Figure 1.1</h3>
#         <img
#           src="https://www.ipcc.ch/report/ar6/wg1/downloads/figures/IPCC_AR6_WGI_Figure_1_1.png"
#           alt="Figure 1.1 | Figure 1.1 | The structure of the AR6 WGI Report"
#           class="img-card">
#       </div>
#       """
#
#     try:
#         figure_containers = chapter_html.xpath("//div[@id='chapter-figures']")
#         figures = figure_containers[0].xpath("./div[h3]")
#         captions = [fig.xpath("h3")[0].text for fig in figures]
#         imgs = [fig.xpath("img")[0] for fig in figures]
#         captioned_figures = list(zip(imgs, captions))
#         return captioned_figures
#     except Exception as e:
#         return None
#
def _ipcc_create_zip_caption_table(chapter_html):
    # search for figures captions in html
    """
    :param chapter_html: chapter (currently in WG1 only)
    :return: Zipped (caption table)
    """
    """
    IPCC WG1 uses a strange approach to captions and puts a <strong> before the table
    WG2 is different :-(
    """
    """#table001"""
    """
    <div class="_idGenObjectStyleOverride-1" id="_idContainer031">
      <strong class="Body-copy_Figures--tables-etc_•-Figure-title--bold-to-------spans-columns" lang="en  -US">
        <span class="•-Figure-table-number---title">
          <span class="•-Bold-condensed--dark-blue-">Table 5.1 | </span>
        </span>
        <span class="•-Bold-condensed--dark-blue-">Global anthropogenic CO</span>
        <sub class="•-Bold-condensed-subscript _idGenCharOverride-1" lang="en-GB">2</sub>
        <span class="•-Bold-condensed--dark-blue-"> budget accumulated since the Industrial Revolution (onset in 1750) and averaged over the 1980s, 1990s, 2000s, and 2010s</span>. By convention, a negative ocean or land to atmosphere CO<sub class="•-Subscript--e-g--for-CO2-etc- _idGenCharOverride-1">2</sub> flux is equivalent to a gain of carbon by these reservoirs. The table does not include natural exchanges (e.g., rivers, weathering) between reservoirs. Uncertainties represent the 68% confidence interval (<a class="reference-link" href="#Friedlingstein--2020">Friedlingstein et al., 2020</a>). </strong>
      <table class="IPCC-Table" id="table001">
            <colgroup><col class="_idGenTableRowColumn-1">
              <col class="_idGenTableRowColumn-2">
              <col class="_idGenTableRowColumn-2">
              <col class="_idGenTableRowColumn-2">
              <col class="_idGenTableRowColumn-2">
              <col class="_idGenTableRowColumn-2">
              <col class="_idGenTableRowColumn-2">
            </colgroup>
            <thead>
              <tr class="IPCC-Table _idGenTableRowColumn-3">
              <td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"></td>
              <td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-">
              <p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">1750–2019</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Cumulative</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC)</p></td><td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">1850–2019</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Cumulative</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC)</p></td><td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">1980–1989</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Mean Annual Growth Rate</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC yr<sup class="•-Superscript--e-g--footnote-refs-in-text- _idGenCharOverride-1">–1</sup>)</p></td><td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">1990–1999</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Mean Annual Growth Rate</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC yr<sup class="•-Superscript--e-g--footnote-refs-in-text- _idGenCharOverride-1">–1</sup>)</p></td><td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">2000–2009</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Mean Annual Growth Rate</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC yr<sup class="•-Superscript--e-g--footnote-refs-in-text- _idGenCharOverride-1">–1</sup>)</p></td><td class="IPCC-Table •-Header-row--blue- •-Header-row--blue-"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">2010–2019</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">Mean Annual Growth Rate</p><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-header-row-" lang="en-US">(PgC yr<sup class="•-Superscript--e-g--footnote-refs-in-text- _idGenCharOverride-1">–1</sup>)</p></td></tr></thead><tbody><tr class="IPCC-Table _idGenTableRowColumn-4"><td class="IPCC-Table •-Body-row •-Body-row" colspan="7"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US"><span class="•-Bold-condensed" lang="en-GB">Emissions</span></p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-5"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Fossil fuel combustion and cement production</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">445 ± 20</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">445 ± 20</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">5.4 ± 0.3</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">6.3 ± 0.3</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">7.7 ± 0.4</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">9.4 ± 0.5</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-4"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Net land-use change</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">240 ± 70</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">210 ± 60</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">1.3 ± 0.7</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">1.4 ± 0.7</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">1.4 ± 0.7</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">1.6 ± 0.7</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-6"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Total emissions</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">685 ± 75</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">655 ± 65</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">6.7 ± 0.8</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">7.7 ± 0.8</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">9.1 ± 0.8</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">10.9 ± 0.9</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-4"><td class="IPCC-Table •-Body-row •-Body-row" colspan="7"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US"><span class="•-Bold-condensed" lang="en-GB">Partition</span></p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-6"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Atmospheric increase</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">285 ± 5</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">265 ± 5</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">3.4 ± 0.02</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">3.2 ± 0.02</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">4.1 ± 0.02</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">5.1 ± 0.02</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-4"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Ocean sink</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">170 ± 20</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">160 ± 20</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">1.7 ± 0.4</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.0 ± 0.5</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.1 ± 0.5</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.5 ± 0.6</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-6"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US">Terrestrial sink</p></td>
              <td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">230 ± 60</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">210 ± 55</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.0 ± 0.7</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.6 ± 0.7</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">2.9 ± 0.8</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">3.4 ± 0.9</p></td></tr><tr class="IPCC-Table _idGenTableRowColumn-4"><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--left-align" lang="en-US"><span class="•-Bold-condensed" lang="en-GB">B</span><span class="•-Bold-condensed" lang="en-GB">udget imbalance</span></p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">0</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">20</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">–0.4</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">–0.1</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">0</p></td><td class="IPCC-Table •-Body-row •-Body-row"><p class="Body-copy_Figures--tables-etc_Table-styles_•-Table-body-row--black--centre-align" lang="en-US">–0.1</p>
              </td>
              </tr>
              </tbody>
        </table></div>"""
    # table_containers = chapter_html.xpath("//div[table[starts-with(@id,'table')")
    # table_containers = chapter_html.xpath("//div[@class='_idGenObjectStyleOverride-1']")
    # table_containers = chapter_html.xpath("//table[@class='IPCC-Table']")
    table_containers = chapter_html.xpath("//div[table]")
    logger.info(f"len {len(table_containers)}")
    captions = []
    tables = []
    for table_container in table_containers:
        strong_children = table_container.xpath("strong")
        table_children = table_container.xpath("table")
        caption = "None" if len(strong_children) == 0 else "".join(strong_children[0].itertext())
        table = "No table" if len(table_children) == 0 else table_children[0]
        logger.info(f"strong {len(strong_children)} tables {len(table_children)} {caption}")
        captions.append(caption)
        tables.append(table)

    logger.info (f"table count {len(table_containers)}")
    assert len(table_containers) > 0
    return list(zip(tables, captions))


wg1_chapter_nums = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16",
                    "17", "18", ]

wg1_chapter_files = [Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1",
                      f"Chapter{chapter_num}", "html_with_ids.html")
                 for chapter_num in wg1_chapter_nums]

wg_dict = {"wg1": "WGI", "wg2": "WGII", "wg3": "WGIII", }
AR6_URL = "https://www.ipcc.ch/report/ar6"
DOWNLOAD_AR6_URL = "downloads/report/IPCC_AR6"
DOT_PDF = ".pdf"


def make_hits_by_url(html1):
    """
    <body>
      <ul>
        <li>term: xyz
          <li><a href-to-para
    """
    # iterate over hit list
    body = HtmlLib.get_body(html1)
    query_ul = HtmlLib.get_first_object_by_xpath(body, "ul")
    hits_by_url = dict()
    for li in query_ul.xpath("li"):
        p0 = HtmlLib.get_first_object_by_xpath(li, "p")
        term = p0.text
        txt = "term: "
        if (term.startswith(txt)):
            term = term[len(txt):]
        hits_ul = HtmlLib.get_first_object_by_xpath(li, "ul")
        hits_li_list = hits_ul.xpath("li")
        for hits_li in hits_li_list:
            add_hit_list_to_hits_by_url(hits_by_url, hits_li, term)

    return hits_by_url


def add_hit_list_to_hits_by_url(hits_by_url, hits_li, term):
    a = HtmlLib.get_first_object_by_xpath(hits_li, "a")
    href = a.attrib.get("href")
    href_target = href.split("#")[0]
    id = href.split("#")[1]
    html_targ = HtmlLib.parse_html(href_target)
    if "[" in id:
        id_list = TextUtil.convert_quoted_list_to_list(id)
        # logger.debug(f"id_list {id_list}")
        for id1 in id_list:
            # logger.debug(f"id1 {id1}")
            _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id1, term)
    else:
        _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id, term)
    # logger.debug(f"len (hits_by_url) {len(hits_by_url)}")


def _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id, term):
    p = HtmlLib.get_element_by_id(html_targ, id)
    # p_text = "".join(p.itertext())
    # logger.debug(f"{term}: {href_target} + {id} => {p_text}")
    if p is not None:
        tuple = (term, p)
        target_id = f"{href_target}#{id}"
        hits_by_url[target_id] = (tuple)



class AmiCorpusTest(AmiAnyTest):

    def test_simple_corpus(self):
        """
        creates a simple tree of containers and documents with token content
        """
        corpus_dir = Path(Resources.TEMP_DIR, "corpus")
        assert corpus_dir.exists()

        corpus = AmiCorpus(corpus_dir, mkdir=True)

        report1 = corpus.create_corpus_container(
            Path(corpus_dir, "report1"), bib_type="report", mkdir=True)
        assert str(report1.file.absolute()) == str(Path(Resources.TEMP_DIR, "corpus", "report1").absolute())
        assert report1.file.exists()

        chapter11 = report1.create_corpus_container("chapter11", bib_type="chapter", mkdir=True)
        assert str(chapter11.file.absolute()) == str(
            Path(Resources.TEMP_DIR, "corpus", "report1", "chapter11").absolute())
        html11 = chapter11.create_document("text.html", text="chapter11")
        assert str(html11.absolute()) == str(Path(
            Resources.TEMP_DIR, "corpus", "report1", "chapter11", "text.html").absolute())

        chapter12 = report1.create_corpus_container("chapter12", bib_type="chapter", mkdir=True)
        assert str(chapter12.file.absolute()) == str(Path(Resources.TEMP_DIR, "corpus", "report1", "chapter12").absolute())
        html12 = chapter12.create_document("text.html", text="chapter12")
        assert str(html12.absolute()) == str(Path(
            Resources.TEMP_DIR, "corpus", "report1", "chapter12", "text.html").absolute())

        report2 = corpus.create_corpus_container(Path(corpus_dir, "report2"), mkdir=True)
        assert str(report2.file.absolute()) == str(Path(Resources.TEMP_DIR, "corpus", "report2"))
        chapter21 = report2.create_corpus_container("chapter21", bib_type="chapter", mkdir=True)
        html21 = chapter21.create_document("text.html", text="chapter21")

        chapter22 = report2.create_corpus_container("chapter22", bib_type="chapter", mkdir=True)
        html22 = chapter22.create_document("text.html", text="chapter22")
        assert html22.exists()
        assert str(html22.absolute()) == str(Path(Resources.TEMP_DIR, "corpus", "report2", "chapter22", "text.html"))

    def test_ipcc_corpus(self):
        """
        make corpus from globbed html files, populate it, and extract the datatables as html
        """
        top_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
        assert top_dir.exists()
        corpus = AmiCorpus(top_dir, mkdir=False, make_descendants=True)
        # this only does WGs as the SR*s don't yet havehtml_with_ids
        html_glob = "./**/html_with_ids.html"  # omit datatables.html
        table_id = "table1"
        labels = ["file"]

        datatables_path = Path(top_dir, "datatables.html")
        corpus.create_datatables_html_with_filenames(html_glob, labels, table_id, outpath=datatables_path)
        assert datatables_path.exists()

    def test_unfccc_corpus(self):
        """
        make corpus from globbed html files, populate it, and extract the datatables as html
        """
        unfccc_dir = Path(Resources.TEST_RESOURCES_DIR, "unfccc", "unfcccdocuments1")
        assert unfccc_dir.exists()
        corpus = AmiCorpus(unfccc_dir, mkdir=False, make_descendants=True)
        html_glob = "./**/total_pages*.html"  # omit datatables.html
        table_id = "table1"
        labels = ["file", "total_pages"]
        labels = ["file"]

        datatables_path = Path(unfccc_dir, "datatables.html").resolve()
        corpus.create_datatables_html_with_filenames(html_glob, labels, table_id, outpath=datatables_path)
        assert datatables_path.exists()

    def test_list_files_from_ipcc(self):
        """
        reads all IPCC htmls and creates a corpus/datatables
        """
        """https://github.com/semanticClimate/ipcc/tree/main/cleaned_content"""
        # Github repository is https://github.com/semanticClimate/ipcc
        # clone tnis
        # *****top director on PMR's machine = needs altering for youu implementation*****
        ipcc_top = Path(Resources.TEST_RESOURCES_DIR, "ipcc")

        assert ipcc_top.exists(), f"{ipcc_top} should exist, you need to change this for your machine"
        cleaned_content_dir =  Path(ipcc_top, "cleaned_content").resolve() # cleans the filename (removes "..")
        logger.info(f"ipcc_dir {cleaned_content_dir}")
        assert cleaned_content_dir.exists(), f"{cleaned_content_dir} should exist"

        report_glob_str = f"{str(cleaned_content_dir)}/*"
        logger.info(f"glob {report_glob_str}")
        report_dirs = FileLib.posix_glob(report_glob_str, recursive=False)
        report_dirs = FileLib.get_children(cleaned_content_dir, dirx=True)
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

    @unittest.skip("Obsolete")
    def test_create_corpus_from_ipcc(self):
        """
        FAILS needs reletive file addressing
        """

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

        # ipcc_top = Path(Resources.TEST_RESOURCES_DIR, "..", "..", "..", "..", "projects", "ipcc")
        # ipcc_top = Path(Resources.TEST_RESOURCES_DIR, )

        # assert ipcc_top.exists(), f"{ipcc_top} should exist, you need to change this for your machine"
        corpus_dir =  Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content") # cleans the filename (removes "..")
        assert corpus_dir.exists()
        corpus_files = FileLib.get_children(corpus_dir, dirx=True)
        assert len(corpus_files) > 0, f"no files in {corpus_dir}"
        labels = [REPORT, REMOTE_CHAPTER, REMOTE_PDF, CLEANED_CHAPTER, CHAP_WITH_IDS]

        datatables = True
        table_id = "table1"
        htmlx, tbody = Datatables.create_table(labels, table_id)

        ami_corpus = AmiCorpus()
        for corpus_file in sorted(corpus_files):
            corpus_text = AmiCorpusContainer(corpus_file, "stem")
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
                cls._output_chapter_row(work, chapter_dir, tbody)

        if datatables:
            Datatables.add_head_info(HtmlLib.get_head(htmlx), htmlx)
            Datatables.add_body_scripts(HtmlLib.get_body(htmlx), table_id=table_id)


        HtmlLib.write_html_file(htmlx, Path(corpus_dir, "datatables.html"), debug=True)


    def _output_chapter_row(cls, IPCC_CH, arx, chapter_dir, report, roman, tbody):
        cls = AmiCorpus
        stem = Path(chapter_dir).stem
        chap_no = stem[-2:]
        if chap_no.startswith("0"):
            chap_no = chap_no[1:]
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

    @classmethod
    def add_content_for_files(cls, files, tr):
        if files:
            cls.add_cell_content(tr, text=Path(files[0]).stem, href=f"file://{files[0]}")
        else:
            cls.add_cell_content(tr, text="?")


    def test_make_ipcc_report_corpus(self):
        """
        read report directory and make corpus
        """
        wg1_dir = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1")
        assert wg1_dir.exists(), f"wg1 {wg1_dir} should exist"
        wg1_corpus = AmiCorpus(wg1_dir)
        assert wg1_corpus.root_dir == wg1_dir
        wg1_corpus.make_descendants()

    def test_get_column_from_data_tables(self):
        """
        get a column from existing datatables file
        """
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        # logger.info(f"datatables is: {datatables_file}")
        assert datatables_file.exists()
        datatables_html = HtmlLib.parse_html(datatables_file)
        col_content = Datatables.extract_column(datatables_html, colindex="file")
        assert len(col_content) == 48
        assert "".join(col_content[2].itertext()) == "wg1/Chapter02/html_with_ids.html"

    def test_transform_column_data_tables(self):
        """
        get a column from existing datatables file
        """

        # @classmethod
        def make_td_with_ahref_from_text(atext, href):
            """
            makes td element (for table cell) containing  <a href=href>atext</a>
            :param atext: body of a
            :param href: value of href
            """
            td = ET.Element("td")
            a = ET.SubElement(td, "a")
            a.text = atext
            if href is None:
                href = atext
            a.attrib["href"] = href
            return td

        def make_td_with_ahref_from_cell_content(cell):
            text0 = "".join(cell.itertext())
            text = str(Path(text0).parent)
            td = make_td_with_ahref_from_text(text, text)
            return td

        def make_ipcc_td_with_remote_pdf_url_cell_content(td_elem):
            """
             start with string

             wg1/Chapter02/html_with_ids.html

             and create

             https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Chapter02.pdf
            """
            strng = "".join(td_elem.itertext())
            # extract report (wg1) and chapter (Chapter02)

            regex = "(?P<report>wg\d)/(?P<chapter>Chapter\d\d)/html_with_ids.html"
            match = re.match(regex, strng)
            if not match:
                return None
            report = match.group("report")
            chapter = match.group("chapter")
            wg = wg_dict.get(report)
            # https://www.ipcc.ch/report/ar6/('wg1',%20'Chapter04')/downloads/report/IPCC_AR6_None_('wg1',%20'Chapter04').pdf
            url = f"{AR6_URL}/{report}/{DOWNLOAD_AR6_URL}_{wg}_{chapter}{DOT_PDF}"
            print(f"url {url}")

            td = make_td_with_ahref_from_text(f"{wg} {chapter}", url)
            return td



        # example function
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        assert datatables_file.exists()
        datatables_html = HtmlLib.parse_html(datatables_file)
        col_content = Datatables.extract_column(datatables_html, colindex="file")

        dirs = list(map(lambda cell: make_td_with_ahref_from_cell_content(cell), col_content))
        Datatables.insert_column(datatables_html, dirs, "chapter_dir")

        pdfs = list(map(lambda cell: make_ipcc_td_with_remote_pdf_url_cell_content(cell), col_content))
        Datatables.insert_column(datatables_html, pdfs, "PDFchapter")

        datatables_file2 = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_pdf_dir.html")
        HtmlLib.write_html_file(datatables_html, datatables_file2, debug=True)

    def test_ipcc_add_executive_summmary_and_acknow_to_datatables(self):
        """
        get a column listing hyperlinks to documents from existing datatables file
        create a new column pointing to subcomponents of the document
        """
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        datatables_html = HtmlLib.parse_html(datatables_file)

        # list to receive td's
        id_ref = "Executive"
        new_content = "Executive Summary"
        new_column_title = "exec_summary"
        new_datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_exec.html")
        Datatables.add_column_with_ahref_pointers_to_sections_with_ids(datatables_file,
                                                                       id_ref,
                                                                       new_column_title,
                                                                       new_content,
                                                                       new_datatables_file)

        # list to receive td's
        new_column_title = "acknowledgements"
        new_datatables_file2 = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_exec_ack.html")
        Datatables.add_column_with_ahref_pointers_to_sections_with_ids(new_datatables_file,
                                                                       "acknowledgements",
                                                                       "acknowledgements",
                                                                       "Acknowledgements",
                                                                       new_datatables_file2)



    def test_extract_figures_from_chapter(self):
        """
        read IPCC Chapter and extract figures
        """
        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter05", "html_with_ids.html")
        outpath = Path(Resources.TEMP_DIR, "datatables", "chapter_wg1_5_figures.html")

        HtmlLib.create_scrolling_thumbnails_from_html_images(chapter_file, HtmlLib._ipcc_create_zip_caption_img,
                                                          outpath)


    def test_extract_tables_from_chapter(self):
        """
        read IPCC Chapter and extract figures
        """
        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter05", "html_with_ids.html")
        chapter_html = HtmlLib.parse_html(chapter_file)
        outpath = Path(Resources.TEMP_DIR, "datatables", "chapter_wg1_5_tables.html")

        htmlx = HtmlLib.create_html_with_scrolling_style()
        body = HtmlLib.get_body(htmlx)
        scroll_div = ET.SubElement(body, "div")
        scroll_div.attrib["class"] = SCROLL_PARENT

        # search for tables
        captioned_tables = _ipcc_create_zip_caption_table(chapter_html)
        HtmlLib.create_horizontal_scrolling_thumbnails_with_tables(captioned_tables, scroll_div)
        HtmlLib.write_html_file(htmlx, outpath, debug=True)

    def test_extract_figures_from_wg1(self):
        """
        read IPCC Chapter and extract figures
        """
        outpath = Path(Resources.TEMP_DIR, "datatables", "chapter_wg1_figures.html")

        htmlx = HtmlLib.create_html_with_scrolling_style()
        body = HtmlLib.get_body(htmlx)

        for chapter_file in wg1_chapter_files:        # search for figure container
            if not chapter_file.exists():
                logger.info(f"file does not exist {chapter_file}")
                continue
            scroll_div = ET.SubElement(body, "div")
            scroll_div.attrib["class"] = SCROLL_PARENT
            chapter_html = HtmlLib.parse_html(chapter_file)

            captioned_figures = HtmlLib.create_scrolling_thumbnails_from_html_images(
                chapter_file,
                HtmlLib._ipcc_create_zip_caption_img,
                outpath)

            HtmlLib.create_horizontal_scrolling_thumbnails_with_hrefs(captioned_figures, scroll_div)
        HtmlLib.write_html_file(htmlx, outpath, debug=True)

    def test_extract_tables_from_wg1(self):
        """
        read IPCC Chapter and extract figures
        """
        chapter_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter05", "html_with_ids.html")
        chapter_html = HtmlLib.parse_html(chapter_file)
        outpath = Path(Resources.TEMP_DIR, "datatables", "chapter_wg1_tables.html")

        htmlx = HtmlLib.create_html_with_scrolling_style()
        body = HtmlLib.get_body(htmlx)

        for chapter_file in wg1_chapter_files:        # search for figure container
            if not chapter_file.exists():
                logger.info(f"file does not exist {chapter_file}")
                continue
            scroll_div = ET.SubElement(body, "div")
            scroll_div.attrib["class"] = SCROLL_PARENT
            chapter_html = HtmlLib.parse_html(chapter_file)
            captioned_tables = _ipcc_create_zip_caption_table(chapter_html)
            HtmlLib.create_horizontal_scrolling_thumbnails_with_tables(captioned_tables, scroll_div)
        HtmlLib.write_html_file(htmlx, outpath, debug=True)

    def test_add_many_columns_to_wg1_datatables(self):
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        datatables_html = HtmlLib.parse_html(datatables_file)

        # list to receive td's
        id_ref = "Executive"
        new_content = "Executive Summary"
        new_column_title = "exec_summary"

        new_datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_exec1.html")
        Datatables.add_column_with_ahref_pointers_to_sections_with_ids(datatables_file, id_ref, new_column_title,
                                                                       new_content, new_datatables_file)

        # list to receive td's
        new_column_title = "acknowledgements"
        new_datatables_file2 = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_ack1.html")
        Datatables.add_column_with_ahref_pointers_to_sections_with_ids(
            new_datatables_file, "acknowledgements",
            "acknowledgements",
            "Acknowledgements",
            new_datatables_file2)


    def test_search_and_create_term_href_p_table(self):

        """
        read chapter, search for words and return list of paragraphs/ids in which they occur
        simple, but requires no server
        """
        debug = True
        query = "bananas_millet_climate"
        xpath = None
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(indir, f"{query}.html")
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        assert 50 == len(infiles)
        phrases = [
            "bananas",
            "millet",
            # "wheat",
            "climate justice",
        ]

        html1 = AmiCorpus.search_files_with_phrases_write_results(
            infiles, phrases=phrases, xpath=xpath, outfile=outfile, debug=debug)

        assert html1 is not None
        assert len(html1.xpath("//p")) > 0
        term_id_by_url = make_hits_by_url(html1)
        logger.debug(f"term_id_by_url {len(term_id_by_url)} {term_id_by_url}")
        term_ref_p_tuple_list = self.get_hits_as_term_ref_p_tuple_list(term_id_by_url)

        htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        self._add_hits_to_table(tbody, term_ref_p_tuple_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

        # markup para with nyperlink
        # new html document
        htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        new_term_ref_p_list = []
        for (term, ref, para) in term_ref_p_tuple_list:
            para_new = HtmlLib.para_contains_phrase(para, term, ignore_case=True, markup=True)
            new_term_ref_p_list.append((term, ref, para))
        self._add_hits_to_table(tbody, new_term_ref_p_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_markup_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

        # datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        # datatables_html = HtmlLib.parse_html(datatables_file)

        """
        <tr> 
          <td class="sorting_1">
            <a href="syr/longer-report/html_with_ids.html">syr/longer-report/html_with_ids.html</a>
          </td>
        </tr>
        """
        # tds = datatables_html.xpath("//body/table/tbody/tr/td")
        # logger.info(f"tds {len(tds)}")
        # # keys in datatables
        # for td in tds:
        #     a_ = td.xpath('a')[0]
        #     logger.debug(f"td {a_.attrib['href']} {a_.text}")
        #
        # # list to receive td's
        # id_ref = "Executive"
        # new_content = "Executive Summary"
        # new_column_title = "exec_summary"
        #
        # new_datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_exec1.html")
        # Datatables.add_column_with_ahref_pointers_to_sections_with_ids(
        #     datatables_file, id_ref, new_column_title, new_content, new_datatables_file)

    def test_search_corpus_with_wordlist(self):
        """
        reads words from file and searches corpus giving term_oriented table
        """
        debug = True
        query = "carbon_cycle"
        xpath = None
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(indir, f"{query}.html")
        globstr = f"{str(indir)}/**/{HTML_WITH_IDS}.html"
        infiles = FileLib.posix_glob(globstr, recursive=True)
        path = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "carbon_cycle_noabb.txt")
        phrases = FileLib.read_strings_from_path(path)

        logger.debug(f"phrases {len(phrases)}")

        html1 = AmiCorpus.search_files_with_phrases_write_results(
            infiles, phrases=phrases, xpath=xpath, outfile=outfile, debug=debug)

        term_id_by_url = make_hits_by_url(html1)
        logger.debug(f"term_id_by_url {len(term_id_by_url)} {term_id_by_url}")
        term_ref_p_tuple_list = self.get_hits_as_term_ref_p_tuple_list(term_id_by_url)
        htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        self._add_hits_to_table(tbody, term_ref_p_tuple_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

    def _add_hits_to_table(self, tbody, term_ref_p_tuple_list):
        for term, ref, p in term_ref_p_tuple_list:
            assert type(term) is str
            assert type(ref) is str
            assert type(p) is _Element or type(p) is HtmlElement
            tr = ET.SubElement(tbody, "tr")
            tds = []
            for item in term, ref, p:
                tds.append(ET.SubElement(tr, "td"))
            tds[0].text = term
            a = ET.SubElement(tds[1], "a")
            a.attrib["href"] = ref
            a.text = ref

            tds[2].append(p)

    def get_hits_as_term_ref_p_tuple_list(self, term_id_by_url):
        trp_list = []
        for ref in term_id_by_url.keys():
            bits = ref.split("#")
            file = bits[0]
            idref = bits[1]
            term_p = term_id_by_url.get(ref)
            term = term_p[0]
            p = term_p[1]
            # logger.debug(f"{term}:{idref} => {''.join(p.itertext())}")
            tuple = (term, ref, p)
            trp_list.append(tuple)

        return trp_list

    # ================ NYI ===============

    @unittest.skip("NYI")
    def test_ipcc_add_figures_to_datatables(self):
        """
        get a column listing hyperlinks to documents from existing datatables file
        create a new column pointing to subcomponents of the document
        """
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        datatables_html = HtmlLib.parse_html(datatables_file)

        # list to receive td's
        # id_ref = "Executive"
        new_content = "Figures"
        new_column_title = "figures"
        new_datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_figures1.html")
        Datatables.add_column_with_ahref_pointers_to_figures(
            datatables_file, new_content, new_datatables_file, new_column_title)

        # NYI
    def test_ipcc_add_tables_to_datatables(self):
        """
        """
        datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables.html")
        datatables_html = HtmlLib.parse_html(datatables_file)

        # list to receive td's
        # id_ref = "Executive"
        new_content = "Tables"
        new_column_title = "tables"
        new_datatables_file = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "datatables_tables.html")
        Datatables.add_column_with_ahref_pointers_to_tables(datatables_file, new_content, new_datatables_file,
                                                                 new_column_title)
        # NYI

# ===================== snippets ===================
"""
HTML, NO Javascript
Top level div contains two children tab-list and tab_display
In tab_list a list of (caption, table) pairs.
all tables in the list should be initially hidden
clicking on a caption will display the table in tab_display
Please give sample code for a list of 3 small tables
"""
"""


You can create this behavior using pure HTML and CSS, without relying on JavaScript. 
The key to achieving this functionality is leveraging the :checked pseudo-class combined with input elements and label elements. 
Here's how you can implement it:

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Table Display</title>
  <style>
    .container {
      display: flex;
      flex-direction: column;
      width: 60%;
      margin: 0 auto;
    }

    .tables {
      display: flex;
      flex-direction: column;
    }

    .caption {
      cursor: pointer;
      padding: 10px;
      background-color: #f1f1f1;
      border: 1px solid #ccc;
      text-align: center;
      margin-bottom: 5px;
      transition: background-color 0.3s;
    }

    .caption:hover {
      background-color: #e0e0e0;
    }

    .table {
      display: none;
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }

    .table th, .table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }

    input[type="radio"] {
      display: none;
    }

    input[type="radio"]:checked + label + .tables .table {
      display: table;
    }
  </style>
</head>
<body>

  <div class="container">
    <div class="tables">
      <!-- Table 1 -->
      <input type="radio" id="table1" name="table" />
      <label class="caption" for="table1">Table 1 Caption</label>
      <div class="table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Age</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Alice</td>
              <td>24</td>
            </tr>
            <tr>
              <td>Bob</td>
              <td>30</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table 2 -->
      <input type="radio" id="table2" name="table" />
      <label class="caption" for="table2">Table 2 Caption</label>
      <div class="table">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Phone</td>
              <td>$500</td>
            </tr>
            <tr>
              <td>Laptop</td>
              <td>$1000</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table 3 -->
      <input type="radio" id="table3" name="table" />
      <label class="caption" for="table3">Table 3 Caption</label>
      <div class="table">
        <table>
          <thead>
            <tr>
              <th>City</th>
              <th>Population</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>New York</td>
              <td>8,623,000</td>
            </tr>
            <tr>
              <td>Los Angeles</td>
              <td>3,990,000</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

</body>
</html>
How It Works:
Radio Buttons & Labels: Each table is associated with a radio input and a label. 
Clicking the label (which acts as the caption) triggers the corresponding radio input.

CSS Display Management:

Initially, all tables are hidden using display: none;.
When a radio button is selected (via :checked), the corresponding table becomes visible using display: table;.
Input/Label Interaction: The input[type="radio"] elements are visually hidden (display: none;), 
and the associated label elements act as clickable captions. When a user clicks a caption (label), 
the corresponding radio button is checked, and the CSS rule applies to make the respective table visible.

Single Table Display: Since all radio buttons share the same name attribute (name="table"), 
only one radio button can be checked at a time. This ensures that only one table is displayed at any given moment.

This is a simple, JavaScript-free solution for toggling between multiple tables using just HTML and CSS.

------------------------------------
Sure! Here's a sample HTML code that meets your requirements:

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tab Display</title>
<style>
.tab_list div {
cursor: pointer;
margin: 5px 0;
padding: 5px;
background-color: #f0f0f0;
border: 1px solid #ccc;
}
.tab_display table {
display: none;
width: 100%;
border-collapse: collapse;
}
.tab_display table, .tab_display th, .tab_display td {
border: 1px solid black;
}
.tab_display th, .tab_display td {
padding: 8px;
text-align: left;
}
</style>
</head>
<body>
<div class="tab_list">
<div onclick="showTable('table1')">Caption 1</div>
<div onclick="showTable('table2')">Caption 2</div>
<div onclick="showTable('table3')">Caption 3</div>
</div>
<div class="tab_display">
<table id="table1">
<tr><th>Header 1</th><th>Header 2</th></tr>
<tr><td>Data 1</td><td>Data 2</td></tr>
</table>
<table id="table2">
<tr><th>Header A</th><th>Header B</th></tr>
<tr><td>Data A</td><td>Data B</td></tr>
</table>
<table id="table3">
<tr><th>Header X</th><th>Header Y</th></tr>
<tr><td>Data X</td><td>Data Y</td></tr>
</table>
</div>

<script>
function showTable(tableId) {
var tables = document.querySelectorAll('.tab_display table');
tables.forEach(function(table) {
table.style.display = 'none';
});
document.getElementById(tableId).style.display = 'table';
}
</script>
</body>
</html>

This code creates a simple tab system where clicking on a caption in the tab_list will display the corresponding table 
in the tab_display section. Initially, all tables are hidden, and only the selected table is shown when a caption is clicked.

Feel free to modify the content and style as needed!







ChatGPT can make mistakes. Check important info.
?
"""
