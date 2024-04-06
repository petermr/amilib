import csv
import logging

logger = logging.getLogger(__file__)


class AmiCSV:

    def read_transpose_write(self, inputx, output):
        a = zip(*csv.reader(open(inputx, "rb")))
        csv.writer(open(output, "wb")).writerows(a)

    @classmethod
    def transpose(cls, a):
        """
        clever trick for transposing a 2-D array
        :param a: array
        :return: transposed array or None if bad arguments
        """
        if a is None or len(a.shape) != 2:
            return None
        b = zip(*a)
        return b
