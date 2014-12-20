"""
Based on code from Aaron Spike. See http://www.bobcookdev.com/inkscape/inkscape-dxf.html
"""

import pkgutil
from . import inkex, simpletransform, cubicsuperpath, cspsubdiv


class DXFExportEffect(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self._dxf_instructions = []
		self._handle = 255
		self._flatness = 0.1
	
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
	
	def _add_dxf_shape(self, node, document_transformation):
		layer = self._get_inkscape_layer(node)
		path = cubicsuperpath.parsePath(node.get('d'))
		
		transformation = simpletransform.composeTransform(
			document_transformation,
			simpletransform.composeParents(node, [[1, 0, 0], [0, 1, 0]]))
		
		simpletransform.applyTransformToPath(transformation, path)
		
		self._add_dxf_path(layer, path)
	
	def effect(self):
		height = self.unittouu(self.document.getroot().xpath('@height', namespaces = inkex.NSS)[0])
		document_transformation = [[1, 0, 0], [0, -1, height]]
		
		for node in self.document.getroot().xpath('//svg:path', namespaces = inkex.NSS):
			self._add_dxf_shape(node, document_transformation)
	
	def write(self, file):
		file.write(pkgutil.get_data(__name__, 'dxf_header.txt'))
		
		for code, value in self._dxf_instructions:
			print >> file, code
			print >> file, value
		
		file.write(pkgutil.get_data(__name__, 'dxf_footer.txt'))
	
	@classmethod
	def _get_inkscape_layer(cls, node):
		while node is not None:
			layer = node.get(inkex.addNS('label', 'inkscape'))
			
			if layer is not None:
				return layer
			
			node = node.getparent()
		
		return ''
