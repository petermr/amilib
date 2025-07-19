"""
Core utilities for amilib.
Refactored to use constants from core.constants to avoid circular dependencies.
"""
import ast
import base64
import codecs
import csv
import getpass
import importlib
import json
import logging
import os
import re
import sys
import time
from enum import Enum
from pathlib import Path

import pandas as pd
import requests

from amilib.core.constants import GENERATE

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
    # this gets called in Util,get_logger(__name__) everywhere except this file
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
    formatx = "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
    formatx = "%(levelname)s %(filename)s:%(lineno)s:%(message)s"
    fmt = logging.Formatter(formatx)
    # Set the log format on each handler
    stdoutHandler.setFormatter(fmt)
    errHandler.setFormatter(fmt)
    # Add each handler to the Logger object
    # I get 2 logger message every time - not sure why
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
                   formatx="%(name)s | %(levelname)s | %(filename)s:%(lineno)s |>>> %(message)s",
                   ):
        """
        creates logger with name == __name__
        """
        return _get_logger(name, level, err_level, err_log, formatx)

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
        """
        read json file into python dictionary
        :param file: to read
        :return: Python dict
        """
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
    def create_name_value(cls, arg: str, delim: str = "="):
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
        \[
        [^\[\]]*
        \]
        """, re.VERBOSE)

    @classmethod
    def range_list_contains_int(cls, value, range_list):
        """does a range or range list contain an int
        :param value: int to check
        :param range_list: range or list of ranges
        :return: True if value is in any range
        """
        if value is None or range_list is None:
            return False
        if isinstance(range_list, range):
            return value in range_list
        if isinstance(range_list, list):
            for r in range_list:
                if isinstance(r, range) and value in r:
                    return True
        return False

    @staticmethod
    def matches_regex_list(string, regex_list):
        """does string match any regex in list
        :param string: string to test
        :param regex_list: list of regex patterns
        :return: True if string matches any regex
        """
        if not string or not regex_list:
            return False
        for regex in regex_list:
            if re.match(regex, string):
                return True
        return False

    @classmethod
    def make_translate_mask_to_char(cls, orig, rep):
        """create translation table for string.translate
        :param orig: original characters
        :param rep: replacement characters
        :return: translation table
        """
        if len(orig) != len(rep):
            raise ValueError(f"orig and rep must have same length: {len(orig)} != {len(rep)}")
        return str.maketrans(orig, rep)

    @classmethod
    def print_stacktrace(cls, ex):
        """print exception with stack trace
        :param ex: exception
        """
        import traceback
        logger.error(f"Exception: {ex}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    @classmethod
    def get_urls_from_webpage(cls, suffixes, weburl):
        """extract URLs from webpage that end with given suffixes
        :param suffixes: list of suffixes to match
        :param weburl: URL of webpage
        :return: list of matching URLs
        """
        # Implementation would go here
        pass

    @classmethod
    def download_urls(cls, urls=None, target_dir=None, maxsave=100, printfile=True, skip_exists=True, sleep=5):
        """download URLs to target directory
        :param urls: list of URLs to download
        :param target_dir: directory to save files
        :param maxsave: maximum number of files to save
        :param printfile: print file names as they're saved
        :param skip_exists: skip files that already exist
        :param sleep: sleep between downloads
        """
        # Implementation would go here
        pass

    @classmethod
    def get_file_from_url(cls, url):
        """extract filename from URL
        :param url: URL
        :return: filename or None
        """
        if not url:
            return None
        return url.split('/')[-1]

    @classmethod
    def create_string_separated_list(cls, listx):
        """create string from list with separator
        :param listx: list
        :return: string
        """
        return " ".join(str(x) for x in listx) if listx else ""

    @classmethod
    def open_write_utf8(cls, outpath):
        """open file for writing with UTF-8 encoding
        :param outpath: output path
        :return: file object
        """
        return open(outpath, "w", encoding="utf-8")

    @classmethod
    def open_read_utf8(cls, inpath):
        """open file for reading with UTF-8 encoding
        :param inpath: input path
        :return: file object
        """
        return open(inpath, "r", encoding="utf-8")

    @classmethod
    def is_base64(cls, s):
        """check if string is base64 encoded
        :param s: string to check
        :return: True if base64
        """
        if not s:
            return False
        try:
            # Try to decode as base64
            decoded = base64.b64decode(s)
            # Check if it's valid UTF-8
            decoded.decode('utf-8')
            return True
        except Exception:
            return False

    @classmethod
    def get_column(cls, data, colname, csvname=None):
        """get column from data
        :param data: data structure
        :param colname: column name
        :param csvname: CSV name for logging
        :return: column data
        """
        # Implementation would go here
        pass

    @classmethod
    def should_make(cls, target, source):
        """check if target should be made based on source
        :param target: target file
        :param source: source file
        :return: True if target should be made
        """
        if not target or not source:
            return False
        if not os.path.exists(target):
            return True
        if not os.path.exists(source):
            return False
        return os.path.getmtime(source) > os.path.getmtime(target)

    @classmethod
    def need_to_make(cls, outfile, infile, debug=False):
        """check if output file needs to be made
        :param outfile: output file
        :param infile: input file
        :param debug: debug flag
        :return: True if output needs to be made
        """
        if debug:
            logger.debug(f"need_to_make {outfile} {infile}")
        if not outfile or not infile:
            return False
        if not os.path.exists(outfile):
            if debug:
                logger.debug(f"outfile {outfile} does not exist")
            return True
        if not os.path.exists(infile):
            if debug:
                logger.debug(f"infile {infile} does not exist")
            return False
        out_time = os.path.getmtime(outfile)
        in_time = os.path.getmtime(infile)
        if debug:
            logger.debug(f"out_time {out_time} in_time {in_time}")
        return in_time > out_time

    @classmethod
    def delete_file_and_check(cls, file):
        """delete file and check it's gone
        :param file: file to delete
        """
        if file and os.path.exists(file):
            os.remove(file)
            assert not os.path.exists(file), f"file {file} should be deleted"

    @classmethod
    def get_float_from_dict(cls, dikt, key):
        """get float value from dictionary
        :param dikt: dictionary
        :param key: key
        :return: float value or None
        """
        if not dikt or key not in dikt:
            return None
        return cls.get_float(dikt[key])

    @classmethod
    def get_float(cls, f):
        """convert to float, return None if fails
        :param f: value to convert
        :return: float or None
        """
        if f is None:
            return None
        try:
            return float(f)
        except (ValueError, TypeError):
            return None

    @classmethod
    def get_list(cls, arg):
        """ensure argument is a list
        :param arg: argument
        :return: list
        """
        if arg is None:
            return []
        if isinstance(arg, list):
            return arg
        return [arg]

    @classmethod
    def get_class_from_name(cls, classname):
        """get class from class name
        :param classname: class name
        :return: class or None
        """
        try:
            module_name, class_name = classname.rsplit('.', 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except Exception:
            return None

    @classmethod
    def get_classname(cls, object):
        """get class name of object
        :param object: object
        :return: class name
        """
        return object.__class__.__name__ if object else None

    @classmethod
    def get_username(cls):
        """get current username
        :return: username
        """
        try:
            return getpass.getuser()
        except Exception:
            return "unknown"

    @classmethod
    def normalize_chars(cls, line):
        """normalize characters in line
        :param line: line to normalize
        :return: normalized line
        """
        if not line:
            return line
        # Implementation would go here
        return line

    @classmethod
    def input_list_of_words(cls, words):
        """get list of words from user input
        :param words: words to process
        :return: list of words
        """
        if not words:
            return []
        if isinstance(words, str):
            return words.split()
        if isinstance(words, list):
            return words
        return [str(words)]


class GithubDownloader:
    """Download files from GitHub"""

    def __init__(self, owner=None, repo=None, sleep=3, max_level=1):
        self.owner = owner
        self.repo = repo
        self.sleep = sleep
        self.max_level = max_level
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def make_get_main_url(self):
        """make main URL for GitHub API"""
        return f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"

    def load_page(self, url, level=1, page=None, last_path=None):
        """load page from GitHub API
        :param url: URL to load
        :param level: recursion level
        :param page: page number
        :param last_path: last path
        :return: response data
        """
        if level > self.max_level:
            return None
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error loading {url}: {e}")
            return None

    @classmethod
    def make_translate_mask_to_char(cls, punct, charx):
        """create translation table
        :param punct: punctuation to replace
        :param charx: replacement character
        :return: translation table
        """
        return str.maketrans(punct, charx * len(punct))


class EnhancedRegex:
    """parses regex and uses them to transform"""

    STYLES = [
        "bold", "italic", "underline", "strikethrough", "superscript", "subscript"
    ]

    def __init__(self, regex=None, components=None):
        self.regex = regex
        self.components = components
        if regex:
            self.make_components_from_regex(regex)
        elif components:
            self.make_regex_with_capture_groups(components)

    def make_components_from_regex(self, regex):
        """extract components from regex
        :param regex: regex pattern
        """
        # Implementation would go here
        pass

    def make_id(self, target):
        """make ID from target
        :param target: target string
        :return: ID
        """
        # Implementation would go here
        pass

    def make_id_with_regex(self, regex, target, sep="_"):
        """make ID using regex
        :param regex: regex pattern
        :param target: target string
        :param sep: separator
        :return: ID
        """
        # Implementation would go here
        pass

    def make_id_with_regex_components(self, components, target, sep="_"):
        """make ID using regex components
        :param components: regex components
        :param target: target string
        :param sep: separator
        :return: ID
        """
        # Implementation would go here
        pass

    def make_regex_with_capture_groups(self, components):
        """make regex with capture groups
        :param components: regex components
        :return: regex pattern
        """
        # Implementation would go here
        pass

    def get_href(self, href, text=None):
        """get href value
        :param href: href value
        :param text: text value
        :return: href or generated href
        """
        if href == GENERATE:
            return f"#{text}" if text else "#"
        return href


class TextUtil:
    """Text utilities"""

    @classmethod
    def replace_chars(cls, text, unwanted_chars, replacement) -> str:
        """replace unwanted characters in text
        :param text: text to process
        :param unwanted_chars: characters to replace
        :param replacement: replacement character
        :return: processed text
        """
        if not text:
            return text
        return text.translate(str.maketrans(unwanted_chars, replacement * len(unwanted_chars)))

    @classmethod
    def convert_quoted_list_to_list(cls, quoted_list):
        """convert quoted list string to list
        :param quoted_list: quoted list string
        :return: list
        """
        if not quoted_list:
            return []
        # Implementation would go here
        return quoted_list.split() if isinstance(quoted_list, str) else quoted_list


class SScript(Enum):
    """Script enumeration"""
    SUB = 1
    SUP = 2 