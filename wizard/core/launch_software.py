# coding: utf-8

# Wizard modules
from wizard.core import project
from wizard.vars import softwares_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

# Python modules
import os
import subprocess

def launch_work_version(version_id):
	work_version_row = project.project().get_version_data(version_id)
	file_path = work_version_row['dir_name']
	work_env_id = work_version_row['work_env_id']
	software_id = project.project().get_work_env_data(work_env_id, 'software_id')
	software_row = project.project().get_software_data(software_id)
	command = build_command(file_path, software_row)
	env = build_env(work_env_id, software_row)
	print(command)
	print(env)
	subprocess.Popen(command, env=env)

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
			raw_command = raw_command.replace(softwares_vars._script_key_, softwares_vars._scripts_dic_[software_row['name']])
		return raw_command

	else:
		logging.warning(f"{software_row['name']} path not defined")
		return None

def build_env(work_env_id, software_row):
	env = os.environ.copy()
	env['wizard_work_env_id'] = str(work_env_id)
	env[softwares_vars._script_env_dic_[software_row['name']]]=softwares_vars._plugins_path_[software_row['name']]
	env[softwares_vars._script_env_dic_[software_row['name']]]+=os.pathsep+softwares_vars._main_script_path_
	return env
