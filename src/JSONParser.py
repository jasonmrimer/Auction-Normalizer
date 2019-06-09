from json import loads


def dictionary_from_json_file(filepath, top_key):
    with open(filepath, 'r') as file:
        return loads(file.read())[top_key]


def values_from_json_file(values, json_filepath, top_key, search_key):
    for obj in dictionary_from_json_file(json_filepath, top_key):
        values = extract_nested_values_from_json_with_key(values, obj, search_key)
    return remove_duplicates(values)


def values_with_relationship(values, collection, child_key, parent_key):
    if type(collection) == list:
        for item in collection:
            if type(item) == dict:
                values = values_with_relationship(values, item, child_key, parent_key)
    if type(collection) == dict:
        if (child_key in collection) and (parent_key in collection):
            values.add((collection[child_key], collection[parent_key]))
        for obj in collection:
            if (type(collection[obj]) == dict) or (type(collection[obj]) == list):
                values = values_with_relationship(values, collection[obj], child_key, parent_key)
    return values


def write_categories_to_dat(categories, dat_filepath):
    file = open(dat_filepath, 'w')
    if type(categories) == list:
        for index in range(len(categories)):
            if index == len(categories) - 1:
                file.write(f'{index + 1}|{categories[index]}')
            else:
                file.write(f'{index + 1}|{categories[index]}\n')
    if type(categories) == set:
        starting_length = len(categories)
        while len(categories) > 0:
            value = categories.pop()
            if len(categories) == 0:
                file.write(f'{starting_length}|{value[0]}|{value[1]}')
            else:
                file.write(f'{starting_length - len(categories)}|{value[0]}|{value[1]}\n')
    file.close()


def remove_duplicates(dedupe_list):
    return list(dict.fromkeys(dedupe_list))


def dedupe(tuple_list):
    return set(tuple_list)


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
