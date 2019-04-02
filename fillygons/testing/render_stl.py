import math
from argparse import ArgumentParser
from functools import reduce

import numpy
from PIL import Image
from PIL import ImageDraw

from fillygons.testing.linalg import rotation_matrix, scale_matrix, \
    translation_matrix
from fillygons.testing.polyhedra import Polyhedron, dihedral_angle


def main(input_path, output_path):
    side_length = 40
    image_size = 1024

    polyhedron = Polyhedron.load_from_stl(input_path)
    img = Image.new('L', (image_size, image_size), 255)
    draw = ImageDraw.Draw(img)

    # TODO: Fix this mess
    def iter_projections():
        """
        Yield iterators of transformations matrix.

        Each iterator represents the projection of a separate view which is
        produced by applying the yielded matrices to all coordinates in the
        loaded STL.
        """
        def iter_transforms(quadrant, view_transform):
            quadrant_x, quadrant_y = quadrant

            # Look at the piece from the front.
            yield rotation_matrix(-.25, [1, 0, 0])

            yield from view_transform

            # Scale to mostly fill the bounding box.
            yield scale_matrix(0.9 / side_length)

            # Convert to the left-handed coordinate system used by Pillow.
            yield scale_matrix([1, -1, 1])

            # Move to the center of the unit square.
            yield translation_matrix([1 / 2, 1 / 2, 0])

            # Move to the selected quadrant of the final image.
            yield translation_matrix([quadrant_x, quadrant_y, 1])

            # Scale to the size of the quadrant.
            yield scale_matrix([image_size / 2, image_size / 2, 1])

        # Front view.
        yield iter_transforms((1, 1), [])

        # Side view.
        yield iter_transforms((0, 1), [rotation_matrix(.25, [0, 1, 0])])

        # Top view.
        yield iter_transforms((1, 0), [rotation_matrix(.25, [1, 0, 0])])

        # Orthographic view.
        yield iter_transforms(
            (0, 0),
            [
                # Turn a bit to the right.
                rotation_matrix(.04, [0, 1, 0]),
                # Look slightly from above.
                rotation_matrix(.06, [1, 0, 0])])

    for i in iter_projections():
        projection = reduce(numpy.dot, reversed(list(i)))

        def project(vector):
            return tuple(numpy.dot(projection, numpy.concatenate([vector, [1]]))[:2])

        for edge_view in polyhedron.edges:
            angle = math.pi - dihedral_angle(edge_view, edge_view.opposite)

            if angle > 0.01:
                start = project(edge_view.vertex_coordinate)
                end = project(edge_view.opposite.vertex_coordinate)

                # Direction of lines depends on the order of faces in the STL,
                # which may change due to modifications to a different part of
                # the model. Line direction affects positioning of individual
                # pixels of the line.
                draw.line(sorted([start, end]), 0, 1)

    img.save(output_path, 'PNG')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_path')

    return parser.parse_args()


def script_main():
    main(**vars(parse_args()))
