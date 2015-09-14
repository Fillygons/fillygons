import sys, contextlib, subprocess, tempfile, shutil, re, os, inspect


class UserError(Exception):
	def __init__(self, message, *args):
		super(UserError, self).__init__(message.format(*args))


def main(fn):
	"""Decorator for "main" functions. Decorates a function that should be called when the containing module is run as a script (e.g. via python -m <module>)."""
	
	frame = inspect.currentframe().f_back
	
	def wrapped_fn(*args, **kwargs):
		try:
			fn(*args, **kwargs)
		except UserError as e:
			print >> sys.stderr, 'Error:', e
			sys.exit(1)
		except KeyboardInterrupt:
			sys.exit(2)
	
	if frame.f_globals['__name__'] == '__main__':
		wrapped_fn(*sys.argv[1:])
	
	# Allow the main function also to be called explicitly
	return wrapped_fn


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


@contextlib.contextmanager
def command_context(args, remove_env = [], set_env = { }, working_dir = None, use_stderr = False):
	env = dict(os.environ)
	
	for i in remove_env:
		del env[i]
	
	for k, v in set_env.items():
		env[k] = v
	
	try:
		process = subprocess.Popen(args, env = env, cwd = working_dir)
		process.wait()
	except OSError as e:
		raise UserError('Error running {}: {}', args[0], e)
	
	try:
		yield process
	except:
		process.kill()
		
		raise
	finally:
		process.wait()
	
	if process.returncode:
		raise UserError('Command failed: {}', ' '.join(args))


def command(args, remove_env = [], set_env = { }, working_dir = None):
	with command_context(args, remove_env, set_env, working_dir) as process:
		process.wait()


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
