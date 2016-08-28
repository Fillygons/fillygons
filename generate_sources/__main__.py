import sys

from generate_sources.variants import get_variants


def main(path=None):
    variants = get_variants()

    for i in sorted(variants) if path is None else variants[path]():
        print(i)


main(*sys.argv[1:])
