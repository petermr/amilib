"""tests in a single path
This is until I or someone else can figure out relative imports
"""
import os
import random
import unittest
from glob import glob
from pathlib import Path

from amilib.util import Util

from test.resources import Resources

skip_config_test = True


# TODO needs local config file
# @unittest.skipIf(skip_config_test, "needs local config")

logger = Util.get_logger(__name__)

class AmiAnyTest(unittest.TestCase):
    # for marking and skipping unittests
    # skipUnless
    ADMIN = True  # check that low-level files, tools, etc. work
    CMD = True   # test runs the commandline
    DEBUG = True   # test runs the commandline
    LONG = True   # test runs for a long time
    NET = True    # test requires Internet
    OLD = True    # test probably out of data
    VERYLONG = False   # test runs for a long time
    # skipIf
    NYI = True    # test not yet implemented
    USER = True   # user-facing test
    BUG = True    # skip BUGs

    PMR_NAME ="pm286"
    IS_PMR = (PMR_NAME == Util.get_username())
    # outputs for tests

    # temporary output data (can be deleted after tests)
    TEMP_DIR = Path(Resources.TEST_RESOURCES_DIR.parent.parent, "temp")
    TEMP_DIR.mkdir(exist_ok=True, parents=True)
    assert TEMP_DIR.is_dir(), f"file exists {TEMP_DIR}"

    TEMP_HTML_DIR = Path(TEMP_DIR, "html")
    TEMP_HTML_DIR.mkdir(exist_ok=True, parents=True)
    TEMP_HTML_IPCC = Path(TEMP_DIR, "html", "ar6")
    TEMP_HTML_IPCC.mkdir(exist_ok=True, parents=True)
    TEMP_HTML_IPCC_CHAP04 = Path(TEMP_HTML_IPCC, "chapter04")
    TEMP_HTML_IPCC_CHAP04.mkdir(exist_ok=True, parents=True)
    TEMP_HTML_IPCC_CHAP06 = Path(TEMP_HTML_IPCC, "chapter06")
    TEMP_HTML_IPCC_CHAP06.mkdir(exist_ok=True, parents=True)

    TEMP_PDFS_DIR = Path(TEMP_DIR, "pdf")
    TEMP_PDFS_DIR.mkdir(exist_ok=True, parents=True)
    TEMP_PDF_IPCC = Path(TEMP_PDFS_DIR, "ar6")
    TEMP_PDF_IPCC.mkdir(exist_ok=True, parents=True)
    TEMP_PDF_IPCC_CHAP06 = Path(TEMP_PDF_IPCC, "chapter06")
    TEMP_PDF_IPCC_CHAP06.mkdir(exist_ok=True, parents=True)

    CLIMATE_10_HTML_TEMP_DIR = Path(TEMP_DIR, "climate10", "html")

    def setUp(self) -> None:
        # if len(sys.argv) == 0:
        #     sys.argv = ["ami"]
        # self.argv_copy = list(sys.argv)
        pass

    def tearDown(self) -> None:
        pass

    # used to control long tests. Crude but robust (other markers are more complex)
    # not sure how to control it with editing
    def run_long(nmax=10):
        n = random.randint(1, nmax)
        return n == 1



