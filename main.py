from operator import truediv

import csv
import argparse
from tabulate import tabulate


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


def parse_filter_condition(condition: str) -> tuple[str]:
    operation_list = ['>=', '<=', '=', '>', '<']

    for operation in operation_list:
        if operation in condition:
            column, value = condition.split(operation)

            if column and value:
                return column, operation, value

            raise ValueError(f"Incorrect filter condition: '{condition}'")

    raise ValueError(f"Incorrect filter condition: '{condition}'")


def parse_aggregate_condition(condition: str) -> tuple[str]:
    if '=' in condition:
        column, aggregate_func = condition.split('=')

        if aggregate_func in ('avg', 'min', 'max'):
            return column, aggregate_func

        raise ValueError(f"Incorrect name of aggregation function: '{aggregate_func}'")

    raise ValueError(f"Incorrect aggregation condition: '{condition}'")


def filter_data(data: list[dict], condition: str) -> list[dict]:
    filtered = []

    if not condition or not data:
        return data

    column, operation, value = parse_filter_condition(condition)

    if column not in data[0].keys():
        raise KeyError(f"Column '{column}' not found.")

    if operation == '=':
        operation = '=='

    for elem in data:
        is_column_float = True
        is_value_float = True

        try:
            elem[column] = float(elem[column])
        except ValueError:
            is_column_float = False

        try:
            value = float(value)
        except ValueError:
            is_value_float = False

        if is_column_float == is_value_float:
            if eval(f"elem[column] {operation} value"):
                filtered.append(elem)
        elif is_column_float:
            raise ValueError(f"Can't compare numbers with string '{value}'")
        elif is_value_float:
            raise ValueError(f"Can't compare strings with number {value}")

    return filtered


def aggregate_data(data: list[dict], condition: str) -> list[dict]:
    if not condition:
        return data

    column, aggregate_func = parse_aggregate_condition(condition)

    if aggregate_func not in ('avg', 'min', 'max'):
        raise ValueError(f"Unknown name of aggregate function: '{aggregate_func}'")

    try:
        values = [float(row[column]) for row in data]
    except KeyError as key_error_exc:
        raise key_error_exc
    except ValueError:
        raise ValueError(f"Cannot perform aggregation on non-numeric column: {column}")

    result = dict()

    if len(values) == 0:
        result[aggregate_func] = 'None'
        return result

    if aggregate_func == 'avg':
        result['avg'] = sum(values) / len(values)
    elif aggregate_func == 'min':
        result['min'] = min(values)
    else:
        result['max'] = max(values)

    return [result]


def print_data(data: list[dict]):
    if not data:
        print('No rows matching the conditions were found.')
        return

    result = []
    result.append(data[0].keys())

    for row in data:
        result.append(row.values())

    print(tabulate(result, headers='firstrow', tablefmt='psql'))


def main():
    args = get_args()

    try:
        data = get_data(args.file)
        data = filter_data(data, args.where)
        data = aggregate_data(data, args.aggregate)
        print_data(data)
    except Exception as exc:
        print(exc)


if __name__ == '__main__':
    main()