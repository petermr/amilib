import argparse
import ast
import codecs
import getpass
import importlib
import logging
import os
import sys
import csv
import re
from enum import Enum

import lxml
import pandas as pd
import pyvis
from lxml import html
from pathlib import Path
import time
import urllib3
import requests
import json
import base64

# THIS FILE HAS NO amilib IMPORTS TO AVOID CYCLIC DEPENDENCIES
def _get_logger(name,
                level=logging.DEBUG,
                err_level=logging.ERROR,
                err_log="error.log",
                format="%(name)s | %(levelname)s | %(filename)s:%(lineno)s |>>> %(message)s",
                ):
    """
    DO NOT CALL THIS
    """
    # this gets called in Util,get_logger(__name) everywhere except this file
    """
    replaces old get_logger

    gets system logger with handlers set
    hopefully works
    :param name: name of logger (recommend __name__)
    :param level: log level for stdout, default WARN
    :param err_level: level for error (default ERROR)
    :param err_log: file to write err_level to, None = no write (default None)
    :param format: default '%(name)s | %(levelname)s | %(filename)s:%(lineno)s |>>> %(message)s'

    Note for exceptions use FileLib.log_exception
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Create handlers for logging to the standard output and a file
    stdoutHandler = logging.StreamHandler(stream=sys.stdout)
    errHandler = logging.FileHandler(err_log)
    # Set the log levels on the handlers
    stdoutHandler.setLevel(level)
    err_level = logging.ERROR
    errHandler.setLevel(err_level)
    # Create a log format using Log Record attributes
    format = "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
    format = "%(levelname)s %(filename)s:%(lineno)s:%(message)s"
    fmt = logging.Formatter(format)
    # Set the log format on each handler
    stdoutHandler.setFormatter(fmt)
    errHandler.setFormatter(fmt)
    # Add each handler to the Logger object
    logger.addHandler(stdoutHandler)
    logger.addHandler(errHandler)
    return logger


logger = _get_logger(__name__)

HREF = "href"


class Util:
    """Utilities, mainly staticmethod or classmethod and not tightly linked to AMI"""


    @classmethod
    def get_logger(cls,
                    name,
                    level=logging.DEBUG,
                    err_level=logging.ERROR,
                    err_log="error.log",
                    format="%(name)s | %(levelname)s | %(filename)s:%(lineno)s |>>> %(message)s",
                    ):
        """
        creates logger with name == __name__
        """
        return _get_logger(name, level, err_level, err_log, format)



    @classmethod
    def set_logger(cls, module,
                   ch_level=logging.INFO, fh_level=logging.DEBUG,
                   log_file=None, logger_level=logging.WARNING):
        """create console and stream loggers

        taken from https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook

        :param module: module to create logger for
        :param ch_level:
        :param fh_level:
        :param log_file:
        :param logger_level:
        :returns: singleton logger for module
        :rtype logger:

        """
        _logger = logging.getLogger(module)
        _logger.setLevel(logger_level)
        # create path handler

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if log_file is not None:
            fh = logging.FileHandler(log_file)
            fh.setLevel(fh_level)
            fh.setFormatter(formatter)
            _logger.addHandler(fh)

        # create console handler
        ch = logging.StreamHandler()
        ch.setLevel(ch_level)
        ch.setFormatter(formatter)
        _logger.addHandler(ch)

        _logger.debug(f"PyAMI {_logger.level}{_logger.name}")
        return _logger

    @staticmethod
    def find_unique_keystart(keys, start):
        """finds keys that start with 'start'
        return a list, empty if none found or null args
        """
        return [] if keys is None or start is None else [k for k in keys if k.startswith(start)]

    @staticmethod
    def find_unique_dict_entry(the_dict, start):
        """
        return None if 0 or >= keys found
        """
        keys = Util.find_unique_keystart(the_dict, start)
        if len(keys) == 1:
            return the_dict[keys[0]]
        logger.debug("matching keys:", keys)
        return None

    @classmethod
    def read_pydict_from_json(cls, file):
        with open(file, "r") as f:
            contents = f.read()
            dictionary = ast.literal_eval(contents)
            return dictionary

    @classmethod
    def normalize_whitespace(cls, text):
        """normalize spaces in string to single space
        :param text: text to normalize"""
        return " ".join(text.split())

    @classmethod
    def is_whitespace(cls, text):
        text = cls.normalize_whitespace(text)
        return text == " " or text == ""

    @classmethod
    def basename(cls, file):
        """returns basename of file
        convenience (e.g. in debug statements
        :param file:
        :return: basename"""
        return os.path.basename(file) if file else None

    @classmethod
    def add_sys_argv_str(cls, argstr):
        """splits argstr and adds (extends) sys.argv
        simulates a commandline
        e.g. Util.add_sys_argv_str("foo bar")
        creates sys.argv as [<progname>, "foo", "bar"]
        Fails if len(sys.argv) != 1 (traps repeats)
        :param argstr: argument string spoce separated
        :return:None
        """
        cls.add_sys_argv(argstr.split())

    @classmethod
    def add_sys_argv(cls, args):
        """adds (extends) sys.argv
        simulates a commandline
        e.g. Util.add_sys_argv_str(["foo", "bar"])
        creates sys.argv as [<progname>, "foo", "bar"]
        Fails if len(sys.argv) != 1 (traps repeats)
        :param args: arguments
        :return:None
        """
        if not args:
            logger.warning(f"empty args, ignored")
            return
        if len(sys.argv) != 1:
            logger.debug(f"should only extend default sys.argv (len=1), found {sys.argv}")
        sys.argv.extend(args)

    @classmethod
    def create_name_value(cls, arg: str, delim: str = "=") -> tuple:
        """create name-value from argument
        if arg is simple string, set value to True
        if arg contains delimeter (e.g. "=") split at that
        :param arg: argument (with 0 or 1 delimiters
        :param delim: delimiter (default "=", cannot be whitespace
        :return: name, value , or name, True or None
        """
        if not arg:
            return None
        if not delim:
            raise ValueError(f"delimiter cannot be None")
        if arg.isspace():
            raise ValueError(f"arg cannot be whitespace")
        if len(arg) == 0:
            raise ValueError(f"arg cannot be empty")
        if len(arg.split()) > 1:
            raise ValueError(f"arg [{arg}] may not contain whitespace")

        if delim.isspace():
            raise ValueError(f"cannot use whitespace delimiter")

        ss = arg.split(delim)
        if len(ss) == 1:
            return arg, True
        if len(ss) > 2:
            raise ValueError(f"too many delimiters in {arg}")
        # convert words to booleans
        try:
            ss[1] = ast.literal_eval(ss[1])
        except Exception:
            pass
        return ss[0], ss[1]

    @classmethod
    def extract_csv_fields(cls, csv_file, name, selector, typex):
        """select fields in CSV file by selector value"""
        values = []
        with open(str(csv_file), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if row[selector] == typex:
                    values.append(row[name])
        return values

    SINGLE_BRACKET_RE = re.compile(r"""
                    (?P<pre>[^(]*)
                    [(]
                    (?P<body>
                    [^)]*
                    )
                    [)]
                    (?P<post>.*)
                    """, re.VERBOSE)  # finds a bracket pair in running text, crude

    @classmethod
    def range_list_contains_int(cls, value, range_list):
        """Is an in in a list of ranges
        :param value: int to test
        :param range_list: list of ranges (or single range)"""
        if range_list is None:
            return False
        # might be a single range
        if type(range_list) is range:
            return value in range_list
        for rangex in range_list:
            if value in rangex:
                return True
        return False

    @staticmethod
    def matches_regex_list(string, regex_list):
        """
        iterate through list and break at first match
        :param string: to match
        :param regex_list: list of regexes
        :return: regex of first match, else None
        """
        for regex in regex_list:
            if re.match(regex, string):
                return regex
        return None

    @classmethod
    def make_translate_mask_to_char(cls, orig, rep):
        """
        make mask to replace all characters in orig with rep character
        :param orig: string of replaceable characters
        :param rep: character to replac e them
        :returns: dict mapping (see str.translate and str.make
        """
        if not orig or not rep:
            return None
        if len(rep) != 1:
            logging.warning(f"rep should be single char, found {rep}")
            return None
        if len(orig) == 0:
            logging.warning(f"orig should be len > 0")
            return None
        return str.maketrans(orig, rep * len(orig))

    @classmethod
    def print_stacktrace(cls, ex):
        """
        prints traceback
        :param ex: the exception
        """
        if ex:
            traceback = ex.__traceback__
            while traceback:
                logger.debug(f"{traceback.tb_frame.f_code.co_filename}: {traceback.tb_lineno}")
                traceback = traceback.tb_next

    @classmethod
    def get_urls_from_webpage(cls, suffixes, weburl):

        page = requests.get(weburl)
        tree = html.fromstring(page.content)
        ahrefs = tree.xpath(f".//a[@{HREF}]")
        urls = []
        for sf in suffixes:
            sf_ = [ahref.attrib[HREF] for ahref in ahrefs if ahref.attrib[HREF].endswith(f".{sf}")]
            urls.extend(sf_)
        return urls

    @classmethod
    def download_urls(cls, urls=None, target_dir=None, maxsave=100, printfile=True, skip_exists=True, sleep=5):
        """
        download list of urls
        :param urls: urls to download
        :param target_dir: directry to receive urls
        :param maxsave: maximum number to download (note: can be used tyo dowwnload in batches) default = 100
        :param printfile: prints download or skip (default = True)
        :param skip_exists: If true does not overwrite existuing file (default = True)
        :param sleep: seconds to wait  between downloads (default = 5)
        """
        if urls is None:
            logger.debug(f"no url list to download")
            return None
        if type(urls) is not list:
            urls = [urls]
        if target_dir is None:
            logger.debug(f"no traget_dir to download into")
            return None
        for url in urls[:maxsave]:
            stem = url.split("/")[-1]
            target_dir.mkdir(exist_ok=True)
            path = Path(target_dir, stem)
            if skip_exists and path.exists():
                if printfile:
                    logger.debug(f"file exists, skipped {path}")
            else:
                try:
                    content = requests.get(url).content
                except Exception as e:
                    logger.debug(f"cannot get content from url {url}")
                    continue
                with open(path, "wb") as f:
                    if printfile:
                        logger.debug(f"wrote url: {path}")
                    f.write(content)
                time.sleep(sleep)
        return None

    @classmethod
    def get_file_from_url(cls, url):
        """
        takes last slash-separated field in url as pseudo filename
        url to parse of form https://foo.nar/plugh/bloop.xml
        :param url: url to parse
        :return: file after last slash (i.e. bloop.xml) or None
        """
        if url is None:
            return None
        rindex = url.rfind('/')
        if rindex == -1:
            return None
        return url[rindex + 1:]

    @classmethod
    def create_string_separated_list(cls, listx):
        """
        create string separated list , e.g. [1,2,3] => "1 2 3"
        :param listx: list of objects
        :return" space-separaated list
        """
        return " ".join(list(map(str, listx))) if listx else ""

    @classmethod
    def open_write_utf8(cls, outpath):
        """
        opens file for writing as UTF-8
        (with open(outpath,"w" as f
        may fail if there are problem characters)
        :param outpath: file to write to
        :return: StreamReaderWriter
        """
        if not outpath:
            return None
        return codecs.open(str(outpath), "w", "UTF-8")

    @classmethod
    def open_read_utf8(cls, inpath):
        """
        opens file for reading as UTF-8
        (with open(inpath,"r" as f
        may fail if there are problem characters)
        :param inpath: file to read
        :return: StreamReaderWriter
        """
        return codecs.open(inpath, "r", "UTF-8")

    @classmethod
    def is_base64(cls, s):
        """
        tests if string is base64 by encoding and decoding
        :param s: string to test
        :return: True if successful , Exception creates False
        """
        try:
            return base64.b64encode(base64.b64decode(s)) == s
        except Exception:
            logger.debug(f"not b64: {s}")
            return False

    @classmethod
    def create_pyviz_graph(cls, incsv, anchor="anchor", target="target", outpath=None):
        """creates network graph from CSV file
        :param incsv: csv filename
        :param anchor: name of anchor column (def 'anchor')
        :param target: name of target column (def 'target')
        :param outpath: file to draw graph to (def None)
        uses pyvis_graph.force_atlas_2based() for layout (will give moer options later
        """
        try:
            with open(str(incsv), "r") as f:
                data = pd.read_csv(f)
        except Exception as e:
            logger.error(f"cannot read {incsv} because {e}")
            return
        anchors = cls.get_column(data, anchor, incsv)
        targets = cls.get_column(data, target, incsv)
        if anchors is None or targets is None:
            logger.error(f"Cannot find anchors/targets in CSV {incsv}")
            return None
        pyvis_graph = pyvis.network.Network(notebook=True)
        for a, t in zip(anchors, targets):
            pyvis_graph.add_node(a, label=a)  # also color, size
            pyvis_graph.add_node(t, label=t)
            pyvis_graph.add_edge(a, t)  # also color
        pyvis_graph.force_atlas_2based()
        if outpath:
            try:
                pyvis_graph.show(str(outpath))
            except Exception as e:
                logger.error(f"Cannot write pyviz graph to {outpath} because {e}")

    @classmethod
    def get_column(cls, data, colname, csvname=None):
        col = data.get(colname)
        if col is None:
            logger.error(f"Cannot find column {colname} in CSV {csvname}")
        return col

    @classmethod
    def should_make(cls, target, source):
        """
        return True if target does not exist or is older than source
        :param target: file to make
        :param source: file to create from
        :return:
        """
        if not source:
            raise ValueError("source is None")
        if not target:
            raise ValueError("target is None")
        source_path = Path(source)
        target_path = Path(target)
        if not source_path.exists():
            raise FileNotFoundError("{source} does not exist")
        if not target_path.exists():
            return True
        # modification times (the smaller the older)
        target_mod = os.path.getmtime(target)
        source_mod = os.path.getmtime(source)
        return target_mod < source_mod

    @classmethod
    def need_to_make(cls, outfile, infile, debug=False):
        """
        simple make-like comparison of files
        :param outfile: file to make
        :param infile: generating file
        :return: True if outfile does not exist or is older than infile
        """
        if not outfile.exists():
            return True
        need_to_make = not outfile.exists() or os.path.getmtime(str(infile)) > os.path.getmtime(str(outfile))
        if debug and need_to_make:
            logger.debug(f"need to make {outfile} from {infile}")
        return need_to_make

    @classmethod
    def delete_file_and_check(cls, file):
        """delete a file and checks it worked
        :param file: to delete"""
        if file.exists():
            file.unlink()
        assert not file.exists()

    @classmethod
    def get_float_from_dict(cls, dikt, key):
        """gets float value from dict
        e.g. {"foo" : 20} gives 20.0
        :param dikt: dictionary
        :param key:
        :return: float or None
        """
        value = None if dikt is None else dikt.get(key)
        value = float(value) if value else None
        return value

    @classmethod
    def get_float(cls, f):
        """converts f to float or None
        """
        try:
            return float(f)
        except Exception as e:
            return None

    @classmethod
    def get_list(cls, arg):
        """
        return a list, including of len=1
        :param arg: list or scalar
        :return: list (or None)
        """
        if arg and not type(arg) is list:
            arg = [arg]
        return arg

    @classmethod
    def get_class_from_name(cls, classname):
        """creates class from fully qualified classname
        :param classname: string of form foo.bar.MyClass
        "return: uninstantiated class
        """
        classname_bits = classname.rsplit(".", 1)
        clazz = getattr(importlib.import_module(classname_bits[0]), classname_bits[1])
        return clazz

    @classmethod
    def get_classname(cls, object):
        return object.__class__.__name__
        pass

    @classmethod
    def get_username(cls):
        """
        gets username
        https://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
        some possibility of spoofing , biut doesn't matter for us
        """
        return getpass.getuser()

    @classmethod
    def normalize_chars(cls, line):
        """
        reduce non-ANSI chars if possible
        """
        line = line.replace('“', '")')
        return line


class GithubDownloader:
    """Note: Github uses the old 'master' name but we have changed it to 'main'"""

    def __init__(self, owner=None, repo=None, sleep=3, max_level=1):
        """if sleep is too small, Github semds 403"""
        self.owner = owner
        self.repo = repo
        self.main_url = None
        self.sleep = sleep
        self.max_level = max_level

        """
        7
https://stackoverflow.com/questions/50601081/github-how-to-get-file-list-under-directory-on-github-pages

Inspired by octotree (a chrome plugin for github),
send API GET https://api.github.com/repos/{owner}/{repo}/git/trees/master to get root folder structure and recursively visit children of "type": "tree".

As github API has rate limit of 5000 requests / hour, this might not be good for deep and wide tree.
{
  "sha": "8b991099652468e1c3c801f5600d37ec483be07f",
  "url": "https://api.github.com/repos/petermr/CEVOpen/git/trees/8b991099652468e1c3c801f5600d37ec483be07f",
  "tree": [
    {
      "path": ".gitignore",
      "mode": "100644",
      "type": "blob",
      "sha": "22c4e9d412e97ebbeceb6d7b922970ba115db9ac",
      "size": 323,
      "url": "https://api.github.com/repos/petermr/CEVOpen/git/blobs/22c4e9d412e97ebbeceb6d7b922970ba115db9ac"
    },
    {
      "path": "BJOC",
      "mode": "040000",
      "type": "tree",
      "sha": "68866e1c37b63e4699b75cae8dc6923ef04fb898",
      "url": "https://api.github.com/repos/petermr/CEVOpen/git/trees/68866e1c37b63e4699b75cae8dc6923ef04fb898"
    },
        """

    def make_get_main_url(self):
        if not self.main_url and self.owner and self.repo:
            self.main_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/master"
        return self.main_url

    def load_page(self, url, level=1, page=None, last_path=None):
        if level >= self.max_level:
            logger.debug(f"maximum tree levels exceeded {level} >= {self.max_level}\n")
            return
        time.sleep(self.sleep)
        response = requests.get(url)
        if str(response.status_code) != '200':
            logger.debug(f"page response {response} {response.status_code} {response.content}")
            return None
        page_dict_str = response.content.decode("UTF-8")
        json_page = json.loads(page_dict_str)
        logger.debug(f"json page {json_page.keys()}")
        path = json_page["path"] if "path" in json_page else last_path
        if "tree" in json_page:
            links = json_page['tree']
            for link in links:
                logger.debug(f"link: {link.items()} ")
                typex = link["type"]
                path = link["path"]  # relative (child) pathname
                child_url = link["url"]
                if typex == 'blob':
                    self.load_page(child_url, level=level, last_path=path)
                elif typex == 'tree':
                    logger.debug(f"\n============={path}===========")
                    self.load_page(child_url, level=level + 1)
        elif "content" in json_page:
            content_str = json_page["content"]
            encoding = json_page["encoding"]
            if encoding == "base64":
                content = base64.b64decode(content_str).decode("UTF-8")
                logger.debug(f"\n===={path}====\n{content[:100]} ...\n")
        else:
            logger.debug(f"unknown type {json_page.keys()}")

    @classmethod
    def make_translate_mask_to_char(cls, punct, charx):
        """
        makes mask to translate all chars to a sigle replacmeny
        uses str,maketrans()

        Use:
        mask = Util.make_translate_mask_to_char("=]%", "_""):
        str1 = str0.translate(mask)
        str1 is same length as str0
        :param punct: string containing unwanted chars
        :param charx: their single character replacement.
        """
        punct_mask = str.maketrans(punct, charx * len(punct))
        return punct_mask


"""PUNCT: !\\"#$%&'()*+,/:;<=>?@[\\]^`{|}~"""

"""
PROBABLY A BAD IDEA
"""

# class AmiLogger:
#     """wrapper for logger to limit or condense voluminous output
#
#     adds a dictionary of counts for each log level
#     """
#
#     def __init__(self, loggerx, initial=10, routine=100):
#         """create from an existing logger"""
#         self.logger = loggerx
#         self.func_dict = {
#             "debug": self.logger.debug,
#             "info": self.logger.info,
#             "warning": self.logger.warning,
#             "error": self.logger.error,
#
#         }
#         self.initial = initial
#         self.routine = routine
#         self.count = {
#         }
#         self.reset_counts()
#
#     def reset_counts(self):
#         for level in self.func_dict.keys():
#             self.count[level] = 0
#
#     # these will be called instead of logger
#     def debug(self, msg):
#         self._print_count(msg, "debug")
#
#     def info(self, msg):
#         self._print_count(msg, "info")
#
#     def warning(self, msg):
#         self._print_count(msg, "warning")
#
#     def error(self, msg):
#         self._print_count(msg, "error")
#
#     # =======
#
#     def _print_count(self, msg, level):
#         """called by the wrapper"""
#         logger_func = self.func_dict[level]
#         if level not in self.count:
#             self.count[level] = 0
#         if self.count[level] <= self.initial or self.count[level] % self.routine == 1:
#             logger_func(f"{self.count[level]}: {msg}")
#         else:
#             logger.debug(".", end="")
#         self.count[level] += 1
#
#     @classmethod
#     def create_named_logger(cls, file):
#         return logging.getLogger(os.path.basename(file))


GENERATE = "_GENERATE"  # should we generate IDREF?


class EnhancedRegex:
    """parses regex and uses them to transform"""

    STYLES = [
        (".class0", [("color", "red;")]),
        (".class1", [("background", "#ccccff;")]),
        (".class2", [("color", "#00cc00;")]),
    ]

    # class EnhancedRegex:

    def __init__(self, regex=None, components=None):
        self.regex = regex
        self.components = components
        if regex and not components:
            self.components = self.make_components_from_regex(self.regex)
        if components and not regex:
            raise NotImplemented("this approach (regex from compponents) was abandoned")
            # self.regex = self.make_regex_with_capture_groups(self.components)

    # class EnhancedRegex:
    def make_components_from_regex(self, regex):
        """splits regex into components
        regex must contain alternating sequence of capture/non_capture groups"""
        split = "(\\([^\\)]*\\))"
        self.components = None
        if regex is not None:
            # logger.debug(f"regex {regex}")
            self.components = re.split(split, regex)
        return self.components

    # class EnhancedRegex:

    def make_id(self, target):
        """assumes self.regex or self.components has been loaded
        """
        return None if not self.regex else self.make_id_with_regex(self.regex, target)

    def make_id_with_regex(self, regex, target, sep="_"):
        """makes ids from strings using list of sub-regexes
        :param regex: regex with cpature groups ...
        :param target: string to generate id from
        :param sep: separator
        see make_regex_with_capture_groups
        at present separator is "_" ; TODO expand this
        """
        if regex is None or target is None:
            return None
        components = self.make_components_from_regex(regex)
        id = self.make_id_with_regex_components(components, target)
        return id

    # class EnhancedRegex:

    def make_id_with_regex_components(self, components, target, sep="_"):
        """makes ids from strings using list of sub-regexes
        :param components: list of regex components of form (name, regex) separator ...
        :param target: string to generate id from
        :param sep: separator
        see make_regex_with_capture_groups
        at present separator is "_" ; TODO expand this
        """

        def make_list_of_names_in_capture_groups(capturegroup_name, components, debug=False):
            names = []
            for comp in components:
                # extract capture_group name from regex
                match1 = re.match(capturegroup_name, comp)
                if match1:
                    names.append(match1.group(1))
            return names

        if self.regex is None:
            return None
        capturegroup_name_regex = ".*\\(\\?P<(.*)>.*"

        names = make_list_of_names_in_capture_groups(capturegroup_name_regex, components)
        match = re.match(self.regex, target)
        # logger.debug(f">>match {match}")
        # SEP = "_"
        id = None
        if match:
            id = ""
            for i, name in enumerate(names):
                if match.group(name) is None:
                    logger.debug(f"cannot match group {name}")
                    continue
                if i > 0:
                    id += sep
                id += match.group(name)

        return id

    # class EnhancedRegex:

    # Abandoned!
    def make_regex_with_capture_groups(self, components):
        """make regex with capture groups
        takes components list of alternating strings and tuples (of form name, regex)
        :param components: list [str] (tuple) str (tuple) str (tuple) ... [str]
        from
        components = ["", ("decision", "\\d+"), "/", ("type", "CP|CMA|CMP"), "\\.", ("session", "\\d+"), ""]
        :return: a regex of form:
        (?P<decision>\\d+)/(?P<type>CP|CMA|CMP)\\.(?P<session>\\d+)
        NOT WORKING
        """
        last_t = None
        regex = ""
        for component in components:
            # t = type(component)
            # if isinstance(component, str) and (last_t is None or isinstance(last_t, tuple)):
            #     regex += component
            # elif isinstance(component, tuple) and (last_t is None or isinstance(last_t, str)):
            #     regex += f"(?P<{component[0]}>{component[1]})"
            # else:
            #     logger.debug(f"bad component [{component}] in {components}")
            last_t = component
        return regex

    # class EnhancedRegex:

    def make_components_from_regex(self, regex):
        """splits regex into components
        regex must contain alternating sequence of capture/non_capture groups"""
        split = "(\\([^\\)]*\\))"
        raw_comps = None
        if regex is not None:
            # print(f"...regex {regex}")
            raw_comps = re.split(split, str(regex))
        return raw_comps

    # class EnhancedRegex:

    def get_href(self, href, text=None):
        """generates href/idref from matched string
        """

        if href == GENERATE:
            idref = self.make_id_with_regex(self.regex, text)
            return idref
        else:
            return href


class TextUtil:

    @classmethod
    def replace_chars(cls, text, unwanted_chars, replacement) -> str:
        """replaces all chars in unwanted chars with wanted_char

        :param text: source text
        :param unwanted_chars: string or list of unwanted characters
        :param replacement: replacement character
        :returns modified string
        """
        text0 = ''.join(
            [c if c not in unwanted_chars else replacement for c in text])
        return text0


# sub/Super

class SScript(Enum):
    SUB = 1
    SUP = 2
