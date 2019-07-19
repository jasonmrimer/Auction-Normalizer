import sys
import unittest
from test_helpers import *
from test_helpers import verify_is_table_unique_on_columns, \
 \
    verify_item_count_did_not_increase, \
    verify_table_denies_duplicates_on_unique_columns, auction_id_exists_in_auction_table, \
    verify_deny_insert_auction_with_end_before_start, verify_all_existing_auctions_end_after_start, \
    generate_bid_that_has_duplicate_key, verify_deny_insert_bid_with_duplicate_key, \
    verify_insert_bid_at_specific_time, \
    get_existing_auction_and_unique_users, verify_deny_insert_bid_for_auction_at_the_same_time


class TestConstraints(unittest.TestCase):
    real_database = None

    def setUp(self) -> None:
        self.conn = connect_to_test_database('ebay_db')
        # self.conn = connect_to_test_database(self.real_database)
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_no_two_users_share_same_id(self):
        verify_is_table_unique_on_columns(
            self,
            self.cursor,
            'user',
            'id'
        )

    def test_cannot_add_duplicate_user(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'user',
            'id',
            ['id', 'rating', 'location']
        )

    def test_auction_id_is_unique(self):
        verify_is_table_unique_on_columns(
            self,
            self.cursor,
            'auction',
            'id'
        )

    def test_cannot_add_duplicate_auction(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'auction',
            'id',
            [
                'id',
                'name',
                'starting_price',
                'start',
                'end',
                'description',
                'buy_price',
                'seller_id',
                'number_of_bids',
                'highest_bid'
            ]
        )

    def test_cannot_add_auctions_with_end_time_before_or_equal_to_start_time(self):
        verify_all_existing_auctions_end_after_start(
            self,
            self.cursor
        )
        auction_count = count_from_table(self.cursor, 'auction')
        seller_id = get_existing_user_id(self.cursor)
        verify_deny_insert_auction_with_end_before_start(
            self,
            self.cursor,
            auction_count,
            seller_id
        )

    def test_bid_composite_primary_key_is_unique(self):
        verify_is_table_unique_on_columns(
            self,
            self.cursor,
            'bid',
            ['auction_id', 'user_id', 'amount']
        )
        (
            existing_bid,
            valid_bid_time
        ) = generate_bid_that_has_duplicate_key(self.cursor)
        verify_deny_insert_bid_with_duplicate_key(
            self,
            self.cursor,
            existing_bid,
            valid_bid_time
        )

    def test_bid_cannot_be_at_the_same_time_for_same_auction(self):
        verify_is_table_unique_on_columns(
            self,
            self.cursor,
            'bid',
            ['auction_id', 'time']
        )
        (
            existing_auction_id,
            first_user_id,
            second_user_id,
            valid_bid_time
        ) = get_existing_auction_and_unique_users(self.cursor)
        verify_insert_bid_at_specific_time(
            self,
            self.cursor,
            existing_auction_id,
            first_user_id,
            valid_bid_time
        )
        verify_deny_insert_bid_for_auction_at_the_same_time(
            self,
            self.cursor,
            existing_auction_id,
            second_user_id,
            valid_bid_time
        )

    def test_location_id_is_unique(self):
        verify_is_table_unique_on_columns(self, self.cursor, 'location', 'id')

    def test_cannot_add_duplicate_location(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'location',
            [
                'name',
                'country_id'
            ],
            [
                'id',
                'name',
                'country_id'
            ]
        )

    def test_country_id_is_unique(self):
        verify_is_table_unique_on_columns(self, self.cursor, 'country', 'id')

    def test_cannot_add_duplicate_country(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'country',
            'name',
            ['id', 'name']
        )

    def test_category_name_is_unique(self):
        verify_is_table_unique_on_columns(self, self.cursor, 'category', 'name')

    def test_auction_cannot_belong_to_category_more_than_once(self):
        verify_is_table_unique_on_columns(self, self.cursor, 'join_auction_category', ['auction_id', 'category_id'])

        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'join_auction_category',
            ['auction_id', 'category_id'],
            ['id', 'auction_id', 'category_id']
        )

    def test_cannot_add_duplicate_category(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'category',
            'name',
            ['id', 'name']
        )

    def test_items_must_exist_for_category_matches(self):
        self.verify_all_auctions_in_join_table_are_in_auction_table()
        non_existent_auction_id = self.generate_non_existent_auction_id()
        starting_join_count = count_from_table(self.cursor, 'join_auction_category')

        try:
            self.cursor.execute(
                f"insert into join_auction_category "
                f"values (null, {non_existent_auction_id}, 1);"
            )
            self.assertTrue(
                False,
                f"Database failed to throw error on Foreign Key for auction ID: {non_existent_auction_id}"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "FOREIGN KEY constraint failed"
                )
            )

        verify_item_count_did_not_increase(
            self,
            self.cursor,
            starting_join_count,
            'join_auction_category'
        )

    def generate_non_existent_auction_id(self):
        non_existent_auction_id = int(round(time.time() * 1000))
        while auction_id_exists_in_auction_table(
                self.cursor,
                non_existent_auction_id
        ):
            non_existent_auction_id = non_existent_auction_id + 1
        return non_existent_auction_id

    def verify_all_auctions_in_join_table_are_in_auction_table(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select auction_id "
                "from join_auction_category "
                "where not exists("
                "select id "
                "from auction"
                ");"
            ).fetchall()
        )

    def test_every_bid_must_correspond_to_an_auction(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select auction_id "
                "from bid "
                "where not exists("
                "select id "
                "from auction"
                ");"
            ).fetchall()
        )
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]

        try:
            self.cursor.execute(
                "insert into bid "
                f"values (null, '{user_id}', '2001-12-13 16:28:34','7.75');"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "NOT NULL constraint failed: bid.auction_id"
                )
            )

        self.assertEqual(
            [],
            self.cursor.execute(
                "select * "
                "from auction "
                "where id=123456789"
            ).fetchall()
        )

        try:
            self.cursor.execute(
                "insert into bid "
                f"values (123456789, '{user_id}', '2001-12-13 16:28:34','7.75');"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "FOREIGN KEY constraint failed"
                )
            )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestConstraints.real_database = sys.argv.pop()
    unittest.main()
