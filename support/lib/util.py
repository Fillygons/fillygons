import contextlib, subprocess, tempfile, shutil, re, os


class UserError(Exception):
	pass


@contextlib.contextmanager
def TemporaryDirectory():
	dir = tempfile.mkdtemp()
	
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
