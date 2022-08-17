# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging

logger = logging.getLogger(__name__)

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
import wizard_hooks
from blender_wizard import wizard_tools

def export(stage_name, export_name, exported_string_asset, export_GRP_list):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                    export_name)
        if export_file.endswith('.abc'):
            export_abc(export_GRP_list, export_file)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_work_env_id']),
                                                            int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_abc(export_GRP_list, export_file):
    wizard_tools.select_GRP_list_and_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True, export_custom_properties=True)

def reopen(scene):
    bpy.ops.wm.open_mainfile(filepath=scene)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = bpy.data.filepath
    if scene == '':
        wizard_tools.save_increment()
        scene = bpy.data.filepath
    else:
        bpy.ops.wm.save_as_mainfile(filepath=scene)
        logger.info("Saving file {}".format(scene))
    return scene

def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('blender', stage_name, string_asset, exported_string_asset)

def trigger_before_export_hook(stage_name, exported_string_asset):
    additionnal_objects = []
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    nodes = wizard_hooks.before_export_hooks('blender', stage_name, string_asset, exported_string_asset)
    for node in nodes:
        if wizard_tools.check_obj_list_existence([node]):
            additionnal_objects.append(bpy.data.objects[node])
        else:
            logger.warning("{} doesn't exists".format(node))
    return additionnal_objects

def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('blender', stage_name, export_dir, string_asset, exported_string_asset)