import os
from lib import util


def _cura(in_path, out_path, profile_path):
	absolute_in_path = os.path.abspath(in_path)
	absolute_profile_path = os.path.abspath(profile_path)
	
	with util.TemporaryDirectory() as temp_dir:
		temp_path = os.path.abspath(os.path.join(temp_dir, 'out.gcode'))
		
		# We capture stdout and stderr and throw it away to get rid of pesky stack traces printed by Cura event when slicing is successful.
		util.command([os.environ['CURA'], '--slice', '--ini', absolute_profile_path, '--output', temp_path, absolute_in_path], use_stdout =  True, use_stderr = True)
		
		with open(temp_path, 'r') as in_file, open(out_path, 'w') as out_file:
			for i in in_file:
				if i.startswith(';TIME:'):
					i = ';TIME:1\n'
				elif i.startswith(';MATERIAL:'):
					i = ';MATERIAL:1\n'
				elif i.startswith(';MATERIAL2:'):
					i = ';MATERIAL2:0\n'
				
				print >> out_file, i,


@util.main
def main(in_path, out_path, profile_path):
	try:
		_cura(in_path, out_path, profile_path)
	except util.UserError as e:
		raise util.UserError('While processing {}: {}', in_path, e)
