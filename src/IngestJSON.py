from JSONParser import *


def ingest_values_from_files(filepaths, dat_filepath, top_key, key):
    values = []
    max_len = 0
    for filepath in filepaths:
        values = values_from_json_file(values, filepath, top_key, key)
    for value in values:
        if len(value) > max_len:
            max_len = len(value)
    print(f'max length{max_len}')
    write_categories_to_dat(values, dat_filepath)


def ingest_related_values_from_files(filepaths, dat_filepath, top_key, child_key, parent_key):
    values = set()
    max_len = 0
    for filepath in filepaths:
        values = values_with_relationship(
            values,
            dictionary_from_json_file(filepath, top_key),
            child_key,
            parent_key
        )
    for value in values:
        if len(value[0]) > max_len:
            max_len = len(value[0])
    print(f'max length{max_len}')
    write_categories_to_dat(values, dat_filepath)
