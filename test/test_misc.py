import re
import unittest
from pathlib import Path

import pytest
from geopy.geocoders import Nominatim

from amilib.file_lib import FileLib
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

    @unittest.skip("requires connection and output can micro-vary")
    def test_geolocate_GEO(self):
        """
        GEO: locates places by name using Nominatim

        (Test occasionally returns variable decimal places
        TODO needs a fixed-place numeric comparison
        :return:
        """
        geolocator = Nominatim(timeout=10, user_agent="semanticclimate@gmail.com")
        results = []
        for name in [
            "Benares",
#            "Bengaluru",
            "Delhi",
            "Ladakh",
            # "Mumbai",
            "Mysore",
        ]:
            location = geolocator.geocode(name)
            tuple = (name, location[1], location.latitude, location.longitude)
            results.append(tuple)
        assert results == [
            ('Benares', (25.3356491, 83.0076292), 25.3356491, 83.0076292),
            # ('Bengaluru', (12.9767936, 77.590082), 12.9767936, 77.590082),
            ('Delhi', (28.6273928, 77.1716954), 28.6273928, 77.1716954),
            ('Ladakh', (33.9456407, 77.6568576), 33.9456407, 77.6568576),
            # ('Mumbai', (18.9733536, 72.82810491917377), 18.9733536, 72.82810491917377), # Mumbai seems to move!
            ('Mysore', (12.3051828, 76.6553609), 12.3051828, 76.6553609),
        ]


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
        with open(outfile, "w") as f:
            f.writelines(lines2)
        logger.debug(f"lines2 {lines2}")

