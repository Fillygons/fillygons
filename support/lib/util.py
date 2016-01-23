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
def command_context(args, remove_env = [], set_env = { }, working_dir = None, use_stdout = True, use_stderr = False):
	env = dict(os.environ)
	
	for i in remove_env:
		del env[i]
	
	for k, v in set_env.items():
		env[k] = v
	
	if use_stdout:
		stdout = subprocess.PIPE
	else:
		stdout = None
	
	if use_stderr:
		stderr = subprocess.PIPE
	else:
		stderr = None
	
	try:
		process = subprocess.Popen(args, env = env, cwd = working_dir, stdout = stdout, stderr = stderr)
	except OSError as e:
		raise UserError('Error running {}: {}', args[0], e)
	
	try:
		yield process
	except:
		try:
			process.kill()
		except OSError:
			# Ignore exceptions here so we don't mask the already-being-thrown exception.
			pass
		
		raise
	finally:
		try:
			# Use communicate so that we won't deadlock if the process generates some unread output.
			process.communicate()
		except (ValueError, OSError):
			# Ignore exceptions here because we're just trying to get the process to complete.
			pass
	
	if process.returncode:
		raise UserError('Command failed: {}', ' '.join(args))


def command(args, remove_env = [], set_env = { }, working_dir = None, use_stdout = False, use_stderr = False):
	with command_context(args, remove_env, set_env, working_dir, use_stdout, use_stderr) as process:
		return process.communicate()


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
