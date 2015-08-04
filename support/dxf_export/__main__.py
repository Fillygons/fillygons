import sys, os, xml.etree.ElementTree, shutil
from lib import util
from . import effect


def _export_dxf(in_path, out_path, layers):
	dxf_export = effect.DXFExportEffect(layers)
	dxf_export.affect(args = [in_path], output = False)
	
	with open(out_path, 'w') as file:
		dxf_export.write(file)


def _get_inkscape_layers(svg_path):
	document = xml.etree.ElementTree.parse(svg_path)
	
	def iter_layers():
		nodes = document.findall(
			'{http://www.w3.org/2000/svg}g[@{http://www.inkscape.org/namespaces/inkscape}groupmode="layer"]')
		
		for i in nodes:
			inkscape_name = i.get('{http://www.inkscape.org/namespaces/inkscape}label').strip()
			
			if inkscape_name.endswith(']'):
				dxf_name, args = inkscape_name[:-1].rsplit('[', 1)
				
				dxf_name = dxf_name.strip()
				args = args.strip()
				
				use_paths = 'p' in args
			else:
				use_paths = False
				dxf_name = inkscape_name
			
			yield effect.Layer(inkscape_name, dxf_name, use_paths = use_paths)
	
	return list(iter_layers())


def _inkscape(svg_path, verbs):
	def iter_args():
		yield os.environ['INKSCAPE']
		
		for i in verbs:
			yield '--verb'
			yield i
		
		yield svg_path
	
	util.command(list(iter_args()))


def _unfuck_svg_document(temp_svg_path, layers):
	"""
	Unfucks an SVG document so is can be processed by the better_dxf_export plugin (or what's left of it).
	"""
	
	def iter_inkscape_verbs():
		yield 'LayerUnlockAll'
		yield 'LayerShowAll'

		# Go to the first layer.
		for _ in layers:
			yield 'LayerPrev'
		
		# Copy each layer and flatten it to a single path object.
		for i in layers:
			yield 'LayerDuplicate'
			yield 'EditSelectAll'
			yield 'ObjectToPath'
			yield 'EditSelectAll'
			yield 'SelectionUnGroup'
			
			if not i.use_paths:
				yield 'EditSelectAll'
				yield 'StrokeToPath'
				yield 'EditSelectAll'
				yield 'SelectionUnion'
			
			yield 'LayerNext'
		
		# Go to the first layer again.
		for _ in range(2 * len(layers)):
			yield 'LayerPrev'
		
		# Move the flattened shapes to the original layers.
		for _ in layers:
			yield 'EditSelectAll'
			yield 'EditDelete'
			yield 'LayerNext'
			
			yield 'EditSelectAll'
			yield 'LayerMoveToPrev'
			yield 'LayerNext'
			yield 'LayerDelete'
		
		yield 'FileSave'
		yield 'FileClose'
		yield 'FileQuit'
	
	_inkscape(temp_svg_path, list(iter_inkscape_verbs()))


def main(in_path, out_path):
	with util.TemporaryDirectory() as temp_dir:
		temp_svg_path = os.path.join(temp_dir, 'temp.svg')
		
		shutil.copyfile(in_path, temp_svg_path)
		
		layers = _get_inkscape_layers(temp_svg_path)
		_unfuck_svg_document(temp_svg_path, layers)
		
		_export_dxf(temp_svg_path, out_path, layers)


try:
	main(*sys.argv[1:])
except util.UserError as e:
	print 'Error:', e
	sys.exit(1)
except KeyboardInterrupt:
	sys.exit(2)
