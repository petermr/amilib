import argparse
import textwrap
from pathlib import Path

from amilib.ami_args import AbstractArgs, AmiArgParser
from amilib.ami_dict import AmiDictionary
from amilib.util import Util
from amilib.xml_lib import HtmlLib

ANNOTATE = "annotate"
DICT = "dict"
INDEX = "index"
INPATH = "inpath"
OPERATION = "operation"
OUTPATH = "outpath"
SEARCH = "SEARCH"
TITLE = "title"

UNKNOWN = "unknown"

logger = Util.get_logger(__name__)

class SearchArgs(AbstractArgs):
    pass

    def __init__(self):
        super().__init__()
        self.dictfile = None
        self.operation = None
        self.parser = None
        self.title = UNKNOWN
        self.words = None

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
        self.parser.add_argument("--debug", type=str,
                                 help="debug these during parsing (NYI)")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="path for dictionary  *.xml or *.html)")
        self.parser.add_argument(f"--{INPATH}", type=str, nargs="+", help="path for input file(s)")
        self.parser.add_argument(f"--{OPERATION}", type=str,
                                 default=ANNOTATE,
                                 choices=[ANNOTATE, INDEX],
                                 help=f"operation: "
                                      f"'{ANNOTATE}' needs '{INPATH} and {DICT}'; annotates words/phrases\n"
                                      f"'{INDEX}' needs '{INPATH}' optionally {OUTPATH} (NYI)\n"
                                      f" default = (%default)s"
                                 )
        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs="+",
                                 help="output file ")
        self.parser.add_argument(f"--{TITLE}", type=str,
                                 default="unknown",
                                 help="internal title for dictionary, normally same as stem of dictionary file")
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

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary
        """
        arg_dict = dict()
        return arg_dict

    def markup_file_with_dict(self):
        """
        uses dictionary from self.dictfile to markup self.inpath and write to self.outpath:
        """
        logger.debug(f"search {self.inpath} with {self.dictfile} and output to {self.outpath}")
        if self.inpath and self.dictfile and self.outpath:
            self.make_dictionary_markup_file(self.inpath, self.dictfile, self.outpath)

    def make_dictionary_markup_file(self, inpath, dictfile, outpath):
        """
        create dictionary and annotate file
        :param inpath: HTML file to annotate
        :param dictfile: file containing dictionary
        :param outpath: output for annotated file
        TODO allow for more dictionaries
        """
        logger.warning("DEPRECATED: use 'amilib SEARCH'")
        from amilib.ami_dict import AmiDictionary

        dictfile = str(dictfile)

        if not dictfile.endswith(".html"):
            logger.error(f"dictionary for commandline must be HTML")
            return None
        # TODO this should not be in AmiDictionary
        AmiDictionary.read_html_dictionary_and_markup_html_file(
            str(inpath), str(outpath), html_dict_path=dictfile)

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


