import csv
import unittest
from pathlib import Path

from amilib.ami_nlp import AmiNLP
from amilib.file_lib import FileLib
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)

class StatTest(AmiAnyTest):
    """
    test statistics and ML (small at present)
    """

    @unittest.skip("throws warning, needs fixing, uncomment if needed")
    def test_plot_scatter_noel_oboyle_STAT_PLOT(self):
        """
        computes labelled 2-D projection of points from distance matrix
        :return:
        """

        # Distance file available from RMDS project:
        #    https://github.com/cheind/rmds/blob/master/examples/european_city_distances.csv

        show_plot = False  # set True if plot wanted, BUT blocks on displaying
        data = []
        inputx = Path(Resources.TEST_RESOURCES_DIR, "misc", "european_city_distances.csv")
        delimiter = ';'
        reader = csv.reader(open(inputx, "r"), delimiter=delimiter)
        data = list(reader)

        dists = []
        labels = []
        for dt in data:
            labels.append(dt[0])
            dists.append([float(dd) for dd in dt[1:-1]])

        AmiNLP.plot_points_labels(dists, labels, show_plot=show_plot)
