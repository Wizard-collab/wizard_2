# coding: utf-8

# Python modules
import yaml
import os

# Wizard modules
from wizard.constants import user_const
from wizard.core.site import site
from wizard.core import tools

from wizard.core import logging
logging = logging.get_logger(__name__)

class user:
	def __init__(self):
		self.get_user_prefs_dic()
	
	def get_site_path(self):
		return self.prefs_dic[user_const._site_path_]

	def set_site_path(self, site_path):
		self.prefs_dic[user_const._site_path_] = site_path
		self.write_prefs_dic()

	def set_user(self, user_name, password):
		site_obj = site()
		if user_name in site_obj.get_user_names_list():
			if tools.decrypt_string(site_obj.get_user_row_by_name(user_name)[2], password):
				self.prefs_dic[user_const._user_] = user_name
				self.write_prefs_dic()
				logging.info(f'{user_name} signed in')
			else:
				logging.warning(f'Wrong password for {user_name}')
		else:
			logging.error(f"{user_name} doesn't exists")

	def get_user(self):
		return self.prefs_dic[user_const._user_]

	def get_user_prefs_dic(self):
		self.user_prefs_file = user_const._user_prefs_file_
		if not os.path.isdir(user_const._user_path_):
			os.mkdir(user_const._user_path_)
		if not os.path.isfile(self.user_prefs_file):
			self.prefs_dic = dict()
			self.prefs_dic[user_const._site_path_] = None
			self.prefs_dic[user_const._user_] = None
			self.write_prefs_dic()
		else:
			with open(self.user_prefs_file, 'r') as f:
				self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

	def write_prefs_dic(self):
		with open(self.user_prefs_file, 'w') as f:
			yaml.dump(self.prefs_dic, f)