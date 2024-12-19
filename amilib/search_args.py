import argparse
import logging
import textwrap
from collections import Counter
from pathlib import Path
import lxml.etree as ET

from amilib.ami_args import AbstractArgs, AmiArgParser
from amilib.util import Util
from amilib.ami_html import (HtmlLib, HtmlUtil, AmiAnnotator)

ANNOTATE = "annotate"
DICT = "dict"
INDEX = "index"
INPATH = "inpath"
NOINPUTSTYLES = "no_input_styles"
COUNTS = "counts"
OPERATION = "operation"
OUTPATH = "outpath"
QUERY = "query"
QUERY_ID = "query_id"
REPORTPATH = "report"
SEARCH = "SEARCH"
TITLE = "title"
WORDS = "words"

UNKNOWN = "unknown"

logger = Util.get_logger(__name__)
logger.setLevel(logging.INFO)

# ANNOTATION = 'annotation'
#
# class AmiAnnotator:
#     """
#     provides tools and syntax for annotating HTML, including hyperlinks
#     """
#     def __init__(self):
#         pass
#
#     def get_annotation_class(self):
#         """return symbol for annotation"""
#         return ANNOTATION
#
#     @classmethod
#     def get_anchors_with_annotations(cls, elem):
#         """
#         get all annotations in element (class='{ANNOTATION}'
#         :param elem: HTML element
#         :return: list of annotated anchor subelements, or None
#         """
#         if elem is None:
#             logger.error("None element")
#             return None
#         return elem.xpath(f".//a[@class='{ANNOTATION}']")
#
#

class AmiSearch:

    @classmethod
    def markup_html_file_with_words_or_dictionary(cls, inpath, outpath, html_dict_path=None,
                                                  phrases=None, remove_styles=False, make_counter=True, reportpath=None):
        """
        read semantic HTML file, extract paras with ids, create AmiDictionary from HTML,
        markup paras, and write marked  file
        :param inpath: to be marked up
        :param outpath: resulting marked file
        :param html_dict_path: dictiomary in HTML format; if None, requires phrases
        :param phrases: avoid AmiDictionary by giving list of phrasee, default None requires dictionary
        :param counter: empty Counter() to be filled
        :param reportpath: file to write counter to
        :return: HTML element marked_up
        """
        from amilib.ami_dict import AmiDictionary # TODO cyclic import

        assert Path(inpath).exists()
        paras = HtmlLib._extract_paras_with_ids(inpath)
        if remove_styles:
            HtmlUtil.remove_elems(paras[0], "/html/head/style")

        if not phrases:
            phrases = AmiDictionary._read_phrases_from_dictionary(html_dict_path)
        phrase_counter_by_para_id = HtmlLib.search_phrases_in_paragraphs(
            paras, phrases, markup=html_dict_path)
        # logger.info(f"phrase_counter_by_para_id {phrase_counter_by_para_id}")
        # logger.info(f"keys: {len(phrase_counter_by_para_id)}")
        # write marked_up html. The 'paras' are views on the original file
        html_elem = paras[0].xpath("/html")[0]
        HtmlLib.write_html_file(html_elem, outpath, debug=True)
        assert Path(outpath).exists()
        if make_counter:
            counter = AmiSearch.add_counts_from_outpath(outpath)
            if reportpath:
                most_common = counter.most_common()
                logger.info(f"most common: {most_common}")
                with open(reportpath, "w") as f:
                    f.write(str(most_common))
        return html_elem

    @classmethod
    def add_counts_from_outpath(cls, htmlpath):
        """
        reads annotated HTML file and counts annotations (a[@href and @title]s
        :param htmlpath: HTML file with annotations
        :return: counter with accumulated a@href counts
        """
        # count annotations
        """
        <a style="border:solid 1px; background: #ffbbbb;" 
        href="/Users/pm286/workspace/amilib/test/resources/dictionary/climate/carbon_cycle.xml"
         title="anthropogenic">anthropogenic</a>
         """
        htmlx = HtmlLib.parse_html(htmlpath)
        annotations = AmiAnnotator.get_anchors_with_annotations(htmlx)
        counter = Counter()
        for annotation in annotations:
            href = annotation.attrib.get("href")
            if not href:
                logger.warning(f"annotation has no href {ET.tostring(annotation)}")
                continue
            counter[href] += 1


        return counter


