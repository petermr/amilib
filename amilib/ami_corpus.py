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
from amilib.ami_html import HtmlLib, HtmlUtil, Datatables
from amilib.ami_util import AmiJson, AmiUtil
from amilib.file_lib import FileLib
# from amilib.ami_bib import DOI, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT, SAVED_CONFIG_INI, Pygetpapers
from amilib.util import Util

EUPMC_RESULTS_JSON = "eupmc_results.json"
DATATABLES_HTML = "datatables.html"
SAVED_CONFIG_INI = "saved_config.ini"  # TODO cyclic import

logger = Util.get_logger(__name__)


class AmiCorpus():
    """
    supports a tree of directories and leaf documents with wrappers AmiCorpus
    (top dir) and AmiCorpusCompnents (subdirectories)

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

    def __init__(self,
                 topdir=None,
                 infiles=None,
                 globstr=None,
                 outfile=None,
                 query=None,
                 make_descendants=False,
                 mkdir=False,
                 **kwargs):
        """
        create new Corpus, withn optional input of data
        :param topdir: Input directory with files/subdis as possible corpus components
        :param infiles: list of files to use (alternative to globstr)
        :param globstr: create infiles using globbing under topdir (requires topdir)
        :param outfile:
        :param mkdir: make topdir if doesn't exist (default=False)
        :param make_descendants: makes AmiCorpusContianers for directories on tree
        :param kwargs: dict of per-corpus user-specified properties

        """
        self.topdir = topdir
        if self.topdir and not self.topdir.is_dir():
            raise ValueError(f"AmiCorpus() requires valid directory {self.topdir}")

        self.container_by_file = dict()
        # rootnode
        self.ami_container = self.create_corpus_container(
            self.topdir, make_descendants=make_descendants, mkdir=mkdir)
        self.eupmc_results = None
        self.infiles = infiles
        self.outfile = outfile
        self.globstr = globstr
        self.search_html = None
        self._make_infiles()
        self._make_outfile()

        self.make_special(kwargs)

    def _make_infiles(self):
        if self.infiles:
            logger.info(f"taking infiles from list")
        else:
            if self.topdir and self.globstr:
                self.infiles = FileLib.posix_glob(f"{self.topdir}/{self.globstr}", recursive=True)
        if self.infiles is None:
            logger.error(f"self.infiles is None")
            return
        logger.info(f"inputting {len(self.infiles)} files")
        return self.infiles

    def create_corpus_container(self, file, bib_type="None", make_descendants=False, mkdir=False):
        """
        create container as child of self
        :param file: file or dir contained by container

        """
        if file is None:
            logger.error("Container has no file")
            return None

        container = AmiCorpusContainer(self, file)
        container.bib_type = bib_type
        if not file.exists() and mkdir:
            Path(file).mkdir()
        if make_descendants:
            self.make_descendants(file)
        return container

    @property
    def root_dir(self):
        return self.ami_container.file

    def make_descendants(self, file=None):
        """
        creates AmiCorpusContainers for directory tree
        :param ami_corpus: top-level corpus or None
        :param parent_dir: top-level directory of corpus
        :param source_dir: each directory in tree
        :return; None
        """
        if file is None:
            file = self.root_dir
        if file is None or not file.is_dir():
            logger.error(f"Cannot make file children for {file}")
            return
        files = FileLib.get_children(file)
        for f in files:
            container = AmiCorpusContainer(self, f)
            container.make_descendants()

    def make_special(self, kwargs):
        """Horrible - us dependency injectiom
        """
        if "eupmc" in kwargs:
            self.eupmc_results = kwargs["eupmc"]
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
    def search_files_with_phrases_write_results(cls, infiles, phrases=None, para_xpath=None, outfile=None, debug=False):
        all_hits_dict = dict()
        url_list_by_phrase_dict = defaultdict(list)
        if type(phrases) is not list:
            phrases = [phrases]
        all_paras = []
        for infile in infiles:
            assert Path(infile).exists(), f"{infile} does not exist"
            html_tree = lxml.etree.parse(str(infile), HTMLParser())
            paras = HtmlLib.find_paras_with_ids(html_tree, para_xpath=para_xpath)
            all_paras.extend(paras)


            # this does the search
            para_id_by_phrase_dict = HtmlLib.create_search_results_para_ohrase_dict(paras, phrases)
            if len(para_id_by_phrase_dict) > 0:
                if debug:
                    # logger.debug(f"para_phrase_dict {para_id_by_phrase_dict}")
                    pass
                cls.add_hit_with_filename_and_para_id(all_hits_dict, url_list_by_phrase_dict, infile, para_id_by_phrase_dict)
        if debug:
            print(f"para count~: {len(all_paras)}")
        html1 = cls.create_html_from_hit_dict(url_list_by_phrase_dict)
        assert html1 is not None
        if outfile:
            outfile = Path(outfile)
            outfile.parent.mkdir(exist_ok=True, parents=True)
            with open(outfile, "w") as f:
                if debug:
                    print(f" hitdict {url_list_by_phrase_dict}")
                HtmlLib.write_html_file(html1, outfile, debug=True)
        return html1

    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_hits_dict, hit_dict, infile, phrase_by_para_id_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_hits_dict: accumulates para_phrase_dict by infile
        :param hit_dict: accumulates url by hit (

        """
        item_paras = [item for item in phrase_by_para_id_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_hits_dict[infile] = phrase_by_para_id_dict
            for para_id, hits in phrase_by_para_id_dict.items():
                for hit in hits:
                    # TODO should write file with slashes (on Windows we get %5C)
                    infile_s = f"{infile}"
                    infile_s = infile_s.replace("\\", "/")
                    infile_s = infile_s.replace("%5C", "/")
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)
                    logger.info(f"hit: {hit} in url {url}")


    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_dict, hit_dict, infile, para_phrase_dict):
        """adds non-empty hits in hit_dict and all to all_dict
        :param all_dict: accumulates para_phrase_dict by infile

        TODO - move to amilib
        """
        infile_s = f"{infile}"
        infile_s = infile_s.replace("\\", "/")
        infile_s = infile_s.replace("%5C", "/")

        item_paras = [item for item in para_phrase_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_dict[infile] = para_phrase_dict
            for term, para_id in para_phrase_dict.items():
                # TODO should write file with slashes (on Windows we get %5C)
                url = f"{infile_s}#{para_id}"
                hit_dict[term].append(url)

    @classmethod
    def create_html_from_hit_dict(cls, hit_dict):
        html = HtmlLib.create_html_with_empty_head_body()
        body = HtmlLib.get_body(html)
        ul = ET.SubElement(body, "ul")
        for term, hits in hit_dict.items():
            li = ET.SubElement(ul, "li")
            p = ET.SubElement(li, "p")
            p.text = f"term: {term}"
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


    @classmethod
    def add_content_for_files(cls, files, tr):
        if files:
            HtmlLib.add_cell_content(tr, text=Path(files[0]).stem, href=f"file://{files[0]}")
        else:
            HtmlLib.add_cell_content(tr, text="?")

    def list_files(self, globstr):
        """
        finds files in corpus starting at root_dir
        :param globstr:
        """
        if globstr and self.root_dir:
            return FileLib.list_files(self.root_dir, globstr=globstr)
        return []

    def create_datatables_html_with_filenames(self, html_glob, labels, table_id, outpath=None, debug=True):
        """
        :param html_glob: globstring to find html files
        :labels
        """
        html_files = sorted(self.list_files(globstr=html_glob))
        self.datables_html, tbody = Datatables._create_html_for_datatables(labels, table_id)

        for html_file in html_files:
            if outpath:
                offset = FileLib.get_reletive_path(html_file, outpath.parent, walk_up=True)
            tr = ET.SubElement(tbody, "tr")
            HtmlLib.add_cell_content(tr, text=offset, href=f"{offset}")
        HtmlLib.write_html_file(self.datables_html, outpath, debug=debug)

        return self.datables_html

    def make_infiles(self):
        self.infiles = FileLib.posix_glob(self.globstr, recursive=True)

    def make_globstr(self):
        pass

    def _make_outfile(self):
        if not self.outfile:
        #     if self.query:
            pass

    def search_files_with_phrases(self, phrases, debug=False):
        self.search_html = AmiCorpus.search_files_with_phrases_write_results(
            self.infiles, phrases=phrases, outfile=self.outfile, debug=debug)



class AmiCorpusContainer:
    def __init__(self, ami_corpus, file, bib_type="unknown", mkdir=False, exist_ok=True):
        """
        create corpusContainer for directory-structured corpus
        :param ami_corpus: corpus to which this belonds
        :param file_node: file/dir on filesystem
        :param bib_type: type of container (e.g. report
        """
        if (t := type(ami_corpus)) is not AmiCorpus:
            raise ValueError(f"ami_corpus has wrong type {t}")
        self.ami_corpus = ami_corpus
        self.file = file
        self.ami_corpus.container_by_file[self.file] = self
        if not file:
            logger.error(f"No file_node argument")
            return None
        # if mkdir and self.source_dir:
        #     Path(self.source_dir).mkdir(exist_ok=exist_ok)
        self.bib_type = bib_type
        self.child_container_list = []
        self.child_document_list = []

    @property
    def child_containers(self):
        child_containers = []
        if self.ami_corpus and self.ami_corpus.source_dir:
            child_nodes = FileLib.get_children()
            for child_node in child_nodes:
                child_container = AmiCorpusContainer(self.ami_corpus, child_node)
                child_container.type = "" if Path(child_node).is_dir() else "file"
                child_containers.append(child_container)
        return child_containers

    def create_corpus_container(self, filename, bib_type="unknown", make_descendants=False, mkdir=False):
        """
        creates a child container and optionally its actual directory
        """
        if not filename :
            logger.error("filename is None")
            return None
        path = Path(self.file, filename)
        if mkdir and not path.exists():
            path.mkdir()
        else:
            if not path.is_dir():
                logger.error(f"{path} exists but is not a directory")
                return None
        corpus_container = AmiCorpusContainer(self.ami_corpus, path, bib_type=bib_type, mkdir=mkdir)
        self.child_container_list.append(corpus_container)
        return corpus_container

    def create_document(self, filename, text=None, type="unknown"):
        """
        creates document file with name and self as parent
        """
        document_file = Path(self.file, filename)
        document_file.touch()
        if text:
            with open(document_file, "w") as f:
                f.write(text)

        self.child_document_list.append(document_file)
        return document_file

    def make_descendants(self):
        if (self.file and self.file.is_dir()):
            self.ami_corpus.make_descendants(self.file)

# to create a hierarchical structure for your Corpus element in Python, you'll need to define a few classes that represent the Corpus, Container, and their relationships. Here's a simple implementation that achieves this:
#
# python
# Copy code
class Container:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def __repr__(self):
        return f"Container({self.name}, children={len(self.children)})"


class Corpus(Container):
    def __init__(self, directory):
        super().__init__(directory)
        # Assume directory is the top-level directory wrapped by this Corpus
        self.directory = directory

    def __repr__(self):
        return f"Corpus({self.directory})"


# Example Usage
if __name__ == "__main__":
    # Create a Corpus for the top directory
    root_corpus = Corpus("root_directory")

    # Create Containers for subdirectories/files
    sub_container1 = Container("sub_directory1")
    sub_container2 = Container("sub_directory2")

    # Add containers as children to the root corpus
    root_corpus.add_child(sub_container1)
    root_corpus.add_child(sub_container2)

    # You can further add children to the sub_containers
    file1 = Container("file1.txt")
    sub_container1.add_child(file1)

    # Display the structure
    print(root_corpus)
    for child in root_corpus.children:
        print(f"  - {child}")
        for grandchild in child.children:
            print(f"    - {grandchild}")
# Explanation
# Container Class:
#
# Holds a name, a list of children, and a reference to its parent.
# The add_child method adds a child and sets its parent to the current container.
# Corpus Class:
#
# Inherits from Container and represents the top-level directory (or corpus).
# It takes a directory name during initialization.
# Example Usage:
#
# Creates a Corpus for the top directory.
# Adds child Container elements (subdirectories or files).
# Prints the structure of the corpus, including its children.
# Usage
# You can expand this structure by adding methods for traversing, searching,
# or manipulating the corpus as needed.
# Each Container instance can easily access its parent and children,
# allowing you to manage the hierarchical structure effectively.




