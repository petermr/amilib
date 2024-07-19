import argparse
import json
import traceback
from collections import Counter
from pathlib import Path

from amilib.ami_args import AbstractArgs

# cyclic import
from amilib.ami_args import AbstractArgs
# from amilib.ami_dict import AmiEntry
from amilib.file_lib import FileLib
from amilib.wikimedia import WikidataPage, WikidataLookup, WikipediaPage

# commandline
DELETE = "delete"
DICT = "dict"
FILTER = "filter"
INPATH = "inpath"
LANGUAGE = "language"
METADATA = "metadata"
OUTPATH = "outpath"
REPLACE = "replace"
SYNONYM = "synonym"
VALIDATE = "validate"
WORDS = "words"

WIKIPEDIA = "wikipedia"
WIKIDATA = "wikidata"


logger = FileLib.get_logger(__file__)


class AmiDictArgs(AbstractArgs):
    """Parse args to build and edit dictionary"""

    def __init__(self):
        """arg_dict is set to default"""
        super().__init__()
        self.dictfile = None
        self.metadata = None
        self.filter = None
        self.language = None
        self.words = None
        self.delete = None
        self.replace = None
        self.synonym = None
        self.validate = None
        self.wikidata = None
        self.wikipedia = None
        self.ami_dict = None
        self.subparser_arg = "DICT"

    def add_arguments(self):
        # from amilib.ami_dict import DELETE, DICT, FILTER, LANGUAGE, METADATA, REPLACE, SYNONYM
        # from amilib.ami_dict import VALIDATE, WIKIDATA, WIKIPEDIA, WORDS

        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        """adds arguments to a parser or subparser"""
        self.parser.description = 'AMI dictionary creation, validation, editing'
        self.parser.add_argument(f"--{DELETE}", type=str, nargs="+",
                                 help="list of entries (terms) to delete ? duplicates (NYI)")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="path for dictionary (existing = edit; new = create (type depends on suffix *.xml or *.html)")
        self.parser.add_argument(f"--{FILTER}", type=str, nargs=1, help="path for filter py_dictionary")
        self.parser.add_argument(f"--{INPATH}", type=str, nargs="+", help="path for input file(s)")
        self.parser.add_argument(f"--{LANGUAGE}", type=str, nargs="+",
                                 help="list of 2-character codes to consider (default = ['en'] (NYI)")
        self.parser.add_argument(f"--{METADATA}", type=str, nargs="+", help="metadata item/s to add (NYI)")
        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs="+",
                                 help="output file ")
        self.parser.add_argument(f"--{REPLACE}", type=str, nargs="+",
                                 help="replace any existing entries/attributes (default preserve) (NYI)")
        self.parser.add_argument(f"--{SYNONYM}", type=str, nargs="+",
                                 help="add sysnonyms (from Wikidata) for terms (NYI)")
        self.parser.add_argument(f"--{VALIDATE}", action="store_true", help="validate dictionary")
        self.parser.add_argument(f"--{WIKIDATA}", type=str, nargs="*", help="add WikidataIDs (NYI)")
        self.parser.add_argument(f"--{WIKIPEDIA}", type=str, nargs="*",
                                 help="add Wikipedia link/s (forces --{WIKIDATA}) (NYI)")
        self.parser.add_argument(f"--{WORDS}", type=str, nargs=1,
                                 help="path/file with words to make or edit dictionary")
        self.parser.epilog = """
        Examples:
        DICT --words wordsfile --dict dictfile --wikipedia   # creates dictionary from wordsfile and adds wikipedia info
        DICT --inpath htmlfile --dict dictfile --outpath resultfile # reads htmlfile, marks up words in dict and write to outpath
        
        """
        # parser.add_argument(f"--{SORT}", type=str, nargs=1, help="sort by term, sort synonyms, sort by weight (NYI)")
        # parser.add_argument(f"--{CATEGORY}", type=str, nargs=1, help="annotate by category (NYI)")

    # class AmiDictArgs:
    def process_args(self):
        """runs parsed args
        :return:
        """
        # from amilib.ami_dict import DELETE, DICT, FILTER, LANGUAGE, METADATA, REPLACE, SYNONYM
        # from amilib.ami_dict import VALIDATE, WIKIDATA, WIKIPEDIA, WORDS

        """
        self.parser.add_argument(f"--dict", type=str, nargs=1, help="path for dictionary (existing = edit; new = create")
        self.parser.add_argument(f"--metadata", type=str, nargs="+", help="metadata item/s to add")
        self.parser.add_argument(f"--language", type=str, nargs="+", help="list of 2-character codes to consider (default = ['en']")
        self.parser.add_argument(f"--words", type=str, nargs=1, help="path/file with words to make or edit dictionary")
        self.parser.add_argument(f"--delete", type=str, nargs="+", help="list of entries (terms) to delete")
        self.parser.add_argument(f"--replace", type=str, help="replace any existing entries/attributes (default preserve)")
        self.parser.add_argument(f"--synonym", type=str, help="add sysnonyms (from Wikidata) for terms")
        self.parser.add_argument(f"--validate", type=str, nargs="*", help="validate dictionary")
        self.parser.add_argument(f"--wikidata", type=str, nargs="*", help="add WikidataIDs")
        self.parser.add_argument(f"--wikipedia", type=str, nargs="*", help="add Wikipedia link/s")
        """
        logger.debug(f"DICT process_args {self.arg_dict}")
        if not self.arg_dict:
            print(f"no arg_dict given, no actiom")

        self.delete = self.arg_dict.get(DELETE)
        self.dictfile = self.arg_dict.get(DICT)
        self.filter = self.arg_dict.get(FILTER)
        self.inpath = self.arg_dict.get(INPATH)
        self.language = self.arg_dict.get(LANGUAGE)
        self.metadata = self.arg_dict.get(METADATA)
        self.replace = self.arg_dict.get(REPLACE)
        self.outpath = self.arg_dict.get(OUTPATH)
        self.synonym = self.arg_dict.get(SYNONYM)
        self.validate = self.arg_dict.get(VALIDATE)
        self.wikidata = self.arg_dict.get(WIKIDATA)
        self.wikipedia = self.arg_dict.get(WIKIPEDIA)
        self.words = self.arg_dict.get(WORDS)

        if self.inpath and self.dictfile and self.outpath:
            self.make_dictionary_markup_file(self.inpath, self.dictfile, self.outpath)
            return

        if self.dictfile:

            print(f"writing to {self.dictfile}")
            # is this right??
            if self.ami_dict is not None:
                with open(self.dictfile, "w"):
                    self.ami_dict.write(self.dictfile)
                    print(f"wrote dict: {self.dictfile}")
            else:
                # print(f"reading dictionary {self.dictfile}")
                self.ami_dict = self.build_or_edit_dictionary()
                if self.ami_dict is None:
                    print(f"failed to read/compile dictionaty {self.dictfile}")

        if self.validate:
            if self.ami_dict is None:
                print(f"no dictionary givem")
            else:
                print(f"VALIDATING {self.ami_dict}")
                status = self.validate_dict()
                print(f"validation finished")

        # for argument --wikidata
        print(f"wikidata: {self.wikidata}")
        if self.wikidata is not None:
            hit_dict = self.add_wikidata_to_dict()
            status = self.validate_dict()

        # for argument --wikipedia
        if self.wikipedia is not None:
            print(f"Wikipedia lookup")
            hit_dict = self.add_wikipedia_to_dict()
            status = self.validate_dict()

        print(f"writing to {self}")
        if self.dictfile:
            if self.ami_dict:
                self.ami_dict.write_to_file(self.dictfile, debug=True)

    # class AmiDictArgs:

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
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

        if not self.dictfile:
            print("No dictionary file given")
            return None

        if not self.words:
            print(f"reading {self.dictfile} as dictionary")
            self.ami_dict = AmiDictionary.create_from_xml_file(self.dictfile)
        else:
            if not Path(self.words).exists():
                raise FileNotFoundError(f"wordfile {self.words} does not exist.")
            title = Path(self.words).stem
            print(f"creating {self.dictfile} from {self.words}")
            word_path = Path(self.words)
            self.ami_dict, _ = AmiDictionary.create_dictionary_from_wordfile(wordfile=word_path, title=None, desc=None)
        return self.ami_dict

    def add_wikidata_to_dict(self, description_regex=None):

        # TODO fix circular imports
        from amilib.ami_dict import AmiEntry

        desc_counter = Counter()
        hit_dict = dict()
        if self.dictfile is None or self.ami_dict is None:
            print(f"add_wikidata_to_dict requires existing dictionary")
            return
        wikidata_lookup = WikidataLookup()
        for entry in self.ami_dict.entries:
            self.add_wikidata_to_entry(entry, hit_dict, wikidata_lookup)

        print(f"JSON DUMPS {json.dumps(hit_dict, sort_keys=False, indent=2)}")
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
            print(f"sub-title {subdict.keys()}")
            for key, item in subdict.items():
                print(f".....{key} item_title {item['title']}")

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
            print(f"no qitem_hits {term} in add_wikidata_to_dict")
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

    def validate_dict(self):
        status = False
        if self.dictfile and Path(self.dictfile).exists():
            self.ami_dict.check_validity()
        else:
            print(f"vallidate_dict requires existing dictionary; no validation")
        return status

    @property
    def module_stem(self):
        """name of module"""
        return Path(__file__).stem

    def make_dictionary_markup_file(self, inpath, dictfile, outpath):
        from amilib.ami_dict import AmiDictionary

        dictfile = str(dictfile)

        if not dictfile.endswith(".html"):
            print(f"dictionary for commandline must be HTML")
            return None
        # dictionary = AmiDictionary.create_from_html_file(dictfile)
        # # print(f"terms: {len(dictionary.get_terms())} {dictionary.get_terms()[0]}")
        # dictionary.markup_html_from_dictionary(inpath, outpath)
        AmiDictionary.read_html_dictionary_and_markup_html_file(
             str(inpath), str(outpath), html_dict_path=dictfile)


# ====================


def main(argv=None):
    # AMIDict.debug_tdd()
    print(f"running AmiDict main")
    dict_args = AmiDictArgs()
    try:
        dict_args.parse_and_process()
    except Exception as e:
        print(traceback.format_exc())
        print(f"***Cannot run amidict***; see output for errors: {e} ")



if __name__ == "__main__":
    print("running dict main")
    main()
else:

    #    print("running dict main anyway")
    #    main()
    pass
