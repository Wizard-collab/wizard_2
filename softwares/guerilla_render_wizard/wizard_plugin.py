# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_reference
from guerilla_render_wizard import guerilla_shader

# Guerilla modules
from guerilla import Document, pynode

def save_increment():
	file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
	if file_path:
		Document().save(file_path)
	else:
		logger.error('Saving failed')
	if version_id is not None:
		os.environ['wizard_version_id'] = str(version_id)

def reference_modeling():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'modeling' in references.keys():
		for modeling_reference in references['modeling']:
			wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'modeling' in references.keys():
		for modeling_reference in references['modeling']:
			wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def import_texturing():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			guerilla_shader.import_texturing(texturing_reference['namespace'],
												texturing_reference['files'],
												texturing_reference['asset_name'])

def update_texturing():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			guerilla_shader.update_texturing(texturing_reference['namespace'],
												texturing_reference['files'],
												texturing_reference['asset_name'])