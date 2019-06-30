from json import loads


def extract_object_list_from_json_file(
        filepath,
        top_key
):
    with open(filepath, 'r') as file:
        return loads(file.read())[top_key]


def dedupe(values):
    if is_list(values):
        remove_duplicates_from_list(values)


def assimilate_values_from_collection(
        values,
        collection,
        search_key
):
    add_values_from_collection(values, collection, search_key)
    dedupe(values)


def add_values_from_collection(values, collection, search_key):
    for obj in collection:
        add_extracted_nested_values_collection(
            values,
            obj,
            search_key
        )


def add_values_extracted_from_single_relationship(values, collection, parent_key, child_key):
    if is_list(collection):
        add_extracted_values_from_list(
            collection,
            parent_key,
            child_key,
            values
        )
    if is_dict(collection):
        add_extracted_values_from_dict(
            collection,
            parent_key,
            child_key,
            values
        )
    return values


def add_extracted_values_from_dict(
        collection,
        parent_key,
        child_key,
        values
):
    collect_values_with_same_level_relationship(values, collection, parent_key, child_key)
    collect_values_with_single_relationship_from_dict_or_list(values, collection, parent_key, child_key)
    return values


def collect_values_with_same_level_relationship(values, collection, parent_key, child_key):
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


def collect_values_with_single_relationship_from_dict_or_list(values, collection, parent_key, child_key):
    for obj in collection:
        if is_item_dict_or_list(collection[obj]):
            add_values_extracted_from_single_relationship(values, collection[obj], parent_key, child_key)
    return values


def add_extracted_values_from_list(
        collection,
        parent_key,
        child_key,
        values
):
    for item in collection:
        if is_dict(item):
            values = add_values_extracted_from_single_relationship(values, item, parent_key, child_key)
    return values


def values_with_many_collocated_relationships(
        collection,
        parent_key,
        child_keys,
        values,
        old_implementation_for_users_without_location=True
):
    parents = []
    get_parent_values(parents, collection, parent_key)
    initialize_dict_with_parent_keys(values, parents)
    add_children_to_values(values, child_keys, collection, parent_key)
    assign_user_values_without_location(child_keys, old_implementation_for_users_without_location, values)
    return values


def get_parent_values(parents, collection, parent_key):
    assimilate_values_from_collection(
        parents,
        collection,
        parent_key
    )


def assign_user_values_without_location(child_keys, old_implementation_for_users_without_location, values):
    if old_implementation_for_users_without_location:
        for key in list(values):
            if len(values[key]) != len(child_keys):
                del values[key]
    return values


def add_children_to_values(values, child_keys, collection, parent_key):
    for child in child_keys:
        sub_values = add_values_extracted_from_single_relationship(set(), collection, parent_key, child)
        for sub_value in sub_values:
            values[sub_value[1]][child] = (sub_value[0])
    return values


def initialize_dict_with_parent_keys(values, parents):
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
    duplicates[:] = list(dict.fromkeys(duplicates))


def add_extracted_nested_values_collection(
        values,
        collection,
        key
):
    if is_nested_relationship(collection):
        add_values_from_same_level_relationship(values, collection, key)
        add_values_from_multi_level_relationship(values, collection, key)


def add_values_from_multi_level_relationship(values, collection, key):
    if is_dict(collection):
        crawl_dict_for_nested_relationships(values, collection, key)


def crawl_dict_for_nested_relationships(values, collection, key):
    for dict_key in collection:
        extract_values_from_dict(values, collection, dict_key, key)
        extract_values_from_list(collection, dict_key, key, values)


def extract_values_from_list(collection, dict_key, parent_key, values):
    if is_list(collection[dict_key]):
        for list_item in collection[dict_key]:
            add_extracted_nested_values_collection(values, list_item, parent_key)


def extract_values_from_dict(values, collection, dict_key, key):
    if is_dict(collection[dict_key]):
        add_extracted_nested_values_collection(values, collection[dict_key], key)


def add_values_from_same_level_relationship(values, collection, key):
    if key in collection:
        append_value(values, collection, key)


def append_value(values, collection, key):
    if is_list(collection[key]):
        for val in collection[key]:
            values.append(val)
    else:
        values.append(collection[key])


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


def is_nested_relationship(collection):
    return type(collection) != str


def is_item_dict_or_list(item):
    return is_list(item) or is_dict(item)
