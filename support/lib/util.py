import contextlib, subprocess, tempfile, shutil, re, os


class UserError(Exception):
	pass


def _temp_dir_is_on_same_mount_point():
	tempdir_stat = os.stat(tempfile.gettempdir())
	working_dir_stat = os.stat('.')
	
	return tempdir_stat.st_dev == working_dir_stat.st_dev


@contextlib.contextmanager
def TemporaryDirectory():
	if _temp_dir_is_on_same_mount_point():
		dir = None
	else:
		dir = '.'
	
	dir = tempfile.mkdtemp(dir = dir, prefix = '.tmp_')
	
	try:
		yield dir
	finally:
		shutil.rmtree(dir)


def command(args, remove_env = None):
	if remove_env is None:
		env = None
	else:
		env = dict(os.environ)
		
		for i in remove_env:
			if i in env:
				del env[i]
	
	process = subprocess.Popen(args, env = env)
	process.wait()
	
	if process.returncode:
		raise UserError('Command failed: {}'.format(' '.join(args)))


def bash_escape_string(string):
	return "'{}'".format(re.sub("'", "'\"'\"'", string))	


def write_file(path, data):
	temp_path = path + '~'
	
	with open(temp_path, 'wb') as file:
		file.write(data)
	
	os.rename(temp_path, path)


def read_file(path):
	with open(path, 'rb') as file:
		return file.read()
