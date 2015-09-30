"""
Based on code from Aaron Spike. See http://www.bobcookdev.com/inkscape/inkscape-dxf.html
"""

import pkgutil, os, re, collections, itertools
from . import inkex, simpletransform, cubicsuperpath, cspsubdiv, inkscape


def _get_unit_factors_map():
	# Fluctuates somewhat between Inkscape releases _and_ between SVG version.
	pixels_per_inch = 96.
	pixels_per_mm = pixels_per_inch / 25.4
	
	return {
		'px': 1.0,
		'mm': pixels_per_mm,
		'cm': pixels_per_mm * 10,
      'm' : pixels_per_mm * 1e3,
      'km': pixels_per_mm * 1e6,
		'pt': pixels_per_inch / 72,
      'pc': pixels_per_inch / 6,
		'in': pixels_per_inch,
      'ft': pixels_per_inch * 12,
      'yd': pixels_per_inch * 36 }


class ExportEffect(inkex.Effect):
	_unit_factors = _get_unit_factors_map()
	_asymptote_all_paths_name = 'all'
	
	def __init__(self):
		inkex.Effect.__init__(self)
		
		self._flatness = float(os.environ['DXF_FLATNESS'])
		
		self._layers = None
		self._paths = None
	
	def _get_document_scale(self):
		"""
		Return scaling factor applied to the document because of a viewBox setting. This currently ignores any setting of a preserveAspectRatio attribute (like Inkscape).
		"""
		
		document_height = self._get_height()
		view_box = self._get_view_box()
		
		if view_box is None or document_height is None:
			return 1
		else:
			_, _, _, view_box_height = view_box
			
			return document_height / view_box_height
	
	def _get_document_height(self):
		"""
		Get the height of the document in pixels in the document coordinate system as it is interpreted by Inkscape.
		"""
		
		view_box = self._get_view_box()
		document_height = self._get_height()
		
		if view_box is not None:
			_, _, _, view_box_height = view_box
			
			return view_box_height
		elif document_height is not None:
			return document_height
		else:
			return 0
	
	def _get_height(self):
		height_attr = self.document.getroot().get('height')
		
		if height_attr is None:
			return None
		else:
			return self._measure_to_pixels(height_attr)
	
	def _get_view_box(self):
		view_box_attr = self.document.getroot().get('viewBox')
		
		if view_box_attr is None:
			return None
		else:
			return [float(i) for i in view_box_attr.split()]
	
	def _get_shape_paths(self, node, transform):
		shape = cubicsuperpath.parsePath(node.get('d'))
		
		transform = simpletransform.composeTransform(
			transform,
			simpletransform.composeParents(node, [[1, 0, 0], [0, 1, 0]]))
		
		simpletransform.applyTransformToPath(transform, shape)
		
		def iter_paths():
			for path in shape:
				cspsubdiv.subdiv(path, self._flatness)
				
				# path contains two control point coordinates and the actual coordinates per point.
				yield [i for _, i, _ in path]
		
		return list(iter_paths())
	
	def effect(self):
		document_height = self._get_document_height()
		document_scale = self._get_document_scale()
		
		transform = simpletransform.composeTransform(
			[[document_scale, 0, 0], [0, document_scale, 0]],
			[[1, 0, 0], [0, -1, document_height]])
		
		layers = inkscape.get_inkscape_layers(self.svg_file)
		layers_by_inkscape_name = { i.inkscape_name: i for i in layers }
		
		def iter_paths():
			for node in self.document.getroot().xpath('//svg:path', namespaces = inkex.NSS):
				layer = layers_by_inkscape_name.get(self._get_inkscape_layer_name(node))
				
				for path in self._get_shape_paths(node, transform):
					yield layer, path
		
		self._layers = layers
		self._paths = list(iter_paths())
	
	def write_dxf(self, file):
		# Scales pixels to millimeters. This is the predominant unit in CAD.
		unit_factor = self._unit_factors['mm']
		
		layer_indices = { l: i for i, l in enumerate(self._layers) }
		
		file.write(pkgutil.get_data(__name__, 'dxf_header.txt'))
		
		def write_instruction(code, value):
			print >> file, code
			print >> file, value
		
		handle_iter = itertools.count(256)
		
		for layer, path in self._paths:
			for (x1, y1), (x2, y2) in zip(path, path[1:]):
				write_instruction(0, 'LINE')
				
				if layer is not None:
					write_instruction(8, layer.export_name)
					write_instruction(62, layer_indices.get(layer, 0))
				
				write_instruction(5, '{:x}'.format(next(handle_iter)))
				write_instruction(100, 'AcDbEntity')
				write_instruction(100, 'AcDbLine')
				write_instruction(10, repr(x1 / unit_factor))
				write_instruction(20, repr(y1 / unit_factor))
				write_instruction(30, 0.0)
				write_instruction(11, repr(x2 / unit_factor))
				write_instruction(21, repr(y2 / unit_factor))
				write_instruction(31, 0.0)
		
		file.write(pkgutil.get_data(__name__, 'dxf_footer.txt'))
	
	def write_asy(self, file):
		def write_line(format, *args):
			print >> file, format.format(*args) + ';'
		
		# Scales pixels to points. Asymptote uses points by default.
		unit_factor = self._unit_factors['pt']
		
		paths_by_layer = collections.defaultdict(list)
		variable_names = []
		
		for layer, path in self._paths:
			paths_by_layer[layer].append(path)
		
		for layer in self._layers + [None]:
			paths = paths_by_layer[layer]
			variable_name = self._asymptote_identifier_from_layer(layer)
			write_line('path[] {}', variable_name)
			
			variable_names.append(variable_name)
			
			for path in paths:
				point_strs = ['({}, {})'.format(x / unit_factor, y / unit_factor) for x, y in path]
				
				# Hack. We should determine this from whether Z or z was used to close the path in the SVG document.
				if path[0] == path[-1]:
					point_strs[-1] = 'cycle'
				
				write_line('{}.push({})', variable_name, ' -- '.join(point_strs))
		
		if self._asymptote_all_paths_name not in variable_names:
			write_line('path[] {}', self._asymptote_all_paths_name)
			
			for i in variable_names:
				write_line('{}.append({})', self._asymptote_all_paths_name, i)
	
	@classmethod
	def _parse_measure(cls, string):
		value_match = re.match(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)', string)
		unit_match = re.search('(%s)$' % '|'.join(cls._unit_factors.keys()), string)	
		
		value = float(string[value_match.start():value_match.end()])
		
		if unit_match:
			unit = string[unit_match.start():unit_match.end()]
		else:
			unit = None
		
		return value, unit
	
	@classmethod
	def _measure_to_pixels(cls, string):
		"""
		Parse a string containing a measure and return it's value converted to pixels.
		"""
		
		value, unit = cls._parse_measure(string)
		
		return value * cls._get_unit_factor(unit)
	
	@classmethod
	def _get_inkscape_layer_name(cls, node):
		while node is not None:
			layer = node.get(inkex.addNS('label', 'inkscape'))
			
			if layer is not None:
				return layer
			
			node = node.getparent()
		
		return None
	
	@classmethod
	def _get_unit_factor(cls, unit):
		if unit is None:
			return 1
		else:
			return cls._unit_factors[unit]
	
	@classmethod
	def _asymptote_identifier_from_layer(cls, layer):
		if layer is None:
			return '_'
		else:
			return re.sub('[^a-zA-Z0-9]', '_', layer.export_name)
