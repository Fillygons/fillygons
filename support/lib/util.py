import contextlib, subprocess, tempfile, shutil, re, os


class UserError(Exception):
	def __init__(self, message, *args):
		super(UserError, self).__init__(message.format(*args))


def rename_atomic(source_path, target_path):
	"""
	Move the file at source_path to target_path.
	
	If both paths reside on the same device, os.rename() is used, otherwise the file is copied to a temporary name next to target_path and moved from there using os.rename().
	"""
	
	source_dir_stat = os.stat(os.path.dirname(source_path))
	target_dir_stat = os.stat(os.path.dirname(target_path))
	
	if source_dir_stat.st_dev == target_dir_stat.st_dev:
		os.rename(source_path, target_path)
	else:
		temp_path = target_path + '~'
		
		shutil.copyfile(source_path, temp_path)
		os.rename(temp_path, target_path)


@contextlib.contextmanager
def TemporaryDirectory():
	dir = tempfile.mkdtemp()
	
	try:
		yield dir
	finally:
		shutil.rmtree(dir)


def command(args, remove_env = [], set_env = { }):
	env = dict(os.environ)
	
	for i in remove_env:
		del env[i]
	
	for k, v in set_env.items():
		env[k] = v
	
	try:
		process = subprocess.Popen(args, env = env)
		process.wait()
	except OSError as e:
		raise UserError('Error running {}: {}', args[0], e)
	
	if process.returncode:
		raise UserError('Command failed: {}', ' '.join(args))


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
