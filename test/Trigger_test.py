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

    def test_new_auction_with_new_seller_triggers_user_creation(self):
        trigger = open('../src/triggers/trigger2_add.sql', 'r')
        sql = trigger.read()
        trigger.close()
        self.cursor.executescript(
            sql
        )
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
            f"'2001-12-13 16:28:34', "
            f"'2001-12-15 16:28:34', "
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


if __name__ == '__main__':
    unittest.main()
