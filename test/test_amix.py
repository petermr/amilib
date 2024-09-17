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

    def test_logger(self):
        """
        logger outputs 2 messages (2024-09-16) - this is to debug it
        """
        logger = Util.get_logger(__name__)
        logger.setLevel(logging.WARNING)

        with self.assertLogs(logger, level='INFO') as cm:

            self._logger_messages(logger)

            self.assertEqual([
                # 'DEBUG:test.test_amix:debug', this was excluded
                'INFO:test.test_amix:info',
                'WARNING:test.test_amix:warning',
                'ERROR:test.test_amix:ERROR',
                'CRITICAL:test.test_amix:FATAL!!',
            ],
                             cm.output)

        amix = AmiLib()


