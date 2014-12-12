import contextlib, subprocess, tempfile, shutil, re, os


@contextlib.contextmanager
def TemporaryDirectory():
	dir = tempfile.mkdtemp()
	
	try:
		yield dir
	finally:
		shutil.rmtree(dir)


def command(args):
	process = subprocess.Popen(args)
	process.wait()
	
	assert not process.returncode


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
