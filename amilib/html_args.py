import argparse
import logging
from pathlib import Path

from amilib.ami_args import AbstractArgs, AmiArgParser, OPERATION
from amilib.util import Util

# commandline
ANNOTATE = "annotate"
ANNOTATE_FILE = "ANNOTATE_FILE"
COLOR = "color"
DATATABLES = "DATATABLES"
DICT = "dict"
INDIR = "indir"
INPATH = "inpath"
OUTDIR = "outdir"
OUTPATH = "outpath"

# logger = AmiLogger.create_named_logger(__file__)
logger = Util.get_logger(__name__)
logger.setLevel(logging.INFO)

class HTMLArgs(AbstractArgs):
    """Parse args to analyze, edit and annotate HTML"""

    def __init__(self):
        """arg_dict is set to default"""
        logger.debug("creating HTML Args")
        super().__init__()
        self.dictfile = None
        self.indir = None
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
        logger.debug(f"================== add arguments HTML ================")

        if self.parser is None:
            self.parser = AmiArgParser(
                usage="HTML amilib always uses subcommands (HTML,PDF)\n e.g. amilib PDF --help"
            )

        super().add_arguments();

        """adds arguments to a parser or subparser"""

        self.parser.description = 'HTML editing, analysing annotation'
        self.parser.formatter_class = argparse.RawDescriptionHelpFormatter

        self.parser.add_argument(f"--{ANNOTATE}", action="store_true",
                                 help="annotate HTML file with dictionary")
        self.parser.add_argument(f"--{COLOR}", type=str, nargs=1,
                                 help="colour for annotation")
        self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
                                 help="dictionary for annotation")
        self.parser.add_argument(f"--{INDIR}", type=str, nargs=1,
                                 help="input directory (CProject)")
        self.parser.add_argument(f"--{INPATH}", type=str, nargs=1,
                                 help="input html file")
        self.parser.add_argument(f"--{OPERATION}", type=str,
                                 default=ANNOTATE_FILE,
                                 choices=[ANNOTATE_FILE, DATATABLES],
                                 help=f"operation: "
                                      f"'{ANNOTATE_FILE}' needs '{INPATH}, {DICT}, {OUTPATH} '\n"
                                      f" '{DATATABLES}' needs '{INDIR}, optional {OUTPATH}'\n"
                                      f" default = '{ANNOTATE_FILE}"
                                 )

        self.parser.add_argument(f"--{OUTPATH}", type=str, nargs=1,
                                 help="output html file")
        self.parser.add_argument(f"--{OUTDIR}", type=str, nargs=1,
                                 help="output directory")
        self.parser.epilog = "====== epilog ========="
        return self.parser

    """python -m amilib.amix HTML --annotate 
     --dict /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/dict/emissions_abbreviations.xml
     --inpath /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/fulltext.html
     --outpsth /Users/pm286/projects/semanticClimate/ar6/ar6/wg3/Chapter02/annotated/fulltext_emissions.html
     --color pink
     """

    def process_args(self):
        """runs parsed args
        :return:
        """
        logger.debug(f"process_args")

        if not self.arg_dict:
            logger.warning(f"no arg_dict given, no action")
            return

        super().process_args()
        self.annotate = self.arg_dict.get(ANNOTATE)
        self.color = self.arg_dict.get(COLOR)
        self.dictfile = self.arg_dict.get(DICT)
        self.indir = self.arg_dict.get(INDIR)
        self.inpath = self.arg_dict.get(INPATH)
        self.outdir = self.arg_dict.get(OUTDIR)
        self.outpath = self.arg_dict.get(OUTPATH)
        self.operation = self.arg_dict.get(OPERATION)

        if self.annotate or self.operation == ANNOTATE_FILE:
            self.annotate_with_dict()
            return
        if self.operation == DATATABLES:
            self.make_datatables()
            return
        logger.error("No explicit operation given")



    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        arg_dict = dict()
        arg_dict[DICT] = None
        return arg_dict

    def annotate_with_dict(self):
        """uses dictionary to annotate words and phrases in HTML file"""
        logger.warning("Dictionaries not supported")

    def make_datatables(self):
        """
        makes JQuery.datatables for a CProject/corpus
        at present requires Pygetpapers output
        """
        from amilib.ami_corpus import AmiCorpus
        if self.indir is None:
            logger.error(f"Datables needs input directory {INDIR}")
            return None
        self.indir = Path(self.indir)
        if not self.indir.is_dir():
            logger.error(f"datatables needs existing directory {self.indir}")
            return None

        AmiCorpus.make_datatables(self.indir)



def main(argv=None):
    """entry point for HTML conversiom
    NYI

    """
    logger.debug(f"running HTMLArgs main")
    pdf_args = HTMLArgs()


if __name__ == "__main__":
    main()
else:
    pass
