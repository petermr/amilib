import argparse
import logging
import re
import sys
import textwrap
from enum import Enum
from pathlib import Path

# sometimes relative imports work, sometimes absolute
# maybe some wiser Pythonista can clean this
# i have no idea why html_args and pdf_args behave differently

try:
    from html_args import HTMLArgs
except ModuleNotFoundError as e:
    from amilib.html_args import HTMLArgs

from amilib.pdf_args import PDFArgs

from amilib.util import AbstractArgs
from amilib.wikimedia import WikidataLookup

# local

AMIX_DIR = Path(__file__).parent
REPO_DIR = AMIX_DIR.parent


class AmiLib:
    logger = logging.getLogger("amilib")
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

    def create_arg_parser(self):
        """creates adds the arguments for pyami commandline
        """

        def run_dict(self):
            print(f"run dict pyamix")

        def run_pdf(args):
            print(f"run pdf")

        # def run_project():
        #     print(f"run project {self.args}")

        version = self.version()
        if not sys.argv or len(sys.argv) == 0:
            # what does this do?
            sys.argv = [AmiLib.AmiLib]
        parser = argparse.ArgumentParser(
            description=f'pyamihtmlx: V{version} call with ONE of subcommands (HTML,PDF, IPCC, UNFCCC), e.g. pyamihtmlx IPCC --help'
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
            '  HTML <options>      # create/edit HTML\n'
            '  PDF <options>       # convert PDF into HTML and images\n'
            '\n'
            'After installation, run \n'
            '  amilib <subcommand> <options>\n'
            '\n'
            '\nExamples (# foo is a comment):\n'
            '  amilib        # runs help\n'
            '  pyamihtmlx -h     # runs help\n'
            '  pyamihtmlx PDF -h # runs PDF help\n'
            '  pyamihtmlx PDF --infile foo.pdf --outdir bar/ # converts PDF to HTML\n'
            '\n'
            '----------------------------------------\n\n'
        )

        # TODO should tests be run from this menu

        subparsers = parser.add_subparsers(help='subcommands', dest="command")
        for choice in subparsers.choices:
            print(f">>> {choice}")

        html_parser = HTMLArgs().make_sub_parser(subparsers)
        pdf_parser = PDFArgs().make_sub_parser(subparsers)

        amilib_parser = AmiLibArgs().make_sub_parser(subparsers)

        parser.epilog = "other entry points run as 'python -m pyamihtmlx.ami_dict args' also ami_pdf, ami_project"
        parser.epilog = """run:
        pyamihtmlx <subcommand> <args>
          where subcommand is in   {
          DICT,GUI,HTML,PDF,PROJECT} and args depend on subcommand
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

        if args is a string we split it at spaces into a list of strings

        """
        if isinstance(args, str):
            args = args.strip()
            args = args.split(" ")

        print(f"command: {args}")
        self.logger.debug(f"********** raw arglist {args}")
        test_catch = False
        if test_catch:  # try to trap exception
            try:
                self.parse_and_run_args(args)
            except Exception as e:
                print(f"ERROR {e.args} from {args}")
                logging.error(f"\n============PARSE ERROR==({e.__cause__})======\n")
                return
            if self.is_flag_true(self.PRINT_SYMBOLS):
                self.symbol_ini.print_symbols()
        else:
            self.parse_and_run_args(args)

        return

    def parse_and_run_args(self, arglist, debug=False):
        """runs cmds and makes substitutions (${...} then runs workflow

        :param arglist:

        """
        # no args, create help
        if not arglist:
            self.logger.warning("No args, running --help")
            arglist = ["--help"]
        parser = self.create_arg_parser()
        self.args = self.make_substitutions_create_arg_tuples(arglist, parser, debug=debug)
        self.logger.debug("ARGS before substitution: " + str(self.args))
        # this may be redundant
        self.substitute_args()
        self.logger.debug(f"self.args {self.args}")
        self.add_single_str_to_list()
        self.logger.debug("ARGS after substitution: " + str(self.args))
        self.set_loglevel_from_args()
        self.run_arguments()

    #
    def substitute_args(self):
        """ iterates through self.args and makes subsitutions
        May duplicates
        """
        new_items = {}
        # self.logger.debug(f"SYMBOLS1 {self.symbol_ini.symbols}")
        for item in self.args.items():
            new_item = self.make_substitutions(item)
            self.logger.debug(f"++++++++{item} ==> {new_item}")
            new_items[new_item[0]] = new_item[1]
        self.args = new_items
        self.logger.debug(f"******** substituted ARGS {self.args}")

    #
    def add_single_str_to_list(self):
        """convert single strings to list of one string
        Not sure of what this is for
        """
        str_args = [self.DEBUG, self.EXAMPLES]
        for str_arg in str_args:
            self.logger.debug(f"key {str_arg}")
            self.replace_single_values_in_self_args_with_list(str_arg)
            self.logger.debug(f"args => {self.args}")

    #
    def run_arguments(self):
        """ parse and expland arguments then ru options for

        Currently:
        * examples
        * project
        * tests

        There will be more here

         """
        # print(f"RUN ARGUMENTS on {self} {self.args}")
        # path workflow
        self.wikipedia_lookup = WikidataLookup()
        self.logger.debug(f"commandline args {self.args}")
        subparser_type = self.args.get("command")
        logging.debug(f" COMMAND: {subparser_type} {self.args}")

        subparser_dict = {
            # "DICT": AmiDictArgs(),
            # "GUI":  GUIArgs(),
            "HTML": HTMLArgs(),
            "PDF": PDFArgs(),
        }
        abstract_args = subparser_dict.get(subparser_type)

        if abstract_args:
            abstract_args.parse_and_process1(self.args)
        else:
            self.run_core_mathods()

    #
    def run_core_mathods(self):
        logging.debug(f"run_core")
        # mainly obsolete
        if self.VERSION in self.args and self.args[self.VERSION] is not None:
            self.print_version()
        if self.FLAGS in self.args and self.args[self.FLAGS] is not None:
            self.add_flags()
        # if self.CONFIG in self.args and self.args[self.CONFIG] is not None:
        #     self.apply_config()
        # if self.EXAMPLES in self.args:
        #     example_args = self.args[self.EXAMPLES]
        #     if example_args is not None:
        #         self.logger.debug(f" examples args: {example_args}")
        #         Examples(self).run_examples(example_args)
        if self.COPY in self.args and not self.args[self.COPY] is None:
            self.logger.warning(f"COPY {self.args[self.COPY]}")
            self.copy_files()
        if self.PROJ in self.args:
            if self.SECT in self.args or self.GLOB in self.args or self.SPLIT in self.args:
                self.run_project_workflow()
        if self.VERSION in self.args:
            self.print_version()
        # elif TestFile.TEST in self.args:
        #     self.logger.warning(f"TEST in **args {self.args}")
        #     TestFile.run_arg_tests(self.args)
        # TODO linkup with test arguments

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
            self.logger.warning(f"NULL self.args")
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
                print(f"PARSED ARGS FAILS {arglist}")
                return new_items
            if parsed_args == self.SYSTEM_EXIT_OK:  # return code 0
                return new_items
            if str(parsed_args).startswith(self.SYSTEM_EXIT_FAIL):
                raise ValueError(f"bad command arguments {parsed_args} (see log output)")

            self.logger.debug(f"PARSED_ARGS {parsed_args}")
            if debug:
                print(f"parsed args {parsed_args}")

            try:
                arg_vars = vars(parsed_args)  # FAILS in Pycharm
            except Exception as e:
                print(
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
            self.logger.error(f"Cannot parse {arglist} , {e}")
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
            self.logger.info(f"loglevel {loglevel}")
            if loglevel is not None:
                loglevel = str(loglevel)
            if loglevel is not None and loglevel.lower() in levels:
                level = levels[loglevel.lower()]
                self.logger.loglevel = level

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

    def add_arguments(self):
        if self.parser is None:
            self.parser = argparse.ArgumentParser()
        """adds arguments to a parser or subparser"""
        self.parser.description = 'HTML editing analysing annotation'
        self.parser.add_argument(f"--foo", action="store_true",
                                 help="annotate HTML file with dictionary")
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
        self.parser.epilog = "==============="

    """python -m pyamihtmlx.pyamix HTML --annotate 
     --dict /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/dict/emissions_abbreviations.xml
     --inpath /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/fulltext.html
     --outpsth /Users/pm286/projects/semanticClimate/ipcc/ar6/wg3/Chapter02/annotated/fulltext_emissions.html
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
        self.logger.warning("Dictionaries not supported")
        return

        if not self.dictfile:
            logging.error(f"no dictionary given")
            return
        if not self.inpath:
            logging.error(f"no input file to annotate given")
            return
        if not self.outpath:
            logging.error(f"no output file given")
            return
        if not self.outdir:
            self.outdir = Path(self.outpath).parent
        self.outdir = Path(self.outdir)
        self.outdir.mkdir(exist_ok=True)

        self.ami_dict = AmiDictionary.create_from_xml_file(self.dictfile)
        self.ami_dict.markup_html_from_dictionary(self.inpath, self.outpath, self.color)

    def make_foo(self):
        pass


class Converter(Enum):

    def __init__(self, converter_class, intype, outtype, indir=".", outdir="."):
        self.intype = intype
        self.indir = indir
        self.outtype = outtype
        self.outdir = outdir

    # PDF2SVG = (Pdf2SvgConverter, "pdf", "svg", ".", "svg")
    # PDF2TXT = (PdfReader, Filetype.F_PDF, Filetype.F_TXT, ".", ".")
    # XML2HTML = (Xml2HtmlConverter, "pdf", "html", ".", ".")
    # XML2TXT = (Xml2TxtConverter, "xml", "txt", ".", ".")
    # SVG2PAGE = (Svg2PageConverter, "svg", "html", "svg", "page")
    # PAGE2SECT = (Page2SectConverter, "html", "html", "page", "sect")
    # TXT2SENT = (Txt2SentSplitter, Filetype.F_TXT, Filetype.F_TXT, ".", "sent")


def main():
    # make_cmd()
    """ main entry point for cmdline

    """
    print(f"amilib")
    run_tests = False  # needs re-implementing

    run_commands = True
    #    run_commands = False

    #    run_tests = True

    AmiLib.logger.debug(
        f"\n============== running amilib main ===============\n{sys.argv[1:]}")
    amix = AmiLib()
    print(f"***** VERSION {amix.version()} *****")
    # this needs commandline
    if run_commands:
        amix.run_command(sys.argv[1:])


if __name__ == "__main__":
    main()
