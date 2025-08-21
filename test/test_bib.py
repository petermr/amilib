import ast
import collections
import configparser
import glob
import json
import logging
import re
import unittest
from re import RegexFlag

import lxml.etree as ET
from pathlib import Path
import pandas as pd
import pytest
from lxml.etree import _Element, XMLSyntaxError
from lxml.html import HtmlElement

from amilib.ami_bib import (SAVED, SAVED_CONFIG_INI, SECTION_KEYS, API, LIMIT, QUERY, STARTDATE, XML, \
                            EUPMC_RESULTS_JSON, PMCID, ABS_TEXT, EPMC_KEYS, JOURNAL_INFO, DOI, TITLE, AUTHOR_STRING,
                            PUB_YEAR, JOURNAL_INFO_TITLE, Pygetpapers, JATSDoc)
from amilib.ami_html import HtmlUtil, HtmlLib, Datatables, SCROLL_PARENT, ANNOTATION
from amilib.ami_util import AmiJson, AmiUtil
from amilib.ami_corpus import AmiCorpus, AmiCorpusContainer, CorpusQuery, HTML_WITH_IDS, OpenAlex
from amilib.amix import AmiLib
from amilib.file_lib import FileLib
from amilib.util import Util, TextUtil
from amilib.xml_lib import XmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)

class AmiBibliographyTest(AmiAnyTest):
    """

    """
    # @classmethod
    # def convert_csv_to_bib(cls):
    #     """
    #
    #     """

    def test_iconize_references(self):
        """
        find references and reduce to a single char
        """
        infile = Path(self.TEST_WG1_05, f"{HTML_WITH_IDS}.html")
        logger.info(f"reading {infile}")
        assert infile.exists(), f"infile {infile} does not exist"
        htmlx = HtmlLib.parse_html(infile)
        assert htmlx is not None
        para = XmlLib.get_single_element(htmlx, ".//p[@id='5.1.1_p1']")
        assert para is not None
        """
<a class="reference-link" href="#Williams--2019">Williams et al., 2019</a>
        """
        xpath = ".//a[@class='reference-link']"
        HtmlLib.iconize_hyperlinks(htmlx, xpath)
        HtmlLib.write_html_file(htmlx, outfile=str(Path(self.TEMP_HTML_DIR, "misc", "dereferenced.html")), debug=True)

    # @classmethod
    # def iconize_hyperlinks(cls, htmlx, xpath):
    #     anchors = htmlx.xpath(xpath)
    #     for anchor in anchors:
    #         if anchor.text is not None and len(anchor.text.strip()) > 0:
    #             anchor.text = anchor.text.strip()
    #             anchor.attrib["title"] = anchor.text
    #             anchor.text = AmiAnyTest.REFERENCE_TEXT


def df_to_ahref_string(s):
    """
    converte a URL to an anchro element
    I don't know whether this does what is wanted!"""
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
        df[PMCID] = df[PMCID].apply(df_to_ahref_string)
        df[ABS_TEXT] = df[ABS_TEXT].apply(df_truncate)
        df[JOURNAL_INFO] = df[JOURNAL_INFO].apply(df_unpack_dict)
        df2 = df[[PMCID, DOI, TITLE, AUTHOR_STRING, JOURNAL_INFO, PUB_YEAR, ABS_TEXT]]

        with open(outfile, "w", encoding="UTF-8") as f:
            f.write(df2.to_csv())
        with open(outfile_h, "w", encoding="UTF-8") as f:
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
        args = ["HTML",
                "--indir", str(indir),
                # "--indir", "/Users/pm286/workspace/amilib/test/resources/json/district_heating",
                "--operation", "DATATABLES"]
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
        # Use cross-platform recursive globbing
        infiles = list(indir.rglob(f"*/{HTML_WITH_IDS}.html"))
        assert 50 <= len(infiles) <= 55
        phrases = [
            "bananas",
            "South Asia",
        ]
        html1 = AmiCorpus.search_files_with_phrases_write_results(infiles, phrases=phrases, para_xpath=xpath, outfile=outfile, debug=debug)
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
        # Use cross-platform recursive globbing
        infiles = list(path.rglob(f"*/{HTML_WITH_IDS}.html"))
        phrases = [
            "bananas",
            "South Asia"
        ]
        html1 = AmiCorpus.search_files_with_phrases_write_results(infiles, phrases=phrases, outfile=outfile, debug=debug)

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


