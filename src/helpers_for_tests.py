from helpers_for_ebay_sql import *
import sqlite3

from helpers_for_generic_sql import count_from_table, duplicates_from_table, get_existing_item_from_key, \
    fetch_last_row_added


def verify_all_bids_have_existing_auction(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select auction_id "
            "from bid "
            "where not exists("
            "select id "
            "from auction"
            ");"
        ).fetchall()
    )


def verify_table_denies_duplicates_on_unique_columns(test, cursor, table_name, unique_columns, column_names):
    starting_item_count = count_from_table(
        cursor,
        table_name
    )
    existing_item_from_table = get_existing_item_from_key(
        cursor,
        table_name,
        unique_columns
    )
    new_item_duplicate_on_unique_columns = concatenate_filler_values_for_non_unique_columns(
        existing_item_from_table,
        unique_columns,
        column_names
    )
    verify_deny_insert_record_that_is_duplicated_on_unique_columns(
        test,
        cursor,
        new_item_duplicate_on_unique_columns,
        table_name,
        unique_columns
    )
    verify_item_count_did_not_increase(
        test,
        cursor,
        starting_item_count,
        table_name

    )


def verify_all_auctions_in_join_table_are_in_auction_table(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select auction_id "
            "from join_auction_category "
            "where not exists("
            "select id "
            "from auction"
            ");"
        ).fetchall()
    )


def verify_all_existing_auctions_end_after_start(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select * "
            "from auction "
            "where end <= start;"
        ).fetchall()
    )


def verify_deny_insert_bid_for_auction_at_the_same_time(test, cursor, existing_auction_id,
                                                        second_user_id, valid_bid_time):
    original_bid_count = count_from_table(
        cursor,
        'bid'
    )
    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{existing_auction_id}, "
            f"'{second_user_id}', "
            f"'{valid_bid_time}', "
            f"1234567);"
        )
        test.assertTrue(
            False,
            "Database failed to deny bid for the same auction at the same time"
        )
    except sqlite3.IntegrityError as e:
        test.assertEqual(
            str(e),
            "UNIQUE constraint failed: bid.auction_id, bid.time"
        )
    verify_item_count_did_not_increase(test, cursor, original_bid_count, 'bid')


def verify_deny_insert_category_with_non_existent_auction(test, cursor, non_existent_auction_id):
    starting_join_count = count_from_table(cursor, 'join_auction_category')
    try:
        cursor.execute(
            f"insert into join_auction_category "
            f"values (null, {non_existent_auction_id}, 1);"
        )
        test.assertTrue(
            False,
            f"Database failed to throw error on Foreign Key for auction ID: {non_existent_auction_id}"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__(
                "FOREIGN KEY constraint failed"
            )
        )
    verify_item_count_did_not_increase(
        test,
        cursor,
        starting_join_count,
        'join_auction_category'
    )


def verify_deny_insert_bid_with_non_existing_auction(test, cursor, user_id):
    try:
        cursor.execute(
            "insert into bid "
            f"values (123456789, '{user_id}', '2001-12-13 16:28:34','7.75');"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__(
                "FOREIGN KEY constraint failed"
            )
        )


def verify_deny_insert_new_bid_without_auction(test, cursor, user_id):
    try:
        cursor.execute(
            "insert into bid "
            f"values (null, '{user_id}', '2001-12-13 16:28:34','7.75');"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__(
                "NOT NULL constraint failed: bid.auction_id"
            )
        )
    test.assertEqual(
        [],
        cursor.execute(
            "select * "
            "from auction "
            "where id=123456789"
        ).fetchall()
    )


def verify_insert_bid_at_specific_time(test, cursor, existing_auction_id, first_user_id, valid_bid_time):
    original_bid_count = count_from_table(
        cursor,
        'bid'
    )
    cursor.execute(
        f"insert into bid "
        f"values "
        f"("
        f"{existing_auction_id}, "
        f"'{first_user_id}', "
        f"'{valid_bid_time}', "
        f"123456"
        f");"
    )
    original_bid_count += 1
    test.assertEqual(
        original_bid_count,
        count_from_table(
            cursor,
            'bid'
        )
    )
    return original_bid_count


def verify_deny_insert_bid_with_duplicate_key(test, cursor, existing_bid, valid_bid_time):
    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"'{existing_bid[0]}', "
            f"'{existing_bid[1]}', "
            f"'{valid_bid_time}', "
            f"{existing_bid[3]}"
            f");"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__(f"UNIQUE constraint failed: bid.auction_id, bid.user_id, bid.amount")
        )


def verify_deny_insert_auction_with_end_before_start(test, cursor, auction_count, seller_id):
    try:
        cursor.execute(
            f"insert into auction "
            f"values ("
            f"null, "
            f"'name', "
            f"0.01, "
            f"'2000-01-01 00:00:01', "
            f"'1999-12-31 23:59:59', "
            f"'description', "
            f"10.00, "
            f"'{seller_id}', "
            f"0, "
            f"0.00);"
        )
        test.assertTrue(
            False,
            "Database failed to deny auction with end time before start time."
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__(
                "CHECK constraint failed: auction"
            )
        )
    verify_item_count_did_not_increase(test, cursor, auction_count, 'auction')


