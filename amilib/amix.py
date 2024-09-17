import argparse
import logging
import re
import sys
import textwrap
from abc import abstractmethod
from enum import Enum
from pathlib import Path

# sometimes relative imports work, sometimes absolute
# maybe some wiser Pythonista can clean this
# i have no idea why html_args and pdf_args behave differently
from amilib.file_lib import FileLib

from amilib.dict_args import AmiDictArgs
from amilib.search_args import SearchArgs
from amilib.util import Util

try:
    from html_args import HTMLArgs
except ModuleNotFoundError as e:
    from amilib.html_args import HTMLArgs

from amilib.pdf_args import PDFArgs

from amilib.ami_args import AbstractArgs
from amilib.wikimedia import WikidataLookup

# local

AMIX_DIR = Path(__file__).parent
REPO_DIR = AMIX_DIR.parent

logger = Util.get_logger(__name__)
logger.setLevel(logging.INFO)

class AmiLib:
    COPY = "copy"
    DEBUG = "debug"
    EXAMPLES = "examples"
    FLAGS = "flags"
    GLOB = "glob"
    PROJ = "proj"
    SECT = "sect"
    SPLIT = "split"
    SYSTEM_EXIT_OK = "SystemExitOK"
    SYSTEM_EXIT_FAIL = "SystemExitFail_"
    VERSION = "version"
    LOGLEVEL = "loglevel"

    def __init__(self):
        """constructor

        creates symbols
        """
        logger.debug(f"amilib constructor")

    def create_arg_parser(self):
        """creates adds the arguments for pyami commandline
        """

        def run_dict(selfx):
            logger.debug(f"run dict amilib")
            pass

        def run_pdf(args):
            logger.debug(f"run pdf")
            pass


        version = self.version()
        if not sys.argv or len(sys.argv) == 0:
            # what does this do?
            sys.argv = [AmiLib.AmiLib]
        parser = argparse.ArgumentParser(
            description=f'amilib: V{version} call with ONE of subcommands (DICT, HTML,PDF, SEARCH), e.g. amilib DICT --help'
        )

        parser.add_argument('-v', '--version', action="store_true",
                            help=f"show version {version}")
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.description = textwrap.dedent(
            'pyamihtml: create, manipulate, use CProject \n'
            '----------------------------------------\n\n'
            'amilib is a set of problem-independent methods to support document retrieval and analysis'
            '\n'
            'The subcommands:\n\n'
            '  DICT <options>      # create and edit Ami Dictionaries\n'
            '  HTML <options>      # create/edit HTML\n'
            '  PDF <options>       # convert PDF into HTML and images\n'
            '  SEARCH <options>    # search and index documents\n'
            '\n'
            'After installation, run \n'
            '  amilib <subcommand> <options>\n'
            '\n'
            '\nExamples (# foo is a comment):\n'
            '  amilib        # runs help\n'
            '  amilib -h     # runs help\n'
            '  amilib PDF -h # runs PDF help\n'
            '  amilib PDF --infile foo.pdf --outdir bar/ # converts PDF to HTML\n'
            '\n'
            '----------------------------------------\n\n'
        )

        # TODO should tests be run from this menu

        subparsers = parser.add_subparsers(help='subcommands', dest="command")
        for choice in subparsers.choices:
            logger.debug(f">>> {choice}")
            pass

        dict_parser = AmiLibArgs.make_sub_parser(AmiDictArgs(), subparsers)
        logger.debug(f"dict_parser {dict_parser}")
        pdf_parser = AmiLibArgs.make_sub_parser(PDFArgs(), subparsers)
        logger.debug(f"pdf_parser {pdf_parser}")
        html_parser = AmiLibArgs.make_sub_parser(HTMLArgs(), subparsers)
        logger.debug(f"html_parser {html_parser}")
        search_parser = AmiLibArgs.make_sub_parser(SearchArgs(), subparsers)
        logger.debug(f"search_parser {search_parser}")

        parser.epilog = "other entry points run as 'python -m amilib.amix <args>'"
        parser.epilog = """run:
        pyamihtmlx <subcommand> <args>
          where subcommand is in   {DICT, HTML,PDF, SEARCH} and args depend on subcommand
        """

        return parser

    def commandline(self, commandline: str) -> None:
        """runs a commandline as a single string
        """
        if not commandline:
            self.run_command(["--help"])
        else:
            arglist = commandline.split(" ")
            self.run_command(arglist)

    def run_commands(self, arglistlist):
        """runs a list of commands

        :param arglistlist:  A list of commands (which are usually lists)

        for each list element uses run_command
        This allows for setup, assertions, etc.

        typical example:
        self.run_commands
        """
        if arglistlist is not None and isinstance(arglistlist, list):
            for arglist in arglistlist:
                self.run_command(arglist)

    def run_command(self, args):
        """parses cmdline, runs command and outputs symbols

        :param args: either a string or a list of strings
        NOTE: if any arg in noty a string it is transformed into one

        if args is a string we split it at spaces into a list of strings

        """
        logger.debug(f"********** raw arglist {args}")
        # split space_separated string into strings
        if isinstance(args, str):
            args = args.strip()
            args = args.split(" ")

        # convert all args to str
        args = [str(s) for s in args]
        logger.info(f"command: {args}")
        test_catch = False
        if test_catch:  # try to trap exception
            try:
                self.parse_and_run_args(args)
            except Exception as e:
                logger.error(f"ERROR {e.args} from {args}")
                return
        else:
            self.parse_and_run_args(args)

        return

    def parse_and_run_args(self, arglist, debug=False):
        """runs cmds and makes substitutions (${...} then runs workflow

        :param arglist:

        """
        # no args, create help
        if not arglist:
            logger.warning("No args, running --help")
            arglist = ["--help"]
        parser = self.create_arg_parser()
        self.args = self.make_substitutions_create_arg_tuples(arglist, parser, debug=debug)
        logger.debug("ARGS before substitution: " + str(self.args))
        # this may be redundant
        self.substitute_args()
        logger.debug(f"self.args {self.args}")
        self.add_single_str_to_list()
        logger.debug("ARGS after substitution: " + str(self.args))
        self.set_loglevel_from_args()
        self.run_arguments()

    #
    def substitute_args(self):
        """ iterates through self.args and makes subsitutions
        May duplicates
        """
        new_items = {}
        for item in self.args.items():
            new_item = self.make_substitutions(item)
            logger.debug(f"++++++++{item} ==> {new_item}")
            new_items[new_item[0]] = new_item[1]
        self.args = new_items
        logger.debug(f"******** substituted ARGS {self.args}")

    #
    def add_single_str_to_list(self):
        """convert single strings to list of one string
        Not sure of what this is for
        """
        str_args = [self.DEBUG, self.EXAMPLES]
        for str_arg in str_args:
            logger.debug(f"key {str_arg}")
            self.replace_single_values_in_self_args_with_list(str_arg)
            logger.debug(f"args => {self.args}")

    #
    def run_arguments(self):
        """ parse and expland arguments then ru options for

        Currently:
        * examples
        * project
        * tests

        There will be more here

         """
        # path workflow
        self.wikipedia_lookup = WikidataLookup()
        logger.debug(f"commandline args {self.args}")
        subparser_type = self.args.get("command")
        logging.debug(f" COMMAND: {subparser_type} {self.args}")

        subparser_dict = {
            "DICT": AmiDictArgs(),
            "SEARCH": SearchArgs(),
            "HTML": HTMLArgs(),
            "PDF": PDFArgs(),
        }
        abstract_args = subparser_dict.get(subparser_type)

        logger.debug(f"abstract_args {abstract_args}")
        if abstract_args:
            abstract_args._parse_and_process1(self.args)
        else:
            self.run_core_mathods()

    #
    def run_core_mathods(self):
        # logging.debug(f"run_core")
        # mainly obsolete
        if self.VERSION in self.args and self.args[self.VERSION] is not None:
            self.print_version()

    def print_version(self):
        print(f"version {self.version()}")


    #
    def replace_single_values_in_self_args_with_list(self, key):
        """always returns list even for single arg
        e.g. turns "foo" into ["foo"]
        This is to avoid strings being interpreted as lists of characters
        I am sure there is a more pythonic way
        """
        # argsx = None
        if self.args is None:
            logger.warning(f"NULL self.args")
        elif key in self.args:
            argsx = self.args[key]
            if argsx is not None:
                if type(argsx) != list:
                    self.args[key] = [argsx]

    #
    def make_substitutions(self, item):
        """

        :param item:

        """
        # no change
        return item


    def make_substitutions_create_arg_tuples(self, arglist, parser, debug=False):
        """
        processes raw args to expand substitutions

        :param arglist:
        :param parser:
        :return: list of transformed arguments as 2-tuples
        """
        new_items = {}
        if arglist and len(arglist) > 0:
            parsed_args = self.parse_args_and_trap_errors(arglist, parser)
            if parsed_args is None:
                logger.error(f"PARSED ARGS FAILS {arglist}")
                return new_items
            if parsed_args == self.SYSTEM_EXIT_OK:  # return code 0
                return new_items
            if str(parsed_args).startswith(self.SYSTEM_EXIT_FAIL):
                raise ValueError(f"bad command arguments {parsed_args} (see log output)")

            logger.debug(f"PARSED_ARGS {parsed_args}")
            if debug:
                logger.warning(f"parsed args {parsed_args}")

            try:
                arg_vars = vars(parsed_args)  # FAILS in Pycharm
            except Exception as e:
                logger.error(
                    f"argparse and vars() fails, see \n BUG in Pycharm/Pandas see https://stackoverflow.com/questions/75453995/pandas-plot-vars-argument-must-have-dict-attribute\n try fudge")
                # Namespace(command=None, version=True)
                match = re.match("Namespace\\((?P<argvals>[^)]*)\\)", parsed_args)
                if match:
                    arglistx = match.groupdict("argvals")
                    arg_vars = arglistx.split(",\\s*")

            for item in arg_vars.items():  # BUG in Pycharm/Pandas see https://stackoverflow.com/questions/75453995/pandas-plot-vars-argument-must-have-dict-attribute
                new_item = self.make_substitutions(item)
                new_items[new_item[0]] = new_item[1]
        return new_items

    #
    def parse_args_and_trap_errors(self, arglist, parser):
        """run argparse parser.parse_args and try to trap serious errors
        --help calls SystemExit (we trap and return None)"""
        try:
            parsed_args = parser.parse_args(arglist)
        except SystemExit as se:  # exit codes
            if str(se) == '0':
                parsed_args = self.SYSTEM_EXIT_OK
            else:
                parsed_args = self.SYSTEM_EXIT_FAIL + str(se)
        except Exception as e:
            parsed_args = None
            raise e
            logger.error(f"Cannot parse {arglist} , {e}")
        return parsed_args

    def set_loglevel_from_args(self):
        """ """
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }

        if self.LOGLEVEL in self.args:
            loglevel = self.args[self.LOGLEVEL]
            logger.info(f"loglevel {loglevel}")
            if loglevel is not None:
                loglevel = str(loglevel)
            if loglevel is not None and loglevel.lower() in levels:
                level = levels[loglevel.lower()]
                logger.loglevel = level

    def version(self):
        """
        reads setup.py and extracts line of form version='0.0.29'
        This is still a mess. We need to set the version once somewhere.
        """

        version = '0.0.1a1'  # 2024-03-27
        version = '0.0.1a3'  # 2024-03-27
        version = '0.0.1'  # 2024-04-03
        version = '0.0.2'  # 2024-04-04
        version = '0.0.3'  # 2024-04-19
        # had to revert here I think
        version = '0.0.6'  # 2024-04-19
        version = '0.0.7'  # 2024-04-23
        version = '0.0.8'  # 2024-04-23
        version = '0.0.9'  # 2024-05-09
        version = '0.0.10'  # 2024-05-09
        version = '0.1.0'  # 2024-05-10 # fixed absolute imports and mended tests
        version = '0.1.1'  # 2024-05-11 # fixed subclassing of AmiLibArgs
        version = '0.1.1a'  # 2024-05-11 # simple requirements.txt
        version = '0.1.2'  # 2024-05-20 # uploadable to pypi
        version = '0.1.3'  # 2024-05-20 # revert pdfplumber to 0.10.0
        version = '0.1.4'  # 2024-05-22 # revert pdfplumber to 0.11.0 
        version = '0.1.5'  # 2024-05-25 # fixed nlp, pdfplumber
        version = '0.2.0a1'  # 2024-06-06 # includes amidict 
        version = '0.2.1a1'  # 2024-06-06 # includes amidict and commandline
        version = '0.2.1a2'  # 2024-06-06 # includes amidict and commandline
        version = '0.2.1a3'  # 2024-07-03 # added wordlists
        version = '0.2.2a1'  # 2024-07-11 # wikipedia lookup and paragrah splitting
        version = '0.2.3a1'  # 2024-07-16 # markup html with dictionaries
        version = '0.2.3a2'  # 2024-07-17 # markup html with dictionaries
        version = '0.2.4a1'  # 2024-07-17 # add Wiktionary
        version = '0.2.4a2'  # 2024-08-27 # build dictionaries from wordlists preparing for release
        version = '0.2.5a1'  # 2024-08-30 # fixed Wiktionary bug
        version = '0.2.5'    # 2024-09-09 # testing as library usable by amiclimate
        version = '0.2.6'    # 2024-09-12 # added medisawiki parser
        version = '0.2.7'    # 2024-09-12 # corrected bug
        version = '0.3.0a1'  # 2024-09-17 # added SEARCH option
        version = '0.3.0a2'  # 2024-09-17 # removed import bug
        version = '0.3.0a3'  # 2024-09-17 # rensure compatibility with amiclimate

        # logging.warn(f"VERSION {version}")
        return version