# def extract_hits_by_url_from_nested_lists(nested_list_html):
#     """
#     <body>
#       <ul>
#         <li>term: xyz
#           <li><a href-to-para
#     """
#     # iterate over hit list
#     if nested_list_html is None:
#         logger.error(f"html1 is None")
#         return None
#     body = HtmlLib.get_body(nested_list_html)
#     query_ul = HtmlLib.get_first_object_by_xpath(body, "ul")
#     hits_by_url = dict()
#     for li in query_ul.xpath("li"):
#         # logger.debug("li")
#         p0 = HtmlLib.get_first_object_by_xpath(li, "p")
#         if p0 is None:
#             continue
#         term = p0.text
#         txt = "term: "
#         if (term.startswith(txt)):
#             term = term[len(txt):]
#         hits_ul = HtmlLib.get_first_object_by_xpath(li, "ul")
#         if hits_ul is None:
#             continue
#         hits_li_list = hits_ul.xpath("li")
#         # logger.debug(f"hits {len(hits_li_list)}")
#         for hits_li in hits_li_list:
#             # logger.debug(f"hits_li")
#             add_hit_list_to_hits_by_url(hits_by_url, hits_li, term)
#             # logger.debug(f"added hits_li")
#
#     return hits_by_url
#

# def add_hit_list_to_hits_by_url(hits_by_url, hits_li, term):
#     if hits_by_url is None or hits_li is None or term is None:
#         logger.error(f"add_hit_list None args ")
#         return
#     a = HtmlLib.get_first_object_by_xpath(hits_li, "a")
#     if a is None:
#         logger.error(f"a is None")
#         return
#     # logger.debug(f"a is {a}")
#     href = a.attrib.get("href")
#     if href is None:
#         logger.error(f"href is None {ET.tostring(a)}")
#         return
#     # logger.debug(f"href {href}")
#     href_target = href.split("#")[0]
#     id = href.split("#")[1]
#     # logger.debug(f"href_target {href_target}")
#     html_targ = HtmlLib.parse_html(href_target)
#     assert html_targ is not None
#     if "[" in id:
#         # logger.debug("quoted list")
#         id_list = TextUtil.convert_quoted_list_to_list(id)
#         for id1 in id_list:
#             _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id1, term)
#     else:
#         # logger.debug("non quoted list")
#         _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id, term)
#     # logger.debug("exit add hitlist")
#
#
# def _get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id, term):
#     if hits_by_url is None or href_target is None or html_targ is None or id is None or term is None:
#         logger.error("arg is None")
#         return None
#     p = HtmlLib.get_element_by_id(html_targ, id)
#     if p is not None:
#         tuple = (term, p)
#         target_id = f"{href_target}#{id}"
#         hits_by_url[target_id] = (tuple)
#     # logger.debug("exit _get_element_by_id_and_add_term_id_tuple_to_hits")
#

def analyze_exec():
    logger.error("Exec Not implemented")

def analyze_faq():
    logger.error("FAQ Not implemented")

def analyze_references():
    logger.error("Ref Not implemented")


main_key = "corpus"
main_out_dir = Path(Resources.TEMP_DIR, main_key)
crop_id = "crops"
outfile = Path(main_out_dir, f"{crop_id}_out.html")
crop_query = {
    "id" : crop_id,
    "outfile" : str(outfile),
    "phrases" : [
            "maize",
            "millet",
            "rice",
            "wheat"
        ],
        }



