from helpers_for_database_setup import connect_to_test_database
from helpers_for_tests import *
from helpers_for_ebay_sql import *
from helpers_for_general_functions import *
import sys
import unittest


class TestTriggers(unittest.TestCase):
    real_database = None
    trigger_dir = "./triggers"

    def setUp(self) -> None:
        # self.conn = connect_to_test_database(self.real_database)
        self.conn = connect_to_test_database('ebay_db')
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_all_triggers_still_allow_happy_path(self):
        add_all_triggers(self.cursor, self.trigger_dir)
        verify_allow_valid_insertion_on_every_table(
            self,
            self.cursor
        )

    def test_new_bid_with_existing_user(self):
        verify_bid_added_to_table(
            self,
            self.cursor
        )

    def test_bidding_with_new_user_triggers_user_creation(self):
        add_trigger(self.cursor, self.trigger_dir, 1)
        new_user = generate_new_user_id(self.cursor)
        insert_bid_from_new_user(
            self.cursor,
            new_user
        )
        verify_new_user_created(
            self,
            self.cursor,
            new_user
        )

    def test_new_auction_with_new_seller_triggers_user_creation(self):
        add_trigger(self.cursor, self.trigger_dir, 2)
        new_seller = generate_new_user_id(self.cursor)
        create_new_auction_from_new_seller(self.cursor, new_seller)
        verify_new_user_created(
            self,
            self.cursor,
            new_seller
        )

    def test_auction_current_price_always_matches_most_recent_bid_for_auction(self):
        add_trigger(self.cursor, self.trigger_dir, 3)
        (
            auction,
            highest_bid_price,
            user_id
        ) = setup_auction_with_beatable_bid(self.cursor)
        verify_insertion_with_exceeding_bid_sets_global_highest_price(
            self,
            self.cursor,
            auction,
            highest_bid_price,
            user_id
        )
        verify_deny_new_bid_with_value_less_than_current_high(
            self,
            self.cursor,
            auction,
            user_id
        )
        verify_current_price_still_matches_highest_bid(
            self,
            self.cursor,
            auction,
            highest_bid_price
        )

    def test_no_bids_belong_to_auction_sellers(self):
        verify_bidders_are_not_auction_sellers(self, self.cursor)

    def test_seller_may_not_bid_on_auction(self):
        add_trigger(self.cursor, self.trigger_dir, 4)
        starting_bid_count = count_from_table(self.cursor, 'bid')
        (
            auction_id,
            seller_id
        ) = fetch_seller_and_auction(self.cursor)
        verify_deny_bid_on_item_auctioned_by_bidder(
            self,
            self.cursor,
            auction_id,
            seller_id
        )
        verify_deny_seller_bid(
            self,
            self.cursor,
            starting_bid_count
        )

    def test_all_bids_occur_within_auction_start_and_end(self):
        add_trigger(self.cursor, self.trigger_dir, 5)
        user_id = get_existing_user_id(self.cursor)
        (
            auction_end,
            auction_id,
            auction_start
        ) = get_auction_values(self.cursor)

        verify_all_existing_bids_fall_within_auction_time_windows(
            self,
            self.cursor
        )
        verify_valid_bid_insertion_at_auction_start(
            self,
            self.cursor,
            auction_id,
            auction_start,
            user_id
        )
        verify_deny_bid_before_auction_start(
            self,
            self.cursor,
            auction_id,
            auction_start,
            user_id
        )
        verify_deny_bid_after_auction_ends(
            self,
            self.cursor,
            auction_end,
            auction_id,
            user_id
        )

    def test_all_auctions_maintain_accurate_number_of_bids(self):
        add_trigger(self.cursor, self.trigger_dir, 6)
        (
            auction_id,
            bidder_id
        ) = create_new_bidder_and_auction(self.cursor)
        make_new_bid_for_ten_dollars(
            self.cursor,
            auction_id,
            bidder_id
        )
        verify_total_bids_for_auction(
            self,
            self.cursor,
            auction_id
        )

    def test_new_bid_price_must_exceed_current_highest_bid(self):
        add_trigger(self.cursor, self.trigger_dir, 7)
        (
            auction_id,
            bidder_id
        ) = create_new_bidder_and_auction(self.cursor)

        make_new_bid_for_ten_dollars(
            self.cursor,
            auction_id,
            bidder_id
        )
        verify_deny_bid_with_price_lower_than_current_high(
            self,
            self.cursor,
            auction_id,
            bidder_id
        )
        verify_allow_bid_insertion_with_higher_price(
            self,
            self.cursor,
            auction_id,
            bidder_id
        )

    def test_new_bids_occur_at_controlled_time(self):
        add_trigger(self.cursor, self.trigger_dir, 8)
        (
            auction_id,
            bid_price,
            seller_id,
            start
        ) = fetch_auction_with_time_range_greater_than_two_hours(self.cursor)
        bidder_id = fetch_user_who_is_not_the_seller(self.cursor, seller_id)
        pseudo_now = add_hours_to_date_string(start, 1)
        update_pseudo_time_and_place_bid(
            self.cursor,
            auction_id,
            bid_price,
            bidder_id,
            pseudo_now
        )
        verify_new_bid_time_matched_pseudo_time(
            self,
            self.cursor,
            auction_id,
            bid_price,
            bidder_id,
            pseudo_now
        )

    def test_pseudo_time_only_moves_forward(self):
        add_trigger(self.cursor, self.trigger_dir, 9)
        verify_allow_move_time_forward(
            self,
            self.cursor
        )
        verify_deny_move_time_backward(
            self,
            self.cursor
        )


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestTriggers.real_database = sys.argv.pop()
    unittest.main()
