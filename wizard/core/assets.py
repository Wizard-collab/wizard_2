# coding: utf-8

# Python modules
import os
import time

# Wizard modules
from wizard.core import environment
from wizard.core import project
from wizard.vars import assets_vars
from wizard.vars import softwares_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_domain(name):
	dir_name = os.path.join(environment.get_project_path(), name)
	domain_id = project.project().add_domain(name)
	if domain_id:
		if not os.path.isdir(dir_name):
			try:
				os.mkdir(dir_name)
				logging.info(f'{dir_name} created')
			except FileNotFoundError:
				logging.error(f"{environment.get_project_path()} doesn't exists")
				project.project().remove_domain(domain_id)
				domain_id = None
	return domain_id

def create_category(name, domain_id):
	category_id = None
	domain_path = get_domain_path(domain_id)
	if domain_path:
		dir_name = os.path.join(domain_path, name)
		category_id = project.project().add_category(name, domain_id)
		if category_id:
			if not os.path.isdir(dir_name):
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{domain_path} doesn't exists")
					project.project().remove_category(category_id)
					category_id = None
	else:
		logging.error("Can't create category")
	return category_id

def create_asset(name, category_id):
	asset_id = None
	category_path = get_category_path(category_id)
	if category_path:
		dir_name = os.path.join(category_path, name)
		asset_id = project.project().add_asset(name, category_id)
		if asset_id:
			if not os.path.isdir(dir_name):
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{category_path} doesn't exists")
					project.project().remove_asset(asset_id)
					asset_id = None
	else:
		logging.error("Can't create asset")
	return asset_id

def create_stage(name, asset_id):

	category_id = project.project().get_asset_parent_id(asset_id)
	category_name = project.project().get_category_name(category_id)
	domain_id = project.project().get_category_parent_id(category_id)
	domain_name = project.project().get_domain_name(domain_id)

	allowed = None

	if domain_name == assets_vars._assets_:
		if name in assets_vars._assets_stage_rules_dic_[category_name]:
			allowed = 1
	if domain_name == assets_vars._sequences_:
			allowed = 1
	if allowed:
		asset_path = get_asset_path(asset_id)
		if asset_path:
			dir_name = os.path.join(asset_path, name)
			stage_id = project.project().add_stage(name, asset_id)
			if stage_id:
				if not os.path.isdir(dir_name):
					try:
						os.mkdir(dir_name)
						logging.info(f'{dir_name} created')
						variant_id = create_variant('main', stage_id, 'default variant')
						project.project().set_stage_default_variant(stage_id, variant_id)
					except FileNotFoundError:
						logging.error(f"{asset_path} doesn't exists")
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
	stage_path = get_stage_path(stage_id)
	if stage_path:
		dir_name = os.path.join(stage_path, name)
		variant_id = project.project().add_variant(name, stage_id, comment)
		if variant_id:
			if not os.path.isdir(dir_name):
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{stage_path} doesn't exists")
					project.project().remove_variant(variant_id)
					variant_id = None
	else:
		logging.error("Can't create variant")
	return variant_id

def create_work_env(name, variant_id):
	work_env_id = None
	variant_path = get_variant_path(variant_id)
	if variant_path:
		dir_name = os.path.join(variant_path, name)
		work_env_id = project.project().add_work_env(name, variant_id)
		if work_env_id:
			if not os.path.isdir(dir_name):
				try:
					os.mkdir(dir_name)
					logging.info(f'{dir_name} created')
				except FileNotFoundError:
					logging.error(f"{variant_path} doesn't exists")
					project.project().remove_work_env(work_env_id)
					work_env_id = None
			add_version(work_env_id)
	else:
		logging.error("Can't create work env")
	return work_env_id

def add_version(work_env_id, comment="Nope."):
	versions_list = project.project().get_work_versions_names(work_env_id)
	if versions_list and versions_list != []:
		new_version =  str(int(versions_list[-1])+1).zfill(4)
	else:
		new_version = '0001'
	file_name = os.path.join(get_work_env_path(work_env_id), build_version_file_name(work_env_id, new_version))
	version_id = project.project().add_version(new_version, file_name, work_env_id, comment)
	return version_id

def get_domain_path(domain_id):
	dir_name = None
	domain_name = project.project().get_domain_name(domain_id)
	if domain_name:
		dir_name = os.path.join(environment.get_project_path(), domain_name)
	return dir_name

def get_category_path(category_id):
	dir_name = None
	domain_id = project.project().get_category_parent_id(category_id)
	if domain_id:
		category_name = project.project().get_category_name(category_id)
		domain_path = get_domain_path(domain_id)
		if category_name and domain_path:
			dir_name = os.path.join(domain_path, category_name)
	return dir_name

def get_asset_path(asset_id):
	dir_name = None
	category_id = project.project().get_asset_parent_id(asset_id)
	if category_id:
		asset_name = project.project().get_asset_name(asset_id)
		category_path = get_category_path(category_id)
		if asset_name and category_path:
			dir_name = os.path.join(category_path, asset_name)
	return dir_name

def get_stage_path(stage_id):
	dir_name = None
	asset_id = project.project().get_stage_parent_id(stage_id)
	if asset_id:
		stage_name = project.project().get_stage_name(stage_id)
		asset_path = get_asset_path(asset_id)
		if stage_name and asset_path:
			dir_name = os.path.join(asset_path, stage_name)
	return dir_name

def get_variant_path(variant_id):
	dir_name = None
	stage_id = project.project().get_variant_parent_id(variant_id)
	if stage_id:
		variant_name = project.project().get_variant_name(variant_id)
		stage_path = get_stage_path(stage_id)
		if variant_name and stage_path:
			dir_name = os.path.join(stage_path, variant_name)
	return dir_name

def get_work_env_path(work_env_id):
	dir_name = None
	variant_id = project.project().get_work_env_parent_id(work_env_id)
	if variant_id:
		work_env_name = project.project().get_work_env_name(work_env_id)
		variant_path = get_variant_path(variant_id)
		if work_env_name and variant_path:
			dir_name = os.path.join(variant_path, work_env_name)
	return dir_name

def build_version_file_name(work_env_id, name):
	variant_id = project.project().get_work_env_parent_id(work_env_id)
	variant_name = project.project().get_variant_name(variant_id)
	stage_id = project.project().get_variant_parent_id(variant_id)
	stage_name = project.project().get_stage_name(stage_id)
	asset_id = project.project().get_stage_parent_id(stage_id)
	asset_name = project.project().get_asset_name(asset_id)
	category_id = project.project().get_asset_parent_id(asset_id)
	category_name = project.project().get_category_name(category_id)
	work_env_name = project.project().get_work_env_name(work_env_id)
	extension = softwares_vars._softwares_extensions_dic_[work_env_name]
	file_name = f'{category_name}_{asset_name}_{stage_name}_{variant_name}.{name}.{extension}'
	return file_name