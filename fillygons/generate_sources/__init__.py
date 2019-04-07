from argparse import ArgumentParser

from fillygons.generate_sources.variants import get_files
from fillygons.generate_sources.utils import write_text_file


def main(list_files):
    files = get_files()

    if list_files:
        for i in files:
            print(i.path)
    else:
        for i in files:
            write_text_file(i.path, i.content)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--list-files', action='store_true')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
