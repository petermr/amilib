# test util

import csv
import logging
import re
import shutil
import sys
import unittest
from json import JSONDecodeError
from pathlib import Path

from amilib.ami_util import AmiJson
from amilib.file_lib import FileLib
from amilib.util import EnhancedRegex
from amilib.util import Util, GithubDownloader, TextUtil
from amilib.ami_args import ArgParseBuilder, AmiArgParser, AmiArgParseException
from amilib.xml_lib import Templater

from test.resources import Resources
from test.test_all import AmiAnyTest

# local


logger = Util.get_logger(__name__)

class Util0Test(AmiAnyTest):
    # def __init__(self):
    sys_argv_save = None

    # @classmethod
    # def setUp(cls):
    #     """save args as they will be edited"""
    #     cls.sys_argv_save = sys.argv
    #
    # @classmethod
    # def tearDown(cls):
    #     """restore args"""
    #     sys.argv = cls.sys_argv_save

    @classmethod
    @unittest.skip("not working properly, I think some tests change the args...")
    # TODO fix args - some  tests change the args
    def test_add_argstr(cls):
        # this is a hack as normally there is only one element
        # sys.argv = sys.argv[1:]
        # assert sys.argv[1:] == []
        cmd = "--help foo bar plinge"
        Util.add_sys_argv_str(cmd)
        assert sys.argv[1:] == ["--help", "foo", "bar", "plinge"]

    @classmethod
    @unittest.skip("not working properly")
    # TODO fix args
    def test_add_args(cls):
        # this is a hack as normally there is only one element
        sys.argv = sys.argv[1:]
        # assert sys.argv[1:] == []
        args = ["--help", "foox", "barx", "plingex"]
        Util.add_sys_argv(args)
        assert sys.argv[1:] == ["--help", "foox", "barx", "plingex"]

    @classmethod
    def test_copy_anything(cls):
        src = Resources.TEST_CLIMATE_10_SVG_DIR
        dst = Path(AmiAnyTest.TEMP_DIR, "tempzz")
        if dst.exists():
            shutil.rmtree(dst)
        FileLib.copyanything(src, dst)
        assert Path(dst).exists()

    def test_create_name_value(self):
        """tests parsing of PyAMI flags
        """
        name, value = Util.create_name_value("foo=bar")
        assert name, value == ("foo", "bar")
        name, value = Util.create_name_value("foo")
        assert name, value == ("foo", True)
        try:
            arg = "foo=bar=plugh"
            Util.create_name_value(arg)
            raise ValueError(f"failed to trap {arg}")
        except ValueError as ve:
            assert str(ve == "too many delimiters in {arg}")
        try:
            arg = "foo bar"
            _, v = Util.create_name_value(arg)
            raise ValueError(f"failed to trap {arg}")
        except ValueError as ve:
            assert str(ve) == "arg [foo bar] may not contain whitespace"

        Util.create_name_value("foo/bar")
        assert name, value == "foo/bar"

        Util.create_name_value("foo/bar", delim="/")
        assert name, value == ("foo", "bar")

        assert Util.create_name_value("") is None

        arg = "foo bar"
        try:
            _, v = Util.create_name_value(arg, delim=" ")
            raise ValueError(f"failed to trap {arg}")
        except ValueError as ve:
            assert str(ve) == f"arg [{arg}] may not contain whitespace"

    def test_read_csv(self):
        """
        use Python csv to select column values
        Reads compound_enzyme.csv into CSV DictReader and checks values in first 3 rows
        with column names "NAME" and "TYPE"
        """
        csv_file = Path(Resources.TEST_RESOURCES_DIR, "eoCompound", "compound_enzyme.csv")
        assert csv_file.exists(), f"{csv_file} should exist"
        expected_row_values = [["isopentenyl diphosphate", "COMPOUND"],
                               ["dimethylallyl diphosphate", "COMPOUND"],
                               ["hemiterpene", "COMPOUND"]]
        with open(str(csv_file), newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for i, row in enumerate(reader):
                if i < 3:
                    assert row['NAME'] == expected_row_values[i][0]
                    assert row['TYPE'] == expected_row_values[i][1]

    def test_select_csv_field_by_type(self):
        """select value in column of csv file by value of defining column
        """
        csv_file = Path(Resources.TEST_RESOURCES_DIR, "eoCompound", "compound_enzyme.csv")
        assert csv_file.exists(), f"{csv_file} should exist"
        selector_column = "TYPE"
        column_with_values = "NAME"
        selector_value = "COMPOUND"

        values = Util.extract_csv_fields(csv_file, column_with_values, selector_column, selector_value)
        assert len(values) == 89
        assert values[:3] == ['isopentenyl diphosphate', 'dimethylallyl diphosphate', 'hemiterpene']

        selector_value = "ENZYME"
        values = Util.extract_csv_fields(csv_file, column_with_values, selector_column, selector_value)
        assert len(values) == 92
        assert values[:3] == ['isomerase', 'GPP synthase', 'FPP synthase']

    def test_create_arg_parse(self):
        arg_parse_file = Path(Resources.TEST_RESOURCES_DIR, "arg_parse.json")
        arg_parse_builder = ArgParseBuilder()
        arg_dict = arg_parse_builder.create_arg_parse(arg_dict_file=arg_parse_file)

    def test_range_list_contains_int(self):
        """does a range or range list contain an int"""
        # single
        rangex = range(1, 3)
        assert not Util.range_list_contains_int(0, rangex)
        assert Util.range_list_contains_int(1, rangex)
        assert not Util.range_list_contains_int(3, rangex)
        # list
        range_list = [range(1, 3), range(5, 9)]
        assert not Util.range_list_contains_int(0, range_list)
        assert Util.range_list_contains_int(1, range_list)
        assert not Util.range_list_contains_int(3, range_list)
        assert not Util.range_list_contains_int(4, range_list)
        assert Util.range_list_contains_int(5, range_list)
        assert not Util.range_list_contains_int(9, range_list)
        assert not Util.range_list_contains_int(10, range_list)
        # None
        range_list = None
        assert not Util.range_list_contains_int(0, range_list)
        range_list = range(1, 3)
        assert not Util.range_list_contains_int(None, range_list)

    def test_get_file_from_url(self):
        url = None
        assert Util.get_file_from_url(url) is None
        url = "https://foo.bar/plugh/bloop.xml"
        assert Util.get_file_from_url(url) == "bloop.xml"

    @unittest.skip("NYI")
    def test_make_id_from_match_and_idgen(self):
        """idgen is of the form <grouo>some text<group>
        where groups correspond to named capture groups in regex
        """
        idgen = "12/CMA.34"
        components = ["", ("decision", "\\d+"), "/", ("type", "CP|CMA|CMP"), "\\.", ("session", "\\d+"), ""]
        enhanced_regex = EnhancedRegex(components=components)
        id = enhanced_regex.make_id(idgen)
        assert id == "12_CMA_34"

    # ABANDONED
    # def test_make_regex_with_capture_groups(self):
    #     """idgen is of the form <grouo>some text<group>
    #     where groups correspond to named capture groups in regex
    #     """
    #     enhanced_regex = EnhancedRegex()
    #     components = ["", ("decision", "\d+"), "/", ("type", "CP|CMA|CMP"), "\.", ("session", "\d+"), ""]
    #     regex = enhanced_regex.make_regex_with_capture_groups(components)
    #     assert regex == '(?P<decision>\\d+)/(?P<type>CP|CMA|CMP)\\.(?P<session>\\d+)'

    def test_make_components_from_regex(self):
        """splits regex with capture groups into its components
        """
        regex = '(?P<decision>\\d+)/(?P<type>CP|CMA|CMP)\\.(?P<session>\\d+)'
        re_parser = EnhancedRegex(regex=regex)
        components = re_parser.make_components_from_regex(regex)
        assert len(components) == 7
        assert components[1] == '(?P<decision>\\d+)'
        assert components[3] == '(?P<type>CP|CMA|CMP)'
        unittest.TestCase().assertListEqual(components,
                                            ['', '(?P<decision>\\d+)', '/', '(?P<type>CP|CMA|CMP)', '\\.',
                                             '(?P<session>\\d+)', ''])

    def test_get_username(self):
        """gets username
        """
        username = Util.get_username()
        if AmiAnyTest.IS_PMR:
            assert username == "pm286"

    def test_parse_quoted_list(self):
        quoted_list = '["a", "b"]'
        parsed_list = TextUtil.convert_quoted_list_to_list(quoted_list)
        assert type(parsed_list) is list
        assert len(parsed_list) == 2
        assert parsed_list[0] == "a"

        quoted_list = '["a", "b", [1 ,2]]'
        parsed_list = TextUtil.convert_quoted_list_to_list(quoted_list)
        assert type(parsed_list) is list
        assert len(parsed_list) == 3
        assert parsed_list[2] == [1,2]

    def test_parse_double_quoted_list(self):
        """
        single quotes fail in json, but we code round it
        """
        quoted_list = "['a', 'b']"
        parsed_list = TextUtil.convert_quoted_list_to_list(quoted_list)
        assert parsed_list == ["a", "b"]




class GithubDownloaderTest(AmiAnyTest):
    # def __init__(self):
    #     pass

    @unittest.skip("VERY LONG, DOWNLOADS")
    def test_explore_main_page(self):
        owner = "petermr"
        repo = "CEVOpen"
        downloader = GithubDownloader(owner=owner, repo=repo, max_level=1)
        page = None
        downloader.make_get_main_url()
        logger.info(f"main page {downloader.main_url}")
        url = downloader.main_url
        if not url:
            print(f"no page {owner}/{repo}")
            return None

        downloader.load_page(url, level=0)


class AmiArgParserTest(AmiAnyTest):

    def test_ami_arg_parse(self):
        """
        test subclassing of argParse
        """
        ami_argparse = AmiArgParser()
        ami_argparse.add_argument("--flt", type=float, nargs=1, help="a float", default=80)
        ami_argparse.add_argument("--str", type=str, nargs=1, help="a string")

        # this works
        arg_dict = ami_argparse.parse_args(["--flt", "3.2"])
        logger.debug(f"arg_dict1 {arg_dict}")
        # this fails
        try:
            arg_dict = ami_argparse.parse_args(["--flt", "3.2", "str"])
        except AmiArgParseException as se:
            print(f"arg parse error {se} line: {se.__traceback__.tb_lineno}")
        except Exception as e:
            print(f" error {e}")

        arg_dict = ami_argparse.parse_args(["--flt", "99.2"])
        logger.debug(f"arg_dict2 {arg_dict}")


class TemplateTest(AmiAnyTest):

    def test_id_templates(self):
        """Splits files at Decisions"""
        """requires previous test to have been run"""

        template_values = {
            'DecRes': 'Decision',
            'decision': 1,
            'type': "CMA",
            'session': "3",
        }

        template = "{DecRes}_{decision}_{type}_{session}"
        regex = "(?P<DecRes>Decision|Resolution)\\s(?P<decision>\\d+)/(?P<type>CMA|CMP|CP)\\.(?P<session>\\d+)"
        ss = ["Decision 12/CMP.5", "Decision 10/CP.17", "Decision 2/CMA.2", "Decision 4/CCC.9"]
        matched_templates = Templater.get_matched_templates(regex, ss, template)
        assert matched_templates == ['Decision_12_CMP_5', 'Decision_10_CP_17', 'Decision_2_CMA_2', None]

# class UtilTests:
#     def test_dict_read(self):
#         file = "section_templates.json"
#         return Util.read_pydict_from_json(file)

class CommandlineTest:

    def test_command(self):
        command = "--help"

class LoggingTest(AmiAnyTest):
    import logging

    def test_logger(self):
        logger = Util.get_logger(__name__)

        logger.info("Server started listening on port 8080")
        logger.warning(
            "Disk space on drive '/var/log' is running low. Consider freeing up space"
        )
        logger.info("")

        try:
            raise Exception("Failed to connect to database: 'my_db'")
        except Exception as e:
            logger.info(f"=========start Exception============")
            # exc_info=True ensures that a Traceback is included
            FileLib.log_exception(e, logger)
            logger.info(f"=========end Exception============")

        print(f"FINISHED")

class AmiJsonTest(AmiAnyTest):
    """
    tricky JSON stuff (e.g. nested dicts)
    """

    def test_nested_dicts(self):
        """
        access values in nested dict by dot-separated strings
        """
        dikt = {
            "key1" : "value1",
            "key2" :
                {
                    "subkey1": "subvalue21",
                    "subkey2": "subvalue22",

                },
            "key3":
                {
                    "subkey1":
                        {
                            "subsubkey1": "subsubvalue311",
                            "subsubkey2": "subsubvalue312",
                        },
                }

        }
        assert "value1" == AmiJson.read_nested_dicts(dikt, "key1")
        assert "subvalue21" == AmiJson.read_nested_dicts(dikt, "key2.subkey1")
        assert "subsubvalue312" == AmiJson.read_nested_dicts(dikt, "key3.subkey1.subsubkey2")

