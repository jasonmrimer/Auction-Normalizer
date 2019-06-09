from JSONParser import *


def ingest_files(filepaths, dat_filepath):
    categories = []
    for filepath in filepaths:
        categories = parse_categories(categories, filepath)
    write_categories_to_dat(categories, dat_filepath)
