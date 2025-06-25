import csv
import argparse


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file',
                        type=str,
                        help='Path to csv file.')
    parser.add_argument('--where',
                        type=str,
                        default='',
                        help='Table filtering condition.')
    parser.add_argument('--aggregate',
                        type=str,
                        default='',
                        help='Column aggregation function.')

    args = parser.parse_args()
    return args


def get_data(filename: str):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)


def parse_condition(condition: str) -> tuple[str]:
    operation_list = ['=', '>=', '<=', '>', '<']

    for operation in operation_list:
        if operation in condition:
            column, value = condition.split(operation)
            return column, operation, value


def filter_data(data: list[dict], condition: str) -> list[dict]:
    filtered = []

    if not condition:
        for elem in data:
            filtered.append(elem)

        return filtered

    column, operation, value = parse_condition(condition)

    for elem in data:
        if isinstance(elem[column], int) and isinstance(value, int):
            if eval(f"elem[{column}] {operation} {int(value)}"):
                filtered.append(elem)
        elif isinstance(elem[column], float) and isinstance(value, float):
            if eval(f"elem[{column}] {operation} {float(value)}"):
                filtered.append(elem)
        else:
            if eval(f"elem[{column}] {operation} {value}"):
                filtered.append(elem)

    return filtered


def main():
    args = get_args()
    data = get_data(args.file)


if __name__ == '__main__':
    main()