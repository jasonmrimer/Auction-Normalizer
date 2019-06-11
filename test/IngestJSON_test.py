import unittest

from IngestJSON import *


class MyTestCase(unittest.TestCase):
    test_filepaths = [
        'TestItems',
        'TestItems2'
    ]
    dat_filepath = 'test_values.dat'

    def test_convertsValueWithNoRelationship(self):
        convert_json_to_dat(
            self.test_filepaths,
            self.dat_filepath,
            'Items',
            'Category'
        )
        file = open(self.dat_filepath, 'r')
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

    def test_convertsValueWithOneRelationship(self):
        convert_json_to_dat([
            'TestItems',
            'TestItems2'
        ],
            self.dat_filepath,
            'Items',
            'Location',
            'Country'
        )
        file = open(self.dat_filepath, 'r')
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
        self.assertTrue(contents.__contains__('|"Sunny South"|"USA"'))
        self.assertTrue(contents.__contains__('|"SEE MY OTHER AUCTIONS"|"Croatia"'))
        self.assertTrue(contents.__contains__('|"Ohio - The Buckeye State!"|"USA"'))
        self.assertTrue(contents.__contains__('|"Sunny South"|"Czech Republic"'))
        self.assertTrue(contents.__contains__('|"Happy Holidays"|"USA"'))
        self.assertTrue(contents.__contains__('|"Sunny South"|"Germany"'))
        self.assertTrue(contents.__contains__('|"SEE MY OTHER AUCTIONS"|"Japan"'))
        self.assertTrue(contents.__contains__('|"Elwood,New York"|"USA"'))
        file.close()

    def test_ConvertsValuesWithManyCollocatedRelationships(self):
        ingest_related_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            self.dat_filepath,
            'Items',
            ['Rating', 'Location', 'Country'],
            'UserID'
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('"torrisattic"|"223"|"Sunny South"|"USA"'))
        self.assertTrue(contents.__contains__('"bidder1"|"223"|"Sunny South"|"USA"'))
        self.assertTrue(contents.__contains__('"dpaustintx"|"100"|"SEE MY OTHER AUCTIONS"|"Croatia"'))
        self.assertTrue(contents.__contains__('"test_user1"|"223"|"Happy Holidays"|"USA"'))
        self.assertTrue(contents.__contains__('"test_user2"|"100"|"SEE MY OTHER AUCTIONS"|"Japan"'))
        file.close()

    def test_ConvertsValuesWithManyDislocatedRelationships(self):
        ingest_related_dislocated_values_from_files([
            'TestItems',
            'TestItems2'
        ],
            self.dat_filepath,
            'Items',
            ['Rating'],
            'Seller',
            ['Location', 'Country'],
            'UserID'
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('"german-guy"|"21"|"Sunny South"|"Germany"'))
        self.assertTrue(contents.__contains__('"dog415@msn.com"|"178"|"Ohio - The Buckeye State!"|"USA"'))
        self.assertTrue(contents.__contains__('"z00ke0pler"|"85"|"Sunny South"|"Czech Republic"'))
        self.assertTrue(contents.__contains__('"test_user3"|"85"|"Elwood,New York"|"USA"'))
        self.assertTrue(contents.__contains__('"do-south"|"21"|"Sunny South"|"USA"'))
        file.close()

    def test_printsMaxLengthFromList(self):
        self.assertEqual(
            9,
            max_length(
                [
                    '1',
                    '12',
                    '12345',
                    '123456789'
                ]
            )
        )

    def test_printsMaxLengthFromTwoValueSet(self):
        self.assertEqual(
            9,
            max_length(
                {
                    ('1','1'),
                    ('12', '12'),
                    ('12345', '12'),
                    ('123456789', '12')
                }
            )
        )

    def test_printsMaxLengthFromSimpleDictionary(self):
        self.assertEqual(
            9,
            max_length(
                {
                    '1': '1',
                    '2': '12',
                    '3': '12',
                    '4': '123456789'
                }
            )
        )

    def test_printsMaxLengthFromExistingMax(self):
        self.assertEqual(
            9,
            max_length(
                '123456789',
                8
            )
        )


if __name__ == '__main__':
    unittest.main()
