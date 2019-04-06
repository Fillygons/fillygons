from argparse import ArgumentParser

from fillygons.generate_sources.variants import get_files
from fillygons.generate_sources.utils import write_text_file


def main(list_files):
    variants = get_files()

    if list_files:
        for i in sorted(variants):
            print(i)
    else:
        for path, content_thunk in variants.items():
            write_text_file(path, content_thunk())


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--list-files', action='store_true')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
