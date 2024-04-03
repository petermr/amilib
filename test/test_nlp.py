"""
Tests for NLP
"""
from pathlib import Path
import csv

from test.resources import Resources
from test.test_all import AmiAnyTest

from amilib.ami_nlp import AmiNLP


class NLPTest(AmiAnyTest):
    """
    Tests for ami_nlp
    """
    # import nltk, string

    def test_compute_similarity(self):
        """
        Ntests ami_nlp,cosine_sim
        :return:
        """
        ami_nlp = AmiNLP()
        print(f"sim00 {ami_nlp.cosine_sim('a little bird', 'a little bird')}")
        print(f"sim01 {ami_nlp.cosine_sim('a little bird', 'a little bird chirps')}")
        print(f"sim02 {ami_nlp.cosine_sim('a little bird', 'a big dog barks')}")

    def test_plot_scatter_noel_oboyle(self):
        """
        Not sure what this does!
        :return:
        """

        # Distance file available from RMDS project:
        #    https://github.com/cheind/rmds/blob/master/examples/european_city_distances.csv
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

        AmiNLP.plot_points_labels(dists, labels)