def _validate_and_count_table(htmlx, min_entries=10, num_columns = 3):
    """
    validate datatable created by term-based search with ID and paragraph
    :param htmlx: document to test
    :param min_entries: to test it got something useful
    :param num_columns: column count
    """
    # find all paras in "para" column
    id_col = 1
    para_column = 2

    table = XmlLib.get_single_element(htmlx, "/html/body/table")
    tbody = XmlLib.get_single_element(table, "./tbody")
    trs = tbody.xpath("./tr")
    assert len(trs) > min_entries
    # logger.debug(f"rows {len(trs)}")
    missing_markup = []
    for tr in trs:
        tds = tr.xpath("./td")
        assert len(tds) == num_columns
        para_td = tds[para_column]
        ps = para_td.xpath("./p")
        assert len(ps) == 1
        # does p contain a markup/ anchor
        """
        <a class="annotation">methane emissions</a>
        """
        # anchor inserted by markup
        anchor = tds[id_col].xpath(".//a")[0]
        text = anchor.text
        # para_id is in column 2, id is after #
        para_id = text.split("#")[1]
        para = ps[0]
        # does para contain <a> created by amilib markup
        # a_elems = para.xpath(".//a[@style='border:solid 1px; background: #ffffbb;']")
        a_elems = para.xpath(f".//a[@class='{ANNOTATION}']")
        if len(a_elems) == 0:
            logger.error(f"no markup for {para_id}")
            missing_markup.append(para)
        elif (len(a_elems) > 1):
            # logger.debug(f"multiple markup for {len(a_elems)} {para_id=} ")
            pass
        else:
            # logger.debug(f"markup for {len(a_elems)} {para_id=} ")
            pass
    if len(missing_markup) > 0:
        logger.error(f"missing markup for {len(missing_markup)} {missing_markup[:20]}...")


