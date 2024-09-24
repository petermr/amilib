import ast
import collections
import json
import logging
from pathlib import Path
import pandas as pd

from amilib.ami_html import HtmlUtil, HtmlLib
from amilib.ami_util import AmiJson
from amilib.ami_corpus import AmiCorpus
from amilib.file_lib import FileLib
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)
class AmiBibliographyTest(AmiAnyTest):
    """

    """
    @classmethod
    def convert_csv_to_bib(cls):
        """

        """

def df_toupper(s):
    return f"<a href='{s}`>s</a>"

def df_truncate(s):
    return f"{s[:200]}..."

class DictParser(ast.NodeVisitor):
    def visit_Dict(self,node):
        keys,values = node.keys,node.values
        keys = [n.s for n in node.keys]
        values = [n.s for n in node.values]
        self.od = collections.OrderedDict(zip(keys, values))

def df_unpack_dict(json_string):
    """
    this is messy. I think we need a recursive descent parser
    """
    print(f"DIKT {json_string}")
    try:
        # dikt = json.loads(s)
    # or
        # decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
        # dikt = decoder.decode(json_string)
    # or
        dp = DictParser()
        dp.visit(ast.parse(json_string))
        dikt = dp.od
    except Exception as e:
        print(f"EXC {e}")
        return "None"
    print(f"dikt {type(dikt)} {dikt.keys()}")
    title = dikt.get("journal").get("title")
    return title

class PygetpapersTest(AmiAnyTest):
    """
    manage output from pygetpapers
    """

    def test_edit_csv(self):
        """
        reade *.csv created by pygetpapers
        not working because of lack of OrderedDict parser
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "csv", "frictionless", "europe_pmc.csv")
        outdir = Path(Resources.TEMP_DIR, "csv", "frictionless")
        outdir.mkdir(parents=True, exist_ok=True)
        outfile = Path(outdir, "europe_pmc.csv")
        outfile_h = Path(outdir, "europe_pmc.html")
        assert infile.exists()
        df = pd.read_csv(infile)

        # idx = pd.Index(['a', 'b', 'c'])
        # idx.drop(['a'])
        # print(f"\n{df}")
        keys = df.keys()
        key_list = keys.to_list()
        # print(f"type keys {type(keys)} {key_list}")
        ABS_TEXT = 'abstractText'
        PMCID = 'pmcid'
        assert ['Unnamed: 0', 'id', 'source', 'pmid', PMCID, 'fullTextIdList', 'doi',
       'title', 'authorString', 'authorList', 'authorIdList',
       'dataLinksTagsList', 'journalInfo', 'pubYear', 'pageInfo',
                ABS_TEXT, 'affiliation', 'publicationStatus', 'language',
       'pubModel', 'pubTypeList', 'keywordList', 'fullTextUrlList',
       'isOpenAccess', 'inEPMC', 'inPMC', 'hasPDF', 'hasBook', 'hasSuppl',
       'citedByCount', 'hasData', 'hasReferences', 'hasTextMinedTerms',
       'hasDbCrossReferences', 'hasLabsLinks', 'license', 'hasEvaluations',
       'authMan', 'epmcAuthMan', 'nihAuthMan', 'hasTMAccessionNumbers',
       'tmAccessionTypeList', 'dateOfCreation', 'firstIndexDate',
       'fullTextReceivedDate', 'dateOfRevision', 'electronicPublicationDate',
                'firstPublicationDate', 'grantsList', 'commentCorrectionList',
                'meshHeadingList', 'subsetList', 'dateOfCompletion', 'chemicalList',
                'investigatorList', 'embargoDate', 'manuscriptId'] == keys.to_list()
        # print(f"df\n{df}")
        # df2 = df.drop(columns=['id', 'source', 'pmid', 'pmcid'])
        df[PMCID] = df[PMCID].apply(df_toupper)
        df[ABS_TEXT] = df[ABS_TEXT].apply(df_truncate)
        JOURNAL_INFO = "journalInfo"
        df[JOURNAL_INFO] = df[JOURNAL_INFO].apply(df_unpack_dict)
        df2 = df[["pmcid", "doi", "title", "authorString", JOURNAL_INFO, "pubYear", ABS_TEXT]]
        # print(f"df2\n{df2}")

        with open(outfile, "w") as f:
            f.write(df2.to_csv())
        with open(outfile_h, "w") as f:
            f.write(df2.to_html(escape="False"))

    def test_make_html_table_from_json(self):
        """
        assume JSON is an implicit table
        """
        effective_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)

        project_name = "frictionless"
        infile = Path(Resources.TEST_RESOURCES_DIR, "json", project_name, "eupmc_results.json")
        outdir = Path(Resources.TEMP_DIR, "json", project_name)
        wanted_keys = ["pmcid", "doi", "title", "authorString", "journalInfo.journal.title", "abstractText"]
        outdir.mkdir(parents=True, exist_ok=True)
        outfile_h = Path(outdir, "europe_pmc.html")
        datatables = True

        self.read_json_create_write_html_table(infile, outfile_h, wanted_keys, datatables=datatables, table_id=None)
        logger.setLevel(effective_level)

    @classmethod
    def read_json_create_write_html_table(
            cls, infile, outfile_h, wanted_keys,
            styles=None, datatables=None, table_id=None):
        """
        read pygetpapers output, select columns and create HTML table
        :param infile: eumpc_results from pygetpapers
        :param outfile_h: HTML table to write
        :param wanted_keys: column headings to select
        :return:html table
        """
        if styles is None:
            styles=["td {border:solid 1px black;}"]
        if table_id is None:
            table_id = "my_table"
            # raise ValueError("must give table_id")

        assert infile.exists()
        with open(infile, "r") as f:
            jsonx = json.load(f)
        # look for all papers
        papers = jsonx.get("papers")
        assert papers is not None, f"cannot find papers"
        # specific keys we want
        dict_by_id = AmiJson.create_json_table(papers, wanted_keys)
        html_table = HtmlLib.create_html_table(
            dict_by_id, transform_dict=AmiCorpus.EUPMC_TRANSFORM,
            styles=styles, datatables=datatables, table_id=table_id
        )
        HtmlUtil.write_html_elem(html_table, outfile_h, debug=True)



