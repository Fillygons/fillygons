import os, sys
from lib import util


def _asymptote(in_path, out_path, asymptote_dir):
	util.command([os.environ['ASYMPTOTE'], '-f', 'pdf', '-o', out_path, in_path], set_env = { 'ASYMPTOTE_DIR': asymptote_dir })


def main(in_path, out_path):
	_, out_suffix = os.path.splitext(out_path)
	
	if out_suffix == '.pdf':
		_asymptote(in_path, out_path, os.path.dirname(in_path))
	else:
		raise Exception('Unknown file type: {}'.format(out_suffix))


try:
	main(*sys.argv[1:])
except util.UserError as e:
	print 'Error:', e
	sys.exit(1)
except KeyboardInterrupt:
	sys.exit(2)
