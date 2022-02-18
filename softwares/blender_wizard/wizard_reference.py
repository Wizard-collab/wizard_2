# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
from blender_wizard import redshift_shader
from blender_wizard import cycles_shader
from blender_wizard import wizard_tools

def reference_textures(namespace, files_list):
	if bpy.context.scene.render.engine == 'REDSHIFT':
		redshift_shader.plug_textures(namespace, files_list)
	elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
		cycles_shader.plug_textures(namespace, files_list)

def reload_textures(namespace, files_list):
	if bpy.context.scene.render.engine == 'REDSHIFT':
		redshift_shader.plug_textures(namespace, files_list, update=True)
	elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
		cycles_shader.plug_textures(namespace, files_list, update=True)

def import_modeling_hard(namespace, files_list):
	for file in files_list:
		wizard_tools.import_abc(file)