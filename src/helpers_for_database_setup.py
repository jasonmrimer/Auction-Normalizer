import csv
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
    file = open('./create.sql')
    sql = file.read()
    file.close()
    cursor.executescript(sql)

    import_dat(
        conn,
        cursor,
        './dat/categories.dat',
        'category',
        [
            'id',
            'name'
        ]
    )

    import_dat(
        conn,
        cursor,
        './dat/countries.dat',
        'country',
        [
            'id',
            'name'
        ]
    )

    import_dat(
        conn,
        cursor,
        './dat/locations.dat',
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
        './dat/users.dat',
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
        './dat/bids.dat',
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
        './dat/auctions.dat',
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
        './dat/join_auction_category.dat',
        'join_auction_category',
        [
            'id',
            'auction_id',
            'category',
        ]
    )

    file = open('./normalize.sql')
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