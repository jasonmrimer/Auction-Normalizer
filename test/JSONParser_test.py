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
            list_of_objects_from_json_file(
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
            list_of_objects_from_json_file(
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
            list_of_objects_from_json_file(self.test_items, self.top_key),
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
            {
                'user1': {
                    'Rating': '1',
                    'Location': 'loc1',
                    'Country': 'country1'
                }
            },
            list_of_objects_from_json_file(
                self.test_items,
                self.top_key
            ),
            ['Rating', 'Location', 'Country'],
            'UserID'
        )
        self.assertEqual(
            4,
            len(users)
        )
        self.assertEqual(
            (
                '1',
                'loc1',
                'country1'
            ),
            (
                users['user1']['Rating'],
                users['user1']['Location'],
                users['user1']['Country']
            )
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
            list_of_objects_from_json_file(
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
            list_of_objects_from_json_file(
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
                list_of_objects_from_json_file(
                    self.test_items,
                    self.top_key
                )
            )
        )

    def test_getBids(self):
        bids = get_bids(
            {},
            list_of_objects_from_json_file(
                self.test_items,
                self.top_key
            )
        )
        self.assertEqual(
            3,
            len(bids)
        )
        self.assertEqual(
            {
                'ItemID': '1045770692',
                'Bidder': {
                    'UserID': 'dpaustintx',
                    'Rating': '100',
                    'Location': 'SEE MY OTHER AUCTIONS',
                    'Country': 'Croatia'
                },
                'Time': 'Dec-10-01 10:25:30',
                'Amount': '$13.99'
            },
            bids[('1045770692', 'dpaustintx', 'Dec-10-01 10:25:30', '$13.99')]
        )
        self.assertEqual(
            {
                'ItemID': '1045769659',
                'Bidder': {
                    'UserID': 'torrisattic',
                    'Rating': '223',
                    'Location': 'Sunny South',
                    'Country': 'USA'
                },
                'Time': 'Dec-10-01 10:23:53',
                'Amount': '$14.50'
            },
            bids[('1045769659', 'torrisattic', 'Dec-10-01 10:23:53', '$14.50')]
        )
        self.assertEqual(
            {
                'ItemID': '1045769659',
                'Bidder': {
                    'UserID': 'bidder1',
                    'Rating': '223',
                    'Location': 'Sunny South',
                    'Country': 'USA'
                },
                'Time': 'Dec-10-01 10:23:53',
                'Amount': '$14.50'
            },
            bids[('1045769659', 'bidder1', 'Dec-10-01 10:23:53', '$14.50')]
        )

    def test_get_auctions(self):
        auctions = get_auctions(
            dict(),
            list_of_objects_from_json_file(
                self.test_items,
                'Items'
            )
        )
        self.assertEqual(
            3,
            len(auctions)
        )
        self.assertEqual(
            {
                'Name': 'SPRINGERLE COOKIE BOARD ** NO RESERVE**',
                'First_Bid': '$14.50',
                'Buy_Price': None,
                'Started': 'Dec-08-01 16:23:53',
                'Ends': 'Dec-15-01 16:23:53',
                'Seller': 'do-south',
                'Description': 'Wood Springerle cookie borad depicting a FISH, flowers & birds. It will imprint 8 '
                               'designs in all. It is app. 3\" x 8\" in size. Nice patina...no cracks. Payment '
                               'Details See item description and Payment Instructions, or contact seller for more '
                               'information. Payment Instructions Contact must be made within 3 days of close of '
                               'auction. Item must be paid for within 10 days by PayPal or Money Order for next day '
                               'shipping. Personal checks must clear bank prior to shipping. International buyers '
                               'must pay by PayPal or Postal Money Orders for US dollars. Buyer to pay '
                               'shipping/handling and insurance if desired. Satisfaction is guaranteed if notified '
                               'within 3 days of receipt of item.'
            },
            auctions['1045769659']
        )
        self.assertEqual(
            {
                'Name': 'Lanam Co. Lid to fit Longaberger Envelope NEW',
                'First_Bid': '$13.99',
                'Buy_Price': None,
                'Started': 'Dec-08-01 16:25:30',
                'Ends': 'Dec-15-01 16:25:30',
                'Seller': 'dog415@msn.com',
                'Description': 'You are bidding on an oak lid made by the Lanam Company to fit the Longaberger '
                               'Envelope Basket. This lid has never been used or displayed, stored in my smoke free '
                               'home. It features laser engraving and hand painting and is just what you need to '
                               'complete your basket. Buyer to pay actual shipping. I will accept money order, '
                               'paypal or personal check but will hold until check clears. Over the next few days, '
                               'I will be selling several baskets and lids from my personal collection. Most have '
                               'never been used or displayed. Be sure to check my other auctions. Feel free to email '
                               'me with questions. Thanks for lookig!'
            },
            auctions['1045770692']
        )

    def test_join(self):
        joins = join(
            {
                (
                    'item1',
                    'cat1'
                )
            },
            list_of_objects_from_json_file(
                self.test_items,
                self.top_key
            )
        )
        self.assertTrue(
            joins ==
            {
                ('item1', 'cat1'),
                ('1045769659', 'Collectibles'),
                ('1045769659', 'Kitchenware'),
                ('1045770692', 'Test'),
                ('1046316741', 'Collectibles'),
                ('1046316741', 'Dept 56'),
            }
        )


if __name__ == '__main__':
    unittest.main()
