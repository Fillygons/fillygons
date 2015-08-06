import sys, os, shutil
from lib import util
from . import effect, inkscape


def _unfuck_svg_document(temp_svg_path):
	"""
	Unfucks an SVG document so is can be processed by the better_dxf_export plugin (or what's left of it).
	"""
	
	command_line = inkscape.InkscapeCommandLine(temp_svg_path)
	layers = command_line.layers
	
	command_line.apply_to_document('LayerUnlockAll', 'LayerShowAll')
	
	layer_copies = []
	
	for i in layers:
		layer_copy = command_line.duplicate_layer(i)
		layer_copies.append(layer_copy)
		
		command_line.apply_to_layer_content(layer_copy, 'ObjectToPath')
		command_line.apply_to_layer_content(layer_copy, 'SelectionUnGroup')
		
		if not i.use_paths:
			command_line.apply_to_layer_content(layer_copy, 'StrokeToPath')
			command_line.apply_to_layer_content(layer_copy, 'SelectionUnion')
	
	for original, copy in zip(layers, layer_copies):
		command_line.clear_layer(original)
		command_line.move_content(copy, original)
		command_line.delete_layer(copy)
	
	command_line.apply_to_document('FileSave', 'FileClose', 'FileQuit')
	
	command_line.run()


def main(in_path, out_path):
	_, out_suffix = os.path.splitext(out_path)
	
	with util.TemporaryDirectory() as temp_dir:
		temp_svg_path = os.path.join(temp_dir, 'temp.svg')
		
		shutil.copyfile(in_path, temp_svg_path)
		
		_unfuck_svg_document(temp_svg_path)
		
		_export_dxf(temp_svg_path, out_path, layers)


try:
	main(*sys.argv[1:])
except util.UserError as e:
	print 'Error:', e
	sys.exit(1)
except KeyboardInterrupt:
	sys.exit(2)
