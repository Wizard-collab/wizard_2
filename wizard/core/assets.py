# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import time
import shutil

# Wizard modules
from wizard.core import environment
from wizard.core import project
from wizard.core import site
from wizard.core import tools
from wizard.core import screenshot
from wizard.vars import assets_vars
from wizard.vars import softwares_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_domain(name):
	domain_id = None
	if tools.is_safe(name):
		dir_name = os.path.normpath(os.path.join(environment.get_project_path(), name))
		domain_id = project.project().add_domain(name)
		if domain_id:
			try:
				os.mkdir(dir_name)
				logging.info(f'{dir_name} created')
			except FileNotFoundError:
				logging.error(f"{environment.get_project_path()} doesn't exists")
				project.project().remove_domain(domain_id)
				domain_id = None
			except FileExistsError:
				logging.error(f"{dir_name} already exists on filesystem")
				project.project().remove_domain(domain_id)
				domain_id = None
			except PermissionError:
				logging.error(f"{dir_name} access denied")
				project.project().remove_domain(domain_id)
				domain_id = None
	else:
		logging.warning(f"{name} contains illegal characters")
	return domain_id

def create_category(name, domain_id):
	category_id = None
	if tools.is_safe(name):
		domain_path = get_domain_path(domain_id)
		if domain_path:
			dir_name = os.path.normpath(os.path.join(domain_path, name))
			category_id = project.project().add_category(name, domain_id)
			if category_id:
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{domain_path} doesn't exists")
					project.project().remove_category(category_id)
					category_id = None
				except FileExistsError:
					logging.error(f"{dir_name} already exists on filesystem")
					project.project().remove_category(category_id)
					category_id = None
				except PermissionError:
					logging.error(f"{dir_name} access denied")
					project.project().remove_category(category_id)
					category_id = None
		else:
			logging.error("Can't create category")
	else:
		logging.warning(f"{name} contains illegal characters")
	return category_id

def create_asset(name, category_id):
	asset_id = None
	if tools.is_safe(name):
		category_path = get_category_path(category_id)
		if category_path:
			dir_name = os.path.normpath(os.path.join(category_path, name))
			asset_id = project.project().add_asset(name, category_id)
			if asset_id:
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{category_path} doesn't exists")
					project.project().remove_asset(asset_id)
					asset_id = None
				except FileExistsError:
					logging.error(f"{dir_name} already exists on filesystem")
					project.project().remove_asset(asset_id)
					asset_id = None
				except PermissionError:
					logging.error(f"{dir_name} access denied")
					project.project().remove_asset(asset_id)
					asset_id = None
		else:
			logging.error("Can't create asset")
	else:
		logging.warning(f"{name} contains illegal characters")
	return asset_id

def create_stage(name, asset_id):
	# The stage creation need to follow some name rules
	# if category is assets, the rules are :
	#	modeling
	#	rigging
	#	grooming
	#	texturing
	#	shading

	category_id = project.project().get_asset_data(asset_id, 'category_id')
	category_name = project.project().get_category_data(category_id, 'name')
	domain_id = project.project().get_category_data(category_id, 'domain_id')
	domain_name = project.project().get_domain_data(domain_id, 'name')

	allowed = None

	if domain_name == assets_vars._assets_:
		if name in assets_vars._assets_stage_rules_dic_[category_name]:
			allowed = 1
	if domain_name == assets_vars._sequences_:
			allowed = 1
	if allowed:
		asset_path = get_asset_path(asset_id)
		if asset_path:
			dir_name = os.path.normpath(os.path.join(asset_path, name))
			stage_id = project.project().add_stage(name, asset_id)
			if stage_id:
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
					variant_id = create_variant('main', stage_id, 'default variant')
					project.project().set_stage_default_variant(stage_id, variant_id)
				except FileNotFoundError:
					logging.error(f"{asset_path} doesn't exists")
					project.project().remove_stage(stage_id)
					stage_id = None
				except FileExistsError:
					logging.error(f"{dir_name} already exists on filesystem")
					project.project().remove_stage(stage_id)
					stage_id = None
				except PermissionError:
					logging.error(f"{dir_name} access denied")
					project.project().remove_stage(stage_id)
					stage_id = None
			return stage_id
		else:
			logging.error("Can't create stage")
			return None
	else:
		logging.warning(f"{name} doesn't match stages rules")
		return None

def create_variant(name, stage_id, comment=''):
	variant_id = None
	if tools.is_safe(name):
		stage_path = get_stage_path(stage_id)
		if stage_path:
			dir_name = os.path.normpath(os.path.join(stage_path, name))
			variant_id = project.project().add_variant(name, stage_id, comment)
			if variant_id:
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{stage_path} doesn't exists")
					project.project().remove_variant(variant_id)
					variant_id = None
				except FileExistsError:
					logging.error(f"{dir_name} already exists on filesystem")
					project.project().remove_variant(variant_id)
					variant_id = None
				except PermissionError:
					logging.error(f"{dir_name} access denied")
					project.project().remove_variant(variant_id)
					variant_id = None
		else:
			logging.error("Can't create variant")
	else:
		logging.warning(f"{name} contains illegal characters")
	return variant_id

