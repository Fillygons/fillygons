#! /usr/bin/env python3

import sys, os, json, contextlib

from math import atan, sqrt, acos, pi


golden_ratio = (sqrt(5) + 1) / 2
degrees = pi / 180


class expression(str): pass


def call(function, **arguments):
	args_str = ['{} = {}'.format(k, serialize_value(v)) for k, v in sorted(arguments.items())]
	
	return expression('{}({})'.format(function, ', '.join(args_str)))


def serialize_value(value):
	if isinstance(value, list):
		return '[{}]'.format(', '.join(map(serialize_value, value)))
	elif isinstance(value, expression):
		return value
	else:
		return json.dumps(value)


def context_value(initial_value):
	def decorator(fn):
		@contextlib.contextmanager
		def decorated_function(*args, **kwargs):
			old_value = decorated_function.current_value
			decorated_function.current_value = fn(old_value, *args, **kwargs)

			try:
				yield
			finally:
				decorated_function.current_value = old_value

		decorated_function.current_value = initial_value

		return decorated_function

	return decorator


def kwargs_accumulator():
	@context_value({ })
	def name_part(value, **kwargs):
		return dict(**value, **kwargs)

	return name_part


def get_variants():
	variants = {}

	@context_value([])
	def include(value, path, type = 'use'):
		return value + [(type, path)]

	argument = kwargs_accumulator()
	name_part = kwargs_accumulator()

	name_part_order = [
		['gap'],
		['polygon', 'variant_size', 'variant_reversed'],
		['variant_filled', 'variant_corners', 'variant_normal']]

	def get_name():
		name_parts_map = name_part.current_value

		assert all(any(k in i for i in name_part_order) for k in name_parts_map), (name_part_order, name_parts_map.keys())

		def iter_path_parts():
			for i in name_part_order:
				name_parts = [name_parts_map[j] for j in i if j in name_parts_map]

				if name_parts:
					yield '-'.join(name_parts)

		path_parts = list(iter_path_parts())

		path_parts[-1] += '.scad'

		return os.path.join('src', 'variants', *path_parts)

	def add_file(expression):
		name = get_name()
		current_includes = include.current_value

		def fn():
			for type, path in current_includes:
				relative_path = os.path.relpath(path, os.path.dirname(name))

				yield '{} <{}>'.format(type, relative_path)

			yield 'render() {};'.format(serialize_value(expression))

		variants[name] = fn

	def fillygon():
		with include('src/_fillygon.scad'):
			add_file(call('fillygon', **argument.current_value))

	def fillygon_gap():
		for i in .2, .25, .4:
			with name_part(gap = '{}mm'.format(i)):
				with argument(gap = i):
					fillygon()

	def fillygon_corners(filled):
		if filled:
			fillygon_gap()
		else:
			with name_part(variant_normal = 'normal'):
				fillygon_gap()

		with name_part(variant_corners = 'corners'):
			with argument(filled_corners = True, min_convex_angle = 90, min_concave_angle = 180):
				fillygon_gap()

	def fillygon_filling():
		fillygon_corners(False)

		with name_part(variant_filled = 'filled'):
			with argument(filled = True):
				fillygon_corners(True)

	def regular_fillygon(sides, side_repetitions = 1):
		directions = [360 / sides * i for i in range(sides) for _ in range(side_repetitions)]
		angles = [180 - b + a for a, b in zip(directions, directions[1:])]

		with name_part(polygon = '{}-gon'.format(sides)):
			with argument(angles = angles):
				if side_repetitions == 1:
					fillygon_filling()
				else:
					with name_part(variant_size = 'double'):
						fillygon_filling()

	def irregular_fillygon(name, *angles):
		with name_part(polygon = name):
			with argument(angles = angles):
				fillygon_filling()

	def reversed_fillygon(sides, *reversed_edges):
		reversed_edges += (False,) * (sides - len(reversed_edges))
		name = 'reversed-{}'.format(''.join('.r'[i] for i in reversed_edges))

		with name_part(variant_reversed = name):
			with argument(reversed_edges = reversed_edges):
				regular_fillygon(sides)

	def rhombus(acute_angle):
		name = 'rhombus-{}'.format(round(acute_angle))

		irregular_fillygon(name, acute_angle, 180 - acute_angle, acute_angle)

	def six_gon_flat(opposite_angle):
		other_angle = 180 - opposite_angle / 2

		name = '6-gon-flat-{}'.format(round(opposite_angle))

		irregular_fillygon(name, other_angle, opposite_angle, other_angle, other_angle, opposite_angle)

	# Regular n-gons.
	for i in range(3, 12 + 1):
		regular_fillygon(i)

	# n-gons with reversed sides.
	reversed_fillygon(3, True)

	reversed_fillygon(4, True)
	reversed_fillygon(4, True, True)
	reversed_fillygon(4, True, False, True)

	reversed_fillygon(5, True)
	reversed_fillygon(5, True, True)
	reversed_fillygon(5, True, False, True)

	# n-gons with doubled sides.
	for i in range(3, 6 + 1):
		regular_fillygon(i, 2)

	# Rhombi
	rhombus(2 * atan(1 / sqrt(2)) / degrees)
	rhombus(2 * atan(1 / golden_ratio) / degrees)
	rhombus(2 * atan(1 / golden_ratio ** 2) / degrees)
	rhombus(2 * atan(1 / sqrt(3)) / degrees)
	rhombus(2 * atan(1 / sqrt(15)) / degrees)

	# Flat hexagons
	six_gon_flat(2 * atan(golden_ratio) / degrees)
	six_gon_flat(90)
	six_gon_flat(2 * atan(sqrt(2)) / degrees)
	six_gon_flat(2 * atan(1 / golden_ratio) / degrees)
	six_gon_flat(2 * atan(1 / sqrt(2)) / degrees)

	# Custom angles
	irregular_fillygon('rectangle', 180, 90, 90, 180, 90)
	irregular_fillygon('triamond', 60, 120, 120, 60)

	return variants


def main(path = None):
	variants = get_variants()

	for i in sorted(variants) if path is None else variants[path]():
		print(i)


main(*sys.argv[1:])
