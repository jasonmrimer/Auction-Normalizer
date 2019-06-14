import unittest
from Writer import *


class MyTestCase(unittest.TestCase):
    dat_filepath = 'test_values.dat'

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
            '1|Val1\n'
            '2|Val2\n'
            '3|Val3'
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

    def test_addsQuotationMarkToExistingQuotation(self):
        self.assertEqual(
            '29"" bike with 2"" tires',
            stringify('29" bike with 2" tires')
        )

if __name__ == '__main__':
    unittest.main()