import sys
import time
import unittest

from test_helpers import *
from test_helpers import insert_fresh_bid, verify_bid_added_to_table, verify_new_user_created, insert_bid_from_new_user, \
    generate_new_user


class TestTriggers(unittest.TestCase):
    real_database = None
    trigger_dir = "../src/triggers"

    def setUp(self) -> None:
        # self.conn = connect_to_test_database(self.real_database)
        self.conn = connect_to_test_database('ebay_db')
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_all_triggers_still_allow_happy_path(self):
        add_all_triggers(self.trigger_dir, self.cursor)
        verify_allow_valid_insertion_on_every_table(self, self.cursor)

    def test_new_bid_with_existing_user(self):
        starting_bid_count = count_from_table(self.cursor, 'bid')
        insert_fresh_bid(self.cursor)
        verify_bid_added_to_table(self, self.cursor, starting_bid_count)

    def test_bidding_with_new_user_triggers_user_creation(self):
        add_trigger(self.trigger_dir, self.cursor, 1)
        new_user = generate_new_user(self, self.cursor)
        insert_bid_from_new_user(self.cursor, new_user)
        verify_new_user_created(self, self.cursor, new_user)

    def test_new_auction_with_new_seller_triggers_user_creation(self):
        add_trigger(self.trigger_dir, self.cursor, 2)
        new_seller = generate_new_user(self, self.cursor)

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

        verify_new_user_created(self, self.cursor, new_seller)

    def test_auction_current_price_always_matches_most_recent_bid_for_auction(self):
        add_trigger(self.trigger_dir, self.cursor, 3)

        highest_bid_price = 123456
        auction = get_existing_auction_with_bid_lower_than_test(self.cursor, highest_bid_price)
        auction_id = auction[0]
        user_id = get_existing_user_id(self.cursor)

        self.verify_insertion_with_exceeding_bid_sets_global_highest_price(auction, highest_bid_price, user_id)
        self.deny_new_bid_with_value_less_than_current_high(auction, auction_id, user_id)
        self.current_price_still_matches_highest_bid(auction_id, highest_bid_price)

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
        add_trigger(self.trigger_dir, self.cursor, 4)
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
        add_trigger(self.trigger_dir, self.cursor, 5)
        self.verify_all_existing_bids_fall_within_auction_time_windows()

        auction_end, auction_id, auction_start = get_auction(self.cursor)
        user_id = get_existing_user_id(self.cursor)

        self.verify_valid_bid_insertion_at_auction_start(auction_id, auction_start, user_id)
        self.attempt_bid_before_auction_start(auction_id, auction_start, user_id)
        self.attempt_bid_after_auction_ends(auction_end, auction_id, user_id)

    def test_all_auctions_maintain_accurate_number_of_bids(self):
        add_trigger(self.trigger_dir, self.cursor, 6)
        auction_id, bidder_id = self.create_new_bidder_and_auction()

        make_new_bid_for_ten_dollars(self.cursor, auction_id, bidder_id)
        self.assertEqual(
            1,
            self.cursor.execute(
                "select number_of_bids "
                "from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

    def test_new_bid_price_must_exceed_current_highest_bid(self):
        add_trigger(self.trigger_dir, self.cursor, 7)
        auction_id, bidder_id = self.create_new_bidder_and_auction()
        make_new_bid_for_ten_dollars(self.cursor, auction_id, bidder_id)
        self.verify_deny_bid_with_price_lower_than_current_high(auction_id, bidder_id)
        self.verify_allow_bid_insertion_with_higher_price(auction_id, bidder_id)

    def test_new_bids_occur_at_controlled_time(self):
        add_trigger(self.trigger_dir, self.cursor, 8)
        auction = self.cursor.execute(
            "select id, start, end, seller_id, highest_bid "
            "from auction "
            "where end > datetime(start, '+2 hours')"
            "limit 1;"
        ).fetchone()
        auction_id = auction[0]
        start = auction[1]
        seller_id = auction[3]
        bid_price = 1 if auction[4] is None else float(auction[4]) + 1

        bidder_id = self.cursor.execute(
            f"select id "
            f"from user "
            f"where id !='{seller_id}' "
            f"limit 1;"
        ).fetchone()[0]

        pseudo_now = add_hours_to_datestring(start, 1)
        self.cursor.execute(
            "update pseudo_time "
            f"set now='{pseudo_now}';"
        )

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{bidder_id}', "
            f"null, "
            f"{bid_price}"
            f");"
        )

        bid_time = self.cursor.execute(
            f"select time "
            f"from bid "
            f"where auction_id={auction_id} "
            f"and user_id='{bidder_id}'"
            f"and amount={bid_price} "
            f"limit 1;"
        ).fetchone()[0]

        self.assertEqual(
            pseudo_now,
            bid_time
        )

    def test_pseudo_time_only_moves_forward(self):
        add_trigger(self.trigger_dir, self.cursor, 9)

        try:
            self.cursor.execute(
                f"insert into pseudo_time "
                f"values ('{now()}');"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                False,
                "Database failed to accept forward modification of pseudo time."
            )

        try:
            self.cursor.execute(
                f"insert into pseudo_time "
                f"values ('{now(-1)}');"
            )
        except sqlite3.IntegrityError as e:
            self.assertEquals(
                "Users may only move the pseudo time forward.",
                str(e)
            )

    def deny_new_bid_with_value_less_than_current_high(self, auction, auction_id, user_id):
        bid_time = calculate_a_valid_bid_time(auction)
        try:
            self.cursor.execute(
                f"insert into bid "
                f"values ("
                f"{auction_id}, "
                f"'{user_id}', "
                f"'{bid_time}', "
                f"1"
                f");"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__('New bids must exceed the current highest bid.')
            )

    def current_price_still_matches_highest_bid(self, auction_id, highest_bid):
        self.assertEqual(
            highest_bid,
            self.cursor.execute(
                f"select highest_bid "
                f"from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

    def verify_insertion_with_exceeding_bid_sets_global_highest_price(self, auction, highest_bid_price, user_id):
        auction_id = auction[0]
        bid_time = calculate_a_valid_bid_time(auction)

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{bid_time}', "
            f"123456"
            f");"
        )
        self.assertEqual(
            highest_bid_price,
            self.cursor.execute(
                f"select highest_bid "
                f"from auction "
                f"where id={auction_id}"
            ).fetchone()[0]
        )

    def attempt_bid_after_auction_ends(self, auction_end, auction_id, user_id):
        starting_bid_count = count_from_table(
            self.cursor,
            'bid'
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
            starting_bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

    def verify_valid_bid_insertion_at_auction_start(self, auction_id, auction_start, user_id):
        starting_bid_count = count_from_table(
            self.cursor,
            'bid'
        )

        amount = int(round(time.time() * 1000))

        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{auction_start}',"
            f"{amount}"
            f");"
        )
        starting_bid_count += 1
        self.assertEqual(
            starting_bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

    def attempt_bid_before_auction_start(self, auction_id, auction_start, user_id):
        starting_bid_count = count_from_table(
            self.cursor,
            'bid'
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
            starting_bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

    def verify_all_existing_bids_fall_within_auction_time_windows(self):
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

    def create_new_bidder_and_auction(self):
        seller_id = "testuser1234567890"
        bidder_id = "987654321testuser"
        add_new_users(self.cursor, bidder_id, seller_id)
        create_new_auction(self.cursor, seller_id)
        auction_id = fetch_last_row_added(self.cursor)
        return auction_id, bidder_id

    def verify_allow_bid_insertion_with_higher_price(self, auction_id, bidder_id):
        try:
            self.cursor.execute(
                "insert or replace into bid "
                f"values "
                f"("
                f"{auction_id}, "
                f"'{bidder_id}', "
                f"'{now(1)}', "
                f"40.00"
                f")"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                False,
                f"Database failed to allow valid bid that exceeded current highest. Threw error:\n{e}"
            )

    def verify_deny_bid_with_price_lower_than_current_high(self, auction_id, bidder_id):
        try:
            self.cursor.execute(
                "insert into bid "
                f"values ({auction_id}, '{bidder_id}','{now()}', 3.50);"
            )
            self.assertTrue(
                False,
                "Database failed to deny low bid."
            )
        except sqlite3.IntegrityError as e:
            self.assertEqual(
                "New bids must exceed the current highest bid.",
                str(e)
            )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestTriggers.real_database = sys.argv.pop()
    unittest.main()
