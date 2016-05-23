#! /usr/bin/env python3

import sys, os, json, contextlib


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


def main(path = None):
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

	def get_file(expression):
		current_includes = include.current_value
		
		def fn():
			for type, path in current_includes:
				yield '{} <{}>'.format(type, path)
			
			yield 'render() {};'.format(serialize_value(expression))

		return get_name(), fn
	
	def fillygon():
		with include('_fillygon.scad'):
			expression = call('fillygon', **argument.current_value)

			yield get_file(expression)

	def fillygon_gap():
		for i in .2, .25, .4:
			with name_part(gap = '{}mm'.format(i)):
				with argument(gap = i):
					yield from fillygon()
	
	def fillygon_corners(filled):
		if filled:
			yield from fillygon_gap()
		else:
			with name_part(variant_normal = 'normal'):
				yield from fillygon_gap()

		with name_part(variant_corners = 'corners'):
			with argument(filled_corners = True, min_convex_angle = 90, min_concave_angle = 180):
				yield from fillygon_gap()
	
	def fillygon_filling():
		yield from fillygon_corners(False)

		with name_part(variant_filled = 'filled'):
			with argument(filled = True):
				yield from fillygon_corners(True)
	
	def regular_fillygon(sides):
		with name_part(polygon = '{}-gon'.format(sides)):
			with argument(angles = call('regular_angles', num_sides = sides)):
				yield from fillygon_filling()

	def non_regular_fillygon(name):
		with include('custom_angles/_{}.scad'.format(name), 'include'):
			with name_part(polygon = name):
				with argument(angles = expression('angles')):
					yield from fillygon_filling()

	def reversed_fillygon(sides, variant_reversed, *reversed_edges):
		with name_part(variant_reversed = variant_reversed):
			with argument(reversed_edges = reversed_edges):
				yield from regular_fillygon(sides)

	def variants():
		# Regular n-gons.
		for i in range(3, 12 + 1):
			yield from regular_fillygon(i)

		# n-gons with reversed sides.
		yield from reversed_fillygon(3, 'reversed-r..', True)

		yield from reversed_fillygon(4, 'reversed-r...', True)
		yield from reversed_fillygon(4, 'reversed-rr..', True, True)
		yield from reversed_fillygon(4, 'reversed-r.r.', True, False, True)

		yield from reversed_fillygon(5, 'reversed-r....', True)
		yield from reversed_fillygon(5, 'reversed-rr...', True, True)
		yield from reversed_fillygon(5, 'reversed-r.r..', True, False, True)

		with name_part(variant_size = 'double'):
			with argument(side_repetitions = 2):
				# n-gons with doubled sides.
				for i in range(3, 6 + 1):
					yield from regular_fillygon(i)

		# n-gons with custom angles.
		for i in os.listdir('src/custom_angles'):
			if i.startswith('_') and i.endswith('.scad'):
				yield from non_regular_fillygon(i[1:-5])

	files = dict(variants())

	for i in sorted(files) if path is None else files[path]():
		print(i)


main(*sys.argv[1:])
