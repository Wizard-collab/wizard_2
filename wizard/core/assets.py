# coding: utf-8

# Python modules
import os
import time

# Wizard modules
from wizard.core import environment
from wizard.core import project
from wizard.vars import assets_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_domain(name):
	dir_name = os.path.join(environment.get_project_path(), name)
	domain_id = project.project().add_domain(name)
	if domain_id:
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)
			logging.info(f'{dir_name} created')
	return domain_id

def create_category(name, domain_id):
	dir_name = os.path.join(get_domain_path(domain_id), name)
	category_id = project.project().add_category(name, domain_id)
	if category_id:
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)
			logging.info(f'{dir_name} created')
	return category_id

def create_asset(name, category_id):
	dir_name = os.path.join(get_category_path(category_id), name)
	asset_id = project.project().add_asset(name, category_id)
	if asset_id:
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)
			logging.info(f'{dir_name} created')
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
		dir_name = os.path.join(get_asset_path(asset_id), name)
		stage_id = project.project().add_stage(name, asset_id)
		if stage_id:
			if not os.path.isdir(dir_name):
				os.mkdir(dir_name)
				logging.info(f'{dir_name} created')
			variant_id = create_variant('main', stage_id, 'default variant')
			project.project().set_stage_default_variant(stage_id, variant_id)
		return stage_id
	else:
		logging.warning(f"{name} doesn't match stages rules")
		return None

def create_variant(name, stage_id, comment=''):
	start_time = time.time()
	dir_name = os.path.join(get_stage_path(stage_id), name)
	variant_id = project.project().add_variant(name, stage_id, comment)
	if variant_id:
		if not os.path.isdir(dir_name):
			os.mkdir(dir_name)
			logging.info(f'{dir_name} created')
	return variant_id
	print('variant creation time : ' + str(time.time()-start_time))

def get_domain_path(domain_id):
	domain_name = project.project().get_domain_name(domain_id)
	dir_name = os.path.join(environment.get_project_path(), domain_name)
	return dir_name

def get_category_path(category_id):
	domain_id = project.project().get_category_parent_id(category_id)
	category_name = project.project().get_category_name(category_id)
	dir_name = os.path.join(get_domain_path(domain_id), category_name)
	return dir_name

def get_asset_path(asset_id):
	category_id = project.project().get_asset_parent_id(asset_id)
	asset_name = project.project().get_asset_name(asset_id)
	dir_name = os.path.join(get_category_path(category_id), asset_name)
	return dir_name

def get_stage_path(stage_id):
	asset_id = project.project().get_stage_parent_id(stage_id)
	stage_name = project.project().get_stage_name(stage_id)
	dir_name = os.path.join(get_asset_path(asset_id), stage_name)
	return dir_name