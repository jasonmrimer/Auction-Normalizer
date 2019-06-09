import unittest

from IngestJSON import ingest_values_from_files


class MyTestCase(unittest.TestCase):
    def test_readsCategoriesFromAllGivenFiles(self):
        ingest_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            'test_values.dat',
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


if __name__ == '__main__':
    unittest.main()