class SearchArgs(AbstractArgs):
    pass

    def __init__(self):
        super().__init__()
        # dictionary file to read search words from
        self.dictfile = None
        # particular search operation
        self.operation = None
        # the argparser
        self.parser = None
        self.reportpath = None
        self.title = UNKNOWN
        # words to search with (may be read directly or from dictfile
        self.words = None
        self.query_id = None

        self.subparser_arg = SEARCH


    def add_arguments(self):
        """creates adds the arguments for pyami commandline

        """
        logger.debug(f"================== add arguments SEARCH ================")
        if self.parser is None:
            self.parser = AmiArgParser(
                usage="SEARCH: amilib always uses subcommands (HTML,PDF, DICT, SEARCH)\n e.g. amilib SEARCH --help"
            )

        self.parser.description = textwrap.dedent(
            'SEARCH tools. \n'
            '----------\n'
            'Search documents and corpora and make indexes and maybe knowledge graphs.'
            'Not yet finished.\n'
            '\nExamples:\n'
            '  * SEARCH --help\n'
        )
        self.parser.formatter_class = argparse.RawDescriptionHelpFormatter

        # don't use superclass
        not_super = True

        logger.debug("adding super args")
        # super().add_arguments()

        self.parser.add_argument("--debug", type=str,
                                 help="debug these during parsing (NYI)")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="path for dictionary input *.xml or *.html)")
        if not_super:
            self.parser.add_argument(f"--{self.INDIR}", nargs="+",
                                     help=self.INDIR_HELP)
            self.parser.add_argument(f"--{self.OUTDIR}",
                                     help=self.OUTDIR_HELP)

        self.parser.add_argument(f"--{INPATH}", type=str, nargs="+", help="path for input file(s)")
        self.parser.add_argument(f"--{OPERATION}", type=str, nargs="+",
                                 default=ANNOTATE,
                                 choices=[ANNOTATE,
                                          COUNTS,
                                          INDEX,
                                          NOINPUTSTYLES],
                                 help=f"operation: "
                                      f"'{NOINPUTSTYLES}' needs '{INPATH} ; remove styles from inpath\n"
                                      f"'{ANNOTATE}' needs '{INPATH} and {DICT}'; annotates words/phrases\n"
                                      f"'{INDEX}' needs '{INPATH}' optionally {OUTPATH} (NYI)\n"
                                      f" default = {ANNOTATE}"
                                 )
        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs="+",
                                 help="output file ")
        # self.parser.add_argument(f"--{QUERY}", type=str,
        #                          nargs="+",
        #                          default=None,
        #                          help="synonym for --words")
        self.parser.add_argument(f"--{QUERY_ID}", type=str,
                                 default=None,
                                 help="id to add to output filenames; defaults to autogenerated (e.g. datetime)")
        self.parser.add_argument(f"--{REPORTPATH}", type=str,
                                 help="path for reporting operations (e.g .lists of extracted terms)")

        self.parser.add_argument(f"--{TITLE}", type=str,
                                 default="unknown",
                                 help="internal title for dictionary, normally same as stem of dictionary file")
        self.parser.add_argument(f"--{WORDS}", type=str,
                                 nargs="+",
                                 default=None,
                                 help="(list of) words/phrases to search with; phrases with spaces must be quoted. "
                                      )
        self.parser.epilog = """
        Examples:
        SEARCH --operation annotate --inpath infile --dict dictfile --outpath outfile  # uses dictfile to annotate words in infile and write outfile\n
        """
        self.parser.epilog = "============ SEARCH epilog ==========="
        return self.parser

    # class PDFArgs:
    def process_args(self):
        """runs parsed args
        pass
        """
        from amilib.ami_dict import AmiDictionary # TODO cyclic import

        logger.debug(f"SEARCH process_args {self.arg_dict}")
        if not self.arg_dict:
            logger.debug(f"no arg_dict given, no actiom")

        self.dictfile = self.arg_dict.get(DICT)
        self.inpath = self.arg_dict.get(INPATH)
        self.outpath = self.arg_dict.get(OUTPATH)
        self.indir = self.arg_dict.get(self.INDIR)
        self.outdir = self.arg_dict.get(self.OUTDIR)
        self.operation = self.arg_dict.get(OPERATION)
        self.reportpath = self.arg_dict.get(REPORTPATH)
        self.title = self.arg_dict.get(TITLE)
        self.words = self.arg_dict.get(WORDS)
        # query = self.arg_dict.get(QUERY)
        # # use self.words rather than self.query #TODO needs tidying
        # if not self.words and query:
        #     self.words = query
        self.query_id = self.arg_dict.get(QUERY_ID)

        self.remove_input_styles = NOINPUTSTYLES in self.operation
        self.counts = COUNTS in self.operation

        if self.operation is None:
            logger.warning("No operation given")
            return
        self.remove_input_styles = NOINPUTSTYLES in self.operation
        self.counts = COUNTS in self.operation

        if self.words is not None:
            self.words = Util.input_list_of_words(self.words)
        elif self.dictfile is not None:
            dikt = AmiDictionary.read_dictionary(self.dictfile)
            self.words = dikt.get_terms()

        logger.info(f"read arguments\n"
                    f"inpath: {self.inpath}\n"
                    f"dictfile: {self.dictfile}\n"
                    f"outpath: {self.outpath}\n"
                    f"operation: {self.operation}\n"
                    f"title: {self.title}\n"
                    f"words: {self.words}\n"
                    )


        if ANNOTATE in self.operation:
            self.markup_file_with_dict_or_words()

        if self.operation == INDEX:
            self.make_index()

