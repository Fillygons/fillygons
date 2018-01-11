import json
import os
from textwrap import dedent

from sympy import GoldenRatio, acos, atan, sqrt, cbrt, pi, latex, rad, deg, S

from fillygons.generate_sources.decisions import iter_decisions, Decider
from fillygons.generate_sources.utils import call


root_path = 'src'


def get_default_settings():
    thickness = 4

    # Look at src/_fillygon.scad for a description of all these settings:
    return dict(
        thickness=thickness,
        loop_width=2 * thickness,
        filling_height=1,
        side_length_unit=40,
        chamfer_height=1,
        fn=32,
        dedent_sphere_offset=0.6,
        dedent_sphere_diameter=3,
        dedent_hole_diameter=1.7,
        large_teeth_width=3.9,
        small_teeth_width=1.6,
        small_teeth_gap=1,
        small_teeth_cutting_depth=5.5,
        small_teeth_cutting_width=0.6)


def get_fillygon_call(arguments):
    all_arguments = dict(get_default_settings(), **arguments)

    excepted_arguments = (
        'angles edges reversed_edges filled filled_corners '
        'min_convex_angle min_concave_angle gap filling_height loop_width '
        'chamfer_height thickness side_length_unit dedent_sphere_offset '
        'dedent_sphere_diameter dedent_hole_diameter large_teeth_width '
        'small_teeth_width small_teeth_gap small_teeth_cutting_depth '
        'small_teeth_cutting_width fn')

    assert all_arguments.keys() == set(excepted_arguments.split())

    return call('fillygon', **all_arguments)


def get_fillygon_file(path, arguments, metadata):
    def content_thunk():
        template = dedent('''\
            use <{use_path}>
            render() {fillygon_call};
            ''')

        return template.format(
            use_path=os.path.relpath('_fillygon.scad', os.path.dirname(path)),
            fillygon_call=get_fillygon_call(arguments))

    return path, content_thunk, dict(metadata, path=path)


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
                ('3-Gon (sqrt2)', '3-gon-sqrt2', [60, 60, 60], [sqrt(2), sqrt(2), sqrt(2)]),
                ('4-Gon (sqrt2)', '4-gon-sqrt2', [90, 90, 90, 90], [sqrt(2), sqrt(2), sqrt(2), sqrt(2)]),

                ('3-Gon (2)', '3-gon-2', [60, 60, 60], [2, 2, 2]),
                ('4-Gon (2)', '4-gon-2', [90, 90, 90, 90], [2, 2, 2, 2])
            )

        elif decider.get_boolean():
            name = 'Deltoidal icositetrahedron'
            polygon_name = 'deltoidal-icositetrahedron'

            α = deg(acos((2 - sqrt(2)) / 4))
            β = deg(acos(-(2 + sqrt(2)) / 8))
            a = 2 - 1 / sqrt(2)

            angles_degree = [α, β, α, α]
            edges = [1, 1, a, a]
        elif decider.get_boolean():
            name = 'Deltoidal hexecontahedron'
            polygon_name = 'deltoidal-hexecontahedron'

            α = deg(acos((5 - 2 * sqrt(5)) / 10))
            β = deg(acos((9 * sqrt(5) - 5) / 40))
            γ = deg(acos(-(5 + 2 * sqrt(5)) / 20))
            a = (7 + sqrt(5)) / 6

            angles_degree = [α, γ, α, β]
            edges = [1, 1, a, a]
        elif decider.get_boolean():
            name = 'Pentagonal icositetrahedron'
            polygon_name = 'pentagonal-icositetrahedron'

            # Note: 2*t + 1 approx. 1.8393 equals the tribonacci constant
            t = (cbrt(19 + 3*sqrt(33)) + cbrt(19 - 3*sqrt(33)) - 2) / 6

            α = deg(acos(-t))
            β = deg(acos(1 - 2 * t))
            a = 1 + t

            angles_degree = [α, α, α, α, β]
            edges = [1, 1, 1, a, a]
        elif decider.get_boolean():
            name = 'Pentagonal hexecontahedron'
            polygon_name = 'pentagonal-hexecontahedron'

            # Note: real solution of the cubic equation: 8*t^3 + 8*t^2 - GoldenRatio^2 = 0
            t = (cbrt(44 + 12*GoldenRatio*(9 + sqrt(81*GoldenRatio - 15)))
               + cbrt(44 + 12*GoldenRatio*(9 - sqrt(81*GoldenRatio - 15))) - 4) / 12

            α = deg(acos(-t))
            β = deg(acos(1 - 2 * (1 - 2 * t**2)**2))
            a = (1 + 2 * t) / (2 * (1 - 2 * t ** 2))

            angles_degree = [α, α, α, α, β]
            edges = [1, 1, 1, a, a]
        else:
            name, polygon_name, angles_degree, edges = decider.get(
                ('Right isoscele triangle', 'right-isoscele-triangle', [45, 90, 45], [1, 1, sqrt(2)]),
                ('Right isoscele triangle (sqrt2)', 'right-isoscele-triangle-sqrt2', [45, 90, 45], [sqrt(2), sqrt(2), 2]),
                ('Right isoscele triangle (sqrt2, double)', 'right-isoscele-triangle-sqrt2-double', [45, 90, 45, 180], [sqrt(2), sqrt(2), 1, 1]))

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

    return get_fillygon_file(path, arguments, metadata)


def get_files():
    """
    Return a dict from filenames to functions which return the contents of
    each file.
    """
    files = {}
    metadata_entries = []

    def add_file(path, write_content_fn):
        full_path = os.path.join(root_path, path)

        assert full_path not in files

        files[full_path] = write_content_fn

    for path, content_thunk, metadata in iter_decisions(decide_file):
        add_file(path, content_thunk)
        metadata_entries.append(metadata)

    def metadata_thunk():
        return json.dumps(metadata_entries, indent=4, sort_keys=True)

    add_file('variants.json', metadata_thunk)

    return files
