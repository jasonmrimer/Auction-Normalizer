from JSONParser import *


def ingest_values_from_files(filepaths, dat_filepath, key):
    values = []
    max_len = 0
    for filepath in filepaths:
        values = values_from_json_file(values, filepath, key)
    for value in values:
        if len(value) > max_len:
            max_len = len(value)
    print(f'max length{max_len}')
    write_categories_to_dat(values, dat_filepath)
