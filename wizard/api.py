# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module permits to access the wizard
# core with simplified commands

# Wizard modules
from wizard import core

class site:
	def __init__(self):
		pass

	def path(self):
		return core.environment.get_site_path()

	def projects(self):
		return core.site.site().get_projects_names_list()

	def users(self):
		return core.site.site().get_user_names_list()

	def upgrade_user_privilege(self, user_name, administrator_pass):
		return core.site.site().upgrade_user_privilege(user_name,
														administrator_pass)

	def downgrade_user_privilege(self, user_name, administrator_pass):
		return core.site.site().downgrade_user_privilege(user_name,
														administrator_pass)

class user:
	def __init__(self):
		pass

	def set(self, user_name, password):
		return core.user.log_user(user_name, password)

	def get(self):
		return core.environment.get_user()

	def change_password(self, old_password, new_password):
		return core.site.site().modify_user_password(core.environment.get_user(),
													old_password,
													new_password)

	def is_admin(self):
		return core.site.site().is_admin()

class project:
	def __init__(self):
		pass

	def set(self, project_name, project_password):
		return core.user.log_project(project_name, project_password)

	def name(self):
		return core.environment.get_project_name()

	def path(self):
		return core.environment.get_project_path()

site = site()
user = user()
project = project()
