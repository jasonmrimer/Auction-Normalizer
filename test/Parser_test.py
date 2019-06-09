import unittest

from JSONParser import *


class ParserTestCase(unittest.TestCase):
    categories_dat_filepath = 'test_values.dat'

    def setUp(self):
        open('test_values.dat', 'w').close()

    def test_readAllCategoriesFromFileWithoutDuplicates(self):
        categories = values_from_json_file([], 'TestItems', 'Items', 'Category')
        self.assertEqual(len(categories), 4)
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))

    def test_readAllCountriesFromFileWithoutDuplicates(self):
        countries = values_from_json_file([], 'TestItems', 'Items', 'Country')
        self.assertEqual(3, len(countries))
        self.assertTrue(countries.__contains__('USA'))
        self.assertTrue(countries.__contains__('Czech Republic'))
        self.assertTrue(countries.__contains__('Croatia'))

    def test_readsValuesWithSingleRelationshipNoDuplicates(self):
        values = values_with_relationship(
            set(),
            dictionary_from_json_file('TestItems', 'Items'),
            'Location',
            'Country'
        )
        self.assertTrue(4, len(values))
        self.assertTrue(values.__contains__(('Sunny South', 'USA')))
        self.assertTrue(values.__contains__(('Ohio - The Buckeye State!', 'USA')))
        self.assertTrue(values.__contains__(('Sunny South', 'Czech Republic')))
        self.assertTrue(values.__contains__(('SEE MY OTHER AUCTIONS', 'Croatia')))

    def test_shouldAddNewCategoriesToList(self):
        categories = values_from_json_file(
            [
                'Collectibles',
                'cat4',
                'cat5',
            ],
            'TestItems',
            'Items',
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

    def test_writesSingleValuesToFile(self):
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

    def test_writesRelatedValuesToFile(self):
        write_categories_to_dat(
            {
                ('Key1', 'Val1'),
                ('Key2', 'Val2'),
                ('Key3', 'Val3')
            },
            'test_values.dat'
        )
        file = open('test_values.dat', 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('Key1|Val1'))
        self.assertTrue(contents.__contains__('Key2|Val2'))
        self.assertTrue(contents.__contains__('Key3|Val3'))
        self.assertTrue(contents.__contains__('1|'))
        self.assertTrue(contents.__contains__('2|'))
        self.assertTrue(contents.__contains__('3|'))
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

    def test_extractObjectsFromJSONFile(self):
        self.assertEqual(list, type(dictionary_from_json_file('TestItems', 'Items')))


if __name__ == '__main__':
    unittest.main()
