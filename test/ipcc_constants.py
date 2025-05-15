from pathlib import Path

from amilib.file_lib import FileLib
from test.resources import Resources

UNFCCC_DIR = Path(Resources.TEST_RESOURCES_DIR, "unfccc")
UNFCCC_TEMP_DIR = Path(Resources.TEMP_DIR, "unfccc")
UNFCCC_TEMP_DOC_DIR = Path(UNFCCC_TEMP_DIR, "unfcccdocuments1")
#
MAXPDF = 3
#
# OMIT_LONG = True  # omit long tests
#
# #
#
IPCC_TOP = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content")
# assert IPCC_TOP.exists(), f"{IPCC_TOP} should exist"
#
QUERIES_DIR = Path(Resources.TEMP_DIR, "queries")
# assert QUERIES_DIR.exists(), f"{QUERIES_DIR} should exist"
#
IPCC_DICT = {
    "_IPCC_REPORTS": IPCC_TOP,
    "_IPCC_QUERIES": QUERIES_DIR,
}
#
CLEANED_CONTENT = 'cleaned_content'
SYR = 'syr'
SYR_LR = 'longer-report'
IPCC_DIR = 'ipcc'
#

OUT_DIR_TOP = Path(FileLib.get_home(), "workspace")

# input
IPCC_URL = "https://www.ipcc.ch/"
AR6_URL = IPCC_URL + "report/ar6/"
SYR_URL = AR6_URL + "syr/"
WG1_URL = AR6_URL + "wg1/"
WG2_URL = AR6_URL + "wg2/"
WG3_URL = AR6_URL + "wg3/"

# from AmiClimate
DE = "de"
IP_WG1 = "wg1"
GATSBY = "gatsby"
GATSBY_RAW = "gatsby_raw"
DE_GATSBY = "de_gatsby"
WORDPRESS_RAW = "wordpress_raw"
WORDPRESS = "wordpress"
DE_WORDPRESS = "de_wordpress"

HTML_WITH_IDS = "html_with_ids"
HTML_WITH_IDS_HTML = "html_with_ids.html"
ID_LIST = "id_list"
PARA_LIST = "para_list"

LR = "longer-report"
SPM = "summary-for-policymakers"
TS = "technical-summary"
ANN_IDX = "annexes-and-index"
