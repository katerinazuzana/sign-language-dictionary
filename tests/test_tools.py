import unittest

from dictionary import tools


class ToolsTest(unittest.TestCase):

    def test_listOfTuplesToList_1tuple(self):
        data = [('foo',), ('bar',), ('egg',)]
        result = tools.listOfTuplesToList(data)
        self.assertEqual(result, ['foo', 'bar', 'egg'])

    def test_listOfTuplesToList_2tuple(self):
        data = [('foo', 3), ('bar', 55), ('egg', 9)]
        result = tools.listOfTuplesToList(data)
        self.assertEqual(result, ['foo', 'bar', 'egg'])

    def test_listOfTuplesToList_empty_list(self):
        data = []
        result = tools.listOfTuplesToList(data)
        self.assertEqual(result, [])

    def test_leftPadItems(self):
        data = ['0:0', 'matematika', 'český jazyk']
        result = tools.leftPadItems(data)
        self.assertEqual(result, [' 0:0', ' matematika', ' český jazyk'])

    def test_leftPadItems_empty_list(self):
        data = []
        result = tools.leftPadItems(data)
        self.assertEqual(result, [])
