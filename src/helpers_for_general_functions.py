import datetime
import helpers_for_sql


def add_hours_to_date_string(
        date_string,
        add_hours=0
):
    datetime_object = \
        datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S') \
        + datetime.timedelta(hours=add_hours)
    return datetime_object.strftime('%Y-%m-%d %H:%M:%S')


def concatenate_column_names_for_sql(
        unique_columns
):
    concatenated_uniques = ''
    for column in range(0, len(unique_columns)):
        if column == 0:
            concatenated_uniques = f'{unique_columns[column]}'
            if len(unique_columns) == 1:
                break
        else:
            concatenated_uniques = f'{concatenated_uniques},{unique_columns[column]}'
    return concatenated_uniques


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
            f"'{now_plus_days()}'"
    elif column_name == 'end':
        concatenated_values = f"{concatenated_values}, " \
            f"'{now_plus_days(1)}'"
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


def concatenate_filler_values_for_non_unique_columns(
        existing_item,
        unique_columns,
        all_column_names
):
    concatenated_values = ''
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
                        concatenated_values = f"'{now_plus_days()}"
                    elif column_name == 'end':
                        concatenated_values = f"'{now_plus_days(1)}"
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


def concatenate_error_values(table_name, unique_columns):
    concatenated_error = ''
    for column_index in range(0, len(unique_columns)):
        if column_index == 0:
            concatenated_error = f"{table_name}.{unique_columns[column_index]}"
        else:
            concatenated_error = f"{concatenated_error}, {table_name}.{unique_columns[column_index]}"
    return concatenated_error


def calculate_a_valid_bid_time(auction):
    auction_start = datetime.datetime.strptime(auction[3], '%Y-%m-%d %H:%M:%S')
    auction_end = datetime.datetime.strptime(auction[4], '%Y-%m-%d %H:%M:%S')
    time_range = auction_end - auction_start
    time_range_in_hours = time_range.days * 24
    bid_time = add_hours_to_date_string(auction[4], - int(time_range_in_hours / 2))
    while bid_time_is_invalid(bid_time, auction_start):
        bid_time = add_hours_to_date_string(auction[4], - int(time_range_in_hours / 2))

    return bid_time


def bid_time_is_invalid(bid_time, auction_start):
    bid_time = datetime.datetime.strptime(bid_time, '%Y-%m-%d %H:%M:%S')
    time_difference = bid_time - auction_start
    return time_difference.days * 24 <= 0


def now_plus_days(
        add_days=0
):
    return (datetime.datetime.now() + datetime.timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M:%S')