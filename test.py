import sys
import logging

class custom_stdout:
	def __init__(self):
		pass

	def write(self, buf):
		sys.__stdout__.write(buf)

	def flush(self):
		sys.__stdout__.flush()

class custom_stderr:
	def __init__(self):
		pass

	def write(self, buf):
		sys.__stderr__.write(buf)

	def flush(self):
		sys.__stderr__.flush()

sys.stdout = custom_stdout()
sys.stderr = custom_stderr()