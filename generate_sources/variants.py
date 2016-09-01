import json
import os

from math import atan, sqrt, pi

from generate_sources.decisions import iter_decisions, Decider
from generate_sources.utils import call, serialize_value


golden_ratio = (sqrt(5) + 1) / 2
degrees = pi / 180

root_path = 'src'


def get_fillygon_file(path, expression, metadata):
    def write_content(file):
        use_path = os.path.relpath('_fillygon.scad', os.path.dirname(path))

        print('use <{}>'.format(use_path), file=file)
        print('render() {};'.format(serialize_value(expression)), file=file)

    return path, write_content, dict(metadata, path=path)


def decide_file(decider: Decider):
    tags = []
    metadata = {}

    reversed_edges = []

    if decider.get_boolean():
        side_repetitions = 1

        # Regular n-gons.
        if decider.get_boolean():
            num_sides = decider.get_item(range(3, 12 + 1))

            if num_sides <= 6:
                side_repetitions = decider.get(1, 2)
        else:
            # n-gons with reversed sides.
            num_sides, *reversed_edges = decider.get(
                (3, True),
                (4, True),
                (4, True, True),
                (4, True, False, True),
                (5, True),
                (5, True, True),
                (5, True, False, True))

            reversed_edges += (False,) * (num_sides - len(reversed_edges))

        directions = [
            360 / num_sides * i
            for i in range(num_sides)
            for _ in range(side_repetitions)]

        angles = [
            180 - b + a
            for a, b in zip(directions, directions[1:] + directions)]

        polygon_name = '{}-gon'.format(num_sides)

        if side_repetitions > 1:
            polygon_name += '-double'
            tags.append('double')

        if reversed_edges:
            polygon_name += '-reversed-{}'.format(''.join('.r'[i] for i in reversed_edges))
            tags.append('reversed')
    else:
        if decider.get_boolean():
            # Rhombi
            acute_angle = decider.get(
                2 * atan(1 / sqrt(2)) / degrees,
                2 * atan(1 / golden_ratio) / degrees,
                2 * atan(1 / golden_ratio ** 2) / degrees,
                2 * atan(1 / sqrt(3)) / degrees,
                2 * atan(1 / sqrt(15)) / degrees)

            polygon_name = 'rhombus-{}'.format(round(acute_angle))
            angles = [acute_angle, 180 - acute_angle, acute_angle]
        elif decider.get_boolean():
            # Flat hexagons
            opposite_angle = decider.get(
                2 * atan(golden_ratio) / degrees,
                90,
                2 * atan(sqrt(2)) / degrees,
                2 * atan(1 / golden_ratio) / degrees,
                2 * atan(1 / sqrt(2)) / degrees)

            other_angle = 180 - opposite_angle / 2

            polygon_name = '6-gon-flat-{}'.format(round(opposite_angle))

            angles = [
                other_angle,
                opposite_angle,
                other_angle,
                other_angle,
                opposite_angle]
        else:
            polygon_name, *angles = decider.get(
                ('rectangle', 180, 90, 90, 180, 90),
                ('triamond', 60, 120, 120, 60))

        tags.append('irregular')

    filled = decider.get_boolean()
    filled_corners = decider.get_boolean()
    gap = decider.get(.2, .25, .4)

    if filled_corners:
        min_convex_angle = 90
        min_concave_angle = 180

        tags.append('filled-corners')

        if filled:
            variant_name = 'filled-corners'
        else:
            variant_name = 'corners'
    else:
        if filled:
            variant_name = 'filled'
        else:
            variant_name = 'normal'

        min_convex_angle = 38
        min_concave_angle = 38

    metadata.update(angles=angles)

    tags.append('{}-gon'.format(len(angles)))

    return get_fillygon_file(
        os.path.join(
            'variants',
            '{}mm'.format(gap),
            polygon_name,
            variant_name + '.scad'),
        call(
            'fillygon',
            angles=angles[:-1],
            reversed_edges=reversed_edges,
            filled=filled,
            filled_corners=filled_corners,
            min_convex_angle=min_convex_angle,
            min_concave_angle=min_concave_angle,
            gap=gap),
        dict(metadata, tags=tags))


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
