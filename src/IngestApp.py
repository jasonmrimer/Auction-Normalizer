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

    ingest_related_values_from_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/bidders.dat',
        'Items',
        ['Rating', 'Location', 'Country'],
        'UserID'
    )

    ingest_related_dislocated_values_from_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/sellers.dat',
        'Items',
        ['Rating'],
        'Seller',
        ['Location', 'Country'],
        'UserID'
    )


if __name__ == "__main__":
    main()
