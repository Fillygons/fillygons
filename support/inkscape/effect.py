"""
Based on code from Aaron Spike. See http://www.bobcookdev.com/inkscape/inkscape-dxf.html
"""

import pkgutil, os, re, collections
from . import inkex, simpletransform, cubicsuperpath, cspsubdiv, inkscape


def _get_unit_factors_map():
	# Fluctuates somewhat between Inkscape releases.
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
	_asymptote_all_paths_name = 'paths'
	
	def __init__(self):
		inkex.Effect.__init__(self)
		
		self._flatness = float(os.environ['DXF_FLATNESS'])
		self._layers = None
		self._layers_by_inkscape_name = None
		
		self._paths = [] # Contains (layer : Layer | None, points : List[(float, float)])
	
	def _get_user_unit(self):
		"""
		Return the size in pixels of the unit used for measures without an explicit unit.
		"""
		
		document_height = self._measure_to_pixels(self._get_document_height_attr())
		view_box_attr = self.document.getroot().get('viewBox')
		
		if view_box_attr:
			_, _, _, view_box_height = map(float, view_box_attr.split())
		else:
			view_box_height = document_height
		
		return document_height / view_box_height
	
	def _get_document_unit(self):
		"""
		Return the size in pixels that the user is working with in Inkscape.
		"""
		
		inkscape_unit_attrs = self.document.getroot().xpath('./sodipodi:namedview/@inkscape:document-units', namespaces = inkex.NSS)
		
		if inkscape_unit_attrs:
			unit = inkscape_unit_attrs[0]
		else:
			_, unit = self._parse_measure(self._get_document_height_attr())
		
		return self._get_unit_factor(unit)
	
	def _get_document_height_attr(self):
		return self.document.getroot().xpath('@height', namespaces = inkex.NSS)[0]
	
	def _add_path(self, layer, path):
		"""
		Warning: Fucks up path.
		"""
		
		cspsubdiv.subdiv(path, self._flatness)
		
		# path contains two control point coordinates and the actual coordinates per point.
		self._paths.append((layer, [i for _, i, _ in path]))
	
	def _add_shape(self, node, document_transform, element_transform):
		shape = cubicsuperpath.parsePath(node.get('d'))
		layer = self._layers_by_inkscape_name.get(self._get_inkscape_layer_name(node))
		
		transform = simpletransform.composeTransform(
			document_transform,
			simpletransform.composeParents(node, element_transform))
		
		simpletransform.applyTransformToPath(transform, shape)
		
		for path in shape:
			self._add_path(layer, path)
	
	def effect(self):
		self._layers = inkscape.get_inkscape_layers(self.svg_file)
		self._layers_by_inkscape_name = { i.inkscape_name: i for i in self._layers }
		
		user_unit = self._get_user_unit()
		document_height = self._measure_to_pixels(self._get_document_height_attr())
		
		document_transform = [[1, 0, 0], [0, -1, document_height]]
		element_transform = [[user_unit, 0, 0], [0, user_unit, 0]]
		
		for node in self.document.getroot().xpath('//svg:path', namespaces = inkex.NSS):
			self._add_shape(node, document_transform, element_transform)
	
	def write_dxf(self, file):
		document_unit = self._get_document_unit()
		layer_indices = { l: i for i, l in enumerate(self._layers) }
		
		file.write(pkgutil.get_data(__name__, 'dxf_header.txt'))
		
		def write_instruction(code, value):
			print >> file, code
			print >> file, value
		
		handle = 256
		
		for layer, path in self._paths:
			for (x1, y1), (x2, y2) in zip(path, path[1:]):
				write_instruction(0, 'LINE')
				write_instruction(8, layer.export_name)
				write_instruction(62, layer_indices.get(layer, 0))
				write_instruction(5, '{:x}'.format(handle))
				write_instruction(100, 'AcDbEntity')
				write_instruction(100, 'AcDbLine')
				write_instruction(10, repr(x1 / document_unit))
				write_instruction(20, repr(y1 / document_unit))
				write_instruction(30, 0.0)
				write_instruction(11, repr(x2 / document_unit))
				write_instruction(21, repr(y2 / document_unit))
				write_instruction(31, 0.0)
				
				handle += 1
		
		file.write(pkgutil.get_data(__name__, 'dxf_footer.txt'))
	
	def write_asy(self, file):
		def write_line(format, *args):
			print >> file, format.format(*args) + ';'
		
		# Scales pixels to points.
		unit_factor = self._unit_factors['pt']
		lines_by_layer_name = collections.defaultdict(list)
		
		for layer, path in self._paths:
			lines_by_layer_name[self._asymptote_identifier_from_layer(layer)].append(path)
		
		for layer_name, paths in sorted(lines_by_layer_name.items()):
			write_line('path[] {}', layer_name)
			
			for path in paths:
				point_strs = ['({}, {})'.format(x / unit_factor, y / unit_factor) for x, y in path]
				
				# Hack. We should determine from whether Z or z was used to close the path in the SVG document.
				if path[0] == path[-1]:
					point_strs[-1] = 'cycle'
				
				write_line('{}.push({})', layer_name, ' -- '.join(point_strs))
		
		if self._asymptote_all_paths_name not in lines_by_layer_name:
			write_line('path[] {}', self._asymptote_all_paths_name)
			
			for layer_name in sorted(lines_by_layer_name):
				write_line('{}.append({})', self._asymptote_all_paths_name, layer_name)
	
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
	def _measure_to_pixels(cls, string, default_unit_factor = None):
		"""
		Parse a string containing a measure and return it's value converted to pixels. If the measure has no unit, it will be assumed that the unit has the size of the specified number of pixels.
		"""
		
		value, unit = cls._parse_measure(string)
		
		return value * cls._get_unit_factor(unit, default_unit_factor)
	
	@classmethod
	def _get_inkscape_layer_name(cls, node):
		while node is not None:
			layer = node.get(inkex.addNS('label', 'inkscape'))
			
			if layer is not None:
				return layer
			
			node = node.getparent()
		
		return None
	
	@classmethod
	def _get_unit_factor(cls, unit, default = None):
		if unit is None:
			if default is None:
				default = 1
			
			return default
		else:
			return cls._unit_factors[unit]
	
	@classmethod
	def _asymptote_identifier_from_layer(cls, layer):
		if layer is None:
			return '_'
		else:
			return re.sub('[^a-zA-Z0-9]', '_', layer.export_name)
