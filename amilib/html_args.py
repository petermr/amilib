import argparse
import logging
from pathlib import Path

from util import AbstractArgs, AmiLogger

# commandline
ANNOTATE = "annotate"
COLOR = "color"
DICT = "dict"
INPATH = "inpath"
OUTDIR = "outdir"
OUTPATH = "outpath"

logger = AmiLogger.create_named_logger(__file__)


class HTMLArgs(AbstractArgs):
    """Parse args to analyze, edit and annotate HTML"""

    def __init__(self):
        """arg_dict is set to default"""
        super().__init__()
        self.dictfile = None
        self.inpath = None
        self.outpath = None
        self.outstem = None
        self.outdir = None
        self.arg_dict = None
        self.subparser_arg = "HTML"
        self.color = None
        self.annotate = None
        self.ami_dict = None

    def add_arguments(self):
        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        """adds arguments to a parser or subparser"""
        self.parser.description = 'HTML editing analysing annotation'
        self.parser.add_argument(f"--{ANNOTATE}", action="store_true",
                                 help="annotate HTML file with dictionary")
        self.parser.add_argument(f"--{COLOR}", type=str, nargs=1,
                                 help="colour for annotation")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="dictionary for annotation")
        self.parser.add_argument(f"--{INPATH}", type=str, nargs=1,
                                 help="input html file")
        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs=1,
                                 help="output html file")
        self.parser.add_argument(f"--{OUTDIR}", type=str, nargs=1,
                                 help="output directory")
        self.parser.epilog = "==============="

    """python -m pyamihtmlx.pyamix HTML --annotate 
     --dict /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/dict/emissions_abbreviations.xml
     --inpath /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/fulltext.html
     --outpsth /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/annotated/fulltext_emissions.html
     --color pink
     """

    # class AmiDictArgs:
    def process_args(self):
        """runs parsed args
        :return:
        """

        if not self.arg_dict:
            logging.warning(f"no arg_dict given, no action")
            return

        self.annotate = self.arg_dict.get(ANNOTATE)
        self.color = self.arg_dict.get(COLOR)
        self.dictfile = self.arg_dict.get(DICT)
        self.inpath = self.arg_dict.get(INPATH)
        self.outdir = self.arg_dict.get(OUTDIR)
        self.outpath = self.arg_dict.get(OUTPATH)

        if self.annotate:
            self.annotate_with_dict()

    # class AmiDictArgs:

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        arg_dict = dict()
        arg_dict[DICT] = None
        return arg_dict

    @property
    def module_stem(self):
        """name of module"""
        return Path(__file__).stem

    def annotate_with_dict(self):
        """uses dictionary to annotate words and phrases in HTML file"""
        logger.warning("Dictionaries not supported")

        # if not self.dictfile:
        #     logging.error(f"no dictionary given")
        #     return
        # if not self.inpath:
        #     logging.error(f"no input file to annotate given")
        #     return
        # if not self.outpath:
        #     logging.error(f"no output file given")
        #     return
        # if not self.outdir:
        #     self.outdir = Path(self.outpath).parent
        # self.outdir = Path(self.outdir)
        # self.outdir.mkdir(exist_ok=True)
        #
        # self.ami_dict = AmiDictionary.create_from_xml_file(self.dictfile)
        # self.ami_dict.markup_html_from_dictionary(self.inpath, self.outpath, self.color)

def main(argv=None):
    """entry point for HTML conversiom
    NYI

    """
    print(f"running HTMLArgs main")
    pdf_args = HTMLArgs()


if __name__ == "__main__":
    main()
else:
    pass
