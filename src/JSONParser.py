from json import loads


def parse_categories(categories, json_filepath):
    with open(json_filepath, 'r') as file:
        items = loads(file.read())['Items']
        for item in items:
            for category in item['Category']:
                categories.append(category)
    return remove_duplicates(categories)


def write_categories_to_dat(categories, dat_filepath):
    file = open(dat_filepath, 'w')
    for index in range(len(categories)):
        if index == len(categories) - 1:
            file.write(f'{index + 1}|{categories[index]}')
        else:
            file.write(f'{index + 1}|{categories[index]}\n')
    file.close()


def convert_json_categories_to_dat(json_filepath, dat_filepath):
    write_categories_to_dat(parse_categories([], json_filepath), dat_filepath)


def remove_duplicates(dedupe_list):
    return list(dict.fromkeys(dedupe_list))
