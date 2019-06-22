import unittest
from test.TestDatabase import create_test_database


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = create_test_database()
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_import_all_categories_with_unique_id(self):
        self.assertEqual(
            1042,
            self.cursor.execute(
                "select count(*) "
                "from category;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from category "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_countries_with_unique_id(self):
        self.assertEqual(
            44,
            self.cursor.execute(
                "select count(*) "
                "from country;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from country "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_locations_with_unique_id(self):
        self.assertEqual(
            9007,
            self.cursor.execute(
                "select count(*) "
                "from location;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from location "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_auction_category_joins(self):
        self.assertEqual(
            90269,
            self.cursor.execute(
                "select count(*) "
                "from join_auction_category;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from join_auction_category "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_no_two_users_share_same_id(self):
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from user "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_all_bids_import(self):
        self.assertEqual(
            9874,
            self.cursor.execute(
                "select count(*) "
                "from bid;"
            ).fetchall()[0][0]
        )

    def test_bid_composite_primary_key_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select auction_id, user_id, amount "
                "from bid "
                "group by auction_id, user_id, amount "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_all_auctions_import(self):
        self.assertEqual(
            19532,
            self.cursor.execute(
                "select count(*) "
                "from auction;"
            ).fetchall()[0][0]
        )

    def test_auction_id_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.executescript(
                "select id "
                "from auction "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )


if __name__ == '__main__':
    unittest.main()
