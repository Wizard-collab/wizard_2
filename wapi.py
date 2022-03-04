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

# This module permits to access the wizard
# core with simplified commands

# Python modules
import logging

# Wizard modules
from wizard import core
logger = logging.getLogger(__name__)

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

	# Creation commands

	def create_sequence(self, name):
		string_sequence = None
		sequence_id = core.assets.create_category(name, 3)
		if sequence_id:
			string_sequence = core.assets.instance_to_string(('category',
																sequence_id))
		return string_sequence

	def create_asset(self, parent, name):
		# The parent argument should look like
		# "assets/characters"
		string_asset = None
		instance_type, category_id = core.assets.string_to_instance(parent)
		if category_id:
			asset_id = core.assets.create_asset(name, category_id)
			if asset_id:
				string_asset = core.assets.instance_to_string(('asset',
																asset_id))
		return string_asset

	def create_shot(self, parent, name):
		# The parent argument should look like
		# "sequences/Intro"
		return self.create_asset(parent, name)

	def create_stage(self, parent, stage):
		# The parent argument should look like
		# "assets/characters/Joe"
		string_stage = None
		instance_type, asset_id = core.assets.string_to_instance(parent)
		if asset_id:
			stage_id = core.assets.create_stage(stage, asset_id)
			if stage_id:
				string_stage = core.assets.instance_to_string(('stage',
																stage_id))
		return string_stage

	def create_variant(self, parent, name):
		# The parent argument should look like
		# "assets/characters/Joe/modeling"
		string_variant = None
		instance_type, stage_id = core.assets.string_to_instance(parent)
		if stage_id:
			variant_id = core.assets.create_variant(name, stage_id)
			if variant_id:
				string_variant = core.assets.instance_to_string(('variant',
																	variant_id))
		return string_variant

	def create_work_env(self, parent, software):
		# The parent argument should look like
		# "assets/characters/Joe/modeling/main"
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

	# Archive commands

	def archive_asset(self, asset):
		success = None
		instance_type, asset_id = core.assets.string_to_instance(asset)
		if asset_id:
			success = core.assets.archive_asset(asset_id)
		return success

	def archive_sequence(self, sequence):
		success = None
		instance_type, sequence_id = core.assets.string_to_instance(sequence)
		if sequence_id:
			success = core.assets.archive_category(sequence_id)
		return success

	def archive_stage(self, stage):
		success = None
		instance_type, stage_id = core.assets.string_to_instance(stage)
		if stage_id:
			success = core.assets.archive_stage(stage_id)
		return success

	def archive_variant(self, variant):
		success = None
		instance_type, variant_id = core.assets.string_to_instance(variant)
		if variant_id:
			success = core.assets.archive_variant(variant_id)
		return success

	def archive_work_env(self, work_env):
		success = None
		instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
		if instance_type == 'work_env' and work_env_id:
			success = core.assets.archive_work_env(work_env_id)
		return success

	def archive_work_version(self, work_version):
		success = None
		instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
		if instance_type == 'work_version' and work_version_id:
			success = core.assets.archive_work_version(work_version_id)
		return success

	# List commands

	def list_domains(self):
		domains = core.project.get_domains('name')
		return domains

	def list_categories(self, parent):
		# The parent argument should look like
		# "assets"
		categories = None
		instance_type, domain_id = core.assets.string_to_instance(parent)
		if domain_id:
			categories = core.project.get_domain_childs(domain_id, 'name')
		return categories

	def list_assets(self, parent):
		# The parent argument should look like
		# "assets/characters"
		assets = None
		instance_type, category_id = core.assets.string_to_instance(parent)
		if category_id:
			assets = core.project.get_category_childs(category_id, 'name')
		return assets

	def list_stages(self, parent):
		# The parent argument should look like
		# "assets/characters/Joe"
		stages = None
		instance_type, asset_id = core.assets.string_to_instance(parent)
		if asset_id:
			stages = core.project.get_asset_childs(asset_id, 'name')
		return stages

	def list_variants(self, parent):
		# The parent argument should look like
		# "assets/characters/Joe/modeling"
		variants = None
		instance_type, stage_id = core.assets.string_to_instance(parent)
		if stage_id:
			variants = core.project.get_stage_childs(stage_id, 'name')
		return variants

	def list_work_envs(self, parent):
		# The parent argument should look like
		# "assets/characters/Joe/modeling/main"
		work_envs = None
		instance_type, variant_id = core.assets.string_to_instance(parent)
		if variant_id:
			work_envs = core.project.get_variant_work_envs_childs(variant_id, 'name')
		return work_envs

	def list_work_versions(self, parent):
		# The parent argument should look like
		# "assets/characters/Joe/modeling/main/blender"
		work_versions = None
		instance_type, work_env_id = core.assets.string_to_work_instance(parent)
		if work_env_id:
			work_versions = core.project.get_work_versions(work_env_id, 'name')
		return work_versions

class launch:
	def __init__(self):
		pass

	def work_env(self, work_env):
		# Run the last version of the given work environment related software
		instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
		if work_env_id:
			last_work_version_id = core.project.get_last_work_version(work_env_id, 'id')
			if last_work_version_id:
				core.launch.launch_work_version(last_work_version_id[0])

	def work_version(self, work_version):
		# Run the given work version related software
		instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
		if work_version_id:
			core.launch.launch_work_version(work_version_id)

	def kill_work_env(self, work_env):
		# Terminate the given work environment related software instance
		instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
		if work_env_id:
			core.launch.kill(work_env_id)

	def get_running_work_envs(self):
		# Return the running work environments related softwares instances
		running_work_envs = []
		running_work_env_ids = core.launch.get()
		if running_work_env_ids:
			for work_env_id in running_work_env_ids:
				running_work_envs.append(core.assets.instance_to_string(('work_env',
																			work_env_id)))
		return running_work_envs

class team:
	def __init__(self):
		pass

	def refresh_ui(self):
		# Refresh the project team interfaces
		core.team_client.refresh_team(core.environment.get_team_dns())

site = site()
user = user()
project = project()
assets = assets()
launch = launch()
team = team()