def verify_allow_move_time_forward(test, cursor):
    try:
        cursor.execute(
            f"insert into pseudo_time "
            f"values ('{now_plus_days()}');"
        )
    except sqlite3.IntegrityError:
        test.assertTrue(
            False,
            "Database failed to accept forward modification of pseudo time."
        )


def verify_deny_move_time_backward(test, cursor):
    try:
        cursor.execute(
            f"insert into pseudo_time "
            f"values ('{now_plus_days(-1)}');"
        )
    except sqlite3.IntegrityError as e:
        test.assertEquals(
            "Users may only move the pseudo time forward.",
            str(e)
        )


def verify_new_bid_time_matched_pseudo_time(test, cursor, auction_id, bid_price, bidder_id, pseudo_now):
    bid_time = cursor.execute(
        f"select time "
        f"from bid "
        f"where auction_id={auction_id} "
        f"and user_id='{bidder_id}'"
        f"and amount={bid_price} "
        f"limit 1;"
    ).fetchone()[0]
    test.assertEqual(
        pseudo_now,
        bid_time
    )


def verify_allow_bid_insertion_with_higher_price(test, cursor, auction_id, bidder_id):
    try:
        cursor.execute(
            "insert or replace into bid "
            f"values "
            f"("
            f"{auction_id}, "
            f"'{bidder_id}', "
            f"'{now_plus_days(1)}', "
            f"40.00"
            f")"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            False,
            f"Database failed to allow valid bid that exceeded current highest. Threw error:\n{e}"
        )


def verify_deny_bid_with_price_lower_than_current_high(test, cursor, auction_id, bidder_id):
    try:
        cursor.execute(
            "insert into bid "
            f"values ({auction_id}, '{bidder_id}','{now_plus_days()}', 3.50);"
        )
        test.assertTrue(
            False,
            "Database failed to deny low bid."
        )
    except sqlite3.IntegrityError as e:
        test.assertEqual(
            "New bids must exceed the current highest bid.",
            str(e)
        )


def verify_total_bids_for_auction(test, cursor, auction_id):
    test.assertEqual(
        1,
        cursor.execute(
            "select number_of_bids "
            "from auction "
            f"where id={auction_id}"
        ).fetchone()[0]
    )


def verify_valid_bid_insertion_at_auction_start(test, cursor, auction_id, auction_start, user_id):
    starting_bid_count = count_from_table(
        cursor,
        'bid'
    )

    amount = int(round(time.time() * 1000))

    cursor.execute(
        f"insert into bid "
        f"values ("
        f"{auction_id}, "
        f"'{user_id}', "
        f"'{auction_start}',"
        f"{amount}"
        f");"
    )
    starting_bid_count += 1
    test.assertEqual(
        starting_bid_count,
        count_from_table(
            cursor,
            'bid'
        )
    )


def verify_all_existing_bids_fall_within_auction_time_windows(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select * "
            "from bid "
            "where "
            "time < (select start from auction where id = auction_id)"
            "and "
            "time > ( select end from auction where id = auction_id);"
        ).fetchall()
    )


def verify_bidders_are_not_auction_sellers(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select * "
            "from bid "
            "where user_id = "
            "(select seller_id from auction where id = bid.auction_id);"
        ).fetchall()
    )


def verify_insertion_with_exceeding_bid_sets_global_highest_price(test, cursor, auction, highest_bid_price, user_id):
    auction_id = auction[0]
    auction_start = auction[3]
    auction_end = auction[4]
    bid_time = calculate_a_valid_bid_time(auction_start, auction_end)

    cursor.execute(
        f"insert into bid "
        f"values ("
        f"{auction_id}, "
        f"'{user_id}', "
        f"'{bid_time}', "
        f"123456"
        f");"
    )
    test.assertEqual(
        highest_bid_price,
        cursor.execute(
            f"select highest_bid "
            f"from auction "
            f"where id={auction_id}"
        ).fetchone()[0]
    )


def verify_new_user_created(test, cursor, new_user):
    test.assertEqual(
        1,
        len(
            cursor.execute(
                f'select * '
                f'from user '
                f'where id=\'{new_user}\';'
            ).fetchall()
        )
    )


def verify_bid_added_to_table(test, cursor, starting_bid_count):
    test.assertEqual(
        starting_bid_count + 1,
        count_from_table(cursor, 'bid')
    )


def verify_user_does_not_exist(test, cursor, new_user):
    test.assertEqual(
        [],
        cursor.execute(
            f'select * '
            f'from user '
            f'where id=\'{new_user}\';'
        ).fetchall()
    )


