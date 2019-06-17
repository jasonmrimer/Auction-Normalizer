from IngestJSON import *
import logging
import sys
import os
#
# def main(argv):
#     if len(argv) < 2:
#         print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
#         sys.exit(1)
#     # loops over all .json files in the argument
#     for f in argv[1:]:
#         if isJson(f):
#             parseJson(f)
#             print >> "Success parsing " + f
#
# if __name__ == '__main__':
#     main(sys.argv)


def is_json(f):
    return len(f) > 5 and f[-5:] == '.json'


def main(argv):
    filepaths = []
    if len(argv) != 3:
        logging.warning('Usage: python IngestApp.py <path to json files> <path to save dat files>')
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
