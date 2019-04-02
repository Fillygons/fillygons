from textwrap import dedent

from fillygons.generate_sources.utils import call, GeneratedFile, \
    use_statement, fillygon_call
from fillygons.utils.deciders import Decider


def decide_test_file(decider: Decider):
    side_length = 40
    index, angle = decider.get_item(list(enumerate([60, 90, 120, 170, 180])))

    path = 'src/tests/{}.scad'.format(index + 1)

    template = dedent('''\
        {use_statement}
        
        module test(side_length, angle) {{
            intersection() {{
                sector_3d(xmin=-side_length / 2);
                
                rotate([0, 0, -angle]) {{
                    sector_3d(xmin=-side_length / 2);
                }}
                
                translate([-side_length, 0, 0]) {{
                    {fillygon_call};
                }}
            }}
        }}
        
        render() {test_call};
        ''')

    arguments = dict(
        angles=[180, angle],
        edges=[1, 1],
        filled=False,
        filled_corners=False,
        gap=0.2,
        min_concave_angle=38.0,
        min_convex_angle=38.0,
        reversed_edges=[],
        fn=8)

    content = template.format(
        use_statement=use_statement(path, 'src/_fillygon.scad'),
        fillygon_call=fillygon_call(arguments),
        test_call=call('test', angle=angle, side_length=side_length))

    return GeneratedFile(path, content)
