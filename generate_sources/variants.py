import json
import os

from sympy import GoldenRatio, acos, atan, sqrt, cbrt, pi, latex, rad, deg, S

from generate_sources.decisions import iter_decisions, Decider
from generate_sources.utils import call, serialize_value


root_path = 'src'


def get_file(path, expression, metadata):
    def write_content(file):
        use_path = os.path.relpath('_fillygon.scad', os.path.dirname(path))

        print('use <{}>'.format(use_path), file=file)
        print('render() {};'.format(serialize_value(expression)), file=file)

    return path, write_content, dict(metadata, path=path)


def decide_file(decider: Decider):
    reversed_edges = []
    side_repetitions = 1

    equilateral = decider.get_boolean()

    if equilateral:

        regular = decider.get_boolean()

        if regular:
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
                2 * pi / num_sides * i
                for i in range(num_sides)
                for _ in range(side_repetitions)]

            angles = [pi - b + a for a, b in zip(directions, directions[1:])]

            name = '{}-Gon'.format(num_sides)
            polygon_name = '{}-gon'.format(num_sides)

            if side_repetitions > 1:
                polygon_name += '-double'
                name += ' (double)'

            if reversed_edges:
                polygon_name += '-reversed-{}'.format(''.join('.r'[i] for i in reversed_edges))
        else:
            if decider.get_boolean():
                # Rhombi
                short_diagonal, long_diagonal = decider.get(
                    # Diamond
                    (1, sqrt(3)),
                    # Rhombic Dodecahedron
                    (1, sqrt(2)),
                    # Rhombic Triacontahedron
                    (1, GoldenRatio),
                    # Rhombic Enneacontahedron
                    (1, GoldenRatio ** 2),

                    # Spiral Tube n = 4 and m = 1
                    (sqrt(3), sqrt(5)),

                    # Polar Zonohedron n = 5
                    (sqrt(7 - sqrt(5)), sqrt(5 + sqrt(5))),
                    (sqrt(5 - sqrt(5)), sqrt(7 + sqrt(5))),
                    # Polar Zonohedron n = 6
                    (1, sqrt(5)),
                )

                assert short_diagonal < long_diagonal

                acute_angle = 2 * atan(S(short_diagonal) / long_diagonal)
                degrees_rounded = round(float(deg(acute_angle)))
                name = 'Rhombus ({})'.format(degrees_rounded)
                polygon_name = 'rhombus-{}'.format(degrees_rounded)

                angles = [acute_angle, pi - acute_angle, acute_angle]
            elif decider.get_boolean():
                # Flat hexagons
                opposite_angle = decider.get(
                    2 * atan(GoldenRatio),
                    pi / 2,
                    2 * atan(sqrt(2)),
                    2 * atan(1 / GoldenRatio),
                    2 * atan(1 / sqrt(2)))

                other_angle = pi - opposite_angle / 2

                degrees_rounded = round(float(deg(opposite_angle)))
                name = '6-Gon {}'.format(degrees_rounded)
                polygon_name = '6-gon-flat-{}'.format(degrees_rounded)

                angles = [
                    other_angle,
                    opposite_angle,
                    other_angle,
                    other_angle,
                    opposite_angle]
            else:
                # Special tiles
                name, polygon_name, *angles_degree = decider.get(
                    ('Rectangle', 'rectangle', 180, 90, 90, 180, 90),
                    ('Triamond', 'triamond', 60, 120, 120, 60))

                angles = [rad(a) for a in angles_degree]

        # Compute the last angle
        angles.insert(0, (len(angles) - 1) * pi - sum(angles))

        # Constant edge length for all equilateral polygons
        edges = len(angles) * [1]

    else:
        # Non-equilateral polygons
        regular = decider.get_boolean()

        if regular:

            name, polygon_name, angles_degree, edges = decider.get(
                ('3-Gon-sqrt2', '3-gon-sqrt2', [60, 60, 60], [sqrt(2), sqrt(2), sqrt(2)]),
                ('4-Gon-sqrt2', '4-gon-sqrt2', [90, 90, 90, 90], [sqrt(2), sqrt(2), sqrt(2), sqrt(2)]),

                ('3-Gon-2', '3-gon-2', [60, 60, 60], [2, 2, 2]),
                ('4-Gon-2', '4-gon-2', [90, 90, 90, 90], [2, 2, 2, 2])
            )

        else:

            name, polygon_name, angles_degree, edges = decider.get(
                ('RightIsosceleTriangle', 'right-isoscele-triangle', [45, 90, 45], [1, 1, sqrt(2)]),
                ('RightIsosceleTriangle-sqrt2', 'right-isoscele-triangle-sqrt2', [45, 90, 45], [sqrt(2), sqrt(2), 2]),

                ('RightIsosceleTriangle-sqrt2-double', 'right-isoscele-triangle-sqrt2-double', [45, 90, 45, 180], [sqrt(2), sqrt(2), 1, 1]),

                ('DeltoidalIcositetrahedron',
                 'deltoidal-icositetrahedron',
                 [deg(acos((2 - sqrt(2))/4)), deg(acos(-(2 + sqrt(2))/8)), deg(acos((2 - sqrt(2))/4)), deg(acos((2 - sqrt(2))/4))],
                 [1, 1, 2 - 1/sqrt(2), 2 - 1/sqrt(2)]),

                ('DeltoidalHexecontahedron',
                 'deltoidal-hexecontahedron',
                 [deg(acos((5 - 2*sqrt(5))/10)), deg(acos(-(5 + 2*sqrt(5))/20)), deg(acos((5 - 2*sqrt(5))/10)), deg(acos((9*sqrt(5) - 5)/40))],
                 [1, 1, (7 + sqrt(5))/6, (7 + sqrt(5))/6]),

                ('PentagonalIcositetrahedron',
                 'pentagonal-icositetrahedron',
                 [deg(acos((2 - cbrt(3*sqrt(33) + 19) - cbrt(-3*sqrt(33) + 19))/6)),
                  deg(acos((2 - cbrt(3*sqrt(33) + 19) - cbrt(-3*sqrt(33) + 19))/6)),
                  deg(acos((2 - cbrt(3*sqrt(33) + 19) - cbrt(-3*sqrt(33) + 19))/6)),
                  deg(acos((2 - cbrt(3*sqrt(33) + 19) - cbrt(-3*sqrt(33) + 19))/6)),
                  deg(acos((5 - cbrt(3*sqrt(33) + 19) - cbrt(-3*sqrt(33) + 19))/3))],
                 [1, 1, 1, (cbrt(-3*sqrt(33) + 19) + cbrt(3*sqrt(33) + 19) + 4)/6, (cbrt(-3*sqrt(33) + 19) + cbrt(3*sqrt(33) + 19) + 4)/6]),

                ('Pentagonal hexecontahedron',
                 'pentagonal-hexecontahedron',
                 [deg(acos((-2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))) - 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 4)/12)),
                  deg(acos((-2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))) - 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 4)/12)),
                  deg(acos((-2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))) - 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 4)/12)),
                  deg(acos((-2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))) - 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 4)/12)),
                  deg(acos(1 - 2*(1 - 2*((-4 + cbrt(12*GoldenRatio*(-sqrt(-15 + 81*GoldenRatio) + 9) + 44) + cbrt(44 + 12*GoldenRatio*(9 + sqrt(-15 + 81*GoldenRatio))))/12)**2)**2))],
                 [1, 1, 1,
                  6*(2 + 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio)))) / (-(-4 + 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))))**2 + 72),
                  6*(2 + 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio)))) / (-(-4 + 2**(2/3)*cbrt(3*GoldenRatio*(-sqrt(3)*sqrt(-5 + 27*GoldenRatio) + 9) + 11) + 2**(2/3)*cbrt(11 + 3*GoldenRatio*(9 + sqrt(3)*sqrt(-5 + 27*GoldenRatio))))**2 + 72)])
            )

        angles = [rad(a) for a in angles_degree]


    filled = decider.get_boolean()
    filled_corners = decider.get_boolean()
    gap = decider.get(.2, .25, .4)

    if filled_corners:
        if filled:
            variant_name = 'filled-corners'
        else:
            variant_name = 'corners'

        min_convex_angle = rad(90)
        min_concave_angle = rad(180)
    else:
        if filled:
            variant_name = 'filled'
        else:
            variant_name = 'normal'

        if min(angles) < rad(45):
            min_edge_angle = rad(75)
        else:
            min_edge_angle = rad(38)

        # Make pieces vertically symmetric.
        min_convex_angle = min_concave_angle = min_edge_angle

    path = os.path.join(
        'variants',
        '{}mm'.format(gap),
        polygon_name,
        variant_name + '.scad')

    arguments = dict(
        angles=[deg(a) for a in angles],
        edges=[float(e) for e in edges],
        reversed_edges=reversed_edges,
        filled=filled,
        filled_corners=filled_corners,
        min_convex_angle=deg(min_convex_angle),
        min_concave_angle=deg(min_concave_angle),
        gap=gap)

    metadata = dict(
        name=name,
        regular=regular,
        side_repetitions=side_repetitions,
        angles_formulae=[latex(a, inv_trig_style='full') for a in angles],
        angles_values=[float(a) for a in angles],
        edges_formulae=[latex(e, inv_trig_style='full') for e in edges],
        edges_values=[float(e) for e in edges],
        reversed_edges=reversed_edges,
        filled=filled,
        filled_corners=filled_corners,
        min_convex_angle=float(min_convex_angle),
        min_concave_angle=float(min_concave_angle),
        gap=gap)

    return get_file(path, call('fillygon', **arguments), metadata)


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
