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


def main(path = None):
	includes = []
	
	@contextlib.contextmanager
	def include(path, type = 'use'):
		includes.append((type, path))
		
		yield
		
		includes.pop()
	
	files = { }
	
	def generate_file(name, expression):
		current_includes = list(includes)
		
		def fn():
			for type, path in current_includes:
				yield '{} <{}>'.format(type, path)
			
			yield 'render() {};'.format(serialize_value(expression))
		
		path = 'src/{}.scad'.format(name)
		
		assert path not in files
		
		files[path] = fn
	
	def fillygon(*name_parts, **arguments):
		with include('_fillygon.scad'):
			expression = call('fillygon', **arguments)
			name = '-'.join(name_parts)
			
			generate_file(name, expression)
	
	def fillygon_gap(function, *name_parts, **arguments):
		for i in .25, .4:
			fillygon(function, *name_parts, '{}mm'.format(i), **arguments, gap = i)
	
	def fillygon_corners(function, *name_parts, **arguments):
		fillygon_gap(function, *name_parts, **arguments)
		fillygon_gap(function, *name_parts, 'corners', **arguments, filled_corners = True, min_convex_angle = 90, min_concave_angle = 180)
	
	def fillygon_filling(function, *name_parts, **arguments):
		fillygon_corners(function, *name_parts, **arguments)
		fillygon_corners(function, *name_parts, 'filled', filled = True, **arguments)
	
	def regular_fillygon(sides, side_repetitions, *name_parts, **arguments):
		fillygon_filling('{}-gon'.format(sides), *name_parts, **arguments, angles = call('regular_angles', num_sides = sides, side_repetitions = side_repetitions))
	
	def non_regular_fillygon(name, *name_parts, **arguments):
		with include('custom_angles/_{}.scad'.format(name), 'include'):
			fillygon_filling(name, *name_parts, **arguments, angles = expression('angles'))
	
	# Regular n-gons.
	for i in range(3, 12 + 1):
		regular_fillygon(i, 1)
	
	# n-gons with reversed sides.
	regular_fillygon(3, 1, 'reversed', reversed_edges = [True])
	regular_fillygon(4, 1, 'reversed-1', reversed_edges = [True])
	regular_fillygon(4, 1, 'reversed-2', reversed_edges = [True, True])
	regular_fillygon(4, 1, 'reversed-3', reversed_edges = [True, False, True])
	
	# n-gons with doubled sides.
	for i in range(3, 6 + 1):
		regular_fillygon(i, 2, 'double')
	
	# n-gons with custom angles.
	for i in os.listdir('src/custom_angles'):
		if i.startswith('_') and i.endswith('.scad'):
			non_regular_fillygon(i[1:-5])
	
	for i in sorted(files) if path is None else files[path]():
		print(i)


main(*sys.argv[1:])
