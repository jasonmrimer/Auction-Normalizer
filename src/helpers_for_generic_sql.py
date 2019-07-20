import os
import time

from helpers_for_general_functions import concatenate_column_names_for_sql


def fetch_existing_record_id_from_table(cursor, table_name):
    # noinspection SqlResolve
    existing_id = cursor.execute(
        f"select id "
        f"from {table_name};"
    ).fetchone()[0]
    return existing_id


def add_trigger(cursor, trigger_dir, trigger_number):
    trigger = open(f"{trigger_dir}/trigger{trigger_number}_add.sql", 'r')
    sql = trigger.read()
    trigger.close()
    cursor.executescript(
        sql
    )


def add_all_triggers(cursor, trigger_dir):
    for trigger in range(1, int(len(os.listdir("./triggers")) / 2)):
        add_trigger(cursor, trigger_dir, trigger)


def item_id_exists_in_table(cursor, item_id, table_name):
    existing_items = cursor.execute(
        f"select * "
        f"from {table_name} "
        f"where id='{item_id}';"
    ).fetchall()
    return len(existing_items) > 0


def generate_new_id_for_table(cursor, table_name):
    new_id = round(time.time() * 1000)
    while item_id_exists_in_table(cursor, new_id, table_name):
        new_id = round(time.time() * 1000)
    return new_id


def count_from_table(
        cursor,
        table_name
):
    return cursor.execute(
        "select count(*) "
        f"from {table_name};"
    ).fetchone()[0]


def duplicates_from_table(
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


def fetch_existing_item_column_values_from_column_names(
        cursor,
        table_name,
        column_names
):
    concatenated_column_names = concatenate_column_names_for_sql(column_names)
    existing_item_key = cursor.execute(
        f"select {concatenated_column_names} "
        f"from {table_name};"
    ).fetchone()
    return existing_item_key


def fetch_existing_item_key_from_single_key(
        cursor,
        table_name,
        column_name
):
    existing_item = cursor.execute(
        f"select {column_name} "
        f"from {table_name};"
    ).fetchone()[0]
    return existing_item


def get_existing_item_from_key(
        cursor,
        table_name,
        key_columns
):
    if type(key_columns) == list:
        existing_item = fetch_existing_item_column_values_from_column_names(cursor, table_name, key_columns)
    else:
        existing_item = fetch_existing_item_key_from_single_key(cursor, table_name, key_columns)
    return existing_item


def fetch_last_row_added(cursor):
    auction_id = cursor.execute(
        "select last_insert_rowid();"
    ).fetchone()[0]
    return auction_id


def fetch_single_item_from_table(cursor, table_name):
    return cursor.execute(
        f"select * "
        f"from {table_name} "
        f"limit 1;"
    ).fetchone()