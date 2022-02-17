# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module permits to access the wizard
# core with simplified commands

# Wizard modules
from wizard import core
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class site:
	def __init__(self):
		pass

	def projects(self):
		# Return a list of the existing projects in the site database
		return core.site.get_projects_names_list()

	def users(self):
		# Return a list of the existing users in the site database
		return core.site.get_user_names_list()

	def upgrade_user_privilege(self, user_name, administrator_pass):
		return core.site.upgrade_user_privilege(user_name,
														administrator_pass)

	def downgrade_user_privilege(self, user_name, administrator_pass):
		return core.site.downgrade_user_privilege(user_name,
														administrator_pass)

class user:
	def __init__(self):
		pass

	def set(self, user_name, password):
		# Log a user
		return core.user.log_user(user_name, password)

	def get(self):
		# Return the current user
		return core.environment.get_user()

	def change_password(self, old_password, new_password):
		return core.site.modify_user_password(core.environment.get_user(),
													old_password,
													new_password)

	def is_admin(self):
		# Return the current user privilege
		return core.site.is_admin()

class project:
	def __init__(self):
		pass

	def set(self, project_name, project_password):
		# Log a project
		return core.user.log_project(project_name, project_password)

	def name(self):
		# Return the current project name
		return core.environment.get_project_name()

	def path(self):
		# Return the current project path
		return core.environment.get_project_path()

	def set_software_path(self, software, path):
		software_id = core.assets.get_software_id_by_name(software)
		if software_id:
			core.project.set_software_path(software_id, path)

class assets:
	def __init__(self):
		pass

	def create_sequence(self, name):
		string_sequence = None
		sequence_id = core.assets.create_category(name, 3)
		if sequence_id:
			string_sequence = core.assets.instance_to_string(('category',
																sequence_id))
		return string_sequence

	def create_asset(self, parent, name):
		string_asset = None
		instance_type, category_id = core.assets.string_to_instance(parent)
		if category_id:
			asset_id = core.assets.create_asset(name, category_id)
			if asset_id:
				string_asset = core.assets.instance_to_string(('asset',
																asset_id))
		return string_asset

	def create_shot(self, parent, name):
		return self.create_asset(parent, name)

	def create_stage(self, parent, stage):
		string_stage = None
		instance_type, asset_id = core.assets.string_to_instance(parent)
		if asset_id:
			stage_id = core.assets.create_stage(stage, asset_id)
			if stage_id:
				string_stage = core.assets.instance_to_string(('stage',
																stage_id))
		return string_stage

	def create_variant(self, parent, name):
		string_variant = None
		instance_type, stage_id = core.assets.string_to_instance(parent)
		if stage_id:
			variant_id = core.assets.create_variant(name, stage_id)
			if variant_id:
				string_variant = core.assets.instance_to_string(('variant',
																	variant_id))
		return string_variant

	def create_work_env(self, parent, software):
		string_work_env = None
		instance_type, variant_id = core.assets.string_to_instance(parent)
		if variant_id:
			software_id = core.assets.get_software_id_by_name(software)
			if software_id:
				work_env_id = core.assets.create_work_env(software_id, variant_id)
				if work_env_id:
					string_work_env = core.assets.instance_to_string(('work_env',
																		work_env_id))
		return string_work_env

class launch:
	def __init__(self):
		pass

	def work_env(self, work_env):
		instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
		if work_env_id:
			last_work_version_id = core.project.get_last_work_version(work_env_id, 'id')
			if last_work_version_id:
				core.launch.launch_work_version(last_work_version_id[0])

	def work_version(self, work_version):
		instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
		if work_version_id:
			core.launch.launch_work_version(work_version_id)

	def kill_work_env(self, work_env):
		instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
		if work_env_id:
			core.launch.kill(work_env_id)

	def get_running_work_envs(self):
		running_work_envs = []
		running_work_env_ids = core.launch.get()
		if running_work_env_ids:
			for work_env_id in running_work_env_ids:
				running_work_envs.append(core.assets.instance_to_string(('work_env',
																			work_env_id)))
		return running_work_envs

site = site()
user = user()
project = project()
assets = assets()
launch = launch()
