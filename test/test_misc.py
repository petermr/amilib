"""
removed geocoding
"""
import re
import unittest
from collections import Counter
from pathlib import Path

import pytest

from amilib.ami_args import AbstractArgs
# from geopy.geocoders import Nominatim

from amilib.ami_html import HtmlUtil
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

subs = {
    "(\\d\\d?:)?\\d\\d?:\\d\\d\\n": "",
    ", , ": " ",
    "\\s*,\\s*": "",
    "OK,?\\s*":" ",
    "Amy\\s+[Dd]ict": "amidict",
    "Amy": "ami",
    "F C C C": "FCCC",
    "So\\s*,?\\s*": " ",
    "\\,\\s*": " ",
    ", ": " ",

}

logger = Util.get_logger(__name__)

def multiple_replace(replacements, text):
    # Create a regular expression from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, replacements.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: replacements[mo.group()], text)


class MiscTest(AmiAnyTest):

#     @unittest.skip("requires connection and output can micro-vary")
#     def test_geolocate_GEO(self):
#         """
#         GEO: locates places by name using Nominatim
#
#         (Test occasionally returns variable decimal places
#         TODO needs a fixed-place numeric comparison
#         :return:
#         """
#         geolocator = Nominatim(timeout=10, user_agent="semanticclimate@gmail.com")
#         results = []
#         for name in [
#             "Benares",
# #            "Bengaluru",
#             "Delhi",
#             "Ladakh",
#             # "Mumbai",
#             "Mysore",
#         ]:
#             location = geolocator.geocode(name)
#             tuple = (name, location[1], location.latitude, location.longitude)
#             results.append(tuple)
#         assert results == [
#             ('Benares', (25.3356491, 83.0076292), 25.3356491, 83.0076292),
#             # ('Bengaluru', (12.9767936, 77.590082), 12.9767936, 77.590082),
#             ('Delhi', (28.6273928, 77.1716954), 28.6273928, 77.1716954),
#             ('Ladakh', (33.9456407, 77.6568576), 33.9456407, 77.6568576),
#             # ('Mumbai', (18.9733536, 72.82810491917377), 18.9733536, 72.82810491917377), # Mumbai seems to move!
#             ('Mysore', (12.3051828, 76.6553609), 12.3051828, 76.6553609),
#         ]
#

    @unittest.skip("Not processing transcript ")
    def test_tidy_transcript(self):


        infile = Path(Resources.TEST_RESOURCES_DIR, "misc", "transcript1.txt")
        assert infile.exists(), f"infile should exists {infile}"
        with open(infile, "r") as f:
            lines = f.readlines()

        assert lines is not None
        assert len(lines) == pytest.approx(1800, abs=20)
        lines2 = []
        for ll in lines:
            ll2 = multiple_replace(subs, ll)
            if len(ll.strip()) > 0:
                lines2.append(ll2)
        transcript_dir = Path(Resources.TEMP_DIR, "misc", "transcript")
        transcript_dir.mkdir(exist_ok=True, parents=True)
        outfile = Path(transcript_dir, "transcript2.txt")
        with open(outfile, "w", encoding="UTF-8") as f:
            f.writelines(lines2)
        logger.debug(f"lines2 {lines2}")

    def test_word_counter(self):
        """
        illustratiue exercise
        reads a ChAPTER of IPCC, tokenize, lowercase ans count words in Counter

        """
        min_len = 5
        infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "wg3", "Chapter03", "html_with_ids.html")
        assert infile.exists()
        container_xpath = ".//div[@id='executive-summary']"
        text_xpath = "div/p//text()"

        p_counter = self.count_words_crude(infile, container_xpath, min_len, text_xpath)
        logger.debug(f"counter {p_counter}")

    def count_words_crude(self, infile, container_xpath, min_len, text_xpath):
        """
        reads html file, extracts <p> objects , and counts lowercase text tokens
        :param container_xpath: top_level container
        ;param infile: html file
        :param min_len: of text chunks
        :param text_xpath;to find text chunks
        """
        htmlx = HtmlUtil.parse_html_file_to_xml(infile)
        exec_summ = htmlx.xpath(container_xpath)
        p_texts = exec_summ[0].xpath(text_xpath)
        p_counter = Counter()
        for p_text in p_texts:
            if len(p_text) >= min_len:
                p_text = p_text.lower().strip()
                splits = p_text.split()
                for split in splits:
                    p_counter[split] += 1
        return p_counter

    def test_wordsquare(self):

        import random
        import numpy as np

        # Word list
        words = [
            "IGBOLAND", "VASSA", "NIGERIA", "BRIDGETOWN", "BARBADOS", "VIRGINIA",
            "PASCAL", "FALMOUTH", "PHILADELPHIA", "KING", "MONTSERRAT", "SPITZBERGEN",
            "SOHAM", "CAMBRIDGE", "MARIA"
        ]
        words = [word.upper() for word in words]

        # Grid size
        grid_size = 13
        grid = np.full((grid_size, grid_size), '', dtype=str)

        # Directions: all 8 possible
        directions = [
            (0, 1), (1, 0), (1, 1), (0, -1),
            (-1, 0), (-1, -1), (1, -1), (-1, 1)
        ]

        placed_words = []


        def can_place(word, row, col, dr, dc):
            for i in range(len(word)):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < grid_size and 0 <= c < grid_size):
                    return False
                if grid[r, c] != '' and grid[r, c] != word[i]:
                    return False
            return True


        def place_word(word):
            random_directions = directions.copy()
            random.shuffle(random_directions)
            for dr, dc in random_directions:
                for _ in range(100):
                    row = random.randint(0, grid_size - 1)
                    col = random.randint(0, grid_size - 1)
                    if can_place(word, row, col, dr, dc):
                        for i in range(len(word)):
                            grid[row + dr * i, col + dc * i] = word[i]
                        placed_words.append((word, row, col, dr, dc))
                        return True
            return False


        # Place each word randomly forward or backward
        for word in words:
            chosen_word = word[::-1] if random.random() < 0.5 else word
            if not place_word(chosen_word):
                print(f"Could not place word: {word}")

        # Fill in the rest with random letters
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for r in range(grid_size):
            for c in range(grid_size):
                if grid[r, c] == '.' or grid[r,c] == ' ' or grid[r, c] == '':
                    grid[r, c] = random.choice(alphabet)

        # Create a solution grid
        solution_grid = np.full((grid_size, grid_size), '.', dtype=str)
        for word, row, col, dr, dc in placed_words:
            for i in range(len(word)):
                solution_grid[row + dr * i, col + dc * i] = grid[row + dr * i, col + dc * i]


        # Print the results
        def grid_to_text(grid_array):
            return '\n'.join(' '.join(row) for row in grid_array)


        print("===== INSTRUCTIONS =====")
        print(
            "Find the following words hidden in the grid below. Words may go forwards, backwards, diagonally, vertically, or horizontally.\n")

        print("===== WORDSEARCH PUZZLE =====")
        print(grid_to_text(grid))

        print("\n===== WORD LIST =====")
        print(', '.join(words))

        print("\n===== SOLUTION KEY =====")
        print(grid_to_text(solution_grid))