class OpenAlexTest:
    pass
    def __init__(self):
        pass

    @classmethod
    def read_json_create_write_html_table(cls, infile: Path, outfile: Path, wanted_keys: list[str]) -> dict:
        """
        :param infile: input containing JSON metadata from OpenAlex
        :param outfile: tabular metadata in datatables format
        :param wanted_keys: list of openalex keys

        start_key
        JSON_KEY = "papers"
        JSON_KEY = "total_json_output"
        """
        with open(infile, "r", encoding="UTF-8") as f:
            input_dict = json.loads(f.read())
            return input_dict



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

        # Use cross-platform get_children instead of posix_glob
        report_dirs = FileLib.get_children(cleaned_content_dir, dirx=True)
        assert len(report_dirs) == 7, f"child files are {report_dirs}"
        total_chapter_count = 0
        all_cleaned_files = []
        all_html_id_files = []
        for report_dir in sorted(report_dirs):
            report = Path(report_dir).stem
            # Use cross-platform get_children with pattern matching
            chapter_dirs = [d for d in FileLib.get_children(report_dir, dirx=True) if "Chapter" in d.name]
            total_chapter_count += len(chapter_dirs)
            logger.info(f"chapter {report}: {total_chapter_count}")
            for chapter_dir in sorted(chapter_dirs):
                # Use cross-platform get_children with pattern matching
                html_files = [f for f in FileLib.get_children(chapter_dir, dirx=False) if f.suffix == '.html']
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
        # Use cross-platform file checking instead of posix_glob
        gatsby_file = chapter_dir / "de_gatsby.html"
        wordpress_file = chapter_dir / "html_with_ids.html"
        cleaned_files = []
        if gatsby_file.exists():
            cleaned_files.append(gatsby_file)
        if wordpress_file.exists():
            cleaned_files.append(wordpress_file)
        cls.add_content_for_files(cleaned_files, tr)
        html_id_files = [wordpress_file] if wordpress_file.exists() else []
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

    @unittest.expectedFailure
    def test_get_column_from_data_tables(self):
        """
    ("Unreliable input and suspect algorithm")
        test that datatables.html contains the correct information
        get a column from existing datatables file with filenames and extract
        """
        filename = "datatables.html"
        src_dir = Path(Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content"), filename)
        temp_datatables_dir = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content")
        Path.mkdir(temp_datatables_dir, parents=True, exist_ok=True)
        temp_datatables = FileLib.copy_file(filename, src_dir, temp_datatables_dir)
        # logger.info(f"datatables is: {datatables_file}")
        datatables_file = Path(temp_datatables_dir, filename)
        assert datatables_file.exists()
        datatables_html = HtmlLib.parse_html(datatables_file)
        logger.info(f"1000 characters {ET.tostring(datatables_html)[:1000]}")
        colname = "chapter_with_ids"
        col_content = Datatables.extract_column(datatables_html, colindex=colname)
        logger.info(f"col_content[2] {ET.tostring(col_content[2])}")
        assert 52 >= len(col_content) >= 48
        filename = "".join(col_content[2].itertext())
        if filename != "wg1/Chapter02/html_with_ids.html":
            raise ValueError(f"filename {filename} != 'wg1/Chapter02/html_with_ids.html'")

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

            regex = "(?P<report>wg\\d)/(?P<chapter>Chapter\\d\\d)/html_with_ids.html"
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
        query = "methane_emissions"
        xpath = None
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(indir, f"{query}.html")
        # Use cross-platform recursive globbing
        infiles = list(indir.rglob(f"*/{HTML_WITH_IDS}.html"))
        assert 50 <= len(infiles) <= 55
        phrases = [
            "methane emissions"
        ]

        html1 = AmiCorpus.search_files_with_phrases_write_results(
            infiles, phrases=phrases, para_xpath=xpath, outfile=outfile, debug=debug)

        assert html1 is not None
        assert len(html1.xpath("//p")) > 0, f"html1 output should contain paragraphs"
        term_id_by_url = CorpusQuery.extract_hits_by_url_from_nested_lists(html1)
        logger.debug(f"term_id_by_url {len(term_id_by_url)} {term_id_by_url}")
        term_ref_p_tuple_list = CorpusQuery.get_hits_as_term_ref_p_tuple_list(term_id_by_url)

        htmlx, table_body = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        CorpusQuery._add_hits_to_table(table_body, term_ref_p_tuple_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_table_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

        # markup para with nyperlink
        # new html document
        htmlx, table_body = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        new_term_ref_p_list = []
        for (term, ref, para) in term_ref_p_tuple_list:
            has_markup = HtmlLib.find_and_markup_phrases(para, term, ignore_case=True, markup=True)
            ahrefs = para.xpath("./a[@href]")
            # for ahref in ahrefs:
            #     print(f"ahref: {ahref.text}")
            new_term_ref_p_list.append((term, ref, para))
        CorpusQuery._add_hits_to_table(table_body, new_term_ref_p_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_table_markup_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

    def test_tutorial_search_and_create_table_IMPORTANT(self):
        """
        read existing table after markup and check that all paras have markup
        uses output of CorpusQuery._add_hits_to_table
        creates annotations
        """
        corpus_query = CorpusQuery()
        htmlx, query_id = corpus_query.run_query_make_table_TUTORIAL(
            query="methane emissions",
            query_id="methane_emissions",
            indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc'),
            outdir = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content")
        )
        # write html datatable
        table_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query_id}_table_markup_hits.html")
        HtmlLib.write_html_file(htmlx, table_file, debug=True)
        assert table_file.exists()

        _validate_and_count_table(htmlx, min_entries=160)

    def test_tutorial_search_and_create_table_CLI_IMPORTANT(self):
        """
        read existing table after markup and check that all paras have markup
        uses output of CorpusQuery._add_hits_to_table
        """
        query = "methane emissions"
        query_id = "methane_emissions"
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outdir = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content")
        outpath = Path(outdir, f"{query_id}_{AmiCorpus.TABLE_MARKUP_HITS}.html")
        args = [
            "SEARCH",
            "--words", query,
            "--query_id", query_id,
            "--indir", str(indir),
            "--outdir", str(outdir),
            "--outpath", str(outpath),
        ]
        amilib = AmiLib()
        amilib.run_command(args)

        logger.debug(f"wrote to dir {outdir}")
        assert outdir.exists()
        outfile = Path(outdir, f"{query_id}_table_hits.html")
        assert outfile.exists()
        # htmlx, query_id = corpus_query.run_query_make_table_TUTORIAL(
        # )
        # write html datatable
        # HtmlLib.write_html_file(htmlx, table_file, debug=True)
        # assert table_file.exists()

        # _validate_and_count_table(htmlx, min_entries=160)


    def test_search_corpus_with_wordlist_LONG(self):
        """
        reads words from file and searches corpus giving term_oriented table
        """
        debug = True
        query = "carbon_cycle"
        xpath = None
        MAXFILES = 1  # Reduced from 5 for faster testing
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        outfile = Path(Resources.TEMP_DIR, "corpus", f"{query}.html")
        # Use cross-platform recursive globbing
        infiles = list(indir.rglob(f"*/{HTML_WITH_IDS}.html"))
        logger.info(f"found {len(infiles)} files")
        assert len(infiles) > 0, f"failed to find {HTML_WITH_IDS}.html in {indir}"
        words_path = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "carbon_cycle_noabb.txt")
        phrases = FileLib.read_strings_from_path(words_path)
        assert len(phrases) > 0, f"failed to find phrases in {words_path}"

        logger.debug(f"phrases {len(phrases)}")

        search_results_html = AmiCorpus.search_files_with_phrases_write_results(
            infiles[:MAXFILES], phrases=phrases, outfile=outfile, debug=debug)

        term_id_by_url = CorpusQuery.extract_hits_by_url_from_nested_lists(search_results_html)
        logger.debug(f"term_id_by_url {len(term_id_by_url)} {term_id_by_url}")
        term_ref_p_tuple_list = CorpusQuery.get_hits_as_term_ref_p_tuple_list(term_id_by_url)
        htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        assert htmlx is not None
        assert tbody is not None
        CorpusQuery._add_hits_to_table(tbody, term_ref_p_tuple_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query}_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists(), f"{trp_file} should exist"

    def test_create_corpus_with_wordlist_and_search_LONG(self):
        """
        reads words from file and searches corpus giving term_oriented table
        """
        MAXFILES = 5 # to save test time
        MAXFILES = 1  # Reduced from 2 for faster testing
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        query_stem = "carbon_cycle"
        outfile = str(Path(Resources.TEMP_DIR, "corpus", f"{query_stem}.html"))
        ami_corpus = AmiCorpus(
            indir=indir,
            globstr=f"**/{HTML_WITH_IDS}.html",
            # query_stem = query_stem,
            # outfile=outfile,
            debug = True)
        ami_corpus.make_infiles(maxfiles=MAXFILES)
        xpath = None
        path = Path(Resources.TEST_RESOURCES_DIR,
                    "wordlists", "carbon_cycle_noabb.txt")
        phrases = FileLib.read_strings_from_path(path)
        logger.debug(f"phrases {len(phrases)}")
        ami_query = ami_corpus.get_or_create_corpus_query(
            query_id=query_stem, phrases=phrases)
        ami_corpus.search_files_with_phrases(ami_query.phrases)
        assert ami_corpus.search_html is not None
        term_id_by_url = CorpusQuery.extract_hits_by_url_from_nested_lists(ami_corpus.search_html)
        assert term_id_by_url is not None
        assert len(term_id_by_url.keys()) > 0
        logger.debug(f"term_id_by_url keys {len(term_id_by_url.keys())}")
        term_ref_p_tuple_list = CorpusQuery.get_hits_as_term_ref_p_tuple_list(term_id_by_url)
        htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
        CorpusQuery._add_hits_to_table(tbody, term_ref_p_tuple_list)

        trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"{query_stem}_hits.html")
        HtmlLib.write_html_file(htmlx, trp_file, debug=True)
        assert trp_file.exists()

    def test_create_corpus_with_wordlist_and_search_with_query_LONG(self):
        """
        reads words from file and searches corpus giving term_oriented table
        uses CorpusQuery.
        Under development
        """
        indir = Path(Resources.TEST_RESOURCES_DIR, 'ipcc')
        main_key = "corpus"
        main_out_dir = Path(Resources.TEMP_DIR, main_key)
        outfile = Path(main_out_dir, f"out.html")
        MAXFILES = 5 # to limit test time
        MAXFILES = 1  # Reduced from 2 for faster testing

        ami_corpus = AmiCorpus(
            indir=indir,
            globstr=f"**/{HTML_WITH_IDS}.html",
            outfile=outfile,
            debug = True)
        files = ami_corpus.make_infiles(maxfiles=MAXFILES)
        logger.info(f"using {len(files)} files")

        # queries
        cc_id = self._carbon_cycle_query(ami_corpus, main_out_dir)
        crop_id = self._crop_query(ami_corpus, main_out_dir)

        logger.debug(f">>>>> {ami_corpus}")
        html_by_id_dict = ami_corpus.search_files_with_queries([
            cc_id,
            crop_id
        ])
        for (query_id, html) in html_by_id_dict.items():
            trp_file = Path(Resources.TEMP_DIR,
                            "ipcc", "cleaned_content", f"xx_{query_id}_hits.html")
            HtmlLib.write_html_file(html_by_id_dict.get(query_id), trp_file, debug=True)
            assert trp_file.exists()

        print(">==================")

    def _crop_query(self, ami_corpus, main_out_dir):
        crop_id = "crops"
        crop_out = Path(main_out_dir, f"{crop_id}_out.html")
        crop_phrases = [
            "maize",
            "millet",
            "rice",
            "wheat"
        ]
        crop_query = ami_corpus.get_or_create_corpus_query(
            query_id=crop_id,
            phrases=crop_phrases,
            outfile=crop_out)
        return crop_id

    def _carbon_cycle_query(cls, ami_corpus, main_out_dir):
        cc_id = "carbon_cycle"
        cc_wordfile = Path(Resources.TEST_RESOURCES_DIR, "wordlists", "carbon_cycle_noabb.txt")
        cc_out = Path(main_out_dir, f"{cc_id}_out.html")
        cc_query = ami_corpus.get_or_create_corpus_query(
            query_id=cc_id,
            phrasefile=cc_wordfile,
            outfile=cc_out)
        print("===================")
        return cc_id

    # def _add_hits_to_table(self, tbody, term_ref_p_tuple_list):
    #     if term_ref_p_tuple_list is None:
    #         logger.error(f"term_ref_p_tuple_list is None")
    #         return
    #     for term, ref, p in term_ref_p_tuple_list:
    #         assert type(term) is str
    #         assert type(ref) is str
    #         assert type(p) is _Element or type(p) is HtmlElement
    #         tr = ET.SubElement(tbody, "tr")
    #         tds = []
    #         for item in term, ref, p:
    #             tds.append(ET.SubElement(tr, "td"))
    #         tds[0].text = term
    #         a = ET.SubElement(tds[1], "a")
    #         a.attrib["href"] = ref
    #         a.text = ref
    #
    #         tds[2].append(p)
    #
    # def get_hits_as_term_ref_p_tuple_list(self, term_id_by_url):
    #     if term_id_by_url is None:
    #         logger.error(f"term_id_by_url is None")
    #         return None
    #     trp_list = []
    #     for ref in term_id_by_url.keys():
    #         bits = ref.split("#")
    #         file = bits[0]
    #         idref = bits[1]
    #         term_p = term_id_by_url.get(ref)
    #         term = term_p[0]
    #         p = term_p[1]
    #         # logger.debug(f"{term}:{idref} => {''.join(p.itertext())}")
    #         tuple = (term, ref, p)
    #         trp_list.append(tuple)
    #
    #     return trp_list
    #
    # ================ NYI ===============


    def test_make_toc_and_make_normalized_html(self):
        """
        take html_with_ids and
          - make TOC
          - remove styles

        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter05", "html_with_ids.html")
        outfile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", "wg1", "Chapter05", "normalized.html")
        assert infile.exists()
        # read file into XML object
        root_element = HtmlLib.parse_html(infile)
        assert root_element is not None
        head = root_element.xpath("./head")[0]
        style_elements = head.xpath("./style")
        assert len(style_elements) > 10
        XmlLib.remove_elements(head, "./style")
        style = ET.SubElement(head, "style")
        style.text = "img {width:10%;border:solid gray 1px;}"
        style = ET.SubElement(head, "style")
        style.text = "img[class='_idGenObjectAttribute-1'] {width:50%;border:solid green 2px;}"
        body = root_element.xpath("./body")[0]

        # find list of images before main text and reduce their scale
        chap_butt_content = body.xpath(".//div[@id='chapter-button-content']")[0]
        assert chap_butt_content is not None
        self.shrink_images(chap_butt_content)

        # make TableOfContents (ToC)
        h1_list = body.xpath(".//div[@class='h1-container']")
        assert len(h1_list) > 0

        body_header = body.xpath("./div/header")[0]
        toc_ul = ET.SubElement(body_header, "ul")
        EXECUTIVE = "Executive"
        FAQ = "frequently-asked-questions"
        REFERENCES = "references"
        id_values = [
            EXECUTIVE,
            FAQ,
            REFERENCES,
        ]
        subchapter_regex = "\\d+\\.\\d+"
        for h1_elem in h1_list:
            id = h1_elem.attrib["id"]
            if id in id_values:
                if id == EXECUTIVE:
                    analyze_exec()
                if id == FAQ:
                    analyze_faq()
                if id == REFERENCES:
                    analyze_references()
                # known ID
                pass
            elif re.match(subchapter_regex, id):
                self.sub_element_title(id, toc_ul, ["h1", "h2"])

                pass
            else:
                logger.error(f"unknown subchapter {id}")



        HtmlLib.write_html_file(root_element, outfile, debug=True)

        # NYI

    def sub_element_title(self, id, toc_ul, h_list):

        sub_elem = XmlLib.get_single_element(toc_ul, f"//*[@id='{id}']")
        if sub_elem is None:
            return
        logger.debug(f"sub_elem {sub_elem.attrib}")
        if len(h_list) == 0:
            return
        sub_h = h_list[0]
        h_elem = sub_elem.xpath(f"./{sub_h}")[0]
        h_text = "".join(h_elem.itertext())
        text = " ".join(sub_elem.itertext())
        toc_li = ET.SubElement(toc_ul, "li")
        toc_li.attrib["title"] = f"sect {id}"
        a = ET.SubElement(toc_li, "a")
        a.attrib["title"] = text[:200]
        a.text = h_text
        a.attrib["href"] = f"#{id}"

        h_list = h_list[1:]
        if len(h_list) == 0:
            logger.debug("finished h-hierarchy")
            return

        h_level = h_list[0]
        xp = f"./div[@class='{h_level}-container']"
        logger.debug(f"xp: {xp}")
        sub_elems = sub_elem.xpath(xp)
        for sub_elem in sub_elems:
            sub_id = sub_elem.attrib['id']
            logger.debug(f"sub id {sub_id}")
            self.sub_element_title(sub_id, sub_elem, h_list[1:])

    def shrink_images(self, chap_butt_content):
        img_list = chap_butt_content.xpath(".//img")
        assert len(img_list) > 0
        """
        <div class="col-lg-3 col-12">
          <h3>Figure 5.5</h3>
          <img src="https://www.ipcc.ch/report/ar6/wg1/downloads/figures/IPCC_AR6_WGI_Figure_5_5.png" alt="" class="img-card" width="10%">
        </div>
        """
        for img in img_list:
            img.attrib["width"] = "10%"
            h3 = img.getparent().xpath("./h3")[0]
            caption = "".join(h3.itertext()).strip().lower()
            img.attrib["alt"] = caption
            a_text = caption
            for punct in [" ", "."]:
                caption = caption.replace(punct, "-")
            caption = caption.replace(",", "")
            h3.text = ""
            a = ET.SubElement(h3, "a")
            a.attrib["href"] = f"#{caption}"
            a.text = a_text

    def test_read_eupmc_json_create_write_datatables_html(self):
        """
        Reads a eupmc_results.json and creates and write an HTML datatables.html
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "pygetpapers", "wildlife", "eupmc_results.json")
        assert infile.exists()
        outfile = Path(Resources. TEMP_DIR, "pygetpapers", "wildlife", "datatables.html")
        AmiCorpus.read_json_create_write_html_table(infile, outfile,
                                wanted_keys=["doi", "fullTextIdList", "title"])

    def test_read_single_openalex_json(self):
        """
        Reads an openalex metadata file and creates and writes an HTML datatables.html
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "openalex", "openalex-result.json")
        logger.info(f"infile {infile}")
        assert infile.exists()
        outfile = Path(Resources.TEMP_DIR, "openalex", "openalex-datatable.html")
        dikt = OpenAlexTest.read_json_create_write_html_table(infile, outfile, wanted_keys=["doi", "title"])
        assert dikt is not None
        assert "doi" in dikt.keys()

    def test_read_total_openalex_json(self):
        """
        Reads an openalex metadata file and creates and writes an HTML datatables.html
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "openalex", "openalex-results.json")
        logger.info(f"infile {infile}")
        assert infile.exists()
        outfile = Path(Resources.TEMP_DIR, "openalex", "openalex-datatable.html")
        dikt = OpenAlexTest.read_json_create_write_html_table(infile, outfile, wanted_keys=["doi", "title"])
        assert dikt is not None
        assert "total_json_output" in dikt.keys(), f"keys {dikt.keys()}"

        # assert outfile.exists(), f"{outfile} should have been created"

    @unittest.skip("Test requires specific pygetpapers test data that doesn't exist")
    def test_read_single_open_alex_files(self):
        """
        iterate over a directory and try to read all open alex metadata
        only works for PMR

        """
        indir = Path(Path(Resources.TEST_RESOURCES_DIR).parent.parent.parent, "pygetpapers")
        assert indir.exists(), f"{indir} should exist"
        pygetpapers_test = Path(indir, "invasive_plant_species_test" )
        assert pygetpapers_test.exists(), f"{pygetpapers_test} should exist"
        dirs = pygetpapers_test.iterdir()
        for dir in dirs:
            openalex = Path(dir, "openalex-result.json")
            if not openalex.exists():
                logger.error(f"no {openalex}")
            else:
                with open(openalex, "r") as f:
                    pydict = json.loads(f.read())
                    logger.info(f"{pydict.keys()}")



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



