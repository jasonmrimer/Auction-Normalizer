import sqlite3
import sys
import unittest

from test_helpers import create_im_memory_database


class TestDatabaseCase(unittest.TestCase):
    REAL_DATABASE = None

    def setUp(self) -> None:
        if self.REAL_DATABASE is not None:
            self.conn = sqlite3.connect(f"{self.REAL_DATABASE}")
        else:
            self.conn = create_im_memory_database()
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

    def test_import_all_countries(self):
        self.assertEqual(
            44,
            self.cursor.execute(
                "select count(*) "
                "from country;"
            ).fetchall()[0][0]
        )

    def test_import_all_locations(self):
        self.assertEqual(
            9007,
            self.cursor.execute(
                "select count(*) "
                "from location;"
            ).fetchall()[0][0]
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
            self.cursor.execute(
                "select id "
                "from join_auction_category "
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

    def test_all_auctions_import(self):
        self.assertEqual(
            19532,
            self.cursor.execute(
                "select count(*) "
                "from auction;"
            ).fetchall()[0][0]
        )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestDatabaseCase.REAL_DATABASE = sys.argv.pop()
    unittest.main()