class AmiLibArgs(AbstractArgs):
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

    @abstractmethod
    def add_arguments(self):
        logger.warn("add arguments")

        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        """adds arguments to a parser or subparser"""
        self.parser.description = 'Abstract editing analysing annotation'
        self.parser.add_argument(f"--foo", action="store_true",
                                 help="annotate HTML file with dictionary (NYI, TEST)")
        # self.parser.add_argument(f"--{COLOR}", type=str, nargs=1,
        #                          help="colour for annotation")
        # self.parser.add_argument(f"--{DICT}", type=str, nargs=1,
        #                          help="dictionary for annotation")
        # self.parser.add_argument(f"--{INPATH}", type=str, nargs=1,
        #                          help="input html file")
        # self.parser.add_argument(f"--{OUTPATH}", type=str, nargs=1,
        #                          help="output html file")
        # self.parser.add_argument(f"--{OUTDIR}", type=str, nargs=1,
        #                          help="output directory")
        self.parser.epilog = "======= ========"

    """python -m pyamihtmlx.pyamix HTML --annotate 
     --dict /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/dict/emissions_abbreviations.xml
     --inpath /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/fulltext.html
     --outpsth /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/annotated/fulltext_emissions.html
     --color pink
     """

    # class AmiDictArgs:
    @abstractmethod
    def process_args(self):
        """runs parsed args
        :return:
        """

        if not self.arg_dict:
            logging.warning(f"no arg_dict given, no action")
            return

        self.foo = self.arg_dict.get("foo")
        # self.color = self.arg_dict.get(COLOR)
        # self.dictfile = self.arg_dict.get(DICT)
        # self.inpath = self.arg_dict.get(INPATH)
        # self.outdir = self.arg_dict.get(OUTDIR)
        # self.outpath = self.arg_dict.get(OUTPATH)

        if self.foo:
            self.make_foo()

    # class AmiDictArgs:

    @classmethod
    def create_default_arg_dict(cls):
        """returns a new COPY of the default dictionary"""
        arg_dict = dict()
        arg_dict["dict"] = None
        return arg_dict

    @property
    def module_stem(self):
        """name of module"""
        return Path(__file__).stem

    def annotate_with_dict(self):
        """uses dictionary to annotate words and phrases in HTML file"""
        logger.warning("Dictionaries not supported")
        return

        if not self.dictfile:
            logging.error(f"no dictionary given")
            return
        if not self.inpath:
            logging.error(f"no input file to annotate given")
            return
        if not self.location_xml:
            logging.error(f"no output file given")
            return
        if not self.outdir:
            self.outdir = Path(self.location_xml).parent
        self.outdir = Path(self.outdir)
        self.outdir.mkdir(exist_ok=True)

        self.ami_dict = AmiDictionary.create_from_xml_file(self.dictfile)
        self.ami_dict.markup_html_from_dictionary(self.inpath, self.location_xml, self.color)

    def make_foo(self):
        pass


class Converter(Enum):

    def __init__(self, converter_class, intype, outtype, indir=".", outdir="."):
        self.intype = intype
        self.indir = indir
        self.outtype = outtype
        self.outdir = outdir


def main():
    # make_cmd()
    """ main entry point for cmdline

    """
    run_tests = False  # needs re-implementing

    run_commands = True
    #    run_commands = False

    #    run_tests = True

    logger.debug(
        f"\n============== running amilib main ===============\n{sys.argv[1:]}")
    amix = AmiLib()
    logger.info(f"***** amilib VERSION {amix.version()} *****")
    # this needs commandline
    if run_commands:
        amix.run_command(sys.argv[1:])


if __name__ == "__main__":
    main()
