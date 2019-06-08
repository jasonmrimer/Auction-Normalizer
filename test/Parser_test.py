import unittest

from JSONParser import *


class ParserTestCase(unittest.TestCase):
    categories_dat_filepath = 'test_categories.dat'

    def setUp(self):
        open('test_categories.dat', 'w').close()

    def test_something(self):
        self.assertEqual(True, True)

    def test_readAllCategoriesFromFileWithoutDuplicates(self):
        categories = parse_categories('TestItems')
        self.assertEqual(len(categories), 4)
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))

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
        self.assertEqual(file.read(), 'Cat1\nCat2\nCat3')
        file.close()

    def test_parsesCategoriesFromJSONToDat(self):
        convert_json_categories_to_dat('TestItems', 'test_categories.dat')
        file = open('test_categories.dat', 'r')
        self.assertEqual(
            file.read(),
            'Collectibles\n'
            'Kitchenware\n'
            'Test\n'
            'Dept 56')
        file.close()


if __name__ == '__main__':
    unittest.main()
