import json
import os
from textwrap import dedent

from sympy import Rational, GoldenRatio, TribonacciConstant, acos, atan, sqrt, cbrt, pi, latex, rad, deg, S

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
    rhombus = False
    short_diagonal = 0
    long_diagonal = 1

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

            rhombus = num_sides == 4
            if rhombus:
                short_diagonal = side_repetitions * sqrt(2)
                long_diagonal = side_repetitions * sqrt(2)

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
                rhombus = True

                diagonal_ratio_num, diagonal_ratio_denom = decider.get(
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

                assert diagonal_ratio_num < diagonal_ratio_denom

                acute_angle = 2 * atan(S(diagonal_ratio_num) / diagonal_ratio_denom)
                short_diagonal = 2 * diagonal_ratio_num / sqrt(diagonal_ratio_num**2 + diagonal_ratio_denom**2)
                long_diagonal = 2 * diagonal_ratio_denom / sqrt(diagonal_ratio_num**2 + diagonal_ratio_denom**2)
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
                name, polygon_name, *angles = decider.get(
                    ('Rectangle', 'rectangle', pi, pi/2, pi/2, pi, pi/2),
                    ('Triamond', 'triamond', pi/3, 2*pi/3, 2*pi/3, pi/3))

        # Compute the last angle
        angles.insert(0, (len(angles) - 1) * pi - sum(angles))

        # Constant edge length for all equilateral polygons
        edges = len(angles) * [1]

    else:
        # Non-equilateral polygons
        regular = decider.get_boolean()

        if regular:
            name, polygon_name, angles, edges = decider.get(
                ('3-Gon (sqrt2)', '3-gon-sqrt2', [pi/3, pi/3, pi/3], [sqrt(2), sqrt(2), sqrt(2)]),
                ('4-Gon (sqrt2)', '4-gon-sqrt2', [pi/2, pi/2, pi/2, pi/2], [sqrt(2), sqrt(2), sqrt(2), sqrt(2)]),
                ('3-Gon (2)', '3-gon-2', [pi/3, pi/3, pi/3], [2, 2, 2]),
                ('4-Gon (2)', '4-gon-2', [pi/2, pi/2, pi/2, pi/2], [2, 2, 2, 2])
            )

            num_sides = len(edges)
            rhombus = num_sides == 4
            if rhombus:
                short_diagonal = edges[0] * sqrt(2)
                long_diagonal = edges[0] * sqrt(2)

        elif decider.get_boolean():
            name, polygon_name, long_side = decider.get(
                ('Triakis tetrahedron', 'triakis-tetrahedron', Rational(5, 3)),
                ('Triakis octahedron', 'triakis-octahedron', 1 + sqrt(2) / 2),
                ('Triakis icosahedron', 'triakis-icosahedron', 22 / (15 - sqrt(5))),
                ('Tetrakis hexahedron', 'tetrakis-hexahedron', Rational(4, 3)),
                ('Pentakis dodecahedron', 'pentakis-dodecahedron', 38 / (3 * (9 + sqrt(5))))
            )

            β = acos(long_side / 2)
            α = pi - 2*β

            angles = [β, β, α]
            edges = [long_side, 1, 1]

        elif decider.get_boolean():
            name, polygon_name, a, b = decider.get(
                ('Disdyakis dodecahedron', 'disdyakis-dodecahedron',
                sqrt(2*sqrt(2) + 20) / sqrt(10 - sqrt(2)),
                3*sqrt(2*sqrt(2) + 4) / (2*sqrt(10 - sqrt(2)))),
                ('Disdyakis triacontahedron', 'disdyakis-triacontahedron',
                22*sqrt(-sqrt(5) + 5)/(5*sqrt(-31*sqrt(5) + 85)),
                3*sqrt(19*sqrt(5) + 65)/(5*sqrt(-31*sqrt(5) + 85)))
            )

            α = acos((b**2 + 1 - a**2) / (2*b))
            β = acos((a**2 + 1 - b**2) / (2*a))
            γ = acos((a**2 + b**2 - 1) / (2*a*b))

            angles = [β, γ, α]
            edges = [a, b, 1]

        elif decider.get_boolean():
            name = 'Deltoidal icositetrahedron'
            polygon_name = 'deltoidal-icositetrahedron'

            α = acos((2 - sqrt(2)) / 4)
            β = acos(-(2 + sqrt(2)) / 8)
            a = 2 - 1 / sqrt(2)

            angles = [α, β, α, α]
            edges = [1, 1, a, a]

        elif decider.get_boolean():
            name = 'Deltoidal hexecontahedron'
            polygon_name = 'deltoidal-hexecontahedron'

            α = acos((5 - 2 * sqrt(5)) / 10)
            β = acos((9 * sqrt(5) - 5) / 40)
            γ = acos(-(5 + 2 * sqrt(5)) / 20)
            a = (7 + sqrt(5)) / 6

            angles = [α, γ, α, β]
            edges = [1, 1, a, a]

        elif decider.get_boolean():
            name = 'Pentagonal icositetrahedron'
            polygon_name = 'pentagonal-icositetrahedron'

            # Note: 2*t + 1 approx. 1.8393 equals the tribonacci constant
            t = (TribonacciConstant - 1) / 2

            α = acos(-t)
            β = acos(1 - 2 * t)
            a = 1 + t

            angles = [α, α, α, α, β]
            edges = [1, 1, 1, a, a]

        elif decider.get_boolean():
            name = 'Pentagonal hexecontahedron'
            polygon_name = 'pentagonal-hexecontahedron'

            # Note: real solution of the cubic equation: 8*t^3 + 8*t^2 - GoldenRatio^2 = 0
            t = (cbrt(44 + 12*GoldenRatio*(9 + sqrt(81*GoldenRatio - 15)))
               + cbrt(44 + 12*GoldenRatio*(9 - sqrt(81*GoldenRatio - 15))) - 4) / 12

            α = acos(-t)
            β = acos(1 - 2 * (1 - 2 * t**2)**2)
            a = (1 + 2 * t) / (2 * (1 - 2 * t ** 2))

            angles = [α, α, α, α, β]
            edges = [1, 1, 1, a, a]

        elif decider.get_boolean():
            enantiomorph = decider.get('laevo', 'dextro')

            name = 'Pentagon Star Half ({})'.format(enantiomorph)
            polygon_name = 'pentagon-star-half-{}'.format(enantiomorph)

            a = 2 / (sqrt(4*GoldenRatio**2 - 1) - 2*sqrt(4 - GoldenRatio**2))

            if enantiomorph == 'laevo':
                angles = [pi/2, 7*pi/10, pi/5, 3*pi/5]
                edges = [1, a, a, a/2]
            else:
                angles = [pi/2, 3*pi/5, pi/5, 7*pi/10]
                edges = [a/2, a, a, 1]

        elif decider.get_boolean():
            # General triangles
            name, polygon_name, angles, edges = decider.get(
                ('Right isoscele triangle', 'right-isoscele-triangle', [pi/4, pi/2, pi/4], [1, 1, sqrt(2)]),
                ('Right isoscele triangle (sqrt2)', 'right-isoscele-triangle-sqrt2', [pi/4, pi/2, pi/4], [sqrt(2), sqrt(2), 2]),
                ('Right isoscele triangle (sqrt2, double)', 'right-isoscele-triangle-sqrt2-double', [pi/4, pi/2, pi/4, pi], [sqrt(2), sqrt(2), 1, 1]))

        else:
            # General rectangles
            name, polygon_name, angles, edges = decider.get(
                ('Rectangle (1, sqrt2)', 'rectangle-1-sqrt2', [pi/2, pi/2, pi/2, pi/2], [sqrt(2), 1, sqrt(2), 1]),
                ('Rectangle (1, Phi)', 'rectangle-1-phi', [pi/2, pi/2, pi/2, pi/2], [GoldenRatio, 1, GoldenRatio, 1]),
                ('Rectangle (1, 2)', 'rectangle-1-2', [pi/2, pi/2, pi/2, pi/2], [2, 1, 2, 1]),
                #('Rectangle (1, double)', 'rectangle-1-double', [pi, pi/2, pi/2, pi, pi/2, pi/2], [1, 1, 1, 1, 1, 1]),

                ('Rectangle (sqrt2, Phi)', 'rectangle-sqrt2-phi', [pi/2, pi/2, pi/2, pi/2], [GoldenRatio, sqrt(2), GoldenRatio, sqrt(2)]),
                ('Rectangle (sqrt2, 2)', 'rectangle-sqrt2-2', [pi/2, pi/2, pi/2, pi/2], [2, sqrt(2), 2, sqrt(2)]),
                ('Rectangle (sqrt2, double)', 'rectangle-sqrt2-double', [pi, pi/2, pi/2, pi, pi/2, pi/2], [1, sqrt(2), 1, 1, sqrt(2), 1]),

                ('Rectangle (Phi, 2)', 'rectangle-phi-2', [pi/2, pi/2, pi/2, pi/2], [2, GoldenRatio, 2, GoldenRatio]),
                ('Rectangle (Phi, double)', 'rectangle-phi-double', [pi, pi/2, pi/2, pi, pi/2, pi/2], [1, GoldenRatio, 1, 1, GoldenRatio, 1]),

                ('Rectangle (2, double)', 'rectangle-2-double', [pi, pi/2, pi/2, pi, pi/2, pi/2], [1, 2, 1, 1, 2, 1])
            )

    diagonal_ratio = short_diagonal / long_diagonal

    filled = decider.get_boolean()
    filled_corners = decider.get_boolean()
    gap = decider.get(.2, .25, .4)

    if filled_corners:
        if filled:
            variant_name = 'filled-corners'
        else:
            variant_name = 'corners'

        min_convex_angle = pi/2
        min_concave_angle = pi
    else:
        if filled:
            variant_name = 'filled'
        else:
            variant_name = 'normal'

        if min(angles) < pi/4:
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
        rhombus=rhombus,
        side_repetitions=side_repetitions,
        angles_formulae=[latex(a, inv_trig_style='full') for a in angles],
        angles_values=[float(a) for a in angles],
        edges_formulae=[latex(e, inv_trig_style='full') for e in edges],
        edges_values=[float(e) for e in edges],
        short_diagonal_value=float(short_diagonal),
        short_diagonal_formula=latex(short_diagonal, inv_trig_style='full'),
        long_diagonal_value=float(long_diagonal),
        long_diagonal_formula=latex(long_diagonal, inv_trig_style='full'),
        diagonal_ratio_value=float(diagonal_ratio),
        diagonal_ratio_formula=latex(diagonal_ratio, inv_trig_style='full'),
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
