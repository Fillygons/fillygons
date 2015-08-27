import os
import xml.etree.ElementTree as etree
from lib import util


def get_inkscape_layers(svg_path):
	document = etree.parse(svg_path)
	
	def iter_layers():
		nodes = document.findall(
			'{http://www.w3.org/2000/svg}g[@{http://www.inkscape.org/namespaces/inkscape}groupmode="layer"]')
		
		for i in nodes:
			inkscape_name = i.get('{http://www.inkscape.org/namespaces/inkscape}label').strip()
			
			if inkscape_name.endswith(']'):
				export_name, args = inkscape_name[:-1].rsplit('[', 1)
				
				export_name = export_name.strip()
				args = args.strip()
				
				use_paths = 'p' in args
			else:
				use_paths = False
				export_name = inkscape_name
			
			yield Layer(inkscape_name, export_name, use_paths)
	
	return list(iter_layers())


def _inkscape(svg_path, verbs):
	def iter_args():
		yield os.environ['INKSCAPE']
		
		for i in verbs:
			yield '--verb'
			yield i
		
		yield svg_path
	
	util.command(list(iter_args()))


class Layer(object):
	def __init__(self, inkscape_name, export_name, use_paths):
		self.inkscape_name = inkscape_name
		self.export_name = export_name
		self.use_paths = use_paths


class InkscapeCommandLine(object):
	def __init__(self, path):
		self._path = path
		self._layers = get_inkscape_layers(path)
		self._current_layer_index = None
		self._verbs = []
	
	def apply_to_document(self, *verb):
		self._verbs.extend(verb)
	
	def apply_to_layer(self, layer, *verb):
		self._go_to_layer(layer)
		self.apply_to_document(*verb)
	
	def select_all_in_layer(self, layer):
		self.apply_to_layer(layer, 'EditSelectAll')
	
	def apply_to_layer_content(self, layer, *verbs):
		self.select_all_in_layer(layer)
		self.apply_to_document(*verbs)
	
	def _go_to_layer(self, layer, with_selection = False):
		if self._current_layer_index is None:
			# Initialize to a known state. We cannot assume that any layer is selected and thus we need as many LayerPrev as we have layers.
			self._current_layer_index = len(self._layers)
			self._go_to_layer(self._layers[0])
		
		target_index = self._layers.index(layer)
		
		while True:
			if self._current_layer_index < target_index:
				self.apply_to_document('LayerMoveToNext' if with_selection else 'LayerNext')
				self._current_layer_index += 1
			elif self._current_layer_index > target_index:
				self.apply_to_document('LayerMoveToPrev' if with_selection else 'LayerPrev')
				self._current_layer_index -= 1
			else:
				break
	
	def duplicate_layer(self, layer):
		self.apply_to_layer(layer, 'LayerDuplicate')
		
		# Inkscape 0.91 places a duplicated layer above (after) the selected one and selects the new layer.
		new_layer = Layer(layer.inkscape_name + ' copy', layer.export_name, layer.use_paths)
		self._current_layer_index += 1
		self._layers.insert(self._current_layer_index, new_layer)
		
		return new_layer
	
	def delete_layer(self, layer):
		self.apply_to_layer(layer, 'LayerDelete')
		
		# Inkscape 0.91 selects the layer above (after) the deleted layer.
		del self._layers[self._current_layer_index]
	
	def clear_layer(self, layer):
		self.select_all_in_layer(layer)
		self.apply_to_document('EditDelete')
	
	def move_content(self, source_layer, target_layer):
		self.select_all_in_layer(source_layer)
		self._go_to_layer(target_layer, True)
	
	def run(self):
		_inkscape(self._path, self._verbs)
	
	@property
	def layers(self):
		return list(self._layers)
