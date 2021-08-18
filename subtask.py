# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
import time

# Wizard modules
from wizard.core import subtask
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

args = sys.argv

command = None
pycmd = None
env = None
cwd = None
print_stdout = False

file = args.pop(0)
while len(args) >=1:
	argument = args[0]
	if argument == '-print_stdout':
		print_stdout = True
		args.pop(0)
	while len(args) >= 2:
		argument = args.pop(0)
		if argument == '-cmd':
			command = args.pop(0)
		elif argument == '-env':
			env = args.pop(0)
		elif argument == '-cwd':
			cwd = args.pop(0)
		elif argument == '-pycmd':
			pycmd = args.pop(0)
		elif argument == '-print_stdout':
			print_stdout = True

if (command == None and pycmd == None):
	logger.error('''Please provide a command with the argument -cmd "your command"''')
else:
	task = subtask.subtask(command, pycmd, env, cwd, print_stdout)
	task.start()
