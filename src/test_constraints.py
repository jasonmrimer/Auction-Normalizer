import sys
import unittest

from helpers_for_tests import *
from test_helpers import *


class TestConstraints(unittest.TestCase):
    real_database = None

    def setUp(self) -> None:
        self.conn = connect_to_test_database(self.real_database)
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_no_two_users_share_same_id(self):
        verify_table_is_unique_on_columns(
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
        verify_table_is_unique_on_columns(
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
        verify_table_is_unique_on_columns(
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
        verify_table_is_unique_on_columns(
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
        verify_table_is_unique_on_columns(self, self.cursor, 'location', 'id')

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
        verify_table_is_unique_on_columns(self, self.cursor, 'country', 'id')

    def test_cannot_add_duplicate_country(self):
        verify_table_denies_duplicates_on_unique_columns(
            self,
            self.cursor,
            'country',
            'name',
            ['id', 'name']
        )

    def test_category_name_is_unique(self):
        verify_table_is_unique_on_columns(
            self,
            self.cursor,
            'category',
            'name'
        )

    def test_auction_cannot_belong_to_category_more_than_once(self):
        verify_table_is_unique_on_columns(
            self,
            self.cursor,
            'join_auction_category',
            ['auction_id', 'category_id']
        )
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
        non_existent_auction_id = generate_non_existent_auction_id(self.cursor)
        verify_all_auctions_in_join_table_are_in_auction_table(
            self,
            self.cursor
        )
        verify_deny_insert_category_with_non_existent_auction(
            self,
            self.cursor,
            non_existent_auction_id
        )

    def test_every_bid_must_correspond_to_an_auction(self):
        user_id = get_existing_user_id(self.cursor)
        verify_all_bids_have_existing_auction(
            self,
            self.cursor
        )
        verify_deny_insert_new_bid_without_auction(
            self,
            self.cursor,
            user_id
        )
        verify_deny_insert_bid_with_non_existing_auction(
            self,
            self.cursor,
            user_id
        )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestConstraints.real_database = sys.argv.pop()
    unittest.main()
