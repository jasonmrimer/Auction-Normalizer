def write_values_to_dat(
        values,
        dat_filepath
):
    file = open(
        dat_filepath,
        'w'
    )
    if type(values) == list:
        for index in range(len(values)):
            if index == len(values) - 1:
                file.write(
                    f'{index + 1}'
                    f'|{values[index]}'
                )
            else:
                file.write(
                    f'{index + 1}'
                    f'|{values[index]}\n'
                )
    if type(values) == set:
        starting_length = len(values)
        while len(values) > 0:
            value = values.pop()
            if len(values) == 0:
                file.write(
                    f'{starting_length}'
                    f'|"{stringify(value[0])}"'
                    f'|"{stringify(value[1])}"'
                )
            else:
                file.write(
                    f'{starting_length - len(values)}'
                    f'|"{stringify(value[0])}"'
                    f'|"{stringify(value[1])}"\n'
                )
    if type(values) == dict:
        keys = list(values.keys())
        while len(keys) > 0:
            key = keys.pop()
            value = values[key]
            print_line = str
            if type(value) == str:
                if len(keys) > 0:
                    print_line = f'"{stringify(key)}"|"{stringify(value)}"\n'
                else:
                    print_line = f'"{stringify(key)}"|"{stringify(value)}"'
            elif type(value) == dict:
                print_line = f'"{stringify(key)}"'
                for child in value:
                    print_line = f'{print_line}|"{stringify(value[child])}"'
                if len(keys) > 0:
                    print_line = f'{print_line}\n'
            file.write(f'{print_line}')
    file.close()


def stringify(
        string
):
    index_of_quote = string.find('"')
    if string.find('"') < 0:
        return string
    left = string[:index_of_quote + 1]
    right = string[index_of_quote + 1:]
    return left + '"' + stringify(right)
