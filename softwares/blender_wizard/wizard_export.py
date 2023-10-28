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

def export(stage_name, export_name, exported_string_asset, export_GRP_list, frange=[0,1], custom_work_env_id = None, comment=''):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])
        export_file = wizard_communicate.request_export(work_env_id,
                                                            export_name)
        if export_file.endswith('.abc'):
            export_abc(export_GRP_list, export_file, frange)
        elif export_file.endswith('.fbx'):
            export_fbx(export_GRP_list, export_file, frange)
        elif export_file.endswith('.blend'):
            export_blend(export_GRP_list, export_file)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            work_env_id,
                                                            int(os.environ['wizard_version_id']),
                                                            comment=comment)
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_abc(export_GRP_list, export_file, frange):
    export_GRP_list = wizard_tools.group_objects_before_export(export_GRP_list)
    abc_command = wizard_hooks.get_abc_command("blender")
    if abc_command is None:
        abc_command = default_abc_command
    abc_command(export_GRP_list, export_file, frange)

def export_fbx(export_GRP_list, export_file, frange):
    export_GRP_list = wizard_tools.group_objects_before_export(export_GRP_list)
    fbx_command = wizard_hooks.get_fbx_command("blender")
    if fbx_command is None:
        fbx_command = default_fbx_command
    fbx_command(export_GRP_list, export_file, frange)

def export_blend(export_GRP_list, export_file): 
    file_name = bpy.data.filepath
    temp_file=export_file.replace(os.path.basename(export_file), 'temp')
    bpy.ops.wm.save_as_mainfile(filepath=temp_file)
    collection_name = export_GRP_list[0].name
    bpy.ops.wm.read_homefile()
    objects = bpy.data.objects
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    collections = bpy.data.collections
    for collection in collections:
        bpy.data.collections.remove(collection, do_unlink=True)
    with bpy.data.libraries.load(temp_file, link=False) as (data_from, data_to):
        data_to.collections = [collection_name]
    for collection in data_to.collections:
        bpy.context.collection.children.link(collection)
    bpy.ops.wm.save_as_mainfile(filepath=export_file, relative_remap=False)

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
        if os.environ["wizard_launch_mode"] == 'gui':
            wizard_communicate.screen_over_version(int(os.environ['wizard_version_id']))
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

def default_abc_command(export_GRP_list, export_file, frange):
    wizard_tools.select_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                    selected=True,
                    export_custom_properties=True,
                    uvs=True,
                    orcos=True,
                    start=frange[0],
                    end=frange[1],
                    sh_open=-0.2,
                    sh_close=0.2)

def default_fbx_command(export_GRP_list, export_file, frange):
    wizard_tools.select_all_children(export_GRP_list)
    bpy.ops.export_scene.fbx(filepath=export_file,
                                use_selection=True,
                                use_custom_props=True)