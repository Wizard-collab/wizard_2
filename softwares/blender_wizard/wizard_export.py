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

def export(stage_name):
    export_dir = None

    trigger_before_export_hook()

    if stage_name == 'modeling':
        export_dir = export_modeling(stage_name)

    trigger_after_export_hook(export_dir)

def export_modeling(stage_name):
    export_dir = None
    GROUPS_DIC = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for GRP_NAME in GROUPS_DIC.keys():
        # Check group existence
        GRP_OBJ = bpy.context.scene.objects.get(GRP_NAME)
        if GRP_OBJ:
            # Remove _LOD# fro all objects names 
            object_list = [GRP_OBJ] + wizard_tools.get_all_children(GRP_OBJ)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            # Assign a LOD# export name
            export_name = GROUPS_DIC[GRP_NAME]
            # Export
            export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
            if export_file.endswith('.abc'):
                export_abc(GRP_OBJ, export_file)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                                [export_file],
                                                                int(os.environ['wizard_version_id']))
            # Reassign old names to objects ( _LOD# )
            wizard_tools.reassign_old_name_to_objects(objects_dic)
        else:
            logger.warning(f"{GRP_NAME} not found")
    return export_dir

def export_abc(export_GRP, export_file):
    wizard_tools.select_GRP_and_all_children(export_GRP)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True)

def trigger_before_export_hook():
    # Trigger the before export hook
    if blender_hook:
        try:
            blender_hook.before_export()
        except:
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(export_dir):
    # Trigger the after export hook
    if blender_hook:
        try:
            blender_hook.after_export(export_dir)
        except:
            logger.error(str(traceback.format_exc()))
