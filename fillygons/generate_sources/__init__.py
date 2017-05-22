from argparse import ArgumentParser

from fillygons.generate_sources.variants import get_files


def main(path):
    variants = get_files()

    if path is None:
        for i in sorted(variants):
            print(i)
    else:
        with open(path, 'w', encoding='utf-8') as file:
            variants[path](file)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('path', nargs='?')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
