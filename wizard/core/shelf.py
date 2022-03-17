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

# This module manages the shelf scripts
# It access and create both project and user
# shelf scripts

# The scripts are stored as files and 
# the scripts datas are stored
# in the users documents or project
# database ( name, icon, onlysubprocess info )

# Python modules
import os
import logging

# Wizard modules
from wizard.core import project
from wizard.core import subtask
from wizard.core import user
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import ressources
from wizard.vars import user_vars

logger = logging.getLogger(__name__)

def create_project_script(name,
							script,
							help,
							only_subprocess=0,
							icon=ressources._default_script_shelf_icon_):
	
	execute = True
	if name is None or name =='':
		logger.warning('Please provide a tool name')
		execute = False

	if script is None or script =='':
		logger.warning('Please provide a script')
		execute = False

	if help is None or help =='':
		logger.warning('Please provide a short help for your tool')
		execute = False

	if execute:
		scripts_folder = project.get_scripts_folder()
		file_name = f"{name}.py"
		file = tools.get_filename_without_override(path_utils.join(scripts_folder, file_name))
		if project.add_shelf_script(name, file, help, only_subprocess, icon):
			with open(file, 'w') as f:
				f.write(script)
			return 1
		else:
			return None
	else:
		return None

def create_separator():
	project.add_shelf_separator()

def edit_project_script(id,
						help,
						icon,
						only_subprocess=0):
	return project.edit_shelf_script(id, help, icon, only_subprocess)

def execute_script(script_id):
	py_file = project.get_shelf_script_data(script_id, 'py_file')
	if py_file:
		user.user().execute_py(py_file)

def execute_script_as_subtask(script_id):
	py_file = project.get_shelf_script_data(script_id, 'py_file')
	if py_file:
		task = subtask.subtask(pycmd=py_file)
		task.start()
