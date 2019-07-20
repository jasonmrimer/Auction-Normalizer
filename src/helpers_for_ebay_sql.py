from helpers_for_tests import *
from helpers_for_generic_sql import *
from helpers_for_general_functions import *


def auction_id_exists_in_auction_table(cursor, auction_id):
    return item_id_exists_in_table(cursor, auction_id, 'auction')


def get_existing_user_id(cursor):
    return fetch_existing_record_id_from_table(cursor, 'user')


def get_existing_auction_id(cursor):
    return fetch_existing_record_id_from_table(cursor, 'auction')


def get_auction_values(cursor):
    auction = fetch_existing_item_column_values_from_column_names(
        cursor,
        'auction',
        ['id', 'start', 'end']
    )
    auction_id = auction[0]
    auction_start = auction[1]
    auction_end = auction[2]
    return auction_end, auction_id, auction_start


def add_new_users(cursor, bidder_id, seller_id):
    cursor.execute(
        "insert into user "
        f"values "
        f"('{seller_id}', 0, null),"
        f"('{bidder_id}', 0, null);"
    )


def create_new_auction(cursor, seller_id):
    cursor.execute(
        "insert into auction "
        f"values "
        f"("
        f"null, "
        f"'test name', "
        f"10.00, "
        f"'{now_plus_days()}', "
        f"'{now_plus_days(4)}', "
        f"'test description', "
        f"99.99, "
        f"'{seller_id}', "
        f"0, "
        f"0.00"
        f");"
    )


def make_new_bid_for_ten_dollars(cursor, auction_id, bidder_id):
    cursor.execute(
        "insert into bid "
        f"values "
        f"("
        f"{auction_id}, "
        f"'{bidder_id}', "
        f"'{now_plus_days()}', "
        f"10.00"
        f")"
    )


def get_existing_auction_with_bid_lower_than_price(cursor, highest_bid_price):
    auction = cursor.execute(
        "select * "
        "from auction "
        f"where highest_bid < {highest_bid_price};"
    ).fetchone()
    return auction


def insert_fresh_bid(cursor):
    user_id = get_existing_user_id(cursor)
    auction_values = fetch_existing_item_column_values_from_column_names(
        cursor, 'auction', ['id', 'start', 'end']
    )
    auction_id = auction_values[0]
    auction_start = auction_values[1]
    auction_end = auction_values[2]
    # auction = fetch_single_item_from_table(cursor, 'auction')
    # auction_id = fetch_existing_record_id_from_table(cursor, 'auction')
    valid_bid_time = generate_a_datetime_within_range(auction_start, auction_end)
    cursor.execute(
        f"insert into bid "
        f"values ({auction_id}, '{user_id}', '{valid_bid_time}', 7.75);"
    )


def insert_bid_from_new_user(cursor, new_user):
    auction_values = fetch_existing_item_column_values_from_column_names(
        cursor, 'auction', ['id', 'start', 'end']
    )
    auction_id = auction_values[0]
    auction_start = auction_values[1]
    auction_end = auction_values[2]
    valid_bid_time = generate_a_datetime_within_range(auction_start, auction_end)
    cursor.execute(
        f"insert into bid "
        f"values ({auction_id}, '{new_user}', '{valid_bid_time}', 7.75);"
    )


def generate_new_user_id(cursor):
    # new_user_id = 'new_user_who_is_definitely_not_already_in_the_database'
    # while item_id_exists_in_table(cursor, new_user_id, 'user'):
    #     new_user_id = f"{new_user_id}{round(time.time() * 1000)}"
    return generate_new_id_for_table(cursor, 'user')


def create_new_auction_from_new_seller(cursor, new_seller):
    new_auction_id = generate_new_id_for_table(cursor, 'auction')

    cursor.execute(
        f"insert into auction "
        f"values ("
        f"{new_auction_id}, "
        f"'name of the auction', "
        f"7.75, "
        f"'{now_plus_days()}', "
        f"'{now_plus_days(2)}', "
        f"'description of the auction', "
        f"70.00, "
        f"'{new_seller}', "
        f"0, "
        f"0 "
        f");"
    )


def setup_auction_with_beatable_bid(cursor):
    highest_bid_price = 123456
    auction = get_existing_auction_with_bid_lower_than_price(cursor, highest_bid_price)
    user_id = get_existing_user_id(cursor)
    return auction, highest_bid_price, user_id


def fetch_seller_and_auction(cursor):
    auction = cursor.execute(
        "select id, seller_id "
        "from auction;"
    ).fetchone()
    auction_id = auction[0]
    seller_id = auction[1]
    return auction_id, seller_id


def create_new_bidder_and_auction(cursor):
    seller_id = "test_user1234567890"
    bidder_id = "987654321test_user"
    add_new_users(cursor, bidder_id, seller_id)
    create_new_auction(cursor, seller_id)
    auction_id = fetch_last_row_added(cursor)
    return auction_id, bidder_id


def fetch_auction_with_time_range_greater_than_two_hours(cursor):
    auction = cursor.execute(
        "select id, start, end, seller_id, highest_bid "
        "from auction "
        "where end > datetime(start, '+2 hours')"
        "limit 1;"
    ).fetchone()
    auction_id = auction[0]
    start = auction[1]
    seller_id = auction[3]
    bid_price = 1 if auction[4] is None else float(auction[4]) + 1
    return auction_id, bid_price, seller_id, start


def fetch_user_who_is_not_the_seller(cursor, seller_id):
    bidder_id = cursor.execute(
        f"select id "
        f"from user "
        f"where id !='{seller_id}' "
        f"limit 1;"
    ).fetchone()[0]
    return bidder_id


def update_pseudo_time_and_place_bid(cursor, auction_id, bid_price, bidder_id, pseudo_now):
    cursor.execute(
        "update pseudo_time "
        f"set now='{pseudo_now}' "
        f"where 1=1;"
    )
    cursor.execute(
        f"insert into bid "
        f"values ("
        f"{auction_id}, "
        f"'{bidder_id}', "
        f"null, "
        f"{bid_price}"
        f");"
    )


def generate_bid_that_has_duplicate_key(cursor):
    existing_bid = cursor.execute(
        f"select * "
        f"from bid "
        f"limit 1;"
    ).fetchone()
    auction_from_bid = cursor.execute(
        f"select * "
        f"from auction "
        f"where id={existing_bid[0]};"
    ).fetchone()
    valid_bid_time = add_hours_to_date_string(auction_from_bid[4], -1)
    return existing_bid, valid_bid_time


def get_existing_unique_users(cursor):
    all_user_ids = cursor.execute(
        "select id "
        "from user;"
    ).fetchall()
    first_user_id = all_user_ids[0][0]
    second_user_id = all_user_ids[1][0]
    return first_user_id, second_user_id


def generate_non_existent_auction_id(cursor):
    return generate_new_id_for_table(cursor, 'auction')


def generate_valid_bid_time(cursor, existing_auction_id):
    auction = cursor.execute(
        f"select start, end "
        f"from auction "
        f"where id='{existing_auction_id}';"
    ).fetchone()
    auction_start = auction[0]
    auction_end = auction[1]
    return generate_a_datetime_within_range(auction_start, auction_end)