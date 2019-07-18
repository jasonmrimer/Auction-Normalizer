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


def create_im_memory_database():
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