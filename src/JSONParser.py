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


def dedupe(
        tuple_list
):
    return set(tuple_list)


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
