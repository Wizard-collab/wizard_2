# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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

def create_script(name,
							script,
							only_subprocess=0,
							icon=ressources._default_script_shelf_icon_,
							project=0):
	if project:
		create_project_script(name,
								script,
								only_subprocess,
								icon)
	else:
		create_user_script(name,
								script,
								only_subprocess,
								icon)

def create_project_script(name,
							script,
							only_subprocess=0,
							icon=ressources._default_script_shelf_icon_):
	scripts_folder = project.project().get_scripts_folder()
	file_name = f"{name}.py"
	file = tools.get_filename_without_override(os.path.normpath(os.path.join(scripts_folder, file_name)))
	if project.project().add_shelf_script(name, file, only_subprocess, icon):
		with open(file, 'w') as f:
			f.write(script)

def create_user_script(name,
						script,
						only_subprocess=0,
						icon=ressources._default_script_shelf_icon_):
	scripts_folder = user_vars._script_path_
	file_name = f"{name}.py"
	file = tools.get_filename_without_override(os.path.normpath(os.path.join(scripts_folder, file_name)))
	if user.user().add_shelf_script(name, file, only_subprocess, icon):
		with open(file, 'w') as f:
			f.write(script)

def execute_project_script(name):
	py_file = project.project().get_shelf_script_data(name, 'py_file')
	if py_file:
		user.user().execute_py(py_file)

def execute_user_script(name):
	py_file = user.user().get_shelf_script_data(name, 'py_file')
	if py_file:
		user.user().execute_py(py_file)
