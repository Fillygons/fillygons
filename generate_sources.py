import sys, os, json, collections


symbol = collections.namedtuple('symbol', ['name'])

def serialize_value(value):
	if isinstance(value, list):
		return '[{}]'.format(', '.join(map(serialize_value, value)))
	elif isinstance(value, symbol):
		return value.name
	else:
		return json.dumps(value)


def main(path = None):
	files = { }
	
	def generate_file(function : list, includes : list, *name_parts, **arguments):
		def fn():
			for type, path in [('use', '_fillygon.scad')] + includes:
				yield '{} <{}>'.format(type, path)
			
			args_str = ['{} = {}'.format(k, serialize_value(v)) for k, v in sorted(arguments.items())]
			
			yield 'render() {}({});'.format(function, ', '.join(args_str))
		
		path = 'src/{}.scad'.format('-'.join(name_parts))
		
		assert path not in files
		
		files[path] = fn
	
	def fillygon_gap(function, includes, *name_parts, **arguments):
		for i in .25, .4:
			generate_file(function, includes, *name_parts, '{}mm'.format(i), **arguments, gap = i)
	
	def fillygon_filling(function, includes, *name_parts, **arguments):
		fillygon_gap(function, includes, *name_parts, **arguments)
		fillygon_gap(function, includes, *name_parts, 'filled', filled = True, **arguments)
	
	def regular_fillygon(sides, *name_parts, **arguments):
		fillygon_filling('regular_fillygon', [], '{}-gon'.format(sides), *name_parts, **arguments, num_sides = sides)
	
	def non_regular_fillygon(name, *name_parts, **arguments):
		fillygon_filling('fillygon', [('include', 'custom_angles/{}.scad'.format(name))], name, *name_parts, **arguments, angles = symbol('angles'))
	
	# Regular n-gons.
	for i in range(3, 12 + 1):
		regular_fillygon(i)
	
	# n-gons with reversed sides.
	regular_fillygon(3, 'reversed', reversed_edges = [True])
	regular_fillygon(4, 'reversed-1', reversed_edges = [True])
	regular_fillygon(4, 'reversed-2', reversed_edges = [True, True])
	regular_fillygon(4, 'reversed-3', reversed_edges = [True, False, True])
	
	# n-gons with doubled sides.
	for i in range(3, 6 + 1):
		regular_fillygon(i, 'double', side_repetitions = 2)
	
	# n-gons with custom angles.
	for i in os.listdir('src/custom_angles'):
		if i.startswith('_') and i.endswith('.scad'):
			non_regular_fillygon(i[1:-5])
	
	for i in sorted(files) if path is None else files[path]():
		print(i)


main(*sys.argv[1:])
