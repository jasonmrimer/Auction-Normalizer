from IngestJSON import *


def main():
    filepaths = []

    for i in range(40):
        filepaths.append(f'/Users/engineer/workspace/cecs535project1/data/json/items-{i}.json')

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
    main()
