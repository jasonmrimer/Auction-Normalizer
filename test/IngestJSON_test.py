import unittest

from IngestJSON import ingest_files


class MyTestCase(unittest.TestCase):
    def test_readsCategoriesFromAllGivenFiles(self):
        ingest_files([
            'TestItems',
            'TestItems2'
        ],
            'test_categories.dat'
        )
        file = open('test_categories.dat', 'r')
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


if __name__ == '__main__':
    unittest.main()
