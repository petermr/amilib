"""
downstream parser for pygetpapers
"""
import datetime
import json
from collections import defaultdict
from pathlib import Path

import lxml
import lxml.etree as ET
from lxml.etree import _Element
from lxml.html import HTMLParser, HtmlElement

from amilib.ami_bib import EUPMC_RESULTS_JSON, EUPMC_TRANSFORM
# from amilib.ami_bib import SAVED, QUERY, STARTDATE, ENDDATE
from amilib.ami_html import HtmlLib, HtmlUtil, Datatables
from amilib.ami_util import AmiJson, AmiUtil
from amilib.file_lib import FileLib
# from amilib.ami_bib import DOI, AUTHOR_STRING, JOURNAL_INFO_TITLE, PUB_YEAR, ABS_TEXT, SAVED_CONFIG_INI, Pygetpapers
from amilib.util import Util, TextUtil
from test.resources import Resources

DATATABLES_HTML = "datatables.html"
SAVED_CONFIG_INI = "saved_config.ini"  # TODO cyclic import
HTML_WITH_IDS = "html_with_ids"

logger = Util.get_logger(__name__)







class AmiCorpus():
    """
    supports a tree of directories and leaf documents with wrappers AmiCorpus
    (top dir) and AmiCorpusCompnents (subdirectories)

    """

    def __init__(self,
                 topdir=None,
                 infiles=None,
                 globstr=None,
                 outfile=None,
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
        self.infiles = infiles
        self.outfile = outfile
        self.globstr = globstr
        self.corpus_queries = dict()
        self.search_html = None
        self.eupmc_results = None
        self._make_infiles()
        self._make_outfile()

        self.make_special(kwargs)

    def __str__(self):
        values = []
        for key in self.corpus_queries.keys():
            value = self.corpus_queries.get(key)
            values.append(value)


            s = f"""AmiCorpus:
topdir:  {self.topdir}
globstr: {self.globstr}
infiles: {len(self.infiles)}
outfile: {self.outfile}
"""
            s += "QUERIES"
            for (key, value) in self.corpus_queries.items():
                s += f"""
                {key}:
                {value.__str__()}
                """
        return s

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
            dict_by_id, transform_dict=EUPMC_TRANSFORM,
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
        if phrases is None:
            logger.error("no phrases")
            return
        all_hits_dict = dict()
        url_list_by_phrase_dict = defaultdict(list)
        if (type(phrases) is not list):
            phrases = [phrases]
        all_paras = []
        for infile in infiles:
            assert Path(infile).exists(), f"{infile} does not exist"
            html_tree = lxml.etree.parse(str(infile), HTMLParser())
            paras = HtmlLib.find_paras_with_ids(html_tree, para_xpath=para_xpath)
            all_paras.extend(paras)


            # this does the search
            para_id_by_phrase_dict = HtmlLib.create_search_results_para_phrase_dict(paras, phrases)
            if para_id_by_phrase_dict is not None and len(para_id_by_phrase_dict) > 0:
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
        """
        This looks awful
        """
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
                a.text = hit.replace("/{HTML_WITH_IDS}.html", "")
                ss = "ipcc/"
                try:
                    idx = a.text.index(ss)
                except Exception as e:
                    print(f"cannot find substring {ss} in {a.text}")
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

    def search_files_with_phrases(self, debug=False):
        if self.phrases:
            self.search_html = AmiCorpus.search_files_with_phrases_write_results(
                self.infiles, phrases=self.phrases, outfile=self.outfile, debug=debug)

    def get_or_create_corpus_query(self,
                                   query_id,
                                   phrasefile=None,
                                   phrases=None,
                                   outfile=None):
        """
        retrieves query by query_stem. If not found creates new one
        :param query_id: unique id of query
        :param outfile: file to output results of search
        :return: query
        """
        corpus_query = self.corpus_queries.get(query_id)
        if not corpus_query:
            corpus_query = CorpusQuery(
                query_id=query_id,
                phrasefile=phrasefile,
                phrases=phrases,
                outfile=outfile)
            self.corpus_queries[query_id] = corpus_query
            corpus_query.corpus = self

        return corpus_query

    def search_files_with_queries(self, query_ids, debug=True):
        """
        run queries. Assumed that queries have been loaded and recallable by id
        :param query_ids: single or list of ids
        """
        if type(query_ids) is str:
            query_ids = [query_ids]
        elif (t :=type(query_ids)) is not list:
            raise ValueError(f"queries requires id/s as list or str, found {t}")
        for query_id in query_ids:
            query = self.corpus_queries.get(query_id)
            if query is None:
                logger.error(f"cannot find query: {query_id}")
                continue
            logger.debug(f"outfile==> {query.outfile}")
            self.search_html = AmiCorpus.search_files_with_phrases_write_results(
                self.infiles, phrases=query.phrases, outfile=query.outfile, debug=debug)

            term_id_by_url = CorpusQuery.make_hits_by_url(self.search_html)
            term_ref_p_tuple_list = CorpusQuery.get_hits_as_term_ref_p_tuple_list(term_id_by_url)
            htmlx, tbody = HtmlLib.make_skeleton_table(colheads=["term", "ref", "para"])
            CorpusQuery._add_hits_to_table(tbody, term_ref_p_tuple_list)

            trp_file = Path(Resources.TEMP_DIR, "ipcc", "cleaned_content", f"xx_{query_id}_hits.html")
            HtmlLib.write_html_file(htmlx, trp_file, debug=True)
            assert trp_file.exists()

            # AmiCorpus.search_files_with_phrases_write_results(self.infiles, phrases=query.phrases)

class CorpusQuery:
    """
    holds query and related info (hits, files)
    """
    def __init__(self,
                 query_id=None,
                 phrasefile=None,
                 phrases=None,
                 outfile=None,
                 ):
        self.query_id = query_id
        self.phrasefile = phrasefile
        self.phrases = phrases
        if self.phrasefile and not self.phrases:
            self.phrases = FileLib.read_strings_from_path(self.phrasefile)

        self.outfile = outfile
        self.corpus = None
        logger.debug(f"made query {self}")

    def __str__(self):
        s = f"""CorpusQuery
query_id:  {self.query_id}
phrasefile:{self.phrasefile}
phrases:   {None if not self.phrases else len(self.phrases) }
outfile:   {self.outfile}
corpus:    {None if self.corpus is None else self.corpus.__hash__() }
"""
        return s
    @classmethod
    def make_hits_by_url(cls, nested_list_html):
        """
        <body>
          <ul>
            <li>term: xyz
              <li><a href-to-para
        """
        # iterate over hit list
        if nested_list_html is None:
            logger.error(f"html1 is None")
            return None
        body = HtmlLib.get_body(nested_list_html)
        query_ul = HtmlLib.get_first_object_by_xpath(body, "ul")
        hits_by_url = dict()
        for li in query_ul.xpath("li"):
            # logger.debug("li")
            p0 = HtmlLib.get_first_object_by_xpath(li, "p")
            if p0 is None:
                continue
            term = p0.text
            txt = "term: "
            if (term.startswith(txt)):
                term = term[len(txt):]
            hits_ul = HtmlLib.get_first_object_by_xpath(li, "ul")
            if hits_ul is None:
                continue
            hits_li_list = hits_ul.xpath("li")
            # logger.debug(f"hits {len(hits_li_list)}")
            for hits_li in hits_li_list:
                # logger.debug(f"hits_li")
                cls.add_hit_list_to_hits_by_url(hits_by_url, hits_li, term)
                # logger.debug(f"added hits_li")

        return hits_by_url


    @classmethod
    def add_hit_list_to_hits_by_url(cls, hits_by_url, hits_li, term):
        if hits_by_url is None or hits_li is None or term is None:
            logger.error(f"add_hit_list None args ")
            return
        a = HtmlLib.get_first_object_by_xpath(hits_li, "a")
        if a is None:
            logger.error(f"a is None")
            return
        # logger.debug(f"a is {a}")
        href = a.attrib.get("href")
        if href is None:
            logger.error(f"href is None {ET.tostring(a)}")
            return
        # logger.debug(f"href {href}")
        href_target = href.split("#")[0]
        id = href.split("#")[1]
        # logger.debug(f"href_target {href_target}")
        html_targ = HtmlLib.parse_html(href_target)
        assert html_targ is not None
        if "[" in id:
            # logger.debug("quoted list")
            id_list = TextUtil.convert_quoted_list_to_list(id)
            for id1 in id_list:
                cls._get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id1, term)
        else:
            # logger.debug("non quoted list")
            cls._get_element_by_id_and_add_term_id_tuple_to_hits(hits_by_url, href_target, html_targ, id, term)
        # logger.debug("exit add hitlist")


    @classmethod
    def _get_element_by_id_and_add_term_id_tuple_to_hits(cls, hits_by_url, href_target, html_targ, id, term):
        if hits_by_url is None or href_target is None or html_targ is None or id is None or term is None:
            logger.error("arg is None")
            return None
        p = HtmlLib.get_element_by_id(html_targ, id)
        if p is not None:
            tuple = (term, p)
            target_id = f"{href_target}#{id}"
            hits_by_url[target_id] = (tuple)
        # logger.debug("exit _get_element_by_id_and_add_term_id_tuple_to_hits")

    @classmethod
    def get_hits_as_term_ref_p_tuple_list(cls, term_id_by_url):
        if term_id_by_url is None:
            logger.error(f"term_id_by_url is None")
            return None
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

    @classmethod
    def _add_hits_to_table(cls, tbody, term_ref_p_tuple_list):
        if term_ref_p_tuple_list is None:
            logger.error(f"term_ref_p_tuple_list is None")
            return
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




