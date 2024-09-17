from pathlib import Path

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

    def test_remove_styles_annotate_file_with_phrases(self):
        """
        read inpath HTML, remove styles, and use dict to match words and phrases
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
            "--operation", "annotate", "no_input_styles",

            ])
        pyami = AmiLib()
        pyami.run_command(args)
        assert outpath.exists(), f"{outpath} should exist"


