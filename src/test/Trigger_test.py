import sqlite3
import unittest

from test.TestDatabase import create_test_database

from test.helper import *


class ConstraintTestCase(unittest.TestCase):
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
