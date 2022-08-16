# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
import wizard_hooks
from blender_wizard import redshift_shader
from blender_wizard import cycles_shader
from blender_wizard import wizard_tools

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)


def reference_texturing(namespace, files_list):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(namespace, files_list)
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(namespace, files_list)
    trigger_after_reference_hook('texturing',
                                files_list,
                                namespace,
                                wizard_tools.get_new_objects(old_objects))

def update_texturing(namespace, files_list):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(namespace, files_list, update=True)
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(namespace, files_list, update=True)
    trigger_after_reference_hook('texturing',
                                files_list,
                                namespace,
                                wizard_tools.get_new_objects(old_objects))

def import_modeling_hard(namespace, files_list):
    old_objects = wizard_tools.get_all_nodes()
    for file in files_list:
        if file.endswith('.abc'):
            wizard_tools.import_abc(file)
        else:
            logger.info('{} extension is unknown'.format(file))
    trigger_after_reference_hook('modeling',
                                files_list,
                                namespace,
                                wizard_tools.get_new_objects(old_objects))

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    wizard_hooks.after_reference_hooks('blender',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects)

