import re
from collections import defaultdict, Counter

from amilib.file_lib import FileLib
from amilib.util import Util

logger = Util.get_logger(__name__)


class HtmlExtra:

    @classmethod
    def create_counters(cls, package, section, subpackage, matched_dict, debug=False):
        pck_counter = defaultdict(int)
        subp_counter = defaultdict(int)
        sect_counter = defaultdict(int)
        for key in matched_dict:
            value = matched_dict.get(key)
            pck_counter[value[package]] += 1
            subp_counter[value[subpackage]] += 1
            sect_counter[value[section]] += 1
        if debug:
            logger.debug(f"package: {Counter(pck_counter)}")
            logger.debug(f"subpack: {Counter(subp_counter)}")
            logger.debug(f"section: {Counter(sect_counter)}")

        return (matched_dict.keys(), Counter(pck_counter), Counter(subp_counter), Counter(sect_counter))

    @classmethod
    def create_matched_dict_and_unmatched_keys(cls, def_dict, node_re):
        logger.debug(f"def_dict {def_dict}")
        counter = Counter(def_dict)
        logger.debug(f"counter {len(counter)}: {counter.most_common()}")

        matched_dict = dict()
        unmatched_keys = set()
        for key in counter:
            match = re.match(node_re, key)
            if match is None:
                unmatched_keys.add(key)
            else:
                matched_dict[key] = match.groupdict()
        return matched_dict
