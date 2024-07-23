import csv
from pathlib import Path

import pandas as pd

from amilib.api import EPMCBib
from amilib.util import Util
from amilib.xml_lib import HtmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest


class AmiBibliographyTest(AmiAnyTest):
    """

    """
    @classmethod
    def test_convert_empc_csv_to_bib(cls):
        """
        read a set of EMPC metadata is CSV form and convert to journal references
        """
        infile = Path(Resources.TEST_RESOURCES_DIR, "bib", "europe_pmc.csv")
        assert infile.exists()
        df = pd.read_csv(infile)

        bib_html = EPMCBib.make_bib_html(infile)
        outfile = Path(Resources.TEMP_DIR, "bib", "epmc.html")
        HtmlLib.write_html_file(bib_html, outfile, debug=True)

