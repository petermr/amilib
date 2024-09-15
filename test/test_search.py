from amilib.amix import AmiLib
from amilib.util import Util
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

    def test_markup_file_with_phrases(self):
        """

        """
        logger.debug("do nothing")
        args = ([
            "SEARCH",
            "--inpath", "",
            "--dict", "",
            "--outpath", "",
            "--operation", "annotate"

            ])
        pyami = AmiLib()
        pyami.run_command(args)

