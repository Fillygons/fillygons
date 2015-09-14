from . import util


def write_dependencies(path, target, dependencies):
	util.write_file(path, '{}: {}\n'.format(target, ' '.join(dependencies)).encode())
