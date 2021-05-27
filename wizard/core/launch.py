# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# The main wizard software launching module
# This module permits to launch a work version ( id )
# It build the command and environment for the Popen
# call

# If no file is found for the given version id
# it launches the software without a file but 
# with the correct environment in order to save
# a version later within the software

# Python modules
import os
import subprocess

# Wizard modules
from wizard.core import project
from wizard.vars import softwares_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def launch_work_version(version_id):
	work_version_row = project.project().get_version_data(version_id)
	if work_version_row:
		file_path = work_version_row['file_path']
		work_env_id = work_version_row['work_env_id']
		if not project.project().get_lock(work_env_id):
			software_id = project.project().get_work_env_data(work_env_id, 'software_id')
			software_row = project.project().get_software_data(software_id)
			command = build_command(file_path, software_row)
			env = build_env(work_env_id, software_row)
			if command :
				subprocess.Popen(command, env=env, cwd='softwares')
				logging.info(f"{software_row['name']} launched")

def build_command(file_path, software_row):
	software_path = software_row['path']
	if software_path != '':
		if os.path.isfile(file_path):
			raw_command = software_row['file_command']
		else:
			raw_command = software_row['no_file_command']
			logging.info("File not existing, launching software with empty scene")

		raw_command = raw_command.replace(softwares_vars._executable_key_, software_path)
		raw_command = raw_command.replace(softwares_vars._file_key_, file_path)
		if software_row['name'] in softwares_vars._scripts_dic_.keys():
			raw_command = raw_command.replace(softwares_vars._script_key_,
								softwares_vars._scripts_dic_[software_row['name']])
		return raw_command

	else:
		logging.warning(f"{software_row['name']} path not defined")
		return None

def build_env(work_env_id, software_row):
	env = os.environ.copy()
	env['wizard_work_env_id'] = str(work_env_id)
	env[softwares_vars._script_env_dic_[software_row['name']]] = os.pathsep+softwares_vars._main_script_path_
	return env
