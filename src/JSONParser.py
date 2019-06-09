from json import loads


def dictionary_from_json_file(filepath, top_key):
    with open(filepath, 'r') as file:
        return loads(file.read())[top_key]


def values_from_json_file(values, json_filepath, top_key, search_key):
    for obj in dictionary_from_json_file(json_filepath, top_key):
        values = extract_nested_values_from_json_with_key(values, obj, search_key)
    return remove_duplicates(values)


def values_with_relationship(values, json_filepath, top_key, child_key, parent_key):
    for obj in dictionary_from_json_file(json_filepath, top_key):
        if 


def write_categories_to_dat(categories, dat_filepath):
    file = open(dat_filepath, 'w')
    for index in range(len(categories)):
        if index == len(categories) - 1:
            file.write(f'{index + 1}|{categories[index]}')
        else:
            file.write(f'{index + 1}|{categories[index]}\n')
    file.close()


def remove_duplicates(dedupe_list):
    return list(dict.fromkeys(dedupe_list))


def extract_nested_values_from_json_with_key(values, json_object, key):
    if type(json_object) == str:
        return values
    if key in json_object:
        if type(json_object[key]) == list:
            for val in json_object[key]:
                values.append(val)
        else:
            values.append(json_object[key])

    if type(json_object) == dict:
        for dict_key in json_object:
            if type(json_object[dict_key]) == dict:
                values = extract_nested_values_from_json_with_key(values, json_object[dict_key], key)
            if type(json_object[dict_key]) == list:
                for list_item in json_object[dict_key]:
                    values = extract_nested_values_from_json_with_key(values, list_item, key)

    return values
