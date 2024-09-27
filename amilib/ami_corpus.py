"""
downstream parser for pygetpapers
"""
import datetime
import json
from pathlib import Path
import lxml.etree as ET

# from amilib.ami_bib import SAVED, QUERY, STARTDATE, ENDDATE
from amilib.ami_html import HtmlLib, HtmlUtil
from amilib.ami_util import AmiJson, AmiUtil
# from amilib.ami_bib import DOI, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT, SAVED_CONFIG_INI, Pygetpapers
from amilib.util import Util

EUPMC_RESULTS_JSON = "eupmc_results.json"
DATATABLES_HTML = "datatables.html"
SAVED_CONFIG_INI = "saved_config.ini"  # TODO cyclic import

logger = Util.get_logger(__name__)


class AmiCorpus():
    """

    """
    EUPMC_TRANSFORM = {
        "doi": {
            "url": {
                "prefix": "https://www.doi.org/",
            }
        },
        "authorString": {
            "text": {
                "split": ",",
            }
        },
        "abstractText": {
            "text": {
                "truncate": 200,
            }
        },
        "pmcid": {
            "url": {
                "prefix": "https://europepmc.org/betaSearch?query=",
            }

        }

    }

    def __init__(self, indir=None):
        """

        """
        self.indir = indir
        self.eupmc_results = None

    def get_datatables(self):
        """
        create a JQuery datatables from eumpc_reults.json
        """
        self.get_or_create_eupmc_results()
        if self.eupmc_results is None:
            logger.error(f"no {EUPMC_RESULTS_JSON}, so cannot create datatables at present")
            return

    def get_or_create_eupmc_results(self):
        f"""
        gets file {EUPMC_RESULTS_JSON} from directory
        :return: {EUPMC_RESULTS_JSON} from directory or None if not exists
        """
        if self.eumpc_results is None:
            if not Path(self.indir).is_dir():
                logger.error(f"not a directory {self.indir}")
                return None
            self.eupmc_results = Path(self.eupmc_results, EUPMC_RESULTS_JSON)
            if not self.eupmc_results.exists():
                self.eupmc_results = None
        return self.eupmc_results

    @classmethod
    def make_datatables(cls, indir, outdir=None, outfile_h=None):
        """
        creates a JQuery.datatables (HTML) file from an AmiCorpus
        May make this method a member function later
        :param indir: directory with corpus (normally created by pygetpapers)
        :param outdir: output for datatables (if omitted uses indir)
        :param outfile_h: the HTML file ceated (may be changed)
        """
        from amilib.ami_bib import SAVED_CONFIG_INI

        if outdir is None:
            outdir = indir
        if outfile_h is None:
            outfile_h = Path(outdir, DATATABLES_HTML)
        # wanted_keys = [PMCID, DOI, TITLE, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT]
        config_ini = Path(indir, SAVED_CONFIG_INI)
        infile = Path(indir, EUPMC_RESULTS_JSON)
        outdir.mkdir(parents=True, exist_ok=True)
        datatables = True
        AmiCorpus.read_json_create_write_html_table(
            infile, outfile_h, wanted_keys=None, datatables=datatables, table_id=None, config_ini=config_ini)

    @classmethod
    def read_json_create_write_html_table(
            cls, infile, outfile_h, wanted_keys,
            styles=None, datatables=None, table_id=None, config_ini=None):
        """
        read pygetpapers output, select columns and create HTML table
        :param infile: eumpc_results from pygetpapers
        :param outfile_h: HTML table to write
        :param wanted_keys: column headings to select
        :param styles: datatables styles
        :param datatables: datatables
        :param table_id: id links script to table (default "my_table")
        :param config_ini: adds info from saved_config.ini - mainly the query
        :return: html table
        """
        # TODO cyclic imports
        from amilib.ami_bib import PMCID, TITLE
        from amilib.ami_bib import DOI, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT
        if styles is None:
            styles = ["td {border:solid 1px black;}"]
        if table_id is None:
            table_id = "my_table"
        if wanted_keys is None:
            wanted_keys = [PMCID, DOI, TITLE, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT]

        assert infile.exists(), f"infile {infile} must exist"
        with open(infile, "r") as f:
            jsonx = json.load(f)
        # look for all papers
        papers = jsonx.get("papers")
        assert papers is not None, f"cannot find papers"
        # specific keys we want
        dict_by_id = AmiJson.create_json_table(papers, wanted_keys)
        htmlx, table = HtmlLib.create_html_table(
            dict_by_id, transform_dict=AmiCorpus.EUPMC_TRANSFORM,
            styles=styles, datatables=datatables, table_id=table_id
        )
        cls.add_query_as_caption(config_ini, table)

        HtmlUtil.write_html_elem(htmlx, outfile_h, debug=True)

    @classmethod
    def add_query_as_caption(cls, config_ini, table):
        """
        add query string from config.ini to table caption
        :param config_ini: saved_config.ini file
        :param table: to add caption to
        """
        from amilib.ami_bib import SAVED, QUERY, STARTDATE, ENDDATE
        if config_ini is not None:
            config, _ = AmiUtil.get_config_and_section_names(config_ini)
            saved_section = config[SAVED]
            query = saved_section[QUERY]
            startdate = saved_section[STARTDATE]
            if startdate == 'False':
                startdate = "..."
            enddate = saved_section[ENDDATE]
            if enddate == 'False':
                enddate = datetime.date.today()

            caption = ET.SubElement(table, "caption")
            caption.text = f"query: {query}"
            if startdate:
                caption.text += f"; start: {startdate}"
            if enddate:
                caption.text += f"; end: {enddate}"
