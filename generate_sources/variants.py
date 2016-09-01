import json
import os

from math import atan, sqrt, pi

from generate_sources.decisions import iter_decisions, Decider
from generate_sources.utils import call, serialize_value


golden_ratio = (sqrt(5) + 1) / 2
degrees = pi / 180

root_path = 'src'

name_part_order = [
    ['gap'],
    ['polygon', 'variant_size', 'variant_reversed'],
    ['variant_filled']]


def get_path(name_part):
    assert all(any(k in i for i in name_part_order) for k in name_part), \
        (name_part_order, name_part.keys())

    def iter_path_parts():
        for i in name_part_order:
            name_parts = [name_part[j] for j in i if j in name_part]

            if name_parts:
                yield '-'.join(name_parts)

    path_parts = list(iter_path_parts())

    path_parts[-1] += '.scad'

    return os.path.join('variants', *path_parts)


def get_fillygon_file(expression, name_part, metadata, tags):
    path = get_path(name_part)

    def write_content(file):
        relative_path = os.path.relpath(path, os.path.dirname(path))

        print('use <{}>'.format(relative_path), file=file)
        print('render() {};'.format(serialize_value(expression)), file=file)

    metadata = dict(metadata, path=path, tags=tags)

    return path, write_content, metadata


def decide_file(decider: Decider):
    argument = {}
    name_part = {}
    tags = []
    metadata = {}

    if decider.get_boolean():
        # Regular n-gons.
        if decider.get_boolean():
            sides = decider.get(range(3, 12 + 1))

            if sides <= 6:
                side_repetitions = decider.get([1, 2])
            else:
                side_repetitions = 1
        else:
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

            name_part.update(variant_reversed=name)
            argument.update(reversed_edges=reversed_edges)
            tags.append('reversed')

            side_repetitions = 1

        directions = [
            360 / sides * i
            for i in range(sides) for _ in range(side_repetitions)]
        angles = [180 - b + a for a, b in zip(directions, directions[1:])]

        name_part.update(polygon='{}-gon'.format(sides))
        argument.update(angles=angles)

        if side_repetitions != 1:
            name_part.update(variant_size='double')
            tags.append('double')
    else:
        if decider.get_boolean():
            # Rhombi
            acute_angle = decider.get(
                [
                    2 * atan(1 / sqrt(2)) / degrees,
                    2 * atan(1 / golden_ratio) / degrees,
                    2 * atan(1 / golden_ratio ** 2) / degrees,
                    2 * atan(1 / sqrt(3)) / degrees,
                    2 * atan(1 / sqrt(15)) / degrees])

            name = 'rhombus-{}'.format(round(acute_angle))
            angles = [acute_angle, 180 - acute_angle, acute_angle]
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

            angles = [
                other_angle,
                opposite_angle,
                other_angle,
                other_angle,
                opposite_angle]
        else:
            name, *angles = decider.get(
                [
                    ('rectangle', 180, 90, 90, 180, 90),
                    ('triamond', 60, 120, 120, 60)])

        name_part.update(polygon=name)
        argument.update(angles=angles)
        tags.append('irregular')

    face = decider.get_boolean()
    corners = decider.get_boolean()

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

    name_part.update(variant_filled=variant_name_part)

    if face:
        argument.update(filled=True)
        tags.append('filled-face')

    if corners:
        argument.update(
            filled_corners=True,
            min_convex_angle=90,
            min_concave_angle=180)

        tags.append('filled-corners')

    gap = decider.get([.2, .25, .4])

    name_part.update(gap='{}mm'.format(gap))
    argument.update(gap=gap)

    angles = argument['angles']
    angles = [*angles, 180 * (len(angles) - 1) - sum(angles)]

    metadata.update(angles=angles)
    tags.append('{}-gon'.format(len(angles)))

    return get_fillygon_file(call('fillygon', **argument), name_part, metadata, tags)


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
