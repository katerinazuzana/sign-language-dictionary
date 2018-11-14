import unittest
from unittest import mock
import math
import numpy as np

import dictionary.search_engine
from dictionary.search_engine import SearchEngine


class SearchEngineTest(unittest.TestCase):

    @mock.patch('dictionary.search_engine.os.listdir')
    def setUp(self, mock_os_listdir):
        """Create an instance of SearchEngine."""

        mock_os_listdir.return_value = ['0:0.mp4',
                                        'box.mp4',
                                        'aljaska_1.mkv']
        self.searchEng = SearchEngine('dbpath', 'vfdirectory', 5, (3, 2))

    def test_mySort(self):
        """Test alphabetical ordering - should be:
        case insensitive, stable, numbers go last.
        """
        self.assertEqual(self.searchEng._mySort(['a', 'b']), ['a', 'b'])
        self.assertEqual(self.searchEng._mySort(['b', 'a']), ['a', 'b'])
        self.assertEqual(self.searchEng._mySort(['A', 'a']), ['A', 'a'])
        self.assertEqual(self.searchEng._mySort(['a', 'A']), ['a', 'A'])
        self.assertEqual(self.searchEng._mySort(['a', '1']), ['a', '1'])
        self.assertEqual(self.searchEng._mySort(['1', 'a']), ['a', '1'])
        self.assertEqual(self.searchEng._mySort(['0', '1']), ['0', '1'])
        self.assertEqual(self.searchEng._mySort(['1', '0']), ['0', '1'])

    def test_findVideoFile(self):
        """Linux specific test."""
        
        self.assertEqual(self.searchEng._findVideoFile('0:0'),
                         'vfdirectory/0:0.mp4')
        self.assertEqual(self.searchEng._findVideoFile('box'),
                         'vfdirectory/box.mp4')
        self.assertEqual(self.searchEng._findVideoFile('aljaska_1'),
                         'vfdirectory/aljaska_1.mkv')

    @mock.patch('dictionary.search_engine.SearchEngine._findVideoFile')
    def test_addSuffixes(self, mock_findVideoFile):
        mock_findVideoFile.side_effect = ['0:0.mp4',
                                          'box.mp4',
                                          'aljaska_1.mkv']
        
        test_input = [('0:0', '0:0'),
                      ('box', 'box'),
                      ('aljaska', 'aljaska_1')]
        expected_output = [('0:0', '0:0.mp4'),
                           ('box', 'box.mp4'),
                           ('aljaska', 'aljaska_1.mkv')]
        self.assertEqual(self.searchEng.addSuffixes(test_input),
                         expected_output)

    def test_calcActDist_the_same_shapes(self):
        test_input = {1, 2}, set(), {1, 2}, set()
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0)

    def test_calcActDist_1common_shape_others_similar(self):
        test_input = {1, 2}, {'I', 'II'}, {1, 3}, {'I', 'II'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.25)
        test_input = {1}, {'I'}, {1, 3}, {'I', 'I'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.25)

    def test_calcActDist_all_similar_shapes(self):
        test_input = {1, 2}, {'I', 'II'}, {3, 4}, {'I', 'II'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.5)
        test_input = {1}, {'I'}, {2}, {'I'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.5)

    def test_calcActDist_1similar_or_common_1different(self):
        test_input = {1, 2}, {'I', 'II'}, {3, 4}, {'I', 'III'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.75)
        test_input = {1, 2}, {'I', 'II'}, {1, 3}, {'I', 'III'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 0.75)

    def test_calcActDist_all_different_shapes(self):
        test_input = {1, 2}, {'I', 'II'}, {3, 4}, {'III', 'IV'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 1)
        test_input = {1}, {'I'}, {2}, {'II'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 1)
        test_input = set(), set(), {2}, {'II'}
        self.assertEqual(self.searchEng._calcActDist(*test_input), 1)

    def test_calcActDist_empty_input(self):
        test_input = set(), set(), set(), set()
        self.assertEqual(self.searchEng._calcActDist(*test_input), 1)

    def test_calcTypeDist_different_type(self):
        test_input = 'single hand', 0, 'both the same', None
        self.assertEqual(self.searchEng._calcTypeDist(*test_input), 1)

    def test_calcTypeDist_the_same_type(self):
        test_input = 'passive hand', 1, 'passive hand', 2
        self.assertEqual(self.searchEng._calcTypeDist(*test_input), 0.5)
        test_input = 'passive hand', 1, 'passive hand', 1
        self.assertEqual(self.searchEng._calcTypeDist(*test_input), 0)
        test_input = 'single hand', 0, 'single hand', None
        self.assertEqual(self.searchEng._calcTypeDist(*test_input), 0)

    def test_calcPlaceDist_totally_overlapping_ellipses(self):
        # test input:
        uRelief = np.array ([[0, 1, 1],
                             [0, 0, 1]])
        uArea = 3
        dbRelief = uRelief
        dbArea = uArea

        expected_output = 0
        self.assertEqual(self.searchEng._calcPlaceDist(uRelief, uArea,
                         dbRelief, dbArea), expected_output)

    def test_calcPlaceDist_distinct_ellipses(self):
        # test input:
        uRelief = np.array ([[0, 1, 1],
                             [0, 0, 1]])
        uArea = 3
        dbRelief = np.array ([[0, 0, 0],
                              [1, 1, 0]])
        dbArea = 2

        expected_output = 1
        self.assertEqual(self.searchEng._calcPlaceDist(uRelief, uArea,
                         dbRelief, dbArea), expected_output)

    def test_calcPlaceDist_partially_overlapping_ellipses(self):
        # test input:
        uRelief = np.array ([[0, 1, 1],
                             [0, 1, 1]])
        uArea = 4
        dbRelief = np.array ([[1, 1, 0],
                              [1, 1, 0]])
        dbArea = 4

        expected_output = 0.5
        self.assertEqual(self.searchEng._calcPlaceDist(uRelief, uArea,
                         dbRelief, dbArea), expected_output)

    def test_getReliefFcn_circle(self):
        """
        Input is of form: centerx, centery, a, b, angle.
        'function_to_test' should return 1 inside a circle with radius 10,
        and 0 outside.
        """
        test_input = 0, 0, 10, 10, 0
        function_to_test = self.searchEng._getReliefFcn(*test_input)
        
        for (x, y) in ((-10, 0), (0, 0), (10, 0), (0, 10),
            (math.sqrt(50), math.sqrt(50))):
            self.assertEqual(function_to_test(x, y), 1, (x, y))
        
        for (x, y) in ((11, 0), (0, 11), (8, 8)):
            self.assertEqual(function_to_test(x, y), 0, (x, y))

    def test_getReliefFcn_ellipse(self):
        """
        Input is of form: centerx, centery, a, b, angle.
        'function_to_test' should return 1 inside an ellipse with horizontal
        semi-axis of 20, and vertical semi-axis of 10.
        """
        test_input = 0, 0, 20, 10, 0
        func_to_test_zero_angle = self.searchEng._getReliefFcn(*test_input)

        test_input = 0, 0, 10, 20, math.pi / 2
        func_to_test_nonzero_angle = self.searchEng._getReliefFcn(*test_input)

        for (x, y) in ((-20, 0), (0, 0), (20, 0), (0, 10), (0, -10)):
            self.assertEqual(func_to_test_zero_angle(x, y), 1, (x, y))
            self.assertEqual(func_to_test_nonzero_angle(x, y), 1, (x, y))

        for (x, y) in ((-21, 0), (21, 0), (0, 11), (0, -11)):
            self.assertEqual(func_to_test_zero_angle(x, y), 0, (x, y))
            self.assertEqual(func_to_test_nonzero_angle(x, y), 0, (x, y))

    def test_getReliefFcn_zero_a_axis_ellipse(self):
        """
        Input is of form: centerx, centery, a, b, angle.
        'function_to_test' should always return 0.
        """
        test_input = 0, 0, 10, 0, 0
        function_to_test = self.searchEng._getReliefFcn(*test_input)

        for (x, y) in ((0, 0), (10, 0), (0, 10), (10, 10)):
            self.assertEqual(function_to_test(x, y), 0, (x, y))

    def test_getReliefFcn_zero_b_axis_ellipse(self):
        """
        Input is of form: centerx, centery, a, b, angle.
        'function_to_test' should always return 0.
        """
        test_input = 0, 0, 0, 10, 0
        function_to_test = self.searchEng._getReliefFcn(*test_input)

        for (x, y) in ((0, 0), (10, 0), (0, 10), (10, 10)):
            self.assertEqual(function_to_test(x, y), 0, (x, y))

    def test_getRelief_zero_fcn(self):
        input_fcn = lambda x, y: 0
        expected_output = np.array([[0, 0, 0],
                                    [0, 0, 0]])
        self.assertTrue(
            np.array_equal(self.searchEng._getRelief(input_fcn),
            expected_output)
        )

    def test_getRelief_nonzero_fcn(self):
        input_fcn = lambda x, y: 1 if y == 0 else 0
        expected_output = np.array([[1, 1, 1],
                                    [0, 0, 0]])
        self.assertTrue(
            np.array_equal(self.searchEng._getRelief(input_fcn),
            expected_output)
        )

        input_fcn = lambda x, y: 1 if x == 2 else 0
        expected_output = np.array([[0, 0, 1],
                                    [0, 0, 1]])
        self.assertTrue(
            np.array_equal(self.searchEng._getRelief(input_fcn),
            expected_output)
        )

    def test_getDbRelief(self):
        # input is of form: "y-coord, # of 0s, # of 1s, # of 0s;
        #                    y-coord, # of 0s, # of 1s, # of 0s;
        #                    ...                               "

        test_input = '0, 0, 3, 0'
        expected_output = np.array([[1, 1, 1],
                                    [0, 0, 0]])
        self.assertTrue(
            np.array_equal(self.searchEng._getDbRelief(test_input),
            expected_output)
        )

        test_input = '0, 2, 1, 0; 1, 2, 1, 0'
        expected_output = np.array([[0, 0, 1],
                                    [0, 0, 1]])
        self.assertTrue(
            np.array_equal(self.searchEng._getDbRelief(test_input),
            expected_output)
        )
