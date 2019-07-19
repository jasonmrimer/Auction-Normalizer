from helpers_for_tests import *
from helpers_for_general_functions import *
import time
import csv
import os
import sqlite3


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
    concatenated_value_headers = ''
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


def auction_id_exists_in_auction_table(cursor, auction_id):
    auction_count = cursor.execute(
        "select count(*) "
        f"from auction "
        f"where id = {auction_id};"
    ).fetchone()[0]
    return auction_count > 0


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


def add_trigger(cursor, trigger_dir, trigger_number):
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


def add_all_triggers(cursor, trigger_dir):
    for trigger in range(1, int(len(os.listdir("../src/triggers")) / 2)):
        add_trigger(cursor, trigger_dir, trigger)


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


def generate_new_user_id(cursor):
    new_user_id = 'new_user_who_is_definitely_not_already_in_the_database'
    users = fetch_all_users_with_id(cursor, new_user_id)

    while len(users) > 0:
        new_user_id = f"{new_user_id}{round(time.time() * 1000)}"
        users = fetch_all_users_with_id(cursor, new_user_id)
    return new_user_id


def fetch_all_users_with_id(cursor, new_user_id):
    users = cursor.execute(
        f"select * "
        f"from user "
        f"where id='{new_user_id}';"
    ).fetchall()
    return users


def fetch_all_auctions_with_id(cursor, new_user_id):
    users = cursor.execute(
        f"select * "
        f"from user "
        f"where id='{auction_id_exists_in_auction_table()}';"
    ).fetchall()
    return users


def create_new_auction_from_new_seller(cursor, new_seller):
    new_auction_id = round(time.time() * 1000)
    while auction_id_exists_in_auction_table(cursor, new_auction_id):
        new_auction_id = {round(time.time() * 1000)}

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
    auction = get_existing_auction_with_bid_lower_than_test(cursor, highest_bid_price)
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


def get_existing_auction_and_unique_users(cursor):
    existing_auction = cursor.execute(
        "select id, end "
        "from auction;"
    ).fetchone()
    existing_auction_id = existing_auction[0]
    existing_auction_end = existing_auction[1]
    valid_bid_time = add_hours_to_date_string(existing_auction_end, -1)
    all_user_ids = cursor.execute(
        "select id "
        "from user;"
    ).fetchall()
    first_user_id = all_user_ids[0][0]
    second_user_id = all_user_ids[1][0]
    return existing_auction_id, first_user_id, second_user_id, valid_bid_time


def generate_non_existent_auction_id(cursor):
    non_existent_auction_id = int(round(time.time() * 1000))
    while auction_id_exists_in_auction_table(
            cursor,
            non_existent_auction_id
    ):
        non_existent_auction_id = non_existent_auction_id + 1
    return non_existent_auction_id
