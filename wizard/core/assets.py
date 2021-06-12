# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is the main instances management module
# You can create, get the path and archive the following instances
# - domains
# - categories
# - assets
# - stages
# - variants
# - work env
# - versions
# - export assets
# - export versions

# The creation of an instance basically log the instance 
# in the project database and create the corresponding folders
# on the file system

# The archiving of an instance basically archive the corresponding 
# folder, delete the original folder from the file
# system and remove the instance from the project database

# The path query of an instance will only access the database and
# construct the directory name, this modules doesn't
# query the file system

# Python modules
import os
import time
import shutil

# Wizard modules
from wizard.core import environment
from wizard.core import events
from wizard.core import project
from wizard.core import site
from wizard.core import tools
from wizard.core import image
from wizard.vars import assets_vars
from wizard.vars import softwares_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_domain(name):
	domain_id = None
	if tools.is_safe(name):
		dir_name = os.path.normpath(os.path.join(environment.get_project_path(),
									name))
		domain_id = project.project().add_domain(name)
		if domain_id:
			if not tools.create_folder(dir_name):
				project.project().remove_domain(domain_id)
				domain_id = None
	else:
		logging.warning(f"{name} contains illegal characters")
	return domain_id

def archive_domain(domain_id):
	if site.site().is_admin():
		domain_row = project.project().get_domain_data(domain_id)
		if domain_row:
			dir_name = get_domain_path(domain_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_domain(domain_id)
		else:
			return None
	else:
		return None

def create_category(name, domain_id):
	category_id = None
	if tools.is_safe(name):
		domain_path = get_domain_path(domain_id)
		if domain_path:
			dir_name = os.path.normpath(os.path.join(domain_path, name))
			category_id = project.project().add_category(name, domain_id)
			if category_id:
				if not tools.create_folder(dir_name):
					project.project().remove_category(category_id)
					category_id = None
				else:
					events.add_creation_event('category', category_id)
		else:
			logging.error("Can't create category")
	else:
		logging.warning(f"{name} contains illegal characters")
	return category_id

def archive_category(category_id):
	if site.site().is_admin():
		category_row = project.project().get_category_data(category_id)
		if category_row:
			dir_name = get_category_path(category_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_category(category_id)
		else:
			return None
	else:
		return None

def create_asset(name, category_id):
	asset_id = None
	if tools.is_safe(name):
		category_path = get_category_path(category_id)
		if category_path:
			dir_name = os.path.normpath(os.path.join(category_path, name))
			asset_id = project.project().add_asset(name, category_id)
			if asset_id:
				if not tools.create_folder(dir_name):
					project.project().remove_asset(asset_id)
					asset_id = None
				else:
					events.add_creation_event('asset', asset_id)
		else:
			logging.error("Can't create asset")
	else:
		logging.warning(f"{name} contains illegal characters")
	return asset_id

def archive_asset(asset_id):
	if site.site().is_admin():
		asset_row = project.project().get_asset_data(asset_id)
		if asset_row:
			dir_name = get_asset_path(asset_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_asset(asset_id)
		else:
			return None
	else:
		return None

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
				if not tools.create_folder(dir_name):
					project.project().remove_stage(stage_id)
					stage_id = None
				else:
					variant_id = create_variant('main', stage_id, 'default variant')
					if variant_id:
						project.project().set_stage_default_variant(stage_id, variant_id)
			return stage_id
		else:
			logging.error("Can't create stage")
			return None
	else:
		logging.warning(f"{name} doesn't match stages rules")
		return None

def archive_stage(stage_id):
	if site.site().is_admin():
		stage_row = project.project().get_stage_data(stage_id)
		if stage_row:
			dir_name = get_stage_path(stage_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_stage(stage_id)
		else:
			return None
	else:
		return None

def create_variant(name, stage_id, comment=''):
	variant_id = None
	if tools.is_safe(name):
		stage_path = get_stage_path(stage_id)
		if stage_path:
			dir_name = os.path.normpath(os.path.join(stage_path, name))
			variant_id = project.project().add_variant(name, stage_id, comment)
			if variant_id:
				if not tools.create_folder(dir_name):
					project.project().remove_variant(variant_id)
					variant_id = None
				else:
					# Add other folders
					tools.create_folder(os.path.normpath(os.path.join(dir_name, '_EXPORTS')))
					tools.create_folder(os.path.normpath(os.path.join(dir_name, '_SANDBOX')))
					events.add_creation_event('variant', variant_id)
		else:
			logging.error("Can't create variant")
	else:
		logging.warning(f"{name} contains illegal characters")
	return variant_id

def archive_variant(variant_id):
	if site.site().is_admin():
		variant_row = project.project().get_variant_data(variant_id)
		if variant_row:
			dir_name = get_variant_path(variant_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_variant(variant_id)
		else:
			return None
	else:
		return None

def create_work_env(software_id, variant_id):
	work_env_id = None
	name = project.project().get_software_data(software_id, 'name')
	if name in project.project().get_softwares_names_list():
		variant_path = get_variant_path(variant_id)
		if variant_path:
			dir_name = os.path.normpath(os.path.join(variant_path, name))
			work_env_id = project.project().add_work_env(name,
														software_id,
														variant_id)
			if work_env_id:
				if not tools.create_folder(dir_name):
					project.project().remove_work_env(work_env_id)
					work_env_id = None
				else:
					add_version(work_env_id)
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
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_work_env(work_env_id)
		else:
			return None
	else:
		return None

def add_export_version(export_name, files, version_id, comment=''):
	# For adding an export version, wizard need an existing files list
	# it will just create the new version in the database
	# and copy the files in the corresponding directory

	work_env_id = project.project().get_version_data(version_id, 'work_env_id')
	if work_env_id:
		work_env_row = project.project().get_work_env_data(work_env_id)
		variant_id = work_env_row['variant_id']
		variant_row = project.project().get_variant_data(variant_id)

		stage_name = project.project().get_stage_data(variant_row['stage_id'], 'name')
		extension_errors = []
		for file in files:
			if os.path.splitext(file)[-1].replace('.', '') not in assets_vars._export_ext_dic_[stage_name]:
				extension_errors.append(file)
		if extension_errors == []:
			if variant_row:
				export_id = get_or_add_export(export_name, variant_id)
				if export_id:
					last_version_list = project.project().get_last_export_version(export_id, 'name')
					if len(last_version_list) == 1:
						last_version = last_version_list[0]
						new_version =  str(int(last_version)+1).zfill(4)
					else:
						new_version = '0001'
					export_path = get_export_path(export_id)
					if export_path:
						dir_name = os.path.normpath(os.path.join(export_path, new_version))
						if not tools.create_folder(dir_name):
							project.project().remove_export_version(export_version_id)
							export_version_id = None
						else:
							copied_files = tools.copy_files(files, dir_name)
							if not copied_files:
								if not tools.remove_folder(dir_name):
									logging.warning(f"{dir_name} can't be removed, keep export version {new_version} in database")
								export_version_id = None
							else:
								export_version_id = project.project().add_export_version(new_version,
																				copied_files,
																				export_id,
																				version_id,
																				comment)
								events.add_export_event(export_version_id, comment)
					return export_version_id
				else:
					return None
			else:
				return None
		else:
			for file in extension_errors:
				logging.warning(f"{file} format doesn't math the stage export rules ( {os.path.splitext(file)[-1]} )")
	else:
		return None

def request_export(work_env_id, export_name, multiple=None, only_dir=None):
	# Gives a temporary ( and local ) export file name
	# for the softwares
	dir_name = tools.temp_dir()
	logging.info(f"Temporary directory created : {dir_name}, if something goes wrong in the export please go there to find your temporary export file")
	file_name = build_export_file_name(work_env_id, export_name, multiple)
	if file_name and not only_dir:
		return os.path.normpath(os.path.join(dir_name, file_name))
	elif file_name and only_dir:
		return dir_name
	else:
		return None

def archive_export(export_id):
	if site.site().is_admin():
		export_row = project.project().get_export_data(export_id)
		if export_row:
			dir_name = get_export_path(export_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					tools.remove_tree(dir_name)	
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_export(export_id)
		else:
			return None
	else:
		return None

def get_or_add_export(name, variant_id):
	# If the given export name exists, it return
	# the corresponding export_id
	# If i doesn't exists, it add it to the database
	# and rreturn the new export_id
	export_id = None
	if tools.is_safe(name):
		variant_path = get_variant_path(variant_id)
		if variant_path:
			dir_name = os.path.normpath(os.path.join(variant_path, '_EXPORTS', name))
			is_export = project.project().is_export(name, variant_id)
			if not is_export:
				export_id = project.project().add_export(name, variant_id)
				if not tools.create_folder(dir_name):
					project.project().remove_export(export_id)
					export_id = None
			else:
				export_id = project.project().get_export_by_name(name, variant_id)['id']
		else:
			logging.error("Can't create export")
	else:
		logging.warning(f"{name} contains illegal characters")
	return export_id

def archive_export_version(export_version_id):
	if site.site().is_admin():
		export_version_row = project.project().get_export_version_data(export_version_id)
		if export_version_row:
			dir_name = get_export_version_path(export_version_id)
			if os.path.isdir(dir_name):
				if tools.make_archive(dir_name):
					shutil.rmtree(dir_name)
					logging.info(f"{dir_name} deleted")
			else:
				logging.warning(f"{dir_name} not found")
			return project.project().remove_export_version(export_version_id)
		else:
			return None
	else:
		return None

def add_version(work_env_id, comment="", do_screenshot=1):
	last_version_list = project.project().get_last_work_version(work_env_id, 'name')
	if len(last_version_list) == 1:
		last_version = last_version_list[0]
		new_version =  str(int(last_version)+1).zfill(4)
	else:
		new_version = '0001'
	file_name = os.path.normpath(os.path.join(get_work_env_path(work_env_id), 
							build_version_file_name(work_env_id, new_version)))
	if do_screenshot:
		screenshot_bytes = image.screenshot()
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
			return project.project().remove_version(version_row['id'])
		else:
			return None		
	else:
		return None

def create_ticket(title, message, export_version_id, destination_user=None, files=[]):
	ticket_id = project.project().create_ticket(title, message, export_version_id, destination_user, files)
	if ticket_id:
		events.add_ticket_openned_event(ticket_id)

def close_ticket(ticket_id):
	if project.project().change_ticket_state(ticket_id, 0):
		events.add_ticket_closed_event(ticket_id)

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

def get_export_path(export_id):
	dir_name = None
	export_row = project.project().get_export_data(export_id)
	if export_row:
		export_name = export_row['name']
		variant_path = get_variant_path(export_row['variant_id'])
		if export_name and variant_path:
			dir_name = os.path.join(variant_path, '_EXPORTS', export_name)
	return dir_name

def get_export_version_path(export_version_id):
	dir_name = None
	export_version_row = project.project().get_export_version_data(export_version_id)
	if export_version_row:
		export_version_name = export_version_row['name']
		export_path = get_export_path(export_version_row['export_id'])
		if export_version_name and export_path:
			dir_name = os.path.join(export_path, export_version_name)
	return dir_name

def build_version_file_name(work_env_id, name):
	project_obj = project.project()
	work_env_row = project_obj.get_work_env_data(work_env_id)
	variant_row = project_obj.get_variant_data(work_env_row['variant_id'])
	stage_row = project_obj.get_stage_data(variant_row['stage_id'])
	asset_row = project_obj.get_asset_data(stage_row['asset_id'])
	category_row = project_obj.get_category_data(asset_row['category_id'])
	extension = project_obj.get_software_data(work_env_row['software_id'],
												'extension')
	file_name = f"{category_row['name']}"
	file_name += f"_{asset_row['name']}"
	file_name += f"_{stage_row['name']}"
	file_name += f"_{variant_row['name']}"
	file_name += f".{name}"
	file_name += f".{extension}"
	return file_name

def build_export_file_name(work_env_id, export_name, multiple=None):
	project_obj = project.project()
	work_env_row = project_obj.get_work_env_data(work_env_id)
	variant_row = project_obj.get_variant_data(work_env_row['variant_id'])
	stage_row = project_obj.get_stage_data(variant_row['stage_id'])
	asset_row = project_obj.get_asset_data(stage_row['asset_id'])
	category_row = project_obj.get_category_data(asset_row['category_id'])
	extension = work_env_row['export_extension']
	if not extension:
		extension = project_obj.get_extension(stage_row['name'], work_env_row['software_id'])
	if extension:
		file_name = f"{category_row['name']}"
		file_name += f"_{asset_row['name']}"
		file_name += f"_{stage_row['name']}"
		file_name += f"_{variant_row['name']}"
		file_name += f"_{export_name}"
		if multiple:
			file_name += f".{multiple}"
		file_name += f".{extension}"
		return file_name
	else:
		logging.error("Can't build file name")
		return None