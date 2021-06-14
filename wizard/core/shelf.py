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
from wizard.vars import ressources

def create_project_script(name,
							script,
							only_subprocess=0,
							icon=ressources._default_script_shelf_icon_):
	scripts_folder = project.project().get_scripts_folder()
	file_name = f"{name}.py"
	file = os.path.normpath(os.path.join(scripts_folder, file_name))
	if project.project().add_shelf_script(name, file, only_subprocess, icon):
		with open(file, 'w') as f:
			f.write(script)

def execute_project_script(shelf_script_id):
	py_file = project.project().get_shelf_script_data(shelf_script_id, 'py_file')
	user.execute_py(py_file)