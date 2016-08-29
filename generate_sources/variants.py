import json
import os

from math import atan, sqrt, pi

from generate_sources.decisions import iter_decisions, Decider
from generate_sources.utils import call, serialize_value, kwargs_accumulator, \
    context_value, args_accumulator, chained_contexts


golden_ratio = (sqrt(5) + 1) / 2
degrees = pi / 180

root_path = 'src'


def decide_file(decider: Decider):
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
        ['variant_filled']]

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

    def get_fillygon_file(expression):
        path = get_path()
        current_includes = include.current_value

        def write_content(file):
            for type, path in current_includes:
                relative_path = os.path.relpath(path, os.path.dirname(path))

                print('{} <{}>'.format(type, relative_path), file=file)

            print('render() {};'.format(serialize_value(expression)), file=file)

        with metadata(path=path, tags=tags.current_value):
            return path, write_content, metadata.current_value

    def fillygon():
        with include('src/_fillygon.scad'):
            angles = argument.current_value['angles']
            angles = [*angles, 180 * (len(angles) - 1) - sum(angles)]

            with metadata(angles=angles):
                with tags('{}-gon'.format(len(angles))):
                    return get_fillygon_file(call('fillygon', **argument.current_value))

    def fillygon_gap():
        i = decider.get([.2, .25, .4])

        with name_part(gap='{}mm'.format(i)):
            with argument(gap=i):
                return fillygon()

    def fillygon_filling():
        face = decider.get_boolean()
        corners = decider.get_boolean()

        def iter_contexts():
            if face:
                if corners:
                    variant_name_part='filled-corners'
                else:
                    variant_name_part='filled'
            else:
                if corners:
                    variant_name_part='corners'
                else:
                    variant_name_part='normal'

            yield name_part(variant_filled=variant_name_part)

            if face:
                yield argument(filled=True)
                yield tags('filled-face')

            if corners:
                yield argument(
                    filled_corners=True,
                    min_convex_angle=90,
                    min_concave_angle=180)

                yield tags('filled-corners')

        with chained_contexts(list(iter_contexts())):
            return fillygon_gap()

    def regular_fillygon(sides, side_repetitions=1):
        directions = [
            360 / sides * i
            for i in range(sides) for _ in range(side_repetitions)]
        angles = [180 - b + a for a, b in zip(directions, directions[1:])]

        with name_part(polygon='{}-gon'.format(sides)):
            with argument(angles=angles):
                if side_repetitions == 1:
                    return fillygon_filling()
                else:
                    with name_part(variant_size='double'):
                        with tags('double'):
                            return fillygon_filling()

    def irregular_fillygon(name, *angles):
        with name_part(polygon=name):
            with argument(angles=angles):
                with tags('irregular'):
                    return fillygon_filling()

    if decider.get_boolean():
        sides = decider.get(range(3, 12 + 1))

        if sides <= 6:
            side_repetitions = decider.get([1, 2])
        else:
            side_repetitions = 1

        # Regular n-gons.
        return regular_fillygon(sides, side_repetitions)
    elif decider.get_boolean():
        # n-gons with reversed sides.
        sides, *reversed_edges = decider.get(
            [
                (3, True),
                (4, True),
                (4, True, True),
                (4, True, False, True),
                (5, True),
                (5, True, True),
                (5, True, False, True)])

        reversed_edges += (False,) * (sides - len(reversed_edges))
        name = 'reversed-{}'.format(''.join('.r'[i] for i in reversed_edges))

        with name_part(variant_reversed=name):
            with argument(reversed_edges=reversed_edges):
                with tags('reversed'):
                    return regular_fillygon(sides)
    elif decider.get_boolean():
        # Rhombi
        acute_angle = decider.get(
            [
                2 * atan(1 / sqrt(2)) / degrees,
                2 * atan(1 / golden_ratio) / degrees,
                2 * atan(1 / golden_ratio ** 2) / degrees,
                2 * atan(1 / sqrt(3)) / degrees,
                2 * atan(1 / sqrt(15)) / degrees])

        name = 'rhombus-{}'.format(round(acute_angle))

        return irregular_fillygon(name, acute_angle, 180 - acute_angle, acute_angle)
    elif decider.get_boolean():
        # Flat hexagons
        opposite_angle = decider.get([
            2 * atan(golden_ratio) / degrees,
            90,
            2 * atan(sqrt(2)) / degrees,
            2 * atan(1 / golden_ratio) / degrees,
            2 * atan(1 / sqrt(2)) / degrees])

        other_angle = 180 - opposite_angle / 2

        name = '6-gon-flat-{}'.format(round(opposite_angle))

        return irregular_fillygon(
            name,
            other_angle,
            opposite_angle,
            other_angle,
            other_angle,
            opposite_angle)
    else:
        name, *angles = decider.get(
            [
                ('rectangle', 180, 90, 90, 180, 90),
                ('triamond', 60, 120, 120, 60)])

        return irregular_fillygon(name, *angles)


def get_files():
    """
    Return a dict from filenames to file contents represented as a function
    taking a file object which writes the file's content to the file object.
    """
    files = {}
    metadata_entries = []

    def add_file(path, write_content_fn):
        full_path = os.path.join(root_path, path)

        assert full_path not in files

        files[full_path] = write_content_fn

    for path, write_content_fn, metadata in iter_decisions(decide_file):
        add_file(path, write_content_fn)
        metadata_entries.append(metadata)

    def write_metadata(file):
        json.dump(metadata_entries, file, indent=4, sort_keys=True)

    add_file('variants.json', write_metadata)

    return files
