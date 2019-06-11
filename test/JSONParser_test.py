import unittest

from JSONParser import *


class JSONParserTestCase(unittest.TestCase):
    test_items = 'TestItems'
    dat_filepath = 'test_values.dat'
    top_key = 'Items'

    def setUp(self):
        open(
            self.dat_filepath,
            'w'
        ).close()

    def test_readAllCategoriesFromFileWithoutDuplicates(self):
        categories = values_from_json_file(
            [],
            dictionary_from_json_file(
                self.test_items,
                self.top_key
            ),
            'Category'
        )
        self.assertEqual(
            len(categories),
            4
        )
        self.assertTrue(categories.__contains__('Collectibles'))
        self.assertTrue(categories.__contains__('Kitchenware'))
        self.assertTrue(categories.__contains__('Test'))
        self.assertTrue(categories.__contains__('Dept 56'))

    def test_readAllCountriesFromFileWithoutDuplicates(self):
        countries = values_from_json_file(
            [],
            dictionary_from_json_file(
                self.test_items,
                self.top_key
            ),
            'Country'
        )
        self.assertEqual(
            3,
            len(countries)
        )
        self.assertTrue(countries.__contains__('USA'))
        self.assertTrue(countries.__contains__('Czech Republic'))
        self.assertTrue(countries.__contains__('Croatia'))

    def test_readsValuesWithSingleRelationshipNoDuplicates(self):
        values = values_with_single_relationship(
            set(),
            dictionary_from_json_file(self.test_items, self.top_key),
            'Location',
            'Country'
        )
        self.assertTrue(4, len(values))
        self.assertTrue(values.__contains__(('Sunny South', 'USA')))
        self.assertTrue(values.__contains__(('Ohio - The Buckeye State!', 'USA')))
        self.assertTrue(values.__contains__(('Sunny South', 'Czech Republic')))
        self.assertTrue(values.__contains__(('SEE MY OTHER AUCTIONS', 'Croatia')))

    def test_extractsValuesWithManyRelationships(self):
        users = values_with_many_collocated_relationships(
            dict(),
            dictionary_from_json_file(
                self.test_items,
                self.top_key
            ),
            ['Rating', 'Location', 'Country'],
            'UserID'
        )
        self.assertEqual(
            3,
            len(users)
        )
        self.assertEqual(
            (
                '223',
                'Sunny South',
                'USA'
            ),
            (
                users['torrisattic']['Rating'],
                users['torrisattic']['Location'],
                users['torrisattic']['Country']
            )
        )
        self.assertEqual(
            (
                '223',
                'Sunny South',
                'USA'
            ),
            (
                users['bidder1']['Rating'],
                users['bidder1']['Location'],
                users['bidder1']['Country']
            )
        )
        self.assertEqual(
            (
                '100',
                'SEE MY OTHER AUCTIONS',
                'Croatia'
            ),
            (
                users['dpaustintx']['Rating'],
                users['dpaustintx']['Location'],
                users['dpaustintx']['Country']
            )
        )


    def test_extractsValuesWithDislocatedRelationships(self):
        users = values_with_dislocated_relationships(
            dict(),
            dictionary_from_json_file(
                self.test_items,
                self.top_key
            ),
            ['Rating'],
            'Seller',
            ['Location', 'Country'],
            'UserID'

        )
        self.assertEqual(
            3,
            len(users)
        )
        self.assertEqual(
            (
                '85',
                'Sunny South',
                'Czech Republic'
            ),
            (
                users['z00ke0pler']['Rating'],
                users['z00ke0pler']['Location'],
                users['z00ke0pler']['Country']
            )
        )
        self.assertEqual(
            (
                '178',
                'Ohio - The Buckeye State!',
                'USA'
            ),
            (
                users['dog415@msn.com']['Rating'],
                users['dog415@msn.com']['Location'],
                users['dog415@msn.com']['Country']
            )
        )
        self.assertEqual(
            (
                '21',
                'Sunny South',
                'USA'
            ),
            (
                users['do-south']['Rating'],
                users['do-south']['Location'],
                users['do-south']['Country']
            )
        )

    def test_shouldAddNewCategoriesToList(self):
        categories = values_from_json_file(
            [
                'Collectibles',
                'cat4',
                'cat5',
            ],
            dictionary_from_json_file(
                self.test_items,
                self.top_key
            ),
            'Category'
        )
        self.assertEqual(
            len(categories),
            6
        )
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

    def test_extractsNestedValues(self):
        json_object = dict(
            {
                'Key':
                    [
                        'value1',
                        'value2'
                    ],
                'SingleSub':
                    {
                        'Not applicable': 'red herring',
                        'Key': 'value3'
                    },
                'DoubleSub':
                    {
                        'Sub':
                            {
                                'Key':
                                    [
                                        'value4',
                                        'value5'
                                    ],
                                'n/a': 'nope'
                            }
                    },
                'SubObjectList':
                    [
                        {
                            'Object':
                                {
                                    'Key': 'value6',
                                    'NA': 'notapp'
                                }
                        },
                        {
                            'Object':
                                {
                                    'Key':
                                        [
                                            'value7',
                                            'value8'
                                        ]
                                }
                        }
                    ]

            }
        )
        values = extract_nested_values_from_json_with_key(
            [],
            json_object,
            'Key'
        )
        self.assertEqual(
            8,
            len(values)
        )
        self.assertTrue(
            values.__contains__(
                'value1'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value2'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value3'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value4'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value5'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value6'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value7'
            )
        )
        self.assertTrue(
            values.__contains__(
                'value8'
            )
        )

    def test_extractObjectsFromJSONFile(self):
        self.assertEqual(
            list,
            type(
                dictionary_from_json_file(
                    self.test_items,
                    self.top_key
                )
            )
        )


if __name__ == '__main__':
    unittest.main()
