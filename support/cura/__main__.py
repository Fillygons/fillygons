import sys, os
from lib import util


def _cura(in_path, out_path, profile_path):
	util.command([os.environ['CURA'], '--slice', '--ini', profile_path, '--output', out_path, in_path])


@util.main
def main(in_path, out_path, profile_path):
	try:
		absolute_in_path = os.path.abspath(in_path)
		absolute_out_path = os.path.abspath(out_path)
		absolute_profile_path = os.path.abspath(profile_path)
		
		_cura(absolute_in_path, absolute_out_path, absolute_profile_path)
		
		print >> sys.stderr, 'GCode generation was successful!'
	except util.UserError as e:
		raise util.UserError('While processing {}: {}', in_path, e)
