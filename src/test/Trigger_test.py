import sqlite3
import unittest
import glob
import os

from test.TestDatabase import create_test_database

from test.helper import *


class TestTriggers(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = create_test_database()
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_new_bid_with_existing_user(self):
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]
        auction_id = self.cursor.execute(
            "select id "
            "from auction;"
        ).fetchone()[0]
        self.cursor.execute(
            f"insert into bid "
            f"values ({auction_id}, '{user_id}', '{now()}', 7.75);"

        )
        self.assertEqual(
            9875,
            self.conn.execute(
                "select count(*) "
                "from bid;"
            ).fetchall()[0][0]
        )

    def test_bidding_with_new_user_triggers_user_creation(self):
        self.add_trigger('../src/triggers/trigger1_add.sql')
        new_user = 'newuserwhoisdefinitelynotalreadyinthedatabase'
        self.assertEqual(
            [],
            self.cursor.execute(
                f'select * '
                f'from user '
                f'where id=\'{new_user}\';'
            ).fetchall()
        )

        auction_id = self.cursor.execute(
            "select id "
            "from auction;"
        ).fetchone()[0]
        self.cursor.execute(
            f"insert into bid "
            f"values ({auction_id}, '{new_user}', '{now()}', 7.75);"
        )

        self.assertEqual(
            1,
            len(
                self.cursor.execute(
                    f'select * '
                    f'from user '
                    f'where id=\'{new_user}\';'
                ).fetchall()
            )
        )

    def test_new_auction_with_new_seller_triggers_user_creation(self):
        self.add_trigger('../src/triggers/trigger2_add.sql')
        new_seller = 'newuserwhoisdefinitelynotalreadyinthedatabase'
        self.assertEqual(
            [],
            self.cursor.execute(
                f'select * '
                f'from user '
                f'where id=\'{new_seller}\';'
            ).fetchall()
        )

        new_auction = 123456789
        self.assertEqual(
            [],
            self.cursor.execute(
                f'select * '
                f'from auction '
                f'where id=\'{new_auction}\';'
            ).fetchall()
        )
        self.cursor.execute(
            f"insert into auction "
            f"values ("
            f"{new_auction}, "
            f"'name of the auction', "
            f"7.75, "
            f"'{now()}', "
            f"'{now(2)}', "
            f"'description of the auction', "
            f"70.00, "
            f"'{new_seller}', "
            f"0, "
            f"0 "
            f");"
        )

        self.assertEqual(
            1,
            len(
                self.cursor.execute(
                    f'select * '
                    f'from user '
                    f'where id=\'{new_seller}\';'
                ).fetchall()
            )
        )

    def test_auction_current_price_always_matches_most_recent_bid_for_auction(self):
        self.add_trigger('../src/triggers/trigger3_add.sql')
        auction_id = self.cursor.execute(
            "select id "
            "from auction "
            "where highest_bid < 123456;"
        ).fetchone()[0]
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{now()}', "
            f"123456"
            f");"
        )

        self.assertEqual(
            123456,
            self.cursor.execute(
                f"select highest_bid "
                f"from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{now(1)}', "
            f"1"
            f");"
        )

        self.assertEqual(
            1,
            self.cursor.execute(
                f"select highest_bid "
                f"from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

    def test_no_bids_belong_to_auction_sellers(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select * "
                "from bid "
                "where user_id = "
                "(select seller_id from auction where id = bid.auction_id);"
            ).fetchall()
        )

    def test_seller_may_not_bid_on_auction(self):
        self.add_trigger('../src/triggers/trigger4_add.sql')
        bid_count = count_from_table(
            self.cursor,
            'bid'
        )

        auction = self.cursor.execute(
            "select id, seller_id "
            "from auction;"
        ).fetchone()
        auction_id = auction[0]
        seller_id = auction[1]

        try:
            self.cursor.execute(
                f"insert into bid "
                f"values ("
                f"{auction_id}, "
                f"'{seller_id}', "
                f"'{now()}', "
                f"123456"
                f")"
            )
            self.assertTrue(
                False,
                "Database failed to deny bid on an auction from the seller of that auction."
            )
        except sqlite3.IntegrityError as e:
            self.assertEqual(
                str(e),
                "Sellers may not bid on their own auction."
            )

        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            ),
            "Database allowed new bid from seller of auction."
        )

    def test_all_bids_occur_within_auction_start_and_end(self):
        self.add_trigger('../src/triggers/trigger5_add.sql')
        bid_count = count_from_table(
            self.cursor,
            'bid'
        )

        self.assertEqual(
            [],
            self.cursor.execute(
                "select * "
                "from bid "
                "where "
                "time < (select start from auction where id = auction_id)"
                "and "
                "time > ( select end from auction where id = auction_id);"
            ).fetchall()
        )
        auction = self.cursor.execute(
            "select id, start, end "
            "from auction;"
        ).fetchone()
        auction_id = auction[0]
        auction_start = auction[1]
        auction_end = auction[2]
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{auction_start}',"
            f"123456"
            f");"
        )

        bid_count += 1
        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

        try:
            self.cursor.execute(
                f"insert into bid "
                f"values ("
                f"{auction_id}, "
                f"'{user_id}', "
                f"'{add_hours_to_datestring(auction_start, -4)}',"
                f"123456"
                f");"
            )
            self.assertTrue(
                False,
                "Databased failed to check bid time is after auction start"
            )
        except sqlite3.IntegrityError as e:
            self.assertEqual(
                "Bids must be after the auction starts.",
                str(e)
            )

        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{auction_end}',"
            f"1234567"
            f");"
        )
        bid_count += 1
        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

        try:
            self.cursor.execute(
                f"insert into bid "
                f"values ("
                f"{auction_id}, "
                f"'{user_id}', "
                f"'{add_hours_to_datestring(auction_end, 4)}',"
                f"123456"
                f");"
            )
            self.assertTrue(
                False,
                "Databased failed to check bid time is before auction end"
            )
        except sqlite3.IntegrityError as e:
            self.assertEqual(
                "Bids must be before the auction ends.",
                str(e)
            )
        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

    def test_all_auctions_maintain_accurate_number_of_bids(self):
        self.add_trigger("../src/triggers/trigger6_add.sql")
        seller_id = "testuser1234567890"
        bidder_id = "987654321testuser"
        self.cursor.execute(
            "insert into user "
            f"values "
            f"('{seller_id}', 0, null),"
            f"('{bidder_id}', 0, null);"
        )

        self.cursor.execute(
            "insert into auction "
            f"values "
            f"("
            f"null, "
            f"'test name', "
            f"10.00, "
            f"'{now()}', "
            f"'{now(4)}', "
            f"'test description', "
            f"99.99, "
            f"'{seller_id}', "
            f"0, "
            f"0.00"
            f");"
        )
        auction_id = self.cursor.execute(
            "select last_insert_rowid();"
        ).fetchone()[0]

        self.cursor.execute(
            "insert into bid "
            f"values "
            f"("
            f"{auction_id}, "
            f"'{bidder_id}', "
            f"'{now()}', "
            f"10.00"
            f")"
        )
        self.assertEqual(
            1,
            self.cursor.execute(
                "select number_of_bids "
                "from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

    def test_all_triggers_still_allow_happy_path(self):
        for trigger in os.listdir("../src/triggers"):
            self.add_trigger(f"../src/triggers/{trigger}")
        try:
            self.cursor.execute(
                "insert into category "
                "values (null, 'Test Category');"
            )

            category_id = self.cursor.execute(
                "select last_insert_rowid();"
            ).fetchone()[0]

            self.cursor.execute(
                "insert into country "
                "values (null, 'Test Country');"
            )
            country_id = self.cursor.execute(
                "select last_insert_rowid();"
            ).fetchone()[0]

            self.cursor.execute(
                f"insert into location "
                f"values (null, 'Test Location', {country_id});"
            )
            location_id = self.cursor.execute(
                "select last_insert_rowid();"
            ).fetchone()[0]

            seller_id = "testuser1234567890"
            bidder_id = "987654321testuser"
            self.cursor.execute(
                "insert into user "
                f"values "
                f"('{seller_id}', 0, {location_id}),"
                f"('{bidder_id}', 0, {location_id});"
            )

            self.cursor.execute(
                "insert into auction "
                f"values "
                f"("
                f"null, "
                f"'test name', "
                f"10.00, "
                f"'{now()}', "
                f"'{now(4)}', "
                f"'test description', "
                f"99.99, "
                f"'{seller_id}', "
                f"0, "
                f"0.00"
                f");"
            )
            auction_id = self.cursor.execute(
                "select last_insert_rowid();"
            ).fetchone()[0]

            self.cursor.execute(
                "insert into bid "
                f"values ({auction_id}, '{bidder_id}', '{now()}', 12.00)"
            )

            self.cursor.execute(
                "insert into join_auction_category "
                f"values (null, {auction_id}, {category_id})"
            )

        except sqlite3.IntegrityError as e:
            self.assertTrue(
                False,
                f"All triggers failed an addition on a valid condition:\n{e}"
            )
        except sqlite3.Error as e:
            self.assertTrue(
                False,
                f"All triggers failed an addition on a valid condition:\n{e}"
            )

    def add_trigger(
            self,
            trigger_path
    ):
        trigger = open(trigger_path, 'r')
        sql = trigger.read()
        trigger.close()
        self.cursor.executescript(
            sql
        )


if __name__ == '__main__':
    unittest.main()
