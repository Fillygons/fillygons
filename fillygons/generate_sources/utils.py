import os
from textwrap import dedent

from fillygons.utils.openscad import call


def default_settings():
    thickness = 4

    # Look at src/_fillygon.scad for a description of all these settings.
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


def fillygon_call(arguments):
    all_arguments = dict(default_settings(), **arguments)

    expected_arguments_str = (
        'angles edges reversed_edges filled filled_corners '
        'min_convex_angle min_concave_angle gap filling_height loop_width '
        'chamfer_height thickness side_length_unit dedent_sphere_offset '
        'dedent_sphere_diameter dedent_hole_diameter large_teeth_width '
        'small_teeth_width small_teeth_gap small_teeth_cutting_depth '
        'small_teeth_cutting_width fn')

    expected_arguments = set(expected_arguments_str.split())
    actual_arguments = all_arguments.keys()

    if expected_arguments - actual_arguments:
        raise Exception(
            'Missing arguments: {}'.format(
                expected_arguments - actual_arguments))

    if actual_arguments - expected_arguments:
        raise Exception(
            'Unknown arguments: {}'.format(
                actual_arguments - expected_arguments))

    return call('fillygon', **all_arguments)


def fillygon_file(path, arguments, metadata):
    def content_thunk():
        template = dedent('''\
            use <{use_path}>
            render() {fillygon_call};
            ''')

        return template.format(
            use_path=os.path.relpath('_fillygon.scad', os.path.dirname(path)),
            fillygon_call=fillygon_call(arguments))

    return path, content_thunk, dict(metadata, path=path)


def write_text_file(path: str, content: str):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            current_content = file.read()
    else:
        current_content = None

    # Only overwrite the file if it changed, to avoid unnecessary
    # recompilation.
    if current_content != content:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
