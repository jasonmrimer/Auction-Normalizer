from IngestJSON import ingest_files


def main():
    filepaths = []
    for i in range(40):
        filepaths.append(f'/Users/engineer/workspace/cecs535project1/data/json/items-{i}.json')

    ingest_files(
        filepaths,
        '/Users/engineer/workspace/cecs535project1/flyway-5.2.4/sql/categories.dat'
    )


if __name__ == "__main__":
    main()
