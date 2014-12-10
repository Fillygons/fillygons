import contextlib, subprocess, tempfile, shutil


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
