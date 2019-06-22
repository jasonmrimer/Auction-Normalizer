import csv
import sqlite3
import unittest


# insert users ./
# insert bids ./
# insert auctions ./
# create trigger ./
# test adding a bid without a user ./
# test adding an auction with a seller who is not a user
# test bids and auctions with existing user
# test that all current auctions and bids' users exist
from test.TestDatabase import create_test_database


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
            f'insert into bid '
            f'values ({auction_id}, \'{user_id}\', \'2001-12-13 16:28:34\', 7.75);'
        )
        self.assertEqual(
            9875,
            self.conn.execute(
                "select count(*) "
                "from bid;"
            ).fetchall()[0][0]
        )

    def test_bidding_with_new_user_triggers_user_creation(self):
        trigger = open('../src/triggers/trigger1_add.sql', 'r')
        sql = trigger.read()
        trigger.close()
        self.cursor.executescript(
            sql
        )
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
            f'insert into bid '
            f'values ({auction_id}, \'{new_user}\', \'2001-12-13 16:28:34\', 7.75);'
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

    
if __name__ == '__main__':
    unittest.main()
