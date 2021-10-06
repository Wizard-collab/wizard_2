# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
from blender_wizard import redshift_shader
from blender_wizard import tools

def reference_textures(namespace, files_list):
	if bpy.context.scene.render.engine == 'REDSHIFT':
		redshift_shader.plug_textures(namespace, files_list)

def reload_textures(namespace, files_list):
	if bpy.context.scene.render.engine == 'REDSHIFT':
		redshift_shader.plug_textures(namespace, files_list, update=True)

def import_modeling_hard(namespace, files_list):
	for file in files_list:
		tools.import_abc(file)
