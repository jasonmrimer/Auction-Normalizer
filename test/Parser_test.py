import unittest

from JSONParser import *


class ParserTestCase(unittest.TestCase):
    categories_dat_filepath = 'test_categories.dat'

    def setUp(self):
        open('test_categories.dat', 'w').close()

    def test_readAllCategoriesFromFileWithoutDuplicates(self):
        categories = parse_categories([], 'TestItems')
        self.assertEqual(len(categories), 4)
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))

    def test_shouldAddNewCategoriesToList(self):
        categories = parse_categories(
            [
                'Collectibles',
                'cat4',
                'cat5',
            ],
            'TestItems'
        )
        self.assertEqual(len(categories), 6)
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))
        self.assertTrue(categories.__contains__('cat4'))
        self.assertTrue(categories.__contains__('cat5'))

    def test_removeDuplicatesFromList(self):
        self.assertEqual(
            len(
                remove_duplicates(
                    [
                        'a', 'a', 'a', 'b', 'b'
                    ]
                )
            ),
            2,
            'duplicates remain after dedupe'
        )

    def test_writesCategoriesToFile(self):
        write_categories_to_dat(
            ['Cat1', 'Cat2', 'Cat3'],
            'test_categories.dat'
        )
        file = open('test_categories.dat', 'r')
        self.assertEqual(
            file.read(),
            '1|Cat1\n'
            '2|Cat2\n'
            '3|Cat3')
        file.close()

    def test_parsesCategoriesFromJSONToDat(self):
        convert_json_categories_to_dat('TestItems', 'test_categories.dat')
        file = open('test_categories.dat', 'r')
        self.assertEqual(
            file.read(),
            '1|Collectibles\n'
            '2|Kitchenware\n'
            '3|Test\n'
            '4|Dept 56')
        file.close()


if __name__ == '__main__':
    unittest.main()
