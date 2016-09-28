import sys

from generate_sources.variants import get_files


def main(path=None):
    variants = get_files()

    if path is None:
        for i in sorted(variants):
            print(i)
    else:
        with open(path, 'w', encoding='utf-8') as file:
            variants[path](file)


main(*sys.argv[1:])
