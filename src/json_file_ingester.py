from json_parser import *
from writer import *


def ingest_single_value_from_files(filepaths, dat_filepath, top_key, key):
    values = []
    for filepath in filepaths:
        collection = extract_object_list_from_json_file(filepath, top_key)
        assimilate_values_from_collection(
            values,
            collection,
            key
        )
    write_values_to_dat(values, dat_filepath)


def ingest_related_values_from_files(
        filepaths,
        dat_filepath,
        top_key,
        child_keys,
        parent_key
):
    values = initialize_values(child_keys)
    aggregate_values(values, filepaths, parent_key, top_key, child_keys)
    write_values_to_dat(values, dat_filepath)


def aggregate_values(values, filepaths, parent_key, top_key, child_keys):
    for filepath in filepaths:
        collection = extract_object_list_from_json_file(filepath, top_key)
        if has_single_relationship(child_keys):
            values = add_values_extracted_from_single_relationship(
                values,
                collection,
                parent_key,
                child_keys
            )
        else:
            values = values_with_many_collocated_relationships(
                collection,
                parent_key,
                child_keys,
                values
            )


def initialize_values(child_keys):
    if has_single_relationship(child_keys):
        values = set()
    else:
        values = dict()
    return values


def ingest_bids(
        filepaths,
        dat_filepath
):
    bids = dict()
    for filepath in filepaths:
        bids = get_bids(
            bids,
            extract_object_list_from_json_file(
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
            extract_object_list_from_json_file(
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
            extract_object_list_from_json_file(
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
            extract_object_list_from_json_file(
                filepath,
                'Items'
            )
        )
    bidders = get_bidders(bids)

    sellers = dict()
    for filepath in filepaths:
        sellers = values_with_dislocated_relationships(
            sellers,
            extract_object_list_from_json_file(
                filepath,
                'Items'
            ),
            ['Rating'],
            'Seller',
            ['Location', 'Country'],
            'UserID'
        )

    users = {**bidders, **sellers}
    write_values_to_dat(users, dat_filepath)


def has_single_relationship(child_keys):
    return type(child_keys) == str
