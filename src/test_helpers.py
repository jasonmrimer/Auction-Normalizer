import csv
import datetime
import os
import sqlite3


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
    verify_item_count_did_not_increase_after_duplicate_insertion(
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


def is_table_unique_on_columns(test, cursor, table_name, unique_on_column_names):
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


def verify_item_count_did_not_increase_after_duplicate_insertion(
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
