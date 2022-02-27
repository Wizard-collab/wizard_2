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

def export(stage_name):
    if stage_name == 'modeling':
        export_modeling()
    if stage_name == 'rigging':
        export_rigging()

def export_modeling():
    groups_dic = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for grp_name in groups_dic.keys():
        process = check_obj_list_existence([grp_name])
        if process:
            # Remove _LOD# fro all objects names 
            grp_obj = pm.PyNode(grp_name)
            object_list = [grp_obj] + pm.listRelatives(grp_name,
                                                        allDescendents=True)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            # Assign a LOD# export name
            export_name = groups_dic[grp_name]
            # Export
            export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
            export_by_extension([grp_obj], export_file)
            wizard_communicate.add_export_version(export_name,
                                                    [export_file],
                                                    int(os.environ['wizard_version_id']))
            # Reassign old names to objects ( _LOD# )
            wizard_tools.reassign_old_name_to_objects(objects_dic)

def export_rigging():
    export_name = 'main'
    process = check_obj_list_existence(['rigging_GRP', 'render_set'])
    if process:
        export_GRP_list = ['rigging_GRP', 'render_set']
        export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                    export_name)
        export_by_extension(export_GRP_list, export_file)
        wizard_communicate.add_export_version(export_name,
                                                [export_file],
                                                int(os.environ['wizard_version_id']))

def check_obj_list_existence(object_list):
    success = True
    for obj_name in object_list:
        if not pm.objExists(obj_name):
            logger.warning("'{}' not found".format(obj_name))
            success = False
    return success

def export_by_extension(export_GRP_list, export_file):
    if export_file.endswith('.abc'):
        export_abc(export_GRP_list[0], export_file)
    elif export_file.endswith('.ma'):
        export_ma(export_GRP_list, export_file)
    else:
        logger.info("{} extension is unkown".format(export_file))

def export_ma(export_GRP_list, export_file):
    pm.select(export_GRP_list, replace=True, noExpand=True)
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
