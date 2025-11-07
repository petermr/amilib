import logging
import unittest

from amilib.amix import AmiLib

from amilib.util import Util

logger = Util.get_logger(__name__)
logger.setLevel(logging.INFO)
class AmixTest(unittest.TestCase):
    """
    test general methods (e.g. custom loggers
    """

    def _logger_messages(self, logger):
        logger.debug("debug")  # won't be printed
        logger.info("info")
        logger.warning("warning")
        logger.error("ERROR")
        logger.fatal("FATAL!!")

