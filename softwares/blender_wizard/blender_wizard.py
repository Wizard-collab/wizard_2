# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import blender_export
from blender_wizard import blender_reference

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path:
        bpy.ops.wm.save_as_mainfile(filepath=file_path)
    if version_id is not None:
    	os.environ['wizard_version_id'] = str(version_id)

def export():
	export_name='main'
	file_path = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']), export_name)
	stage_name = os.environ['wizard_stage_name']
	blender_export.export(file_path, stage_name, export_name)

def set_image_size():
	image_format = wizard_communicate.get_image_format()
	bpy.context.scene.render.resolution_x = image_format[0]
	bpy.context.scene.render.resolution_y = image_format[1]

def reference_textures():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			blender_reference.reference_textures(texturing_reference['namespace'], texturing_reference['files'])

def reload_textures():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'texturing' in references.keys():
		for texturing_reference in references['texturing']:
			blender_reference.reload_textures(texturing_reference['namespace'], texturing_reference['files'])

def reference_modeling():
	references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
	if 'modeling' in references.keys():
		for modeling_reference in references['modeling']:
			blender_reference.import_modeling_hard(modeling_reference['namespace'], modeling_reference['files'])