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
    if len(argv) < 2:
        logging.warning('Usage: python skeleton_json_parser.py <path to json files>')
        sys.exit(1)

    # for f in argv[1:]:
    #     print(f)
    #     if is_json(f):
    #         filepaths.append(f)
    print(f'arg: {argv[1]}')
    directory = os.fsencode(argv[1])
    print(f'dir: {directory}')

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if is_json(filename):
            filepaths.append(os.path.join(argv[1], filename))
    # for i in range(40):
    #     filepaths.append(f'/Users/engineer/workspace/cecs535project1/data/json/items-{i}.json')

    ingest_single_value_from_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/categories.dat',
        'Items',
        'Category'
    )

    ingest_single_value_from_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/countries.dat',
        'Items',
        'Country'
    )

    ingest_related_values_from_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/locations.dat',
        'Items',
        'Location',
        'Country'
    )

    ingest_users(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/users.dat',
    )

    ingest_bids(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/bids.dat',
    )

    ingest_auctions(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/auctions.dat',
    )

    join_auction_category(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/join_auction_category.dat',
    )


if __name__ == "__main__":
    main(sys.argv)
