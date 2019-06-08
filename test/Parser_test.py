import unittest

from JSONParser import parse_categories


class ParserTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_readAllCategoriesFromFile(self):
        categories = parse_categories('/Users/engineer/workspace/cecs535project1/test/TestItems')
        self.assertEqual(categories.length, 14)


if __name__ == '__main__':
    unittest.main()
