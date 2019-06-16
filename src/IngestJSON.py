from JSONParser import *
from Writer import *


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
