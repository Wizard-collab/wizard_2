# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
import wizard_hooks
from blender_wizard import redshift_shader
from blender_wizard import cycles_shader
from blender_wizard import wizard_tools

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)


def reference_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(reference_dic['namespace'], reference_dic['files'])
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(reference_dic['namespace'], reference_dic['files'])
    trigger_after_reference_hook('texturing',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def update_texturing(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    if bpy.context.scene.render.engine == 'REDSHIFT':
        redshift_shader.plug_textures(reference_dic['namespace'], reference_dic['files'], update=True)
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE' or bpy.context.scene.render.engine == 'CYCLES':
        cycles_shader.plug_textures(reference_dic['namespace'], reference_dic['files'], update=True)
    trigger_after_reference_hook('texturing',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def import_modeling_hard(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    for file in reference_dic['files']:
        if file.endswith('.abc'):
            wizard_tools.import_abc(file)
        else:
            logger.info('{} extension is unknown'.format(file))
    trigger_after_reference_hook('modeling',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def import_layout_hard(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    for file in reference_dic['files']:
        if file.endswith('.abc'):
            wizard_tools.import_abc(file)
        else:
            logger.info('{} extension is unknown'.format(file))
    trigger_after_reference_hook('layout',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def import_animation_hard(reference_dic):
    old_objects = wizard_tools.get_all_nodes()
    for file in reference_dic['files']:
        if file.endswith('.abc'):
            wizard_tools.import_abc(file)
        else:
            logger.info('{} extension is unknown'.format(file))
    trigger_after_reference_hook('animation',
                                reference_dic['files'],
                                reference_dic['namespace'],
                                wizard_tools.get_new_objects(old_objects),
                                reference_dic['string_variant'])

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects,
                                    referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('blender',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects,
                                string_asset,
                                referenced_string_asset)

