import logging
import sys
import os
from re import sub
from json import loads


def list_of_objects_from_json_file(
        filepath,
        top_key
):
    with open(filepath, 'r') as file:
        return loads(file.read())[top_key]


def values_from_json_file(
        values,
        collection,
        search_key
):
    for obj in collection:
        values = extract_nested_values_from_json_with_key(
            values,
            obj,
            search_key
        )
    if type(values) == list:
        return remove_duplicates(values)
    return values


def values_with_single_relationship(
        values,
        collection,
        child_key,
        parent_key
):
    if type(collection) == list:
        for item in collection:
            if type(item) == dict:
                values = values_with_single_relationship(values, item, child_key, parent_key)
    if type(collection) == dict:
        if (child_key in collection) and (parent_key in collection):
            values.add((collection[child_key], collection[parent_key]))
        for obj in collection:
            if (type(collection[obj]) == dict) or (type(collection[obj]) == list):
                values = values_with_single_relationship(values, collection[obj], child_key, parent_key)
    return values


def values_with_many_collocated_relationships(
        values,
        collection,
        child_keys,
        parent_key,
        old_implementation_for_users_without_location=True
):
    parents = values_from_json_file(
        [],
        collection,
        parent_key
    )
    for parent in parents:
        values[parent] = dict()
    for child in child_keys:
        sub_values = values_with_single_relationship(
            set(),
            collection,
            child,
            parent_key
        )
        for sub_value in sub_values:
            values[sub_value[1]][child] = (sub_value[0])
    if old_implementation_for_users_without_location:
        for key in list(values):
            if len(values[key]) != len(child_keys):
                del values[key]
    return values


def values_with_dislocated_relationships(
        values,
        collection,
        child_keys,
        parent_key,
        disjointed_children_keys,
        parent_unique_id
):
    for item in collection:
        uid = item[parent_key][parent_unique_id]
        values[uid] = dict()
        for child in child_keys:
            values[uid][child] = item[parent_key][child]
        for disjointed_child in disjointed_children_keys:
            values[uid][disjointed_child] = item[disjointed_child]
    return values


def remove_duplicates(
        dedupe_list
):
    return list(dict.fromkeys(dedupe_list))


def extract_nested_values_from_json_with_key(
        values,
        json_object,
        key
):
    if type(json_object) == str:
        return values
    if key in json_object:
        if type(json_object[key]) == list:
            for val in json_object[key]:
                values.append(val)
        else:
            values.append(json_object[key])

    if type(json_object) == dict:
        for dict_key in json_object:
            if type(json_object[dict_key]) == dict:
                values = extract_nested_values_from_json_with_key(values, json_object[dict_key], key)
            if type(json_object[dict_key]) == list:
                for list_item in json_object[dict_key]:
                    values = extract_nested_values_from_json_with_key(values, list_item, key)

    return values


def get_bids(
        bids,
        collection
):
    for item in collection:
        for key in item:
            if key == 'Bids':
                if item[key] is not None:
                    for bid in item[key]:
                        b = bid['Bid']
                        bids[
                            (
                                item['ItemID'],
                                b['Bidder']['UserID'],
                                b['Time'],
                                b['Amount']
                            )
                        ] = {
                            'ItemID': item['ItemID'],
                            'Bidder': b['Bidder'],
                            'Time': b['Time'],
                            'Amount': b['Amount'],
                        }
    return bids


def get_auctions(
        auctions,
        collection
):
    auctions = values_with_many_collocated_relationships(
        auctions,
        collection,
        ['Name', 'First_Bid', 'Started', 'Ends', 'Description'],
        'ItemID',
        False
    )
    for item in collection:
        if list(item.keys()).__contains__('Buy_Price'):
            auctions[item['ItemID']]['Buy_Price'] = item['Buy_Price']
        else:
            auctions[item['ItemID']]['Buy_Price'] = None
        auctions[item['ItemID']]['Seller'] = item['Seller']['UserID']
    return auctions


def join(
        joins,
        collection
):
    for item in collection:
        for cat in item['Category']:
            joins.add(
                (
                    item['ItemID'],
                    cat
                )
            )
    return joins


