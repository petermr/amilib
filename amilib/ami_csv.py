import csv

from amilib.file_lib import FileLib

logger = FileLib().get_logger(__name__)


class AmiCSV:
    """Not many methods"""

    def read_transpose_write(self, inputx, output):
        """not developed"""
        a = zip(*csv.reader(open("input.csv", "rb")))
        csv.writer(open("output.csv", "wb")).writerows(a)

    def transpose(self, a):

        b = zip(*a)
        return b

