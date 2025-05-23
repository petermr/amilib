from collections import Counter
from pathlib import Path
import lxml.etree as ET

from amilib.ami_html import HtmlLib
from amilib.amix import AmiLib
from amilib.file_lib import FileLib
from amilib.util import Util

from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)


class SearchTest(AmiAnyTest):
    pass

    def test_help(self):
        logger.debug("do nothing")
        args = ([
            "SEARCH",
            "--help",
        ])
        pyami = AmiLib()
        pyami.run_command(args)

    def test_annotate_file_with_phrases(self):
        """
        read inpath HTML, and use dict to match words and phrases
        """
        """
        TODO
        NOTE: annotates html but fails to use dictionary, so fails 
        to add hrefs to words.
        may be simple fix 
        look in def add_counts_from_outpath()
        the parameter `markup` should be set to Tru, not a dictionary name
        
        """
        stem = "carbon_cycle"
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")
        assert inpath.exists()
        dictpath = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", f"{stem}.xml")
        assert dictpath.exists()
        outpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.html")
        reportpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.report.html")
        args = ([
            "SEARCH",
            "--inpath", inpath,
            "--dict", dictpath,
            "--outpath", outpath,
            "--operation", "annotate", "counts",
            "--report", reportpath,

        ])
        pyami = AmiLib()
        pyami.run_command(args)
        logger.info(f"wrote outpath to {outpath}")
        assert outpath.exists(), f"{outpath} should exist"
        # ERROR REPORT is not written correctly
        logger.info(f"wrote report to {reportpath}")
        assert reportpath.exists()

        # count annotations
        logger.info(f"reading report from {reportpath}")
        title_counter = FileLib.read_counter_from_file(reportpath)
        logger.debug(f"title_counter {title_counter}")
        #  report file is wrong
        # assert title_counter == str([('carbon_dioxide_removal', 20), ('anthropogenic', 13), ('sequestration', 13),
        #                              ('bioenergy_with_carbon_capture_and_storage', 7), ('aerosols', 4),
        #                              ('tropospheric', 2), ('solar_radiation_modification', 1),
        #                              ('evapotranspiration', 1), ('permafrost', 1)])

    def test_annotate_file_with_phrases_from_dict(self):
        """
        read inpath HTML, remove styles, and use dict to match words and phrases
        """
        stem = "carbon_cycle"
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")

        ahrefs = self._find_ahrefs(inpath)
        inset = set()
        for ahref in ahrefs:
            inset.add(ahref.text)

        dictpath = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", f"{stem}.xml")
        outpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.html")
        args = ([
            "SEARCH",
            "--inpath", inpath,
            "--dict", dictpath,
            "--outpath", outpath,
            "--operation", "annotate", "no_input_styles",

        ])
        pyami = AmiLib()
        pyami.run_command(args)
        assert outpath.exists(), f"{outpath} should exist"
        ahrefs = self._find_ahrefs(outpath)
        # print(f"ahrefs {ahrefs}")
        outset = set()
        for ahref in ahrefs:
            outset.add(ahref.text)
        diffset = outset.difference(inset)
        assert len(diffset) >= 9
        assert "tropospheric" in diffset

    def _find_ahrefs(self, path):
        """
        find all a[@href] in file
        """
        xml = HtmlLib.parse_html(path)
        ahrefs = xml.xpath(".//a[@href]")
        return ahrefs

    def test_annotate_file_with_phrases_from_file(self):
        """
        read inpath HTML, remove styles, and use dict to match words and phrases
        """
        stem = "food_security"
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")

        wordpath = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", f"{stem}.txt")
        with open(wordpath, "r") as f:
            lines = f.readlines()
            assert len(lines) == 62
        outpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.html")
        args = ([
            "SEARCH",
            "--inpath", inpath,
            "--words", wordpath,
            "--outpath", outpath,
            "--operation", "annotate", "no_input_styles",
        ])
        pyami = AmiLib()
        pyami.run_command(args)
        assert outpath.exists(), f"{outpath} should exist"
        logger.info(f"wrote {outpath}")
        # TODO test we have annotation