# output goes here
        pass


    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary
        """
        arg_dict = dict()
        return arg_dict

    def markup_file_with_dict_or_words(self):
        """
        uses dictionary from self.dictfile, or list of words, to markup self.inpath and write to self.outpath:
        """
        # assert self.words, "must have self.words for search"
        logger.debug(f"search {self.inpath} with {self.dictfile} or {len(self.words) if self.words else 'NO'} words and output to {self.outpath}")
        if self.inpath and (self.words or self.dictfile) and self.outpath:
            self.make_dictionary_markup_file(self.inpath, self.dictfile, self.outpath)

    def make_dictionary_markup_file(self, inpath, dictfile, outpath):
        """
        create dictionary and annotate file
        :param inpath: HTML file to annotate
        :param dictfile: file containing dictionary
        :param outpath: output for annotated file
        TODO allow for more dictionaries
        """
        from amilib.ami_dict import AmiDictionary

        if self.words:
            pass
        elif dictfile:
            dictfile = str(dictfile)
            if not dictfile.endswith(".html"):
                logger.error(f"dictionary for commandline must be HTML")
                return None
        else:
            logger.error("Must give dictfile or words")

        # TODO this should not be in AmiDictionary
        AmiSearch.markup_html_file_with_words_or_dictionary(
            str(inpath), str(outpath), remove_styles=self.remove_input_styles,  html_dict_path=dictfile,
            phrases=self.words, make_counter=self.counts, reportpath=self.reportpath)
        # logger.info(f"wrote annotated file {outpath}")

    @classmethod
    def read_html_dictionary_and_markup_html_file(cls, inpath, outpath, html_dict_path):
        """
        read semantic HTML file, extract paras with ids, create AmiDictionary from HTML,
        markup paras, and write marked  file
        :param inpath: to be marked up
        :param outpath: resulting marked file
        :param html_dict_path: dictiomary in HTML format
        :return: HTML element marked_up
        """
        from amilib.ami_dict import AmiDictionary # TODO cyclic import

        assert Path(inpath).exists()
        paras = HtmlLib._extract_paras_with_ids(inpath)
        assert Path(html_dict_path).exists()
        # TODO this should not be an AmiDictinary responsibility. Use the phrases
        dictionary = AmiDictionary.create_from_html_file(html_dict_path)
        assert dictionary is not None
        phrases = dictionary.get_terms()
        dictionary.location = html_dict_path
        HtmlLib.search_phrases_in_paragraphs(paras, phrases, markup=html_dict_path)
        # write marked_up html
        chapter_elem = paras[0].xpath("/html")[0]
        HtmlLib.write_html_file(chapter_elem, outpath, debug=True)
        assert Path(outpath).exists()
        return chapter_elem



