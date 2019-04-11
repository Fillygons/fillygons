import math
import numpy.linalg


norm = numpy.linalg.norm


def normalize(v):
    """
    Normalize the vector v.
    """
    return v / numpy.linalg.norm(v)


def projector(basis):
    """
    Projection onto a subspace with given basis, assuming the basis is
    orthonormal.
    """

    K = numpy.column_stack(basis)
    P = numpy.dot(K, K.T)
    return P


def intersect_planes(P1, P2):
    """
    Compute the intersection line of two planes P1 and P2 in parametric form.
    """
    # P1 := [s, r1, r2]
    # P2 := [s, r1, r2]
    p1s, p1r1, p1r2 = P1
    p2s, p2r1, p2r2 = P2

    # Normal vectors
    n1 = normalize(numpy.cross(p1r1, p1r2))
    n2 = normalize(numpy.cross(p2r1, p2r2))

    # Direction
    n3 = normalize(numpy.cross(n1, n2))

    # Distances
    d1 = -numpy.dot(p1s, n1)
    d2 = -numpy.dot(p2s, n2)

    # Intersection point
    p0 = numpy.cross(d2 * n1 - d1 * n2, numpy.cross(n1, n2)) / numpy.linalg.norm(numpy.cross(n1, n2)) ** 2

    return p0, n3


def rot_cw(v):
    return numpy.array([v[1], -v[0]])


def rot_ccw(v):
    return numpy.array([-v[1], v[0]])


def interpolate(a, b, t):
    return a + (b - a) * t


def _turn_cos_sin(turns):
    angle = turns * 2 * math.pi

    return math.cos(angle), math.sin(angle)


def rotation_matrix(turns, axis):
    x, y, z = normalize(axis)
    a, b = _turn_cos_sin(turns)
    c = 1 - a

    return numpy.array(
        (
            (a + x * x * c, x * y * c - z * b, x * z * c + y * b, 0),
            (x * y * c + z * b, a + y * y * c, y * z * c - x * b, 0),
            (x * z * c - y * b, y * z * c + x * b, a + z * z * c, 0),
            (0, 0, 0, 1)))


def scale_matrix(factors):
    if not hasattr(factors, '__iter__'):
        factors = factors, factors, factors

    x, y, z = factors

    return numpy.array(
        (
            (x, 0, 0, 0),
            (0, y, 0, 0),
            (0, 0, z, 0),
            (0, 0, 0, 1)))


def translation_matrix(offset):
    x, y, z = offset

    return numpy.array(
        (
            (1, 0, 0, x),
            (0, 1, 0, y),
            (0, 0, 1, z),
            (0, 0, 0, 1)))
