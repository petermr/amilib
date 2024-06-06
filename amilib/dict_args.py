import argparse
import json
from collections import Counter
from pathlib import Path

# commandline
DELETE = "delete"
DICT = "dict"
FILTER = "filter"
LANGUAGE = "language"
METADATA = "metadata"
REPLACE = "replace"
SYNONYM = "synonym"
VALIDATE = "validate"
WORDS = "words"

WIKIPEDIA = "wikipedia"
WIKIDATA = "wikidata"

from amilib.ami_args import AbstractArgs
try:

    from amilib.ami_dict import AmiDictionary
except Exception as e:
    pass
from amilib.file_lib import FileLib
from amilib.wikimedia import WikidataPage, WikidataLookup

logger = FileLib.get_logger(__file__)


class AmiDictArgs(AbstractArgs):
    """Parse args to build and edit dictionary"""

    def __init__(self):
        """arg_dict is set to default"""
        super().__init__()
        self.dictfile = None
        self.metadata = None
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
                                 help="path for dictionary (existing = edit; new = create")
        self.parser.add_argument(f"--{FILTER}", type=str, nargs=1, help="path for filter py_dictionary")
        self.parser.add_argument(f"--{LANGUAGE}", type=str, nargs="+",
                                 help="list of 2-character codes to consider (default = ['en'] (NYI)")
        self.parser.add_argument(f"--{METADATA}", type=str, nargs="+", help="metadata item/s to add (NYI)")
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
        self.language = self.arg_dict.get(LANGUAGE)
        self.metadata = self.arg_dict.get(METADATA)
        self.replace = self.arg_dict.get(REPLACE)
        self.synonym = self.arg_dict.get(SYNONYM)
        self.validate = self.arg_dict.get(VALIDATE)
        self.wikidata = self.arg_dict.get(WIKIDATA)
        self.wikipedia = self.arg_dict.get(WIKIPEDIA)
        self.words = self.arg_dict.get(WORDS)

        if self.dictfile:
            if self.ami_dict is not None:
                with open(self.dictfile, "w") as f:
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

        if self.wikidata:
            self.add_wikidata_to_dict()
            status = self.validate_dict()

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
        desc_counter = Counter()
        hit_dict = dict()
        if self.dictfile is not None and self.ami_dict is not None:
            wikidata_lookup = WikidataLookup()
            for entry in self.ami_dict.entries:
                term = entry.attrib["term"]
                term_dict = dict()
                hit_dict[term] = term_dict
                qitem0, desc, qitem_hits = wikidata_lookup.lookup_wikidata(term)
                for i, qitem_hit in enumerate(qitem_hits):
                    qitem_hit_dict = self.create_hit_dict_for(i, qitem_hit)
                    term_dict[qitem_hit] = qitem_hit_dict
        else:
            print(f"requires existing dictionary")

        print(json.dumps(hit_dict, sort_keys=False, indent=2))
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
            print(f"requires existing dictionary")
        return status

    @property
    def module_stem(self):
        """name of module"""
        return Path(__file__).stem
