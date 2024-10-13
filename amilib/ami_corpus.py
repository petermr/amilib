"""
downstream parser for pygetpapers
"""
import datetime
import json
from collections import defaultdict
from pathlib import Path

import lxml
import lxml.etree as ET
from lxml.html import HTMLParser

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

    def __init__(self, indir=None, mkdir=False):
        """

        """
        self.source_dir = indir
        if mkdir and self.source_dir:
            if not Path(self.source_dir).is_dir():
                Path(self.source_dir).mkdir()

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
            if not Path(self.source_dir).is_dir():
                logger.error(f"not a directory {self.source_dir}")
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

        if indir is None:
            logger.warning("No indir")
            return
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

    @classmethod
    def create_hit_html(cls, infiles, phrases=None, outfile=None, xpath=None, debug=False):
        all_paras = []
        all_dict = dict()
        hit_dict = defaultdict(list)
        if type(phrases) is not list:
            phrases = [phrases]
        for infile in infiles:
            assert Path(infile).exists(), f"{infile} does not exist"
            html_tree = lxml.etree.parse(str(infile), HTMLParser())
            paras = HtmlLib.find_paras_with_ids(html_tree, xpath=xpath)
            all_paras.extend(paras)

            # this does the search
            para_id_by_phrase_dict = HtmlLib.create_para_ohrase_dict(paras, phrases)
            if len(para_id_by_phrase_dict) > 0:
                if debug:
                    print(f"para_phrase_dict {para_id_by_phrase_dict}")
                cls.add_hit_with_filename_and_para_id(all_dict, hit_dict, infile, para_id_by_phrase_dict)
        if debug:
            print(f"para count~: {len(all_paras)}")
        outfile = Path(outfile)
        outfile.parent.mkdir(exist_ok=True, parents=True)
        html1 = cls.create_html_from_hit_dict(hit_dict)
        if outfile:
            with open(outfile, "w") as f:
                if debug:
                    print(f" hitdict {hit_dict}")
                HtmlLib.write_html_file(html1, outfile, debug=True)
        return html1

    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_dict, hit_dict, infile, phrase_by_para_id_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_dict: accumulates para_phrase_dict by infile

        TODO - move to amilib
        """
        item_paras = [item for item in phrase_by_para_id_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_dict[infile] = phrase_by_para_id_dict
            for para_id, hits in phrase_by_para_id_dict.items():
                for hit in hits:
                    # TODO should write file with slashes (on Windows we get %5C)
                    infile_s = f"{infile}"
                    infile_s = infile_s.replace("\\", "/")
                    infile_s = infile_s.replace("%5C", "/")
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)


    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_dict, hit_dict, infile, para_phrase_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_dict: accumulates para_phrase_dict by infile

        TODO - move to amilib
        """
        item_paras = [item for item in para_phrase_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_dict[infile] = para_phrase_dict
            for para_id, hits in para_phrase_dict.items():
                for hit in hits:
                    # TODO should write file with slashes (on Windows we get %5C)
                    infile_s = f"{infile}"
                    infile_s = infile_s.replace("\\", "/")
                    infile_s = infile_s.replace("%5C", "/")
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)

    @classmethod
    def create_html_from_hit_dict(cls, hit_dict):
        html = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html)
        ul = ET.SubElement(body, "ul")
        for term, hits in hit_dict.items():
            li = ET.SubElement(ul, "li")
            p = ET.SubElement(li, "p")
            p.text = term
            ul1 = ET.SubElement(li, "ul")
            for hit in hits:
                # TODO manage hits with Paths
                # on windows some hits have "%5C' instead of "/"
                hit = str(hit).replace("%5C", "/")
                li1 = ET.SubElement(ul1, "li")
                a = ET.SubElement(li1, "a")
                a.text = hit.replace("/html_with_ids.html", "")
                ss = "ipcc/"
                try:
                    idx = a.text.index(ss)
                except Exception as e:
                    print(f"cannot find substring {ss} in {a}")
                    continue
                a.text = a.text[idx + len(ss):]
                a.attrib["href"] = hit
        return html

    def create_corpus_container(self, container_dir, mkdir=False, type="unknown"):
        """
        create container as child of self
        :param container_dir: new container
        """
        if container_dir is not None:
            container = AmiCorpusContainer(self, container_dir)
            # logger.debug(f"container_dir: {container_dir}")
            path = Path(container_dir)
            if not path.exists():
                path.mkdir()
            # logger.debug(f"container exists {path}")
            return container

# class AmiCorpusText:
#     """
#     holds a single work, report, book, scholarly article, etc.
#     probably standalone.
#     based on hierarchical directories initially (this may change)
#     corpus
#         corpus_texts
#             chapters
#     Contained within an AmiCorpus and may/may_not contain chapters, sections and may other document
#     components
#     """
#
#     def __init__(self, source_dir):
#         self.source_dir = source_dir
#         self.chapter_list = []
#
#     def create_chapter(self, source_dir, title=None, mkdir=False):
#         """
#         create a chapter (maybe child dir of corpus text)
#         """
#         if source_dir.parent != self:
#             logger.error(f"cannot add child {source_dir}")
#             return None
#         chapter = AmiChapter(source_dir, mkdir=mkdir)
#         self.chapter_list.append(chapter)
#
class AmiCorpusContainer:
    def __init__(self, parent_container, dir_name, type="unknown", mkdir=False, exist_ok=True):
        """
        create corpusContainer with parent and child dir name
        :param parent_container:
        :param dir_name: name relative to self.source_dir
        """
        if not parent_container or not dir_name:
            logger.error(f"None arbguments")
            return None
        self.parent_container = parent_container
        self.source_dir = Path(parent_container.source_dir, dir_name)
        if mkdir and self.source_dir:
            Path(self.source_dir).mkdir(exist_ok=exist_ok)
        self.type = type
        self.child_container_list = []
        self.child_document_list = []

    def create_corpus_container(self, filename, type="unknown", mkdir=False):
        """
        creates a child container and optionally its actual directory
        """
        if not filename :
            logger.error("filename is None")
            return None
        path = Path(self.source_dir, filename)
        if not path.exists():
            if mkdir:
                path.mkdir()
        else:
            if not path.is_dir():
                logger.error(f"{path} exists but is not a directory")
                return None
        corpus_container = AmiCorpusContainer(self, path, type=type, mkdir=mkdir)
        self.child_container_list.append(corpus_container)
        return corpus_container

    def create_document(self, name, text=None, type="unknown"):
        """
        creates document file with name and self as parent
        """
        document_file = Path(self.source_dir, name)
        # logger.debug(f"created {document_file}")
        document_file.touch()
        if text:
            with open(document_file, "w") as f:
                f.write(text)

        self.child_document_list.append(document_file)
        return document_file




