import unittest

from JSONParser import *


class ParserTestCase(unittest.TestCase):
    categories_dat_filepath = 'test_values.dat'

    def setUp(self):
        open('test_values.dat', 'w').close()

    def test_readAllCategoriesFromFileWithoutDuplicates(self):
        categories = parse_values([], 'TestItems', 'Category')
        self.assertEqual(len(categories), 4)
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))

    def test_readAllCountriesFromFileWithoutDupicates(self):
        countries = parse_values([], 'TestItems', 'Country')
        self.assertEqual(3, len(countries))
        self.assertTrue(countries.__contains__('USA'))
        self.assertTrue(countries.__contains__('Czech Republic'))
        self.assertTrue(countries.__contains__('Croatia'))

    def test_shouldAddNewCategoriesToList(self):
        categories = parse_values(
            [
                'Collectibles',
                'cat4',
                'cat5',
            ],
            'TestItems',
            'Category'
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

    def test_writesValuesToFile(self):
        write_categories_to_dat(
            ['Val1', 'Val2', 'Val3'],
            'test_values.dat'
        )
        file = open('test_values.dat', 'r')
        self.assertEqual(
            file.read(),
            '1|Val1\n'
            '2|Val2\n'
            '3|Val3')
        file.close()

    def test_extractsNestedValues(self):
        json_object = dict(
            {
                'Key': [
                    'value1',
                    'value2'
                ],
                'SingleSub': {
                    'Not applicable': 'red herring',
                    'Key': 'value3'
                },
                'DoubleSub': {
                    'Sub': {
                        'Key': [
                            'value4',
                            'value5'
                        ],
                        'n/a': 'nope'
                    }
                },
                'SubObjectList': [
                    {
                        'Object': {
                            'Key': 'value6',
                            'NA': 'notapp'
                        }
                    },
                    {
                        'Object': {
                            'Key': [
                                'value7',
                                'value8'
                            ]
                        }
                    }
                ]

            }
        )
        values = extract_nested_values_from_json_with_key([], json_object, 'Key')
        self.assertEqual(8, len(values))
        self.assertTrue(values.__contains__('value1'))
        self.assertTrue(values.__contains__('value2'))
        self.assertTrue(values.__contains__('value3'))
        self.assertTrue(values.__contains__('value4'))
        self.assertTrue(values.__contains__('value5'))
        self.assertTrue(values.__contains__('value6'))
        self.assertTrue(values.__contains__('value7'))
        self.assertTrue(values.__contains__('value8'))


if __name__ == '__main__':
            unittest.main()
