import unittest
from unittest import mock

import dictionary.search_engine
from dictionary.search_engine import SearchEngine


class SearchEngineTest(unittest.TestCase):

    @mock.patch('dictionary.search_engine.os.listdir')
    def setUp(self, mock_os_listdir):
        """Create an instance of SearchEngine."""
        mock_os_listdir.return_value = ['0:0.mp4',
                                        'box.mp4',
                                        'aljaska_1.mkv']
        self.searchEng = SearchEngine('dbpath', 'vfdirectory', 5, (50, 40))

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
