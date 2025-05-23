"""
Utilities (mainly classmethods)
"""
import collections
import logging
from pathlib import Path

import configparser
import numpy as np
import math
import csv

# from amilib.util import Util

X = 0
Y = 1

logger = logging.getLogger(__name__)


class AmiUtil:

    @classmethod
    def check_type_and_existence(cls, target, expected_type):
        """
        asserts not None for object and its type
        if path asserts existence


        :param target: object to check
        :param expected_type: type of object
        :return: None
        """
        assert target is not None
        typ = type(target)
        assert typ is expected_type, f"type {typ} should be {expected_type}"
        if expected_type is Path:
            assert target.exists(), f"{target} should exist"

    @classmethod
    def is_ordered_numbers(cls, limits2):
        """
        check limits2 is a numeric 2-tuple in increasing order
        :param limits2:
        :return: True tuple[1] > tuple[2]
        """
        return limits2 is not None and len(limits2) == 2 \
               and AmiUtil.is_number(limits2[0]) and AmiUtil.is_number(limits2[1]) \
               and limits2[1] > limits2[0]

    @classmethod
    def is_number(cls, s):
        """
        test if s is a number
        :param s:
        :return: True if float(s) succeeds
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    @classmethod
    def get_float(cls, s):
        """numeric value of s
        traps Exception
        :param s: string to parse
        :return: numeric value or None
        """
        try:
            return float(s)
        except ValueError:
            return None

    @classmethod
    def int2hex(cls, ii):
        """convert int (0-255) to 2-character hex string
        :param ii: integer
        :return: 2-digit hex string of form 01, 09, 0f, 10, ff , or None if not int 0-125
        """
        if ii is None or not type(ii) is int or ii < 0 or ii> 255:
            return None
        return ('0' + hex(ii)[2:])[-2:]

    @classmethod
    def is_white(cls, color, delta=20, sat=255):
        """is color white within given tolerance
        255 - color[i] < delta
         """
        if color is None or len(color) != 3 or not AmiUtil.is_number(color[0]) \
                or not AmiUtil.is_number(delta):
            return False
        for i in range(3):
            if sat - color[i] > delta:
                return False
        return True

    @classmethod
    def is_black(cls, color, delta=20):
        """is color white within given tolerance
        color[i] < delta
         """
        if color is None or len(color) != 3 or not AmiUtil.is_number(color[0]) \
                or not AmiUtil.is_number(delta):
            return False
        for i in range(3):
            if color[i] > delta:
                return False
        return True

    @classmethod
    def col6_to_col3(cls, col6):
        """
        shortens 6 character hex color to 3-character
        e.g.
        a1b2c3 +> abc
        :param col6: 6 letter color
        :return: None if invalid input
        """
        if not col6 or not len(col6) == 6:
            return None
        return "".join([col6[::2]])

    @classmethod
    def is_gray(cls, color, delta=20):
        """is color gray within given tolerance
        color is triple of numbers , mean is its mean
        if abs(color[i] - mean) > delta) return False
         """
        if color is None or len(color) != 3 or not AmiUtil.is_number(color[0]) \
                or not AmiUtil.is_number(delta):
            return False
        mean = (color[0] + color[1] + color[2]) / 3
        for i in range(3):
            if abs(color[i] - mean) > delta:
                return False
        return True


    @classmethod
    def get_xy_from_sknw_centroid(cls, yx):
        """
        yx is a 2-array and coords need swapping
        and changing from numpy to int
        :param yx:
        :return: [x,y]
        """
        assert yx is not None
        assert len(yx) == 2 and type(yx) is np.ndarray, f"xy was {yx}"
        return [int(yx[1]), int(yx[0])]

    # @classmethod
    # def make_numpy_assert(cls, numpy_array, shape=None, maxx=None, dtype=None):
    #     """
    #     Asserts properties of numpy_array
    #     :param numpy_array:
    #     :param shape:
    #     :param maxx: max value (e.g. 255, or 1.0 for images)
    #     :param dtype:
    #     :return:
    #     """
    #     assert numpy_array is not None, f"numpy array should not be None"
    #     assert type(numpy_array) is np.ndarray, \
    #         f"object should be numpy.darray, found {type(numpy_array)} \n {numpy_array}"
    #     if shape:
    #         assert numpy_array.shape == shape, f"shape was {numpy_array.shape} should be {shape}"
    #     if maxx:
    #         assert np.max(numpy_array) == maxx, f"maxx was {np.max(numpy_array)}, shou,d be {maxx}"
    #     if dtype:
    #         assert numpy_array.dtype == dtype, f"dtype was {numpy_array.dtype} should be {dtype}"
    #
    @classmethod
    def get_angle(cls, p0, p1, p2):
        """
        replace this

        :param p0:
        :param p1:
        :param p2:
        :return:
        """
        '''
        signed angle p0-p1-p2
        :param p0:
        :param p1: centre point
        :param p2:
        '''
        AmiUtil.assert_is_float_array(p0)
        AmiUtil.assert_is_float_array(p1)
        AmiUtil.assert_is_float_array(p2)

        linal = False
        if linal:
            np0 = np.array(p0, dtype=uint8)
            np1 = np.array(p1, dtype=uint8)
            np2 = np.array(p2, dtype=uint8)
            v0 = np0 - np1
            v1 = np2 - np1
            angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
        else:
            dx0 = p0[0] - p1[0]
            dy0 = p0[1] - p1[1]
            v01 = [p0[0] - p1[0], p0[1] - p1[1]]
            v21 = [p2[0] - p1[0], p2[1] - p1[1]]
            ang01 = math.atan2(v01[1], v01[0])
            ang21 = math.atan2(v21[1], v21[0])
            angle = ang21 - ang01
            angle = AmiUtil.normalize_angle(angle)

        return angle

    @classmethod
    def normalize_angle(cls, angle):
        """
        normalizes angle to -Pi 0 +Pi
        :param angle:
        :return:
        """
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle <= -math.pi:
            angle += 2 * math.pi
        return angle

    @classmethod
    def get_dist(cls, xy0, xy1):
        '''
        length p0-p1
        :param xy0:
        :param xy1:
        '''
        fxy0 = AmiUtil.to_float_array(xy0)
        fxy1 = AmiUtil.to_float_array(xy1)
        if fxy0 is None or fxy1 is None:
            return None
        AmiUtil.assert_is_float_array(fxy0)
        AmiUtil.assert_is_float_array(fxy1)

        dx0 = fxy0[0] - fxy1[0]
        dy0 = fxy0[1] - fxy1[1]
        dist = math.sqrt(dx0 * dx0 + dy0 * dy0)

        return dist


    @classmethod
    def assert_is_float_array(cls, arr, length=2):
        """
        assert arr[0] is float and has given length
        :param arr:
        :param length:
        :return:
        """
        assert arr is not None
        assert (len(arr) == length) and AmiUtil.is_number(arr[0]), f"arr must be numeric {arr} {len(arr)}"

    @classmethod
    def assert_is_coord_array(cls, arr, length=2):
        """
        assert arr[0] is float and has given length
        :param arr:
        :param length:
        :return:
        """
        assert arr is not None and len(arr) > 0
        AmiUtil.assert_is_float_array(arr[0], length=2), f"arr must be numeric width 2 {arr[0]}"

    @classmethod
    def float_list(cls, int_lst):
        """
        converts a list of ints or uint16 or uint8 to floats
        :param int_lst: 
        :return: 
        """
        assert int_lst is not None and type(int_lst) is list and len(int_lst) > 0, f"not a list: {int_lst}"
        tt = type(int_lst[0])
        assert tt is int or tt is uint8 or tt is uint16, f"expected int, got {tt}"
        return [float(i) for i in int_lst]

    @classmethod
    def to_float_array(cls, arr):
        """
        converts to array of floats if possible
        :param arr:
        :return:
        """
        if arr is None:
            return None
        try:
            farr = [float(a) for a in arr]
        except ValueError as e:
            raise f"cannot convet to float {type(arr[0])}"
        return farr

    @classmethod
    def swap_yx_to_xy(cls, yx):
        return [yx[1], yx[0]]

    @classmethod
    def are_coincident(cls, point1, point2, tolerance=0.001):
        """are two points coincident within a tolerance?
        uses abs(deltax) + abs(deltay) <= tolerance
        :param point1:
        :param point2:
        :param tolerance: default 0.001
        :return: true if sum of detas within tolerance
        """
        if not point1 or not point2:
            return False
        if abs(point1[X] - point2[X]) + abs(point1[Y] - point2[Y]) <= tolerance:
            return True
        else:
            return False

    @classmethod
    def make_unique_points_list(cls, points, tolerance):
        """merge points which are within tolerance
        simplistic (probably O(n**2)
        compares each point with each other
        :param points: list of points
        :param tolerance:
        """
        new_points = []
        for point in points:
            exist = False
            for new_point in new_points:
                if AmiUtil.are_coincident(point, new_point, tolerance):
                    exist = True
                    break
            if not exist:
                new_points.append(point)
        return new_points

    @classmethod
    def write_xy_to_csv(cls, xy_array, path, header=None):

        if path is None:
            logger.error("no path given")
            return
        AmiUtil.assert_is_coord_array(xy_array)
        with open(path, "w", encoding="UTF-8", newline='') as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(xy_array)

    @classmethod
    def get_config_and_section_names(cls, inpath):
        """
        read a config(.ini) file and get the sections
        :param inpath: input
        :return: sections (name-values under e.g. [SAVED])
        """
        logger.debug(f"inpath config.ini {inpath}")
        config = configparser.ConfigParser()
        config.read(inpath)

        sections = config.sections()
        assert len(sections) > 0, f"section names in {inpath} must not be empty"
        logger.debug(f"sections {sections}")
        logger.debug(f"confif {config} {config.keys()}")
        return config, sections

    @classmethod
    def is_iterable(cls, obj):
        """
        Is obj iterable? It's messy
        see https://stackoverflow.com/questions/1952464/python-how-to-determine-if-an-object-is-iterable
        :param obj: possible iterable.
        :return: False if obj is None or not iterable
        """
        try:
            some_object_iterator = iter(obj)
        except TypeError as te:
            # print(obj, 'is not iterable')
            return False
        return True


