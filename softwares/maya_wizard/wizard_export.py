# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Maya modules
import pymel.core as pm
import maya.cmds as cmds

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools

# Hook modules
try:
    import maya_hook
except:
    maya_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import maya_hook")

def export(stage_name):
    if stage_name == 'modeling':
        export_dir = export_modeling(stage_name)

def export_modeling(stage_name):
    export_dir = None
    GROUPS_DIC = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for GRP_NAME in GROUPS_DIC.keys():
        # Check group existence
        GRP_OBJ = pm.objExists(GRP_NAME)
        if GRP_OBJ:
            # Trigger the before export hook
            if maya_hook:
                try:
                    maya_hook.before_export()
                except:
                    logger.error(str(traceback.format_exc()))
            GRP_OBJ = pm.PyNode(GRP_NAME)
            # Remove _LOD# fro all objects names 
            object_list = [GRP_OBJ] + pm.listRelatives(GRP_OBJ, allDescendents=True)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            # Assign a LOD# export name
            export_name = GROUPS_DIC[GRP_NAME]
            # Export
            export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
            export_by_extension(GRP_OBJ, export_file)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                                [export_file],
                                                                int(os.environ['wizard_version_id']))
            # Reassign old names to objects ( _LOD# )
            wizard_tools.reassign_old_name_to_objects(objects_dic)
            # Trigger the after export hook
            if maya_hook:
                try:
                    maya_hook.after_export(export_dir)
                except:
                    logger.error(str(traceback.format_exc()))
        else:
            logger.warning(f"{GRP_NAME} not found")
    return export_dir

def export_by_extension(export_GRP, export_file):
    if export_file.endswith('.abc'):
        export_abc(export_GRP, export_file)
    elif export_file.endswith('.ma'):
        export_ma(export_GRP, export_file)
    else:
        logger.info("{} extension is unkown".format(export_file))

def export_ma(export_GRP, export_file):
    pm.select(export_GRP, replace=True)
    pm.exportSelected(export_file, type='mayaAscii', pr=0)

def export_abc(export_GRP, export_file, range=[0,1]):
    start = str(range[0])
    end = str(range[1])
    command = "-frameRange "
    command += start
    command += " "
    command += end
    command += " -step 1"
    command += " -frameRelativeSample -0.2 -frameRelativeSample 0 -frameRelativeSample 0.2 -attr GuerillaTags -writeVisibility -writeUVSets -uvWrite -worldSpace -root "
    command += export_GRP
    command += " -dataFormat ogawa -file "
    command += export_file
    cmds.AbcExport(j=command)
