import csv
import datetime
import sqlite3


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


def fetch_existing_item_from_many_columns(cursor,
                                          concatenated_uniques,
                                          table_name
                                          ):
    existing_item = cursor.execute(
        f"select {concatenated_uniques} "
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


def fetch_existing_item_from_single_column(cursor,
                                           table_name,
                                           unique_columns
                                           ):
    existing_item = cursor.execute(
        f"select {unique_columns} "
        f"from {table_name};"
    ).fetchone()[0]
    return existing_item


def generate_values_for_insertion_attempt(column_names, existing_item, unique_columns):
    for column_index in range(0, len(column_names)):
        column_name = column_names[column_index]
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

                if len(column_names) == 1:
                    break
            else:
                concatenated_values = concatenate_many_values(
                    column_name,
                    concatenated_values,
                    existing_item,
                    unique_columns
                )
    return concatenated_values


def get_existing_item(cursor,
                      table_name,
                      unique_columns
                      ):
    if type(unique_columns) == list:
        concatenated_uniques = concatenate_column_names_for_sql(unique_columns)
        existing_item = fetch_existing_item_from_many_columns(cursor, concatenated_uniques, table_name)
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
            f'insert into {table_name} '
            f'values ({concatenated_values});'
        )
    except sqlite3.IntegrityError as e:
        if type(unique_columns) == list:
            for column_index in range(0, len(unique_columns)):
                if column_index == 0:
                    concatenated_error = f"{table_name}.{unique_columns[column_index]}"
                else:
                    concatenated_error = f"{concatenated_error}, {table_name}.{unique_columns[column_index]}"

            test.assertTrue(
                str(e).__contains__(f"UNIQUE constraint failed: {concatenated_error}")
            )
        else:
            test.assertTrue(
                str(e).__contains__(f"UNIQUE constraint failed: {table_name}.{unique_columns}")
            )


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


def denies_duplicates(
        test,
        cursor,
        table_name,
        unique_columns,
        column_names
):
    starting_item_count = count_from_table(cursor, table_name)
    existing_item = get_existing_item(cursor, table_name, unique_columns)
    concatenated_values = generate_values_for_insertion_attempt(column_names, existing_item, unique_columns)
    attempt_insert_of_record_duplicate_on_unique_columns(test, cursor, concatenated_values, table_name, unique_columns)

    verify_item_count_did_not_increase_after_duplicate_insertion(test, cursor, starting_item_count, table_name)