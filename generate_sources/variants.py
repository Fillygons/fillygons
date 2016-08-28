import json
import os
from functools import partial

from math import atan, sqrt, pi

from generate_sources.utils import call, serialize_value, kwargs_accumulator, \
    context_value, args_accumulator


golden_ratio = (sqrt(5) + 1) / 2
degrees = pi / 180

root_path = 'src'


def get_files():
    """
    Return a dict from filenames to file contents represented as generator
    functions yielding a list of lines.
    """
    files = {}
    metadata_entries = []

    @context_value([])
    def include(value, path, type='use'):
        return value + [(type, path)]

    argument = kwargs_accumulator()
    name_part = kwargs_accumulator()

    tags = args_accumulator()
    metadata = kwargs_accumulator()

    name_part_order = [
        ['gap'],
        ['polygon', 'variant_size', 'variant_reversed'],
        ['variant_filled', 'variant_corners', 'variant_normal']]

    def get_path():
        name_parts_map = name_part.current_value

        assert all(any(k in i for i in name_part_order) for k in name_parts_map), \
            (name_part_order, name_parts_map.keys())

        def iter_path_parts():
            for i in name_part_order:
                name_parts = [name_parts_map[j] for j in i if j in name_parts_map]

                if name_parts:
                    yield '-'.join(name_parts)

        path_parts = list(iter_path_parts())

        path_parts[-1] += '.scad'

        return os.path.join('variants', *path_parts)

    def add_file(path, write_content_fn):
        files[os.path.join(root_path, path)] = write_content_fn

    def add_fillygon_file(expression):
        path = get_path()
        current_includes = include.current_value

        def write_content(file):
            for type, path in current_includes:
                relative_path = os.path.relpath(path, os.path.dirname(path))

                print('{} <{}>'.format(type, relative_path), file=file)

            print('render() {};'.format(serialize_value(expression)), file=file)

        add_file(path, write_content)

        with metadata(path=path, tags=tags.current_value):
            metadata_entries.append(metadata.current_value)

    def add_metadata_file():
        add_file('variants.json', partial(json.dump, metadata_entries, indent=4))

    def fillygon():
        with include('src/_fillygon.scad'):
            angles = argument.current_value['angles']
            angles = [*angles, 180 * (len(angles) - 1) - sum(angles)]

            with metadata(angles=angles):
                with tags('{}-gon'.format(len(angles))):
                    add_fillygon_file(call('fillygon', **argument.current_value))

    def fillygon_gap():
        for i in .2, .25, .4:
            with name_part(gap='{}mm'.format(i)):
                with argument(gap=i):
                    fillygon()

    def fillygon_corners(filled):
        if filled:
            fillygon_gap()
        else:
            with name_part(variant_normal='normal'):
                fillygon_gap()

        with name_part(variant_corners='corners'):
            with argument(
                    filled_corners=True,
                    min_convex_angle=90,
                    min_concave_angle=180):
                with tags('filled-corners'):
                    fillygon_gap()

    def fillygon_filling():
        fillygon_corners(False)

        with name_part(variant_filled='filled'):
            with argument(filled=True):
                with tags('filled-face'):
                    fillygon_corners(True)

    def regular_fillygon(sides, side_repetitions=1):
        directions = [
            360 / sides * i
            for i in range(sides) for _ in range(side_repetitions)]
        angles = [180 - b + a for a, b in zip(directions, directions[1:])]

        with name_part(polygon='{}-gon'.format(sides)):
            with argument(angles=angles):
                if side_repetitions == 1:
                    fillygon_filling()
                else:
                    with name_part(variant_size='double'):
                        with tags('double'):
                            fillygon_filling()

    def irregular_fillygon(name, *angles):
        with name_part(polygon=name):
            with argument(angles=angles):
                with tags('irregular'):
                    fillygon_filling()

    def reversed_fillygon(sides, *reversed_edges):
        reversed_edges += (False,) * (sides - len(reversed_edges))
        name = 'reversed-{}'.format(''.join('.r'[i] for i in reversed_edges))

        with name_part(variant_reversed=name):
            with argument(reversed_edges=reversed_edges):
                with tags('reversed'):
                    regular_fillygon(sides)

    def rhombus(acute_angle):
        name = 'rhombus-{}'.format(round(acute_angle))

        irregular_fillygon(name, acute_angle, 180 - acute_angle, acute_angle)

    def six_gon_flat(opposite_angle):
        other_angle = 180 - opposite_angle / 2

        name = '6-gon-flat-{}'.format(round(opposite_angle))

        irregular_fillygon(
            name,
            other_angle,
            opposite_angle,
            other_angle,
            other_angle,
            opposite_angle)

    # Regular n-gons.
    for i in range(3, 12 + 1):
        regular_fillygon(i)

    # n-gons with reversed sides.
    reversed_fillygon(3, True)

    reversed_fillygon(4, True)
    reversed_fillygon(4, True, True)
    reversed_fillygon(4, True, False, True)

    reversed_fillygon(5, True)
    reversed_fillygon(5, True, True)
    reversed_fillygon(5, True, False, True)

    # n-gons with doubled sides.
    for i in range(3, 6 + 1):
        regular_fillygon(i, 2)

    # Rhombi
    rhombus(2 * atan(1 / sqrt(2)) / degrees)
    rhombus(2 * atan(1 / golden_ratio) / degrees)
    rhombus(2 * atan(1 / golden_ratio ** 2) / degrees)
    rhombus(2 * atan(1 / sqrt(3)) / degrees)
    rhombus(2 * atan(1 / sqrt(15)) / degrees)

    # Flat hexagons
    six_gon_flat(2 * atan(golden_ratio) / degrees)
    six_gon_flat(90)
    six_gon_flat(2 * atan(sqrt(2)) / degrees)
    six_gon_flat(2 * atan(1 / golden_ratio) / degrees)
    six_gon_flat(2 * atan(1 / sqrt(2)) / degrees)

    # Custom angles
    irregular_fillygon('rectangle', 180, 90, 90, 180, 90)
    irregular_fillygon('triamond', 60, 120, 120, 60)

    add_metadata_file()

    return files
