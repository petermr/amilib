import argparse
import json
import logging
import traceback
from collections import Counter
from pathlib import Path

from amilib.ami_args import AbstractArgs

# cyclic import
from amilib.ami_args import AbstractArgs
# from amilib.ami_dict import AmiDictionary # CYCLIC import
# from amilib.ami_dict import AmiEntry
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.wikimedia import WikidataPage, WikidataLookup, WikipediaPage, WiktionaryPage
from amilib.ami_html import HtmlLib

# commandline
DESCRIPTION = "description"
DICT = "dict"
FIGURES = "figures"
IMAGE = "image"
INPATH = "inpath"
OPERATION = "operation"
OUTPATH = "outpath"
SYNONYM = "synonym"
TITLE = "title"
VALIDATE = "validate"
WORDS = "words"

UNKNOWN = "unknown"

# operations
CREATE_DICT = "create"
EDIT_DICT = "edit"
MARKUP_FILE = "markup"
VALIDATE_DICT = "validate"

# description sources
WIKIPEDIA = "wikipedia"
WIKIDATA = "wikidata"
WIKTIONARY = "wiktionary"

logger = Util.get_logger(__name__)
logger.setLevel(logging.DEBUG)


class AmiDictArgs(AbstractArgs):
    """Parse args to build and edit dictionary"""

    def __init__(self):
        """arg_dict is set to default"""
        super().__init__()
        self.dictfile = None
        self.description = None
        self.operation = None
        self.parser = None
        self.synonym = None
        self.validate = None
        self.title = UNKNOWN
        self.wikidata = None
        self.wikipedia = None
        self.wiktionary = None
        self.words = None

        self.ami_dict = None
        self.subparser_arg = "DICT"

    def add_arguments(self):
        """
        add arguments into self.parser
        """

        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        """adds arguments to a parser or subparser"""
        self.parser.description = 'AMI dictionary creation, validation, editing'
        self.parser.add_argument(f"--{DESCRIPTION}", type=str, nargs="+",
                                 choices=[WIKIPEDIA, WIKTIONARY, WIKIDATA],
                                 help="add extended description tp dict from one or more of these")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="path for dictionary (existing = edit; new = create (type depends on suffix *.xml or *.html)")
        self.parser.add_argument(f"--{INPATH}", type=str, nargs="+", help="path for input file(s)")
        self.parser.add_argument(f"--{FIGURES}", type=str,
                                 nargs="*",
                                 default="None",
                                 choices=["None", WIKIPEDIA, WIKIDATA],
                                 help=f"sources for figures: "
                                      f"'{WIKIPEDIA}' uses infobox or first thumbnail, {WIKIDATA} uses first figure"
                                 )
        self.parser.add_argument(f"--{OPERATION}", type=str,
                                 default=CREATE_DICT,
                                 choices=[CREATE_DICT, EDIT_DICT, MARKUP_FILE, VALIDATE_DICT],
                                 help=f"operation: "
                                      f"'{CREATE_DICT}' needs '{WORDS}'\n"
                                      f" '{EDIT_DICT}' needs '{INPATH}'\n"
                                      f" '{MARKUP_FILE}' need '{INPATH}' and '{OUTPATH}` (move to search?)\n"
                                      f" '{VALIDATE}' requires '{INPATH}'\n"
                                      f" default = '{CREATE_DICT}"
                                 )
        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs="+",
                                 help="output file ")
        self.parser.add_argument(f"--{SYNONYM}", type=str, nargs="+",
                                 help="add sysnonyms (from Wikidata) for terms (NYI)")
        self.parser.add_argument(f"--{TITLE}", type=str,
                                 default="unknown",
                                 help="internal title for dictionary, normally same as stem of dictionary file")
        self.parser.add_argument(f"--{VALIDATE}", action="store_true", help="validate dictionary; DEPRECATED use '--operation validate'")
        self.parser.add_argument(f"--{WIKIDATA}", type=str, nargs="*", help=f"DEPRECATED use --description {WIKIDATA} add WikidataIDs (NYI)")
        self.parser.add_argument(f"--{WIKIPEDIA}", type=str, nargs="*",
                                 help="add Wikipedia link/s; DEPRECATED use '--description wikipedia'")
        self.parser.add_argument(f"--{WIKTIONARY}", type=str, nargs="*",
                                 help="add Wiktionary output as html (may be messy); DEPRECATED use '--description wiktionary'")
        self.parser.add_argument(f"--{WORDS}", type=str, nargs="*",
                                 help="path/file with words or list of words to create dictionaray")
        self.parser.epilog = """
        Examples:
        DICT --words wordsfile --dict dictfile --description wikipedia   # creates dictionary from wordsfile and adds wikipedia info\n
        
        
        """

    # class AmiDictArgs:
    def process_args(self):
        """runs parsed args
        :return:
        """
        logger.debug(f"DICT process_args {self.arg_dict}")
        if not self.arg_dict:
            logger.debug(f"no arg_dict given, no actiom")

        self.description = self.arg_dict.get(DESCRIPTION)
        self.dictfile = self.arg_dict.get(DICT)
        self.figures = self.arg_dict.get(FIGURES)
        if self.figures == "None":
            self.figures = None
        self.inpath = self.arg_dict.get(INPATH)
        self.outpath = self.arg_dict.get(OUTPATH)
        self.operation = self.arg_dict.get(OPERATION)
        self.synonym = self.arg_dict.get(SYNONYM)
        self.title = self.arg_dict.get(TITLE)
        self.validate = self.arg_dict.get(VALIDATE)
        self.wikidata = self.arg_dict.get(WIKIDATA)
        self.wikipedia = self.arg_dict.get(WIKIPEDIA)
        self.wiktionary = self.arg_dict.get(WIKTIONARY)
        self.words = self.make_input_words( self.arg_dict.get(WORDS))


        if self.operation is None:
            raise ValueError("No operation given")
        elif self.operation == CREATE_DICT:
            self.create_dictionary_from_words(self.title)
        elif self.operation == EDIT_DICT:
            self.edit_dictionary()
        elif self.operation == MARKUP_FILE:
            logger.warning(f"DEPRECATED; use 'amilib SEARCH'")
            self.markup_file_with_dict()
        elif self.operation == VALIDATE:
            self.validate_dict()
        else:
            raise ValueError(f"unknown oeration {self.operation}")

        if self.dictfile:
            if self.ami_dict:
                self.ami_dict.create_html_write_to_file(self.dictfile, debug=True)

    def add_descriptions_old(self):
        if self.wikidata is not None:
            hit_dict = self.add_wikidata_to_dict()
            status = self.validate_dict()
        # for argument --wikipedia
        if self.wikipedia is not None:
            logger.debug(f"Wikipedia lookup")
            hit_dict = self.add_wikipedia_to_dict()
            status = self.validate_dict()
        # for argument --wikipedia
        if self.wiktionary is not None:
            logger.debug(f"Wiktionary lookup {self.wiktionary}")
            if len(self.wiktionary) > 0:
                logger.debug(f"searching wiktionary for {self.wiktionary}")
                htmlx = WiktionaryPage.search_terms_create_html(self.wiktionary)
                temp = Path(Path(__file__).parent.parent, "temp")
                logger.info(f"temp dir {temp}")
                HtmlLib.write_html_file(htmlx, Path(temp, "wiktionary", f"{self.title}.html"))
                body = htmlx
            else:
                logger.debug(f"add to dictionary NYI")

    def add_descriptions(self):
        """
        add 1 or more descriptons from WIKIPEDIA, WIKIDATA or WIKTIONARY
        """
        if self.description is None:
            logger.warning("No entry description given")
            return
        for entry_description in self.description:
            if entry_description == WIKIDATA:
                hit_dict = self.add_wikidata_to_dict()
                status = self.validate_dict()
            elif entry_description == WIKIPEDIA:
                logger.debug(f"Wikipedia lookup")
                hit_dict = self.add_wikipedia_to_dict()
                status = self.validate_dict()
            elif entry_description == WIKTIONARY:
                logger.debug(f"Wiktionary lookup {self.wiktionary}")
                logger.debug(f"searching wiktionary for {self.wiktionary}")
                htmlx = WiktionaryPage.search_terms_create_html(self.wiktionary)
                temp = Path(Path(__file__).parent.parent, "temp")
                logger.info(f"temp dir {temp}")
                HtmlLib.write_html_file(htmlx, Path(temp, "wiktionary", f"{self.title}.html"))
                body = htmlx

    def create_dictionary_from_words(self, title):
        """
        use self.words to create a dictionary
        potentially add decriptions and figures
        :param title: mandatory title
        """
        if title is None:
            logger.error("must give title")
            return
        if self.words is None:
            logger.warning("no words given in args")
            return

        self.build_or_edit_dictionary()
        assert self.ami_dict is not None

        self.add_descriptions()
        if self.figures is not None:
            self.add_figures()

        if self.dictfile is not None:
            self.ami_dict.create_html_write_to_file(self.dictfile, debug=True)

    # class AmiDictArgs:

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        """
        is this used?
        """
        # from amilib.dict_args import DICT, VALIDATE, WIKIDATA, WORDS
        arg_dict = dict()
        arg_dict[DICT] = None
        arg_dict[VALIDATE] = None
        arg_dict[WIKIDATA] = None
        arg_dict[WORDS] = None
        return arg_dict

    def build_or_edit_dictionary(self):
        # cyclic imports TODO
        from amilib.ami_dict import AmiDictionary

        if self.words is not None:
            logger.info(f"creating dictionary from {self.words[:3]}...")
            self.ami_dict, _ = AmiDictionary.create_dictionary_from_words(
                terms=self.words, title=self.title, wiktionary=False)
        return self.ami_dict

    def add_wikidata_to_dict(self, description_regex=None):

        # TODO fix circular imports
        from amilib.ami_dict import AmiEntry

        desc_counter = Counter()
        hit_dict = dict()
        if self.dictfile is None or self.ami_dict is None:
            logger.debug(f"add_wikidata_to_dict requires existing dictionary")
            return
        wikidata_lookup = WikidataLookup()
        for entry in self.ami_dict.entries:
            self.add_wikidata_to_entry(entry, hit_dict, wikidata_lookup)

        logger.debug(f"JSON DUMPS {json.dumps(hit_dict, sort_keys=False, indent=2)}")
        counter = Counter()

        """
{
  "acetone": {
    "Q49546": {
      "title": "acetone",
      "description": "chemical compound",
      "score": 0
    },
    "Q222936": {
      "title": "acetone cyanohydrin",
      "description": "chemical compound",
      "score": 1
    },
  },
  "benzene": {
    ...
    },
  },
}
        """
        for hit_dict_key in hit_dict.keys():
            subdict = hit_dict[hit_dict_key]
            logger.debug(f"sub-title {subdict.keys()}")
            for key, item in subdict.items():
                logger.debug(f".....{key} item_title {item['title']}")

        return hit_dict

    def add_wikidata_to_entry(self, entry, hit_dict, wikidata_lookup):
        # cyclic import
        from amilib.ami_dict import AmiEntry
        ami_entry = AmiEntry.create_from_element(entry)
        term = entry.attrib["term"]
        term_dict = dict()
        hit_dict[term] = term_dict
        qitem0, desc, qitem_hits = wikidata_lookup.lookup_wikidata(term)
        if qitem_hits is None:
            logger.error(f"no qitem_hits {term} in add_wikidata_to_dict")
            return
        for i, qid in enumerate(qitem_hits):
            qitem_hit_dict = self.create_hit_dict_for(i, qid)
            term_dict[qid] = qitem_hit_dict
            ami_entry.add_hits_to_xml(qid, qitem_hit_dict)

    def add_wikipedia_to_dict(self):
        # TODO CYCLIC import
        from amilib.ami_dict import AmiEntry
        """
        NYI
        """
        if self.ami_dict.entries is None:
            logger.error("No self.ami_dict.entries")
            return
        for entry_elem in self.ami_dict.entries:
            ami_entry = AmiEntry.create_from_element(entry_elem)
            ami_entry.lookup_and_add_wikipedia_page()

    def create_hit_dict_for(self, serial, qitem_hit):
        qitem_hit_dict = dict()
        page = WikidataPage(pqitem=qitem_hit)
        description = page.get_description()
        title = page.get_title()
        qitem_hit_dict["title"] = title
        qitem_hit_dict["description"] = description
        qitem_hit_dict["score"] = serial

        return qitem_hit_dict

    @property
    def module_stem(self):
        """name of module"""
        return Path(__file__).stem

    def make_input_words(self, words):
        self.words = None if words is None else FileLib.get_input_strings(words)
        return self.words

