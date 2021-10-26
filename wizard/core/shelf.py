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

# Wizard modules
from wizard.core import project
from wizard.core import user
from wizard.core import tools
from wizard.vars import ressources
from wizard.vars import user_vars

def create_project_script(name,
							script,
							only_subprocess=0,
							icon=ressources._default_script_shelf_icon_):
	scripts_folder = project.get_scripts_folder()
	file_name = f"{name}.py"
	file = tools.get_filename_without_override(os.path.normpath(os.path.join(scripts_folder, file_name)))
	if project.add_shelf_script(name, file, only_subprocess, icon):
		with open(file, 'w') as f:
			f.write(script)

def execute_script(script_id):
	py_file = project.get_shelf_script_data(script_id, 'py_file')
	if py_file:
		user.user().execute_py(py_file)
