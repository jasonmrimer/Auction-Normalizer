import unittest

from IngestJSON import *


class MyTestCase(unittest.TestCase):
    auction_filepaths = [
        'TestItems',
        'TestItems2'
    ]
    dat_filepath = 'test_values.dat'

    def test_convertsValueWithNoRelationship(self):
        convert_json_to_dat(
            self.auction_filepaths,
            self.dat_filepath,
            'Items',
            'Category'
        )
        file = open(self.dat_filepath, 'r')
        self.assertEqual(
            file.read(),
            '"1"|"Collectibles"\n'
            '"2"|"Kitchenware"\n'
            '"3"|"Test"\n'
            '"4"|"Dept 56"\n'
            '"5"|"cat5"\n'
            '"6"|"cat6"\n'
            '"7"|"cat7"'
        )
        file.close()

    def test_convertsValueWithOneRelationship(self):
        convert_json_to_dat(
            self.auction_filepaths,
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

    def test_ingest_bidders(self):
        ingest_bidders(
            self.auction_filepaths,
            self.dat_filepath
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('"torrisattic"|"223"|"Sunny South"|"USA"'))
        self.assertTrue(contents.__contains__('"bidder1"|"223"|"Sunny South"|"NULL"'))
        self.assertTrue(contents.__contains__('"dpaustintx"|"100"|"SEE MY OTHER AUCTIONS"|"Croatia"'))
        self.assertTrue(contents.__contains__('"test_user1"|"223"|"Happy Holidays"|"USA"'))
        self.assertTrue(contents.__contains__('"test_user2"|"100"|"SEE MY OTHER AUCTIONS"|"Japan"'))
        file.close()

    def test_ingest_users(self):
        ingest_users(
            self.auction_filepaths,
            self.dat_filepath
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('"torrisattic"|"223"|"Sunny South"|"USA"'))
        self.assertTrue(contents.__contains__('"bidder1"|"223"|"Sunny South"|"NULL"'))
        self.assertTrue(contents.__contains__('"dpaustintx"|"100"|"SEE MY OTHER AUCTIONS"|"Croatia"'))
        self.assertTrue(contents.__contains__('"test_user1"|"223"|"Happy Holidays"|"USA"'))
        self.assertTrue(contents.__contains__('"test_user2"|"100"|"SEE MY OTHER AUCTIONS"|"Japan"'))
        self.assertTrue(contents.__contains__('"german-guy"|"21"|"Sunny South"|"Germany"'))
        self.assertTrue(contents.__contains__('"dog415@msn.com"|"178"|"Ohio - The Buckeye State!"|"USA"'))
        self.assertTrue(contents.__contains__('"z00ke0pler"|"85"|"Sunny South"|"Czech Republic"'))
        self.assertTrue(contents.__contains__('"test_user3"|"85"|"Elwood,New York"|"USA"'))
        self.assertTrue(contents.__contains__('"do-south"|"21"|"Sunny South"|"USA"'))
        file.close()


    def test_ConvertsValuesWithManyDislocatedRelationships(self):
        ingest_related_dislocated_values_from_files(
            self.auction_filepaths,
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

    def test_IngestBids(self):
        ingest_bids(
            self.auction_filepaths,
            self.dat_filepath
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(contents.__contains__('"1045769659"|"torrisattic"|"2001-12-10 10:23:53"|"14.50"'))
        self.assertTrue(contents.__contains__('"1045769659"|"bidder1"|"2001-12-10 10:23:53"|"14.50"'))
        self.assertTrue(contents.__contains__('"1045770692"|"dpaustintx"|"2001-12-10 10:25:30"|"13.99"'))
        self.assertTrue(contents.__contains__('"1045769659777"|"test_user1"|"2001-12-10 10:23:53"|"14.50"'))
        self.assertTrue(contents.__contains__('"1045770692777"|"test_user2"|"2001-12-10 10:25:30"|"13.99"'))
        file.close()

    def test_IngestAuctions(self):
        ingest_auctions(
            self.auction_filepaths,
            self.dat_filepath,
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(
            contents.__contains__(
                '"1045769659"'
                '|"SPRINGERLE COOKIE BOARD ** NO RESERVE**"'
                '|"14.50"'
                '|"2001-12-08 16:23:53"'
                '|"2001-12-15 16:23:53"'
                '|"Wood Springerle cookie borad depicting a FISH, flowers & birds. It '
                'will imprint 8 designs in all. It is app. 3"" x 8"" in size. Nice '
                'patina...no cracks. Payment Details See item description and Payment '
                'Instructions, or contact seller for more information. Payment '
                'Instructions Contact must be made within 3 days of close of auction. '
                'Item must be paid for within 10 days by PayPal or Money Order for next '
                'day shipping. Personal checks must clear bank prior to shipping. '
                'International buyers must pay by PayPal or Postal Money Orders for US '
                'dollars. Buyer to pay shipping/handling and insurance if desired. '
                'Satisfaction is guaranteed if notified within 3 days of receipt of '
                'item."'
                '|"NULL"'
                '|"do-south"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045770692"'
                '|"Lanam Co. Lid to fit Longaberger Envelope NEW"'
                '|"13.99"'
                '|"2001-12-08 16:25:30"'
                '|"2001-12-15 16:25:30"'
                '|"You are bidding on an oak lid made by the Lanam Company to fit the '
                'Longaberger Envelope Basket. This lid has never been used or '
                'displayed, stored in my smoke free home. It features laser engraving '
                'and hand painting and is just what you need to complete your basket. '
                'Buyer to pay actual shipping. I will accept money order, '
                'paypal or personal check but will hold until check clears. Over the '
                'next few days, I will be selling several baskets and lids from my '
                'personal collection. Most have never been used or displayed. Be sure '
                'to check my other auctions. Feel free to email me with questions. '
                'Thanks for lookig!"'
                '|"NULL"'
                '|"dog415@msn.com"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1046316741"'
                '|"NP Acc,I\'LL NEED MORE TOYS,**NRFB**"'
                '|"5.00"'
                '|"2001-12-09 16:41:48"'
                '|"2001-12-16 16:41:48"'
                '|"* MINT! Never Removed From Box. Original packing and wrapping. Two piece set. '
                'Wonderful NEW CONCEPT-Porcelain and Acrylic. You have to see this one! Issued in '
                '1995 and retired in 1998, this is one of the earlier accessories issued. Box and '
                'sleeve are in very good condition. These pieces are in MINT condition. No chips,'
                'cracks or repairs. From a smoke-free environment. Selling many pieces from North '
                'Pole collection. Check out my other auctions. Multiple purchase will be shipped '
                'together to save you postage. Please email me with the pieces you want shipped '
                'together. I accept PAYPAL, BILLPOINT, MONEY ORDERS, Personal Checks(must clear '
                'before shipping). I will ship all packages the next day. Priority Mail (2-3 days) '
                'w/ Delivery Confirmation and insurance $6.00. May your holidays be healthy and '
                'happy. Looking forward to hearing from you. Good Luck!!*LOW, LOW RESERVE! TWO WAYS '
                'TO GO. EITHER BUY IT NOW FOR 20% OFF THE GREENBOOK VALUE 0R WIN IT AT THE EVEN '
                'LOWER RESERVE PRICE. EITHER WAY YOU CAN\'T LOSE"'
                '|"30.52"'
                '|"z00ke0pler"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045769659777"'
                '|"SPRINGERLE COOKIE BOARD ** NO RESERVE**"'
                '|"14.50"'
                '|"2001-12-08 16:23:53"'
                '|"2001-12-15 16:23:53"'
                '|"Wood Springerle cookie borad depicting a FISH, flowers & birds. It '
                'will imprint 8 designs in all. It is app. 3"" x 8"" in size. Nice '
                'patina...no cracks. Payment Details See item description and Payment '
                'Instructions, or contact seller for more information. Payment '
                'Instructions Contact must be made within 3 days of close of auction. '
                'Item must be paid for within 10 days by PayPal or Money Order for next '
                'day shipping. Personal checks must clear bank prior to shipping. '
                'International buyers must pay by PayPal or Postal Money Orders for US '
                'dollars. Buyer to pay shipping/handling and insurance if desired. '
                'Satisfaction is guaranteed if notified within 3 days of receipt of '
                'item."'
                '|"NULL"'
                '|"german-guy"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045770692777"'
                '|"Lanam Co. Lid to fit Longaberger Envelope NEW"'
                '|"13.99"'
                '|"2001-12-08 16:25:30"'
                '|"2001-12-15 16:25:30"'
                '|"You are bidding on an oak lid made by the Lanam Company to fit the '
                'Longaberger Envelope Basket. This lid has never been used or '
                'displayed, stored in my smoke free home. It features laser engraving '
                'and hand painting and is just what you need to complete your basket. '
                'Buyer to pay actual shipping. I will accept money order, '
                'paypal or personal check but will hold until check clears. Over the '
                'next few days, I will be selling several baskets and lids from my '
                'personal collection. Most have never been used or displayed. Be sure '
                'to check my other auctions. Feel free to email me with questions. '
                'Thanks for lookig!"'
                '|"NULL"'
                '|"dog415@msn.com"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1046316741777"'
                '|"NP Acc,I\'LL NEED MORE TOYS,**NRFB**"'
                '|"5.00"'
                '|"2001-12-09 16:41:48"'
                '|"2001-12-16 16:41:48"'
                '|"* MINT! Never Removed From Box. Original packing and wrapping. Two piece set. '
                'Wonderful NEW CONCEPT-Porcelain and Acrylic. You have to see this one! Issued in '
                '1995 and retired in 1998, this is one of the earlier accessories issued. Box and '
                'sleeve are in very good condition. These pieces are in MINT condition. No chips,'
                'cracks or repairs. From a smoke-free environment. Selling many pieces from North '
                'Pole collection. Check out my other auctions. Multiple purchase will be shipped '
                'together to save you postage. Please email me with the pieces you want shipped '
                'together. I accept PAYPAL, BILLPOINT, MONEY ORDERS, Personal Checks(must clear '
                'before shipping). I will ship all packages the next day. Priority Mail (2-3 days) '
                'w/ Delivery Confirmation and insurance $6.00. May your holidays be healthy and '
                'happy. Looking forward to hearing from you. Good Luck!!*LOW, LOW RESERVE! TWO WAYS '
                'TO GO. EITHER BUY IT NOW FOR 20% OFF THE GREENBOOK VALUE 0R WIN IT AT THE EVEN '
                'LOWER RESERVE PRICE. EITHER WAY YOU CAN\'T LOSE"'
                '|"30.52"'
                '|"test_user3"'
            )
        )
        file.close()

    def test_join_auction_category(self):
        join_auction_category(
            self.auction_filepaths,
            self.dat_filepath
        )
        file = open(self.dat_filepath, 'r')
        contents = file.read()
        self.assertTrue(
            contents.__contains__(
                '"1045769659"'
                '|"Collectibles"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045769659"'
                '|"Kitchenware"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045770692"'
                '|"Test"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1046316741"'
                '|"Collectibles"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1046316741"'
                '|"Dept 56"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045769659777"'
                '|"cat5"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045769659777"'
                '|"cat6"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1045770692777"'
                '|"cat5"'
            )
        )
        self.assertTrue(
            contents.__contains__(
                '"1046316741777"'
                '|"cat7"'
            )
        )
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
                    ('1', '1'),
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
