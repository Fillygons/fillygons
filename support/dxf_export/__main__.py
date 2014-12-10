import sys, os, xml.etree.ElementTree, shutil
from lib import util
from . import better_dxf_outlines


def _export_dxf(in_path, out_path):
	dxf_export = better_dxf_outlines.MyEffect()
	dxf_export.affect(args = [in_path], output = False)
	
	with open(out_path, 'w') as file:
		file.write(dxf_export.dxf)


def _get_inkscape_layer_count(svg_path):
	document = xml.etree.ElementTree.parse(svg_path)
	layers = document.findall(
		'{http://www.w3.org/2000/svg}g[@{http://www.inkscape.org/namespaces/inkscape}groupmode="layer"]')
	
	return len(layers)


def _inkscape(svg_path, verbs):
	def iter_args():
		yield os.environ['INKSCAPE']
		
		for i in verbs:
			yield '--verb'
			yield i
		
		yield svg_path
	
	util.command(list(iter_args()))


def _unfuck_svg_document(temp_svg_path):
	"""
	Unfucks an SVG document so is can be processed by the better_dxf_export plugin.
	"""
	
	layers_count = _get_inkscape_layer_count(temp_svg_path)

	def iter_inkscape_verbs():
		yield 'LayerUnlockAll'
		yield 'LayerShowAll'

		# Go to the first layer
		for _ in range(layers_count):
			yield 'LayerPrev'

		for _ in range(layers_count):
			yield 'EditSelectAll'
			yield 'ObjectToPath'
			yield 'EditSelectAll'
			yield 'SelectionUnGroup'
			yield 'EditSelectAll'
			yield 'StrokeToPath'
			yield 'EditSelectAll'
			yield 'SelectionUnion'
			yield 'LayerNext'

		yield 'FileSave'
		yield 'FileClose'
		yield 'FileQuit'

	_inkscape(temp_svg_path, list(iter_inkscape_verbs()))


def main(in_path, out_path):
	with util.TemporaryDirectory() as temp_dir:
		temp_svg_path = os.path.join(temp_dir, 'temp.svg')
		
		shutil.copyfile(in_path, temp_svg_path)

		_unfuck_svg_document(temp_svg_path)
		
		_export_dxf(temp_svg_path, out_path)


main(*sys.argv[1:])
