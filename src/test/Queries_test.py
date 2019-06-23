import unittest

from test.TestDatabase import create_test_database


class QueriesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = create_test_database()
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_query_1_number_of_users(self):
        file = open('../src/queries/query1.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            13422,
            users[0][0]
        )

    def test_query_2_users_from_new_york(self):
        file = open('../src/queries/query2.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            80,
            users[0][0]
        )

    def test_query_3_auctions_with_four_categories(self):
        file = open('../src/queries/query3.sql')
        sql = file.read()
        file.close()
        auctions = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            8365,
            auctions[0][0]
        )

    def test_query_4_auction_with_highest_bid(self):
        file = open('../src/queries/query4.sql')
        sql = file.read()
        file.close()
        auctions = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            1046740686,
            auctions[0][0]
        )

    def test_query_5_sellers_with_ratings_over_1000(self):
        file = open('../src/queries/query5.sql')
        sql = file.read()
        file.close()
        sellers = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            3130,
            sellers[0][0]
        )

    def test_query_6_users_that_are_bidders_and_sellers(self):
        file = open('../src/queries/query6.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            6717,
            users[0][0]
        )

    def test_query_7_categories_with_bids_over_100(self):
        file = open('../src/queries/query7.sql')
        sql = file.read()
        file.close()
        categories = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            150,
            categories[0][0]
        )


if __name__ == '__main__':
    unittest.main()
