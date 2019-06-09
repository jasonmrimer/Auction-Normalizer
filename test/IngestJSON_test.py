import unittest

from IngestJSON import *


class MyTestCase(unittest.TestCase):
    def test_readsCategoriesFromAllGivenFiles(self):
        ingest_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            'test_values.dat',
            'Items',
            'Category'
        )
        file = open('test_values.dat', 'r')
        self.assertEqual(
            file.read(),
            '1|Collectibles\n'
            '2|Kitchenware\n'
            '3|Test\n'
            '4|Dept 56\n'
            '5|cat5\n'
            '6|cat6\n'
            '7|cat7'
        )
        file.close()

    def test_readsCountriesFromAllGivenFiles(self):
        ingest_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            'test_values.dat',
            'Items',
            'Country'
        )
        file = open('test_values.dat', 'r')
        self.assertEqual(
            '1|USA\n'
            '2|Croatia\n'
            '3|Czech Republic\n'
            '4|Germany\n'
            '5|Japan',
            file.read(),
            'the extracted countries do not match the test files\'s contents'
        )
        file.close()

    def test_readsLocationsFromAllGivenFiles(self):
        ingest_related_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            'test_values.dat',
            'Location',
            'Country'
        )
        file = open('test_values.dat', 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('1|'))
        self.assertTrue(contents.__contains__('2|'))
        self.assertTrue(contents.__contains__('3|'))
        self.assertTrue(contents.__contains__('4|'))
        self.assertTrue(contents.__contains__('5|'))
        self.assertTrue(contents.__contains__('6|'))
        self.assertTrue(contents.__contains__('7|'))
        self.assertTrue(contents.__contains__('8|'))
        self.assertFalse(contents.__contains__('9|'))
        self.assertTrue(contents.__contains__('|Sunny South|USA'))
        self.assertTrue(contents.__contains__('|SEE MY OTHER AUCTIONS|Croatia'))
        self.assertTrue(contents.__contains__('|Ohio - The Buckeye State!|USA'))
        self.assertTrue(contents.__contains__('|Sunny South|Czech Republic'))
        self.assertTrue(contents.__contains__('|Happy Holidays|USA'))
        self.assertTrue(contents.__contains__('|Sunny South|Germany'))
        self.assertTrue(contents.__contains__('|SEE MY OTHER AUCTIONS|Japan'))
        self.assertTrue(contents.__contains__('|Elwood,New York|USA'))
        file.close()


if __name__ == '__main__':
    unittest.main()