# ========== create=======

    def add_figures(self):
        # TODO CYCLIC import
        from amilib.ami_dict import AmiEntry
        """
        iterate over all entries, and find the WikipediaPage. 
        extract figure/s from the page and add to the entry 
        calls ami_entry.add_figures_to_entry
        """
        if self.ami_dict.entries is None:
            logger.warning("No self.ami_dict.entries")
            return
        for entry_elem in self.ami_dict.entries:
            ami_entry = AmiEntry.create_from_element(entry_elem)
            wikipedia_page = ami_entry.lookup_and_add_wikipedia_page()
            # ami_entry.add_figures_to_entry_old()
            if wikipedia_page is not None:
                ami_entry.add_figures_to_entry(wikipedia_page)

    # ========== eiit ========
    def edit_dictionary(self):
        self.add_descriptions()


# ========== markup ========
    def markup_file_with_dict(self):
        """
        uses dictionary from self.dictfile to markup self.inpath and write to self.outpath:
        """
        logger.warning("DEPRECATED markup_file will be moved to SEARCH")
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
        # dictionary = AmiDictionary.create_from_html_file(dictfile)
        # # logger.info(f"terms: {len(dictionary.get_terms())} {dictionary.get_terms()[0]}")
        # dictionary.markup_html_from_dictionary(inpath, outpath)
        AmiDictionary.read_html_dictionary_and_markup_html_file(
            str(inpath), str(outpath), html_dict_path=dictfile)

    # ========== validate ========
    def validate_dict(self):
        logger.debug(f"VALIDATING {self.ami_dict}")
        status = False
        if self.dictfile and Path(self.dictfile).exists():
            self.ami_dict.check_validity()
        else:
            logger.error(f"vallidate_dict requires existing dictionary; no validation")
        logger.debug(f"validation finished")
        return status



# =============================


# ====================


def main(argv=None):
    # AMIDict.debug_tdd()
    logger.info(f"running AmiDict main")
    dict_args = AmiDictArgs()
    try:
        dict_args.parse_and_process()
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.error(f"***Cannot run amidict***; see output for errors: {e} ")


if __name__ == "__main__":
    logger.info("running dict main")
    main()
else:

    #    logger.debug("running dict main anyway")
    #    main()
    pass
