import os, sys
from lib import util


def _openscad(in_path, out_path, deps_path):
	util.command([os.environ['OPENSCAD'], '-o', out_path, '-d', deps_path, in_path])


def _write_dependencies(path, target, dependencies):
	util.write_file(path, '{}: {}\n'.format(target, ' '.join(dependencies)).encode())


def main(in_path, out_path, deps_path):
	cwd = os.getcwd()
	
	def relpath(path):
		return os.path.relpath(path, cwd)
	
	with util.TemporaryDirectory() as temp_dir:
		temp_deps_path = os.path.join(temp_dir, 'deps')
		temp_mk_path = os.path.join(temp_dir, 'mk')
		temp_files_path = os.path.join(temp_dir, 'files')
		
		_openscad(in_path, out_path, temp_deps_path)
		
		mk_content = '%:; echo "$@" >> {}'.format(util.bash_escape_string(temp_files_path))
		
		util.write_file(temp_mk_path, mk_content.encode())
		util.command(['make', '-s', '-B', '-f', temp_mk_path, '-f', temp_deps_path])
		
		deps = set(map(relpath, util.read_file(temp_files_path).decode().splitlines()))
		ignored_files = set(map(relpath, [temp_deps_path, temp_mk_path, in_path, out_path]))
		
		_write_dependencies(deps_path, relpath(out_path), deps - ignored_files)


try:
	main(*sys.argv[1:])
except util.UserError as e:
	print 'Error:', e
	sys.exit(1)
except KeyboardInterrupt:
	sys.exit(2)
