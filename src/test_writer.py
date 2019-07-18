import unittest
from Writer import *


class MyTestCase(unittest.TestCase):
    dat_filepath = 'test_values.dat'

    def test_new_line(self):
        self.assertEqual(
            '\n',
            new_line([1, 2, 3])
        )
        self.assertEqual(
            '',
            new_line([])
        )

    def test_writeListToFile(self):
        write_values_to_dat(
            [
                'Val1',
                'Val2',
                'Val3'
            ],
            self.dat_filepath
        )
        file = open(
            self.dat_filepath,
            'r'
        )
        self.assertEqual(
            file.read(),
            '"1"|"Val3"\n'
            '"2"|"Val2"\n'
            '"3"|"Val1"'
        )
        file.close()

    def test_writeSetToFile(self):
        write_values_to_dat(
            {
                (
                    'Key1',
                    'Val1'
                ),
                (
                    'Key"2',
                    'Val2'
                ),
                (
                    'Key3',
                    'Val3'
                )
            },
            self.dat_filepath
        )
        file = open(
            self.dat_filepath,
            'r'
        )
        contents = file.read()
        self.assertTrue(
            contents.__contains__(
                '"Key1"|"Val1"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"Key""2"|"Val2"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"Key3"|"Val3"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '1|'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '2|'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '3|'
            )
        )
        file.close()

    def test_writeSingleValueDictionaryToFile(self):
        dictionary = dict()
        dictionary['item1'] = 'value"1'
        dictionary['item2'] = 'value2'
        dictionary['item"3'] = 'value"3'
        write_values_to_dat(
            dictionary,
            self.dat_filepath
        )
        file = open(
            self.dat_filepath,
            'r'
        )
        contents = file.read()
        self.assertEqual(
            contents,
            '"item""3"|"value""3"\n'
            '"item2"|"value2"\n'
            '"item1"|"value""1"'
        )
        file.close()

    def test_writeDictionaryOfDictionariesToFile(self):
        dictionary = {
            'item1':
                {
                    'subkey1': 'subval"1.1',
                    'subkey2': 'subval1.2'
                },

            'item"2':
                {
                    'subkey1': 'subval2.1',
                    'subkey2': 'subval"2.2'
                },
            'item3':
                {
                    'subkey1': 'subval3.1',
                    'subkey2': 'subval"3.2'
                }
        }
        write_values_to_dat(
            dictionary,
            self.dat_filepath
        )
        file = open(
            self.dat_filepath,
            'r'
        )
        contents = file.read()
        self.assertEqual(
            contents,
            '"item3"|"subval3.1"|"subval""3.2"\n'
            '"item""2"|"subval2.1"|"subval""2.2"\n'
            '"item1"|"subval""1.1"|"subval1.2"'
        )
        file.close()

    def test_writes_bids(self):
        bids = {
            ('1045770692', 'torrisattic', 'Dec-10-01 10:23:53', '$14.50'):
                {
                    'ItemID': '1045770692',
                    'Bidder': {
                        'UserID': 'torrisattic',
                        'Rating': '223',
                        'Location': 'Sunny South',
                        'Country': 'USA'
                    },
                    'Time': 'Dec-10-01 10:23:53',
                    'Amount': '$14.50'
                },
            ('1045769659', 'dpaustintx', 'Dec-10-01 10:25:30', '$13.99'):
                {
                    'ItemID': '1045769659',
                    'Bidder': {
                        'UserID': 'dpaustintx',
                        'Rating': '100',
                        'Location': 'SEE MY OTHER AUCTIONS',
                        'Country': 'Croatia'
                    },
                    'Time': 'Dec-10-01 10:25:30',
                    'Amount': '$13.99'
                },

        }
        write_bids_to_dat(
            bids,
            self.dat_filepath
        )
        file = open(
            self.dat_filepath,
            'r'
        )
        contents = file.read()
        self.assertEqual(
            contents,
            '"1045769659"|"dpaustintx"|"2001-12-10 10:25:30"|"13.99"\n'
            '"1045770692"|"torrisattic"|"2001-12-10 10:23:53"|"14.50"'
        )
        file.close()

    def test_addsQuotationMarkToExistingQuotation(self):
        self.assertEqual(
            '29"" bike with 2"" tires',
            stringify('29" bike with 2" tires')
        )

    def test_transformsMonthToValue(self):
        self.assertEqual(
            '08',
            json_month_to_sqlite('Aug')
        )

    def test_transformDateToSQL(self):
        self.assertEqual(
            '2002-01-01 11:12:13',
            json_date_to_sqlite('Jan-01-02 11:12:13')
        )

    def test_transformDollarToFloat(self):
        self.assertEqual(
            '',
            json_cash_to_sql('')
        )
        self.assertEqual(
            '3.50',
            json_cash_to_sql('$3.50')
        )
        self.assertEqual(
            '1234.56',
            json_cash_to_sql('$1234.56')
        )


if __name__ == '__main__':
    unittest.main()