def get_bidders(
        bids
):
    bidders = dict()
    for bid in bids:
        bidders[bids[bid]['Bidder']['UserID']] = {
            'Rating': optional_value_from_dictionary(bids[bid]['Bidder'], 'Rating'),
            'Location': optional_value_from_dictionary(bids[bid]['Bidder'], 'Location'),
            'Country': optional_value_from_dictionary(bids[bid]['Bidder'], 'Country')
        }
    return bidders


def optional_value_from_dictionary(
        dictionary,
        optional_key
):
    if list(dictionary.keys()).__contains__(optional_key):
        return dictionary[optional_key]
    else:
        return None


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


def ingest_single_value_from_files(filepaths, dat_filepath, top_key, key):
    values = []
    for filepath in filepaths:
        values = values_from_json_file(
            values,
            list_of_objects_from_json_file(
                filepath,
                top_key
            ),
            key
        )
    write_values_to_dat(
        values,
        dat_filepath
    )


def ingest_related_values_from_files(
        filepaths,
        dat_filepath,
        top_key,
        child_keys,
        parent_key
):
    if type(child_keys) == str:
        values = set()
    else:
        values = dict()

    for filepath in filepaths:
        if type(child_keys) == str:
            values = values_with_single_relationship(
                values,
                list_of_objects_from_json_file(filepath, top_key),
                child_keys,
                parent_key
            )
        else:
            values = values_with_many_collocated_relationships(
                values,
                list_of_objects_from_json_file(filepath, top_key),
                child_keys,
                parent_key
            )
    write_values_to_dat(values, dat_filepath)


def ingest_bids(
        filepaths,
        dat_filepath
):
    bids = dict()
    for filepath in filepaths:
        bids = get_bids(
            bids,
            list_of_objects_from_json_file(
                filepath,
                'Items'
            )
        )
        write_bids_to_dat(bids, dat_filepath)


def ingest_auctions(
        filepaths,
        dat_filepath
):
    auctions = dict()
    for filepath in filepaths:
        auctions = get_auctions(
            auctions,
            list_of_objects_from_json_file(
                filepath,
                'Items'
            )
        )
    write_values_to_dat(
        auctions,
        dat_filepath,
        ['Buy_Price', 'First_Bid'],
        ['Started', 'Ends']
    )


def join_auction_category(
        filepaths,
        dat_filepath
):
    joins = set()
    for filepath in filepaths:
        joins = join(
            joins,
            list_of_objects_from_json_file(
                filepath,
                'Items'
            )
        )
    write_values_to_dat(
        joins,
        dat_filepath
    )


def ingest_users(
        filepaths,
        dat_filepath
):
    bids = dict()
    for filepath in filepaths:
        bids = get_bids(
            bids,
            list_of_objects_from_json_file(
                filepath,
                'Items'
            )
        )
    bidders = get_bidders(bids)

    sellers = dict()
    for filepath in filepaths:
        sellers = values_with_dislocated_relationships(
            sellers,
            list_of_objects_from_json_file(
                filepath,
                'Items'
            ),
            ['Rating'],
            'Seller',
            ['Location', 'Country'],
            'UserID'
        )

    users = {**bidders, **sellers}

    write_values_to_dat(
        users,
        dat_filepath
    )


def is_json(f):
    return len(f) > 5 and f[-5:] == '.json'


def main(argv):
    filepaths = []
    if len(argv) != 3:
        logging.warning('Usage: python ingest_app.py <path to json files> <path to save dat files>')
        sys.exit(1)

    directory = os.fsencode(argv[1])
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if is_json(filename):
            filepaths.append(os.path.join(argv[1], filename))

    dat_filepath = os.fsdecode(argv[2])

    ingest_single_value_from_files(
        filepaths,
        f'{dat_filepath}/categories.dat',
        'Items',
        'Category'
    )

    ingest_single_value_from_files(
        filepaths,
        f'{dat_filepath}/countries.dat',
        'Items',
        'Country'
    )

    ingest_related_values_from_files(
        filepaths,
        f'{dat_filepath}/locations.dat',
        'Items',
        'Location',
        'Country'
    )

    ingest_users(
        filepaths,
        f'{dat_filepath}/users.dat',
    )

    ingest_bids(
        filepaths,
        f'{dat_filepath}/bids.dat',
    )

    ingest_auctions(
        filepaths,
        f'{dat_filepath}/auctions.dat',
    )

    join_auction_category(
        filepaths,
        f'{dat_filepath}/join_auction_category.dat',
    )


if __name__ == "__main__":
    main(sys.argv)
