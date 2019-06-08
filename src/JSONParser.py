from json import loads


def parse_categories(json_file_path):
    with open(json_file_path, 'r') as file:
        items = loads(file.read())
        print('===============')
        for key, value in items.items():
            print(value)
        return items