def create_work_env(software_id, variant_id):
	work_env_id = None
	name = project.project().get_software_data(software_id, 'name')
	if name in project.project().get_softwares_names_list():
		variant_path = get_variant_path(variant_id)
		if variant_path:
			dir_name = os.path.normpath(os.path.join(variant_path, name))
			work_env_id = project.project().add_work_env(name, software_id, variant_id)
			if work_env_id:
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
					add_version(work_env_id, do_screenshot=0)
				except FileNotFoundError:
					logging.error(f"{variant_path} doesn't exists")
					project.project().remove_work_env(work_env_id)
					work_env_id = None
				except FileExistsError:
					logging.error(f"{dir_name} already exists on filesystem")
					project.project().remove_work_env(work_env_id)
					work_env_id = None
				except PermissionError:
					logging.error(f"{dir_name} access denied")
					project.project().remove_work_env(work_env_id)
					work_env_id = None
		else:
			logging.error("Can't create work env")
	else:
		logging.warning(f"{name} is not a valid work environment ( software not handled )")
	return work_env_id

def archive_work_env(work_env_id):
	if site.site().is_admin():
		work_env_row = project.project().get_work_env_data(work_env_id)
		if work_env_row:
			dir_name = get_work_env_path(work_env_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					print(shutil.rmtree(dir_name))
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			project.project().remove_work_env(work_env_id)
		else:
			return None
	else:
		return None


def add_version(work_env_id, comment="", do_screenshot=1):
	versions_list = project.project().get_work_versions(work_env_id, 'name')
	if versions_list and versions_list != []:
		new_version =  str(int(versions_list[-1])+1).zfill(4)
	else:
		new_version = '0001'
	file_name = os.path.normpath(os.path.join(get_work_env_path(work_env_id), 
							build_version_file_name(work_env_id, new_version)))
	if screenshot:
		screenshot_bytes = screenshot.screenshot_to_bytes()
	else:
		screenshot_bytes = None
	version_id = project.project().add_version(new_version,
												file_name,
												work_env_id,
												comment,
												screenshot_bytes)
	return version_id

def archive_version(version_id):
	if site.site().is_admin():
		version_row = project.project().get_version_data(version_id)
		if version_row:
			if os.path.isfile(version_row['file_path']):
				zip_file = os.path.join(os.path.split(version_row['file_path'])[0], 
							'archives.zip')
				if tools.zip_files([version_row['file_path']], zip_file):
					os.remove(version_row['file_path'])
					logging.info(f"{version_row['file_path']} deleted")
			else:
				logging.warning(f"{version_row['file_path']} not found")
			project.project().remove_version(version_row['id'])
			return 1
		else:
			return None		
	else:
		return None


def get_domain_path(domain_id):
	dir_name = None
	domain_name = project.project().get_domain_data(domain_id, 'name')
	if domain_name:
		dir_name = os.path.join(environment.get_project_path(), domain_name)
	return dir_name

def get_category_path(category_id):
	dir_name = None
	category_row = project.project().get_category_data(category_id)
	if category_row:
		category_name = category_row['name']
		domain_path = get_domain_path(category_row['domain_id'])
		if category_name and domain_path:
			dir_name = os.path.join(domain_path, category_name)
	return dir_name

def get_asset_path(asset_id):
	dir_name = None
	asset_row = project.project().get_asset_data(asset_id)
	if asset_row:
		asset_name = asset_row['name']
		category_path = get_category_path(asset_row['category_id'])
		if asset_name and category_path:
			dir_name = os.path.join(category_path, asset_name)
	return dir_name

def get_stage_path(stage_id):
	dir_name = None
	stage_row = project.project().get_stage_data(stage_id)
	if stage_row:
		stage_name = stage_row['name']
		asset_path = get_asset_path(stage_row['asset_id'])
		if stage_name and asset_path:
			dir_name = os.path.join(asset_path, stage_name)
	return dir_name

def get_variant_path(variant_id):
	dir_name = None
	variant_row = project.project().get_variant_data(variant_id)
	if variant_row:
		variant_name = variant_row['name']
		stage_path = get_stage_path(variant_row['stage_id'])
		if variant_name and stage_path:
			dir_name = os.path.join(stage_path, variant_name)
	return dir_name

def get_work_env_path(work_env_id):
	dir_name = None
	work_env_row = project.project().get_work_env_data(work_env_id)
	if work_env_row:
		work_env_name = work_env_row['name']
		variant_path = get_variant_path(work_env_row['variant_id'])
		if work_env_name and variant_path:
			dir_name = os.path.join(variant_path, work_env_name)
	return dir_name

def build_version_file_name(work_env_id, name):
	project_obj = project.project()
	work_env_row = project_obj.get_work_env_data(work_env_id)
	variant_row = project_obj.get_variant_data(work_env_row['variant_id'])
	stage_row = project_obj.get_stage_data(variant_row['stage_id'])
	asset_row = project_obj.get_asset_data(stage_row['asset_id'])
	category_row = project_obj.get_category_data(asset_row['category_id'])
	extension = project_obj.get_software_data(work_env_row['software_id'], 'extension')
	file_name = f"{category_row['name']}"
	file_name += f"_{asset_row['name']}"
	file_name += f"_{stage_row['name']}"
	file_name += f"_{variant_row['name']}"
	file_name += f"_{work_env_row['name']}"
	file_name += f".{name}"
	file_name += f".{extension}"
	return file_name