class ArgsTest(AmiAnyTest):
    """
    test argparse stuff
    """
    def test_capture_errors(self):
        """capture errors on stderr
        If you don't want to subclass but still want to capture what argparse prints,
        you can redirect sys.stderr:


        """
        import argparse
        import sys
        import io
        from contextlib import redirect_stderr

        def try_parse(args=None):
            parser = argparse.ArgumentParser(description="My CLI")
            parser.add_argument(
                "--value",
                type=int,
                required=True,
                help="value of value"
            )
            parser.add_argument(
                "--operation",
                choices=["annotate", "counts", "index", "no_input_styles"],
                required=True,
                help="Type of operation to perform"
            )
            """
            Captured argparse error:
usage: _jb_pytest_runner.py [-h] --operation
                            {annotate,counts,index,no_input_styles}
_jb_pytest_runner.py: error: argument --operation: invalid choice: 'search' (choose from annotate, counts, index, no_input_styles)
            """

            err = AbstractArgs.parse_error(parser, args)
            return err

        # valid args
        err = try_parse(["--value", "3", "--operation", "index"])
        assert err is None

        # missing arg
        err = try_parse(["--value", "3"])
        assert err == "the following arguments are required: --operation\n"

        # arg with wrong type
        err = try_parse(["--value", "foo", "--operation", "index"])
        assert err == "argument --value: invalid int value: 'foo'\n"

        # arg with wrong choice value
        err = try_parse(["--operation", "search"])
        assert err and err.strip() == "argument --operation: invalid choice: 'search' (choose from 'annotate', 'counts', 'index', 'no_input_styles')"
