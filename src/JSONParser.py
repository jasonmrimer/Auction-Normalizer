from json import loads


def extract_object_list_from_json_file(
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
    if is_list(values):
        return remove_duplicates_from_list(values)
    return values


def values_with_single_relationship(
        collection,
        parent_key,
        child_key,
        values
):
    if is_list(collection):
        values = extract_values_from_list(
            collection,
            parent_key,
            child_key,
            values
        )
    if is_dict(collection):
        values = extract_values_from_dict(
            collection,
            parent_key,
            child_key,
            values
        )
    return values


def extract_values_from_dict(
        collection,
        parent_key,
        child_key,
        values
):
    values = collect_values_with_same_level_relationship(
        collection,
        parent_key,
        child_key,
        values
    )
    values = collect_values_with_single_relationship_from_dict_or_list(
        collection,
        parent_key,
        child_key,
        values
    )
    return values


def collect_values_with_same_level_relationship(
        collection,
        parent_key,
        child_key,
        values
):
    if is_same_level_relationship(
            collection,
            parent_key,
            child_key
    ):
        values.add(
            (
                collection[child_key],
                collection[parent_key]
            )
        )
    return values


def collect_values_with_single_relationship_from_dict_or_list(
        collection,
        parent_key,
        child_key,
        values
):
    for obj in collection:
        if is_item_dict_or_list(collection[obj]):
            values = values_with_single_relationship(
                collection[obj],
                parent_key,
                child_key,
                values
            )
    return values


def extract_values_from_list(
        collection,
        parent_key,
        child_key,
        values
):
    for item in collection:
        if is_dict(item):
            values = values_with_single_relationship(
                item,
                parent_key,
                child_key,
                values
            )
    return values


def values_with_many_collocated_relationships(
        collection,
        parent_key,
        child_keys,
        values,
        old_implementation_for_users_without_location=True
):
    parents = values_from_json_file(
        [],
        collection,
        parent_key
    )
    values = initialize_dict_with_parent_keys(parents, values)
    values = add_child_values(child_keys, collection, parent_key, values)
    values = assign_user_values_without_location(child_keys, old_implementation_for_users_without_location, values)
    return values


def assign_user_values_without_location(child_keys, old_implementation_for_users_without_location, values):
    if old_implementation_for_users_without_location:
        for key in list(values):
            if len(values[key]) != len(child_keys):
                del values[key]
    return values


def add_child_values(child_keys, collection, parent_key, values):
    for child in child_keys:
        sub_values = values_with_single_relationship(
            collection,
            parent_key,
            child,
            set()
        )
        for sub_value in sub_values:
            values[sub_value[1]][child] = (sub_value[0])
    return values


def initialize_dict_with_parent_keys(parents, values):
    for parent in parents:
        values[parent] = dict()
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


def remove_duplicates_from_list(
        duplicates
):
    return list(dict.fromkeys(duplicates))


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
        collection,
        'ItemID',
        ['Name', 'First_Bid', 'Started', 'Ends', 'Description'],
        auctions,
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


def is_list(values):
    return type(values) == list


def is_dict(collection):
    return type(collection) == dict


def is_same_level_relationship(collection, parent_key, child_key):
    return (child_key in collection) and (parent_key in collection)


def is_item_dict_or_list(item):
    return is_list(item) or is_dict(item)
