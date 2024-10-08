from pathlib import Path
import lxml.etree as ET

from amilib.ami_html import HtmlLib
from amilib.amix import AmiLib
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
        stem = "carbon_cycle1"
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")
        dictpath = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", f"{stem}.html")
        outpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.html")
        args = ([
            "SEARCH",
            "--inpath", inpath,
            "--dict", dictpath,
            "--outpath", outpath,
            "--operation", "annotate"

            ])
        pyami = AmiLib()
        pyami.run_command(args)
        assert outpath.exists(), f"{outpath} should exist"

    def test_annotate_file_with_phrases_from_dict(self):
        """
        read inpath HTML, remove styles, and use dict to match words and phrases
        """
        stem = "carbon_cycle1"
        inpath = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")

        ahrefs = self._find_ahrefs(inpath)
        inset = set()
        for ahref in ahrefs:
            inset.add(ahref.text)

        dictpath = Path(Resources.TEST_RESOURCES_DIR, "dictionary", "climate", f"{stem}.html")
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
        outpath = Path(Resources.TEMP_DIR, "annotate", f"{stem}.html")
        args = ([
            "SEARCH",
            "--inpath", inpath,
            "--words", wordpath,
            # "--outpath", outpath,
            "--operation", "annotate", "no_input_styles",
        ])
        pyami = AmiLib()
        pyami.run_command(args)
        assert outpath.exists(), f"{outpath} should exist"

