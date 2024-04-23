import csv
from itertools import izip

class AmiCSV:

    def read_transpose_write(self, input, output):
        a = izip(*csv.reader(open("input.csv", "rb")))
        csv.writer(open("output.csv", "wb")).writerows(a)

    def transpose(self, a):

        b = izip(*a)
        return b

