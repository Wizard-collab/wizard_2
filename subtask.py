# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
