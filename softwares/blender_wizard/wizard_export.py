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
from blender_wizard import wizard_tools

# Hook modules
try:
    import blender_hook
except:
    blender_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import blender_hook")

def main(stage_name):
    export_dir = None
    if stage_name == 'modeling':
        export_modeling(stage_name)

def export(stage_name, export_name, export_GRP_list):
    trigger_before_export_hook(stage_name)
    export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
    if export_file.endswith('.abc'):
        export_abc(export_GRP_list, export_file)
    export_dir = wizard_communicate.add_export_version(export_name,
                                                        [export_file],
                                                        int(os.environ['wizard_version_id']))
    trigger_after_export_hook(stage_name, export_dir)

def export_modeling(stage_name):
    groups_dic = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for grp_name in groups_dic.keys():
        # Check group existence
        grp_obj = bpy.context.scene.objects.get(grp_name)
        if grp_obj:
            object_list = [grp_obj] + wizard_tools.get_all_children(grp_obj)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            export_name = groups_dic[grp_name]
            export('modeling', export_name, [grp_obj])
            wizard_tools.reassign_old_name_to_objects(objects_dic)
        else:
            logger.warning(f"{grp_name} not found")

def export_abc(export_GRP_list, export_file):
    wizard_tools.select_GRP_and_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True)

def trigger_before_export_hook(stage_name):
    # Trigger the before export hook
    if blender_hook:
        try:
            blender_hook.before_export(stage_name)
        except:
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if blender_hook:
        try:
            blender_hook.after_export(stage_name, export_dir)
        except:
            logger.error(str(traceback.format_exc()))
