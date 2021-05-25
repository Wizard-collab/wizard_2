# coding: utf-8

# Python modules
import yaml
import os

# Wizard modules
from wizard.vars import user_vars
from wizard.core.site import site
from wizard.core import environment
from wizard.core import tools

from wizard.core import logging
logging = logging.get_logger(__name__)

class user:
	def __init__(self):
		self.get_user_prefs_dic()
	
	def get_site_path(self):
		return self.prefs_dic[user_vars._site_path_]

	def set_site_path(self, site_path):
		self.prefs_dic[user_vars._site_path_] = site_path
		self.write_prefs_dic()
		environment.build_site_env(site_path)

	def set_user(self, user_name, password):
		site_obj = site()
		if user_name in site_obj.get_user_names_list():
			if tools.decrypt_string(site_obj.get_user_row_by_name(user_name)['pass'],
									password):
				self.prefs_dic[user_vars._user_] = user_name
				self.write_prefs_dic()
				environment.build_user_env(user_name)
				logging.info(f'{user_name} signed in')
			else:
				logging.warning(f'Wrong password for {user_name}')
		else:
			logging.error(f"{user_name} doesn't exists")

	def get_user(self):
		return self.prefs_dic[user_vars._user_]

	def set_project(self, project_name, password):
		site_obj = site()
		if project_name in site_obj.get_projects_names_list():
			if tools.decrypt_string(site_obj.get_project_row_by_name(project_name)['project_password'],
									password):
				self.prefs_dic[user_vars._project_] = project_name
				self.write_prefs_dic()
				environment.build_project_env(project_name, 
							site_obj.get_project_row_by_name(project_name)['project_path'])
				logging.info(f'Successfully signed in {project_name} project')
			else:
				logging.warning(f'Wrong password for {project_name}')
		else:
			logging.error(f"{project_name} doesn't exists")

	def get_project(self):
		return self.prefs_dic[user_vars._project_]

	def get_user_prefs_dic(self):
		self.user_prefs_file = user_vars._user_prefs_file_
		if not os.path.isdir(user_vars._user_path_):
			os.mkdir(user_vars._user_path_)
		if not os.path.isfile(self.user_prefs_file):
			self.prefs_dic = dict()
			self.prefs_dic[user_vars._site_path_] = None
			self.prefs_dic[user_vars._user_] = None
			self.prefs_dic[user_vars._project_] = None
			self.write_prefs_dic()
		else:
			with open(self.user_prefs_file, 'r') as f:
				self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

	def write_prefs_dic(self):
		with open(self.user_prefs_file, 'w') as f:
			yaml.dump(self.prefs_dic, f)