import csv
import datetime
import os
import sqlite3
import time


def verify_table_denies_duplicates_on_unique_columns(
        test,
        cursor,
        table_name,
        unique_columns,
        column_names
):
    starting_item_count = count_from_table(
        cursor,
        table_name
    )
    existing_item_from_table = get_existing_item(
        cursor,
        table_name,
        unique_columns
    )
    new_item_duplicate_on_unique_columns = concatenate_filler_values_for_non_unique_columns(
        existing_item_from_table,
        unique_columns,
        column_names
    )
    attempt_insert_of_record_duplicate_on_unique_columns(
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


def count_from_table(
        cursor,
        table_name
):
    return cursor.execute(
        "select count(*) "
        f"from {table_name};"
    ).fetchone()[0]


def duplicate_rows_from_table(
        cursor,
        table_name,
        column_names
):
    if type(column_names) == list:
        column_names = ','.join(column_names)

    return cursor.execute(
        f"select {column_names} "
        f"from {table_name} "
        f"group by {column_names} "
        f"having count (*) > 1;"
    ).fetchall()


def now(
        add_days=0
):
    return (datetime.datetime.now() + datetime.timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M:%S')


def add_hours_to_datestring(
        datestring,
        add_hours=0
):
    datetime_object = \
        datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S') \
        + datetime.timedelta(hours=add_hours)
    return datetime_object.strftime('%Y-%m-%d %H:%M:%S')


def connect_to_test_database(real_database):
    if real_database:
        conn = sqlite3.connect(real_database)
    else:
        conn = create_test_database()
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_test_database():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    file = open('../src/create.sql')
    sql = file.read()
    file.close()
    cursor.executescript(sql)

    import_dat(
        conn,
        cursor,
        '../src/dat/categories.dat',
        'category',
        [
            'id',
            'name'
        ]
    )

    import_dat(
        conn,
        cursor,
        '../src/dat/countries.dat',
        'country',
        [
            'id',
            'name'
        ]
    )

    import_dat(
        conn,
        cursor,
        '../src/dat/locations.dat',
        'location',
        [
            'id',
            'name',
            'country_name'
        ]
    )

    import_dat(
        conn,
        cursor,
        '../src/dat/users.dat',
        'user',
        [
            'id',
            'rating',
            'location_name',
            'country_name'
        ]
    )
    import_dat(
        conn,
        cursor,
        '../src/dat/bids.dat',
        'bid',
        [
            'auction_id',
            'user_id',
            'time',
            'amount'
        ]
    )
    import_dat(
        conn,
        cursor,
        '../src/dat/auctions.dat',
        'auction',
        [
            'id',
            'name',
            'starting_price',
            'start',
            'end',
            'description',
            'buy_price',
            'seller_id'
        ]
    )
    import_dat(
        conn,
        cursor,
        '../src/dat/join_auction_category.dat',
        'join_auction_category',
        [
            'id',
            'auction_id',
            'category',
        ]
    )

    file = open('../src/normalize.sql')
    sql = file.read()
    file.close()
    cursor.executescript(sql)
    return conn


def import_dat(
        conn,
        cursor,
        dat_path,
        table_name,
        column_names
):
    file = open(dat_path, 'r')
    dat_file = csv.reader(
        file,
        delimiter='|'
    )
    concatenated_column_names = ','.join(column_names)
    for i in range(0, len(column_names)):
        if i == 0:
            concatenated_value_headers = f'?'
            if len(column_names) == 1:
                break
        else:
            concatenated_value_headers = f'{concatenated_value_headers},?'

    for row in dat_file:
        to_db = []
        while len(row) > 0:
            to_db.insert(0, row.pop())
        cursor.execute(
            f'insert into {table_name} ({concatenated_column_names}) '
            f'values ({concatenated_value_headers});', to_db
        )
    conn.commit()
    file.close()


def concatenate_column_names_for_sql(
        unique_columns
):
    for column in range(0, len(unique_columns)):
        if column == 0:
            concatenated_uniques = f'{unique_columns[column]}'
            if len(unique_columns) == 1:
                break
        else:
            concatenated_uniques = f'{concatenated_uniques},{unique_columns[column]}'
    return concatenated_uniques


def fetch_existing_item_from_many_columns(
        cursor,
        table_name,
        unique_column_names
):
    concatenated_column_names = concatenate_column_names_for_sql(unique_column_names)
    existing_item = cursor.execute(
        f"select {concatenated_column_names} "
        f"from {table_name};"
    ).fetchone()
    return existing_item


def concatenate_many_values(
        column_name,
        concatenated_values,
        existing_item,
        unique_columns
):
    if column_name == unique_columns:
        concatenated_values = f"{concatenated_values}, '{existing_item}'"
    elif column_name == 'start':
        concatenated_values = f"{concatenated_values}, " \
            f"'{now()}'"
    elif column_name == 'end':
        concatenated_values = f"{concatenated_values}, " \
            f"'{now(1)}'"
    else:
        concatenated_values = f"{concatenated_values}, '123456789'"
    return concatenated_values


def concatenate_remaining_existing_values_or_static_values(
        column_name,
        concatenated_values,
        existing_item,
        unique_columns
):
    if unique_columns.__contains__(column_name):
        concatenated_values = \
            f"{concatenated_values}, " \
                f"'{existing_item[unique_columns.index(column_name)]}'"
    else:
        concatenated_values = f"{concatenated_values}, '123456789'"
    return concatenated_values


def concatenate_first_existing_value_or_static_value(
        column_name,
        existing_item,
        unique_columns
):
    if unique_columns.__contains__(column_name):
        concatenated_values = f"'{existing_item[unique_columns.index(column_name)]}'"
    else:
        concatenated_values = f"'123456789'"
    return concatenated_values


def fetch_existing_item_from_single_column(
        cursor,
        table_name,
        column_name
):
    existing_item = cursor.execute(
        f"select {column_name} "
        f"from {table_name};"
    ).fetchone()[0]
    return existing_item


def concatenate_filler_values_for_non_unique_columns(
        existing_item,
        unique_columns,
        all_column_names
):
    for column_index in range(0, len(all_column_names)):
        column_name = all_column_names[column_index]
        if type(unique_columns) == list:
            if column_index == 0:
                concatenated_values = concatenate_first_existing_value_or_static_value(
                    column_name,
                    existing_item,
                    unique_columns
                )
            else:
                concatenated_values = concatenate_remaining_existing_values_or_static_values(
                    column_name,
                    concatenated_values,
                    existing_item,
                    unique_columns
                )
        else:
            if column_index == 0:
                if column_name == unique_columns:
                    concatenated_values = f"'{existing_item}'"
                else:
                    if column_name == 'start':
                        concatenated_values = f"'{now()}"
                    elif column_name == 'end':
                        concatenated_values = f"'{now(1)}"
                    else:
                        concatenated_values = f"'123456789'"

                if len(all_column_names) == 1:
                    break
            else:
                concatenated_values = concatenate_many_values(
                    column_name,
                    concatenated_values,
                    existing_item,
                    unique_columns
                )
    return concatenated_values


def get_existing_item(
        cursor,
        table_name,
        unique_columns
):
    if type(unique_columns) == list:
        existing_item = fetch_existing_item_from_many_columns(cursor, table_name, unique_columns)
    else:
        existing_item = fetch_existing_item_from_single_column(cursor, table_name, unique_columns)
    return existing_item


def verify_table_is_unique_on_columns(test, cursor, table_name, unique_on_column_names):
    test.assertEqual(
        [],
        duplicate_rows_from_table(
            cursor,
            table_name,
            unique_on_column_names
        )
    )


def attempt_insert_of_record_duplicate_on_unique_columns(
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


def concatenate_error_values(table_name, unique_columns):
    concatenated_error = ''
    for column_index in range(0, len(unique_columns)):
        if column_index == 0:
            concatenated_error = f"{table_name}.{unique_columns[column_index]}"
        else:
            concatenated_error = f"{concatenated_error}, {table_name}.{unique_columns[column_index]}"
    return concatenated_error


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


def auction_id_exists_in_auction_table(cursor, auction_id):
    auction_count = cursor.execute(
        "select count(*) "
        f"from auction "
        f"where id = {auction_id};"
    ).fetchone()[0]
    return auction_count > 0


def calculate_a_valid_bid_time(auction):
    auction_start = datetime.datetime.strptime(auction[3], '%Y-%m-%d %H:%M:%S')
    auction_end = datetime.datetime.strptime(auction[4], '%Y-%m-%d %H:%M:%S')
    time_range = auction_end - auction_start
    time_range_in_hours = time_range.days * 24
    bid_time = add_hours_to_datestring(auction[4], -(time_range_in_hours / 2))
    while bid_time_is_invalid(bid_time, auction_start):
        bid_time = add_hours_to_datestring(auction[4], -(time_range_in_hours / 2))

    return bid_time


def bid_time_is_invalid(bid_time, auction_start):
    bid_time = datetime.datetime.strptime(bid_time, '%Y-%m-%d %H:%M:%S')
    time_difference = bid_time - auction_start
    return time_difference.days * 24 <= 0


def get_existing_user_id(cursor):
    user_id = cursor.execute(
        "select id "
        "from user;"
    ).fetchone()[0]
    return user_id


def get_auction(cursor):
    auction = cursor.execute(
        "select id, start, end "
        "from auction;"
    ).fetchone()
    auction_id = auction[0]
    auction_start = auction[1]
    auction_end = auction[2]
    return auction_end, auction_id, auction_start


def add_trigger(trigger_dir, cursor,
                trigger_number
                ):
    trigger = open(f"{trigger_dir}/trigger{trigger_number}_add.sql", 'r')
    sql = trigger.read()
    trigger.close()
    cursor.executescript(
        sql
    )


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
        f"'{now()}', "
        f"'{now(4)}', "
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
        f"'{now()}', "
        f"10.00"
        f")"
    )


def fetch_last_row_added(cursor):
    auction_id = cursor.execute(
        "select last_insert_rowid();"
    ).fetchone()[0]
    return auction_id


def get_existing_auction_with_bid_lower_than_test(cursor, highest_bid_price):
    auction = cursor.execute(
        "select * "
        "from auction "
        f"where highest_bid < {highest_bid_price};"
    ).fetchone()
    return auction


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
            f"values ({auction_id}, '{bidder_id}', '{now()}', 12.00)"
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


def add_all_triggers(trigger_dir, cursor):
    for trigger in range(1, int(len(os.listdir("../src/triggers")) / 2)):
        add_trigger(trigger_dir, cursor, trigger)


def insert_fresh_bid(cursor):
    user_id = get_existing_user_id(cursor)
    auction = cursor.execute(
        "select * "
        "from auction;"
    ).fetchone()
    valid_bid_time = calculate_a_valid_bid_time(auction)
    cursor.execute(
        f"insert into bid "
        f"values ({auction[0]}, '{user_id}', '{valid_bid_time}', 7.75);"
    )


def verify_bid_added_to_table(test, cursor, starting_bid_count):
    test.assertEqual(
        starting_bid_count + 1,
        count_from_table(cursor, 'bid')
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


def insert_bid_from_new_user(cursor, new_user):
    auction = cursor.execute(
        "select * "
        "from auction;"
    ).fetchone()
    auction_id = auction[0]
    valid_bid_time = calculate_a_valid_bid_time(auction)
    cursor.execute(
        f"insert into bid "
        f"values ({auction_id}, '{new_user}', '{valid_bid_time}', 7.75);"
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


def generate_new_user(test, cursor):
    new_user = 'newuserwhoisdefinitelynotalreadyinthedatabase'
    verify_user_does_not_exist(test, cursor, new_user)
    return new_user


def create_new_auction_from_new_seller(test, cursor, new_seller):
    new_auction = 123456789
    test.assertEqual(
        [],
        cursor.execute(
            f'select * '
            f'from auction '
            f'where id=\'{new_auction}\';'
        ).fetchall()
    )
    cursor.execute(
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


def verify_insertion_with_exceeding_bid_sets_global_highest_price(test, cursor, auction, highest_bid_price, user_id):
    auction_id = auction[0]
    bid_time = calculate_a_valid_bid_time(auction)

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


def deny_new_bid_with_value_less_than_current_high(test, cursor, auction, user_id):
    auction_id = auction[0]
    bid_time = calculate_a_valid_bid_time(auction)
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


def current_price_still_matches_highest_bid(test, cursor, auction, highest_bid):
    auction_id = auction[0]
    test.assertEqual(
        highest_bid,
        cursor.execute(
            f"select highest_bid "
            f"from auction "
            f"where id={auction_id}"
        ).fetchone()[0]
    )


def setup_auction_with_beatable_bid(cursor):
    highest_bid_price = 123456
    auction = get_existing_auction_with_bid_lower_than_test(cursor, highest_bid_price)
    user_id = get_existing_user_id(cursor)
    return auction, highest_bid_price, user_id


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


def attempt_bid_on_item_auctioned_by_bidder(test, cursor, auction_id, seller_id):
    try:
        cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{seller_id}', "
            f"'{now()}', "
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


def fetch_seller_and_auction(cursor):
    auction = cursor.execute(
        "select id, seller_id "
        "from auction;"
    ).fetchone()
    auction_id = auction[0]
    seller_id = auction[1]
    return auction_id, seller_id


def verify_deny_seller_bid(test, cursor, bid_count):
    test.assertEqual(
        bid_count,
        count_from_table(
            cursor,
            'bid'
        ),
        "Database allowed new bid from seller of auction."
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


def attempt_bid_before_auction_start(test, cursor, auction_id, auction_start, user_id):
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
            f"'{add_hours_to_datestring(auction_start, -4)}',"
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


def attempt_bid_after_auction_ends(test, cursor, auction_end, auction_id, user_id):
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
            f"'{add_hours_to_datestring(auction_end, 4)}',"
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


def create_new_bidder_and_auction(cursor):
    seller_id = "testuser1234567890"
    bidder_id = "987654321testuser"
    add_new_users(cursor, bidder_id, seller_id)
    create_new_auction(cursor, seller_id)
    auction_id = fetch_last_row_added(cursor)
    return auction_id, bidder_id


def verify_total_bids_for_auction(test, cursor, auction_id):
    test.assertEqual(
        1,
        cursor.execute(
            "select number_of_bids "
            "from auction "
            f"where id={auction_id}"
        ).fetchone()[0]
    )


def verify_deny_bid_with_price_lower_than_current_high(test, cursor, auction_id, bidder_id):
    try:
        cursor.execute(
            "insert into bid "
            f"values ({auction_id}, '{bidder_id}','{now()}', 3.50);"
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


def verify_allow_bid_insertion_with_higher_price(test, cursor, auction_id, bidder_id):
    try:
        cursor.execute(
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
        test.assertTrue(
            False,
            f"Database failed to allow valid bid that exceeded current highest. Threw error:\n{e}"
        )


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
        f"set now='{pseudo_now}';"
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


def verify_deny_move_time_backward(test, cursor):
    try:
        cursor.execute(
            f"insert into pseudo_time "
            f"values ('{now(-1)}');"
        )
    except sqlite3.IntegrityError as e:
        test.assertEquals(
            "Users may only move the pseudo time forward.",
            str(e)
        )


def verify_allow_move_time_forward(test, cursor):
    try:
        cursor.execute(
            f"insert into pseudo_time "
            f"values ('{now()}');"
        )
    except sqlite3.IntegrityError as e:
        test.assertTrue(
            False,
            "Database failed to accept forward modification of pseudo time."
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


def verify_all_existing_auctions_end_after_start(test, cursor):
    test.assertEqual(
        [],
        cursor.execute(
            "select * "
            "from auction "
            "where end <= start;"
        ).fetchall()
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
    valid_bid_time = add_hours_to_datestring(auction_from_bid[4], -1)
    return existing_bid, valid_bid_time


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


def get_existing_auction_and_unique_users(cursor):
    existing_auction = cursor.execute(
        "select id, end "
        "from auction;"
    ).fetchone()
    existing_auction_id = existing_auction[0]
    existing_auction_end = existing_auction[1]
    valid_bid_time = add_hours_to_datestring(existing_auction_end, -1)
    all_user_ids = cursor.execute(
        "select id "
        "from user;"
    ).fetchall()
    first_user_id = all_user_ids[0][0]
    second_user_id = all_user_ids[1][0]
    return existing_auction_id, first_user_id, second_user_id, valid_bid_time


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


def generate_non_existent_auction_id(cursor):
    non_existent_auction_id = int(round(time.time() * 1000))
    while auction_id_exists_in_auction_table(
            cursor,
            non_existent_auction_id
    ):
        non_existent_auction_id = non_existent_auction_id + 1
    return non_existent_auction_id


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