class AmiJson:
    """
    parses and writes JSON

    """
    @classmethod
    def read_nested_dicts(cls, dict1, key_string, separator="."):
        """
        reads nested dictionary values
        developed for reading rows in tables
        e.g.
        {"key1:
            {"foo" :
                {"bar":"plugh"}
            }
        can be addressed a "key1.foo.bar"
        None values anywhere return None so no Exceptions
        :param dict1: JSON dictionary  may have values as subdictionaries
        :param key_string: key (may include separators)
        :param separator: default = "."
        TODO use JsonPath
        """
        if dict1 is None or key_string is None:
            logger.warning("None arguments")
            return None
        keys = key_string.strip().split(separator)
        next_val = dict1
        for key in keys:
            value = next_val.get(key)
            if type(value) is not dict: # include None
                return value
            next_val = value

    @classmethod
    def create_json_table(cls, data_items, wanted_keys):
        """
        iterates over an implicit json table of dicts
        developed for EuropePMC output
        Not guaranteed to work elsewhere
        :param data_items: a dict of key:dict items
        :param wanted_keys: keys to extract - assumed toplevel in each dict (may use AmiJson notations a.b.c
        :return: dictionary corresponding to a ?rectangular table
        TODO use JsonPath
        """
        dict_by_id = collections.OrderedDict()
        for key, data in data_items.items():
            dict_row = {k: AmiJson.read_nested_dicts(data, k) for k in wanted_keys}
            dict_by_id.update({key: dict_row})
        return dict_by_id


class Vector2:

    def __init__(self, v2):
        self.vec2 = v2

    # @classmethod
    # def angle_to(cls, vv0, vv1):
    #     """
    #
    #     :param vv0: Vector2
    #     :param vv1: Vector2
    #     :return: angle(rad) between vectors (maybe unsigned??)
    #     """
    #     raise NotImplemented("don't use LA for angles")
    #     v0 = vv0.vec2
    #     v1 = vv1.vec2
    #
    #     inner = np.inner(v0, v1)
    #     norms = LA.norm(v0) * LA.norm(v1)
    #
    #     cos = inner / norms
    #     rad = np.arccos(np.clip(cos, -1.0, 1.0))
    #     return rad

