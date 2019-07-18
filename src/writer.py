from re import sub


def new_line(
        values
):
    return '\n' if len(values) > 0 else ''


def write_values_to_dat(
        values,
        dat_filepath,
        cash_keys=None,
        date_keys=None
):
    if cash_keys is None:
        cash_keys = []
    if date_keys is None:
        date_keys = []
    file = open(
        dat_filepath,
        'w'
    )
    if type(values) == list:
        starting_length = len(values)
        while len(values) > 0:
            value = values.pop()
            file.write(
                f'"{starting_length - len(values)}"'
                f'|"{stringify(value)}"'
                f'{new_line(values)}'
            )
    if type(values) == set:
        starting_length = len(values)
        while len(values) > 0:
            value = values.pop()
            file.write(
                f'{starting_length - len(values)}'
                f'|"{stringify(value[0])}"'
                f'|"{stringify(value[1])}"'
                f'{new_line(values)}'
            )
    if type(values) == dict:
        keys = list(values.keys())
        while len(keys) > 0:
            key = keys.pop()
            value = values[key]
            print_line = ''
            if type(value) == str:
                print_line = f'"{stringify(key)}"|"{stringify(value)}"'
            elif type(value) == dict:
                print_line = f'"{stringify(key)}"'
                child_keys = list(value.keys())
                child_keys.reverse()
                while len(child_keys) > 0:
                    child_key = child_keys.pop()
                    child_value = value[child_key]
                    if cash_keys.__contains__(child_key):
                        print_line = f'{print_line}|"{stringify(json_cash_to_sql(child_value))}"'
                    elif date_keys.__contains__(child_key):
                        print_line = f'{print_line}|"{stringify(json_date_to_sqlite(child_value))}"'
                    else:
                        print_line = f'{print_line}|"{stringify(child_value)}"'
            file.write(
                f'{print_line}'
                f'{new_line(keys)}'
            )
    file.close()


def write_bids_to_dat(
        bids,
        dat_filepath
):
    file = open(
        dat_filepath,
        'w'
    )
    keys = list(bids.keys())
    item_id = 'ItemID'
    bidder = 'Bidder'
    user_id = 'UserID'
    time = 'Time'
    amount = 'Amount'
    while len(keys) > 0:
        key = keys.pop()
        bid = bids[key]
        print_line = f'' \
            f'"{stringify(bid[item_id])}"' \
            f'|"{stringify(bid[bidder][user_id])}"' \
            f'|"{stringify(json_date_to_sqlite(bid[time]))}"' \
            f'|"{stringify(json_cash_to_sql(bid[amount]))}"'
        if len(keys) > 0:
            print_line = f'{print_line}\n'
        file.write(print_line)
    file.close()


def stringify(
        string
):
    if string is None:
        return 'NULL'
    if type(string) != str:
        return string
    index_of_quote = string.find('"')
    if string.find('"') < 0:
        return string
    left = string[:index_of_quote + 1]
    right = string[index_of_quote + 1:]
    return left + '"' + stringify(right)


def json_month_to_sqlite(mon):
    months = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    if mon in months:
        return months[mon]
    else:
        return mon


def json_date_to_sqlite(date):
    date = date.strip().split(' ')
    dt = date[0].split('-')
    date = f'20{dt[2]}-{json_month_to_sqlite(dt[0])}-{dt[1]} {date[1]}'
    return date


def json_cash_to_sql(cash):
    if cash is None or len(cash) == 0:
        return cash
    return sub(r'[^\d.]', '', cash)
