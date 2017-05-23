import os
from argparse import ArgumentParser

from fillygons.generate_sources.variants import get_files


def main(list_files):
    variants = get_files()

    if list_files:
        for i in sorted(variants):
            print(i)
    else:
        for path, write_fn in variants.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'w', encoding='utf-8') as file:
                write_fn(file)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--list-files', action='store_true')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
