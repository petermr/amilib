"""
Tests for NLP
"""
from pathlib import Path
import csv

from pytest import approx

from test.resources import Resources
from test.test_all import AmiAnyTest

from amilib.ami_nlp import AmiNLP



class NLPTest(AmiAnyTest):
    """
    Tests for ami_nlp
    """
    # import nltk, string

    def test_compute_text_similarity_STAT(self):
        """
        ami_nlp,cosine_sim compares strings
        :return:
        """
        ami_nlp = AmiNLP()
        assert ami_nlp.cosine_sim('a little bird', 'a little bird') == approx(1.0)
        assert ami_nlp.cosine_sim('a little bird', 'a little bird chirps') == approx(0.7093, abs=0.001)
        assert ami_nlp.cosine_sim('a little bird', 'a big dog barks') == approx(0, abs=0.001)