class JATSTest(AmiAnyTest):

    """
    EuropePMC output is JATS
    """
    def test_read_pmc_sections(self):
        pass
        amoc_dir = Path(Resources.TEST_RESOURCES_DIR, "jats", "amoc")
        assert amoc_dir.exists()
        pmcdirs = glob.glob(str(Path(amoc_dir, "./PMC*")))
        assert len(pmcdirs) == 50
        for pmcdir in pmcdirs:
            path = Path(pmcdir, "fulltext.xml")
            try:
                xml = XmlLib.parse_xml_file_to_root(path)
            except XMLSyntaxError as xmle:
                logger.error(f"cannot parse {path}; error {xmle}")
                continue
            jats_doc = JATSDoc(xml)
            secs, non_secs = jats_doc.get_body_secs_non_secs()
            sec_xpath = f"./@{JATSDoc.SEC_TYPE}"
            non_sec_xpath = f"local-name()"
            if secs is not None:
                sectype_list = [XmlLib.get_single_element(s, sec_xpath) for s in secs]
                JATSDoc.get_titles_and_ids(secs)
                try:
                    non_sec_list = [ns.tag for ns in non_secs]
                except Exception as e:
                    logger.error(f"error {e} non_sec {non_sec_xpath}")
                    continue
                logger.info(f"secs {len(secs)} {sectype_list} ; "
                            f"non_secs {len(non_secs)} {non_sec_list}")
            else:
                logger.warn(f"no secs")







