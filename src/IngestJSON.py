from JSONParser import *
from Writer import *


def convert_json_to_dat(filepaths, dat_filepath, top_key, child_keys, parent_key=''):
    if parent_key == '':
        ingest_single_value_from_files(
            filepaths,
            dat_filepath,
            top_key,
            child_keys
        )
    else:
        ingest_related_values_from_files(
            filepaths,
            dat_filepath,
            top_key,
            child_keys,
            parent_key
        )


def ingest_single_value_from_files(filepaths, dat_filepath, top_key, key):
    values = []
    for filepath in filepaths:
        values = values_from_json_file(
            values,
            dictionary_from_json_file(
                filepath,
                top_key
            ),
            key
        )
    print(f'max length of {key}: {max_length(values)}')
    write_values_to_dat(
        values,
        dat_filepath
    )


def ingest_related_values_from_files(filepaths, dat_filepath, top_key, child_keys, parent_key):
    if type(child_keys) == str:
        values = set()
    else:
        values = dict()

    max_len = 0
    for filepath in filepaths:
        if type(child_keys) == str:
            values = values_with_single_relationship(
                values,
                dictionary_from_json_file(filepath, top_key),
                child_keys,
                parent_key
            )
        else:
            values = values_with_many_collocated_relationships(
                values,
                dictionary_from_json_file(filepath, top_key),
                child_keys,
                parent_key
            )
    for value in values:
        if len(value[0]) > max_len:
            max_len = len(value[0])
    if type(child_keys) == str:
        print(f'max length of {child_keys}: {max_length(values)}')
    write_values_to_dat(values, dat_filepath)


def ingest_related_dislocated_values_from_files(
        filepaths,
        dat_filepath,
        top_key,
        child_keys,
        parent_key,
        disjointed_children_keys,
        parent_unique_id

):
    values = dict()
    for filepath in filepaths:
        values = values_with_dislocated_relationships(
            values,
            dictionary_from_json_file(
                filepath,
                top_key
            ),
            child_keys,
            parent_key,
            disjointed_children_keys,
            parent_unique_id
        )
    for key in values:
        if type(values[key]) == str:
            print(f'max length of {key}: {max_length(values)}')
    print(f'max length of {parent_unique_id}: {max_length(list(values.keys()))}')
    write_values_to_dat(values, dat_filepath)


def max_length(values, current_max=0):
    max_len = 0
    if type(values) == str:
        max_len = len(values) if len(values) > current_max else current_max
    elif type(values) == list:
        for value in values:
            if len(value) > max_len:
                max_len = len(value)
    elif type(values) == set:
        for value in values:
            if len(value[0]) > max_len:
                max_len = len(value[0])
    elif type(values) == dict:
        for key in values:
            if len(values[key]) > max_len:
                max_len = len(values[key])
    return max_len
