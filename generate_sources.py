import sys, os, functools, glob


def main(path = None):
	files = { }
	
	def generate_file(path, function, *args):
		files[path] = lambda: function(*args)
	
	def code(included_file, function_call):
		yield 'use <_fillygon.scad>'
		
		if included_file is not None:
			yield 'include <{}>'.format(included_file)
		
		yield 'render() {};'.format(function_call)
	
	def fillygon(file_name, included_file, called_function, arguments):
		for i in '0.24', '0.4':
			generate_file('src/{}-{}mm.scad'.format(file_name, i), code, included_file, '{}({}, gap = {})'.format(called_function, arguments, i))
			generate_file('src/{}-filled-{}mm.scad'.format(file_name, i), code, included_file, '{}({}, filled = true, gap = {})'.format(called_function, arguments, i)) 
	
	def regular_fillygon(file_name, sides, side_repetitions = 1, reversed_sides = ''):
		fillygon(file_name, None, 'regular_fillygon', '{}, side_repetitions = {}, reversed_sides = [{}]'.format(sides, side_repetitions, reversed_sides))
	
	def non_regular_fillygon(file_name, included_file, reversed_sides = ''):
		fillygon(file_name, included_file, 'fillygon', 'angles, reversed_sides = [{}]'.format(reversed_sides))
	
	# Regular n-gons.
	for i in range(3, 12):
		regular_fillygon('{}-gon'.format(i), i, 1)
	
	# n-gons with reversed sides.
	regular_fillygon('3-gon-reversed', 3, 1, 'true')
	regular_fillygon('4-gon-reversed-1', 4, 1, 'true')
	regular_fillygon('4-gon-reversed-2', 4, 1, 'true, true')
	regular_fillygon('4-gon-reversed-3', 4, 1, 'true, false, true')
	
	# n-gons with doubled sides.
	for i in range(3, 7):
		regular_fillygon('{}-gon-double'.format(i), i, 2)
	
	# n-gons with custom angles.
	for i in os.listdir('src/custom_angles'):
		if i.startswith('_') and i.endswith('.scad'):
			name = i[1:-5]
			
			non_regular_fillygon(name, 'custom_angles/_{}'.format(i))
	
	for i in files if path is None else files[path]():
		print(i)


main(*sys.argv[1:])