def verify_allow_valid_insertion_on_every_table(test, cursor):
    try:
        cursor.execute(
            "insert into category "
            "values (null, 'Test Category');"
        )

        category_id = fetch_last_row_added(cursor)

        cursor.execute(
            "insert into country "
            "values (null, 'Test Country');"
        )
        country_id = fetch_last_row_added(cursor)

        cursor.execute(
            f"insert into location "
            f"values (null, 'Test Location', {country_id});"
        )
        location_id = fetch_last_row_added(cursor)

        seller_id = "testuser1234567890"
        bidder_id = "987654321testuser"
        cursor.execute(
            "insert into user "
            f"values "
            f"('{seller_id}', 0, {location_id}),"
            f"('{bidder_id}', 0, {location_id});"
        )

        create_new_auction(cursor, seller_id)
        auction_id = fetch_last_row_added(cursor)

        cursor.execute(
            "insert into bid "
            f"values ({auction_id}, '{bidder_id}', '{now_plus_days()}', 12.00)"
        )

        cursor.execute(
            "insert into join_auction_category "
            f"values (null, {auction_id}, {category_id})"
        )

    except sqlite3.IntegrityError as e:
        test.assertTrue(
            False,
            f"All triggers failed an addition on a valid condition:\n{e}"
        )
    except sqlite3.Error as e:
        test.assertTrue(
            False,
            f"All triggers failed an addition on a valid condition:\n{e}"
        )


def verify_deny_seller_bid(test, cursor, bid_count):
    test.assertEqual(
        bid_count,
        count_from_table(
            cursor,
            'bid'
        ),
        "Database allowed new bid from seller of auction."
    )


def verify_item_count_did_not_increase(
        test,
        cursor,
        starting_item_count,
        table_name
):
    test.assertEqual(
        starting_item_count,
        count_from_table(cursor, table_name)
    )


def verify_table_is_unique_on_columns(test, cursor, table_name, unique_on_column_names):
    test.assertEqual(
        [],
        duplicates_from_table(
            cursor,
            table_name,
            unique_on_column_names
        )
    )


def verify_deny_insert_record_that_is_duplicated_on_unique_columns(
        test,
        cursor,
        concatenated_values,
        table_name,
        unique_columns
):
    try:
        cursor.execute(
            f"insert into {table_name} "
            f"values ({concatenated_values});"
        )
    except sqlite3.IntegrityError as e:
        if type(unique_columns) == list:
            concatenated_error = concatenate_error_values(table_name, unique_columns)
            test.assertTrue(
                str(e).__contains__(f"UNIQUE constraint failed: {concatenated_error}")
            )
        else:
            test.assertTrue(
                str(e).__contains__(f"UNIQUE constraint failed: {table_name}.{unique_columns}")
            )


def verify_auction_does_not_exist(test, cursor):
    new_auction = 123456789
    test.assertEqual(
        [],
        cursor.execute(
            f'select * '
            f'from auction '
            f'where id=\'{new_auction}\';'
        ).fetchall()
    )
    return new_auction


def verify_deny_bid_before_auction_start(test, cursor, auction_id, auction_start, user_id):
    starting_bid_count = count_from_table(
        cursor,
        'bid'
    )

    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{add_hours_to_date_string(auction_start, -4)}',"
            f"123456"
            f");"
        )
        test.assertTrue(
            False,
            "Databased failed to check bid time is after auction start"
        )
    except sqlite3.IntegrityError as e:
        test.assertEqual(
            "Bids must be after the auction starts.",
            str(e)
        )

    test.assertEqual(
        starting_bid_count,
        count_from_table(
            cursor,
            'bid'
        )
    )


def verify_deny_bid_after_auction_ends(test, cursor, auction_end, auction_id, user_id):
    starting_bid_count = count_from_table(
        cursor,
        'bid'
    )

    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{add_hours_to_date_string(auction_end, 4)}',"
            f"123456"
            f");"
        )
        test.assertTrue(
            False,
            "Databased failed to check bid time is before auction end"
        )
    except sqlite3.IntegrityError as e:
        test.assertEqual(
            "Bids must be before the auction ends.",
            str(e)
        )
    test.assertEqual(
        starting_bid_count,
        count_from_table(
            cursor,
            'bid'
        )
    )


def verify_deny_new_bid_with_value_less_than_current_high(test, cursor, auction, user_id):
    auction_id = auction[0]
    auction_start = auction[3]
    auction_end = auction[4]
    bid_time = calculate_a_valid_bid_time(auction_start, auction_end)
    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{user_id}', "
            f"'{bid_time}', "
            f"1"
            f");"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            str(e).__contains__('New bids must exceed the current highest bid.')
        )


def verify_current_price_still_matches_highest_bid(test, cursor, auction, highest_bid):
    auction_id = auction[0]
    test.assertEqual(
        highest_bid,
        cursor.execute(
            f"select highest_bid "
            f"from auction "
            f"where id={auction_id}"
        ).fetchone()[0]
    )


def verify_deny_bid_on_item_auctioned_by_bidder(test, cursor, auction_id, seller_id):
    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{seller_id}', "
            f"'{now_plus_days()}', "
            f"123456"
            f")"
        )
        test.assertTrue(
            False,
            "Database failed to deny bid on an auction from the seller of that auction."
        )
    except sqlite3.IntegrityError as e:
        test.assertEqual(
            str(e),
            "Sellers may not bid on their own auction."
        )