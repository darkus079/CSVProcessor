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


def main():
    args = get_args()
    data = get_data(args.file)
    print(data)


if __name__ == '__main__':
    main()