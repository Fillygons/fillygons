"""
Based on code from Aaron Spike. See http://www.bobcookdev.com/inkscape/inkscape-dxf.html
"""

import pkgutil, os, re
from . import inkex, simpletransform, cubicsuperpath, cspsubdiv


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


class DXFExportEffect(inkex.Effect):
	_unit_factors = _get_unit_factors_map()
	
	def __init__(self):
		inkex.Effect.__init__(self)
		
		self._dxf_instructions = []
		self._handle = 255
		self._flatness = float(os.environ['DXF_FLATNESS'])
	
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
	
	def _add_instruction(self, code, value):
		self._dxf_instructions.append((code, str(value)))
	
	def _add_dxf_line(self, layer, csp):
		self._add_instruction(0, 'LINE')
		self._add_instruction(8, layer)
		self._add_instruction(62, 4)
		self._add_instruction(5, '{:x}'.format(self._handle))
		self._add_instruction(100, 'AcDbEntity')
		self._add_instruction(100, 'AcDbLine')
		self._add_instruction(10, repr(csp[0][0]))
		self._add_instruction(20, repr(csp[0][1]))
		self._add_instruction(30, 0.0)
		self._add_instruction(11, repr(csp[1][0]))
		self._add_instruction(21, repr(csp[1][1]))
		self._add_instruction(31, 0.0)
	
	def _add_dxf_path(self, layer, path):
		cspsubdiv.cspsubdiv(path, self._flatness)
		
		for sub in path:
			for i in range(len(sub) - 1):
				self._handle += 1
				s = sub[i]
				e = sub[i + 1]
				self._add_dxf_line(layer, [s[1], e[1]])
	
	def _add_dxf_shape(self, node, document_transform, element_transform):
		layer = self._get_inkscape_layer(node)
		path = cubicsuperpath.parsePath(node.get('d'))
		
		transform = simpletransform.composeTransform(
			document_transform,
			simpletransform.composeParents(node, element_transform))
		
		simpletransform.applyTransformToPath(transform, path)
		
		self._add_dxf_path(layer, path)
	
	def effect(self):
		user_unit = self._get_user_unit()
		document_unit = self._get_document_unit()
		height = self._measure_to_pixels(self._get_document_height_attr())
		
		document_transform = simpletransform.composeTransform(
			[[1 / document_unit, 0, 0], [0, 1 / document_unit, 0]],
			[[1, 0, 0], [0, -1, height]])
		
		element_transform = [[user_unit, 0, 0], [0, user_unit, 0]]
		
		for node in self.document.getroot().xpath('//svg:path', namespaces = inkex.NSS):
			self._add_dxf_shape(node, document_transform, element_transform)
	
	def write(self, file):
		file.write(pkgutil.get_data(__name__, 'dxf_header.txt'))
		
		for code, value in self._dxf_instructions:
			print >> file, code
			print >> file, value
		
		file.write(pkgutil.get_data(__name__, 'dxf_footer.txt'))
	
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
	def _get_inkscape_layer(cls, node):
		while node is not None:
			layer = node.get(inkex.addNS('label', 'inkscape'))
			
			if layer is not None:
				return layer
			
			node = node.getparent()
		
		return ''
	
	@classmethod
	def _get_unit_factor(cls, unit, default = None):
		if unit is None:
			if default is None:
				default = 1
			
			return default
		else:
			return cls._unit_factors[unit]
